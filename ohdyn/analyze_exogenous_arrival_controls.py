"""Bootstrap and null-control analysis for frozen exogenous-arrival artifacts."""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from ohdyn.analyze_queue_blind_lobes import _queue_blind_label
from ohdyn.analyze_service_capacity_trajectory import (
    _dwell_runs,
    _entropy,
    _final_metrics,
    _labels_from_metrics,
    _lobe_summary_from_labels,
    _mean_values,
    _normalized_entropy,
    _null_metric_fields,
    _quantile,
    _safe_ratio,
    _sign_stability,
)
from ohdyn.compare_attention import _format_number


EXOGENOUS_CONTROL_METRIC_FIELDS = (
    "condition",
    "rate_per_tick",
    "seed_count",
    "run_count",
    "queue_depth_per_created_task_mean",
    "queued_task_age_mean_final_mean",
    "baseline_transition_entropy_mean",
    "baseline_transition_entropy_normalized_mean",
    "baseline_dwell_length_max_mean",
    "baseline_backlog_growth_dwell_share_mean",
    "queue_blind_transition_entropy_mean",
    "queue_blind_transition_entropy_normalized_mean",
    "queue_blind_dwell_length_max_mean",
    "queue_blind_task_generation_dwell_share_mean",
    "queue_blind_execution_dwell_share_mean",
)

EXOGENOUS_CONTROL_BOOTSTRAP_FIELDS = (
    "effect_axis",
    "low_label",
    "high_label",
    "metric",
    "bootstrap_reps",
    "seed_count",
    "observed_delta",
    "ci_low",
    "ci_high",
    "sign_stability",
)

EXOGENOUS_CONTROL_NULL_FIELDS = (
    "condition",
    "rate_per_tick",
    "null_reps",
    "run_count",
    "transition_count_observed_mean",
    "transition_count_null_mean",
    "transition_count_observed_minus_null",
    "transition_entropy_observed_mean",
    "transition_entropy_null_mean",
    "transition_entropy_observed_minus_null",
    "transition_entropy_normalized_observed_mean",
    "transition_entropy_normalized_null_mean",
    "transition_entropy_normalized_observed_minus_null",
    "dwell_length_max_observed_mean",
    "dwell_length_max_null_mean",
    "dwell_length_max_observed_minus_null",
)

CONTROL_CONDITIONS = (
    "endogenous_control",
    "exogenous_low",
    "exogenous_medium",
    "exogenous_high",
)

BOOTSTRAP_METRICS = (
    "queue_depth_per_created_task",
    "baseline_transition_entropy",
    "baseline_dwell_length_max",
    "baseline_backlog_growth_dwell_share",
    "queue_blind_transition_entropy",
    "queue_blind_dwell_length_max",
    "queue_blind_task_generation_dwell_share",
    "queue_blind_execution_dwell_share",
)


def run_exogenous_arrival_control_analysis(
    *,
    exogenous_arrival_dir: str | Path,
    out_dir: str | Path,
    bootstrap_reps: int = 200,
    null_reps: int = 100,
    random_seed: int = 314159,
) -> list[dict[str, Any]]:
    source_path = Path(exogenous_arrival_dir)
    output_path = Path(out_dir)
    _validate_source_dir(source_path)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    comparison_rows = _read_comparison_rows(
        source_path / "exogenous_arrival_comparison_metrics.csv"
    )
    per_seed_rows = _per_seed_rows(source_path, comparison_rows)
    metric_rows = _metric_rows(comparison_rows, per_seed_rows)
    bootstrap_rows = _bootstrap_rows(
        per_seed_rows,
        reps=bootstrap_reps,
        random_seed=random_seed,
    )
    null_rows = _null_rows(
        source_path,
        comparison_rows,
        reps=null_reps,
        random_seed=random_seed,
    )

    _write_csv(
        output_path / "exogenous_arrival_control_metrics.csv",
        EXOGENOUS_CONTROL_METRIC_FIELDS,
        metric_rows,
    )
    _write_csv(
        output_path / "exogenous_arrival_control_bootstrap.csv",
        EXOGENOUS_CONTROL_BOOTSTRAP_FIELDS,
        bootstrap_rows,
    )
    _write_csv(
        output_path / "exogenous_arrival_control_nulls.csv",
        EXOGENOUS_CONTROL_NULL_FIELDS,
        null_rows,
    )
    (output_path / "summary.md").write_text(
        _summary(metric_rows, bootstrap_rows, null_rows, source_path)
    )
    return metric_rows


def _validate_source_dir(source_path: Path) -> None:
    if not source_path.is_dir():
        raise FileNotFoundError(f"Source directory {source_path} does not exist.")
    required = (
        "exogenous_arrival_comparison_metrics.csv",
        "exogenous_arrival_effects.csv",
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
            "exogenous_arrival_control_metrics.csv",
            "exogenous_arrival_control_bootstrap.csv",
            "exogenous_arrival_control_nulls.csv",
            "summary.md",
        )
        if (output_path / name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(
            f"Output path {output_path} already contains exogenous-control artifacts: {names}"
        )


def _read_comparison_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "condition",
        "rate_per_tick",
        "seed_count",
        "queue_depth_per_created_task_mean",
        "queued_task_age_mean_final_mean",
    }
    missing = required - set(rows[0].keys() if rows else ())
    if missing:
        raise ValueError(f"{path} is missing required fields: {', '.join(sorted(missing))}")
    conditions = [row["condition"] for row in rows]
    if conditions != list(CONTROL_CONDITIONS):
        raise ValueError(
            f"{path} must contain frozen exogenous conditions in order: "
            f"{', '.join(CONTROL_CONDITIONS)}"
        )
    return rows


def _per_seed_rows(
    source_path: Path,
    comparison_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for comparison_row in comparison_rows:
        condition = comparison_row["condition"]
        run_dirs = sorted(source_path.glob(f"{condition}_seed*"))
        if not run_dirs:
            raise FileNotFoundError(f"No run directories found for {condition}.")
        for run_dir in run_dirs:
            metrics_path = run_dir / "metrics.csv"
            final = _final_metrics(metrics_path)
            baseline = _baseline_summary(metrics_path)
            queue_blind = _queue_blind_summary(metrics_path)
            rows.append(
                {
                    "condition": condition,
                    "rate_per_tick": float(comparison_row["rate_per_tick"]),
                    "seed": _seed_from_run_dir(run_dir),
                    "queue_depth_per_created_task": _safe_ratio(
                        float(final["queue_depth"]),
                        float(final["tasks_created_total"]),
                    ),
                    "queued_task_age_mean_final": float(final["queued_task_age_mean_tick"]),
                    "baseline_transition_entropy": float(baseline["transition_entropy"]),
                    "baseline_transition_entropy_normalized": float(
                        baseline["transition_entropy_normalized"]
                    ),
                    "baseline_dwell_length_max": float(baseline["dwell_length_max"]),
                    "baseline_backlog_growth_dwell_share": float(
                        baseline["backlog_growth_dwell_share"]
                    ),
                    "queue_blind_transition_entropy": float(queue_blind["transition_entropy"]),
                    "queue_blind_transition_entropy_normalized": float(
                        queue_blind["transition_entropy_normalized"]
                    ),
                    "queue_blind_dwell_length_max": float(queue_blind["dwell_length_max"]),
                    "queue_blind_task_generation_dwell_share": float(
                        queue_blind["task_generation_dwell_share"]
                    ),
                    "queue_blind_execution_dwell_share": float(
                        queue_blind["execution_dwell_share"]
                    ),
                }
            )
    return rows


def _seed_from_run_dir(run_dir: Path) -> int:
    try:
        return int(run_dir.name.rsplit("_seed", maxsplit=1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Cannot parse seed from run directory {run_dir}.") from exc


def _baseline_summary(metrics_path: Path) -> dict[str, Any]:
    return _lobe_summary_from_labels(_labels_from_metrics(metrics_path))


def _queue_blind_summary(metrics_path: Path) -> dict[str, Any]:
    labels: list[str] = []
    with metrics_path.open() as handle:
        for row in csv.DictReader(handle):
            labels.append(_queue_blind_label(row))
    if not labels:
        raise ValueError(f"{metrics_path} contains no metric rows.")
    transition_pairs = [
        f"{previous}->{current}"
        for previous, current in zip(labels, labels[1:])
        if previous != current
    ]
    dwell_runs = _dwell_runs(labels)
    dwell_lengths = [length for _, length in dwell_runs]
    label_ticks = Counter(labels)
    return {
        "transition_entropy": _entropy(transition_pairs),
        "transition_entropy_normalized": _normalized_entropy(transition_pairs),
        "dwell_length_max": max(dwell_lengths),
        "task_generation_dwell_share": _safe_ratio(
            float(label_ticks["task_generation"]),
            float(len(labels)),
        ),
        "execution_dwell_share": _safe_ratio(
            float(label_ticks["execution"]),
            float(len(labels)),
        ),
    }


def _metric_rows(
    comparison_rows: list[dict[str, str]],
    per_seed_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for comparison_row in comparison_rows:
        condition = comparison_row["condition"]
        seed_rows = [row for row in per_seed_rows if row["condition"] == condition]
        rows.append(
            {
                "condition": condition,
                "rate_per_tick": comparison_row["rate_per_tick"],
                "seed_count": comparison_row["seed_count"],
                "run_count": len(seed_rows),
                "queue_depth_per_created_task_mean": comparison_row[
                    "queue_depth_per_created_task_mean"
                ],
                "queued_task_age_mean_final_mean": comparison_row[
                    "queued_task_age_mean_final_mean"
                ],
                "baseline_transition_entropy_mean": _mean_metric(
                    seed_rows,
                    "baseline_transition_entropy",
                ),
                "baseline_transition_entropy_normalized_mean": _mean_metric(
                    seed_rows,
                    "baseline_transition_entropy_normalized",
                ),
                "baseline_dwell_length_max_mean": _mean_metric(
                    seed_rows,
                    "baseline_dwell_length_max",
                ),
                "baseline_backlog_growth_dwell_share_mean": _mean_metric(
                    seed_rows,
                    "baseline_backlog_growth_dwell_share",
                ),
                "queue_blind_transition_entropy_mean": _mean_metric(
                    seed_rows,
                    "queue_blind_transition_entropy",
                ),
                "queue_blind_transition_entropy_normalized_mean": _mean_metric(
                    seed_rows,
                    "queue_blind_transition_entropy_normalized",
                ),
                "queue_blind_dwell_length_max_mean": _mean_metric(
                    seed_rows,
                    "queue_blind_dwell_length_max",
                ),
                "queue_blind_task_generation_dwell_share_mean": _mean_metric(
                    seed_rows,
                    "queue_blind_task_generation_dwell_share",
                ),
                "queue_blind_execution_dwell_share_mean": _mean_metric(
                    seed_rows,
                    "queue_blind_execution_dwell_share",
                ),
            }
        )
    return rows


def _mean_metric(rows: list[dict[str, Any]], metric: str) -> float:
    return _mean_values([float(row[metric]) for row in rows])


def _bootstrap_rows(
    per_seed_rows: list[dict[str, Any]],
    *,
    reps: int,
    random_seed: int,
) -> list[dict[str, Any]]:
    if reps <= 0:
        raise ValueError("bootstrap_reps must be positive.")
    seeds = sorted({int(row["seed"]) for row in per_seed_rows})
    by_condition_seed = {
        (str(row["condition"]), int(row["seed"])): row
        for row in per_seed_rows
    }
    rng = random.Random(random_seed)
    rows: list[dict[str, Any]] = []
    for high_condition in CONTROL_CONDITIONS[1:]:
        for metric in BOOTSTRAP_METRICS:
            observed_delta = _paired_delta(
                by_condition_seed,
                seeds,
                high_condition=high_condition,
                metric=metric,
            )
            deltas = [
                _paired_delta(
                    by_condition_seed,
                    [rng.choice(seeds) for _ in seeds],
                    high_condition=high_condition,
                    metric=metric,
                )
                for _ in range(reps)
            ]
            rows.append(
                {
                    "effect_axis": "exogenous_arrival_rate",
                    "low_label": "endogenous_control",
                    "high_label": high_condition,
                    "metric": metric,
                    "bootstrap_reps": reps,
                    "seed_count": len(seeds),
                    "observed_delta": observed_delta,
                    "ci_low": _quantile(deltas, 0.025),
                    "ci_high": _quantile(deltas, 0.975),
                    "sign_stability": _sign_stability(deltas, observed_delta),
                }
            )
    return rows


def _paired_delta(
    by_condition_seed: dict[tuple[str, int], dict[str, Any]],
    seeds: list[int],
    *,
    high_condition: str,
    metric: str,
) -> float:
    deltas = []
    for seed in seeds:
        low_row = by_condition_seed[("endogenous_control", seed)]
        high_row = by_condition_seed[(high_condition, seed)]
        deltas.append(float(high_row[metric]) - float(low_row[metric]))
    return _mean_values(deltas)


def _null_rows(
    source_path: Path,
    comparison_rows: list[dict[str, str]],
    *,
    reps: int,
    random_seed: int,
) -> list[dict[str, Any]]:
    if reps <= 0:
        raise ValueError("null_reps must be positive.")
    rows: list[dict[str, Any]] = []
    for comparison_row in comparison_rows:
        condition = comparison_row["condition"]
        run_dirs = sorted(source_path.glob(f"{condition}_seed*"))
        observed_summaries: list[dict[str, Any]] = []
        null_summaries: list[dict[str, Any]] = []
        for run_dir in run_dirs:
            labels = _labels_from_metrics(run_dir / "metrics.csv")
            observed_summaries.append(_lobe_summary_from_labels(labels))
            for rep in range(reps):
                shuffled_labels = list(labels)
                rng = random.Random(f"{random_seed}:{condition}:{run_dir.name}:{rep}")
                rng.shuffle(shuffled_labels)
                null_summaries.append(_lobe_summary_from_labels(shuffled_labels))
        rows.append(
            {
                "condition": condition,
                "rate_per_tick": comparison_row["rate_per_tick"],
                "null_reps": reps,
                "run_count": len(run_dirs),
                **_null_metric_fields(
                    observed_summaries,
                    null_summaries,
                    "transition_count",
                ),
                **_null_metric_fields(
                    observed_summaries,
                    null_summaries,
                    "transition_entropy",
                ),
                **_null_metric_fields(
                    observed_summaries,
                    null_summaries,
                    "transition_entropy_normalized",
                ),
                **_null_metric_fields(
                    observed_summaries,
                    null_summaries,
                    "dwell_length_max",
                ),
            }
        )
    return rows


def _write_csv(
    path: Path,
    fieldnames: tuple[str, ...],
    rows: list[dict[str, Any]],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    metric_rows: list[dict[str, Any]],
    bootstrap_rows: list[dict[str, Any]],
    null_rows: list[dict[str, Any]],
    source_path: Path,
) -> str:
    stable_rows = [
        row for row in bootstrap_rows if float(row["sign_stability"]) >= 0.95
    ]
    high_entropy = _find_bootstrap_row(
        bootstrap_rows,
        "exogenous_high",
        "queue_blind_transition_entropy",
    )
    high_generation = _find_bootstrap_row(
        bootstrap_rows,
        "exogenous_high",
        "queue_blind_task_generation_dwell_share",
    )
    high_load = _find_bootstrap_row(
        bootstrap_rows,
        "exogenous_high",
        "queue_depth_per_created_task",
    )
    strongest_null = max(
        null_rows,
        key=lambda row: float(row["dwell_length_max_observed_minus_null"]),
    )
    lines = [
        "# A2 exogenous-arrival control analysis",
        "",
        f"- source: {source_path}",
        f"- conditions: {len(metric_rows)}",
        "- bootstrap: paired by seed against endogenous_control",
        "- null control: label-count-preserving baseline-lobe shuffles",
        "- queue-blind labels use agent_tasks_created_tick when present",
        "",
        "## Condition Metrics",
        "",
        *[
            f"- {row['condition']}: rate={_format_number(float(row['rate_per_tick']))}, "
            f"queue_per_created={_format_number(float(row['queue_depth_per_created_task_mean']))}, "
            f"baseline_entropy={_format_number(float(row['baseline_transition_entropy_mean']))}, "
            f"baseline_backlog_share={_format_number(float(row['baseline_backlog_growth_dwell_share_mean']))}, "
            f"queue_blind_entropy={_format_number(float(row['queue_blind_transition_entropy_mean']))}, "
            f"queue_blind_generation_share={_format_number(float(row['queue_blind_task_generation_dwell_share_mean']))}"
            for row in metric_rows
        ],
        "",
        "## Bootstrap Highlights",
        "",
        (
            f"- stable rows at >=0.95 sign stability: {len(stable_rows)} / "
            f"{len(bootstrap_rows)}"
        ),
        (
            "- high exogenous load delta: "
            f"{_format_number(float(high_load['observed_delta']))}, "
            f"ci=[{_format_number(float(high_load['ci_low']))}, "
            f"{_format_number(float(high_load['ci_high']))}], "
            f"sign_stability={_format_number(float(high_load['sign_stability']))}"
        ),
        (
            "- high exogenous queue-blind entropy delta: "
            f"{_format_number(float(high_entropy['observed_delta']))}, "
            f"ci=[{_format_number(float(high_entropy['ci_low']))}, "
            f"{_format_number(float(high_entropy['ci_high']))}], "
            f"sign_stability={_format_number(float(high_entropy['sign_stability']))}"
        ),
        (
            "- high exogenous queue-blind task-generation share delta: "
            f"{_format_number(float(high_generation['observed_delta']))}, "
            f"ci=[{_format_number(float(high_generation['ci_low']))}, "
            f"{_format_number(float(high_generation['ci_high']))}], "
            f"sign_stability={_format_number(float(high_generation['sign_stability']))}"
        ),
        "",
        "## Null Control",
        "",
        *[
            f"- {row['condition']}: "
            "baseline_entropy_observed_minus_null="
            f"{_format_number(float(row['transition_entropy_observed_minus_null']))}, "
            "baseline_dwell_max_observed_minus_null="
            f"{_format_number(float(row['dwell_length_max_observed_minus_null']))}"
            for row in null_rows
        ],
        "",
        "## Interpretation",
        "",
        (
            "- Strong sign-stable load growth without a matching sign-stable "
            "queue-blind task-generation dwell-share increase supports the "
            "load-pressure interpretation over independent lobe grammar."
        ),
        (
            "- Strongest baseline observed-minus-null dwell locking: "
            f"{strongest_null['condition']} "
            "dwell_length_max_observed_minus_null="
            f"{_format_number(float(strongest_null['dwell_length_max_observed_minus_null']))}."
        ),
        "",
    ]
    return "\n".join(lines)


def _find_bootstrap_row(
    rows: list[dict[str, Any]],
    high_label: str,
    metric: str,
) -> dict[str, Any]:
    for row in rows:
        if row["high_label"] == high_label and row["metric"] == metric:
            return row
    raise ValueError(f"Missing bootstrap row for {high_label}/{metric}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze bootstrap and null controls for exogenous-arrival artifacts."
    )
    parser.add_argument(
        "--exogenous-arrival-dir",
        required=True,
        help="Existing ohdyn.compare_exogenous_arrivals output directory.",
    )
    parser.add_argument("--out", required=True, help="Output directory for analysis artifacts.")
    parser.add_argument(
        "--bootstrap-reps",
        type=int,
        default=200,
        help="Deterministic paired seed-bootstrap resamples per effect.",
    )
    parser.add_argument(
        "--null-reps",
        type=int,
        default=100,
        help="Deterministic label-count-preserving shuffles per run.",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=314159,
        help="Seed for deterministic bootstrap and null-control generation.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_exogenous_arrival_control_analysis(
            exogenous_arrival_dir=args.exogenous_arrival_dir,
            out_dir=args.out,
            bootstrap_reps=args.bootstrap_reps,
            null_reps=args.null_reps,
            random_seed=args.random_seed,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
