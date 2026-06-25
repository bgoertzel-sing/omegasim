"""Analyze lagged service/queue-flow synchronization from existing artifacts."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path
from typing import Any

import yaml

from ohdyn.analyze_queue_flow_service import (
    DEFAULT_EXOGENOUS_ARRIVAL_DIR,
    DEFAULT_SERVICE_CAPACITY_DIR,
    _delta,
    _find_condition,
    _find_row,
    _mean,
    _pearson,
    _read_rows,
    _safe_ratio,
    _validate_fields,
)
from ohdyn.compare_attention import _format_number


LAGGED_SERVICE_SYNC_FIELDS = (
    "source_family",
    "condition_label",
    "demand_label",
    "service_label",
    "task_creation_pressure",
    "exogenous_rate_per_tick",
    "work_service_capacity",
    "seed_count",
    "run_count",
    "service_completion_lag_minus1_corr_mean",
    "service_completion_lag_plus1_corr_mean",
    "service_completion_best_lag",
    "service_completion_best_lagged_corr_mean",
    "service_load_change_lag_minus1_corr_mean",
    "service_load_change_lag_plus1_corr_mean",
    "service_load_change_best_lag",
    "service_load_change_best_lagged_corr_mean",
    "flow_balance_queue_delta_same_tick_corr_mean",
)

LAGGED_SERVICE_SYNC_EFFECT_FIELDS = (
    "source_family",
    "effect_axis",
    "fixed_label",
    "low_label",
    "high_label",
    "low_value",
    "high_value",
    "service_completion_best_lagged_corr_mean_delta",
    "service_completion_paired_seed_count",
    "service_completion_seed_median_delta",
    "service_completion_seed_bootstrap_median_ci_low",
    "service_completion_seed_bootstrap_median_ci_high",
    "service_completion_seed_sign_stability",
    "service_load_change_best_lagged_corr_mean_delta",
    "service_load_change_paired_seed_count",
    "service_load_change_seed_median_delta",
    "service_load_change_seed_bootstrap_median_ci_low",
    "service_load_change_seed_bootstrap_median_ci_high",
    "service_load_change_seed_sign_stability",
    "flow_balance_queue_delta_same_tick_corr_mean_delta",
    "interpretation",
)

DEFAULT_BOOTSTRAP_REPS = 200
DEFAULT_BOOTSTRAP_SEED = 1


def run_lagged_service_sync_analysis(
    *,
    service_capacity_dir: str | Path = DEFAULT_SERVICE_CAPACITY_DIR,
    exogenous_arrival_dir: str | Path = DEFAULT_EXOGENOUS_ARRIVAL_DIR,
    out_dir: str | Path,
    bootstrap_reps: int = DEFAULT_BOOTSTRAP_REPS,
    bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED,
) -> list[dict[str, Any]]:
    _validate_bootstrap_options(bootstrap_reps, bootstrap_seed)
    service_path = Path(service_capacity_dir)
    exogenous_path = Path(exogenous_arrival_dir)
    output_path = Path(out_dir)
    _validate_source_dirs(service_path, exogenous_path)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    rows = _service_rows(service_path) + _exogenous_rows(exogenous_path)
    effect_rows = _effect_rows(
        rows,
        bootstrap_reps=bootstrap_reps,
        bootstrap_seed=bootstrap_seed,
    )
    _write_csv(
        output_path / "lagged_service_sync_metrics.csv",
        LAGGED_SERVICE_SYNC_FIELDS,
        rows,
    )
    _write_csv(
        output_path / "lagged_service_sync_effects.csv",
        LAGGED_SERVICE_SYNC_EFFECT_FIELDS,
        effect_rows,
    )
    (output_path / "summary.md").write_text(
        _summary(
            rows,
            effect_rows,
            service_path,
            exogenous_path,
            bootstrap_reps=bootstrap_reps,
            bootstrap_seed=bootstrap_seed,
        )
    )
    return rows


def _validate_bootstrap_options(bootstrap_reps: int, bootstrap_seed: int) -> None:
    if isinstance(bootstrap_reps, bool) or not isinstance(bootstrap_reps, int):
        raise ValueError("bootstrap_reps must be an integer.")
    if bootstrap_reps <= 0:
        raise ValueError("bootstrap_reps must be positive.")
    if isinstance(bootstrap_seed, bool) or not isinstance(bootstrap_seed, int):
        raise ValueError("bootstrap_seed must be an integer.")


def _validate_source_dirs(service_path: Path, exogenous_path: Path) -> None:
    _require_files(service_path, ("service_capacity_comparison_metrics.csv", "summary.md"))
    _require_files(exogenous_path, ("exogenous_arrival_comparison_metrics.csv", "summary.md"))


def _require_files(source_path: Path, names: tuple[str, ...]) -> None:
    if not source_path.is_dir():
        raise FileNotFoundError(f"Source directory {source_path} does not exist.")
    missing = [name for name in names if not (source_path / name).is_file()]
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
            "lagged_service_sync_metrics.csv",
            "lagged_service_sync_effects.csv",
            "summary.md",
        )
        if (output_path / name).exists()
    ]
    if collisions:
        raise FileExistsError(
            f"Output path {output_path} already contains lagged sync artifacts: "
            f"{', '.join(collisions)}"
        )


def _service_rows(source_path: Path) -> list[dict[str, Any]]:
    rows = _read_rows(source_path / "service_capacity_comparison_metrics.csv")
    required = {
        "pressure_label",
        "service_capacity_label",
        "task_creation_pressure",
        "work_service_capacity",
        "seed_count",
    }
    _validate_fields(source_path / "service_capacity_comparison_metrics.csv", rows, required)
    return [
        _row_from_run_dirs(
            source_family="service_capacity",
            condition_label=f"{row['pressure_label']}/{row['service_capacity_label']}",
            demand_label=str(row["pressure_label"]),
            service_label=str(row["service_capacity_label"]),
            task_creation_pressure=float(row["task_creation_pressure"]),
            exogenous_rate_per_tick=0.0,
            work_service_capacity=float(row["work_service_capacity"]),
            seed_count=int(row["seed_count"]),
            run_dirs=sorted(
                source_path.glob(
                    f"{row['pressure_label']}_{row['service_capacity_label']}_seed*"
                )
            ),
        )
        for row in rows
    ]


def _exogenous_rows(source_path: Path) -> list[dict[str, Any]]:
    rows = _read_rows(source_path / "exogenous_arrival_comparison_metrics.csv")
    required = {
        "condition",
        "rate_per_tick",
        "task_creation_pressure",
        "work_service_capacity",
        "seed_count",
    }
    _validate_fields(source_path / "exogenous_arrival_comparison_metrics.csv", rows, required)
    return [
        _row_from_run_dirs(
            source_family="exogenous_arrivals",
            condition_label=str(row["condition"]),
            demand_label=str(row["condition"]),
            service_label="baseline_service",
            task_creation_pressure=float(row["task_creation_pressure"]),
            exogenous_rate_per_tick=float(row["rate_per_tick"]),
            work_service_capacity=float(row["work_service_capacity"]),
            seed_count=int(row["seed_count"]),
            run_dirs=sorted(source_path.glob(f"{row['condition']}_seed*")),
        )
        for row in rows
    ]


def _row_from_run_dirs(
    *,
    source_family: str,
    condition_label: str,
    demand_label: str,
    service_label: str,
    task_creation_pressure: float,
    exogenous_rate_per_tick: float,
    work_service_capacity: float,
    seed_count: int,
    run_dirs: list[Path],
) -> dict[str, Any]:
    if not run_dirs:
        raise FileNotFoundError(f"No run directories found for {condition_label}.")
    summaries_by_seed = {
        _seed_from_run_dir(run_dir): _run_sync_summary(run_dir / "metrics.csv")
        for run_dir in run_dirs
    }
    summaries = [summaries_by_seed[seed] for seed in sorted(summaries_by_seed)]
    completion_best = _best_lagged_mean(
        summaries,
        "service_completion_lag_minus1_corr",
        "service_completion_lag_plus1_corr",
    )
    load_best = _best_lagged_mean(
        summaries,
        "service_load_change_lag_minus1_corr",
        "service_load_change_lag_plus1_corr",
    )
    return {
        "source_family": source_family,
        "condition_label": condition_label,
        "demand_label": demand_label,
        "service_label": service_label,
        "task_creation_pressure": task_creation_pressure,
        "exogenous_rate_per_tick": exogenous_rate_per_tick,
        "work_service_capacity": work_service_capacity,
        "seed_count": seed_count,
        "run_count": len(run_dirs),
        "service_completion_lag_minus1_corr_mean": _mean(
            summaries,
            "service_completion_lag_minus1_corr",
        ),
        "service_completion_lag_plus1_corr_mean": _mean(
            summaries,
            "service_completion_lag_plus1_corr",
        ),
        "service_completion_best_lag": completion_best["lag"],
        "service_completion_best_lagged_corr_mean": completion_best["value"],
        "service_load_change_lag_minus1_corr_mean": _mean(
            summaries,
            "service_load_change_lag_minus1_corr",
        ),
        "service_load_change_lag_plus1_corr_mean": _mean(
            summaries,
            "service_load_change_lag_plus1_corr",
        ),
        "service_load_change_best_lag": load_best["lag"],
        "service_load_change_best_lagged_corr_mean": load_best["value"],
        "flow_balance_queue_delta_same_tick_corr_mean": _mean(
            summaries,
            "flow_balance_queue_delta_same_tick_corr",
        ),
        "_seed_summaries": summaries_by_seed,
    }


def _seed_from_run_dir(run_dir: Path) -> int:
    marker = "_seed"
    if marker not in run_dir.name:
        raise ValueError(f"Run directory name does not include a seed suffix: {run_dir}")
    seed_text = run_dir.name.rsplit(marker, 1)[1]
    try:
        return int(seed_text)
    except ValueError as exc:
        raise ValueError(f"Run directory seed suffix is not an integer: {run_dir}") from exc


def _run_sync_summary(metrics_path: Path) -> dict[str, float]:
    rows = _metrics_rows(metrics_path)
    service_opportunity = [float(row["tasks_worked_tick"]) for row in rows]
    completion_fraction = [
        _safe_ratio(float(row["tasks_completed_tick"]), float(row["tasks_worked_tick"]))
        for row in rows
    ]
    load_normalized = [
        _safe_ratio(float(row["queue_depth"]), float(row["tasks_created_total"]))
        for row in rows
    ]
    load_change = [
        round(current - previous, 6)
        for previous, current in zip(load_normalized, load_normalized[1:])
    ]
    service_for_load_change = service_opportunity[1:]
    service_completion_lag_minus1 = _lagged_corr(
        service_opportunity,
        completion_fraction,
        -1,
    )
    service_completion_lag_plus1 = _lagged_corr(
        service_opportunity,
        completion_fraction,
        1,
    )
    service_load_change_lag_minus1 = _lagged_corr(
        service_for_load_change,
        load_change,
        -1,
    )
    service_load_change_lag_plus1 = _lagged_corr(
        service_for_load_change,
        load_change,
        1,
    )
    return {
        "service_completion_lag_minus1_corr": service_completion_lag_minus1,
        "service_completion_lag_plus1_corr": service_completion_lag_plus1,
        "service_load_change_lag_minus1_corr": service_load_change_lag_minus1,
        "service_load_change_lag_plus1_corr": service_load_change_lag_plus1,
        "flow_balance_queue_delta_same_tick_corr": _pearson(
            [float(row["created_completed_balance_tick"]) for row in rows],
            [float(row["queue_delta_tick"]) for row in rows],
        ),
    }


def _metrics_rows(metrics_path: Path) -> list[dict[str, str]]:
    if not metrics_path.is_file():
        raise FileNotFoundError(f"Missing metrics artifact: {metrics_path}")
    with metrics_path.open() as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{metrics_path} contains no metric rows.")
    required = {
        "queue_depth",
        "queue_delta_tick",
        "tasks_created_total",
        "tasks_completed_tick",
        "tasks_worked_tick",
        "created_completed_balance_tick",
    }
    missing = required - set(rows[0].keys())
    if missing:
        raise ValueError(
            f"{metrics_path} is missing required fields: {', '.join(sorted(missing))}"
        )
    return rows


def _lagged_corr(left: list[float], right: list[float], lag: int) -> float:
    if lag == 0:
        return _pearson(left, right)
    if abs(lag) >= min(len(left), len(right)):
        return 0.0
    if lag > 0:
        return _pearson(left[:-lag], right[lag:])
    offset = abs(lag)
    return _pearson(left[offset:], right[:-offset])


def _best_lagged_mean(
    summaries: list[dict[str, float]],
    lag_minus_field: str,
    lag_plus_field: str,
) -> dict[str, Any]:
    lag_values = {
        "-1": _mean(summaries, lag_minus_field),
        "+1": _mean(summaries, lag_plus_field),
    }
    lag, value = max(lag_values.items(), key=lambda item: (abs(item[1]), item[0]))
    return {"lag": lag, "value": value}


def _effect_rows(
    rows: list[dict[str, Any]],
    *,
    bootstrap_reps: int,
    bootstrap_seed: int,
) -> list[dict[str, Any]]:
    effects: list[dict[str, Any]] = []
    for pressure_label in ("normal_pressure", "high_pressure", "extreme_pressure"):
        effects.append(
            _delta_row(
                source_family="service_capacity",
                effect_axis="service_capacity",
                fixed_label=pressure_label,
                low_row=_find_row(rows, "service_capacity", pressure_label, "low_service"),
                high_row=_find_row(rows, "service_capacity", pressure_label, "high_service"),
                interpretation=(
                    "fixed-pressure high-minus-low service-capacity lagged sync effect"
                ),
                bootstrap_reps=bootstrap_reps,
                bootstrap_seed=bootstrap_seed,
            )
        )
    for service_label in ("low_service", "baseline_service", "high_service"):
        effects.append(
            _delta_row(
                source_family="service_capacity",
                effect_axis="task_creation_pressure",
                fixed_label=service_label,
                low_row=_find_row(rows, "service_capacity", "normal_pressure", service_label),
                high_row=_find_row(rows, "service_capacity", "extreme_pressure", service_label),
                interpretation=(
                    "fixed-service extreme-minus-normal pressure lagged sync effect"
                ),
                bootstrap_reps=bootstrap_reps,
                bootstrap_seed=bootstrap_seed,
            )
        )

    endogenous = _find_condition(rows, "exogenous_arrivals", "endogenous_control")
    for condition in ("exogenous_low", "exogenous_medium", "exogenous_high"):
        effects.append(
            _delta_row(
                source_family="exogenous_arrivals",
                effect_axis="exogenous_arrival_rate",
                fixed_label="baseline_service",
                low_row=endogenous,
                high_row=_find_condition(rows, "exogenous_arrivals", condition),
                interpretation=(
                    "fixed-action-pressure exogenous-minus-endogenous lagged sync effect"
                ),
                bootstrap_reps=bootstrap_reps,
                bootstrap_seed=bootstrap_seed,
            )
        )
    return effects


def _delta_row(
    *,
    source_family: str,
    effect_axis: str,
    fixed_label: str,
    low_row: dict[str, Any],
    high_row: dict[str, Any],
    interpretation: str,
    bootstrap_reps: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    completion_stats = _paired_seed_delta_stats(
        low_row,
        high_row,
        metric_prefix="service_completion",
        lag_field="service_completion_best_lag",
        observed_delta=_delta(
            low_row,
            high_row,
            "service_completion_best_lagged_corr_mean",
        ),
        bootstrap_reps=bootstrap_reps,
        bootstrap_seed=bootstrap_seed,
    )
    load_change_stats = _paired_seed_delta_stats(
        low_row,
        high_row,
        metric_prefix="service_load_change",
        lag_field="service_load_change_best_lag",
        observed_delta=_delta(
            low_row,
            high_row,
            "service_load_change_best_lagged_corr_mean",
        ),
        bootstrap_reps=bootstrap_reps,
        bootstrap_seed=bootstrap_seed + 1,
    )
    return {
        "source_family": source_family,
        "effect_axis": effect_axis,
        "fixed_label": fixed_label,
        "low_label": low_row["condition_label"],
        "high_label": high_row["condition_label"],
        "low_value": _axis_value(low_row, effect_axis),
        "high_value": _axis_value(high_row, effect_axis),
        "service_completion_best_lagged_corr_mean_delta": _delta(
            low_row,
            high_row,
            "service_completion_best_lagged_corr_mean",
        ),
        "service_completion_paired_seed_count": completion_stats["paired_seed_count"],
        "service_completion_seed_median_delta": completion_stats["seed_median_delta"],
        "service_completion_seed_bootstrap_median_ci_low": completion_stats["ci_low"],
        "service_completion_seed_bootstrap_median_ci_high": completion_stats["ci_high"],
        "service_completion_seed_sign_stability": completion_stats["sign_stability"],
        "service_load_change_best_lagged_corr_mean_delta": _delta(
            low_row,
            high_row,
            "service_load_change_best_lagged_corr_mean",
        ),
        "service_load_change_paired_seed_count": load_change_stats["paired_seed_count"],
        "service_load_change_seed_median_delta": load_change_stats["seed_median_delta"],
        "service_load_change_seed_bootstrap_median_ci_low": load_change_stats["ci_low"],
        "service_load_change_seed_bootstrap_median_ci_high": load_change_stats["ci_high"],
        "service_load_change_seed_sign_stability": load_change_stats["sign_stability"],
        "flow_balance_queue_delta_same_tick_corr_mean_delta": _delta(
            low_row,
            high_row,
            "flow_balance_queue_delta_same_tick_corr_mean",
        ),
        "interpretation": interpretation,
    }


def _axis_value(row: dict[str, Any], effect_axis: str) -> float:
    if effect_axis == "service_capacity":
        return float(row["work_service_capacity"])
    if effect_axis == "exogenous_arrival_rate":
        return float(row["exogenous_rate_per_tick"])
    if effect_axis == "task_creation_pressure":
        return float(row["task_creation_pressure"])
    raise ValueError(f"Unsupported effect axis: {effect_axis}")


def _paired_seed_delta_stats(
    low_row: dict[str, Any],
    high_row: dict[str, Any],
    *,
    metric_prefix: str,
    lag_field: str,
    observed_delta: float,
    bootstrap_reps: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    low_summaries = low_row["_seed_summaries"]
    high_summaries = high_row["_seed_summaries"]
    paired_seeds = sorted(set(low_summaries) & set(high_summaries))
    if not paired_seeds:
        raise ValueError(
            f"No paired seeds for lagged sync effect "
            f"{low_row['condition_label']} -> {high_row['condition_label']}."
        )
    low_metric = _lagged_seed_metric(metric_prefix, str(low_row[lag_field]))
    high_metric = _lagged_seed_metric(metric_prefix, str(high_row[lag_field]))
    deltas = [
        round(
            float(high_summaries[seed][high_metric])
            - float(low_summaries[seed][low_metric]),
            6,
        )
        for seed in paired_seeds
    ]
    rng = random.Random(bootstrap_seed)
    bootstrap_medians = [
        _median([rng.choice(deltas) for _ in deltas]) for _ in range(bootstrap_reps)
    ]
    return {
        "paired_seed_count": len(paired_seeds),
        "seed_median_delta": _median(deltas),
        "ci_low": _quantile(bootstrap_medians, 0.025),
        "ci_high": _quantile(bootstrap_medians, 0.975),
        "sign_stability": _raw_sign_stability(deltas, observed_delta),
    }


def _lagged_seed_metric(metric_prefix: str, lag: str) -> str:
    if lag == "-1":
        return f"{metric_prefix}_lag_minus1_corr"
    if lag == "+1":
        return f"{metric_prefix}_lag_plus1_corr"
    raise ValueError(f"Unsupported lag for paired seed uncertainty: {lag}")


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    midpoint = len(sorted_values) // 2
    if len(sorted_values) % 2 == 1:
        return round(sorted_values[midpoint], 6)
    return round((sorted_values[midpoint - 1] + sorted_values[midpoint]) / 2.0, 6)


def _quantile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = round((len(sorted_values) - 1) * quantile)
    return round(sorted_values[index], 6)


def _raw_sign_stability(values: list[float], observed_delta: float) -> float:
    if not values or observed_delta == 0:
        return 0.0
    if observed_delta > 0:
        stable = sum(1 for value in values if value > 0)
    else:
        stable = sum(1 for value in values if value < 0)
    return _safe_ratio(float(stable), float(len(values)))


def _summary(
    rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    service_path: Path,
    exogenous_path: Path,
    bootstrap_reps: int,
    bootstrap_seed: int,
) -> str:
    strongest_completion = max(
        effect_rows,
        key=lambda row: abs(float(row["service_completion_best_lagged_corr_mean_delta"])),
    )
    strongest_load_change = max(
        effect_rows,
        key=lambda row: abs(float(row["service_load_change_best_lagged_corr_mean_delta"])),
    )
    service_rows = [row for row in rows if row["source_family"] == "service_capacity"]
    exogenous_rows = [row for row in rows if row["source_family"] == "exogenous_arrivals"]
    lines = [
        "# A3 lagged service synchronization analysis",
        "",
        f"- service-capacity source: `{service_path}`",
        f"- exogenous-arrival source: `{exogenous_path}`",
        f"- condition rows: {len(rows)}",
        "- analysis mode: existing artifacts only; no new simulations or simulator mechanics",
        (
            "- primary endpoints: lagged service/completion and service/load-change "
            "correlations at lag -1 or +1"
        ),
        "- diagnostic only: same-tick created-completed balance versus queue delta",
        (
            "- uncertainty: paired seed medians, deterministic bootstrap median CIs, "
            f"and raw seed sign stability; bootstrap_reps={bootstrap_reps}, "
            f"bootstrap_seed={bootstrap_seed}"
        ),
        "",
        "## Service-capacity conditions",
        "",
        *[
            f"- {row['condition_label']}: "
            f"service_completion_best_lag={row['service_completion_best_lag']}, "
            f"service_completion_corr="
            f"{_format_number(float(row['service_completion_best_lagged_corr_mean']))}, "
            f"service_load_change_best_lag={row['service_load_change_best_lag']}, "
            f"service_load_change_corr="
            f"{_format_number(float(row['service_load_change_best_lagged_corr_mean']))}, "
            f"flow_identity_corr="
            f"{_format_number(float(row['flow_balance_queue_delta_same_tick_corr_mean']))}"
            for row in service_rows
        ],
        "",
        "## Exogenous-demand conditions",
        "",
        *[
            f"- {row['condition_label']}: "
            f"rate={_format_number(float(row['exogenous_rate_per_tick']))}, "
            f"service_completion_best_lag={row['service_completion_best_lag']}, "
            f"service_completion_corr="
            f"{_format_number(float(row['service_completion_best_lagged_corr_mean']))}, "
            f"service_load_change_corr="
            f"{_format_number(float(row['service_load_change_best_lagged_corr_mean']))}, "
            f"flow_identity_corr="
            f"{_format_number(float(row['flow_balance_queue_delta_same_tick_corr_mean']))}"
            for row in exogenous_rows
        ],
        "",
        "## Lagged synchronization effects",
        "",
        *[
            f"- {row['source_family']} {row['effect_axis']} {row['low_label']} -> "
            f"{row['high_label']}: "
            f"service_completion_corr_delta="
            f"{_format_number(float(row['service_completion_best_lagged_corr_mean_delta']))}, "
            f"service_load_change_corr_delta="
            f"{_format_number(float(row['service_load_change_best_lagged_corr_mean_delta']))}, "
            f"flow_identity_corr_delta="
            f"{_format_number(float(row['flow_balance_queue_delta_same_tick_corr_mean_delta']))}"
            for row in effect_rows
        ],
        "",
        "## Interpretation guardrails",
        "",
        (
            "- Strongest lagged service/completion shift: "
            f"{strongest_completion['source_family']} {strongest_completion['low_label']} -> "
            f"{strongest_completion['high_label']} = "
            f"{_format_number(float(strongest_completion['service_completion_best_lagged_corr_mean_delta']))}; "
            "seed_median_delta="
            f"{_format_number(float(strongest_completion['service_completion_seed_median_delta']))}, "
            "bootstrap_median_ci=["
            f"{_format_number(float(strongest_completion['service_completion_seed_bootstrap_median_ci_low']))}, "
            f"{_format_number(float(strongest_completion['service_completion_seed_bootstrap_median_ci_high']))}], "
            "sign_stability="
            f"{_format_number(float(strongest_completion['service_completion_seed_sign_stability']))}."
        ),
        (
            "- Strongest lagged service/load-change shift: "
            f"{strongest_load_change['source_family']} {strongest_load_change['low_label']} -> "
            f"{strongest_load_change['high_label']} = "
            f"{_format_number(float(strongest_load_change['service_load_change_best_lagged_corr_mean_delta']))}; "
            "seed_median_delta="
            f"{_format_number(float(strongest_load_change['service_load_change_seed_median_delta']))}, "
            "bootstrap_median_ci=["
            f"{_format_number(float(strongest_load_change['service_load_change_seed_bootstrap_median_ci_low']))}, "
            f"{_format_number(float(strongest_load_change['service_load_change_seed_bootstrap_median_ci_high']))}], "
            "sign_stability="
            f"{_format_number(float(strongest_load_change['service_load_change_seed_sign_stability']))}."
        ),
        (
            "- The same-tick flow-balance correlation is retained only as an artifact "
            "identity diagnostic and is excluded from the primary synchronization endpoint."
        ),
        "- Baseline and queue-blind lobe summaries remain secondary diagnostics.",
        "",
    ]
    return "\n".join(lines)


def _write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(fieldnames),
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze lagged A3 service/queue-flow synchronization from existing artifacts."
        )
    )
    parser.add_argument("--service-capacity-dir", default=str(DEFAULT_SERVICE_CAPACITY_DIR))
    parser.add_argument("--exogenous-arrival-dir", default=str(DEFAULT_EXOGENOUS_ARRIVAL_DIR))
    parser.add_argument("--out", required=True, help="Output directory for lagged sync artifacts.")
    parser.add_argument(
        "--bootstrap-reps",
        type=int,
        default=DEFAULT_BOOTSTRAP_REPS,
        help="Deterministic paired seed-bootstrap resamples for median delta CIs.",
    )
    parser.add_argument(
        "--bootstrap-seed",
        type=int,
        default=DEFAULT_BOOTSTRAP_SEED,
        help="Pseudo-random seed for deterministic bootstrap resampling.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_lagged_service_sync_analysis(
            service_capacity_dir=args.service_capacity_dir,
            exogenous_arrival_dir=args.exogenous_arrival_dir,
            out_dir=args.out,
            bootstrap_reps=args.bootstrap_reps,
            bootstrap_seed=args.bootstrap_seed,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
