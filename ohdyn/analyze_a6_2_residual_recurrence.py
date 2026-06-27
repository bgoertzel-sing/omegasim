"""Read-only A6.2 source-accounted residual recurrence gate."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import yaml


DEFAULT_A6_2_COMPARE_DIR = Path("runs/a6_1_pilot_null_compare")
DEFAULT_A6_2_OUT_DIR = Path("runs/a6_2_residual_recurrence_analysis")

A6_2_REQUIRED_CONDITIONS = (
    "logistic",
    "linear",
    "phase_shuffled",
    "threshold_shuffled",
    "source_label_shuffled_within_tick",
    "handoff_success_timing_broken_matched_counts",
)
A6_2_TARGET_FIELDS = (
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
)
A6_2_CONTROL_FIELDS = (
    "tick",
    "queue_depth",
    "tasks_created_total",
    "tasks_completed_total",
    "a6_service_capacity_tick",
    "a6_action_opportunity_tick",
    "a6_work_actions_tick",
    "a6_prediction_actions_tick",
    "a6_prediction_budget_spent_tick",
    "a6_handoff_attempts_tick",
    "a6_handoff_successes_tick",
    "a6_handoff_failures_tick",
)
A6_2_EVENT_SOURCE_FIELDS = (
    "tick",
    "a6_artifact_update_source",
    "a6_artifact_field",
    "a6_artifact_delta_total",
    "a6_artifact_delta_ambient",
    "a6_artifact_delta_handoff_attempt",
    "a6_artifact_delta_handoff_success",
    "a6_artifact_delta_handoff_failure",
    "a6_artifact_delta_prediction_expenditure",
    "a6_artifact_delta_prediction_error",
    "a6_artifact_delta_queue_work_accounting",
    "a6_artifact_delta_noise",
    "a6_artifact_delta_clip_residual",
)
A6_2_SOURCE_SHARE_FIELDS = (
    "ambient_share",
    "handoff_attempt_share",
    "handoff_success_share",
    "handoff_failure_share",
    "prediction_expenditure_share",
    "prediction_error_share",
    "queue_work_accounting_share",
    "noise_share",
    "clip_residual_share",
)
A6_2_RECURRENCE_FIELDS = (
    "condition",
    "seed",
    "target_field",
    "row_count",
    "residualization_status",
    "missing_required_fields",
    "control_fields_used",
    "embedding_delay",
    "embedding_dimension",
    "recurrence_radius",
    "residual_variance",
    "lag1_autocorrelation",
    "delay_embedded_recurrence_rate",
    "return_interval_cv",
    "linear_ar_forecast_mae",
    "nonlinear_forecast_mae",
    "backlog_adjusted_productivity",
    "dominant_source_share",
    "dominant_source",
    "status",
    "interpretation",
)
A6_2_DELTA_FIELDS = (
    "contrast",
    "seed",
    "control_condition",
    "target_field",
    "paired",
    "status",
    "logistic_status",
    "control_status",
    "residual_variance_delta",
    "lag1_autocorrelation_delta",
    "delay_embedded_recurrence_rate_delta",
    "return_interval_cv_delta",
    "linear_ar_forecast_mae_delta",
    "nonlinear_forecast_mae_delta",
    "backlog_adjusted_productivity_delta",
    "gate_status",
    "interpretation",
)
A6_2_COMPLETENESS_FIELDS = (
    "condition",
    "seed",
    "metrics_path",
    "events_path",
    "row_count",
    "required_field_status",
    "missing_required_fields",
    "interpretation",
)
A6_2_MANIFEST_FIELDS = (
    "compare_dir",
    "condition_count",
    "seed_count",
    "run_count",
    "recurrence_rows",
    "delta_rows",
    "status",
)
_A6_2_OUTPUT_NAMES = (
    "a6_2_paired_seed_completeness.csv",
    "a6_2_residual_recurrence_metrics.csv",
    "a6_2_residual_recurrence_deltas.csv",
    "a6_2_manifest.csv",
    "summary.md",
)
_A6_2_CONTROL_CONDITIONS = (
    "linear",
    "phase_shuffled",
    "threshold_shuffled",
    "source_label_shuffled_within_tick",
    "handoff_success_timing_broken_matched_counts",
)
_MIN_RECURRENCE_ROWS = 24
_EMBEDDING_DELAY = 1
_EMBEDDING_DIMENSION = 2


def run_a6_2_residual_recurrence_analysis(
    compare_dir: str | Path = DEFAULT_A6_2_COMPARE_DIR,
    out_dir: str | Path = DEFAULT_A6_2_OUT_DIR,
) -> dict[str, Any]:
    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs = _read_runs(compare_path)
    completeness_rows = [_completeness_row(run) for run in runs]
    recurrence_rows = [
        _recurrence_row(run, target_field)
        for run in runs
        for target_field in A6_2_TARGET_FIELDS
    ]
    delta_rows = _delta_rows(recurrence_rows)
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    manifest_rows = [
        {
            "compare_dir": str(compare_path),
            "condition_count": len(conditions),
            "seed_count": len(seeds),
            "run_count": len(runs),
            "recurrence_rows": len(recurrence_rows),
            "delta_rows": len(delta_rows),
            "status": _overall_status(completeness_rows, recurrence_rows, delta_rows),
        }
    ]

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(output_path / "a6_2_paired_seed_completeness.csv", completeness_rows, A6_2_COMPLETENESS_FIELDS)
    _write_csv(output_path / "a6_2_residual_recurrence_metrics.csv", recurrence_rows, A6_2_RECURRENCE_FIELDS)
    _write_csv(output_path / "a6_2_residual_recurrence_deltas.csv", delta_rows, A6_2_DELTA_FIELDS)
    _write_csv(output_path / "a6_2_manifest.csv", manifest_rows, A6_2_MANIFEST_FIELDS)
    (output_path / "summary.md").write_text(
        _summary(compare_path, completeness_rows, recurrence_rows, delta_rows, manifest_rows[0])
    )
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "condition_count": len(conditions),
        "seed_count": len(seeds),
        "run_count": len(runs),
        "recurrence_count": len(recurrence_rows),
        "delta_count": len(delta_rows),
        "status": manifest_rows[0]["status"],
        "missing_required_fields": sorted(
            {
                field
                for row in completeness_rows
                for field in str(row["missing_required_fields"]).split("|")
                if field
            }
        ),
    }


def _read_runs(compare_path: Path) -> list[dict[str, Any]]:
    if not compare_path.exists():
        raise FileNotFoundError(f"A6.2 comparison directory does not exist: {compare_path}")
    runs: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        config_path = run_dir / "config.yaml"
        manifest_path = run_dir / "manifest.yaml"
        metrics_path = run_dir / "metrics.csv"
        events_path = run_dir / "events.csv"
        if not config_path.exists() or not manifest_path.exists() or not metrics_path.exists():
            continue
        config = yaml.safe_load(config_path.read_text()) or {}
        logistic_appraisal = config.get("logistic_appraisal")
        if not isinstance(logistic_appraisal, dict):
            continue
        metrics_rows = _read_csv(metrics_path)
        if not metrics_rows:
            continue
        manifest = yaml.safe_load(manifest_path.read_text()) or {}
        condition = str(logistic_appraisal.get("condition", ""))
        if condition not in A6_2_REQUIRED_CONDITIONS:
            continue
        runs.append(
            {
                "condition": condition,
                "seed": int(manifest.get("seed", -1)),
                "metrics_path": metrics_path,
                "events_path": events_path,
                "metrics": metrics_rows,
                "events": _read_csv(events_path) if events_path.exists() else [],
            }
        )
    if not runs:
        raise ValueError(f"No A6.2-compatible run artifacts found in {compare_path}")
    return runs


def _completeness_row(run: dict[str, Any]) -> dict[str, Any]:
    metrics = run["metrics"]
    events = run["events"]
    metric_fields = set(metrics[0])
    event_fields = set(events[0]) if events else set()
    missing = sorted(
        (set(A6_2_TARGET_FIELDS) | set(A6_2_CONTROL_FIELDS) | {"tasks_worked_tick"})
        - metric_fields
    )
    missing.extend(field for field in A6_2_EVENT_SOURCE_FIELDS if field not in event_fields)
    missing = sorted(set(missing))
    status = "complete" if not missing else "missing_required_fields"
    return {
        "condition": run["condition"],
        "seed": run["seed"],
        "metrics_path": str(run["metrics_path"]),
        "events_path": str(run["events_path"]),
        "row_count": len(metrics),
        "required_field_status": status,
        "missing_required_fields": "|".join(missing),
        "interpretation": (
            "all A6.2 metric/control/source fields are present"
            if status == "complete"
            else "A6.2 recurrence interpretation blocked by missing required fields"
        ),
    }


def _recurrence_row(run: dict[str, Any], target_field: str) -> dict[str, Any]:
    metrics = run["metrics"]
    missing = _missing_run_fields(run, target_field)
    source_shares = _source_shares(run, target_field)
    base = {
        "condition": run["condition"],
        "seed": run["seed"],
        "target_field": target_field,
        "row_count": len(metrics),
        "missing_required_fields": "|".join(missing),
        "control_fields_used": "|".join(A6_2_CONTROL_FIELDS + A6_2_SOURCE_SHARE_FIELDS),
        "embedding_delay": _EMBEDDING_DELAY,
        "embedding_dimension": _EMBEDDING_DIMENSION,
        "recurrence_radius": "",
        "residual_variance": "",
        "lag1_autocorrelation": "",
        "delay_embedded_recurrence_rate": "",
        "return_interval_cv": "",
        "linear_ar_forecast_mae": "",
        "nonlinear_forecast_mae": "",
        "backlog_adjusted_productivity": _backlog_adjusted_productivity(metrics),
        "dominant_source_share": source_shares["dominant_source_share"],
        "dominant_source": source_shares["dominant_source"],
    }
    if missing:
        return {
            **base,
            "residualization_status": "missing_required_fields",
            "status": "missing_required_fields",
            "interpretation": "required source/control fields are absent; recurrence not evaluated",
        }
    if len(metrics) < _MIN_RECURRENCE_ROWS:
        return {
            **base,
            "residualization_status": "insufficient_horizon",
            "status": "insufficient_horizon",
            "interpretation": "smoke horizon is too short for preregistered recurrence interpretation",
        }

    raw_values = [_number(row, target_field) for row in metrics]
    controls = [
        [_number(row, field) for field in A6_2_CONTROL_FIELDS] + _source_share_vector(source_shares)
        for row in metrics
    ]
    residuals = _residualize(raw_values, controls)
    recurrence = _recurrence_metrics(residuals)
    return {
        **base,
        "residualization_status": "computed",
        "recurrence_radius": recurrence["recurrence_radius"],
        "residual_variance": recurrence["residual_variance"],
        "lag1_autocorrelation": recurrence["lag1_autocorrelation"],
        "delay_embedded_recurrence_rate": recurrence["delay_embedded_recurrence_rate"],
        "return_interval_cv": recurrence["return_interval_cv"],
        "linear_ar_forecast_mae": recurrence["linear_ar_forecast_mae"],
        "nonlinear_forecast_mae": recurrence["nonlinear_forecast_mae"],
        "status": "computed",
        "interpretation": "recurrence metrics computed for audit; promotion requires paired null-gate deltas",
    }


def _delta_rows(recurrence_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {
        (str(row["condition"]), int(row["seed"]), str(row["target_field"])): row
        for row in recurrence_rows
    }
    seeds = sorted({int(row["seed"]) for row in recurrence_rows})
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        for target_field in A6_2_TARGET_FIELDS:
            logistic = by_key.get(("logistic", seed, target_field))
            for control_condition in _A6_2_CONTROL_CONDITIONS:
                control = by_key.get((control_condition, seed, target_field))
                paired = logistic is not None and control is not None
                status = _paired_status(logistic, control)
                gate_status = _gate_status(logistic, control, status)
                rows.append(
                    {
                        "contrast": f"logistic_vs_{control_condition}",
                        "seed": seed,
                        "control_condition": control_condition,
                        "target_field": target_field,
                        "paired": str(paired).lower(),
                        "status": status,
                        "logistic_status": "" if logistic is None else logistic["status"],
                        "control_status": "" if control is None else control["status"],
                        "residual_variance_delta": _metric_delta(logistic, control, "residual_variance"),
                        "lag1_autocorrelation_delta": _metric_delta(logistic, control, "lag1_autocorrelation"),
                        "delay_embedded_recurrence_rate_delta": _metric_delta(logistic, control, "delay_embedded_recurrence_rate"),
                        "return_interval_cv_delta": _metric_delta(logistic, control, "return_interval_cv"),
                        "linear_ar_forecast_mae_delta": _metric_delta(logistic, control, "linear_ar_forecast_mae"),
                        "nonlinear_forecast_mae_delta": _metric_delta(logistic, control, "nonlinear_forecast_mae"),
                        "backlog_adjusted_productivity_delta": _metric_delta(logistic, control, "backlog_adjusted_productivity"),
                        "gate_status": gate_status,
                        "interpretation": _delta_interpretation(gate_status),
                    }
                )
    return rows


def _missing_run_fields(run: dict[str, Any], target_field: str) -> list[str]:
    metrics = run["metrics"]
    events = run["events"]
    metric_fields = set(metrics[0])
    event_fields = set(events[0]) if events else set()
    missing = ({target_field, "tasks_worked_tick"} | set(A6_2_CONTROL_FIELDS)) - metric_fields
    missing |= set(A6_2_EVENT_SOURCE_FIELDS) - event_fields
    return sorted(missing)


def _source_shares(run: dict[str, Any], target_field: str) -> dict[str, Any]:
    artifact_field = target_field.removesuffix("_tick")
    if artifact_field.startswith("a6_artifact_"):
        artifact_field = artifact_field.removeprefix("a6_artifact_")
    totals = {
        "ambient": 0.0,
        "handoff_attempt": 0.0,
        "handoff_success": 0.0,
        "handoff_failure": 0.0,
        "prediction_expenditure": 0.0,
        "prediction_error": 0.0,
        "queue_work_accounting": 0.0,
        "noise": 0.0,
        "clip_residual": 0.0,
    }
    if not target_field.startswith("a6_artifact_"):
        return _share_result(totals)
    for event in run["events"]:
        if str(event.get("a6_artifact_field", "")) != artifact_field:
            continue
        for source in totals:
            totals[source] += abs(_number(event, f"a6_artifact_delta_{source}"))
    return _share_result(totals)


def _share_result(totals: dict[str, float]) -> dict[str, Any]:
    total = sum(totals.values())
    shares = {
        f"{source}_share": (round(value / total, 6) if total else 0.0)
        for source, value in totals.items()
    }
    dominant_source = max(totals, key=totals.get) if total else ""
    shares["dominant_source"] = dominant_source
    shares["dominant_source_share"] = shares.get(f"{dominant_source}_share", 0.0) if dominant_source else 0.0
    return shares


def _source_share_vector(source_shares: dict[str, Any]) -> list[float]:
    return [float(source_shares.get(field, 0.0)) for field in A6_2_SOURCE_SHARE_FIELDS]


def _residualize(values: list[float], controls: list[list[float]]) -> list[float]:
    # Small deterministic projection: remove intercept plus one-at-a-time linear effects.
    residuals = [value - _mean(values) for value in values]
    for column_index in range(len(controls[0]) if controls else 0):
        column = [row[column_index] for row in controls]
        centered = [value - _mean(column) for value in column]
        denom = sum(value * value for value in centered)
        if denom <= 1e-12:
            continue
        slope = sum(x * y for x, y in zip(centered, residuals)) / denom
        residuals = [y - slope * x for x, y in zip(centered, residuals)]
    return residuals


def _recurrence_metrics(values: list[float]) -> dict[str, Any]:
    variance = _variance(values)
    lag1 = _lag1_autocorrelation(values)
    embedded = list(zip(values[:-_EMBEDDING_DELAY], values[_EMBEDDING_DELAY:]))
    distances = [
        math.dist(left, right)
        for index, left in enumerate(embedded)
        for right in embedded[index + 1 :]
    ]
    radius = _mean(distances) * 0.25 if distances else 0.0
    hits = [index for index, distance in enumerate(distances) if distance <= radius]
    intervals = [b - a for a, b in zip(hits, hits[1:])]
    return {
        "recurrence_radius": _round(radius),
        "residual_variance": _round(variance),
        "lag1_autocorrelation": _round(lag1),
        "delay_embedded_recurrence_rate": _round(len(hits) / len(distances)) if distances else "",
        "return_interval_cv": _round(_stddev(intervals) / _mean(intervals)) if intervals and _mean(intervals) else "",
        "linear_ar_forecast_mae": _round(_linear_ar_mae(values)),
        "nonlinear_forecast_mae": _round(_nearest_neighbor_mae(values)),
    }


def _linear_ar_mae(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    xs = values[:-1]
    ys = values[1:]
    x_mean = _mean(xs)
    y_mean = _mean(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom if denom else 0.0
    intercept = y_mean - slope * x_mean
    return _mean([abs((intercept + slope * x) - y) for x, y in zip(xs, ys)])


def _nearest_neighbor_mae(values: list[float]) -> float:
    if len(values) < 4:
        return 0.0
    errors = []
    for index in range(1, len(values) - 1):
        prior_indices = range(0, index)
        nearest = min(prior_indices, key=lambda prior: abs(values[prior] - values[index]))
        errors.append(abs(values[nearest + 1] - values[index + 1]))
    return _mean(errors)


def _paired_status(logistic: dict[str, Any] | None, control: dict[str, Any] | None) -> str:
    if logistic is None or control is None:
        return "paired_seed_incomplete"
    if logistic["status"] == "missing_required_fields" or control["status"] == "missing_required_fields":
        return "missing_required_fields"
    if logistic["status"] == "insufficient_horizon" or control["status"] == "insufficient_horizon":
        return "insufficient_horizon"
    return "computed"


def _gate_status(
    logistic: dict[str, Any] | None,
    control: dict[str, Any] | None,
    status: str,
) -> str:
    if status != "computed":
        return status
    if _as_float(logistic["backlog_adjusted_productivity"]) < _as_float(control["backlog_adjusted_productivity"]):
        return "closure_productivity_degrades"
    if _as_float(logistic["delay_embedded_recurrence_rate"]) <= _as_float(control["delay_embedded_recurrence_rate"]):
        return "closure_no_recurrence_advantage"
    return "eligible_for_cross_seed_direction_check"


def _delta_interpretation(gate_status: str) -> str:
    if gate_status == "insufficient_horizon":
        return "existing smoke horizon is too short; do not rescue by broadening seeds in this run"
    if gate_status == "missing_required_fields":
        return "required A6.2 fields missing; recurrence interpretation blocked"
    if gate_status == "paired_seed_incomplete":
        return "paired condition/seed artifacts incomplete"
    if gate_status == "closure_productivity_degrades":
        return "recurrence-like metric is not enough because backlog-adjusted productivity degrades"
    if gate_status == "closure_no_recurrence_advantage":
        return "logistic does not beat the paired control on recurrence rate"
    return "computed row only; cross-seed and null agreement still required before eligibility"


def _metric_delta(
    logistic: dict[str, Any] | None,
    control: dict[str, Any] | None,
    field: str,
) -> str:
    if logistic is None or control is None:
        return ""
    if logistic.get(field, "") == "" or control.get(field, "") == "":
        return ""
    return _round(_as_float(logistic[field]) - _as_float(control[field]))


def _backlog_adjusted_productivity(metrics: list[dict[str, str]]) -> float:
    last = metrics[-1]
    completed = _number(last, "tasks_completed_total")
    queue_depth = _number(last, "queue_depth")
    work_events = sum(_number(row, "tasks_worked_tick") for row in metrics)
    return _round(completed / (1.0 + queue_depth + work_events))


def _overall_status(
    completeness_rows: list[dict[str, Any]],
    recurrence_rows: list[dict[str, Any]],
    delta_rows: list[dict[str, Any]],
) -> str:
    if any(row["required_field_status"] == "missing_required_fields" for row in completeness_rows):
        return "missing_required_fields"
    if any(row["status"] == "insufficient_horizon" for row in recurrence_rows):
        return "insufficient_horizon"
    if any(row["gate_status"].startswith("closure") for row in delta_rows):
        return "conservative_closure"
    return "computed_no_promotion"


def _summary(
    compare_path: Path,
    completeness_rows: list[dict[str, Any]],
    recurrence_rows: list[dict[str, Any]],
    delta_rows: list[dict[str, Any]],
    manifest_row: dict[str, Any],
) -> str:
    completeness_statuses = _counts(row["required_field_status"] for row in completeness_rows)
    recurrence_statuses = _counts(row["status"] for row in recurrence_rows)
    gate_statuses = _counts(row["gate_status"] for row in delta_rows)
    lines = [
        "# A6.2 Residual-Recurrence Gate",
        "",
        f"- compare dir: {compare_path}",
        "- reran simulations: no",
        f"- run artifacts read: {manifest_row['run_count']}",
        f"- conditions observed: {manifest_row['condition_count']}",
        f"- seeds observed: {manifest_row['seed_count']}",
        f"- recurrence rows: {manifest_row['recurrence_rows']}",
        f"- paired delta rows: {manifest_row['delta_rows']}",
        f"- status: {manifest_row['status']}",
        "",
        "## Status Counts",
        "",
        f"- required field status: {_format_counts(completeness_statuses)}",
        f"- recurrence row status: {_format_counts(recurrence_statuses)}",
        f"- delta gate status: {_format_counts(gate_statuses)}",
        "",
        "## Gate Reminder",
        "",
        "- A6.2 is read-only and consumes existing A6.1 source-preserving null artifacts.",
        "- Rows marked insufficient_horizon are not recurrence evidence.",
        "- Do not broaden seeds, add mechanisms, or promote A6 from this gate.",
        "- Eligibility requires source fields, residualization, recurrence advantage over linear and both source-preserving nulls, cross-seed sign agreement, and no backlog-adjusted productivity degradation.",
        "",
    ]
    return "\n".join(lines)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _ensure_output_paths_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [name for name in _A6_2_OUTPUT_NAMES if (output_path / name).exists()]
    if collisions:
        raise FileExistsError(
            f"Output path {output_path} already contains A6.2 analysis artifacts: {', '.join(collisions)}"
        )


def _number(row: dict[str, Any], field: str) -> float:
    value = row.get(field, 0)
    if value in ("", None):
        return 0.0
    return float(value)


def _as_float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    return float(value)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _variance(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = _mean(values)
    return _mean([(value - mean) ** 2 for value in values])


def _stddev(values: list[float]) -> float:
    return math.sqrt(_variance(values))


def _lag1_autocorrelation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    left = values[:-1]
    right = values[1:]
    left_mean = _mean(left)
    right_mean = _mean(right)
    denom = math.sqrt(
        sum((value - left_mean) ** 2 for value in left)
        * sum((value - right_mean) ** 2 for value in right)
    )
    if denom <= 1e-12:
        return 0.0
    return sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right)) / denom


def _round(value: float) -> float:
    return round(float(value), 6)


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[str(value)] = counts.get(str(value), 0) + 1
    return counts


def _format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts)) if counts else "none"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze existing A6.1 artifacts for the A6.2 residual-recurrence gate."
    )
    parser.add_argument(
        "--compare-dir",
        default=str(DEFAULT_A6_2_COMPARE_DIR),
        help="Directory containing existing A6.1 source-preserving null run artifacts.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A6_2_OUT_DIR),
        help="Output directory for derived A6.2 analysis artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_a6_2_residual_recurrence_analysis(args.compare_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
