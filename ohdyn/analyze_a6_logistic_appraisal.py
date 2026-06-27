"""Read A6 logistic-appraisal artifacts and emit gate-control outputs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml


DEFAULT_A6_COMPARE_DIR = Path("runs/a6_logistic_appraisal_compare")
DEFAULT_A6_ANALYSIS_OUT_DIR = Path("runs/a6_logistic_appraisal_analysis")
A6_REQUIRED_CONDITIONS = (
    "logistic",
    "linear",
    "threshold_shuffled",
    "phase_shuffled",
)
A6_ANALYSIS_CONTROL_LEVELS = (
    "load_service_action_opportunity",
    "clock_queue_residualized",
    "amplitude_matched_linear",
    "phase_shuffled",
    "threshold_shuffled",
    "paired_seed_uncertainty",
    "promotion_closure_rules",
)
A6_ANALYSIS_MANIFEST_FIELDS = (
    "control_level",
    "compare_dir",
    "condition_count",
    "seed_count",
    "status",
)
A6_ANALYSIS_ENDPOINT_FIELDS = (
    "condition",
    "seed",
    "tick_count",
    "final_latent_activation_mean",
    "final_latent_focus_mean",
    "final_latent_fatigue_mean",
    "final_latent_prediction_error_abs_mean",
    "final_artifact_novelty",
    "final_artifact_coherence",
    "final_artifact_actionability",
    "final_artifact_provenance_debt",
    "final_artifact_risk",
    "final_artifact_contradiction",
    "final_artifact_readiness",
    "final_artifact_implementation_maturity",
    "final_artifact_communication_maturity",
    "final_artifact_utility",
    "handoff_attempts_total",
    "handoff_successes_total",
    "handoff_failures_total",
    "prediction_budget_spent_total",
    "tasks_created_total",
    "tasks_completed_total",
    "tasks_worked_total",
    "messages_sent_total",
    "completion_fraction",
    "queue_depth",
    "queue_delta_tick",
    "queued_task_age_mean_final",
    "action_opportunity_total",
    "idle_total",
    "message_total",
    "create_task_total",
    "work_task_total",
    "synthesize_total",
    "review_total",
    "formalize_total",
    "maintain_total",
    "predict_total",
    "communicate_total",
    "pause_total",
)
A6_CONTROL_DELTA_FIELDS = (
    "contrast",
    "seed",
    "control_condition",
    "paired",
    "missing_required_fields",
    *(
        f"{field}_delta"
        for field in A6_ANALYSIS_ENDPOINT_FIELDS
        if field not in {"condition", "seed"}
    ),
)
A6_CONTROL_SUMMARY_FIELDS = (
    "contrast",
    "control_condition",
    "outcome_field",
    "paired_seed_count",
    "missing_required_fields",
    "residual_status",
    "mean_raw_variance_delta",
    "mean_residual_variance_delta",
    "mean_raw_lag1_autocorrelation_delta",
    "mean_residual_lag1_autocorrelation_delta",
    "mean_final_artifact_utility_delta",
    "mean_queue_depth_delta",
    "mean_action_opportunity_total_delta",
    "mean_completion_fraction_delta",
    "interpretation",
)
A6_RESIDUAL_PREFLIGHT_FIELDS = (
    "condition",
    "seed",
    "outcome_field",
    "row_count",
    "control_count",
    "degrees_of_freedom",
    "status",
    "missing_control_fields",
    "control_fields_used",
    "raw_variance",
    "residual_variance",
    "raw_lag1_autocorrelation",
    "residual_lag1_autocorrelation",
)
A6_COMPARISON_CONSISTENCY_FIELDS = (
    "condition",
    "comparison_csv_path",
    "status",
    "expected_seed_count",
    "observed_seed_count",
    "expected_run_count",
    "observed_run_count",
    "fields_checked",
    "max_abs_difference",
    "mismatched_fields",
    "missing_comparison_fields",
    "interpretation",
)
A6_EFFECTS_CONSISTENCY_FIELDS = (
    "effect_axis",
    "effects_csv_path",
    "status",
    "low_label",
    "high_label",
    "fields_checked",
    "max_abs_difference",
    "mismatched_fields",
    "missing_effect_fields",
    "missing_comparison_conditions",
    "interpretation",
)
_OUTPUT_NAMES = (
    "a6_logistic_appraisal_endpoints.csv",
    "a6_logistic_appraisal_manifest.csv",
    "a6_logistic_appraisal_control_deltas.csv",
    "a6_logistic_appraisal_control_summary.csv",
    "a6_logistic_appraisal_residual_preflight.csv",
    "a6_logistic_appraisal_comparison_consistency.csv",
    "a6_logistic_appraisal_effects_consistency.csv",
    "summary.md",
)
_A6_CONTROL_PAIRS = (
    ("logistic_vs_linear", "linear"),
    ("logistic_vs_phase_shuffled", "phase_shuffled"),
    ("logistic_vs_threshold_shuffled", "threshold_shuffled"),
)
_A6_REQUIRED_CONTROL_FIELDS = (
    "tick",
    "queue_depth",
    "queue_delta_tick",
    "tasks_created_total",
    "tasks_completed_total",
    "tasks_worked_tick",
    "messages_sent_tick",
    "a6_prediction_budget_spent_tick",
    "a6_latent_activation_mean_tick",
    "a6_latent_focus_mean_tick",
    "a6_latent_fatigue_mean_tick",
    "a6_latent_prediction_error_mean_tick",
    "a6_artifact_readiness_tick",
    "a6_handoff_attempts_tick",
    "a6_handoff_successes_tick",
    "a6_handoff_failures_tick",
)
_A6_RESIDUAL_OUTCOME_FIELDS = (
    "a6_latent_activation_mean_tick",
    "a6_latent_focus_mean_tick",
    "a6_latent_fatigue_mean_tick",
    "a6_latent_prediction_error_mean_tick",
    "a6_artifact_novelty_tick",
    "a6_artifact_coherence_tick",
    "a6_artifact_actionability_tick",
    "a6_artifact_provenance_debt_tick",
    "a6_artifact_risk_tick",
    "a6_artifact_contradiction_tick",
    "a6_artifact_readiness_tick",
    "a6_artifact_implementation_maturity_tick",
    "a6_artifact_communication_maturity_tick",
    "a6_artifact_utility_tick",
)
_A6_RESIDUAL_BASE_CONTROL_FIELDS = (
    "tick",
    "queue_depth",
    "queue_delta_tick",
    "tasks_created_total",
    "tasks_completed_total",
    "tasks_worked_tick",
    "messages_sent_tick",
    "a6_prediction_budget_spent_tick",
)
_A6_ACTIONS = (
    "idle",
    "message",
    "create_task",
    "work_task",
    "synthesize",
    "review",
    "formalize",
    "maintain",
    "predict",
    "communicate",
    "pause",
)
_A6_COMPARISON_METRICS_NAME = "a6_logistic_appraisal_comparison_metrics.csv"
_A6_EFFECTS_NAME = "a6_logistic_appraisal_effects.csv"
_A6_COMPARISON_MEAN_FIELD_MAP = {
    "final_latent_activation_mean": "final_latent_activation_mean",
    "final_latent_focus_mean": "final_latent_focus_mean",
    "final_latent_fatigue_mean": "final_latent_fatigue_mean",
    "final_latent_prediction_error_abs_mean": "final_latent_prediction_error_abs_mean",
    "final_artifact_readiness_mean": "final_artifact_readiness",
    "final_artifact_utility_mean": "final_artifact_utility",
    "handoff_attempts_total_mean": "handoff_attempts_total",
    "handoff_successes_total_mean": "handoff_successes_total",
    "handoff_failures_total_mean": "handoff_failures_total",
    "prediction_budget_spent_total_mean": "prediction_budget_spent_total",
    "tasks_created_mean": "tasks_created_total",
    "tasks_completed_mean": "tasks_completed_total",
    "completion_fraction_mean": "completion_fraction",
    "queue_depth_mean": "queue_depth",
    "queued_task_age_mean_final_mean": "queued_task_age_mean_final",
}
_A6_EFFECT_DELTA_FIELDS = (
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
)
_A6_COMPARISON_CONSISTENCY_TOLERANCE = 1e-6


def run_a6_logistic_appraisal_analysis(
    compare_dir: str | Path = DEFAULT_A6_COMPARE_DIR,
    out_dir: str | Path = DEFAULT_A6_ANALYSIS_OUT_DIR,
) -> dict[str, Any]:
    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs, missing_required_fields = _read_a6_runs(compare_path)
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    control_delta_rows = _control_delta_rows(runs, missing_required_fields)
    residual_preflight_rows = _residual_preflight_rows(compare_path)
    control_summary_rows = _control_summary_rows(
        control_delta_rows,
        residual_preflight_rows,
        missing_required_fields,
    )
    comparison_consistency_rows = _comparison_consistency_rows(compare_path, runs)
    effects_consistency_rows = _effects_consistency_rows(compare_path)
    manifest_rows = [
        {
            "control_level": control_level,
            "compare_dir": str(compare_path),
            "condition_count": len(conditions),
            "seed_count": len(seeds),
            "status": _control_level_status(
                control_level,
                control_delta_rows,
                missing_required_fields,
                residual_preflight_rows,
                control_summary_rows,
            ),
        }
        for control_level in A6_ANALYSIS_CONTROL_LEVELS
    ]

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "a6_logistic_appraisal_endpoints.csv",
        runs,
        A6_ANALYSIS_ENDPOINT_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_manifest.csv",
        manifest_rows,
        A6_ANALYSIS_MANIFEST_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_control_deltas.csv",
        control_delta_rows,
        A6_CONTROL_DELTA_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_control_summary.csv",
        control_summary_rows,
        A6_CONTROL_SUMMARY_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_residual_preflight.csv",
        residual_preflight_rows,
        A6_RESIDUAL_PREFLIGHT_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_comparison_consistency.csv",
        comparison_consistency_rows,
        A6_COMPARISON_CONSISTENCY_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_effects_consistency.csv",
        effects_consistency_rows,
        A6_EFFECTS_CONSISTENCY_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(
            compare_path,
            runs,
            manifest_rows,
            control_delta_rows,
            residual_preflight_rows,
            control_summary_rows,
            comparison_consistency_rows,
            effects_consistency_rows,
            missing_required_fields,
        )
    )
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "condition_count": len(conditions),
        "seed_count": len(seeds),
        "run_count": len(runs),
        "control_delta_count": len(control_delta_rows),
        "control_summary_count": len(control_summary_rows),
        "residual_preflight_count": len(residual_preflight_rows),
        "comparison_consistency_count": len(comparison_consistency_rows),
        "effects_consistency_count": len(effects_consistency_rows),
        "missing_required_fields": sorted(missing_required_fields),
    }


def _read_a6_runs(compare_path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    if not compare_path.exists():
        raise FileNotFoundError(f"A6 comparison/artifact directory does not exist: {compare_path}")
    run_dirs = sorted(path for path in compare_path.iterdir() if path.is_dir())
    if not run_dirs:
        raise ValueError(f"A6 comparison/artifact directory contains no run subdirectories: {compare_path}")

    rows = []
    missing_required_fields: set[str] = set()
    for run_dir in run_dirs:
        config_path = run_dir / "config.yaml"
        metrics_path = run_dir / "metrics.csv"
        manifest_path = run_dir / "manifest.yaml"
        if not config_path.exists() or not metrics_path.exists() or not manifest_path.exists():
            continue
        config = yaml.safe_load(config_path.read_text()) or {}
        logistic_appraisal = config.get("logistic_appraisal")
        if not isinstance(logistic_appraisal, dict):
            continue
        condition = str(logistic_appraisal.get("condition", ""))
        metrics = _read_csv(metrics_path)
        if not metrics:
            continue
        missing_required_fields.update(
            field for field in _A6_REQUIRED_CONTROL_FIELDS if field not in metrics[0]
        )
        seed = int((yaml.safe_load(manifest_path.read_text()) or {}).get("seed", -1))
        last = metrics[-1]
        rows.append(
            {
                "condition": condition,
                "seed": seed,
                "tick_count": len(metrics),
                "final_latent_activation_mean": _number(last, "a6_latent_activation_mean_tick"),
                "final_latent_focus_mean": _number(last, "a6_latent_focus_mean_tick"),
                "final_latent_fatigue_mean": _number(last, "a6_latent_fatigue_mean_tick"),
                "final_latent_prediction_error_abs_mean": abs(
                    _number(last, "a6_latent_prediction_error_mean_tick")
                ),
                "final_artifact_novelty": _number(last, "a6_artifact_novelty_tick"),
                "final_artifact_coherence": _number(last, "a6_artifact_coherence_tick"),
                "final_artifact_actionability": _number(last, "a6_artifact_actionability_tick"),
                "final_artifact_provenance_debt": _number(
                    last, "a6_artifact_provenance_debt_tick"
                ),
                "final_artifact_risk": _number(last, "a6_artifact_risk_tick"),
                "final_artifact_contradiction": _number(last, "a6_artifact_contradiction_tick"),
                "final_artifact_readiness": _number(last, "a6_artifact_readiness_tick"),
                "final_artifact_implementation_maturity": _number(
                    last, "a6_artifact_implementation_maturity_tick"
                ),
                "final_artifact_communication_maturity": _number(
                    last, "a6_artifact_communication_maturity_tick"
                ),
                "final_artifact_utility": _artifact_utility(last),
                "handoff_attempts_total": sum(
                    _number(row, "a6_handoff_attempts_tick") for row in metrics
                ),
                "handoff_successes_total": sum(
                    _number(row, "a6_handoff_successes_tick") for row in metrics
                ),
                "handoff_failures_total": sum(
                    _number(row, "a6_handoff_failures_tick") for row in metrics
                ),
                "prediction_budget_spent_total": sum(
                    _number(row, "a6_prediction_budget_spent_tick") for row in metrics
                ),
                "tasks_created_total": _number(last, "tasks_created_total"),
                "tasks_completed_total": _number(last, "tasks_completed_total"),
                "tasks_worked_total": sum(_number(row, "tasks_worked_tick") for row in metrics),
                "messages_sent_total": sum(_number(row, "messages_sent_tick") for row in metrics),
                "completion_fraction": _safe_ratio(
                    _number(last, "tasks_completed_total"),
                    _number(last, "tasks_created_total"),
                ),
                "queue_depth": _number(last, "queue_depth"),
                "queue_delta_tick": _number(last, "queue_delta_tick"),
                "queued_task_age_mean_final": _number(last, "queued_task_age_mean_tick"),
                "action_opportunity_total": _action_opportunity_total(metrics),
                **{
                    f"{action}_total": _action_total(metrics, action)
                    for action in _A6_ACTIONS
                },
            }
        )
    if not rows:
        raise ValueError(f"No A6 logistic_appraisal run artifacts found in {compare_path}")
    return rows, missing_required_fields


def _control_delta_rows(
    runs: list[dict[str, Any]],
    missing_required_fields: set[str],
) -> list[dict[str, Any]]:
    by_condition_seed = {
        (str(row["condition"]), int(row["seed"])): row
        for row in runs
    }
    seeds = sorted({int(row["seed"]) for row in runs})
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        logistic = by_condition_seed.get(("logistic", seed))
        for contrast, control_condition in _A6_CONTROL_PAIRS:
            control = by_condition_seed.get((control_condition, seed))
            row: dict[str, Any] = {
                "contrast": contrast,
                "seed": seed,
                "control_condition": control_condition,
                "paired": str(logistic is not None and control is not None).lower(),
                "missing_required_fields": "|".join(sorted(missing_required_fields)),
            }
            for field in A6_ANALYSIS_ENDPOINT_FIELDS:
                if field in {"condition", "seed"}:
                    continue
                row[f"{field}_delta"] = (
                    round(float(logistic[field]) - float(control[field]), 6)
                    if logistic is not None and control is not None
                    else ""
                )
            rows.append(row)
    return rows


def _control_level_status(
    control_level: str,
    control_delta_rows: list[dict[str, Any]],
    missing_required_fields: set[str],
    residual_preflight_rows: list[dict[str, Any]],
    control_summary_rows: list[dict[str, Any]],
) -> str:
    complete_pairs = [row for row in control_delta_rows if row["paired"] == "true"]
    if missing_required_fields:
        return "control_delta_preflight_missing_fields"
    if not complete_pairs:
        return "control_delta_preflight_incomplete_pairs"
    if control_level in {
        "load_service_action_opportunity",
        "amplitude_matched_linear",
        "phase_shuffled",
        "threshold_shuffled",
        "paired_seed_uncertainty",
    }:
        return "paired_delta_preflight_complete"
    if control_level == "clock_queue_residualized":
        statuses = {str(row["status"]) for row in residual_preflight_rows}
        if not residual_preflight_rows:
            return "residualization_not_yet_computed"
        if any(status.startswith("missing_controls") for status in statuses):
            return "residual_preflight_missing_controls"
        if any(status.startswith("underdetermined") for status in statuses):
            return "residual_preflight_underdetermined_smoke_scale"
        return "residual_preflight_computed"
    if control_level == "promotion_closure_rules" and control_summary_rows:
        return "promotion_not_evaluated_control_summary_written"
    return "promotion_not_evaluated"


def _comparison_consistency_rows(
    compare_path: Path,
    runs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    comparison_path = compare_path / _A6_COMPARISON_METRICS_NAME
    conditions = sorted({str(row["condition"]) for row in runs})
    derived_by_condition = {
        condition: [row for row in runs if str(row["condition"]) == condition]
        for condition in conditions
    }
    if not comparison_path.exists():
        return [
            {
                "condition": condition,
                "comparison_csv_path": str(comparison_path),
                "status": "missing_comparison_csv",
                "expected_seed_count": "",
                "observed_seed_count": len({int(row["seed"]) for row in condition_runs}),
                "expected_run_count": "",
                "observed_run_count": len(condition_runs),
                "fields_checked": "",
                "max_abs_difference": "",
                "mismatched_fields": "",
                "missing_comparison_fields": "",
                "interpretation": "aggregate comparison CSV absent; consistency preflight not applicable",
            }
            for condition, condition_runs in derived_by_condition.items()
        ]

    comparison_rows = _read_csv(comparison_path)
    comparison_by_condition = {str(row.get("condition", "")): row for row in comparison_rows}
    rows: list[dict[str, Any]] = []
    for condition, condition_runs in derived_by_condition.items():
        comparison_row = comparison_by_condition.get(condition)
        observed_seed_count = len({int(row["seed"]) for row in condition_runs})
        observed_run_count = len(condition_runs)
        if comparison_row is None:
            rows.append(
                {
                    "condition": condition,
                    "comparison_csv_path": str(comparison_path),
                    "status": "missing_condition",
                    "expected_seed_count": "",
                    "observed_seed_count": observed_seed_count,
                    "expected_run_count": "",
                    "observed_run_count": observed_run_count,
                    "fields_checked": "",
                    "max_abs_difference": "",
                    "mismatched_fields": "",
                    "missing_comparison_fields": "",
                    "interpretation": "condition missing from aggregate comparison CSV; consistency blocked",
                }
            )
            continue

        missing_fields = [
            field for field in _A6_COMPARISON_MEAN_FIELD_MAP if field not in comparison_row
        ]
        mismatched_fields: list[str] = []
        differences: list[float] = []
        for comparison_field, endpoint_field in _A6_COMPARISON_MEAN_FIELD_MAP.items():
            if comparison_field not in comparison_row:
                continue
            expected_value = _number(comparison_row, comparison_field)
            observed_value = _mean_available(
                [row.get(endpoint_field, "") for row in condition_runs]
            )
            if observed_value == "":
                continue
            difference = abs(expected_value - float(observed_value))
            differences.append(difference)
            if difference > _A6_COMPARISON_CONSISTENCY_TOLERANCE:
                mismatched_fields.append(comparison_field)
        expected_seed_count = comparison_row.get("seed_count", "")
        expected_run_count = comparison_row.get("run_count", "")
        count_mismatches = []
        if expected_seed_count not in {"", None} and int(float(expected_seed_count)) != observed_seed_count:
            count_mismatches.append("seed_count")
        if expected_run_count not in {"", None} and int(float(expected_run_count)) != observed_run_count:
            count_mismatches.append("run_count")
        mismatched_fields.extend(count_mismatches)
        status = (
            "missing_comparison_fields"
            if missing_fields
            else "mismatch"
            if mismatched_fields
            else "consistent"
        )
        rows.append(
            {
                "condition": condition,
                "comparison_csv_path": str(comparison_path),
                "status": status,
                "expected_seed_count": expected_seed_count,
                "observed_seed_count": observed_seed_count,
                "expected_run_count": expected_run_count,
                "observed_run_count": observed_run_count,
                "fields_checked": "|".join(
                    field
                    for field in _A6_COMPARISON_MEAN_FIELD_MAP
                    if field not in missing_fields
                ),
                "max_abs_difference": _rounded_mean([max(differences)]) if differences else "",
                "mismatched_fields": "|".join(mismatched_fields),
                "missing_comparison_fields": "|".join(missing_fields),
                "interpretation": _comparison_consistency_interpretation(status),
            }
        )
    return rows


def _comparison_consistency_interpretation(status: str) -> str:
    if status == "consistent":
        return "aggregate comparison CSV agrees with run-directory-derived endpoint means"
    if status == "missing_comparison_csv":
        return "aggregate comparison CSV absent; consistency preflight not applicable"
    if status == "missing_comparison_fields":
        return "aggregate comparison CSV is missing fields required for consistency check"
    if status == "missing_condition":
        return "condition missing from aggregate comparison CSV; consistency blocked"
    return "aggregate comparison CSV differs from run-directory-derived endpoint means"


def _effects_consistency_rows(compare_path: Path) -> list[dict[str, Any]]:
    effects_path = compare_path / _A6_EFFECTS_NAME
    comparison_path = compare_path / _A6_COMPARISON_METRICS_NAME
    expected_pairs = (
        ("logistic_vs_linear", "linear", "logistic"),
        ("logistic_vs_phase_shuffled", "phase_shuffled", "logistic"),
        ("logistic_vs_threshold_shuffled", "threshold_shuffled", "logistic"),
    )
    if not effects_path.exists():
        return [
            _missing_effects_row(effect_axis, effects_path, low_label, high_label)
            for effect_axis, low_label, high_label in expected_pairs
        ]
    if not comparison_path.exists():
        return [
            {
                "effect_axis": effect_axis,
                "effects_csv_path": str(effects_path),
                "status": "missing_comparison_csv",
                "low_label": low_label,
                "high_label": high_label,
                "fields_checked": "",
                "max_abs_difference": "",
                "mismatched_fields": "",
                "missing_effect_fields": "",
                "missing_comparison_conditions": "",
                "interpretation": _effects_consistency_interpretation(
                    "missing_comparison_csv"
                ),
            }
            for effect_axis, low_label, high_label in expected_pairs
        ]

    effect_rows = _read_csv(effects_path)
    comparison_rows = _read_csv(comparison_path)
    effects_by_axis = {str(row.get("effect_axis", "")): row for row in effect_rows}
    comparison_by_condition = {
        str(row.get("condition", "")): row for row in comparison_rows
    }
    rows: list[dict[str, Any]] = []
    for effect_axis, low_label, high_label in expected_pairs:
        effect_row = effects_by_axis.get(effect_axis)
        if effect_row is None:
            rows.append(_missing_effect_axis_row(effect_axis, effects_path, low_label, high_label))
            continue

        missing_effect_fields = [
            field for field in _A6_EFFECT_DELTA_FIELDS if field not in effect_row
        ]
        missing_comparison_conditions = [
            label
            for label in (low_label, high_label)
            if label not in comparison_by_condition
        ]
        mismatched_fields: list[str] = []
        differences: list[float] = []
        if not missing_comparison_conditions:
            low = comparison_by_condition[low_label]
            high = comparison_by_condition[high_label]
            for field in _A6_EFFECT_DELTA_FIELDS:
                if field not in effect_row:
                    continue
                base_field = field.removesuffix("_delta")
                if base_field not in low or base_field not in high:
                    missing_effect_fields.append(field)
                    continue
                expected_value = _number(effect_row, field)
                observed_value = _number(high, base_field) - _number(low, base_field)
                difference = abs(expected_value - observed_value)
                differences.append(difference)
                if difference > _A6_COMPARISON_CONSISTENCY_TOLERANCE:
                    mismatched_fields.append(field)

        status = (
            "missing_comparison_conditions"
            if missing_comparison_conditions
            else "missing_effect_fields"
            if missing_effect_fields
            else "mismatch"
            if mismatched_fields
            else "consistent"
        )
        rows.append(
            {
                "effect_axis": effect_axis,
                "effects_csv_path": str(effects_path),
                "status": status,
                "low_label": effect_row.get("low_label", ""),
                "high_label": effect_row.get("high_label", ""),
                "fields_checked": "|".join(
                    field
                    for field in _A6_EFFECT_DELTA_FIELDS
                    if field not in missing_effect_fields
                ),
                "max_abs_difference": _rounded_mean([max(differences)])
                if differences
                else "",
                "mismatched_fields": "|".join(mismatched_fields),
                "missing_effect_fields": "|".join(sorted(set(missing_effect_fields))),
                "missing_comparison_conditions": "|".join(
                    missing_comparison_conditions
                ),
                "interpretation": _effects_consistency_interpretation(status),
            }
        )
    return rows


def _missing_effects_row(
    effect_axis: str,
    effects_path: Path,
    low_label: str,
    high_label: str,
) -> dict[str, Any]:
    return {
        "effect_axis": effect_axis,
        "effects_csv_path": str(effects_path),
        "status": "missing_effects_csv",
        "low_label": low_label,
        "high_label": high_label,
        "fields_checked": "",
        "max_abs_difference": "",
        "mismatched_fields": "",
        "missing_effect_fields": "",
        "missing_comparison_conditions": "",
        "interpretation": _effects_consistency_interpretation("missing_effects_csv"),
    }


def _missing_effect_axis_row(
    effect_axis: str,
    effects_path: Path,
    low_label: str,
    high_label: str,
) -> dict[str, Any]:
    return {
        "effect_axis": effect_axis,
        "effects_csv_path": str(effects_path),
        "status": "missing_effect_axis",
        "low_label": low_label,
        "high_label": high_label,
        "fields_checked": "",
        "max_abs_difference": "",
        "mismatched_fields": "",
        "missing_effect_fields": "",
        "missing_comparison_conditions": "",
        "interpretation": _effects_consistency_interpretation("missing_effect_axis"),
    }


def _effects_consistency_interpretation(status: str) -> str:
    if status == "consistent":
        return "effects CSV deltas agree with aggregate comparison CSV condition means"
    if status == "missing_effects_csv":
        return "effects CSV absent; consistency preflight not applicable"
    if status == "missing_comparison_csv":
        return "aggregate comparison CSV absent; effects consistency blocked"
    if status == "missing_effect_axis":
        return "expected effect axis missing from effects CSV; consistency blocked"
    if status == "missing_effect_fields":
        return "effects CSV is missing delta fields required for consistency check"
    if status == "missing_comparison_conditions":
        return "aggregate comparison CSV lacks one or more conditions for this effect"
    return "effects CSV deltas differ from aggregate comparison CSV condition means"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows(rows)


def _number(row: dict[str, str], field: str) -> float:
    value = row.get(field, "")
    return float(value) if value not in {"", None} else 0.0


def _safe_ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _artifact_utility(row: dict[str, str]) -> float:
    positive = (
        _number(row, "a6_artifact_readiness_tick")
        + _number(row, "a6_artifact_coherence_tick")
        + _number(row, "a6_artifact_actionability_tick")
        + _number(row, "a6_artifact_implementation_maturity_tick")
        + _number(row, "a6_artifact_communication_maturity_tick")
    )
    negative = (
        _number(row, "a6_artifact_provenance_debt_tick")
        + _number(row, "a6_artifact_risk_tick")
        + _number(row, "a6_artifact_contradiction_tick")
    )
    return round((positive - negative) / 5.0, 6)


def _action_opportunity_total(metrics: list[dict[str, str]]) -> float:
    return sum(
        _number(row, field)
        for row in metrics
        for field in row
        if field.startswith("role_") and field.endswith("_tick")
    )


def _action_total(metrics: list[dict[str, str]], action: str) -> float:
    suffix = f"_{action}_tick"
    return sum(
        _number(row, field)
        for row in metrics
        for field in row
        if field.startswith("role_") and field.endswith(suffix)
    )


def _residual_preflight_rows(compare_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        config_path = run_dir / "config.yaml"
        metrics_path = run_dir / "metrics.csv"
        manifest_path = run_dir / "manifest.yaml"
        if not config_path.exists() or not metrics_path.exists() or not manifest_path.exists():
            continue
        config = yaml.safe_load(config_path.read_text()) or {}
        logistic_appraisal = config.get("logistic_appraisal")
        if not isinstance(logistic_appraisal, dict):
            continue
        metrics = _read_csv(metrics_path)
        if not metrics:
            continue
        condition = str(logistic_appraisal.get("condition", ""))
        seed = int((yaml.safe_load(manifest_path.read_text()) or {}).get("seed", -1))
        enriched_metrics = [_with_a6_derived_fields(row) for row in metrics]
        available_fields = set(enriched_metrics[0])
        action_control_fields = tuple(f"action_{action}_tick" for action in _A6_ACTIONS)
        control_fields = (*_A6_RESIDUAL_BASE_CONTROL_FIELDS, *action_control_fields)
        missing_control_fields = tuple(
            field for field in control_fields if field not in available_fields
        )
        usable_control_fields = tuple(
            field for field in control_fields if field in available_fields
        )
        for outcome_field in _A6_RESIDUAL_OUTCOME_FIELDS:
            if outcome_field not in available_fields:
                rows.append(
                    _empty_residual_row(
                        condition,
                        seed,
                        outcome_field,
                        len(enriched_metrics),
                        usable_control_fields,
                        (*missing_control_fields, outcome_field),
                    )
                )
                continue
            values = [_number(row, outcome_field) for row in enriched_metrics]
            controls = [
                [_number(row, field) for field in usable_control_fields]
                for row in enriched_metrics
            ]
            residuals = _ridge_residuals(values, controls)
            row_count = len(values)
            control_count = len(usable_control_fields)
            degrees_of_freedom = row_count - control_count - 1
            status = (
                "missing_controls_preflight"
                if missing_control_fields
                else "underdetermined_smoke_scale"
                if degrees_of_freedom <= 0
                else "computed"
            )
            rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "outcome_field": outcome_field,
                    "row_count": row_count,
                    "control_count": control_count,
                    "degrees_of_freedom": degrees_of_freedom,
                    "status": status,
                    "missing_control_fields": "|".join(missing_control_fields),
                    "control_fields_used": "|".join(usable_control_fields),
                    "raw_variance": round(_variance(values), 6),
                    "residual_variance": round(_variance(residuals), 6),
                    "raw_lag1_autocorrelation": round(_lag1_autocorrelation(values), 6),
                    "residual_lag1_autocorrelation": round(
                        _lag1_autocorrelation(residuals), 6
                    ),
                }
            )
    return rows


def _control_summary_rows(
    control_delta_rows: list[dict[str, Any]],
    residual_preflight_rows: list[dict[str, Any]],
    missing_required_fields: set[str],
) -> list[dict[str, Any]]:
    residual_by_condition_seed_outcome = {
        (
            str(row["condition"]),
            int(row["seed"]),
            str(row["outcome_field"]),
        ): row
        for row in residual_preflight_rows
    }
    outcomes = sorted({str(row["outcome_field"]) for row in residual_preflight_rows})
    rows: list[dict[str, Any]] = []
    for contrast, control_condition in _A6_CONTROL_PAIRS:
        endpoint_rows = [
            row
            for row in control_delta_rows
            if row["contrast"] == contrast and row["paired"] == "true"
        ]
        paired_seeds = sorted(int(row["seed"]) for row in endpoint_rows)
        endpoint_means = {
            field: _mean_available([row.get(field, "") for row in endpoint_rows])
            for field in (
                "final_artifact_utility_delta",
                "queue_depth_delta",
                "action_opportunity_total_delta",
                "completion_fraction_delta",
            )
        }
        for outcome in outcomes:
            raw_variance_deltas: list[float] = []
            residual_variance_deltas: list[float] = []
            raw_autocorrelation_deltas: list[float] = []
            residual_autocorrelation_deltas: list[float] = []
            statuses: set[str] = set()
            for seed in paired_seeds:
                logistic = residual_by_condition_seed_outcome.get(("logistic", seed, outcome))
                control = residual_by_condition_seed_outcome.get(
                    (control_condition, seed, outcome)
                )
                if logistic is None or control is None:
                    statuses.add("missing_residual_pair")
                    continue
                statuses.update({str(logistic["status"]), str(control["status"])})
                _append_delta(
                    raw_variance_deltas,
                    logistic.get("raw_variance", ""),
                    control.get("raw_variance", ""),
                )
                _append_delta(
                    residual_variance_deltas,
                    logistic.get("residual_variance", ""),
                    control.get("residual_variance", ""),
                )
                _append_delta(
                    raw_autocorrelation_deltas,
                    logistic.get("raw_lag1_autocorrelation", ""),
                    control.get("raw_lag1_autocorrelation", ""),
                )
                _append_delta(
                    residual_autocorrelation_deltas,
                    logistic.get("residual_lag1_autocorrelation", ""),
                    control.get("residual_lag1_autocorrelation", ""),
                )
            residual_status = _summary_residual_status(statuses, missing_required_fields)
            rows.append(
                {
                    "contrast": contrast,
                    "control_condition": control_condition,
                    "outcome_field": outcome,
                    "paired_seed_count": len(paired_seeds),
                    "missing_required_fields": "|".join(sorted(missing_required_fields)),
                    "residual_status": residual_status,
                    "mean_raw_variance_delta": _rounded_mean(raw_variance_deltas),
                    "mean_residual_variance_delta": _rounded_mean(residual_variance_deltas),
                    "mean_raw_lag1_autocorrelation_delta": _rounded_mean(
                        raw_autocorrelation_deltas
                    ),
                    "mean_residual_lag1_autocorrelation_delta": _rounded_mean(
                        residual_autocorrelation_deltas
                    ),
                    "mean_final_artifact_utility_delta": endpoint_means[
                        "final_artifact_utility_delta"
                    ],
                    "mean_queue_depth_delta": endpoint_means["queue_depth_delta"],
                    "mean_action_opportunity_total_delta": endpoint_means[
                        "action_opportunity_total_delta"
                    ],
                    "mean_completion_fraction_delta": endpoint_means[
                        "completion_fraction_delta"
                    ],
                    "interpretation": _control_summary_interpretation(residual_status),
                }
            )
    return rows


def _append_delta(target: list[float], high: Any, low: Any) -> None:
    if high in {"", None} or low in {"", None}:
        return
    target.append(float(high) - float(low))


def _mean_available(values: list[Any]) -> str:
    numeric = [float(value) for value in values if value not in {"", None}]
    return _rounded_mean(numeric)


def _rounded_mean(values: list[float]) -> str:
    if not values:
        return ""
    return str(round(sum(values) / len(values), 6))


def _summary_residual_status(statuses: set[str], missing_required_fields: set[str]) -> str:
    if missing_required_fields:
        return "missing_required_fields"
    if not statuses:
        return "missing_residual_pair"
    if any(status.startswith("missing") for status in statuses):
        return "missing_residual_pair"
    if any(status.startswith("underdetermined") for status in statuses):
        return "underdetermined_smoke_scale"
    if statuses == {"computed"}:
        return "computed"
    return "|".join(sorted(statuses))


def _control_summary_interpretation(residual_status: str) -> str:
    if residual_status == "computed":
        return "read-only residual contrast computed; still requires preregistered promotion gate"
    if residual_status == "underdetermined_smoke_scale":
        return "smoke-scale residual contrast only; not recurrence or promotion evidence"
    if residual_status == "missing_required_fields":
        return "required accounting fields missing; control interpretation blocked"
    return "residual contrast incomplete; do not interpret as mechanism evidence"


def _with_a6_derived_fields(row: dict[str, str]) -> dict[str, str]:
    enriched = dict(row)
    enriched["a6_artifact_utility_tick"] = str(_artifact_utility(row))
    for action in _A6_ACTIONS:
        enriched[f"action_{action}_tick"] = str(_action_tick(row, action))
    return enriched


def _action_tick(row: dict[str, str], action: str) -> float:
    suffix = f"_{action}_tick"
    return sum(
        _number(row, field)
        for field in row
        if field.startswith("role_") and field.endswith(suffix)
    )


def _empty_residual_row(
    condition: str,
    seed: int,
    outcome_field: str,
    row_count: int,
    control_fields: tuple[str, ...],
    missing_fields: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "condition": condition,
        "seed": seed,
        "outcome_field": outcome_field,
        "row_count": row_count,
        "control_count": len(control_fields),
        "degrees_of_freedom": row_count - len(control_fields) - 1,
        "status": "missing_controls_or_outcome_preflight",
        "missing_control_fields": "|".join(missing_fields),
        "control_fields_used": "|".join(control_fields),
        "raw_variance": "",
        "residual_variance": "",
        "raw_lag1_autocorrelation": "",
        "residual_lag1_autocorrelation": "",
    }


def _ridge_residuals(values: list[float], controls: list[list[float]]) -> list[float]:
    if not values:
        return []
    design = [[1.0, *row] for row in controls]
    if not design or not design[0]:
        mean_value = sum(values) / len(values)
        return [value - mean_value for value in values]
    coefficient_count = len(design[0])
    xtx = [
        [
            sum(design[row][left] * design[row][right] for row in range(len(design)))
            for right in range(coefficient_count)
        ]
        for left in range(coefficient_count)
    ]
    xty = [
        sum(design[row][column] * values[row] for row in range(len(design)))
        for column in range(coefficient_count)
    ]
    for index in range(1, coefficient_count):
        xtx[index][index] += 1e-9
    coefficients = _solve_linear_system(xtx, xty)
    return [
        value - sum(coefficients[column] * design[row_index][column] for column in range(coefficient_count))
        for row_index, value in enumerate(values)
    ]


def _solve_linear_system(matrix: list[list[float]], values: list[float]) -> list[float]:
    size = len(values)
    augmented = [list(matrix[row]) + [values[row]] for row in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            augmented[column][column] += 1e-9
            pivot = column
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        if abs(divisor) < 1e-12:
            continue
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    augmented[row][col] - factor * augmented[column][col]
                    for col in range(size + 1)
                ]
    return [augmented[row][-1] for row in range(size)]


def _variance(values: list[float]) -> float:
    if not values:
        return 0.0
    mean_value = sum(values) / len(values)
    return sum((value - mean_value) ** 2 for value in values) / len(values)


def _lag1_autocorrelation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean_value = sum(values) / len(values)
    numerator = sum(
        (values[index] - mean_value) * (values[index - 1] - mean_value)
        for index in range(1, len(values))
    )
    denominator = sum((value - mean_value) ** 2 for value in values)
    return numerator / denominator if denominator else 0.0


def _summary(
    compare_path: Path,
    runs: list[dict[str, Any]],
    manifest_rows: list[dict[str, Any]],
    control_delta_rows: list[dict[str, Any]],
    residual_preflight_rows: list[dict[str, Any]],
    control_summary_rows: list[dict[str, Any]],
    comparison_consistency_rows: list[dict[str, Any]],
    effects_consistency_rows: list[dict[str, Any]],
    missing_required_fields: set[str],
) -> str:
    conditions = sorted({str(row["condition"]) for row in runs})
    seeds = sorted({int(row["seed"]) for row in runs})
    lines = [
        "# A6 Logistic-Appraisal Analysis Gate",
        "",
        f"- compare dir: {compare_path}",
        f"- run artifacts read: {len(runs)}",
        f"- conditions observed: {', '.join(conditions)}",
        f"- seeds observed: {', '.join(str(seed) for seed in seeds)}",
        "- reran simulations: no",
        f"- paired control delta rows: {len(control_delta_rows)}",
        f"- residual preflight rows: {len(residual_preflight_rows)}",
        f"- control summary rows: {len(control_summary_rows)}",
        f"- comparison consistency rows: {len(comparison_consistency_rows)}",
        f"- effects consistency rows: {len(effects_consistency_rows)}",
        "- status: read-only control/residual preflight; not promotion evidence",
        "- missing required fields: "
        + ("none" if not missing_required_fields else ", ".join(sorted(missing_required_fields))),
        "",
        "## Control Levels",
        "",
    ]
    for row in manifest_rows:
        lines.append(f"- {row['control_level']}: {row['status']}")
    lines.extend(
        [
            "",
            "## Gate Reminder",
            "",
            "- Do not promote A6 from smoke artifacts alone.",
            "- Paired deltas are logistic minus the named control within the same seed.",
            "- Residual preflight uses existing per-tick smoke metrics only; underdetermined smoke-scale rows are not recurrence evidence.",
            "- Comparison consistency preflight checks aggregate CSV arithmetic against existing run artifacts only.",
            "- Effects consistency preflight checks aggregate effect deltas against comparison CSV condition means only.",
            "- Residual latent/artifact recurrence must beat linear, phase-shuffled, and threshold-shuffled controls.",
            "- Load, service, action opportunity, work budget, clock trend, and queue variables remain accounting controls.",
            "",
        ]
    )
    return "\n".join(lines)


def _ensure_output_paths_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        output_name
        for output_name in _OUTPUT_NAMES
        if (output_path / output_name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains A6 analysis artifacts: {names}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze existing A6 logistic-appraisal artifacts without rerunning simulations."
    )
    parser.add_argument(
        "--compare-dir",
        default=str(DEFAULT_A6_COMPARE_DIR),
        help="Directory containing existing A6 run artifact subdirectories.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A6_ANALYSIS_OUT_DIR),
        help="Output directory for derived A6 analysis skeleton artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_a6_logistic_appraisal_analysis(args.compare_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
