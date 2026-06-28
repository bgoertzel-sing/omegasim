"""Read-only A7.2 delayed-prediction analyzer preflight."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import yaml

from ohdyn.a7_2_delayed_prediction_contract import (
    A7_2_ANALYZER_COMPLETENESS_FIELDS,
    A7_2_ANALYZER_GUARDRAIL_FIELDS,
    A7_2_ANALYZER_MANIFEST_FIELDS,
    A7_2_ANALYZER_NULL_CONTRAST_FIELDS,
    A7_2_ANALYZER_PREFLIGHT_FIELDS,
    A7_2_ANALYZER_RESIDUAL_FIELDS,
    A7_2_CONDITIONS,
    A7_2_CONTROL_FIELDS,
    A7_2_NULL_CONDITIONS,
    A7_2_POSITIVE_CONDITION,
    A7_2_PRODUCTIVITY_GUARDRAILS,
    A7_2_SMOKE_PARAMETERS,
    A7_2_SOURCE_LEDGER_FIELDS,
    A7_2_STATE_FIELDS,
    a7_2_required_event_fields,
    a7_2_required_metric_fields,
)


DEFAULT_A7_2_COMPARE_DIR = Path("runs/a7_2_delayed_prediction_compare_seed1_2")
DEFAULT_A7_2_OUT_DIR = Path("runs/a7_2_delayed_prediction_analysis_seed1_2")
_A7_2_OUTPUT_NAMES = (
    "a7_2_delayed_prediction_completeness.csv",
    "a7_2_delayed_prediction_manifest.csv",
    "a7_2_delayed_prediction_preflight.csv",
    "a7_2_delayed_prediction_residual_metrics.csv",
    "a7_2_delayed_prediction_null_contrasts.csv",
    "a7_2_delayed_prediction_productivity_guardrails.csv",
    "summary.md",
)
_A7_2_TARGET_FIELDS = (
    "a7_2_forecast_error_lag1",
    "a7_2_forecast_uncertainty_lag1",
    "a7_2_artifact_readiness",
    "a7_2_artifact_coherence",
    "a7_2_artifact_contradiction",
    "a7_2_artifact_risk",
    "a7_2_artifact_revision_pressure",
)


def run_a7_2_delayed_prediction_analysis(
    compare_dir: str | Path = DEFAULT_A7_2_COMPARE_DIR,
    out_dir: str | Path = DEFAULT_A7_2_OUT_DIR,
) -> dict[str, Any]:
    """Inspect existing A7.2 artifacts without rerunning simulations."""

    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs = _read_runs(compare_path)
    completeness_rows = [_completeness_row(run) for run in runs]
    preflight_rows = [
        _preflight_row(run, completeness)
        for run, completeness in zip(runs, completeness_rows, strict=True)
    ]
    residual_rows = [
        _residual_metric_row(run, target_field)
        for run in runs
        for target_field in _A7_2_TARGET_FIELDS
    ]
    contrast_rows = _null_contrast_rows(residual_rows)
    guardrail_rows = _guardrail_rows(runs)
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    status = _overall_status(
        completeness_rows,
        preflight_rows,
        residual_rows,
        contrast_rows,
        guardrail_rows,
        conditions,
        seeds,
    )
    manifest_rows = [
        {
            "compare_dir": str(compare_path),
            "condition_count": len(conditions),
            "seed_count": len(seeds),
            "run_count": len(runs),
            "status": status,
        }
    ]

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "a7_2_delayed_prediction_completeness.csv",
        completeness_rows,
        A7_2_ANALYZER_COMPLETENESS_FIELDS,
    )
    _write_csv(
        output_path / "a7_2_delayed_prediction_manifest.csv",
        manifest_rows,
        A7_2_ANALYZER_MANIFEST_FIELDS,
    )
    _write_csv(
        output_path / "a7_2_delayed_prediction_preflight.csv",
        preflight_rows,
        A7_2_ANALYZER_PREFLIGHT_FIELDS,
    )
    _write_csv(
        output_path / "a7_2_delayed_prediction_residual_metrics.csv",
        residual_rows,
        A7_2_ANALYZER_RESIDUAL_FIELDS,
    )
    _write_csv(
        output_path / "a7_2_delayed_prediction_null_contrasts.csv",
        contrast_rows,
        A7_2_ANALYZER_NULL_CONTRAST_FIELDS,
    )
    _write_csv(
        output_path / "a7_2_delayed_prediction_productivity_guardrails.csv",
        guardrail_rows,
        A7_2_ANALYZER_GUARDRAIL_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(
            compare_path,
            completeness_rows,
            preflight_rows,
            residual_rows,
            contrast_rows,
            guardrail_rows,
            manifest_rows[0],
        )
    )
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "condition_count": len(conditions),
        "seed_count": len(seeds),
        "run_count": len(runs),
        "status": status,
    }


def _read_runs(compare_path: Path) -> list[dict[str, Any]]:
    if not compare_path.exists():
        raise FileNotFoundError(f"A7.2 comparison directory does not exist: {compare_path}")
    runs: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        manifest_path = run_dir / "manifest.yaml"
        if not manifest_path.exists():
            continue
        manifest = yaml.safe_load(manifest_path.read_text()) or {}
        config = manifest.get("config", {})
        a7_2_config = config.get("a7_2_delayed_prediction", {})
        condition = a7_2_config.get("condition") or _condition_from_name(run_dir.name)
        seed = int(manifest.get("seed", _seed_from_name(run_dir.name)))
        runs.append(
            {
                "condition": condition,
                "seed": seed,
                "metrics_path": run_dir / "metrics.csv",
                "events_path": run_dir / "events.csv",
                "metrics": _read_csv_rows(run_dir / "metrics.csv"),
                "events": _read_csv_rows(run_dir / "events.csv"),
            }
        )
    return runs


def _condition_from_name(name: str) -> str:
    for condition in A7_2_CONDITIONS:
        if name.startswith(condition):
            return condition
    return name.rsplit("_seed", 1)[0]


def _seed_from_name(name: str) -> int:
    if "_seed" not in name:
        return 0
    suffix = name.rsplit("_seed", 1)[1]
    digits = "".join(char for char in suffix if char.isdigit())
    return int(digits) if digits else 0


def _completeness_row(run: dict[str, Any]) -> dict[str, str | int]:
    metrics_path = Path(run["metrics_path"])
    events_path = Path(run["events_path"])
    metric_header, row_count = _csv_header_and_row_count(metrics_path)
    event_header, _ = _csv_header_and_row_count(events_path)
    missing = (
        *missing_fields(metric_header, a7_2_required_metric_fields()),
        *missing_fields(event_header, a7_2_required_event_fields()),
    )
    required_status = "pass" if not missing else "missing_fields"
    source_status = (
        _source_reconstruction_status(run["events"]) if not missing else "not_evaluable"
    )
    status = "pass" if not missing and source_status == "pass" else "fail_closed"
    interpretation = (
        "A7.2 schema/source ledger is present; result interpretation still requires null and guardrail gates."
        if status == "pass"
        else "A7.2 artifacts are incomplete; no delayed-prediction interpretation is allowed."
    )
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "metrics_path": str(metrics_path),
        "events_path": str(events_path),
        "row_count": row_count,
        "required_field_status": required_status,
        "missing_required_fields": "|".join(missing),
        "source_reconstruction_status": source_status,
        "status": status,
        "interpretation": interpretation,
    }


def missing_fields(observed: set[str] | frozenset[str], required: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(field for field in required if field not in observed)


def _csv_header_and_row_count(path: Path) -> tuple[frozenset[str], int]:
    if not path.exists():
        return frozenset(), 0
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return frozenset(reader.fieldnames or ()), sum(1 for _ in reader)


def _source_reconstruction_status(events: list[dict[str, str]]) -> str:
    if not events:
        return "missing_events"
    checked = 0
    for row in events:
        if row.get("event_type") not in {
            "a7_2_action_selected",
            "a7_2_delayed_artifact_update",
        }:
            continue
        checked += 1
        for field in A7_2_SOURCE_LEDGER_FIELDS:
            _float_cell(row.get(field))
        if row.get("selected_action") in {"review", "synthesize"}:
            source_sum = sum(
                abs(_float_cell(row.get(field)))
                for field in (
                    "source_ledger_artifact_readiness_delta",
                    "source_ledger_artifact_coherence_delta",
                    "source_ledger_artifact_contradiction_delta",
                    "source_ledger_artifact_risk_delta",
                )
            )
            artifact_total = abs(_float_cell(row.get("source_ledger_artifact")))
            if round(source_sum, 6) != round(artifact_total, 6):
                return "fail"
    return "pass" if checked else "no_a7_2_events"


def _preflight_row(
    run: dict[str, Any],
    completeness_row: dict[str, str | int],
) -> dict[str, str | int]:
    metrics = run["metrics"]
    events = run["events"]
    varying_state_count = sum(1 for field in A7_2_STATE_FIELDS if _metric_range(metrics, field) > 0)
    prediction_spend_ticks = sum(
        1 for row in metrics if _float_cell(row.get("a7_2_prediction_spend")) > 0.0
    )
    work_budget_reduction_ticks = sum(
        1
        for row in metrics
        if _float_cell(row.get("remaining_work_budget"))
        < _float_cell(row.get("action_opportunity"))
    )
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "field_variation_status": "pass" if varying_state_count else "no_field_variation",
        "varying_state_field_count": varying_state_count,
        "prediction_spend_ticks": prediction_spend_ticks,
        "work_budget_reduction_ticks": work_budget_reduction_ticks,
        "forecast_delay_status": _forecast_delay_status(events),
        "artifact_delay_status": _artifact_delay_status(events),
        "source_reconstruction_status": completeness_row["source_reconstruction_status"],
        "scientific_interpretation_status": (
            "preflight_only_no_a7_2_promotion_claim"
        ),
    }


def _metric_range(rows: list[dict[str, str]], state_field: str) -> float:
    metric_name = f"a7_2_{state_field}"
    values = [
        _float_cell(row.get(metric_name))
        for row in rows
        if metric_name in row and _is_float_cell(row.get(metric_name))
    ]
    return max(values) - min(values) if values else 0.0


def _forecast_delay_status(events: list[dict[str, str]]) -> str:
    expected = A7_2_SMOKE_PARAMETERS["forecast_delay_ticks"]
    predict_events = [
        row
        for row in events
        if row.get("event_type") == "a7_2_action_selected"
        and row.get("selected_action") == "predict"
        and row.get("forecast_update_created_tick") not in {"", None}
    ]
    if not predict_events:
        return "no_predict_events"
    for row in predict_events:
        observed = int(_float_cell(row.get("forecast_update_visible_tick"))) - int(
            _float_cell(row.get("forecast_update_created_tick"))
        )
        if observed != expected:
            return "fail"
    return "pass"


def _artifact_delay_status(events: list[dict[str, str]]) -> str:
    expected = A7_2_SMOKE_PARAMETERS["artifact_delay_ticks"]
    artifact_events = [
        row
        for row in events
        if row.get("event_type") == "a7_2_action_selected"
        and row.get("selected_action") in {"review", "synthesize"}
        and row.get("artifact_update_created_tick") not in {"", None}
    ]
    if not artifact_events:
        return "no_artifact_events"
    for row in artifact_events:
        observed = int(_float_cell(row.get("artifact_update_visible_tick"))) - int(
            _float_cell(row.get("artifact_update_created_tick"))
        )
        if observed != expected:
            return "fail"
    return "pass"


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _residual_metric_row(run: dict[str, Any], target_field: str) -> dict[str, Any]:
    metrics = run["metrics"]
    missing = _missing_residual_fields(metrics, target_field)
    base = {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "target_field": target_field,
        "row_count": len(metrics),
        "missing_required_fields": "|".join(missing),
        "control_fields_used": "|".join(A7_2_CONTROL_FIELDS),
        "residualization_status": "",
        "residual_variance": "",
        "lag1_autocorrelation": "",
        "nearest_neighbor_forecast_mae": "",
        "status": "",
        "interpretation": "",
    }
    if missing:
        return {
            **base,
            "residualization_status": "missing_required_fields",
            "status": "missing_required_fields",
            "interpretation": "required A7.2 target/control fields are absent",
        }
    raw_values = [_float_cell(row.get(target_field)) for row in metrics]
    controls = [[_float_cell(row.get(field)) for field in A7_2_CONTROL_FIELDS] for row in metrics]
    residuals = _residualize(raw_values, controls)
    return {
        **base,
        "residualization_status": "computed",
        "residual_variance": _round(_variance(residuals)),
        "lag1_autocorrelation": _round(_lag1_autocorrelation(residuals)),
        "nearest_neighbor_forecast_mae": _round(_nearest_neighbor_mae(residuals)),
        "status": "computed",
        "interpretation": "residual preflight metric computed; promotion requires all null and guardrail gates",
    }


def _missing_residual_fields(metrics: list[dict[str, str]], target_field: str) -> list[str]:
    if not metrics:
        return sorted({target_field, *A7_2_CONTROL_FIELDS})
    fields = set(metrics[0])
    return sorted(({target_field} | set(A7_2_CONTROL_FIELDS)) - fields)


def _null_contrast_rows(residual_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {
        (str(row["condition"]), int(row["seed"]), str(row["target_field"])): row
        for row in residual_rows
    }
    seeds = sorted({int(row["seed"]) for row in residual_rows})
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        for target_field in _A7_2_TARGET_FIELDS:
            positive = by_key.get((A7_2_POSITIVE_CONDITION, seed, target_field))
            for control_condition in A7_2_NULL_CONDITIONS:
                control = by_key.get((control_condition, seed, target_field))
                status = _paired_status(positive, control)
                gate_status = _gate_status(positive, control, status)
                rows.append(
                    {
                        "contrast": f"{A7_2_POSITIVE_CONDITION}_vs_{control_condition}",
                        "seed": seed,
                        "control_condition": control_condition,
                        "target_field": target_field,
                        "paired": str(positive is not None and control is not None).lower(),
                        "status": status,
                        "positive_status": "" if positive is None else positive["status"],
                        "control_status": "" if control is None else control["status"],
                        "residual_variance_delta": _metric_delta(positive, control, "residual_variance"),
                        "lag1_autocorrelation_delta": _metric_delta(positive, control, "lag1_autocorrelation"),
                        "nearest_neighbor_forecast_mae_delta": _metric_delta(positive, control, "nearest_neighbor_forecast_mae"),
                        "gate_status": gate_status,
                        "interpretation": _contrast_interpretation(gate_status),
                    }
                )
    return rows


def _paired_status(
    positive: dict[str, Any] | None,
    control: dict[str, Any] | None,
) -> str:
    if positive is None or control is None:
        return "paired_seed_incomplete"
    if positive["status"] == "missing_required_fields" or control["status"] == "missing_required_fields":
        return "missing_required_fields"
    return "computed"


def _gate_status(
    positive: dict[str, Any] | None,
    control: dict[str, Any] | None,
    status: str,
) -> str:
    if status != "computed":
        return status
    if _as_float(positive["lag1_autocorrelation"]) <= _as_float(control["lag1_autocorrelation"]):
        return "fail_closed_no_residual_autocorrelation_advantage"
    if _as_float(positive["nearest_neighbor_forecast_mae"]) >= _as_float(control["nearest_neighbor_forecast_mae"]):
        return "fail_closed_no_nonlinear_forecastability_advantage"
    return "eligible_for_guardrail_and_cross_seed_review"


def _contrast_interpretation(gate_status: str) -> str:
    if gate_status == "missing_required_fields":
        return "required residualization fields are missing"
    if gate_status == "paired_seed_incomplete":
        return "paired A7.2 condition/seed artifact is incomplete"
    if gate_status == "fail_closed_no_residual_autocorrelation_advantage":
        return "candidate does not beat the paired null on residual autocorrelation"
    if gate_status == "fail_closed_no_nonlinear_forecastability_advantage":
        return "candidate does not beat the paired null on nonlinear forecastability"
    return "computed preflight row only; guardrails and cross-seed agreement are still required"


def _guardrail_rows(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {(str(run["condition"]), int(run["seed"])): run for run in runs}
    seeds = sorted({int(run["seed"]) for run in runs})
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        positive = by_key.get((A7_2_POSITIVE_CONDITION, seed))
        for control_condition in A7_2_NULL_CONDITIONS:
            control = by_key.get((control_condition, seed))
            row = _guardrail_row(seed, control_condition, positive, control)
            rows.append(row)
    return rows


def _guardrail_row(
    seed: int,
    control_condition: str,
    positive: dict[str, Any] | None,
    control: dict[str, Any] | None,
) -> dict[str, Any]:
    if positive is None or control is None:
        return {
            "seed": seed,
            "control_condition": control_condition,
            "completion_fraction_delta": "",
            "backlog_delta": "",
            "queued_age_delta": "",
            "starvation_delta": "",
            "prediction_spend_volatility_delta": "",
            "work_budget_volatility_delta": "",
            "status": "paired_seed_incomplete",
            "interpretation": "paired A7.2 condition/seed artifact is incomplete",
        }
    positive_summary = _run_summary_stats(positive["metrics"])
    control_summary = _run_summary_stats(control["metrics"])
    deltas = {
        key: _round(positive_summary[key] - control_summary[key])
        for key in positive_summary
    }
    failures = []
    if deltas["completion_fraction"] < A7_2_PRODUCTIVITY_GUARDRAILS["completion_fraction_delta_min"]:
        failures.append("completion_fraction")
    if deltas["backlog"] > A7_2_PRODUCTIVITY_GUARDRAILS["backlog_delta_max"]:
        failures.append("backlog")
    if deltas["queued_age"] > A7_2_PRODUCTIVITY_GUARDRAILS["queued_age_delta_max"]:
        failures.append("queued_age")
    if deltas["starvation"] > A7_2_PRODUCTIVITY_GUARDRAILS["starvation_delta_max"]:
        failures.append("starvation")
    if deltas["prediction_spend_volatility"] > A7_2_PRODUCTIVITY_GUARDRAILS["prediction_spend_volatility_delta_max"]:
        failures.append("prediction_spend_volatility")
    if deltas["work_budget_volatility"] > A7_2_PRODUCTIVITY_GUARDRAILS["work_budget_volatility_delta_max"]:
        failures.append("work_budget_volatility")
    return {
        "seed": seed,
        "control_condition": control_condition,
        "completion_fraction_delta": deltas["completion_fraction"],
        "backlog_delta": deltas["backlog"],
        "queued_age_delta": deltas["queued_age"],
        "starvation_delta": deltas["starvation"],
        "prediction_spend_volatility_delta": deltas["prediction_spend_volatility"],
        "work_budget_volatility_delta": deltas["work_budget_volatility"],
        "status": "pass" if not failures else "fail_closed_" + "|".join(failures),
        "interpretation": (
            "productivity guardrail preflight passed for this paired contrast"
            if not failures
            else "candidate violates preregistered productivity guardrail(s): "
            + ", ".join(failures)
        ),
    }


def _run_summary_stats(metrics: list[dict[str, str]]) -> dict[str, float]:
    if not metrics:
        return {
            "completion_fraction": 0.0,
            "backlog": 0.0,
            "queued_age": 0.0,
            "starvation": 0.0,
            "prediction_spend_volatility": 0.0,
            "work_budget_volatility": 0.0,
        }
    return {
        "completion_fraction": _mean([_float_cell(row.get("completion_fraction")) for row in metrics]),
        "backlog": _float_cell(metrics[-1].get("backlog")),
        "queued_age": _mean([_float_cell(row.get("queued_age")) for row in metrics]),
        "starvation": _mean([_float_cell(row.get("starvation")) for row in metrics]),
        "prediction_spend_volatility": _mean(
            [_float_cell(row.get("prediction_spend_volatility")) for row in metrics]
        ),
        "work_budget_volatility": _mean(
            [_float_cell(row.get("work_budget_volatility")) for row in metrics]
        ),
    }


def _metric_delta(
    positive: dict[str, Any] | None,
    control: dict[str, Any] | None,
    field: str,
) -> str:
    if positive is None or control is None:
        return ""
    if positive.get(field, "") == "" or control.get(field, "") == "":
        return ""
    return _round(_as_float(positive[field]) - _as_float(control[field]))


def _residualize(values: list[float], controls: list[list[float]]) -> list[float]:
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


def _nearest_neighbor_mae(values: list[float]) -> float:
    if len(values) < 4:
        return 0.0
    errors = []
    for index in range(1, len(values) - 1):
        nearest = min(range(0, index), key=lambda prior: abs(values[prior] - values[index]))
        errors.append(abs(values[nearest + 1] - values[index + 1]))
    return _mean(errors)


def _lag1_autocorrelation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = _mean(values)
    denom = sum((value - mean) ** 2 for value in values)
    if denom <= 1e-12:
        return 0.0
    return sum((a - mean) * (b - mean) for a, b in zip(values[:-1], values[1:])) / denom


def _variance(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = _mean(values)
    return _mean([(value - mean) ** 2 for value in values])


def _float_cell(value: str | None) -> float:
    if value in {None, ""}:
        return 0.0
    return float(value)


def _is_float_cell(value: str | None) -> bool:
    if value in {None, ""}:
        return True
    try:
        float(value)
    except ValueError:
        return False
    return True


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _as_float(value: Any) -> float:
    if value in {"", None}:
        return 0.0
    return float(value)


def _round(value: float) -> float:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return 0.0
    return round(value, 6)


def _overall_status(
    completeness_rows: list[dict[str, str | int]],
    preflight_rows: list[dict[str, str | int]],
    residual_rows: list[dict[str, Any]],
    contrast_rows: list[dict[str, Any]],
    guardrail_rows: list[dict[str, Any]],
    conditions: list[str],
    seeds: list[int],
) -> str:
    if not completeness_rows:
        return "fail_closed_no_runs"
    if set(conditions) != set(A7_2_CONDITIONS):
        return "fail_closed_missing_conditions"
    if tuple(seeds) != (1, 2):
        return "fail_closed_unregistered_seeds"
    if any(row["status"] != "pass" for row in completeness_rows):
        return "fail_closed_missing_schema_or_source_ledger"
    if any(row["forecast_delay_status"] == "fail" or row["artifact_delay_status"] == "fail" for row in preflight_rows):
        return "fail_closed_delay_contract"
    if any(row["status"] != "computed" for row in residual_rows):
        return "fail_closed_residual_preflight"
    if any(str(row["status"]).startswith("fail_closed") for row in guardrail_rows):
        return "fail_closed_productivity_guardrails"
    if not contrast_rows or any(
        row["gate_status"] != "eligible_for_guardrail_and_cross_seed_review"
        for row in contrast_rows
    ):
        return "fail_closed_residual_null_gate"
    return "computed_no_promotion_cross_seed_review_required"


def _ensure_output_paths_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [name for name in _A7_2_OUTPUT_NAMES if (output_path / name).exists()]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains artifacts: {names}")


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: tuple[str, ...],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    compare_path: Path,
    completeness_rows: list[dict[str, str | int]],
    preflight_rows: list[dict[str, str | int]],
    residual_rows: list[dict[str, Any]],
    contrast_rows: list[dict[str, Any]],
    guardrail_rows: list[dict[str, Any]],
    manifest: dict[str, str | int],
) -> str:
    schema_pass = sum(1 for row in completeness_rows if row["status"] == "pass")
    forecast_delay_pass = sum(1 for row in preflight_rows if row["forecast_delay_status"] == "pass")
    artifact_delay_pass = sum(1 for row in preflight_rows if row["artifact_delay_status"] == "pass")
    residual_statuses = _counts(str(row["status"]) for row in residual_rows)
    gate_statuses = _counts(str(row["gate_status"]) for row in contrast_rows)
    guardrail_statuses = _counts(str(row["status"]) for row in guardrail_rows)
    return "\n".join(
        [
            "# A7.2 Delayed Prediction Analyzer Preflight",
            "",
            f"- Compare directory: `{compare_path}`",
            f"- Runs inspected: {manifest['run_count']}",
            f"- Status: `{manifest['status']}`",
            f"- Schema/source pass rows: {schema_pass}",
            f"- Forecast delay pass rows: {forecast_delay_pass}",
            f"- Artifact delay pass rows: {artifact_delay_pass}",
            f"- Residual row status: {_format_counts(residual_statuses)}",
            f"- Null-contrast gate status: {_format_counts(gate_statuses)}",
            f"- Productivity guardrail status: {_format_counts(guardrail_statuses)}",
            "",
            "This analyzer is read-only and consumes existing A7.2 artifacts only.",
            "Positive interpretation remains blocked unless every preregistered",
            "null contrast, source-ledger check, productivity guardrail, and paired",
            "seed direction check passes without parameter tuning.",
            "",
        ]
    )


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[str(value)] = counts.get(str(value), 0) + 1
    return counts


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the fail-closed read-only A7.2 delayed-prediction analyzer."
    )
    parser.add_argument("--compare-dir", default=str(DEFAULT_A7_2_COMPARE_DIR))
    parser.add_argument("--out", default=str(DEFAULT_A7_2_OUT_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    run_a7_2_delayed_prediction_analysis(args.compare_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
