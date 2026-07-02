"""Run a bounded A6 logistic-appraisal smoke comparison."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_attention import _format_number
from ohdyn.config import LOGISTIC_APPRAISAL_CONDITIONS, load_config
from ohdyn.run import run_experiment
from ohdyn.sim import SimulationResult


DEFAULT_A6_SEEDS = (1, 2)
DEFAULT_A6_COMPARE_DIR = Path("runs/a6_logistic_appraisal_compare")
A6_SMOKE_CONFIGS = (
    ("logistic", Path("configs/a6_logistic_appraisal_smoke.yaml")),
    ("linear", Path("configs/a6_linear_appraisal_smoke.yaml")),
    ("threshold_shuffled", Path("configs/a6_threshold_shuffled_smoke.yaml")),
    ("phase_shuffled", Path("configs/a6_phase_shuffled_smoke.yaml")),
)
A6_2_LONG_HORIZON_CONFIGS = (
    ("logistic", Path("configs/a6_2_long_horizon_logistic.yaml")),
    ("linear", Path("configs/a6_2_long_horizon_linear.yaml")),
    ("threshold_shuffled", Path("configs/a6_2_long_horizon_threshold_shuffled.yaml")),
    ("phase_shuffled", Path("configs/a6_2_long_horizon_phase_shuffled.yaml")),
)
A6_1_SOURCE_NULL_CONDITIONS = (
    "source_label_shuffled_within_tick",
    "handoff_success_timing_broken_matched_counts",
)
A6_BOUNDED_RESOURCE_REPLAY_CONDITION = "budget_matched_prediction_replay"
_A6_ARTIFACT_EVENT_FIELDS = (
    "artifact_novelty",
    "artifact_coherence",
    "artifact_actionability",
    "artifact_provenance_debt",
    "artifact_risk",
    "artifact_contradiction",
    "artifact_readiness",
    "artifact_implementation_maturity",
    "artifact_communication_maturity",
)
_A6_ARTIFACT_METRIC_FIELDS = {
    field: f"a6_{field}_tick" for field in _A6_ARTIFACT_EVENT_FIELDS
}
_A6_SOURCE_DELTA_COLUMNS = (
    "a6_artifact_delta_ambient",
    "a6_artifact_delta_handoff_attempt",
    "a6_artifact_delta_handoff_success",
    "a6_artifact_delta_handoff_failure",
    "a6_artifact_delta_prediction_expenditure",
    "a6_artifact_delta_prediction_error",
    "a6_artifact_delta_queue_work_accounting",
    "a6_artifact_delta_noise",
)

A6_COMPARISON_FIELDS = (
    "condition",
    "config",
    "seed_count",
    "run_count",
    "tick_count",
    "appraisal_gain",
    "sigmoid_slope",
    "prediction_budget",
    "final_latent_activation_mean",
    "final_latent_focus_mean",
    "final_latent_fatigue_mean",
    "final_latent_prediction_error_abs_mean",
    "final_artifact_readiness_mean",
    "final_artifact_utility_mean",
    "handoff_attempts_total_mean",
    "handoff_successes_total_mean",
    "handoff_failures_total_mean",
    "prediction_budget_spent_total_mean",
    "tasks_created_mean",
    "tasks_completed_mean",
    "completion_fraction_mean",
    "queue_depth_mean",
    "queued_task_age_mean_final_mean",
)

A6_EFFECT_FIELDS = (
    "effect_axis",
    "low_label",
    "high_label",
    "final_latent_activation_mean_delta",
    "final_latent_fatigue_mean_delta",
    "final_latent_prediction_error_abs_mean_delta",
    "final_artifact_readiness_mean_delta",
    "final_artifact_utility_mean_delta",
    "handoff_successes_total_mean_delta",
    "handoff_failures_total_mean_delta",
    "prediction_budget_spent_total_mean_delta",
    "completion_fraction_mean_delta",
    "queue_depth_mean_delta",
    "queued_task_age_mean_final_mean_delta",
    "interpretation",
)

_OUTPUT_NAMES = (
    "a6_logistic_appraisal_comparison_metrics.csv",
    "a6_logistic_appraisal_effects.csv",
    "summary.md",
)


def run_a6_logistic_appraisal_comparison(
    *,
    seeds: tuple[int, ...] = DEFAULT_A6_SEEDS,
    out_dir: str | Path = DEFAULT_A6_COMPARE_DIR,
    include_a6_1_nulls: bool = False,
    include_bounded_resource_replay: bool = False,
    config_specs: tuple[tuple[str, Path], ...] = A6_SMOKE_CONFIGS,
    summary_title: str = "A6 Logistic-Appraisal Smoke Comparison",
    scope_line: str = "four checked-in single-hive smoke fixtures only; no broad sweep",
    scientific_status: str = "smoke artifact comparison, not promotion evidence",
    conservative_use: str = (
        "This helper is limited to the preregistered A6 smoke fixtures. "
        "Use these artifacts to exercise schemas and the read-only analyzer; "
        "do not treat them as evidence for residual latent-state attractors."
    ),
) -> list[dict[str, Any]]:
    _validate_seeds(seeds)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    _validate_a6_configs(config_specs)
    output_path.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    logistic_results_by_seed: dict[int, SimulationResult] = {}
    for condition, config_path in config_specs:
        results: list[SimulationResult] = []
        for seed in seeds:
            run_dir = output_path / f"{condition}_seed{seed}"
            results.append(run_experiment(config_path, seed=seed, out_dir=run_dir))
            if condition == "logistic":
                logistic_results_by_seed[seed] = results[-1]
        rows.append(_aggregate_row(condition, config_path, results))

    if include_a6_1_nulls:
        for null_condition in A6_1_SOURCE_NULL_CONDITIONS:
            results = []
            for seed in seeds:
                source_dir = output_path / f"logistic_seed{seed}"
                run_dir = output_path / f"{null_condition}_seed{seed}"
                _write_a6_1_null_run(
                    source_dir=source_dir,
                    out_dir=run_dir,
                    condition=null_condition,
                    seed=seed,
                )
                base_result = logistic_results_by_seed[seed]
                results.append(
                    SimulationResult(
                        config=base_result.config,
                        seed=base_result.seed,
                        bus_graph=base_result.bus_graph,
                        agents=base_result.agents,
                        metrics=_read_csv(run_dir / "metrics.csv"),
                        events=_read_csv(run_dir / "events.csv"),
                    )
                )
            rows.append(
                _aggregate_row(
                    null_condition,
                    Path(f"derived:{null_condition}:{_logistic_config_path(config_specs)}"),
                    results,
                )
            )
    if include_bounded_resource_replay:
        results = []
        for seed in seeds:
            source_dir = output_path / f"logistic_seed{seed}"
            run_dir = output_path / f"{A6_BOUNDED_RESOURCE_REPLAY_CONDITION}_seed{seed}"
            _write_budget_matched_prediction_replay_run(
                source_dir=source_dir,
                out_dir=run_dir,
                seed=seed,
            )
            base_result = logistic_results_by_seed[seed]
            results.append(
                SimulationResult(
                    config=base_result.config,
                    seed=base_result.seed,
                    bus_graph=base_result.bus_graph,
                    agents=base_result.agents,
                    metrics=_read_csv(run_dir / "metrics.csv"),
                    events=_read_csv(run_dir / "events.csv"),
                )
            )
        rows.append(
            _aggregate_row(
                A6_BOUNDED_RESOURCE_REPLAY_CONDITION,
                Path(
                    "derived:"
                    f"{A6_BOUNDED_RESOURCE_REPLAY_CONDITION}:"
                    f"{_logistic_config_path(config_specs)}"
                ),
                results,
            )
        )

    effect_rows = _effect_rows(rows)
    _write_csv(
        output_path / "a6_logistic_appraisal_comparison_metrics.csv",
        A6_COMPARISON_FIELDS,
        rows,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_effects.csv",
        A6_EFFECT_FIELDS,
        effect_rows,
    )
    (output_path / "summary.md").write_text(
        _summary(
            rows,
            effect_rows,
            seeds,
            title=summary_title,
            scope_line=scope_line,
            scientific_status=scientific_status,
            conservative_use=conservative_use,
        )
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
    collisions = [name for name in _OUTPUT_NAMES if (output_path / name).exists()]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains A6 artifacts: {names}")


def _validate_a6_configs(config_specs: tuple[tuple[str, Path], ...]) -> None:
    expected_conditions = set(LOGISTIC_APPRAISAL_CONDITIONS)
    observed_conditions = {condition for condition, _ in config_specs}
    if observed_conditions != expected_conditions:
        raise ValueError("A6 comparison must include exactly the preregistered conditions.")

    for condition, config_path in config_specs:
        cfg = load_config(config_path)
        if cfg.logistic_appraisal is None:
            raise ValueError(f"{config_path} must enable logistic_appraisal.")
        if cfg.logistic_appraisal.condition != condition:
            raise ValueError(
                f"{config_path} condition {cfg.logistic_appraisal.condition!r} "
                f"does not match {condition!r}."
            )
        if cfg.hives:
            raise ValueError(f"{config_path} must remain single-hive for A6 smoke.")


def _logistic_config_path(config_specs: tuple[tuple[str, Path], ...]) -> str:
    for condition, config_path in config_specs:
        if condition == "logistic":
            return str(config_path)
    raise ValueError("A6 comparison requires a logistic config.")


def _aggregate_row(
    condition: str,
    config_path: Path,
    results: list[SimulationResult],
) -> dict[str, Any]:
    cfg = results[0].config
    assert cfg.logistic_appraisal is not None
    last_rows = [result.metrics[-1] for result in results]
    created_values = [float(row["tasks_created_total"]) for row in last_rows]
    completed_values = [float(row["tasks_completed_total"]) for row in last_rows]
    handoff_attempt_totals = [
        sum(float(row["a6_handoff_attempts_tick"]) for row in result.metrics)
        for result in results
    ]
    handoff_success_totals = [
        sum(float(row["a6_handoff_successes_tick"]) for row in result.metrics)
        for result in results
    ]
    handoff_failure_totals = [
        sum(float(row["a6_handoff_failures_tick"]) for row in result.metrics)
        for result in results
    ]
    prediction_spend_totals = [
        sum(float(row["a6_prediction_budget_spent_tick"]) for row in result.metrics)
        for result in results
    ]

    return {
        "condition": condition,
        "config": str(config_path),
        "seed_count": len(results),
        "run_count": len(results),
        "tick_count": cfg.run.ticks,
        "appraisal_gain": cfg.logistic_appraisal.appraisal_gain,
        "sigmoid_slope": cfg.logistic_appraisal.sigmoid_slope,
        "prediction_budget": cfg.logistic_appraisal.prediction_budget,
        "final_latent_activation_mean": _mean_metric(
            last_rows, "a6_latent_activation_mean_tick"
        ),
        "final_latent_focus_mean": _mean_metric(last_rows, "a6_latent_focus_mean_tick"),
        "final_latent_fatigue_mean": _mean_metric(last_rows, "a6_latent_fatigue_mean_tick"),
        "final_latent_prediction_error_abs_mean": _mean_values(
            [abs(float(row["a6_latent_prediction_error_mean_tick"])) for row in last_rows]
        ),
        "final_artifact_readiness_mean": _mean_metric(last_rows, "a6_artifact_readiness_tick"),
        "final_artifact_utility_mean": _mean_values(
            [_artifact_utility(row) for row in last_rows]
        ),
        "handoff_attempts_total_mean": _mean_values(handoff_attempt_totals),
        "handoff_successes_total_mean": _mean_values(handoff_success_totals),
        "handoff_failures_total_mean": _mean_values(handoff_failure_totals),
        "prediction_budget_spent_total_mean": _mean_values(prediction_spend_totals),
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
    }


def _artifact_utility(row: dict[str, Any]) -> float:
    positive = (
        float(row["a6_artifact_readiness_tick"])
        + float(row["a6_artifact_coherence_tick"])
        + float(row["a6_artifact_actionability_tick"])
        + float(row["a6_artifact_implementation_maturity_tick"])
        + float(row["a6_artifact_communication_maturity_tick"])
    )
    negative = (
        float(row["a6_artifact_provenance_debt_tick"])
        + float(row["a6_artifact_risk_tick"])
        + float(row["a6_artifact_contradiction_tick"])
    )
    return round((positive - negative) / 5.0, 6)


def _effect_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_condition = {str(row["condition"]): row for row in rows}
    pairs = [
        ("logistic_vs_linear", "linear", "logistic"),
        ("logistic_vs_phase_shuffled", "phase_shuffled", "logistic"),
        ("logistic_vs_threshold_shuffled", "threshold_shuffled", "logistic"),
    ]
    for null_condition in A6_1_SOURCE_NULL_CONDITIONS:
        if null_condition in by_condition:
            pairs.append((f"logistic_vs_{null_condition}", null_condition, "logistic"))
    if A6_BOUNDED_RESOURCE_REPLAY_CONDITION in by_condition:
        pairs.append(
            (
                f"logistic_vs_{A6_BOUNDED_RESOURCE_REPLAY_CONDITION}",
                A6_BOUNDED_RESOURCE_REPLAY_CONDITION,
                "logistic",
            )
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
    for field in A6_EFFECT_FIELDS:
        if field.endswith("_delta"):
            base_field = field.removesuffix("_delta")
            row[field] = _as_float(high[base_field]) - _as_float(low[base_field])
    row["interpretation"] = _interpret_effect(row)
    return row


def _interpret_effect(row: dict[str, Any]) -> str:
    utility_delta = _as_float(row["final_artifact_utility_mean_delta"])
    queue_delta = _as_float(row["queue_depth_mean_delta"])
    failure_delta = _as_float(row["handoff_failures_total_mean_delta"])
    if utility_delta > 0.0 and queue_delta <= 0.0 and failure_delta <= 0.0:
        return "comparison guardrails improve, but residual recurrence remains unanalyzed"
    if utility_delta <= 0.0:
        return "artifact-utility guardrail does not improve in this comparison"
    if queue_delta > 0.0:
        return "artifact utility improves with higher queue load; treat as accounting risk"
    return "artifact comparison only; read-only residual analysis required before interpretation"


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_a6_1_null_run(
    *,
    source_dir: Path,
    out_dir: Path,
    condition: str,
    seed: int,
) -> None:
    if out_dir.exists():
        raise FileExistsError(f"Output path {out_dir} already exists.")
    shutil.copytree(source_dir, out_dir)
    _rewrite_null_config(out_dir / "config.yaml", condition)
    events = _read_csv(out_dir / "events.csv")
    metrics = _read_csv(out_dir / "metrics.csv")
    if condition == "source_label_shuffled_within_tick":
        events = _source_label_shuffled_events(events, seed)
    elif condition == "handoff_success_timing_broken_matched_counts":
        events = _handoff_success_timing_broken_events(events, seed)
        metrics = _metrics_with_transformed_artifacts(
            metrics=metrics,
            original_events=_read_csv(source_dir / "events.csv"),
            transformed_events=events,
        )
    else:
        raise ValueError(f"Unknown A6.1 null condition: {condition}")
    _write_dict_csv(out_dir / "events.csv", events)
    _write_dict_csv(out_dir / "metrics.csv", metrics)
    summary_path = out_dir / "summary.md"
    summary_path.write_text(
        summary_path.read_text()
        + "\n\n"
        + "## A6.1 Source-Preserving Null\n\n"
        + f"- derived_condition: {condition}\n"
        + "- source_run: logistic with the same deterministic seed\n"
        + "- scientific status: read-only null artifact; not a simulator mechanism\n"
    )


def _write_budget_matched_prediction_replay_run(
    *,
    source_dir: Path,
    out_dir: Path,
    seed: int,
) -> None:
    if out_dir.exists():
        raise FileExistsError(f"Output path {out_dir} already exists.")
    shutil.copytree(source_dir, out_dir)
    _rewrite_null_config(out_dir / "config.yaml", A6_BOUNDED_RESOURCE_REPLAY_CONDITION)
    events = _prediction_replay_events(_read_csv(out_dir / "events.csv"), seed)
    metrics = _prediction_replay_metrics(
        metrics=_read_csv(out_dir / "metrics.csv"),
        original_events=_read_csv(source_dir / "events.csv"),
        transformed_events=events,
        seed=seed,
    )
    _write_dict_csv(out_dir / "events.csv", events)
    _write_dict_csv(out_dir / "metrics.csv", metrics)
    summary_path = out_dir / "summary.md"
    summary_path.write_text(
        summary_path.read_text()
        + "\n\n"
        + "## A6 Bounded Prediction-Resource Replay Null\n\n"
        + f"- derived_condition: {A6_BOUNDED_RESOURCE_REPLAY_CONDITION}\n"
        + "- source_run: logistic with the same deterministic seed\n"
        + "- prediction spend/action ticks: preserved exactly from source run\n"
        + "- replay transform: deterministic phase rotation of prediction-derived "
        + "artifact deltas and prediction-error traces\n"
        + "- scientific status: budget-matched replay control artifact; not a "
        + "new simulator mechanism or promotion run\n"
    )


def _rewrite_null_config(path: Path, condition: str) -> None:
    config = yaml.safe_load(path.read_text()) or {}
    logistic_appraisal = config.setdefault("logistic_appraisal", {})
    logistic_appraisal["condition"] = condition
    path.write_text(yaml.safe_dump(config, sort_keys=False))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _write_dict_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _source_label_shuffled_events(
    events: list[dict[str, str]],
    seed: int,
) -> list[dict[str, str]]:
    rows = [dict(row) for row in events]
    for row in rows:
        if row.get("event_type") != "a6_artifact_update":
            continue
        tick = int(float(row["tick"]))
        shift = 1 + ((seed + tick) % (len(_A6_SOURCE_DELTA_COLUMNS) - 1))
        values = [row.get(column, "") for column in _A6_SOURCE_DELTA_COLUMNS]
        rotated = values[-shift:] + values[:-shift]
        for column, value in zip(_A6_SOURCE_DELTA_COLUMNS, rotated, strict=True):
            row[column] = value
        row["a6_artifact_update_source"] = "source_label_shuffled_within_tick"
    return rows


def _handoff_success_timing_broken_events(
    events: list[dict[str, str]],
    seed: int,
) -> list[dict[str, str]]:
    rows = [dict(row) for row in events]
    by_field: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        if row.get("event_type") == "a6_artifact_update":
            by_field.setdefault(str(row.get("a6_artifact_field", "")), []).append(row)
    for field, field_rows in by_field.items():
        success_values = [
            row.get("a6_artifact_delta_handoff_success", "") for row in field_rows
        ]
        nonzero = [value for value in success_values if _float(value) != 0.0]
        if len(nonzero) < 2:
            continue
        shift = 1 + ((seed + len(field)) % (len(field_rows) - 1))
        rotated = success_values[-shift:] + success_values[:-shift]
        for row, value in zip(field_rows, rotated, strict=True):
            row["a6_artifact_delta_handoff_success"] = value
            _refresh_event_total(row)
    return rows


def _prediction_replay_events(
    events: list[dict[str, str]],
    seed: int,
) -> list[dict[str, str]]:
    rows = [dict(row) for row in events]
    by_field: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        if row.get("event_type") == "a6_artifact_update":
            by_field.setdefault(str(row.get("a6_artifact_field", "")), []).append(row)
    for field, field_rows in by_field.items():
        for row in field_rows:
            row["a6_artifact_update_source"] = A6_BOUNDED_RESOURCE_REPLAY_CONDITION
        for column in (
            "a6_artifact_delta_prediction_expenditure",
            "a6_artifact_delta_prediction_error",
        ):
            values = [row.get(column, "") for row in field_rows]
            if len([value for value in values if _float(value) != 0.0]) < 2:
                continue
            shift = 1 + ((seed + len(field) + len(column)) % (len(field_rows) - 1))
            rotated = values[-shift:] + values[:-shift]
            for row, value in zip(field_rows, rotated, strict=True):
                row[column] = value
        for row in field_rows:
            _refresh_event_total(row)
    return rows


def _refresh_event_total(row: dict[str, str]) -> None:
    unclipped = round(sum(_float(row.get(column, "")) for column in _A6_SOURCE_DELTA_COLUMNS), 6)
    row["a6_artifact_delta_unclipped"] = str(unclipped)
    row["a6_artifact_delta_clip_residual"] = "0.0"
    row["a6_artifact_delta_total"] = str(unclipped)


def _metrics_with_transformed_artifacts(
    *,
    metrics: list[dict[str, str]],
    original_events: list[dict[str, str]],
    transformed_events: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows = [dict(row) for row in metrics]
    if not rows:
        return rows
    original_by_tick_field = _event_deltas_by_tick_field(original_events)
    transformed_by_tick_field = _event_deltas_by_tick_field(transformed_events)
    values: dict[str, float] = {}
    first_tick = int(float(rows[0]["tick"]))
    for event_field, metric_field in _A6_ARTIFACT_METRIC_FIELDS.items():
        values[metric_field] = _float(rows[0].get(metric_field, "")) - original_by_tick_field.get(
            (first_tick, event_field),
            0.0,
        )
    for row in rows:
        tick = int(float(row["tick"]))
        for event_field, metric_field in _A6_ARTIFACT_METRIC_FIELDS.items():
            values[metric_field] = _clamp01(
                values[metric_field]
                + transformed_by_tick_field.get((tick, event_field), 0.0)
            )
            row[metric_field] = str(round(values[metric_field], 6))
    return rows


def _prediction_replay_metrics(
    *,
    metrics: list[dict[str, str]],
    original_events: list[dict[str, str]],
    transformed_events: list[dict[str, str]],
    seed: int,
) -> list[dict[str, str]]:
    rows = _metrics_with_transformed_artifacts(
        metrics=metrics,
        original_events=original_events,
        transformed_events=transformed_events,
    )
    _rotate_metric_column(rows, "a6_prediction_error_mean_tick", seed + 3)
    _rotate_metric_column(rows, "a6_latent_prediction_error_mean_tick", seed + 5)
    for row in rows:
        row["a6_condition"] = A6_BOUNDED_RESOURCE_REPLAY_CONDITION
    return rows


def _rotate_metric_column(
    rows: list[dict[str, str]],
    field: str,
    salt: int,
) -> None:
    if len(rows) < 2 or field not in rows[0]:
        return
    values = [row.get(field, "") for row in rows]
    shift = 1 + (salt % (len(rows) - 1))
    rotated = values[-shift:] + values[:-shift]
    for row, value in zip(rows, rotated, strict=True):
        row[field] = value


def _event_deltas_by_tick_field(events: list[dict[str, str]]) -> dict[tuple[int, str], float]:
    deltas: dict[tuple[int, str], float] = {}
    for row in events:
        if row.get("event_type") != "a6_artifact_update":
            continue
        key = (int(float(row["tick"])), str(row.get("a6_artifact_field", "")))
        deltas[key] = deltas.get(key, 0.0) + _float(row.get("a6_artifact_delta_total", ""))
    return deltas


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _summary(
    rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    seeds: tuple[int, ...],
    *,
    title: str,
    scope_line: str,
    scientific_status: str,
    conservative_use: str,
) -> str:
    lines = [
        f"# {title}",
        "",
        f"- seeds: {', '.join(str(seed) for seed in seeds)}",
        f"- run count: {sum(int(row['run_count']) for row in rows)}",
        f"- scope: {scope_line}",
        f"- scientific status: {scientific_status}",
        "",
        "## Condition Means",
        "",
    ]
    for row in rows:
        lines.append(
            "- "
            f"{row['condition']}: "
            f"readiness={_format_number(row['final_artifact_readiness_mean'])}, "
            f"artifact_utility={_format_number(row['final_artifact_utility_mean'])}, "
            f"handoff_successes={_format_number(row['handoff_successes_total_mean'])}, "
            f"handoff_failures={_format_number(row['handoff_failures_total_mean'])}, "
            f"prediction_spent={_format_number(row['prediction_budget_spent_total_mean'])}, "
            f"completion_fraction={_format_number(row['completion_fraction_mean'])}, "
            f"queue_depth={_format_number(row['queue_depth_mean'])}"
        )
    lines.extend(["", "## Effects", ""])
    for row in effect_rows:
        lines.append(
            "- "
            f"{row['high_label']} minus {row['low_label']}: "
            f"artifact_utility_delta={_format_number(row['final_artifact_utility_mean_delta'])}, "
            f"handoff_success_delta={_format_number(row['handoff_successes_total_mean_delta'])}, "
            f"queue_depth_delta={_format_number(row['queue_depth_mean_delta'])}; "
            f"{row['interpretation']}"
        )
    lines.extend(
        [
            "",
            "## Conservative Use",
            "",
            conservative_use,
            "",
        ]
    )
    return "\n".join(lines)


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
        description="Run the bounded A6 logistic-appraisal smoke comparison."
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_A6_SEEDS),
        help="Deterministic paired smoke seeds.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A6_COMPARE_DIR),
        help="Output directory for A6 smoke comparison artifacts.",
    )
    parser.add_argument(
        "--include-a6-1-nulls",
        action="store_true",
        help="Also derive the preregistered A6.1 source-preserving null artifact directories.",
    )
    parser.add_argument(
        "--include-bounded-resource-replay",
        action="store_true",
        help=(
            "Also derive the A6 bounded prediction-resource budget-matched "
            "prediction replay control artifact directory."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a6_logistic_appraisal_comparison(
            seeds=tuple(args.seeds),
            out_dir=args.out,
            include_a6_1_nulls=args.include_a6_1_nulls,
            include_bounded_resource_replay=args.include_bounded_resource_replay,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
