"""Compare A5 predictive-control conditions under matched demand streams."""

from __future__ import annotations

import argparse
import csv
import zlib
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_attention import DEFAULT_SEEDS, _format_number
from ohdyn.config import ATTENTION_CLASSES, load_config
from ohdyn.run import run_experiment
from ohdyn.sim import SimulationResult


DEFAULT_BASE_CONFIG = Path("configs/a5_predictive_linear_smoke.yaml")

A5_PREDICTIVE_CONDITIONS = (
    ("reactive", 0.0, 3),
    ("linear", 0.35, 3),
    ("nonlinear", 0.65, 3),
    ("nonlinear_high_budget", 0.85, 4),
    ("oracle", 1.0, 3),
    ("shuffled", 0.35, 3),
    ("nonlinear_shuffled", 0.65, 3),
    ("nonlinear_high_budget_shuffled", 0.85, 4),
)

A5_1A_COST_CALIBRATION_CONDITIONS = (
    ("linear_harsh_cost", "linear", 0.35, 3, 1.0, None),
    ("linear_harsh_cost_spend_only_replay", "spend_only_replay", 0.35, 3, 1.0, None),
    ("linear_gentle_cost", "linear", 0.35, 3, 0.5, 0.25),
    ("linear_gentle_cost_spend_only_replay", "spend_only_replay", 0.35, 3, 0.5, 0.25),
    ("linear_capped_cost", "linear", 0.35, 3, 1.0, 0.25),
    ("linear_capped_cost_spend_only_replay", "spend_only_replay", 0.35, 3, 1.0, 0.25),
    ("linear_no_cost_diagnostic", "linear", 0.35, 3, 1.0, None),
)

A5_PREDICTIVE_COMPARISON_FIELDS = (
    "condition",
    "predictive_condition",
    "config",
    "prediction_budget",
    "prediction_cost_scale",
    "max_prediction_work_fraction_per_tick",
    "charge_prediction_to_work",
    "lead_ticks",
    "signal_period",
    "signal_amplitude",
    "seed_count",
    "run_count",
    "forecast_abs_error_final_mean",
    "forecast_skill_final_mean",
    "forecast_skill_per_budget_final_mean",
    "prediction_work_charged_final_mean",
    "work_budget_remaining_final_mean",
    "work_forecast_alignment_final_mean",
    "work_future_demand_alignment_final_mean",
    "allocation_future_residual_abs_final_mean",
    "tasks_created_mean",
    "tasks_completed_mean",
    "completion_fraction_mean",
    "queue_depth_mean",
    "queued_task_age_mean_final_mean",
    "attention_capture_pressure_max_final_mean",
)

A5_PREDICTIVE_EFFECT_FIELDS = (
    "effect_axis",
    "low_label",
    "high_label",
    "forecast_skill_final_mean_delta",
    "forecast_skill_per_budget_final_mean_delta",
    "prediction_work_charged_final_mean_delta",
    "work_budget_remaining_final_mean_delta",
    "work_future_demand_alignment_final_mean_delta",
    "allocation_future_residual_abs_final_mean_delta",
    "completion_fraction_mean_delta",
    "queue_depth_mean_delta",
    "queued_task_age_mean_final_mean_delta",
    "interpretation",
)

A5_ACCOUNTING_LOCK_FIELDS = (
    "condition",
    "seed",
    "tasks_created_total",
    "agent_tasks_created_total",
    "exogenous_tasks_created_total",
    "task_arrival_signature",
    "demand_stream_signature",
    "future_demand_stream_signature",
    "service_capacity",
    "action_opportunity_total",
    "work_opportunity_before_prediction_total",
    "prediction_work_charged_total",
    "work_budget_remaining_total",
    "matches_reactive_task_stream",
    "matches_reactive_demand_stream",
    "matches_reactive_service_capacity",
    "matches_reactive_action_opportunity",
    "matches_reactive_work_opportunity",
    "matches_budget_matched_null_prediction_spend",
    "status",
)


def run_predictive_control_comparison(
    *,
    base_config: str | Path = DEFAULT_BASE_CONFIG,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    out_dir: str | Path,
) -> list[dict[str, Any]]:
    _validate_seeds(seeds)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_configs = _write_condition_configs(Path(base_config), output_path / "configs")
    rows: list[dict[str, Any]] = []
    audit_inputs: list[tuple[str, int, SimulationResult]] = []
    for condition, config_path in generated_configs:
        results: list[SimulationResult] = []
        for seed in seeds:
            run_dir = output_path / f"{condition}_seed{seed}"
            result = run_experiment(config_path, seed=seed, out_dir=run_dir)
            results.append(result)
            audit_inputs.append((condition, seed, result))
        rows.append(_aggregate_row(condition, config_path, results))

    effect_rows = _effect_rows(rows)
    accounting_rows = _accounting_lock_rows(audit_inputs)
    _write_csv(
        output_path / "predictive_control_comparison_metrics.csv",
        A5_PREDICTIVE_COMPARISON_FIELDS,
        rows,
    )
    _write_csv(
        output_path / "predictive_control_effects.csv",
        A5_PREDICTIVE_EFFECT_FIELDS,
        effect_rows,
    )
    _write_csv(
        output_path / "predictive_control_accounting_locks.csv",
        A5_ACCOUNTING_LOCK_FIELDS,
        accounting_rows,
    )
    (output_path / "predictive_control_design_manifest.yaml").write_text(
        yaml.safe_dump(
            _design_manifest(
                base_config=Path(base_config),
                generated_configs=generated_configs,
                seeds=seeds,
            ),
            sort_keys=False,
        )
    )
    (output_path / "summary.md").write_text(
        _summary(rows, effect_rows, accounting_rows, seeds)
    )
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
            "predictive_control_comparison_metrics.csv",
            "predictive_control_effects.csv",
            "predictive_control_accounting_locks.csv",
            "predictive_control_design_manifest.yaml",
            "summary.md",
        )
        if (output_path / name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(
            f"Output path {output_path} already contains A5 predictive-control artifacts: {names}"
        )


def _write_condition_configs(
    base_config: Path,
    config_dir: Path,
) -> tuple[tuple[str, Path], ...]:
    cfg = load_config(base_config)
    if cfg.predictive_control is None:
        raise ValueError(f"{base_config} must enable predictive_control.")
    if cfg.attention_policy is None:
        raise ValueError(f"{base_config} must enable attention_policy.")
    if cfg.hives:
        raise ValueError(f"{base_config} must be a single-hive config.")

    raw = yaml.safe_load(base_config.read_text()) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{base_config} must contain a YAML mapping.")

    config_dir.mkdir(parents=True, exist_ok=True)
    generated = []
    if cfg.predictive_control.charge_prediction_to_work:
        condition_specs = A5_1A_COST_CALIBRATION_CONDITIONS
    else:
        condition_specs = tuple(
            (condition, condition, budget, memory_window, 1.0, None)
            for condition, budget, memory_window in A5_PREDICTIVE_CONDITIONS
        )
    for label, condition, budget, memory_window, cost_scale, max_work_fraction in condition_specs:
        condition_raw = dict(raw)
        condition_raw["run"] = dict(raw["run"])
        condition_raw["run"]["experiment_id"] = f"a5_predictive_{label}_comparison"
        condition_raw["predictive_control"] = dict(raw["predictive_control"])
        condition_raw["predictive_control"]["condition"] = condition
        condition_raw["predictive_control"]["prediction_budget"] = budget
        condition_raw["predictive_control"]["memory_window"] = memory_window
        condition_raw["predictive_control"]["prediction_cost_scale"] = cost_scale
        if max_work_fraction is None:
            condition_raw["predictive_control"].pop(
                "max_prediction_work_fraction_per_tick",
                None,
            )
        else:
            condition_raw["predictive_control"][
                "max_prediction_work_fraction_per_tick"
            ] = max_work_fraction
        if label == "linear_no_cost_diagnostic":
            condition_raw["predictive_control"]["charge_prediction_to_work"] = False
        path = config_dir / f"a5_predictive_{label}.yaml"
        path.write_text(yaml.safe_dump(condition_raw, sort_keys=False))
        generated.append((label, path))
    return tuple(generated)


def _aggregate_row(
    condition: str,
    config_path: Path,
    results: list[SimulationResult],
) -> dict[str, Any]:
    last_rows = [result.metrics[-1] for result in results]
    cfg = results[0].config
    assert cfg.predictive_control is not None
    created_values = [float(row["tasks_created_total"]) for row in last_rows]
    completed_values = [float(row["tasks_completed_total"]) for row in last_rows]
    residual_abs_values = [
        sum(
            abs(float(row[f"a5_{class_name}_allocation_future_residual_tick"]))
            for class_name in ATTENTION_CLASSES
        )
        / len(ATTENTION_CLASSES)
        for row in last_rows
    ]
    return {
        "condition": condition,
        "predictive_condition": cfg.predictive_control.condition,
        "config": str(Path("configs") / config_path.name),
        "prediction_budget": cfg.predictive_control.prediction_budget,
        "prediction_cost_scale": cfg.predictive_control.prediction_cost_scale,
        "max_prediction_work_fraction_per_tick": (
            ""
            if cfg.predictive_control.max_prediction_work_fraction_per_tick is None
            else cfg.predictive_control.max_prediction_work_fraction_per_tick
        ),
        "charge_prediction_to_work": str(cfg.predictive_control.charge_prediction_to_work).lower(),
        "lead_ticks": cfg.predictive_control.lead_ticks,
        "signal_period": cfg.predictive_control.signal_period,
        "signal_amplitude": cfg.predictive_control.signal_amplitude,
        "seed_count": len(results),
        "run_count": len(results),
        "forecast_abs_error_final_mean": _mean_metric(last_rows, "a5_forecast_abs_error_tick"),
        "forecast_skill_final_mean": _mean_metric(last_rows, "a5_forecast_skill_tick"),
        "forecast_skill_per_budget_final_mean": _mean_metric(
            last_rows,
            "a5_forecast_skill_per_budget_tick",
        ),
        "prediction_work_charged_final_mean": _mean_metric(
            last_rows,
            "a5_prediction_work_charged_tick",
        ),
        "work_budget_remaining_final_mean": _mean_metric(
            last_rows,
            "a5_work_budget_remaining_tick",
        ),
        "work_forecast_alignment_final_mean": _mean_metric(
            last_rows,
            "a5_work_forecast_alignment_tick",
        ),
        "work_future_demand_alignment_final_mean": _mean_metric(
            last_rows,
            "a5_work_future_demand_alignment_tick",
        ),
        "allocation_future_residual_abs_final_mean": _mean_values(residual_abs_values),
        "tasks_created_mean": _mean_values(created_values),
        "tasks_completed_mean": _mean_values(completed_values),
        "completion_fraction_mean": _mean_values(
            [
                _safe_ratio(completed, created)
                for created, completed in zip(created_values, completed_values, strict=True)
            ]
        ),
        "queue_depth_mean": _mean_metric(last_rows, "queue_depth"),
        "queued_task_age_mean_final_mean": _mean_metric(last_rows, "queued_task_age_mean_tick"),
        "attention_capture_pressure_max_final_mean": _mean_metric(
            last_rows,
            "attention_capture_pressure_max_tick",
        ),
    }


def _effect_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_condition = {str(row["condition"]): row for row in rows}
    if "linear_harsh_cost" in by_condition:
        pairs = (
            (
                "a5_1a_spend_only_replay_null",
                "linear_harsh_cost_spend_only_replay",
                "linear_harsh_cost",
            ),
            (
                "a5_1a_spend_only_replay_null",
                "linear_gentle_cost_spend_only_replay",
                "linear_gentle_cost",
            ),
            (
                "a5_1a_spend_only_replay_null",
                "linear_capped_cost_spend_only_replay",
                "linear_capped_cost",
            ),
            ("a5_1a_cost_scale", "linear_harsh_cost", "linear_gentle_cost"),
            ("a5_1a_cost_cap", "linear_harsh_cost", "linear_capped_cost"),
            ("a5_1a_no_cost_diagnostic", "linear_harsh_cost", "linear_no_cost_diagnostic"),
        )
    else:
        pairs = (
            ("condition_vs_reactive", "reactive", "linear"),
            ("condition_vs_reactive", "reactive", "nonlinear"),
            ("condition_vs_reactive", "reactive", "nonlinear_high_budget"),
            ("condition_vs_reactive", "reactive", "oracle"),
            ("condition_vs_shuffled", "shuffled", "linear"),
            ("condition_vs_budget_matched_shuffled", "nonlinear_shuffled", "nonlinear"),
            (
                "condition_vs_budget_matched_shuffled",
                "nonlinear_high_budget_shuffled",
                "nonlinear_high_budget",
            ),
            ("oracle_vs_nonlinear", "nonlinear", "oracle"),
            ("oracle_vs_high_budget_nonlinear", "nonlinear_high_budget", "oracle"),
        )
    return [
        _effect_row(effect_axis, by_condition[low_label], by_condition[high_label])
        for effect_axis, low_label, high_label in pairs
    ]


def _effect_row(
    effect_axis: str,
    low: dict[str, Any],
    high: dict[str, Any],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "effect_axis": effect_axis,
        "low_label": low["condition"],
        "high_label": high["condition"],
    }
    for field in A5_PREDICTIVE_EFFECT_FIELDS:
        if field.endswith("_delta"):
            base_field = field.removesuffix("_delta")
            row[field] = _as_float(high[base_field]) - _as_float(low[base_field])
    row["interpretation"] = _interpret_effect(row)
    return row


def _interpret_effect(row: dict[str, Any]) -> str:
    skill_delta = _as_float(row["forecast_skill_final_mean_delta"])
    residual_delta = _as_float(row["allocation_future_residual_abs_final_mean_delta"])
    queue_delta = _as_float(row["queue_depth_mean_delta"])
    if skill_delta > 0.0 and residual_delta < 0.0:
        return "forecast skill improves with closer allocation to future demand"
    if skill_delta > 0.0 and queue_delta <= 0.0:
        return "forecast skill improves without higher final queue depth"
    if skill_delta <= 0.0:
        return "no forecast-skill improvement"
    return "forecast skill improves but allocation/load controls need follow-up"


def _accounting_lock_rows(
    audit_inputs: list[tuple[str, int, SimulationResult]],
) -> list[dict[str, Any]]:
    raw_rows = [
        _accounting_lock_base_row(condition, seed, result)
        for condition, seed, result in audit_inputs
    ]
    reactive_by_seed = {
        int(row["seed"]): row for row in raw_rows if row["condition"] == "reactive"
    }
    reference_by_seed: dict[int, dict[str, Any]] = {}
    for row in raw_rows:
        seed = int(row["seed"])
        if seed not in reference_by_seed:
            reference_by_seed[seed] = row
    reference_by_seed.update(reactive_by_seed)
    by_condition_seed = {
        (str(row["condition"]), int(row["seed"])): row for row in raw_rows
    }
    null_by_condition = _budget_null_map({str(row["condition"]) for row in raw_rows})

    rows: list[dict[str, Any]] = []
    for row in raw_rows:
        seed = int(row["seed"])
        reactive = reference_by_seed.get(seed)
        if reactive is None:
            raise ValueError(f"A5 comparison is missing accounting reference seed {seed}.")
        task_match = _same_fields(
            row,
            reactive,
            (
                "tasks_created_total",
                "agent_tasks_created_total",
                "exogenous_tasks_created_total",
                "task_arrival_signature",
            ),
        )
        demand_match = _same_fields(
            row,
            reactive,
            ("demand_stream_signature", "future_demand_stream_signature"),
        )
        service_match = _same_fields(row, reactive, ("service_capacity",))
        action_match = _same_fields(row, reactive, ("action_opportunity_total",))
        work_opportunity_match = _same_fields(
            row,
            reactive,
            ("work_opportunity_before_prediction_total",),
        )
        null_label = null_by_condition.get(str(row["condition"]))
        if null_label is None:
            spend_match = "not_applicable"
        else:
            null_row = by_condition_seed.get((null_label, seed))
            if null_row is None:
                raise ValueError(
                    f"A5 comparison is missing budget-matched null {null_label} seed {seed}."
                )
            spend_match = str(
                _same_fields(
                    row,
                    null_row,
                    ("prediction_work_charged_total", "work_budget_remaining_total"),
                )
            ).lower()
        status = (
            "pass"
            if all(
                (
                    task_match,
                    demand_match,
                    service_match,
                    action_match,
                    work_opportunity_match,
                    spend_match != "false",
                )
            )
            else "fail"
        )
        rows.append(
            {
                **row,
                "matches_reactive_task_stream": str(task_match).lower(),
                "matches_reactive_demand_stream": str(demand_match).lower(),
                "matches_reactive_service_capacity": str(service_match).lower(),
                "matches_reactive_action_opportunity": str(action_match).lower(),
                "matches_reactive_work_opportunity": str(work_opportunity_match).lower(),
                "matches_budget_matched_null_prediction_spend": spend_match,
                "status": status,
            }
        )
    return rows


def _accounting_lock_base_row(
    condition: str,
    seed: int,
    result: SimulationResult,
) -> dict[str, Any]:
    final = result.metrics[-1]
    return {
        "condition": condition,
        "seed": seed,
        "tasks_created_total": final["tasks_created_total"],
        "agent_tasks_created_total": final["agent_tasks_created_total"],
        "exogenous_tasks_created_total": final["exogenous_tasks_created_total"],
        "task_arrival_signature": _series_signature(
            result.metrics,
            ("tasks_created_tick", "agent_tasks_created_tick", "exogenous_tasks_created_tick"),
        ),
        "demand_stream_signature": _series_signature(
            result.metrics,
            tuple(
                f"a5_{class_name}_demand_share_tick"
                for class_name in ATTENTION_CLASSES
            ),
        ),
        "future_demand_stream_signature": _series_signature(
            result.metrics,
            tuple(
                f"a5_{class_name}_future_demand_share_tick"
                for class_name in ATTENTION_CLASSES
            ),
        ),
        "service_capacity": result.config.model.work_service_capacity,
        "action_opportunity_total": _sum_metric(
            result.metrics,
            "a5_work_opportunity_before_prediction_tick",
        ),
        "work_opportunity_before_prediction_total": _sum_metric(
            result.metrics,
            "a5_work_opportunity_before_prediction_tick",
        ),
        "prediction_work_charged_total": _sum_metric(
            result.metrics,
            "a5_prediction_work_charged_tick",
        ),
        "work_budget_remaining_total": _sum_metric(
            result.metrics,
            "a5_work_budget_remaining_tick",
        ),
    }


def _budget_null_map(conditions: set[str]) -> dict[str, str]:
    if "linear_harsh_cost" in conditions:
        return {
            "linear_harsh_cost": "linear_harsh_cost_spend_only_replay",
            "linear_gentle_cost": "linear_gentle_cost_spend_only_replay",
            "linear_capped_cost": "linear_capped_cost_spend_only_replay",
        }
    return {
        "linear": "shuffled",
        "nonlinear": "nonlinear_shuffled",
        "nonlinear_high_budget": "nonlinear_high_budget_shuffled",
    }


def _design_manifest(
    *,
    base_config: Path,
    generated_configs: tuple[tuple[str, Path], ...],
    seeds: tuple[int, ...],
) -> dict[str, Any]:
    labels = tuple(label for label, _ in generated_configs)
    return {
        "stage": "A5 single-hive anticipatory predictive control",
        "preregistration": (
            "docs/a5_single_hive_anticipatory_predictive_control_preregistration.md"
        ),
        "base_config": str(base_config),
        "seeds": list(seeds),
        "scope": {
            "single_hive_only": True,
            "deterministic": True,
            "no_external_services": True,
            "no_multi_hive_coupling": True,
        },
        "conditions": [
            _condition_manifest_row(label, config_path)
            for label, config_path in generated_configs
        ],
        "prediction_budget_axis": _prediction_budget_axis(generated_configs),
        "budget_matched_null_pairings": _budget_null_map(set(labels)),
        "accounting_locks": {
            "artifact": "predictive_control_accounting_locks.csv",
            "required_fields": list(A5_ACCOUNTING_LOCK_FIELDS),
            "must_pass_before_residual_interpretation": True,
        },
        "residual_interpretation": {
            "strange_attractor_like_claims": "secondary_fail_closed",
            "requires_surrogate_nulls": True,
        },
        "timing_broken_null_controls": [
            _null_control_manifest_row(label, config_path)
            for label, config_path in generated_configs
            if _condition_manifest_row(label, config_path)["predictive_condition"]
            in {"shuffled", "nonlinear_shuffled", "nonlinear_high_budget_shuffled"}
        ],
    }


def _condition_manifest_row(label: str, config_path: Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    assert cfg.predictive_control is not None
    return {
        "label": label,
        "config": str(Path("configs") / config_path.name),
        "predictive_condition": cfg.predictive_control.condition,
        "prediction_budget": cfg.predictive_control.prediction_budget,
        "lead_ticks": cfg.predictive_control.lead_ticks,
        "signal_period": cfg.predictive_control.signal_period,
        "signal_amplitude": cfg.predictive_control.signal_amplitude,
        "memory_window": cfg.predictive_control.memory_window,
        "phase_shift_ticks": cfg.predictive_control.phase_shift_ticks,
        "prediction_cost_scale": cfg.predictive_control.prediction_cost_scale,
        "max_prediction_work_fraction_per_tick": (
            cfg.predictive_control.max_prediction_work_fraction_per_tick
        ),
        "charge_prediction_to_work": cfg.predictive_control.charge_prediction_to_work,
    }


def _prediction_budget_axis(
    generated_configs: tuple[tuple[str, Path], ...],
) -> list[dict[str, Any]]:
    axis: list[dict[str, Any]] = []
    seen: set[tuple[str, float, bool]] = set()
    for label, config_path in generated_configs:
        cfg = load_config(config_path)
        assert cfg.predictive_control is not None
        key = (
            cfg.predictive_control.condition,
            cfg.predictive_control.prediction_budget,
            cfg.predictive_control.charge_prediction_to_work,
        )
        if key in seen:
            continue
        seen.add(key)
        axis.append(
            {
                "label": label,
                "predictive_condition": cfg.predictive_control.condition,
                "prediction_budget": cfg.predictive_control.prediction_budget,
                "charge_prediction_to_work": cfg.predictive_control.charge_prediction_to_work,
            }
        )
    return axis


def _null_control_manifest_row(label: str, config_path: Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    assert cfg.predictive_control is not None
    return {
        "label": label,
        "predictive_condition": cfg.predictive_control.condition,
        "prediction_budget": cfg.predictive_control.prediction_budget,
        "phase_shift_ticks": cfg.predictive_control.phase_shift_ticks,
        "null_type": "deterministic_phase_shifted_timing_broken_predictor",
        "preserves": [
            "prediction_budget",
            "signal_period",
            "signal_amplitude",
            "memory_window",
            "task_arrival_stream",
            "demand_share_stream",
            "service_capacity",
            "action_opportunity",
            "work_opportunity",
        ],
        "breaks": "useful forecast timing",
    }


def _same_fields(
    left: dict[str, Any],
    right: dict[str, Any],
    fields: tuple[str, ...],
) -> bool:
    return all(str(left[field]) == str(right[field]) for field in fields)


def _series_signature(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> str:
    payload = "|".join(
        ",".join(str(row[field]) for field in fields)
        for row in rows
    )
    return f"{zlib.crc32(payload.encode('utf-8')):08x}"


def _sum_metric(rows: list[dict[str, Any]], field: str) -> float:
    return round(sum(float(row[field]) for row in rows), 6)


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    accounting_rows: list[dict[str, Any]],
    seeds: tuple[int, ...],
) -> str:
    lines = [
        "# A5 Predictive-Control Comparison",
        "",
        f"- seeds: {', '.join(str(seed) for seed in seeds)}",
        f"- run count: {sum(int(row['run_count']) for row in rows)}",
        "- scope: single-hive matched-demand pilot; no multi-hive coupling or external services",
        "",
        "## Condition Means",
        "",
    ]
    for row in rows:
        lines.append(
            "- "
            f"{row['condition']}: budget={_format_number(row['prediction_budget'])}, "
            f"cost_scale={_format_number(row['prediction_cost_scale'])}, "
            f"max_work_fraction={row['max_prediction_work_fraction_per_tick'] or 'uncapped'}, "
            f"charged_to_work={row['charge_prediction_to_work']}, "
            f"forecast_skill={_format_number(row['forecast_skill_final_mean'])}, "
            f"skill_per_budget={_format_number(row['forecast_skill_per_budget_final_mean'])}, "
            f"prediction_work_charged={_format_number(row['prediction_work_charged_final_mean'])}, "
            f"work_budget_remaining={_format_number(row['work_budget_remaining_final_mean'])}, "
            f"future_alignment={_format_number(row['work_future_demand_alignment_final_mean'])}, "
            f"residual_abs={_format_number(row['allocation_future_residual_abs_final_mean'])}, "
            f"completion_fraction={_format_number(row['completion_fraction_mean'])}, "
            f"queue_depth={_format_number(row['queue_depth_mean'])}"
        )
    lines.extend(["", "## Effects", ""])
    for row in effect_rows:
        lines.append(
            "- "
            f"{row['high_label']} minus {row['low_label']}: "
            f"forecast_skill_delta={_format_number(row['forecast_skill_final_mean_delta'])}, "
            f"residual_abs_delta={_format_number(row['allocation_future_residual_abs_final_mean_delta'])}, "
            f"queue_depth_delta={_format_number(row['queue_depth_mean_delta'])}; "
            f"{row['interpretation']}"
        )
    passed_locks = sum(1 for row in accounting_rows if row["status"] == "pass")
    lines.extend(
        [
            "",
            "## Accounting Locks",
            "",
            (
                f"- pass rows: {passed_locks}/{len(accounting_rows)} "
                "for matched task stream, demand stream, service capacity, "
                "action opportunity, work opportunity, and budget-matched "
                "null prediction-spend checks"
            ),
            "- artifact: predictive_control_accounting_locks.csv",
        ]
    )
    lines.extend(
        [
            "",
            "## Conservative Use",
            "",
            (
                "This pilot compares forecast modes under matched task-arrival, action, "
                "service, and deterministic demand-signal settings. Treat throughput and "
                "queue changes as guardrails, not as evidence for structured dynamics. "
                "`shuffled` is the linear-budget timing-broken null; "
                "`nonlinear_shuffled` is the medium nonlinear-budget timing-broken null; "
                "`nonlinear_high_budget_shuffled` is the high nonlinear-budget "
                "timing-broken null. A5.1a `*_spend_only_replay` rows are cost-matched "
                "replay nulls that pay the same configured prediction-work charge rule "
                "while breaking useful forecast timing."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def _mean_metric(rows: list[dict[str, Any]], field: str) -> float:
    return _mean_values([float(row[field]) for row in rows])


def _mean_values(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def _safe_ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _as_float(value: Any) -> float:
    return float(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a matched A5 predictive-control comparison."
    )
    parser.add_argument(
        "--base-config",
        default=str(DEFAULT_BASE_CONFIG),
        help="Base A5 predictive-control YAML config.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_SEEDS),
        help="Deterministic paired seeds.",
    )
    parser.add_argument("--out", required=True, help="Output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_predictive_control_comparison(
            base_config=args.base_config,
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
