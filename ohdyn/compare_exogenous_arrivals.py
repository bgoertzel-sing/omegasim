"""Compare frozen exogenous-arrival rates against an endogenous control."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from ohdyn.analyze_queue_blind_lobes import _queue_blind_label
from ohdyn.analyze_service_capacity_trajectory import (
    _dwell_runs,
    _entropy,
    _normalized_entropy,
    _safe_ratio,
)
from ohdyn.calibrate_exogenous_arrivals import BASELINE_ARRIVAL_SHARES
from ohdyn.compare_attention import DEFAULT_SEEDS, _format_number, _format_regime_counts
from ohdyn.config import OmegaConfig, load_config
from ohdyn.run import run_experiment
from ohdyn.sim import SimulationResult


DEFAULT_ENDOGENOUS_CONTROL_CONFIG = Path("configs/a2_attention_smoke.yaml")
DEFAULT_LOW_EXOGENOUS_CONFIG = Path("configs/a2_exogenous_arrivals_low.yaml")
DEFAULT_MEDIUM_EXOGENOUS_CONFIG = Path("configs/a2_exogenous_arrivals_medium.yaml")
DEFAULT_HIGH_EXOGENOUS_CONFIG = Path("configs/a2_exogenous_arrivals_high.yaml")

EXOGENOUS_COMPARISON_FIELDS = (
    "condition",
    "config",
    "rate_per_tick",
    "task_creation_pressure",
    "work_service_capacity",
    "seed_count",
    "run_count",
    "agent_tasks_created_mean",
    "exogenous_tasks_created_mean",
    "tasks_created_mean",
    "tasks_completed_mean",
    "work_events_mean",
    "completion_fraction_mean",
    "queue_depth_mean",
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
    "attention_capture_pressure_max_final_mean",
    "baseline_lobe_transition_count_mean",
    "baseline_lobe_transition_entropy_mean",
    "baseline_lobe_transition_entropy_normalized_mean",
    "baseline_lobe_dwell_length_mean",
    "baseline_lobe_dwell_length_max_mean",
    "baseline_lobe_backlog_growth_dwell_share_mean",
    "queue_blind_transition_entropy_mean",
    "queue_blind_transition_entropy_normalized_mean",
    "queue_blind_task_generation_dwell_share_mean",
    "queue_blind_execution_dwell_share_mean",
)

EXOGENOUS_EFFECT_FIELDS = (
    "effect_axis",
    "low_label",
    "high_label",
    "low_value",
    "high_value",
    "tasks_created_mean_delta",
    "exogenous_tasks_created_mean_delta",
    "queue_depth_per_created_task_mean_delta",
    "queue_depth_per_created_completed_balance_mean_delta",
    "completion_fraction_mean_delta",
    "queued_task_age_mean_final_mean_delta",
    "baseline_lobe_transition_entropy_mean_delta",
    "baseline_lobe_dwell_length_max_mean_delta",
    "baseline_lobe_backlog_growth_dwell_share_mean_delta",
    "queue_blind_transition_entropy_mean_delta",
    "queue_blind_task_generation_dwell_share_mean_delta",
    "queue_blind_execution_dwell_share_mean_delta",
    "interpretation",
)


def run_exogenous_arrival_comparison(
    *,
    endogenous_control_config: str | Path = DEFAULT_ENDOGENOUS_CONTROL_CONFIG,
    low_exogenous_config: str | Path = DEFAULT_LOW_EXOGENOUS_CONFIG,
    medium_exogenous_config: str | Path = DEFAULT_MEDIUM_EXOGENOUS_CONFIG,
    high_exogenous_config: str | Path = DEFAULT_HIGH_EXOGENOUS_CONFIG,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    out_dir: str | Path,
) -> list[dict[str, Any]]:
    _validate_seeds(seeds)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    conditions = (
        ("endogenous_control", Path(endogenous_control_config)),
        ("exogenous_low", Path(low_exogenous_config)),
        ("exogenous_medium", Path(medium_exogenous_config)),
        ("exogenous_high", Path(high_exogenous_config)),
    )
    _validate_conditions(conditions)

    rows: list[dict[str, Any]] = []
    for condition, config_path in conditions:
        results = []
        for seed in seeds:
            run_dir = output_path / f"{condition}_seed{seed}"
            results.append(run_experiment(config_path, seed=seed, out_dir=run_dir))
        rows.append(_aggregate_row(condition, config_path, results))

    effect_rows = _effect_rows(rows)
    _write_csv(output_path / "exogenous_arrival_comparison_metrics.csv", EXOGENOUS_COMPARISON_FIELDS, rows)
    _write_csv(output_path / "exogenous_arrival_effects.csv", EXOGENOUS_EFFECT_FIELDS, effect_rows)
    (output_path / "summary.md").write_text(_summary(rows, effect_rows, seeds))
    return rows


def _validate_seeds(seeds: tuple[int, ...]) -> None:
    if not seeds:
        raise ValueError("At least one seed is required.")
    invalid = [
        seed
        for seed in seeds
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0
    ]
    if invalid:
        raise ValueError("Seeds must be non-negative integers.")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must not contain duplicates.")


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        name
        for name in (
            "exogenous_arrival_comparison_metrics.csv",
            "exogenous_arrival_effects.csv",
            "summary.md",
        )
        if (output_path / name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(
            f"Output path {output_path} already contains exogenous-arrival artifacts: {names}"
        )


def _validate_conditions(conditions: tuple[tuple[str, Path], ...]) -> None:
    loaded = [(label, path, load_config(path)) for label, path in conditions]
    rates = []
    for label, path, cfg in loaded:
        _validate_baseline_shape(path, cfg)
        if label == "endogenous_control":
            if _exogenous_enabled(cfg):
                raise ValueError(f"{path} must not enable exogenous arrivals.")
            rates.append(0.0)
            continue
        if not _exogenous_enabled(cfg):
            raise ValueError(f"{path} must enable exogenous arrivals.")
        assert cfg.exogenous_arrivals is not None
        if cfg.exogenous_arrivals.task_class_shares() != BASELINE_ARRIVAL_SHARES:
            raise ValueError(f"{path} must use baseline exogenous arrival shares.")
        rates.append(cfg.exogenous_arrivals.rate_per_tick)
    if not rates[0] == 0.0 < rates[1] < rates[2] < rates[3]:
        joined = ", ".join(
            f"{path}={rate}" for (_, path, _), rate in zip(loaded, rates, strict=True)
        )
        raise ValueError(f"Exogenous rates must be frozen and increasing: {joined}")


def _validate_baseline_shape(path: Path, cfg: OmegaConfig) -> None:
    if cfg.attention_policy is None:
        raise ValueError(f"{path} must enable attention_policy.")
    if cfg.attention_policy.shares() != BASELINE_ARRIVAL_SHARES:
        raise ValueError(f"{path} must use baseline attention shares.")
    if cfg.attention_policy.selection_strategy != "quota_balance":
        raise ValueError(f"{path} must use quota_balance selection_strategy.")
    if cfg.model.task_creation_pressure != 1.0:
        raise ValueError(f"{path} must use task_creation_pressure 1.0.")
    if cfg.model.work_service_capacity != 1.0:
        raise ValueError(f"{path} must use work_service_capacity 1.0.")


def _exogenous_enabled(cfg: OmegaConfig) -> bool:
    return cfg.exogenous_arrivals is not None and cfg.exogenous_arrivals.enabled


def _aggregate_row(
    condition: str,
    config_path: Path,
    results: list[SimulationResult],
) -> dict[str, Any]:
    last_rows = [result.metrics[-1] for result in results]
    created_values = [float(row["tasks_created_total"]) for row in last_rows]
    completed_values = [float(row["tasks_completed_total"]) for row in last_rows]
    queue_values = [float(row["queue_depth"]) for row in last_rows]
    balances = [
        created - completed
        for created, completed in zip(created_values, completed_values, strict=True)
    ]
    action_totals = [_action_totals(result) for result in results]
    baseline_lobes = [_lobe_summary(result, "baseline") for result in results]
    queue_blind_lobes = [_lobe_summary(result, "queue_blind") for result in results]
    cfg = results[0].config
    rate = 0.0
    if cfg.exogenous_arrivals is not None and cfg.exogenous_arrivals.enabled:
        rate = cfg.exogenous_arrivals.rate_per_tick
    agent_created_values = [
        _agent_tasks_created_total(row)
        for row in last_rows
    ]
    exogenous_created_values = [
        float(row.get("exogenous_tasks_created_total", 0.0))
        for row in last_rows
    ]
    return {
        "condition": condition,
        "config": str(config_path),
        "rate_per_tick": rate,
        "task_creation_pressure": cfg.model.task_creation_pressure,
        "work_service_capacity": cfg.model.work_service_capacity,
        "seed_count": len(results),
        "run_count": len(results),
        "agent_tasks_created_mean": _mean_values(agent_created_values),
        "exogenous_tasks_created_mean": _mean_values(exogenous_created_values),
        "tasks_created_mean": _mean_values(created_values),
        "tasks_completed_mean": _mean_values(completed_values),
        "work_events_mean": _mean_values([float(totals["work_task"]) for totals in action_totals]),
        "completion_fraction_mean": _mean_values(
            [
                _safe_ratio(completed, created)
                for created, completed in zip(created_values, completed_values, strict=True)
            ]
        ),
        "queue_depth_mean": _mean_values(queue_values),
        "created_completed_balance_mean": _mean_values(balances),
        "queue_depth_per_created_task_mean": _mean_values(
            [
                _safe_ratio(queue, created)
                for queue, created in zip(queue_values, created_values, strict=True)
            ]
        ),
        "queue_depth_per_created_completed_balance_mean": _mean_values(
            [
                _safe_ratio(queue, balance)
                for queue, balance in zip(queue_values, balances, strict=True)
            ]
        ),
        "queued_task_age_mean_final_mean": _mean(last_rows, "queued_task_age_mean_tick"),
        "queued_task_age_max_peak_mean": _mean_values(
            [
                max(float(row["queued_task_age_max_tick"]) for row in result.metrics)
                for result in results
            ]
        ),
        "create_task_actions_mean": _mean_values([float(totals["create_task"]) for totals in action_totals]),
        "work_task_actions_mean": _mean_values([float(totals["work_task"]) for totals in action_totals]),
        "message_actions_mean": _mean_values([float(totals["message"]) for totals in action_totals]),
        "idle_actions_mean": _mean_values([float(totals["idle"]) for totals in action_totals]),
        "value_per_work_event_mean": _mean(last_rows, "attention_value_per_work_event_total"),
        "attention_capture_pressure_max_final_mean": _mean(last_rows, "attention_capture_pressure_max_tick"),
        "baseline_lobe_transition_count_mean": _mean_values([summary["transition_count"] for summary in baseline_lobes]),
        "baseline_lobe_transition_entropy_mean": _mean_values([summary["transition_entropy"] for summary in baseline_lobes]),
        "baseline_lobe_transition_entropy_normalized_mean": _mean_values([summary["transition_entropy_normalized"] for summary in baseline_lobes]),
        "baseline_lobe_dwell_length_mean": _mean_values([summary["dwell_length_mean"] for summary in baseline_lobes]),
        "baseline_lobe_dwell_length_max_mean": _mean_values([summary["dwell_length_max"] for summary in baseline_lobes]),
        "baseline_lobe_backlog_growth_dwell_share_mean": _mean_values([summary["backlog_growth_dwell_share"] for summary in baseline_lobes]),
        "queue_blind_transition_entropy_mean": _mean_values([summary["transition_entropy"] for summary in queue_blind_lobes]),
        "queue_blind_transition_entropy_normalized_mean": _mean_values([summary["transition_entropy_normalized"] for summary in queue_blind_lobes]),
        "queue_blind_task_generation_dwell_share_mean": _mean_values([summary["task_generation_dwell_share"] for summary in queue_blind_lobes]),
        "queue_blind_execution_dwell_share_mean": _mean_values([summary["execution_dwell_share"] for summary in queue_blind_lobes]),
    }


def _action_totals(result: SimulationResult) -> dict[str, int]:
    totals = {"create_task": 0, "work_task": 0, "message": 0, "idle": 0}
    for row in result.metrics:
        totals["create_task"] += int(row.get("agent_tasks_created_tick", row["tasks_created_tick"]))
        totals["work_task"] += int(row["tasks_worked_tick"])
        totals["message"] += int(row["messages_sent_tick"])
        totals["idle"] += int(row["idle_tick"])
    return totals


def _agent_tasks_created_total(row: dict[str, Any]) -> float:
    if "agent_tasks_created_total" in row:
        return float(row["agent_tasks_created_total"])
    return float(row["tasks_created_total"])


def _lobe_summary(result: SimulationResult, label_source: str) -> dict[str, float]:
    if label_source == "baseline":
        labels = [str(row["baseline_lobe_label"]) for row in result.metrics]
    elif label_source == "queue_blind":
        labels = [_queue_blind_label({key: str(value) for key, value in row.items()}) for row in result.metrics]
    else:
        raise ValueError(f"Unsupported lobe label source: {label_source}")
    transitions = [
        f"{previous}->{current}"
        for previous, current in zip(labels, labels[1:])
        if previous != current
    ]
    dwell_runs = _dwell_runs(labels)
    dwell_lengths = [length for _, length in dwell_runs]
    label_ticks = Counter(labels)
    return {
        "transition_count": float(len(transitions)),
        "transition_entropy": _entropy(transitions),
        "transition_entropy_normalized": _normalized_entropy(transitions),
        "dwell_length_mean": _mean_values([float(length) for length in dwell_lengths]),
        "dwell_length_max": float(max(dwell_lengths)),
        "backlog_growth_dwell_share": _safe_ratio(float(label_ticks["backlog_growth"]), float(len(labels))),
        "task_generation_dwell_share": _safe_ratio(float(label_ticks["task_generation"]), float(len(labels))),
        "execution_dwell_share": _safe_ratio(float(label_ticks["execution"]), float(len(labels))),
    }


def _effect_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    control = _find_row(rows, "endogenous_control")
    return [
        _delta_row(control, _find_row(rows, condition))
        for condition in ("exogenous_low", "exogenous_medium", "exogenous_high")
    ]


def _find_row(rows: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    for row in rows:
        if str(row["condition"]) == condition:
            return row
    raise ValueError(f"Missing exogenous-arrival row for {condition}.")


def _delta_row(low_row: dict[str, Any], high_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "effect_axis": "exogenous_arrival_rate",
        "low_label": low_row["condition"],
        "high_label": high_row["condition"],
        "low_value": low_row["rate_per_tick"],
        "high_value": high_row["rate_per_tick"],
        "tasks_created_mean_delta": _delta(low_row, high_row, "tasks_created_mean"),
        "exogenous_tasks_created_mean_delta": _delta(low_row, high_row, "exogenous_tasks_created_mean"),
        "queue_depth_per_created_task_mean_delta": _delta(low_row, high_row, "queue_depth_per_created_task_mean"),
        "queue_depth_per_created_completed_balance_mean_delta": _delta(low_row, high_row, "queue_depth_per_created_completed_balance_mean"),
        "completion_fraction_mean_delta": _delta(low_row, high_row, "completion_fraction_mean"),
        "queued_task_age_mean_final_mean_delta": _delta(low_row, high_row, "queued_task_age_mean_final_mean"),
        "baseline_lobe_transition_entropy_mean_delta": _delta(low_row, high_row, "baseline_lobe_transition_entropy_mean"),
        "baseline_lobe_dwell_length_max_mean_delta": _delta(low_row, high_row, "baseline_lobe_dwell_length_max_mean"),
        "baseline_lobe_backlog_growth_dwell_share_mean_delta": _delta(low_row, high_row, "baseline_lobe_backlog_growth_dwell_share_mean"),
        "queue_blind_transition_entropy_mean_delta": _delta(low_row, high_row, "queue_blind_transition_entropy_mean"),
        "queue_blind_task_generation_dwell_share_mean_delta": _delta(low_row, high_row, "queue_blind_task_generation_dwell_share_mean"),
        "queue_blind_execution_dwell_share_mean_delta": _delta(low_row, high_row, "queue_blind_execution_dwell_share_mean"),
        "interpretation": (
            "fixed-action-pressure exogenous-minus-endogenous effect; compare "
            "load-normalized backlog against queue-blind trajectory deltas before "
            "claiming residual lobe dynamics"
        ),
    }


def _delta(low_row: dict[str, Any], high_row: dict[str, Any], field: str) -> float:
    return round(float(high_row[field]) - float(low_row[field]), 6)


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    seeds: tuple[int, ...],
) -> str:
    strongest_queue = max(
        effect_rows,
        key=lambda row: abs(float(row["queue_depth_per_created_task_mean_delta"])),
    )
    strongest_queue_blind = max(
        effect_rows,
        key=lambda row: abs(float(row["queue_blind_transition_entropy_mean_delta"])),
    )
    lines = [
        "# A2 exogenous-arrival comparison scaffold",
        "",
        f"- seeds: {', '.join(str(seed) for seed in seeds)}",
        f"- conditions: {len(rows)}",
        "- task_creation_pressure: fixed at 1.0",
        "- scheduler: quota_balance",
        "- attention and exogenous task-class shares: baseline",
        "",
        "## Load and action accounting",
        "",
        *[
            f"- {row['condition']}: rate={_format_number(float(row['rate_per_tick']))}, "
            f"agent_created_mean={_format_number(float(row['agent_tasks_created_mean']))}, "
            f"exogenous_created_mean={_format_number(float(row['exogenous_tasks_created_mean']))}, "
            f"total_created_mean={_format_number(float(row['tasks_created_mean']))}, "
            f"completed_mean={_format_number(float(row['tasks_completed_mean']))}, "
            f"work_events_mean={_format_number(float(row['work_events_mean']))}, "
            f"queue_per_created={_format_number(float(row['queue_depth_per_created_task_mean']))}"
            for row in rows
        ],
        "",
        "## Trajectory summaries",
        "",
        *[
            f"- {row['condition']}: "
            f"baseline_entropy={_format_number(float(row['baseline_lobe_transition_entropy_mean']))}, "
            f"baseline_backlog_share={_format_number(float(row['baseline_lobe_backlog_growth_dwell_share_mean']))}, "
            f"queue_blind_entropy={_format_number(float(row['queue_blind_transition_entropy_mean']))}, "
            f"queue_blind_task_generation_share={_format_number(float(row['queue_blind_task_generation_dwell_share_mean']))}, "
            f"queue_blind_execution_share={_format_number(float(row['queue_blind_execution_dwell_share_mean']))}"
            for row in rows
        ],
        "",
        "## Endogenous-control deltas",
        "",
        *[
            f"- {row['high_label']}: "
            f"created_delta={_format_number(float(row['tasks_created_mean_delta']))}, "
            f"queue_per_created_delta={_format_number(float(row['queue_depth_per_created_task_mean_delta']))}, "
            f"baseline_entropy_delta={_format_number(float(row['baseline_lobe_transition_entropy_mean_delta']))}, "
            f"queue_blind_entropy_delta={_format_number(float(row['queue_blind_transition_entropy_mean_delta']))}, "
            f"queue_blind_generation_share_delta={_format_number(float(row['queue_blind_task_generation_dwell_share_mean_delta']))}"
            for row in effect_rows
        ],
        "",
        "## Interpretation guardrails",
        "",
        (
            "- Strongest load-normalized backlog delta: "
            f"{strongest_queue['high_label']}="
            f"{_format_number(float(strongest_queue['queue_depth_per_created_task_mean_delta']))}."
        ),
        (
            "- Strongest queue-blind entropy delta: "
            f"{strongest_queue_blind['high_label']}="
            f"{_format_number(float(strongest_queue_blind['queue_blind_transition_entropy_mean_delta']))}."
        ),
        "- Treat this helper as the frozen-rate holdout scaffold; do not interpret small seed smoke outputs as lobe-dynamics evidence.",
        "",
    ]
    return "\n".join(lines)


def _mean(rows: list[dict[str, Any]], field: str) -> float:
    return _mean_values([float(row.get(field, 0.0)) for row in rows])


def _mean_values(values: list[float]) -> float:
    return round(sum(values) / len(values), 6)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare frozen exogenous-arrival rates against endogenous control."
    )
    parser.add_argument("--endogenous-control-config", default=str(DEFAULT_ENDOGENOUS_CONTROL_CONFIG))
    parser.add_argument("--low-exogenous-config", default=str(DEFAULT_LOW_EXOGENOUS_CONFIG))
    parser.add_argument("--medium-exogenous-config", default=str(DEFAULT_MEDIUM_EXOGENOUS_CONFIG))
    parser.add_argument("--high-exogenous-config", default=str(DEFAULT_HIGH_EXOGENOUS_CONFIG))
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_SEEDS),
        help="Deterministic seed set to run for each frozen exogenous condition.",
    )
    parser.add_argument("--out", required=True, help="Output directory for comparison artifacts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_exogenous_arrival_comparison(
            endogenous_control_config=args.endogenous_control_config,
            low_exogenous_config=args.low_exogenous_config,
            medium_exogenous_config=args.medium_exogenous_config,
            high_exogenous_config=args.high_exogenous_config,
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
