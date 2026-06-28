"""Run the fixed three-hive ring deterministic mechanics smoke."""

from __future__ import annotations

import argparse
import csv
import math
from collections import deque
from pathlib import Path
from typing import Any

import yaml

from ohdyn.config import load_config
from ohdyn.compare_three_hive_ring import (
    DEFAULT_THREE_HIVE_RING_CONTRACT_CONFIG,
    DEFAULT_THREE_HIVE_RING_SEEDS,
    _write_schema,
)
from ohdyn.three_hive_ring_contract import (
    THREE_HIVE_RING_CONDITIONS,
    THREE_HIVE_RING_EDGE_HIVES,
    THREE_HIVE_RING_EDGES,
    THREE_HIVE_RING_MECHANICS_MANIFEST_FIELDS,
    THREE_HIVE_RING_SMOKE_PARAMETERS,
    THREE_HIVE_RING_SOURCE_LEDGER_CSV_FIELDS,
    THREE_HIVE_RING_SOURCE_LEDGER_FIELDS,
    three_hive_ring_required_event_fields,
    three_hive_ring_required_metric_fields,
)


DEFAULT_THREE_HIVE_RING_MECHANICS_DIR = Path(
    "runs/three_hive_ring_mechanics_smoke_seed1_2"
)
THREE_HIVE_RING_MECHANICS_STATUS = "deterministic_mechanics_smoke_artifacts_only"
THREE_HIVE_RING_MECHANICS_SCIENTIFIC_STATUS = (
    "metrics_events_present_requires_future_read_only_residual_null_analyzer"
)
_HIVE_INDEX = {
    "hive_a_explore_research": 0,
    "hive_b_formalize_implement": 1,
    "hive_c_synthesize_review": 2,
}


def run_three_hive_ring_mechanics_smoke(
    *,
    config_path: str | Path = DEFAULT_THREE_HIVE_RING_CONTRACT_CONFIG,
    seeds: tuple[int, ...] = DEFAULT_THREE_HIVE_RING_SEEDS,
    out_dir: str | Path = DEFAULT_THREE_HIVE_RING_MECHANICS_DIR,
) -> list[dict[str, Any]]:
    """Run only the frozen paired-seed deterministic three-hive smoke grid."""

    if seeds != DEFAULT_THREE_HIVE_RING_SEEDS:
        raise ValueError("Three-hive ring mechanics smoke is fixed to paired seeds 1 and 2.")
    config = load_config(config_path)
    if config.three_hive_ring is None:
        raise ValueError(f"{config_path} must enable three_hive_ring.")
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, Any]] = []
    for condition in THREE_HIVE_RING_CONDITIONS:
        for seed in seeds:
            run_dir = output_path / f"{condition}_seed{seed}"
            run_dir.mkdir(parents=True, exist_ok=True)
            metrics, events, source_ledger = _simulate_condition(condition, seed)
            config_dict = config.to_dict()
            (run_dir / "config.yaml").write_text(
                yaml.safe_dump(config_dict, sort_keys=True)
            )
            _write_csv(run_dir / "metrics.csv", metrics, _metric_fieldnames())
            _write_csv(
                run_dir / "events.csv",
                events,
                three_hive_ring_required_event_fields(),
            )
            _write_csv(
                run_dir / "source_ledger.csv",
                source_ledger,
                THREE_HIVE_RING_SOURCE_LEDGER_CSV_FIELDS,
            )
            _write_schema(run_dir / "metrics_schema.csv", three_hive_ring_required_metric_fields())
            _write_schema(run_dir / "events_schema.csv", three_hive_ring_required_event_fields())
            _write_schema(run_dir / "source_ledger_schema.csv", THREE_HIVE_RING_SOURCE_LEDGER_FIELDS)
            (run_dir / "manifest.yaml").write_text(
                yaml.safe_dump(
                    _run_manifest(
                        config_dict,
                        condition,
                        seed,
                        len(metrics),
                        len(events),
                        len(source_ledger),
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
                    "hive_count": len(config.three_hive_ring.hives),
                    "edge_count": len(config.three_hive_ring.edges),
                    "metrics_rows": len(metrics),
                    "events_rows": len(events),
                    "source_ledger_rows": len(source_ledger),
                    "mechanics_status": THREE_HIVE_RING_MECHANICS_STATUS,
                    "scientific_status": THREE_HIVE_RING_MECHANICS_SCIENTIFIC_STATUS,
                }
            )

    _write_csv(
        output_path / "three_hive_ring_mechanics_manifest.csv",
        manifest_rows,
        THREE_HIVE_RING_MECHANICS_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(_summary(manifest_rows, seeds))
    return manifest_rows


def _simulate_condition(
    condition: str,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    params = THREE_HIVE_RING_SMOKE_PARAMETERS
    hives = tuple(hive for pair in THREE_HIVE_RING_EDGE_HIVES for hive in pair[:1])
    state = {hive: _initial_hive_state(hive, seed) for hive in hives}
    inbound: dict[str, deque[dict[str, float | int]]] = {hive: deque() for hive in hives}
    metrics: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []

    for tick in range(int(params["horizon_ticks"])):
        visible = _visible_inbound(inbound, tick)
        action_rows: dict[str, dict[str, Any]] = {}
        for hive in hives:
            action_rows[hive] = _advance_hive(condition, seed, tick, hive, state[hive], visible[hive])

        edge_rows: list[dict[str, Any]] = []
        for edge_index, edge_id in enumerate(THREE_HIVE_RING_EDGES):
            source_hive, target_hive = _edge_hives_for_condition(condition, edge_index, hives)
            edge_row = _transfer_event(
                condition,
                seed,
                tick,
                edge_id,
                source_hive,
                target_hive,
                state[source_hive],
                state[target_hive],
                action_rows[source_hive],
            )
            edge_rows.append(edge_row)
            if float(edge_row["accepted_transfer_volume"]) > 0.0:
                delay = int(edge_row["transfer_delay_ticks"])
                inbound[target_hive].append(
                    {
                        "visible_tick": tick + delay,
                        "readiness": float(edge_row["artifact_payload_readiness"]),
                        "coherence": float(edge_row["artifact_payload_coherence"]),
                        "contradiction": float(edge_row["artifact_payload_contradiction"]),
                        "risk": float(edge_row["artifact_payload_risk"]),
                    }
                )
        edge_by_source = {row["source_hive"]: row for row in edge_rows}
        edge_by_target = {row["target_hive"]: row for row in edge_rows}
        for hive in hives:
            metrics.append(_metric_row(condition, seed, tick, hive, state[hive], action_rows[hive], edge_by_source[hive], edge_by_target[hive]))
            source_rows.append(_source_ledger_row(condition, seed, tick, hive, action_rows[hive], edge_by_source[hive]))
        events.extend(edge_rows)
    return metrics, events, source_rows


def _initial_hive_state(hive: str, seed: int) -> dict[str, float | str]:
    index = _HIVE_INDEX[hive]
    return {
        "local_backlog": 2.0 + index + 0.1 * seed,
        "local_queued_age": 1.0 + 0.2 * index,
        "fatigue": 0.10 + 0.02 * index,
        "adaptive_prediction_threshold": 0.15,
        "adaptive_work_threshold": 0.05,
        "adaptive_review_threshold": 0.10,
        "adaptive_synthesis_threshold": 0.12,
        "artifact_readiness": 0.28 + 0.04 * index,
        "artifact_coherence": 0.34 + 0.03 * index,
        "artifact_contradiction": 0.24 - 0.02 * index,
        "artifact_risk": 0.22 - 0.01 * index,
        "cross_hive_forecast_error_lag": 0.24 + 0.02 * index,
        "cross_hive_forecast_uncertainty_lag": 0.18,
        "accepted_transfer_count": 0.0,
        "rejected_transfer_count": 0.0,
        "selected_action": "idle",
    }


def _visible_inbound(
    inbound: dict[str, deque[dict[str, float | int]]],
    tick: int,
) -> dict[str, dict[str, float]]:
    visible = {
        hive: {"readiness": 0.0, "coherence": 0.0, "contradiction": 0.0, "risk": 0.0}
        for hive in inbound
    }
    for hive, queue in inbound.items():
        while queue and int(queue[0]["visible_tick"]) <= tick:
            update = queue.popleft()
            for field in visible[hive]:
                visible[hive][field] += float(update[field])
    return visible


def _advance_hive(
    condition: str,
    seed: int,
    tick: int,
    hive: str,
    state: dict[str, float | str],
    inbound: dict[str, float],
) -> dict[str, Any]:
    params = THREE_HIVE_RING_SMOKE_PARAMETERS
    index = _HIVE_INDEX[hive]
    demand_phase = math.sin((tick + 1 + index) / 5.0)
    arrivals = 1 + ((tick + index + seed) % 3 == 0)
    service = 1.0 + 0.1 * (index == 1) + 0.05 * math.cos((tick + seed) / 7.0)
    action_opportunity = 5.0
    work_budget = 1.0 + 0.1 * math.sin((tick + index + seed) / 6.0)
    inbound_readiness = _condition_inbound(condition, inbound["readiness"], tick, index)
    inbound_coherence = _condition_inbound(condition, inbound["coherence"], tick, index)
    inbound_contradiction = _condition_inbound(condition, inbound["contradiction"], tick, index)
    inbound_risk = _condition_inbound(condition, inbound["risk"], tick, index)
    forecast_error = float(state["cross_hive_forecast_error_lag"])
    uncertainty = float(state["cross_hive_forecast_uncertainty_lag"])
    fatigue = float(state["fatigue"])
    gate = _linear_gate if condition == "amplitude_matched_linear_delayed_ring" else _sigmoid
    thresholds = _thresholds_for_condition(condition, state, index)
    utilities = {
        "predict_cross_hive": params["utility_slope_cross_predict"]
        * gate(forecast_error + uncertainty + inbound_contradiction + inbound_risk - thresholds["predict"] - fatigue),
        "work_local": params["utility_slope_work"]
        * gate(float(state["local_backlog"]) / 8.0 + float(state["artifact_readiness"]) - thresholds["work"] - fatigue),
        "review_inbound_artifact": params["utility_slope_review"]
        * gate(inbound_contradiction + inbound_risk - thresholds["review"] - fatigue),
        "synthesize_outbound_artifact": params["utility_slope_synthesize"]
        * gate(float(state["artifact_readiness"]) + float(state["artifact_coherence"]) + inbound_readiness - float(state["artifact_contradiction"]) - thresholds["synthesize"] - fatigue),
        "idle": 0.05,
    }
    if condition == "no_coupling":
        utilities["predict_cross_hive"] = 0.0
        utilities["review_inbound_artifact"] *= 0.25
        utilities["synthesize_outbound_artifact"] *= 0.5
    if condition == "high_budget_oracle_smoothing":
        utilities["predict_cross_hive"] *= 1.6
    selected = max(utilities, key=lambda key: (utilities[key], key))
    prediction_spend = 0.0
    lost_work = 0.0
    if selected == "predict_cross_hive" or condition in {"spend_only_cross_hive_prediction_replay", "high_budget_oracle_smoothing"}:
        prediction_spend = min(0.55 if condition == "high_budget_oracle_smoothing" else 0.35, action_opportunity)
        lost_work = min(
            float(params["prediction_cost_work_fraction"]) * prediction_spend,
            float(params["max_prediction_work_fraction_per_tick"]) * work_budget,
        )
    completion_capacity = max(service * work_budget - lost_work, 0.0)
    completed = min(float(state["local_backlog"]) + arrivals, completion_capacity)
    state["local_backlog"] = max(float(state["local_backlog"]) + arrivals - completed, 0.0)
    state["local_queued_age"] = max(float(state["local_queued_age"]) + float(state["local_backlog"]) / 10.0 - completed / 8.0, 0.0)
    deltas = _artifact_deltas(condition, selected, inbound_readiness, inbound_coherence, inbound_contradiction, inbound_risk)
    before = {key: float(state[key]) for key in ("artifact_readiness", "artifact_coherence", "artifact_contradiction", "artifact_risk")}
    for field, delta in deltas.items():
        state[field] = _clip((1.0 - float(params["artifact_decay"])) * float(state[field]) + delta)
    state["artifact_revision_pressure"] = _clip(float(state["artifact_contradiction"]) + float(state["artifact_risk"]) - float(state["artifact_readiness"]))
    state["cross_hive_forecast_error_lag"] = _clip(0.85 * forecast_error + 0.08 * abs(demand_phase) - 0.10 * prediction_spend)
    state["cross_hive_forecast_uncertainty_lag"] = _clip(0.90 * uncertainty + 0.03 - 0.06 * prediction_spend)
    state["fatigue"] = _clip((1.0 - float(params["fatigue_decay"])) * fatigue + _fatigue_increment(selected))
    state["selected_action"] = selected
    state["accepted_transfer_count"] = float(state["accepted_transfer_count"])
    state["rejected_transfer_count"] = float(state["rejected_transfer_count"])
    return {
        "demand_phase": round(demand_phase, 6),
        "local_task_arrivals": int(arrivals),
        "local_service_capacity": round(service, 6),
        "local_action_opportunity": round(action_opportunity, 6),
        "local_work_budget": round(work_budget, 6),
        "local_prediction_spend": round(prediction_spend, 6),
        "lost_work_opportunity_from_prediction": round(lost_work, 6),
        "inbound_artifact_readiness_lag": round(inbound_readiness, 6),
        "inbound_artifact_coherence_lag": round(inbound_coherence, 6),
        "inbound_artifact_contradiction_lag": round(inbound_contradiction, 6),
        "inbound_artifact_risk_lag": round(inbound_risk, 6),
        "completion_fraction": round(completed / max(action_opportunity, 1.0), 6),
        "source_ledger_queue_accounting": round(completed, 6),
        "source_ledger_artifact_readiness_delta": round(float(state["artifact_readiness"]) - before["artifact_readiness"], 6),
        "source_ledger_artifact_coherence_delta": round(float(state["artifact_coherence"]) - before["artifact_coherence"], 6),
        "source_ledger_artifact_contradiction_delta": round(float(state["artifact_contradiction"]) - before["artifact_contradiction"], 6),
        "source_ledger_artifact_risk_delta": round(float(state["artifact_risk"]) - before["artifact_risk"], 6),
    }


def _condition_inbound(condition: str, value: float, tick: int, index: int) -> float:
    if condition in {"no_coupling", "artifact_off_source_ledger_null"}:
        return 0.0
    if condition == "phase_shuffled_transfer":
        return max(value, 0.025 * (1.0 + math.sin((tick + 11 + index) / 4.0)))
    if condition == "source_preserving_artifact_label_shuffle":
        return value * (0.7 + 0.1 * index)
    return value


def _thresholds_for_condition(
    condition: str,
    state: dict[str, float | str],
    index: int,
) -> dict[str, float]:
    values = {
        "predict": float(state["adaptive_prediction_threshold"]),
        "work": float(state["adaptive_work_threshold"]),
        "review": float(state["adaptive_review_threshold"]),
        "synthesize": float(state["adaptive_synthesis_threshold"]),
    }
    if condition == "threshold_shuffled_ring":
        order = ("review", "synthesize", "work", "predict")
        return dict(zip(values, (values[key] + 0.03 * index for key in order)))
    return values


def _artifact_deltas(
    condition: str,
    selected: str,
    readiness: float,
    coherence: float,
    contradiction: float,
    risk: float,
) -> dict[str, float]:
    if condition == "artifact_off_source_ledger_null":
        return {field: 0.0 for field in ("artifact_readiness", "artifact_coherence", "artifact_contradiction", "artifact_risk")}
    local_work = 0.030 if selected == "work_local" else 0.0
    review = 0.020 if selected == "review_inbound_artifact" else 0.0
    synth = 0.030 if selected == "synthesize_outbound_artifact" else 0.0
    return {
        "artifact_readiness": local_work + 0.40 * readiness + synth - 0.12 * contradiction,
        "artifact_coherence": 0.35 * coherence + synth + 0.5 * review - 0.08 * risk,
        "artifact_contradiction": 0.45 * contradiction + 0.25 * risk + 0.5 * review - 0.5 * synth,
        "artifact_risk": 0.40 * risk + 0.10 * contradiction - 0.45 * review,
    }


def _edge_hives_for_condition(
    condition: str,
    edge_index: int,
    hives: tuple[str, ...],
) -> tuple[str, str]:
    source, target = THREE_HIVE_RING_EDGE_HIVES[edge_index]
    if condition == "target_shuffled_transfer":
        return source, hives[(edge_index + 2) % len(hives)]
    return source, target


def _transfer_event(
    condition: str,
    seed: int,
    tick: int,
    edge_id: str,
    source_hive: str,
    target_hive: str,
    source_state: dict[str, float | str],
    target_state: dict[str, float | str],
    action_row: dict[str, Any],
) -> dict[str, Any]:
    params = THREE_HIVE_RING_SMOKE_PARAMETERS
    opportunity = 0.0 if condition == "no_coupling" else 1.0 + 0.2 * math.sin((tick + seed + _HIVE_INDEX[source_hive]) / 4.0)
    proposed = opportunity * max(float(source_state["artifact_readiness"]), 0.0)
    if action_row["local_prediction_spend"] > 0.0:
        proposed *= 1.15
    if condition == "transfer_opportunity_matched_replay":
        proposed = opportunity * 0.20
    acceptance = _sigmoid(float(params["membrane_permeability"]) + float(source_state["artifact_coherence"]) - float(source_state["artifact_risk"]) - float(target_state["fatigue"]))
    if condition == "spend_only_cross_hive_prediction_replay":
        acceptance *= 0.25
    accepted = proposed * acceptance
    rejected = max(proposed - accepted, 0.0)
    source_state["accepted_transfer_count"] = float(source_state["accepted_transfer_count"]) + (1 if accepted > 0 else 0)
    source_state["rejected_transfer_count"] = float(source_state["rejected_transfer_count"]) + (1 if rejected > 0 else 0)
    delay = 0 if condition == "same_tick_logistic_ring" else int(params["transfer_delay_ticks"])
    if condition == "heterogeneous_delay_logistic_ring":
        delay += _HIVE_INDEX[source_hive]
    if condition in {"transfer_opportunity_matched_replay", "spend_only_cross_hive_prediction_replay"}:
        payload = {"readiness": 0.0, "coherence": 0.0, "contradiction": 0.0, "risk": 0.0}
    else:
        payload = {
            "readiness": accepted * float(source_state["artifact_readiness"]) * 0.12,
            "coherence": accepted * float(source_state["artifact_coherence"]) * 0.10,
            "contradiction": accepted * float(source_state["artifact_contradiction"]) * 0.08,
            "risk": accepted * float(source_state["artifact_risk"]) * 0.06,
        }
    transfer_cost = min(
        float(params["transfer_cost_work_fraction"]) * proposed,
        float(params["max_transfer_work_fraction_per_tick"]) * float(action_row["local_work_budget"]),
    )
    prediction_error = float(source_state["cross_hive_forecast_error_lag"])
    return {
        "tick": tick,
        "condition": condition,
        "seed": seed,
        "edge_id": edge_id,
        "source_hive": source_hive,
        "target_hive": target_hive,
        "proposed_transfer_volume": round(proposed, 6),
        "accepted_transfer_volume": round(accepted, 6),
        "transfer_opportunity": round(opportunity, 6),
        "transfer_delay_ticks": delay,
        "membrane_acceptance": round(acceptance, 6),
        "cross_hive_prediction_spend": action_row["local_prediction_spend"],
        "cross_hive_prediction_error": round(prediction_error, 6),
        "artifact_payload_readiness": round(payload["readiness"], 6),
        "artifact_payload_coherence": round(payload["coherence"], 6),
        "artifact_payload_contradiction": round(payload["contradiction"], 6),
        "artifact_payload_risk": round(payload["risk"], 6),
        "source_ledger_transfer": round(accepted, 6),
        "source_ledger_prediction": action_row["local_prediction_spend"],
        "source_ledger_queue_accounting": action_row["source_ledger_queue_accounting"],
        "source_ledger_artifact_delta": round(sum(abs(value) for value in payload.values()), 6),
        "source_ledger_artifact_readiness_delta": round(payload["readiness"], 6),
        "source_ledger_artifact_coherence_delta": round(payload["coherence"], 6),
        "source_ledger_artifact_contradiction_delta": round(payload["contradiction"], 6),
        "source_ledger_artifact_risk_delta": round(payload["risk"], 6),
        "source_ledger_clip_residual": 0.0,
    }


def _metric_row(
    condition: str,
    seed: int,
    tick: int,
    hive: str,
    state: dict[str, float | str],
    action_row: dict[str, Any],
    outbound: dict[str, Any],
    inbound_edge: dict[str, Any],
) -> dict[str, Any]:
    row = {
        "condition": condition,
        "seed": seed,
        "hive_id": hive,
        "tick": tick,
        **action_row,
        "local_backlog": round(float(state["local_backlog"]), 6),
        "local_queued_age": round(float(state["local_queued_age"]), 6),
        "fatigue": round(float(state["fatigue"]), 6),
        "adaptive_prediction_threshold": round(float(state["adaptive_prediction_threshold"]), 6),
        "adaptive_work_threshold": round(float(state["adaptive_work_threshold"]), 6),
        "adaptive_review_threshold": round(float(state["adaptive_review_threshold"]), 6),
        "adaptive_synthesis_threshold": round(float(state["adaptive_synthesis_threshold"]), 6),
        "artifact_readiness": round(float(state["artifact_readiness"]), 6),
        "artifact_coherence": round(float(state["artifact_coherence"]), 6),
        "artifact_contradiction": round(float(state["artifact_contradiction"]), 6),
        "artifact_risk": round(float(state["artifact_risk"]), 6),
        "artifact_revision_pressure": round(float(state["artifact_revision_pressure"]), 6),
        "cross_hive_forecast_error_lag": round(float(state["cross_hive_forecast_error_lag"]), 6),
        "cross_hive_forecast_uncertainty_lag": round(float(state["cross_hive_forecast_uncertainty_lag"]), 6),
        "transfer_opportunity": outbound["transfer_opportunity"],
        "accepted_transfer_count": int(float(state["accepted_transfer_count"])),
        "rejected_transfer_count": int(float(state["rejected_transfer_count"])),
        "selected_action": state["selected_action"],
        "proposed_transfer_volume": outbound["proposed_transfer_volume"],
        "accepted_transfer_volume": outbound["accepted_transfer_volume"],
        "transfer_work_cost": round(float(outbound["proposed_transfer_volume"]) * THREE_HIVE_RING_SMOKE_PARAMETERS["transfer_cost_work_fraction"], 6),
        "role_bias": hive,
        "source_hive": outbound["source_hive"],
        "target_hive": outbound["target_hive"],
    }
    return {field: row.get(field, "") for field in _metric_fieldnames()}


def _source_ledger_row(
    condition: str,
    seed: int,
    tick: int,
    hive: str,
    action_row: dict[str, Any],
    outbound: dict[str, Any],
) -> dict[str, Any]:
    row = {
        "tick": tick,
        "condition": condition,
        "seed": seed,
        "hive_id": hive,
        "source_ledger_transfer": outbound["source_ledger_transfer"],
        "source_ledger_prediction": action_row["local_prediction_spend"],
        "source_ledger_queue_accounting": action_row["source_ledger_queue_accounting"],
        "source_ledger_artifact_delta": round(
            sum(
                abs(float(action_row[field]))
                for field in (
                    "source_ledger_artifact_readiness_delta",
                    "source_ledger_artifact_coherence_delta",
                    "source_ledger_artifact_contradiction_delta",
                    "source_ledger_artifact_risk_delta",
                )
            ),
            6,
        ),
        "source_ledger_artifact_readiness_delta": action_row["source_ledger_artifact_readiness_delta"],
        "source_ledger_artifact_coherence_delta": action_row["source_ledger_artifact_coherence_delta"],
        "source_ledger_artifact_contradiction_delta": action_row["source_ledger_artifact_contradiction_delta"],
        "source_ledger_artifact_risk_delta": action_row["source_ledger_artifact_risk_delta"],
        "source_ledger_clip_residual": 0.0,
    }
    return {field: row.get(field, "") for field in THREE_HIVE_RING_SOURCE_LEDGER_CSV_FIELDS}


def _run_manifest(
    config: dict[str, Any],
    condition: str,
    seed: int,
    metrics_rows: int,
    events_rows: int,
    source_ledger_rows: int,
) -> dict[str, Any]:
    params = THREE_HIVE_RING_SMOKE_PARAMETERS
    return {
        "experiment_id": config["run"]["experiment_id"],
        "condition": condition,
        "seed": seed,
        "ticks": params["horizon_ticks"],
        "metrics_rows": metrics_rows,
        "events_rows": events_rows,
        "source_ledger_rows": source_ledger_rows,
        "dimensionless": {
            "coupling_gain": round(params["utility_slope_cross_predict"] * params["membrane_permeability"], 6),
            "delay_relaxation_ratio": round(params["transfer_delay_ticks"] / params["artifact_relaxation_time_ticks"], 6),
            "prediction_cost_ratio": params["prediction_cost_work_fraction"],
            "transfer_cost_ratio": params["transfer_cost_work_fraction"],
            "memory_persistence": round(1.0 - params["artifact_decay"], 6),
            "threshold_adaptation_ratio": round(params["threshold_learning_rate_error"] / params["threshold_recovery_rate"], 6),
        },
        "artifacts": [
            "config.yaml",
            "manifest.yaml",
            "metrics.csv",
            "events.csv",
            "source_ledger.csv",
            "metrics_schema.csv",
            "events_schema.csv",
            "source_ledger_schema.csv",
            "summary.md",
        ],
        "mechanics_status": THREE_HIVE_RING_MECHANICS_STATUS,
        "scientific_status": THREE_HIVE_RING_MECHANICS_SCIENTIFIC_STATUS,
        "config": config,
    }


def _metric_fieldnames() -> tuple[str, ...]:
    return ("condition", "seed", "hive_id", *three_hive_ring_required_metric_fields())


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    if (output_path / "three_hive_ring_mechanics_manifest.csv").exists():
        raise FileExistsError(
            f"Output path {output_path} already contains three-hive ring mechanics artifacts."
        )


def _run_summary(condition: str, seed: int) -> str:
    return "\n".join(
        [
            "# Three-Hive Ring Mechanics Smoke Artifact",
            "",
            f"- Condition: `{condition}`",
            f"- Seed: `{seed}`",
            f"- Status: `{THREE_HIVE_RING_MECHANICS_STATUS}`",
            f"- Scientific status: `{THREE_HIVE_RING_MECHANICS_SCIENTIFIC_STATUS}`",
            "",
            "This directory contains deterministic smoke metrics/events/source-ledger artifacts.",
            "It is not a promotion analysis and does not support three-hive dynamics claims.",
            "",
        ]
    )


def _summary(rows: list[dict[str, Any]], seeds: tuple[int, ...]) -> str:
    return "\n".join(
        [
            "# Three-Hive Ring Mechanics Smoke",
            "",
            f"- Conditions: {len(THREE_HIVE_RING_CONDITIONS)}",
            f"- Seeds: {', '.join(str(seed) for seed in seeds)}",
            f"- Run directories: {len(rows)}",
            f"- Horizon: {THREE_HIVE_RING_SMOKE_PARAMETERS['horizon_ticks']} ticks",
            f"- Status: `{THREE_HIVE_RING_MECHANICS_STATUS}`",
            f"- Scientific status: `{THREE_HIVE_RING_MECHANICS_SCIENTIFIC_STATUS}`",
            "",
            "This helper emits the frozen metrics/events/source-ledger fields for the fixed paired-seed mechanics gate.",
            "It does not compute promotion endpoints, run broad sweeps, add integrations, or add hives beyond the frozen ring.",
            "",
        ]
    )


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def _linear_gate(value: float) -> float:
    return _clip(0.5 + 0.5 * value)


def _clip(value: float) -> float:
    params = THREE_HIVE_RING_SMOKE_PARAMETERS
    return max(float(params["artifact_clip_min"]), min(float(params["artifact_clip_max"]), value))


def _fatigue_increment(action: str) -> float:
    params = THREE_HIVE_RING_SMOKE_PARAMETERS
    if action == "predict_cross_hive":
        return float(params["fatigue_increment_predict"])
    if action == "work_local":
        return float(params["fatigue_increment_work"])
    if action == "review_inbound_artifact":
        return float(params["fatigue_increment_review"])
    if action == "synthesize_outbound_artifact":
        return float(params["fatigue_increment_synthesize"])
    return 0.0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the fixed three-hive ring deterministic mechanics smoke."
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_THREE_HIVE_RING_CONTRACT_CONFIG),
        help="Frozen three-hive ring contract fixture.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_THREE_HIVE_RING_SEEDS),
        help="Fixed deterministic paired seeds; preregistered value is 1 2.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_THREE_HIVE_RING_MECHANICS_DIR),
        help="Output directory for mechanics smoke artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_three_hive_ring_mechanics_smoke(
            config_path=args.config,
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
