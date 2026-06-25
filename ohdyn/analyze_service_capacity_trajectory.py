"""Analyze lobe-transition structure in service-capacity comparison artifacts."""

from __future__ import annotations

import argparse
import csv
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_attention import _format_number, _format_regime_counts


SERVICE_CAPACITY_TRAJECTORY_FIELDS = (
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
    "backlog_growth_dwell_share_mean",
    "dominant_lobe_label_counts",
    "transition_pair_counts",
    "dwell_length_histogram",
)

SERVICE_CAPACITY_TRAJECTORY_EFFECT_FIELDS = (
    "effect_axis",
    "fixed_label",
    "fixed_value",
    "low_label",
    "high_label",
    "low_value",
    "high_value",
    "queue_depth_per_created_task_mean_delta",
    "queued_task_age_mean_final_mean_delta",
    "transition_entropy_mean_delta",
    "transition_entropy_normalized_mean_delta",
    "dwell_length_mean_delta",
    "dwell_length_max_mean_delta",
    "backlog_growth_dwell_share_mean_delta",
    "interpretation",
)

SERVICE_CAPACITY_TRAJECTORY_BOOTSTRAP_FIELDS = (
    "effect_axis",
    "fixed_label",
    "metric",
    "bootstrap_reps",
    "seed_count",
    "observed_delta",
    "ci_low",
    "ci_high",
    "sign_stability",
)

SERVICE_CAPACITY_TRAJECTORY_NULL_FIELDS = (
    "pressure_label",
    "service_capacity_label",
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

BOOTSTRAP_EFFECT_METRICS = (
    "queue_depth_per_created_task",
    "transition_entropy",
    "transition_entropy_normalized",
    "dwell_length_max",
    "backlog_growth_dwell_share",
)


def run_service_capacity_trajectory_analysis(
    *,
    service_capacity_dir: str | Path,
    out_dir: str | Path,
    bootstrap_reps: int = 200,
    null_reps: int = 100,
    random_seed: int = 271828,
) -> list[dict[str, Any]]:
    source_path = Path(service_capacity_dir)
    output_path = Path(out_dir)
    _validate_source_dir(source_path)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    comparison_rows = _read_comparison_rows(
        source_path / "service_capacity_comparison_metrics.csv"
    )
    rows = [
        _trajectory_row(source_path, comparison_row)
        for comparison_row in comparison_rows
    ]
    effect_rows = _effect_rows(rows)
    per_seed_rows = _per_seed_rows(source_path, comparison_rows)
    bootstrap_rows = _bootstrap_effect_rows(
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
        output_path / "service_capacity_trajectory_metrics.csv",
        SERVICE_CAPACITY_TRAJECTORY_FIELDS,
        rows,
    )
    _write_csv(
        output_path / "service_capacity_trajectory_effects.csv",
        SERVICE_CAPACITY_TRAJECTORY_EFFECT_FIELDS,
        effect_rows,
    )
    _write_csv(
        output_path / "service_capacity_trajectory_bootstrap.csv",
        SERVICE_CAPACITY_TRAJECTORY_BOOTSTRAP_FIELDS,
        bootstrap_rows,
    )
    _write_csv(
        output_path / "service_capacity_trajectory_nulls.csv",
        SERVICE_CAPACITY_TRAJECTORY_NULL_FIELDS,
        null_rows,
    )
    (output_path / "summary.md").write_text(
        _summary(rows, effect_rows, bootstrap_rows, null_rows, source_path)
    )
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
            "service_capacity_trajectory_metrics.csv",
            "service_capacity_trajectory_effects.csv",
            "service_capacity_trajectory_bootstrap.csv",
            "service_capacity_trajectory_nulls.csv",
            "summary.md",
        )
        if (output_path / name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(
            f"Output path {output_path} already contains trajectory artifacts: {names}"
        )


def _read_comparison_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as handle:
        rows = list(csv.DictReader(handle))
    required_fields = {
        "pressure_label",
        "service_capacity_label",
        "task_creation_pressure",
        "work_service_capacity",
        "seed_count",
        "queue_depth_per_created_task_mean",
        "queued_task_age_mean_final_mean",
    }
    missing = required_fields - set(rows[0].keys() if rows else ())
    if missing:
        raise ValueError(f"{path} is missing required fields: {', '.join(sorted(missing))}")
    return rows


def _trajectory_row(
    source_path: Path,
    comparison_row: dict[str, str],
) -> dict[str, Any]:
    pressure_label = comparison_row["pressure_label"]
    service_label = comparison_row["service_capacity_label"]
    run_dirs = sorted(source_path.glob(f"{pressure_label}_{service_label}_seed*"))
    if not run_dirs:
        raise FileNotFoundError(f"No run directories found for {pressure_label}/{service_label}.")

    summaries = [_run_lobe_summary(run_dir / "metrics.csv") for run_dir in run_dirs]
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
        "backlog_growth_dwell_share_mean": _mean_values(
            [float(summary["backlog_growth_dwell_share"]) for summary in summaries]
        ),
        "dominant_lobe_label_counts": _format_regime_counts(dominant_lobes),
        "transition_pair_counts": _format_regime_counts(transition_pair_counts),
        "dwell_length_histogram": _format_regime_counts(dwell_length_histogram),
    }


def _per_seed_rows(
    source_path: Path,
    comparison_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for comparison_row in comparison_rows:
        pressure_label = comparison_row["pressure_label"]
        service_label = comparison_row["service_capacity_label"]
        run_dirs = sorted(source_path.glob(f"{pressure_label}_{service_label}_seed*"))
        for run_dir in run_dirs:
            metrics_path = run_dir / "metrics.csv"
            lobe_summary = _run_lobe_summary(metrics_path)
            final_metrics = _final_metrics(metrics_path)
            rows.append(
                {
                    "pressure_label": pressure_label,
                    "service_capacity_label": service_label,
                    "seed": _seed_from_run_dir(run_dir),
                    "queue_depth_per_created_task": _safe_ratio(
                        float(final_metrics["queue_depth"]),
                        float(final_metrics["tasks_created_total"]),
                    ),
                    "transition_entropy": float(lobe_summary["transition_entropy"]),
                    "transition_entropy_normalized": float(
                        lobe_summary["transition_entropy_normalized"]
                    ),
                    "dwell_length_max": float(lobe_summary["dwell_length_max"]),
                    "backlog_growth_dwell_share": float(
                        lobe_summary["backlog_growth_dwell_share"]
                    ),
                }
            )
    return rows


def _seed_from_run_dir(run_dir: Path) -> int:
    try:
        return int(run_dir.name.rsplit("_seed", maxsplit=1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Cannot parse seed from run directory {run_dir}.") from exc


def _final_metrics(metrics_path: Path) -> dict[str, str]:
    with metrics_path.open() as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{metrics_path} contains no metric rows.")
    return rows[-1]


def _run_lobe_summary(metrics_path: Path) -> dict[str, Any]:
    if not metrics_path.is_file():
        raise FileNotFoundError(f"Missing metrics artifact: {metrics_path}")
    with metrics_path.open() as handle:
        labels = [
            row["baseline_lobe_label"]
            for row in csv.DictReader(handle)
        ]
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
    dominant_label = max(label_ticks.items(), key=lambda item: (item[1], item[0]))[0]
    return {
        "transition_count": len(transition_pairs),
        "transition_entropy": _entropy(transition_pairs),
        "transition_entropy_normalized": _normalized_entropy(transition_pairs),
        "transition_pair_counts": Counter(transition_pairs),
        "dwell_run_count": len(dwell_runs),
        "dwell_length_mean": _mean_values([float(length) for length in dwell_lengths]),
        "dwell_length_max": max(dwell_lengths),
        "backlog_growth_dwell_share": _safe_ratio(
            float(label_ticks["backlog_growth"]),
            float(len(labels)),
        ),
        "dwell_length_histogram": Counter(str(length) for length in dwell_lengths),
        "dominant_lobe_label": dominant_label,
    }


def _labels_from_metrics(metrics_path: Path) -> list[str]:
    if not metrics_path.is_file():
        raise FileNotFoundError(f"Missing metrics artifact: {metrics_path}")
    with metrics_path.open() as handle:
        labels = [row["baseline_lobe_label"] for row in csv.DictReader(handle)]
    if not labels:
        raise ValueError(f"{metrics_path} contains no metric rows.")
    return labels


def _lobe_summary_from_labels(labels: list[str]) -> dict[str, Any]:
    transition_pairs = [
        f"{previous}->{current}"
        for previous, current in zip(labels, labels[1:])
        if previous != current
    ]
    dwell_runs = _dwell_runs(labels)
    dwell_lengths = [length for _, length in dwell_runs]
    label_ticks = Counter(labels)
    return {
        "transition_count": len(transition_pairs),
        "transition_entropy": _entropy(transition_pairs),
        "transition_entropy_normalized": _normalized_entropy(transition_pairs),
        "dwell_length_max": max(dwell_lengths),
        "backlog_growth_dwell_share": _safe_ratio(
            float(label_ticks["backlog_growth"]),
            float(len(labels)),
        ),
    }


def _dwell_runs(labels: list[str]) -> list[tuple[str, int]]:
    runs: list[tuple[str, int]] = []
    current_label = labels[0]
    current_length = 1
    for label in labels[1:]:
        if label == current_label:
            current_length += 1
        else:
            runs.append((current_label, current_length))
            current_label = label
            current_length = 1
    runs.append((current_label, current_length))
    return runs


def _entropy(values: list[str]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    total = float(sum(counts.values()))
    entropy = -sum((count / total) * math.log2(count / total) for count in counts.values())
    return round(entropy, 6)


def _normalized_entropy(values: list[str]) -> float:
    if not values:
        return 0.0
    unique_count = len(set(values))
    if unique_count <= 1:
        return 0.0
    return round(_entropy(values) / math.log2(unique_count), 6)


def _mean_values(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _write_csv(
    path: Path,
    fieldnames: tuple[str, ...],
    rows: list[dict[str, Any]],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


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
                interpretation=(
                    "fixed-pressure high-minus-low service-capacity trajectory effect"
                ),
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
                interpretation=(
                    "fixed-service extreme-minus-normal demand-pressure trajectory effect"
                ),
            )
        )
    return effect_rows


def _bootstrap_effect_rows(
    per_seed_rows: list[dict[str, Any]],
    *,
    reps: int,
    random_seed: int,
) -> list[dict[str, Any]]:
    if reps <= 0:
        raise ValueError("bootstrap_reps must be positive.")
    seeds = sorted({int(row["seed"]) for row in per_seed_rows})
    by_cell_seed = {
        (
            str(row["pressure_label"]),
            str(row["service_capacity_label"]),
            int(row["seed"]),
        ): row
        for row in per_seed_rows
    }
    rng = random.Random(random_seed)
    rows: list[dict[str, Any]] = []
    for contrast in _effect_contrasts():
        low_key = (contrast["low_pressure"], contrast["low_service"])
        high_key = (contrast["high_pressure"], contrast["high_service"])
        for metric in BOOTSTRAP_EFFECT_METRICS:
            observed_delta = _paired_delta_for_seeds(
                by_cell_seed,
                seeds,
                low_key=low_key,
                high_key=high_key,
                metric=metric,
            )
            deltas = [
                _paired_delta_for_seeds(
                    by_cell_seed,
                    [rng.choice(seeds) for _ in seeds],
                    low_key=low_key,
                    high_key=high_key,
                    metric=metric,
                )
                for _ in range(reps)
            ]
            rows.append(
                {
                    "effect_axis": contrast["effect_axis"],
                    "fixed_label": contrast["fixed_label"],
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


def _effect_contrasts() -> list[dict[str, str]]:
    contrasts: list[dict[str, str]] = []
    for pressure_label in ("normal_pressure", "high_pressure", "extreme_pressure"):
        contrasts.append(
            {
                "effect_axis": "service_capacity",
                "fixed_label": pressure_label,
                "low_pressure": pressure_label,
                "low_service": "low_service",
                "high_pressure": pressure_label,
                "high_service": "high_service",
            }
        )
    for service_label in ("low_service", "baseline_service", "high_service"):
        contrasts.append(
            {
                "effect_axis": "task_creation_pressure",
                "fixed_label": service_label,
                "low_pressure": "normal_pressure",
                "low_service": service_label,
                "high_pressure": "extreme_pressure",
                "high_service": service_label,
            }
        )
    return contrasts


def _paired_delta_for_seeds(
    by_cell_seed: dict[tuple[str, str, int], dict[str, Any]],
    seeds: list[int],
    *,
    low_key: tuple[str, str],
    high_key: tuple[str, str],
    metric: str,
) -> float:
    deltas = []
    for seed in seeds:
        low_row = by_cell_seed[(low_key[0], low_key[1], seed)]
        high_row = by_cell_seed[(high_key[0], high_key[1], seed)]
        deltas.append(float(high_row[metric]) - float(low_row[metric]))
    return _mean_values(deltas)


def _quantile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = round((len(sorted_values) - 1) * quantile)
    return round(sorted_values[index], 6)


def _sign_stability(values: list[float], observed_delta: float) -> float:
    if not values or observed_delta == 0:
        return 0.0
    if observed_delta > 0:
        stable = sum(1 for value in values if value > 0)
    else:
        stable = sum(1 for value in values if value < 0)
    return _safe_ratio(float(stable), float(len(values)))


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
        pressure_label = comparison_row["pressure_label"]
        service_label = comparison_row["service_capacity_label"]
        run_dirs = sorted(source_path.glob(f"{pressure_label}_{service_label}_seed*"))
        observed_summaries: list[dict[str, Any]] = []
        null_summaries: list[dict[str, Any]] = []
        for run_dir in run_dirs:
            labels = _labels_from_metrics(run_dir / "metrics.csv")
            observed_summaries.append(_lobe_summary_from_labels(labels))
            for rep in range(reps):
                shuffled_labels = list(labels)
                rng = random.Random(
                    f"{random_seed}:{pressure_label}:{service_label}:{run_dir.name}:{rep}"
                )
                rng.shuffle(shuffled_labels)
                null_summaries.append(_lobe_summary_from_labels(shuffled_labels))
        rows.append(
            {
                "pressure_label": pressure_label,
                "service_capacity_label": service_label,
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


def _null_metric_fields(
    observed_summaries: list[dict[str, Any]],
    null_summaries: list[dict[str, Any]],
    metric: str,
) -> dict[str, float]:
    observed = _mean_values([float(summary[metric]) for summary in observed_summaries])
    null = _mean_values([float(summary[metric]) for summary in null_summaries])
    return {
        f"{metric}_observed_mean": observed,
        f"{metric}_null_mean": null,
        f"{metric}_observed_minus_null": round(observed - null, 6),
    }


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
    raise ValueError(f"Missing trajectory row for {pressure_label}/{service_label}.")


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
        "queue_depth_per_created_task_mean_delta": _delta(
            low_row,
            high_row,
            "queue_depth_per_created_task_mean",
        ),
        "queued_task_age_mean_final_mean_delta": _delta(
            low_row,
            high_row,
            "queued_task_age_mean_final_mean",
        ),
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
        "backlog_growth_dwell_share_mean_delta": _delta(
            low_row,
            high_row,
            "backlog_growth_dwell_share_mean",
        ),
        "interpretation": interpretation,
    }


def _delta(
    low_row: dict[str, Any],
    high_row: dict[str, Any],
    field: str,
) -> float:
    return round(float(high_row[field]) - float(low_row[field]), 6)


def _summary(
    rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    bootstrap_rows: list[dict[str, Any]],
    null_rows: list[dict[str, Any]],
    source_path: Path,
) -> str:
    service_effects = [
        row for row in effect_rows if row["effect_axis"] == "service_capacity"
    ]
    pressure_effects = [
        row for row in effect_rows if row["effect_axis"] == "task_creation_pressure"
    ]
    strongest_pressure_locking = max(
        pressure_effects,
        key=lambda row: float(row["backlog_growth_dwell_share_mean_delta"]),
    )
    strongest_entropy_gain = max(
        service_effects,
        key=lambda row: float(row["transition_entropy_mean_delta"]),
    )
    stable_bootstrap_rows = [
        row for row in bootstrap_rows if float(row["sign_stability"]) >= 0.95
    ]
    strongest_null_locking = max(
        null_rows,
        key=lambda row: float(row["dwell_length_max_observed_minus_null"]),
    )
    lines = [
        "# A2 service-capacity trajectory analysis",
        "",
        f"- source: {source_path}",
        f"- grid rows: {len(rows)}",
        "",
        "## Grid trajectory metrics",
        "",
        *[
            f"- {row['pressure_label']} / {row['service_capacity_label']}: "
            f"queue_per_created={row['queue_depth_per_created_task_mean']}, "
            f"queued_age_final={row['queued_task_age_mean_final_mean']}, "
            f"transition_entropy={row['transition_entropy_mean']}, "
            f"normalized_entropy={row['transition_entropy_normalized_mean']}, "
            f"dwell_length_mean={row['dwell_length_mean']}, "
            f"dwell_length_max_mean={row['dwell_length_max_mean']}, "
            f"backlog_growth_dwell_share={row['backlog_growth_dwell_share_mean']}, "
            f"dominant_lobes={row['dominant_lobe_label_counts']}"
            for row in rows
        ],
        "",
        "## Fixed-pressure service-capacity trajectory effects",
        "",
        *[
            f"- {row['fixed_label']}: "
            "queue_per_created_delta="
            f"{_format_number(float(row['queue_depth_per_created_task_mean_delta']))}, "
            "transition_entropy_delta="
            f"{_format_number(float(row['transition_entropy_mean_delta']))}, "
            "dwell_length_max_delta="
            f"{_format_number(float(row['dwell_length_max_mean_delta']))}, "
            "backlog_growth_dwell_share_delta="
            f"{_format_number(float(row['backlog_growth_dwell_share_mean_delta']))}"
            for row in service_effects
        ],
        "",
        "## Fixed-service demand-pressure trajectory effects",
        "",
        *[
            f"- {row['fixed_label']}: "
            "queue_per_created_delta="
            f"{_format_number(float(row['queue_depth_per_created_task_mean_delta']))}, "
            "transition_entropy_delta="
            f"{_format_number(float(row['transition_entropy_mean_delta']))}, "
            "dwell_length_max_delta="
            f"{_format_number(float(row['dwell_length_max_mean_delta']))}, "
            "backlog_growth_dwell_share_delta="
            f"{_format_number(float(row['backlog_growth_dwell_share_mean_delta']))}"
            for row in pressure_effects
        ],
        "",
        "## Paired bootstrap uncertainty",
        "",
        (
            "- paired seed bootstrap rows: "
            f"{len(bootstrap_rows)}; sign-stable rows at >=0.95: "
            f"{len(stable_bootstrap_rows)}"
        ),
        *[
            f"- {row['effect_axis']} / {row['fixed_label']} / {row['metric']}: "
            f"delta={_format_number(float(row['observed_delta']))}, "
            f"ci=[{_format_number(float(row['ci_low']))}, "
            f"{_format_number(float(row['ci_high']))}], "
            f"sign_stability={_format_number(float(row['sign_stability']))}"
            for row in bootstrap_rows
            if row["metric"] in {"transition_entropy", "dwell_length_max"}
        ],
        "",
        "## Label-count null control",
        "",
        *[
            f"- {row['pressure_label']} / {row['service_capacity_label']}: "
            "transition_entropy_observed_minus_null="
            f"{_format_number(float(row['transition_entropy_observed_minus_null']))}, "
            "normalized_entropy_observed_minus_null="
            f"{_format_number(float(row['transition_entropy_normalized_observed_minus_null']))}, "
            "dwell_length_max_observed_minus_null="
            f"{_format_number(float(row['dwell_length_max_observed_minus_null']))}"
            for row in null_rows
        ],
        "",
        "## Interpretation",
        "",
        (
            "- Strongest fixed-service pressure locking by backlog dwell share: "
            f"{strongest_pressure_locking['fixed_label']} "
            "backlog_growth_dwell_share_delta="
            f"{_format_number(float(strongest_pressure_locking['backlog_growth_dwell_share_mean_delta']))}."
        ),
        (
            "- Strongest fixed-pressure service-capacity entropy gain: "
            f"{strongest_entropy_gain['fixed_label']} "
            "transition_entropy_delta="
            f"{_format_number(float(strongest_entropy_gain['transition_entropy_mean_delta']))}."
        ),
        (
            "- Compare these trajectory deltas with queue_per_created deltas before "
            "treating raw queue depth as an emergent lobe-dynamics result."
        ),
        (
            "- Strongest observed-minus-null dwell locking: "
            f"{strongest_null_locking['pressure_label']} / "
            f"{strongest_null_locking['service_capacity_label']} "
            "dwell_length_max_observed_minus_null="
            f"{_format_number(float(strongest_null_locking['dwell_length_max_observed_minus_null']))}."
        ),
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze lobe trajectories in service-capacity comparison artifacts."
    )
    parser.add_argument(
        "--service-capacity-dir",
        required=True,
        help="Existing ohdyn.compare_service_capacity output directory.",
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
        default=271828,
        help="Seed for deterministic bootstrap and null-control generation.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_service_capacity_trajectory_analysis(
            service_capacity_dir=args.service_capacity_dir,
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
