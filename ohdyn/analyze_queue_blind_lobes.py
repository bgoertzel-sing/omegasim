"""Analyze service-capacity lobe trajectories with queue-blind labels."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from ohdyn.analyze_service_capacity_trajectory import (
    _dwell_runs,
    _entropy,
    _mean_values,
    _normalized_entropy,
    _read_comparison_rows,
    _safe_ratio,
)
from ohdyn.compare_attention import _format_number, _format_regime_counts


QUEUE_BLIND_LOBE_LABELS = (
    "execution",
    "task_generation",
    "coordination",
    "low_activity",
)

QUEUE_BLIND_LOBE_FIELDS = (
    "pressure_label",
    "service_capacity_label",
    "task_creation_pressure",
    "work_service_capacity",
    "seed_count",
    "run_count",
    "queue_depth_per_created_task_mean",
    "queued_task_age_mean_final_mean",
    "transition_count_mean",
    "transition_entropy_mean",
    "transition_entropy_normalized_mean",
    "dwell_run_count_mean",
    "dwell_length_mean",
    "dwell_length_max_mean",
    "task_generation_dwell_share_mean",
    "execution_dwell_share_mean",
    "dominant_queue_blind_lobe_counts",
    "transition_pair_counts",
    "dwell_length_histogram",
)

QUEUE_BLIND_LOBE_EFFECT_FIELDS = (
    "effect_axis",
    "fixed_label",
    "fixed_value",
    "low_label",
    "high_label",
    "low_value",
    "high_value",
    "transition_entropy_mean_delta",
    "transition_entropy_normalized_mean_delta",
    "dwell_length_mean_delta",
    "dwell_length_max_mean_delta",
    "task_generation_dwell_share_mean_delta",
    "execution_dwell_share_mean_delta",
    "interpretation",
)


def run_queue_blind_lobe_analysis(
    *,
    service_capacity_dir: str | Path,
    out_dir: str | Path,
) -> list[dict[str, Any]]:
    source_path = Path(service_capacity_dir)
    output_path = Path(out_dir)
    _validate_source_dir(source_path)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    comparison_rows = _read_comparison_rows(
        source_path / "service_capacity_comparison_metrics.csv"
    )
    rows = [_queue_blind_row(source_path, comparison_row) for comparison_row in comparison_rows]
    effect_rows = _effect_rows(rows)
    _write_csv(output_path / "queue_blind_lobe_metrics.csv", QUEUE_BLIND_LOBE_FIELDS, rows)
    _write_csv(
        output_path / "queue_blind_lobe_effects.csv",
        QUEUE_BLIND_LOBE_EFFECT_FIELDS,
        effect_rows,
    )
    (output_path / "summary.md").write_text(_summary(rows, effect_rows, source_path))
    return rows


def _validate_source_dir(source_path: Path) -> None:
    if not source_path.is_dir():
        raise FileNotFoundError(f"Source directory {source_path} does not exist.")
    required = (
        "service_capacity_comparison_metrics.csv",
        "service_capacity_effects.csv",
        "summary.md",
    )
    missing = [name for name in required if not (source_path / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"Source directory {source_path} is missing: {', '.join(missing)}"
        )


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        name
        for name in (
            "queue_blind_lobe_metrics.csv",
            "queue_blind_lobe_effects.csv",
            "summary.md",
        )
        if (output_path / name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(
            f"Output path {output_path} already contains queue-blind artifacts: {names}"
        )


def _queue_blind_row(
    source_path: Path,
    comparison_row: dict[str, str],
) -> dict[str, Any]:
    pressure_label = comparison_row["pressure_label"]
    service_label = comparison_row["service_capacity_label"]
    run_dirs = sorted(source_path.glob(f"{pressure_label}_{service_label}_seed*"))
    if not run_dirs:
        raise FileNotFoundError(f"No run directories found for {pressure_label}/{service_label}.")

    summaries = [_run_queue_blind_summary(run_dir / "metrics.csv") for run_dir in run_dirs]
    transition_pair_counts: Counter[str] = Counter()
    dwell_length_histogram: Counter[str] = Counter()
    dominant_lobes: Counter[str] = Counter()
    for summary in summaries:
        transition_pair_counts.update(summary["transition_pair_counts"])
        dwell_length_histogram.update(summary["dwell_length_histogram"])
        dominant_lobes[str(summary["dominant_lobe_label"])] += 1

    return {
        "pressure_label": pressure_label,
        "service_capacity_label": service_label,
        "task_creation_pressure": comparison_row["task_creation_pressure"],
        "work_service_capacity": comparison_row["work_service_capacity"],
        "seed_count": comparison_row["seed_count"],
        "run_count": len(run_dirs),
        "queue_depth_per_created_task_mean": comparison_row[
            "queue_depth_per_created_task_mean"
        ],
        "queued_task_age_mean_final_mean": comparison_row[
            "queued_task_age_mean_final_mean"
        ],
        "transition_count_mean": _mean_values(
            [float(summary["transition_count"]) for summary in summaries]
        ),
        "transition_entropy_mean": _mean_values(
            [float(summary["transition_entropy"]) for summary in summaries]
        ),
        "transition_entropy_normalized_mean": _mean_values(
            [float(summary["transition_entropy_normalized"]) for summary in summaries]
        ),
        "dwell_run_count_mean": _mean_values(
            [float(summary["dwell_run_count"]) for summary in summaries]
        ),
        "dwell_length_mean": _mean_values(
            [float(summary["dwell_length_mean"]) for summary in summaries]
        ),
        "dwell_length_max_mean": _mean_values(
            [float(summary["dwell_length_max"]) for summary in summaries]
        ),
        "task_generation_dwell_share_mean": _mean_values(
            [float(summary["task_generation_dwell_share"]) for summary in summaries]
        ),
        "execution_dwell_share_mean": _mean_values(
            [float(summary["execution_dwell_share"]) for summary in summaries]
        ),
        "dominant_queue_blind_lobe_counts": _format_regime_counts(dominant_lobes),
        "transition_pair_counts": _format_regime_counts(transition_pair_counts),
        "dwell_length_histogram": _format_regime_counts(dwell_length_histogram),
    }


def _run_queue_blind_summary(metrics_path: Path) -> dict[str, Any]:
    if not metrics_path.is_file():
        raise FileNotFoundError(f"Missing metrics artifact: {metrics_path}")
    labels = _queue_blind_labels_from_metrics(metrics_path)
    transition_pairs = [
        f"{previous}->{current}"
        for previous, current in zip(labels, labels[1:])
        if previous != current
    ]
    dwell_runs = _dwell_runs(labels)
    dwell_lengths = [length for _, length in dwell_runs]
    label_ticks = Counter(labels)
    dominant_label = max(label_ticks.items(), key=lambda item: (item[1], item[0]))[0]
    return {
        "transition_count": len(transition_pairs),
        "transition_entropy": _entropy(transition_pairs),
        "transition_entropy_normalized": _normalized_entropy(transition_pairs),
        "transition_pair_counts": Counter(transition_pairs),
        "dwell_run_count": len(dwell_runs),
        "dwell_length_mean": _mean_values([float(length) for length in dwell_lengths]),
        "dwell_length_max": max(dwell_lengths),
        "task_generation_dwell_share": _safe_ratio(
            float(label_ticks["task_generation"]),
            float(len(labels)),
        ),
        "execution_dwell_share": _safe_ratio(
            float(label_ticks["execution"]),
            float(len(labels)),
        ),
        "dwell_length_histogram": Counter(str(length) for length in dwell_lengths),
        "dominant_lobe_label": dominant_label,
    }


def _queue_blind_labels_from_metrics(metrics_path: Path) -> list[str]:
    labels: list[str] = []
    with metrics_path.open() as handle:
        for row in csv.DictReader(handle):
            labels.append(_queue_blind_label(row))
    if not labels:
        raise ValueError(f"{metrics_path} contains no metric rows.")
    return labels


def _queue_blind_label(row: dict[str, str]) -> str:
    counts = {
        "work_task": int(float(row["tasks_worked_tick"])),
        "create_task": int(float(row["tasks_created_tick"])),
        "message": int(float(row["messages_sent_tick"])),
        "idle": int(float(row["idle_tick"])),
    }
    dominant_action = _dominant_action(counts)
    if dominant_action == "work_task":
        return "execution"
    if dominant_action == "create_task":
        return "task_generation"
    if dominant_action == "message":
        return "coordination"
    return "low_activity"


def _dominant_action(action_counts: dict[str, int]) -> str:
    priority = ("work_task", "create_task", "message", "idle")
    return max(priority, key=lambda action: (action_counts[action], -priority.index(action)))


def _effect_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    effect_rows: list[dict[str, Any]] = []
    for pressure_label in ("normal_pressure", "high_pressure", "extreme_pressure"):
        low_row = _find_row(rows, pressure_label, "low_service")
        high_row = _find_row(rows, pressure_label, "high_service")
        effect_rows.append(
            _delta_row(
                effect_axis="service_capacity",
                fixed_label=pressure_label,
                fixed_value=float(low_row["task_creation_pressure"]),
                low_label="low_service",
                high_label="high_service",
                low_value=float(low_row["work_service_capacity"]),
                high_value=float(high_row["work_service_capacity"]),
                low_row=low_row,
                high_row=high_row,
                interpretation="queue-blind fixed-pressure high-minus-low service effect",
            )
        )

    for service_label in ("low_service", "baseline_service", "high_service"):
        normal_row = _find_row(rows, "normal_pressure", service_label)
        extreme_row = _find_row(rows, "extreme_pressure", service_label)
        effect_rows.append(
            _delta_row(
                effect_axis="task_creation_pressure",
                fixed_label=service_label,
                fixed_value=float(normal_row["work_service_capacity"]),
                low_label="normal_pressure",
                high_label="extreme_pressure",
                low_value=float(normal_row["task_creation_pressure"]),
                high_value=float(extreme_row["task_creation_pressure"]),
                low_row=normal_row,
                high_row=extreme_row,
                interpretation="queue-blind fixed-service extreme-minus-normal pressure effect",
            )
        )
    return effect_rows


def _find_row(
    rows: list[dict[str, Any]],
    pressure_label: str,
    service_label: str,
) -> dict[str, Any]:
    for row in rows:
        if (
            str(row["pressure_label"]) == pressure_label
            and str(row["service_capacity_label"]) == service_label
        ):
            return row
    raise ValueError(f"Missing queue-blind row for {pressure_label}/{service_label}.")


def _delta_row(
    *,
    effect_axis: str,
    fixed_label: str,
    fixed_value: float,
    low_label: str,
    high_label: str,
    low_value: float,
    high_value: float,
    low_row: dict[str, Any],
    high_row: dict[str, Any],
    interpretation: str,
) -> dict[str, Any]:
    return {
        "effect_axis": effect_axis,
        "fixed_label": fixed_label,
        "fixed_value": fixed_value,
        "low_label": low_label,
        "high_label": high_label,
        "low_value": low_value,
        "high_value": high_value,
        "transition_entropy_mean_delta": _delta(
            low_row,
            high_row,
            "transition_entropy_mean",
        ),
        "transition_entropy_normalized_mean_delta": _delta(
            low_row,
            high_row,
            "transition_entropy_normalized_mean",
        ),
        "dwell_length_mean_delta": _delta(low_row, high_row, "dwell_length_mean"),
        "dwell_length_max_mean_delta": _delta(low_row, high_row, "dwell_length_max_mean"),
        "task_generation_dwell_share_mean_delta": _delta(
            low_row,
            high_row,
            "task_generation_dwell_share_mean",
        ),
        "execution_dwell_share_mean_delta": _delta(
            low_row,
            high_row,
            "execution_dwell_share_mean",
        ),
        "interpretation": interpretation,
    }


def _delta(low_row: dict[str, Any], high_row: dict[str, Any], field: str) -> float:
    return round(float(high_row[field]) - float(low_row[field]), 6)


def _write_csv(
    path: Path,
    fieldnames: tuple[str, ...],
    rows: list[dict[str, Any]],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    source_path: Path,
) -> str:
    service_effects = [
        row for row in effect_rows if row["effect_axis"] == "service_capacity"
    ]
    pressure_effects = [
        row for row in effect_rows if row["effect_axis"] == "task_creation_pressure"
    ]
    strongest_pressure_generation = max(
        pressure_effects,
        key=lambda row: abs(float(row["task_generation_dwell_share_mean_delta"])),
    )
    strongest_pressure_entropy = max(
        pressure_effects,
        key=lambda row: abs(float(row["transition_entropy_mean_delta"])),
    )
    strongest_service_execution = max(
        service_effects,
        key=lambda row: abs(float(row["execution_dwell_share_mean_delta"])),
    )
    lines = [
        "# A2 queue-blind lobe analysis",
        "",
        f"- source: {source_path}",
        f"- grid rows: {len(rows)}",
        "- label inputs: tasks_worked_tick, tasks_created_tick, messages_sent_tick, idle_tick",
        "- excluded inputs: queue_depth, queue_delta_tick, baseline_lobe_label",
        "",
        "## Grid queue-blind lobe metrics",
        "",
        *[
            f"- {row['pressure_label']} / {row['service_capacity_label']}: "
            f"transition_entropy={row['transition_entropy_mean']}, "
            f"normalized_entropy={row['transition_entropy_normalized_mean']}, "
            f"dwell_length_max_mean={row['dwell_length_max_mean']}, "
            f"task_generation_share={row['task_generation_dwell_share_mean']}, "
            f"execution_share={row['execution_dwell_share_mean']}, "
            f"dominant_lobes={row['dominant_queue_blind_lobe_counts']}"
            for row in rows
        ],
        "",
        "## Fixed-pressure service-capacity queue-blind effects",
        "",
        *[
            f"- {row['fixed_label']}: "
            "transition_entropy_delta="
            f"{_format_number(float(row['transition_entropy_mean_delta']))}, "
            "dwell_length_max_delta="
            f"{_format_number(float(row['dwell_length_max_mean_delta']))}, "
            "task_generation_share_delta="
            f"{_format_number(float(row['task_generation_dwell_share_mean_delta']))}, "
            "execution_share_delta="
            f"{_format_number(float(row['execution_dwell_share_mean_delta']))}"
            for row in service_effects
        ],
        "",
        "## Fixed-service pressure queue-blind effects",
        "",
        *[
            f"- {row['fixed_label']}: "
            "transition_entropy_delta="
            f"{_format_number(float(row['transition_entropy_mean_delta']))}, "
            "dwell_length_max_delta="
            f"{_format_number(float(row['dwell_length_max_mean_delta']))}, "
            "task_generation_share_delta="
            f"{_format_number(float(row['task_generation_dwell_share_mean_delta']))}, "
            "execution_share_delta="
            f"{_format_number(float(row['execution_dwell_share_mean_delta']))}"
            for row in pressure_effects
        ],
        "",
        "## Interpretation",
        "",
        (
            "- Strongest fixed-service pressure shift in queue-blind generation share: "
            f"{strongest_pressure_generation['fixed_label']} "
            "task_generation_share_delta="
            f"{_format_number(float(strongest_pressure_generation['task_generation_dwell_share_mean_delta']))}."
        ),
        (
            "- Strongest fixed-service pressure shift in queue-blind entropy: "
            f"{strongest_pressure_entropy['fixed_label']} "
            "transition_entropy_delta="
            f"{_format_number(float(strongest_pressure_entropy['transition_entropy_mean_delta']))}."
        ),
        (
            "- Strongest fixed-pressure service shift in execution share: "
            f"{strongest_service_execution['fixed_label']} "
            "execution_share_delta="
            f"{_format_number(float(strongest_service_execution['execution_dwell_share_mean_delta']))}."
        ),
        (
            "- Use this as a robustness check only: it tests whether pressure "
            "structure remains visible after removing queue-derived label rules."
        ),
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze queue-blind lobe labels in service-capacity artifacts."
    )
    parser.add_argument(
        "--service-capacity-dir",
        required=True,
        help="Existing ohdyn.compare_service_capacity output directory.",
    )
    parser.add_argument("--out", required=True, help="Output directory for analysis artifacts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_queue_blind_lobe_analysis(
            service_capacity_dir=args.service_capacity_dir,
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
