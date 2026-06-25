"""Read existing A2 artifacts and summarize A3 queue-flow/service endpoints."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_attention import _format_number


DEFAULT_SERVICE_CAPACITY_DIR = Path("runs/a2_service_capacity_holdout_seed70_99_20260624")
DEFAULT_EXOGENOUS_ARRIVAL_DIR = Path(
    "runs/a2_exogenous_arrival_holdout_seed70_99_20260625_v2"
)

QUEUE_FLOW_SERVICE_FIELDS = (
    "source_family",
    "condition_label",
    "demand_label",
    "service_label",
    "task_creation_pressure",
    "exogenous_rate_per_tick",
    "work_service_capacity",
    "seed_count",
    "run_count",
    "tasks_created_mean",
    "agent_tasks_created_mean",
    "exogenous_tasks_created_mean",
    "tasks_completed_mean",
    "work_events_mean",
    "completion_fraction_mean",
    "created_completed_balance_mean",
    "queue_depth_per_created_task_mean",
    "queue_depth_per_created_completed_balance_mean",
    "queued_task_age_mean_final_mean",
    "queued_task_age_max_peak_mean",
    "create_task_actions_mean",
    "work_task_actions_mean",
    "message_actions_mean",
    "idle_actions_mean",
    "value_per_work_event_mean",
    "service_opportunity_completion_corr_mean",
    "flow_balance_queue_delta_corr_mean",
    "load_normalized_backlog_delta_mean",
    "queued_age_delta_mean",
)

QUEUE_FLOW_SERVICE_EFFECT_FIELDS = (
    "source_family",
    "effect_axis",
    "fixed_label",
    "low_label",
    "high_label",
    "low_value",
    "high_value",
    "queue_depth_per_created_task_mean_delta",
    "queue_depth_per_created_completed_balance_mean_delta",
    "completion_fraction_mean_delta",
    "queued_task_age_mean_final_mean_delta",
    "work_events_mean_delta",
    "service_opportunity_completion_corr_mean_delta",
    "flow_balance_queue_delta_corr_mean_delta",
    "interpretation",
)


def run_queue_flow_service_analysis(
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
    _write_csv(output_path / "queue_flow_service_metrics.csv", QUEUE_FLOW_SERVICE_FIELDS, rows)
    _write_csv(
        output_path / "queue_flow_service_effects.csv",
        QUEUE_FLOW_SERVICE_EFFECT_FIELDS,
        effect_rows,
    )
    (output_path / "summary.md").write_text(
        _summary(rows, effect_rows, service_path, exogenous_path)
    )
    return rows


def _validate_source_dirs(service_path: Path, exogenous_path: Path) -> None:
    _require_files(
        service_path,
        (
            "service_capacity_comparison_metrics.csv",
            "service_capacity_effects.csv",
            "summary.md",
        ),
    )
    _require_files(
        exogenous_path,
        (
            "exogenous_arrival_comparison_metrics.csv",
            "exogenous_arrival_effects.csv",
            "summary.md",
        ),
    )


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
            "queue_flow_service_metrics.csv",
            "queue_flow_service_effects.csv",
            "summary.md",
        )
        if (output_path / name).exists()
    ]
    if collisions:
        raise FileExistsError(
            "Output path "
            f"{output_path} already contains queue-flow/service artifacts: "
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


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path} contains no rows.")
    return rows


def _validate_fields(path: Path, rows: list[dict[str, str]], required: set[str]) -> None:
    missing = required - set(rows[0].keys())
    if missing:
        raise ValueError(f"{path} is missing required fields: {', '.join(sorted(missing))}")


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
    summaries = [_run_summary(run_dir / "metrics.csv") for run_dir in run_dirs]
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
        "tasks_created_mean": _mean(summaries, "tasks_created"),
        "agent_tasks_created_mean": _mean(summaries, "agent_tasks_created"),
        "exogenous_tasks_created_mean": _mean(summaries, "exogenous_tasks_created"),
        "tasks_completed_mean": _mean(summaries, "tasks_completed"),
        "work_events_mean": _mean(summaries, "work_events"),
        "completion_fraction_mean": _mean(summaries, "completion_fraction"),
        "created_completed_balance_mean": _mean(summaries, "created_completed_balance"),
        "queue_depth_per_created_task_mean": _mean(
            summaries,
            "queue_depth_per_created_task",
        ),
        "queue_depth_per_created_completed_balance_mean": _mean(
            summaries,
            "queue_depth_per_created_completed_balance",
        ),
        "queued_task_age_mean_final_mean": _mean(summaries, "queued_task_age_mean_final"),
        "queued_task_age_max_peak_mean": _mean(summaries, "queued_task_age_max_peak"),
        "create_task_actions_mean": _mean(summaries, "create_task_actions"),
        "work_task_actions_mean": _mean(summaries, "work_task_actions"),
        "message_actions_mean": _mean(summaries, "message_actions"),
        "idle_actions_mean": _mean(summaries, "idle_actions"),
        "value_per_work_event_mean": _mean(summaries, "value_per_work_event"),
        "service_opportunity_completion_corr_mean": _mean(
            summaries,
            "service_opportunity_completion_corr",
        ),
        "flow_balance_queue_delta_corr_mean": _mean(
            summaries,
            "flow_balance_queue_delta_corr",
        ),
        "load_normalized_backlog_delta_mean": _mean(
            summaries,
            "load_normalized_backlog_delta",
        ),
        "queued_age_delta_mean": _mean(summaries, "queued_age_delta"),
    }


def _run_summary(metrics_path: Path) -> dict[str, float]:
    rows = _metrics_rows(metrics_path)
    first = rows[0]
    last = rows[-1]
    created = float(last["tasks_created_total"])
    completed = float(last["tasks_completed_total"])
    balance = created - completed
    queue_depth = float(last["queue_depth"])
    agent_created = float(last.get("agent_tasks_created_total", created))
    exogenous_created = float(last.get("exogenous_tasks_created_total", 0.0))
    work_events = sum(float(row["tasks_worked_tick"]) for row in rows)
    create_actions = sum(
        float(row.get("agent_tasks_created_tick", row["tasks_created_tick"]))
        for row in rows
    )
    load_norm_values = [
        _safe_ratio(float(row["queue_depth"]), float(row["tasks_created_total"]))
        for row in rows
    ]
    age_values = [float(row["queued_task_age_mean_tick"]) for row in rows]
    return {
        "tasks_created": created,
        "agent_tasks_created": agent_created,
        "exogenous_tasks_created": exogenous_created,
        "tasks_completed": completed,
        "work_events": work_events,
        "completion_fraction": _safe_ratio(completed, created),
        "created_completed_balance": balance,
        "queue_depth_per_created_task": _safe_ratio(queue_depth, created),
        "queue_depth_per_created_completed_balance": _safe_ratio(queue_depth, balance),
        "queued_task_age_mean_final": float(last["queued_task_age_mean_tick"]),
        "queued_task_age_max_peak": max(float(row["queued_task_age_max_tick"]) for row in rows),
        "create_task_actions": create_actions,
        "work_task_actions": work_events,
        "message_actions": sum(float(row["messages_sent_tick"]) for row in rows),
        "idle_actions": sum(float(row["idle_tick"]) for row in rows),
        "value_per_work_event": float(last.get("attention_value_per_work_event_total", 0.0)),
        "service_opportunity_completion_corr": _pearson(
            [float(row["tasks_worked_tick"]) for row in rows],
            [float(row["tasks_completed_tick"]) for row in rows],
        ),
        "flow_balance_queue_delta_corr": _pearson(
            [float(row["created_completed_balance_tick"]) for row in rows],
            [float(row["queue_delta_tick"]) for row in rows],
        ),
        "load_normalized_backlog_delta": round(load_norm_values[-1] - load_norm_values[0], 6),
        "queued_age_delta": round(age_values[-1] - age_values[0], 6),
    }


def _metrics_rows(metrics_path: Path) -> list[dict[str, str]]:
    if not metrics_path.is_file():
        raise FileNotFoundError(f"Missing metrics artifact: {metrics_path}")
    with metrics_path.open() as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{metrics_path} contains no metric rows.")
    required = {
        "tasks_created_total",
        "tasks_completed_total",
        "queue_depth",
        "tasks_created_tick",
        "tasks_completed_tick",
        "tasks_worked_tick",
        "messages_sent_tick",
        "idle_tick",
        "created_completed_balance_tick",
        "queue_delta_tick",
        "queued_task_age_mean_tick",
        "queued_task_age_max_tick",
    }
    missing = required - set(rows[0].keys())
    if missing:
        raise ValueError(
            f"{metrics_path} is missing required fields: {', '.join(sorted(missing))}"
        )
    return rows


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
                    "fixed-pressure high-minus-low service-capacity A3 queue-flow effect"
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
                    "fixed-service extreme-minus-normal pressure A3 queue-flow effect"
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
                    "fixed-action-pressure exogenous-minus-endogenous A3 queue-flow effect"
                ),
            )
        )
    return effects


def _find_row(
    rows: list[dict[str, Any]],
    source_family: str,
    demand_label: str,
    service_label: str,
) -> dict[str, Any]:
    for row in rows:
        if (
            row["source_family"] == source_family
            and row["demand_label"] == demand_label
            and row["service_label"] == service_label
        ):
            return row
    raise ValueError(f"Missing row for {source_family} / {demand_label} / {service_label}.")


def _find_condition(
    rows: list[dict[str, Any]],
    source_family: str,
    condition_label: str,
) -> dict[str, Any]:
    for row in rows:
        if row["source_family"] == source_family and row["condition_label"] == condition_label:
            return row
    raise ValueError(f"Missing row for {source_family} / {condition_label}.")


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
        "queue_depth_per_created_task_mean_delta": _delta(
            low_row,
            high_row,
            "queue_depth_per_created_task_mean",
        ),
        "queue_depth_per_created_completed_balance_mean_delta": _delta(
            low_row,
            high_row,
            "queue_depth_per_created_completed_balance_mean",
        ),
        "completion_fraction_mean_delta": _delta(
            low_row,
            high_row,
            "completion_fraction_mean",
        ),
        "queued_task_age_mean_final_mean_delta": _delta(
            low_row,
            high_row,
            "queued_task_age_mean_final_mean",
        ),
        "work_events_mean_delta": _delta(low_row, high_row, "work_events_mean"),
        "service_opportunity_completion_corr_mean_delta": _delta(
            low_row,
            high_row,
            "service_opportunity_completion_corr_mean",
        ),
        "flow_balance_queue_delta_corr_mean_delta": _delta(
            low_row,
            high_row,
            "flow_balance_queue_delta_corr_mean",
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


def _delta(low_row: dict[str, Any], high_row: dict[str, Any], field: str) -> float:
    return round(float(high_row[field]) - float(low_row[field]), 6)


def _mean(rows: list[dict[str, float]], field: str) -> float:
    return round(sum(float(row[field]) for row in rows) / len(rows), 6)


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _pearson(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Correlation inputs must have the same length.")
    if len(left) < 2:
        return 0.0
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    left_centered = [value - left_mean for value in left]
    right_centered = [value - right_mean for value in right]
    left_norm = math.sqrt(sum(value * value for value in left_centered))
    right_norm = math.sqrt(sum(value * value for value in right_centered))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    numerator = sum(
        left_value * right_value
        for left_value, right_value in zip(left_centered, right_centered)
    )
    return round(numerator / (left_norm * right_norm), 6)


def _summary(
    rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    service_path: Path,
    exogenous_path: Path,
) -> str:
    strongest_load = max(
        effect_rows,
        key=lambda row: abs(float(row["queue_depth_per_created_task_mean_delta"])),
    )
    strongest_service_sync = max(
        effect_rows,
        key=lambda row: abs(float(row["service_opportunity_completion_corr_mean_delta"])),
    )
    service_rows = [row for row in rows if row["source_family"] == "service_capacity"]
    exogenous_rows = [row for row in rows if row["source_family"] == "exogenous_arrivals"]
    lines = [
        "# A3 queue-flow/service analysis",
        "",
        f"- service-capacity source: `{service_path}`",
        f"- exogenous-arrival source: `{exogenous_path}`",
        f"- condition rows: {len(rows)}",
        "- analysis mode: existing artifacts only; no new simulations or simulator mechanics",
        "",
        "## Service-capacity grid",
        "",
        *[
            f"- {row['condition_label']}: "
            f"created={_format_number(float(row['tasks_created_mean']))}, "
            f"completed={_format_number(float(row['tasks_completed_mean']))}, "
            f"completion_fraction={_format_number(float(row['completion_fraction_mean']))}, "
            f"queue_per_created={_format_number(float(row['queue_depth_per_created_task_mean']))}, "
            f"age_final={_format_number(float(row['queued_task_age_mean_final_mean']))}"
            for row in service_rows
        ],
        "",
        "## Exogenous-demand control",
        "",
        *[
            f"- {row['condition_label']}: "
            f"rate={_format_number(float(row['exogenous_rate_per_tick']))}, "
            f"agent_created={_format_number(float(row['agent_tasks_created_mean']))}, "
            f"exogenous_created={_format_number(float(row['exogenous_tasks_created_mean']))}, "
            f"queue_per_created={_format_number(float(row['queue_depth_per_created_task_mean']))}, "
            f"flow_queue_corr={_format_number(float(row['flow_balance_queue_delta_corr_mean']))}"
            for row in exogenous_rows
        ],
        "",
        "## A3 queue-flow effects",
        "",
        *[
            f"- {row['source_family']} {row['effect_axis']} {row['low_label']} -> "
            f"{row['high_label']}: "
            f"queue_per_created_delta="
            f"{_format_number(float(row['queue_depth_per_created_task_mean_delta']))}, "
            f"completion_fraction_delta="
            f"{_format_number(float(row['completion_fraction_mean_delta']))}, "
            f"service_completion_corr_delta="
            f"{_format_number(float(row['service_opportunity_completion_corr_mean_delta']))}"
            for row in effect_rows
        ],
        "",
        "## Interpretation guardrails",
        "",
        (
            "- Strongest load-normalized backlog effect: "
            f"{strongest_load['source_family']} {strongest_load['low_label']} -> "
            f"{strongest_load['high_label']} = "
            f"{_format_number(float(strongest_load['queue_depth_per_created_task_mean_delta']))}."
        ),
        (
            "- Strongest service/completion correlation shift: "
            f"{strongest_service_sync['source_family']} "
            f"{strongest_service_sync['low_label']} -> "
            f"{strongest_service_sync['high_label']} = "
            f"{_format_number(float(strongest_service_sync['service_opportunity_completion_corr_mean_delta']))}."
        ),
        "- Baseline and queue-blind lobe summaries remain secondary diagnostics, not A3 primary endpoints.",
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
            "Analyze A3 queue-flow/service endpoints from existing A2 comparison artifacts."
        )
    )
    parser.add_argument("--service-capacity-dir", default=str(DEFAULT_SERVICE_CAPACITY_DIR))
    parser.add_argument("--exogenous-arrival-dir", default=str(DEFAULT_EXOGENOUS_ARRIVAL_DIR))
    parser.add_argument("--out", required=True, help="Output directory for A3 artifacts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_queue_flow_service_analysis(
            service_capacity_dir=args.service_capacity_dir,
            exogenous_arrival_dir=args.exogenous_arrival_dir,
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
