"""Analyze lagged service/queue-flow synchronization from existing artifacts."""

from __future__ import annotations

import argparse
import csv
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
    "service_load_change_best_lagged_corr_mean_delta",
    "flow_balance_queue_delta_same_tick_corr_mean_delta",
    "interpretation",
)


def run_lagged_service_sync_analysis(
    *,
    service_capacity_dir: str | Path = DEFAULT_SERVICE_CAPACITY_DIR,
    exogenous_arrival_dir: str | Path = DEFAULT_EXOGENOUS_ARRIVAL_DIR,
    out_dir: str | Path,
) -> list[dict[str, Any]]:
    service_path = Path(service_capacity_dir)
    exogenous_path = Path(exogenous_arrival_dir)
    output_path = Path(out_dir)
    _validate_source_dirs(service_path, exogenous_path)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    rows = _service_rows(service_path) + _exogenous_rows(exogenous_path)
    effect_rows = _effect_rows(rows)
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
        _summary(rows, effect_rows, service_path, exogenous_path)
    )
    return rows


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
    summaries = [_run_sync_summary(run_dir / "metrics.csv") for run_dir in run_dirs]
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
    }


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
    return {
        "service_completion_lag_minus1_corr": _lagged_corr(
            service_opportunity,
            completion_fraction,
            -1,
        ),
        "service_completion_lag_plus1_corr": _lagged_corr(
            service_opportunity,
            completion_fraction,
            1,
        ),
        "service_load_change_lag_minus1_corr": _lagged_corr(
            service_for_load_change,
            load_change,
            -1,
        ),
        "service_load_change_lag_plus1_corr": _lagged_corr(
            service_for_load_change,
            load_change,
            1,
        ),
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


def _effect_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
) -> dict[str, Any]:
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
        "service_load_change_best_lagged_corr_mean_delta": _delta(
            low_row,
            high_row,
            "service_load_change_best_lagged_corr_mean",
        ),
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


def _summary(
    rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    service_path: Path,
    exogenous_path: Path,
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
            f"{_format_number(float(strongest_completion['service_completion_best_lagged_corr_mean_delta']))}."
        ),
        (
            "- Strongest lagged service/load-change shift: "
            f"{strongest_load_change['source_family']} {strongest_load_change['low_label']} -> "
            f"{strongest_load_change['high_label']} = "
            f"{_format_number(float(strongest_load_change['service_load_change_best_lagged_corr_mean_delta']))}."
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
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), lineterminator="\n")
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_lagged_service_sync_analysis(
            service_capacity_dir=args.service_capacity_dir,
            exogenous_arrival_dir=args.exogenous_arrival_dir,
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
