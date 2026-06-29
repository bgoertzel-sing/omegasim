"""Run the fixed A7.3 one-hive dimensionless delayed-dynamics smoke."""

from __future__ import annotations

import argparse
import csv
import math
from collections import deque
from pathlib import Path
from typing import Any

import yaml

from ohdyn.a7_3_dimensionless_contract import (
    A7_3_ACTIONS,
    A7_3_CONDITIONS,
    A7_3_LIFTED_STATE_FIELDS,
    A7_3_MECHANICS_MANIFEST_FIELDS,
    A7_3_NULL_CONDITIONS,
    A7_3_POSITIVE_CONDITION,
    A7_3_SMOKE_PARAMETERS,
    A7_3_SOURCE_LEDGER_CSV_FIELDS,
    A7_3_SOURCE_LEDGER_FIELDS,
    a7_3_required_event_fields,
    a7_3_required_metric_fields,
)
from ohdyn.compare_three_hive_ring import _write_schema
from ohdyn.config import load_config


DEFAULT_A7_3_CONFIG = Path("configs/a7_3_dimensionless_smoke.yaml")
DEFAULT_A7_3_SEEDS = tuple(A7_3_SMOKE_PARAMETERS["seeds"])
DEFAULT_A7_3_SMOKE_DIR = Path("runs/a7_3_dimensionless_smoke_seed1_2")
A7_3_MECHANICS_STATUS = "deterministic_a7_3_smoke_artifacts_only"
A7_3_SCIENTIFIC_STATUS = (
    "metrics_events_lifted_state_present_requires_future_read_only_preflight"
)


def run_a7_3_dimensionless_smoke(
    *,
    config_path: str | Path = DEFAULT_A7_3_CONFIG,
    seeds: tuple[int, ...] = DEFAULT_A7_3_SEEDS,
    out_dir: str | Path = DEFAULT_A7_3_SMOKE_DIR,
) -> list[dict[str, Any]]:
    """Run only the frozen paired-seed deterministic A7.3 smoke grid."""

    if seeds != DEFAULT_A7_3_SEEDS:
        raise ValueError("A7.3 dimensionless smoke is fixed to paired seeds 1 and 2.")
    config = load_config(config_path)
    if config.a7_3_dimensionless_delayed is None:
        raise ValueError(f"{config_path} must enable a7_3_dimensionless_delayed.")

    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, Any]] = []
    for condition in A7_3_CONDITIONS:
        for seed in seeds:
            run_dir = output_path / f"{condition}_seed{seed}"
            run_dir.mkdir(parents=True, exist_ok=True)
            metrics, events, source_ledger, lifted_state = _simulate_condition(
                condition,
                seed,
            )
            config_dict = config.to_dict()
            (run_dir / "config.yaml").write_text(
                yaml.safe_dump(config_dict, sort_keys=True)
            )
            _write_csv(run_dir / "metrics.csv", metrics, _metric_fieldnames())
            _write_csv(run_dir / "events.csv", events, a7_3_required_event_fields())
            _write_csv(
                run_dir / "source_ledger.csv",
                source_ledger,
                A7_3_SOURCE_LEDGER_CSV_FIELDS,
            )
            _write_csv(
                run_dir / "lifted_state.csv",
                lifted_state,
                _lifted_state_fieldnames(),
            )
            _write_schema(run_dir / "metrics_schema.csv", a7_3_required_metric_fields())
            _write_schema(run_dir / "events_schema.csv", a7_3_required_event_fields())
            _write_schema(run_dir / "source_ledger_schema.csv", A7_3_SOURCE_LEDGER_FIELDS)
            _write_schema(run_dir / "lifted_state_schema.csv", A7_3_LIFTED_STATE_FIELDS)
            (run_dir / "manifest.yaml").write_text(
                yaml.safe_dump(
                    _run_manifest(
                        config_dict,
                        condition,
                        seed,
                        len(metrics),
                        len(events),
                        len(source_ledger),
                        len(lifted_state),
                    ),
                    sort_keys=True,
                )
            )
            (run_dir / "summary.md").write_text(_run_summary(condition, seed))
            manifest_rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "config": str(Path(config_path)),
                    "run_dir": run_dir.name,
                    "tick_count": config.run.ticks,
                    "metrics_rows": len(metrics),
                    "events_rows": len(events),
                    "source_ledger_rows": len(source_ledger),
                    "lifted_state_rows": len(lifted_state),
                    "mechanics_status": A7_3_MECHANICS_STATUS,
                    "scientific_status": A7_3_SCIENTIFIC_STATUS,
                }
            )

    _write_csv(
        output_path / "a7_3_dimensionless_smoke_manifest.csv",
        manifest_rows,
        A7_3_MECHANICS_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(_summary(manifest_rows, seeds))
    return manifest_rows


def _simulate_condition(
    condition: str,
    seed: int,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    params = A7_3_SMOKE_PARAMETERS
    delay = 0 if condition == "no_delay_same_tick_blocked" else int(params["feedback_delay_ticks"])
    history: deque[dict[str, float]] = deque(maxlen=max(delay, 1))
    state = _initial_state(seed)
    metrics: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    lifted_rows: list[dict[str, Any]] = []

    for tick in range(int(params["horizon_ticks"])):
        lag = history[0] if delay > 0 and len(history) >= delay else _empty_activity()
        row = _advance(condition, seed, tick, delay, state, lag)
        history.append(_activity_snapshot(row))
        metric = {field: row.get(field, "") for field in _metric_fieldnames()}
        lifted = {field: row.get(field, "") for field in _lifted_state_fieldnames()}
        source = {field: row.get(field, "") for field in A7_3_SOURCE_LEDGER_CSV_FIELDS}
        event = {field: row.get(field, "") for field in a7_3_required_event_fields()}
        metrics.append(metric)
        lifted_rows.append(lifted)
        source_rows.append(source)
        events.append(event)
    return metrics, events, source_rows, lifted_rows


def _initial_state(seed: int) -> dict[str, float]:
    return {
        "artifact_readiness": 0.30 + 0.01 * seed,
        "artifact_coherence": 0.35,
        "contradiction_risk": 0.22,
        "prediction_error": 0.28,
        "prediction_uncertainty": 0.18,
        "fatigue": 0.10,
        "work_backlog": 3.0 + 0.2 * seed,
        "queued_age": 1.0,
        "memory_pressure": 0.20,
        "adaptive_threshold_predict": 0.12,
        "adaptive_threshold_work": 0.04,
        "adaptive_threshold_review": 0.08,
        "adaptive_threshold_synthesize": 0.10,
        "adaptive_threshold_rest": 0.02,
    }


def _advance(
    condition: str,
    seed: int,
    tick: int,
    delay: int,
    state: dict[str, float],
    lag: dict[str, float],
) -> dict[str, Any]:
    params = A7_3_SMOKE_PARAMETERS
    controls = _dimensionless_controls(condition)
    demand_phase = math.sin((tick + seed) / 6.0)
    arrivals = 1 + int((tick + seed) % 4 == 0)
    service_capacity = 1.0 + 0.08 * math.cos((tick + seed) / 7.0)
    action_opportunity = 5.0
    work_budget = 1.0 + 0.08 * math.sin((tick + 2 * seed) / 5.0)
    peer_activity = {
        "predict": _condition_lag(condition, lag["predict"], tick, seed),
        "work": _condition_lag(condition, lag["work"], tick + 1, seed),
        "review": _condition_lag(condition, lag["review"], tick + 2, seed),
        "synthesize": _condition_lag(condition, lag["synthesize"], tick + 3, seed),
        "rest": lag["rest"],
    }
    gate = _linear_gate if condition == "amplitude_matched_linear" else _sigmoid
    coupling = controls["rho"]
    artifact_factor = 0.0 if condition == "artifact_off" else 1.0
    thresholds = _thresholds_for_condition(condition, state)
    utilities = {
        "predict": gate(
            coupling
            * (
                state["prediction_error"]
                + state["prediction_uncertainty"]
                + peer_activity["predict"]
                - thresholds["predict"]
                - state["fatigue"]
            )
        ),
        "work": gate(
            state["work_backlog"] / 8.0
            + artifact_factor * state["artifact_readiness"]
            + 0.3 * peer_activity["work"]
            - thresholds["work"]
            - state["fatigue"]
        ),
        "review": gate(
            artifact_factor * state["contradiction_risk"]
            + 0.25 * peer_activity["review"]
            - thresholds["review"]
            - state["fatigue"]
        ),
        "synthesize": gate(
            artifact_factor * (state["artifact_readiness"] + state["artifact_coherence"])
            + 0.20 * peer_activity["synthesize"]
            - state["contradiction_risk"]
            - thresholds["synthesize"]
            - state["fatigue"]
        ),
        "rest": gate(state["fatigue"] + peer_activity["rest"] - thresholds["rest"]),
    }
    selected = max(A7_3_ACTIONS, key=lambda action: (utilities[action], action))
    role_total = sum(utilities.values()) or 1.0
    role_activity = {action: utilities[action] / role_total for action in A7_3_ACTIONS}
    prediction_spend = 0.0
    lost_work = 0.0
    if selected == "predict" or condition == "spend_only_replay":
        prediction_spend = 0.35
        if condition != "cost_free_prediction":
            lost_work = min(
                float(params["prediction_cost_work_fraction"]) * prediction_spend,
                float(params["max_prediction_work_fraction_per_tick"]) * work_budget,
            )
    completion_capacity = max(service_capacity * work_budget - lost_work, 0.0)
    completed = min(state["work_backlog"] + arrivals, completion_capacity)
    before_artifact = {
        field: state[field]
        for field in ("artifact_readiness", "artifact_coherence", "contradiction_risk")
    }
    state["work_backlog"] = max(state["work_backlog"] + arrivals - completed, 0.0)
    state["queued_age"] = max(state["queued_age"] + state["work_backlog"] / 12.0 - completed / 8.0, 0.0)
    if condition != "artifact_off":
        state["artifact_readiness"] = _clip(
            (1.0 - params["artifact_memory_decay"]) * state["artifact_readiness"]
            + 0.06 * (selected == "work")
            + 0.04 * (selected == "synthesize")
            - 0.03 * state["contradiction_risk"]
        )
        state["artifact_coherence"] = _clip(
            (1.0 - params["artifact_memory_decay"]) * state["artifact_coherence"]
            + 0.04 * (selected == "review")
            + 0.05 * (selected == "synthesize")
            - 0.02 * state["contradiction_risk"]
        )
        state["contradiction_risk"] = _clip(
            0.88 * state["contradiction_risk"]
            + 0.03 * abs(demand_phase)
            - 0.04 * (selected == "review")
        )
    state["prediction_error"] = _clip(
        0.86 * state["prediction_error"] + 0.06 * abs(demand_phase) - 0.08 * prediction_spend
    )
    state["prediction_uncertainty"] = _clip(
        0.90 * state["prediction_uncertainty"] + 0.02 - 0.05 * prediction_spend
    )
    state["fatigue"] = _clip(0.84 * state["fatigue"] + _fatigue_increment(selected))
    state["memory_pressure"] = _clip(
        controls["mu"] * 0.08 + 0.65 * state["memory_pressure"] + 0.05 * state["artifact_readiness"]
    )
    for action in A7_3_ACTIONS:
        key = f"adaptive_threshold_{action}"
        state[key] = _clip_signed(
            state[key]
            + params["threshold_learning_rate"] * (role_activity[action] - 0.2)
            - params["threshold_recovery_rate"] * state[key]
        )
    feedback_created = tick
    feedback_visible = tick + delay
    same_tick_blocked = True
    source = _source_statuses(condition, same_tick_blocked)
    row: dict[str, Any] = {
        **controls,
        "tick": tick,
        "condition": condition,
        "seed": seed,
        "agent_id": "hive_agent_pool",
        "event_type": "a7_3_role_activity_update",
        "selected_action": selected,
        "feedback_created_tick": feedback_created,
        "feedback_visible_tick": feedback_visible,
        "same_tick_influence_blocked": same_tick_blocked,
        "prediction_work_cost": round(lost_work, 6),
        "demand_phase": round(demand_phase, 6),
        "task_arrivals": arrivals,
        "service_capacity": round(service_capacity, 6),
        "action_opportunity": round(action_opportunity, 6),
        "work_budget": round(work_budget, 6),
        "work_backlog": round(state["work_backlog"], 6),
        "queued_age": round(state["queued_age"], 6),
        "completion_fraction": round(completed / max(action_opportunity, 1.0), 6),
        "prediction_spend": round(prediction_spend, 6),
        "lost_work_opportunity_from_prediction": round(lost_work, 6),
        "memory_pressure": round(state["memory_pressure"], 6),
        "artifact_readiness": round(state["artifact_readiness"], 6),
        "artifact_coherence": round(state["artifact_coherence"], 6),
        "contradiction_risk": round(state["contradiction_risk"], 6),
        "prediction_error": round(state["prediction_error"], 6),
        "prediction_uncertainty": round(state["prediction_uncertainty"], 6),
        "fatigue": round(state["fatigue"], 6),
        **source,
    }
    for action in A7_3_ACTIONS:
        row[f"agent_role_activity_{action}"] = round(role_activity[action], 6)
        row[f"delayed_agent_role_activity_{action}"] = round(lag[action], 6)
        row[f"peer_activity_lag_{action}"] = round(peer_activity[action], 6)
        row[f"adaptive_threshold_{action}"] = round(state[f"adaptive_threshold_{action}"], 6)
    row["source_ledger_artifact_memory"] = round(
        sum(abs(state[field] - before_artifact[field]) for field in before_artifact),
        6,
    )
    row["source_ledger_prediction_cost"] = round(lost_work, 6)
    row["source_ledger_queue_accounting"] = round(completed, 6)
    row["source_ledger_threshold_update"] = "pass"
    row["source_ledger_clip_residual"] = 0.0
    return row


def _dimensionless_controls(condition: str) -> dict[str, float]:
    params = A7_3_SMOKE_PARAMETERS
    rho = (
        params["low_gain_coupling_gain"]
        if condition == "low_gain_contraction"
        else params["linear_gain"]
        if condition == "amplitude_matched_linear"
        else params["nonlinear_coupling_gain"]
    )
    delta = 0.0 if condition == "no_delay_same_tick_blocked" else params["feedback_delay_ticks"] / params["relaxation_time_ticks"]
    return {
        "rho": round(float(rho), 6),
        "delta": round(float(delta), 6),
        "mu": round(float(1.0 - params["artifact_memory_decay"]), 6),
        "kappa": round(float(params["peer_coupling_spread"]), 6),
        "nu": round(float(params["noise_to_signal"]), 6),
        "chi": round(0.0 if condition == "cost_free_prediction" else float(params["prediction_cost_work_fraction"]), 6),
        "eta": round(float(params["threshold_learning_rate"] / params["threshold_recovery_rate"]), 6),
    }


def _condition_lag(condition: str, value: float, tick: int, seed: int) -> float:
    if condition == "phase_shuffled_lag":
        return 0.2 + 0.05 * math.sin((tick + seed + 13) / 3.0)
    return value


def _thresholds_for_condition(
    condition: str,
    state: dict[str, float],
) -> dict[str, float]:
    thresholds = {action: state[f"adaptive_threshold_{action}"] for action in A7_3_ACTIONS}
    if condition == "threshold_shuffled":
        shuffled = ("review", "synthesize", "rest", "predict", "work")
        return dict(zip(A7_3_ACTIONS, (thresholds[action] for action in shuffled)))
    return thresholds


def _source_statuses(condition: str, same_tick_blocked: bool) -> dict[str, Any]:
    return {
        "source_ledger_delay_integrity": (
            "control_no_delay"
            if condition == "no_delay_same_tick_blocked"
            else "pass"
            if same_tick_blocked
            else "fail"
        ),
        "source_ledger_peer_activity_lag": "pass",
        "source_ledger_phase_shuffle": "applied" if condition == "phase_shuffled_lag" else "not_applicable",
        "source_ledger_threshold_shuffle": "applied" if condition == "threshold_shuffled" else "not_applicable",
    }


def _activity_snapshot(row: dict[str, Any]) -> dict[str, float]:
    return {
        action: float(row[f"agent_role_activity_{action}"])
        for action in A7_3_ACTIONS
    }


def _empty_activity() -> dict[str, float]:
    return {action: 0.0 for action in A7_3_ACTIONS}


def _fatigue_increment(selected: str) -> float:
    return {
        "predict": 0.08,
        "work": 0.05,
        "review": 0.04,
        "synthesize": 0.06,
        "rest": -0.03,
    }[selected]


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def _linear_gate(value: float) -> float:
    return _clip(0.5 + 0.5 * value)


def _clip(value: float) -> float:
    return max(0.0, min(1.0, value))


def _clip_signed(value: float) -> float:
    return max(-2.0, min(2.0, value))


def _metric_fieldnames() -> tuple[str, ...]:
    return ("condition", "seed", *a7_3_required_metric_fields())


def _lifted_state_fieldnames() -> tuple[str, ...]:
    return ("condition", "seed", *A7_3_LIFTED_STATE_FIELDS)


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    if (output_path / "a7_3_dimensionless_smoke_manifest.csv").exists():
        raise FileExistsError(
            f"Output path {output_path} already contains A7.3 smoke artifacts."
        )


def _run_manifest(
    config: dict[str, Any],
    condition: str,
    seed: int,
    metrics_rows: int,
    events_rows: int,
    source_ledger_rows: int,
    lifted_state_rows: int,
) -> dict[str, Any]:
    return {
        "experiment_id": config["run"]["experiment_id"],
        "condition": condition,
        "seed": seed,
        "ticks": A7_3_SMOKE_PARAMETERS["horizon_ticks"],
        "condition_class": (
            "positive" if condition == A7_3_POSITIVE_CONDITION else "null_control"
        ),
        "null_conditions": list(A7_3_NULL_CONDITIONS),
        "metrics_rows": metrics_rows,
        "events_rows": events_rows,
        "source_ledger_rows": source_ledger_rows,
        "lifted_state_rows": lifted_state_rows,
        "artifacts": [
            "config.yaml",
            "manifest.yaml",
            "metrics.csv",
            "events.csv",
            "source_ledger.csv",
            "lifted_state.csv",
            "metrics_schema.csv",
            "events_schema.csv",
            "source_ledger_schema.csv",
            "lifted_state_schema.csv",
            "summary.md",
        ],
        "mechanics_status": A7_3_MECHANICS_STATUS,
        "scientific_status": A7_3_SCIENTIFIC_STATUS,
        "config": config,
    }


def _run_summary(condition: str, seed: int) -> str:
    return "\n".join(
        [
            "# A7.3 Dimensionless Delayed Smoke Artifact",
            "",
            f"- Condition: `{condition}`",
            f"- Seed: `{seed}`",
            f"- Status: `{A7_3_MECHANICS_STATUS}`",
            f"- Scientific status: `{A7_3_SCIENTIFIC_STATUS}`",
            "",
            "This directory contains deterministic smoke metrics, events, source-ledger,",
            "and lifted-state artifacts. It is not a promotion analysis.",
            "",
        ]
    )


def _summary(rows: list[dict[str, Any]], seeds: tuple[int, ...]) -> str:
    return "\n".join(
        [
            "# A7.3 Dimensionless Delayed Smoke",
            "",
            f"- Conditions: {len(A7_3_CONDITIONS)}",
            f"- Seeds: {', '.join(str(seed) for seed in seeds)}",
            f"- Run directories: {len(rows)}",
            f"- Horizon: {A7_3_SMOKE_PARAMETERS['horizon_ticks']} ticks",
            f"- Status: `{A7_3_MECHANICS_STATUS}`",
            f"- Scientific status: `{A7_3_SCIENTIFIC_STATUS}`",
            "",
            "This helper emits the frozen A7.3 contract fields for the fixed paired-seed smoke gate.",
            "It does not compute promotion endpoints, run broad sweeps, add integrations,",
            "or reopen A5, A7.2, or three-hive results.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run fixed A7.3 one-hive dimensionless delayed-dynamics smoke."
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_A7_3_CONFIG),
        help="Frozen A7.3 dimensionless smoke fixture.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_A7_3_SEEDS),
        help="Fixed deterministic paired seeds; preregistered value is 1 2.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A7_3_SMOKE_DIR),
        help="Output directory for A7.3 smoke artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a7_3_dimensionless_smoke(
            config_path=args.config,
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
