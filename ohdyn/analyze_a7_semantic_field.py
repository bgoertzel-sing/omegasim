"""Read-only A7 semantic-field analyzer skeleton.

The first A7 gate must fail closed until simulator artifacts expose the frozen
schema from ``ohdyn.a7_semantic_field_contract``. This module does not rerun
simulations or infer missing fields.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import yaml

from ohdyn.a7_semantic_field_contract import (
    A7_ANALYZER_COMPLETENESS_FIELDS,
    A7_ANALYZER_MANIFEST_FIELDS,
    A7_ANALYZER_NULL_CONTRAST_FIELDS,
    A7_ANALYZER_RESIDUAL_FIELDS,
    A7_ANALYZER_SMOKE_REPORT_FIELDS,
    A7_CONDITIONS,
    A7_CONTROL_FIELDS,
    A7_FIELD_VALUES,
    A7_NULL_CONDITIONS,
    A7_POSITIVE_CONDITION,
    A7_SOURCE_COMPONENTS,
    a7_required_event_fields,
    a7_required_metric_fields,
    missing_fields,
)


DEFAULT_A7_COMPARE_DIR = Path("runs/a7_semantic_field_compare")
DEFAULT_A7_OUT_DIR = Path("runs/a7_semantic_field_analysis")
_A7_OUTPUT_NAMES = (
    "a7_semantic_field_completeness.csv",
    "a7_semantic_field_manifest.csv",
    "a7_semantic_field_residual_metrics.csv",
    "a7_semantic_field_null_contrasts.csv",
    "a7_semantic_field_smoke_report.csv",
    "summary.md",
)
_A7_TARGET_FIELDS = tuple(f"a7_{field}_tick" for field in A7_FIELD_VALUES)
_MIN_RESIDUAL_ROWS = 24


def run_a7_semantic_field_analysis(
    compare_dir: str | Path = DEFAULT_A7_COMPARE_DIR,
    out_dir: str | Path = DEFAULT_A7_OUT_DIR,
) -> dict[str, Any]:
    """Inspect existing A7 artifacts and fail closed on absent schema."""

    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs = _read_runs(compare_path)
    completeness_rows = [_completeness_row(run) for run in runs]
    smoke_rows = [
        _smoke_report_row(run, completeness_row)
        for run, completeness_row in zip(runs, completeness_rows, strict=True)
    ]
    residual_rows = [
        _residual_metric_row(run, target_field)
        for run in runs
        for target_field in _A7_TARGET_FIELDS
    ]
    contrast_rows = _null_contrast_rows(residual_rows)
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    status = _overall_status(completeness_rows, residual_rows, contrast_rows, conditions)
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
        output_path / "a7_semantic_field_completeness.csv",
        completeness_rows,
        A7_ANALYZER_COMPLETENESS_FIELDS,
    )
    _write_csv(
        output_path / "a7_semantic_field_manifest.csv",
        manifest_rows,
        A7_ANALYZER_MANIFEST_FIELDS,
    )
    _write_csv(
        output_path / "a7_semantic_field_smoke_report.csv",
        smoke_rows,
        A7_ANALYZER_SMOKE_REPORT_FIELDS,
    )
    _write_csv(
        output_path / "a7_semantic_field_residual_metrics.csv",
        residual_rows,
        A7_ANALYZER_RESIDUAL_FIELDS,
    )
    _write_csv(
        output_path / "a7_semantic_field_null_contrasts.csv",
        contrast_rows,
        A7_ANALYZER_NULL_CONTRAST_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(
            compare_path,
            completeness_rows,
            smoke_rows,
            residual_rows,
            contrast_rows,
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
        raise FileNotFoundError(f"A7 comparison directory does not exist: {compare_path}")
    runs: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        manifest_path = run_dir / "manifest.yaml"
        if not manifest_path.exists():
            continue
        manifest = yaml.safe_load(manifest_path.read_text()) or {}
        config = manifest.get("config", {})
        semantic_field = config.get("semantic_field", {})
        condition = semantic_field.get("condition") or _condition_from_name(run_dir.name)
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
    for condition in A7_CONDITIONS:
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
        *missing_fields(metric_header, a7_required_metric_fields()),
        *missing_fields(event_header, a7_required_event_fields()),
    )
    required_status = "pass" if not missing else "missing_fields"
    source_status = (
        _source_reconstruction_status(events_path) if not missing else "not_evaluable"
    )
    null_status = "not_evaluable"
    status = (
        "fail_closed"
        if missing or source_status != "pass"
        else "schema_present_analysis_not_implemented"
    )
    interpretation = (
        "A7 artifacts are absent or incomplete; no semantic-field interpretation is allowed."
        if missing
        else "A7 source ledger does not reconstruct field deltas; no semantic-field interpretation is allowed."
        if source_status != "pass"
        else "A7 schema is present; residual recurrence and null contrasts remain unimplemented."
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
        "null_artifact_status": null_status,
        "status": status,
        "interpretation": interpretation,
    }


def _csv_header_and_row_count(path: Path) -> tuple[frozenset[str], int]:
    if not path.exists():
        return frozenset(), 0
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return frozenset(reader.fieldnames or ()), sum(1 for _ in reader)


def _source_reconstruction_status(path: Path) -> str:
    if not path.exists():
        return "missing_events"
    checked = 0
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("event_type") != "a7_semantic_field_update":
                continue
            checked += 1
            source_sum = sum(
                _float_cell(row.get(f"a7_delta_{source}", "0"))
                for source in A7_SOURCE_COMPONENTS
            )
            total = _float_cell(row.get("a7_delta_total", "0"))
            if round(source_sum, 6) != round(total, 6):
                return "fail"
    return "pass" if checked else "no_a7_update_events"


def _smoke_report_row(
    run: dict[str, Any],
    completeness_row: dict[str, str | int],
) -> dict[str, str | int | float]:
    metrics_path = Path(run["metrics_path"])
    metric_rows = _read_csv_rows(metrics_path)
    field_ranges = _field_ranges(metric_rows)
    varying_field_count = sum(1 for value in field_ranges.values() if value > 0.0)
    max_field_range = max(field_ranges.values(), default=0.0)
    prediction_spend_ticks = sum(
        1
        for row in metric_rows
        if _float_cell(row.get("a7_prediction_budget_spent_tick")) > 0.0
    )
    work_budget_reduction_ticks = sum(
        1
        for row in metric_rows
        if _float_cell(row.get("a7_work_budget_tick"))
        < _float_cell(row.get("a7_action_opportunity_tick"))
    )
    total_prediction_budget_spent = round(
        sum(_float_cell(row.get("a7_prediction_budget_spent_tick")) for row in metric_rows),
        6,
    )
    near_threshold_values = [
        _float_cell(row.get("a7_near_threshold_occupancy_tick")) for row in metric_rows
    ]
    mean_near_threshold = round(
        sum(near_threshold_values) / len(near_threshold_values),
        6,
    ) if near_threshold_values else 0.0
    max_near_threshold = round(max(near_threshold_values), 6) if near_threshold_values else 0.0
    competition_status = (
        "pass"
        if prediction_spend_ticks > 0 and work_budget_reduction_ticks > 0
        else "no_prediction_spend"
        if prediction_spend_ticks == 0
        else "no_work_budget_reduction"
    )
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "field_variation_status": "pass" if varying_field_count else "no_field_variation",
        "varying_field_count": varying_field_count,
        "max_field_range": round(max_field_range, 6),
        "prediction_work_budget_competition_status": competition_status,
        "prediction_spend_ticks": prediction_spend_ticks,
        "work_budget_reduction_ticks": work_budget_reduction_ticks,
        "total_prediction_budget_spent": total_prediction_budget_spent,
        "near_threshold_occupancy_status": (
            "measured" if near_threshold_values else "missing"
        ),
        "mean_near_threshold_occupancy": mean_near_threshold,
        "max_near_threshold_occupancy": max_near_threshold,
        "source_reconstruction_status": completeness_row["source_reconstruction_status"],
        "scientific_interpretation_status": (
            "fail_closed_residual_recurrence_and_null_contrasts_not_implemented"
        ),
    }


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
        "control_fields_used": "|".join(A7_CONTROL_FIELDS),
        "residual_variance": "",
        "lag1_autocorrelation": "",
        "linear_ar_forecast_mae": "",
        "nearest_neighbor_forecast_mae": "",
        "backlog_adjusted_productivity": _backlog_adjusted_productivity(metrics),
    }
    if missing:
        return {
            **base,
            "residualization_status": "missing_required_fields",
            "status": "missing_required_fields",
            "interpretation": "required A7 target/control fields are absent; residual null gate not evaluated",
        }
    if len(metrics) < _MIN_RESIDUAL_ROWS:
        return {
            **base,
            "residualization_status": "insufficient_horizon",
            "status": "insufficient_horizon",
            "interpretation": "smoke horizon is too short for preregistered residual/null interpretation",
        }
    raw_values = [_float_cell(row.get(target_field)) for row in metrics]
    controls = [
        [_float_cell(row.get(field)) for field in A7_CONTROL_FIELDS]
        for row in metrics
    ]
    residuals = _residualize(raw_values, controls)
    return {
        **base,
        "residualization_status": "computed",
        "residual_variance": _round(_variance(residuals)),
        "lag1_autocorrelation": _round(_lag1_autocorrelation(residuals)),
        "linear_ar_forecast_mae": _round(_linear_ar_mae(residuals)),
        "nearest_neighbor_forecast_mae": _round(_nearest_neighbor_mae(residuals)),
        "status": "computed",
        "interpretation": "residual metrics computed for audit; promotion requires paired null-gate contrasts",
    }


def _missing_residual_fields(
    metrics: list[dict[str, str]],
    target_field: str,
) -> list[str]:
    if not metrics:
        return sorted({target_field, *A7_CONTROL_FIELDS})
    fields = set(metrics[0])
    return sorted(({target_field} | set(A7_CONTROL_FIELDS)) - fields)


def _null_contrast_rows(residual_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {
        (str(row["condition"]), int(row["seed"]), str(row["target_field"])): row
        for row in residual_rows
    }
    seeds = sorted({int(row["seed"]) for row in residual_rows})
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        for target_field in _A7_TARGET_FIELDS:
            positive = by_key.get((A7_POSITIVE_CONDITION, seed, target_field))
            for control_condition in A7_NULL_CONDITIONS:
                control = by_key.get((control_condition, seed, target_field))
                status = _paired_status(positive, control)
                gate_status = _gate_status(positive, control, status)
                rows.append(
                    {
                        "contrast": f"{A7_POSITIVE_CONDITION}_vs_{control_condition}",
                        "seed": seed,
                        "control_condition": control_condition,
                        "target_field": target_field,
                        "paired": str(positive is not None and control is not None).lower(),
                        "status": status,
                        "positive_status": "" if positive is None else positive["status"],
                        "control_status": "" if control is None else control["status"],
                        "residual_variance_delta": _metric_delta(positive, control, "residual_variance"),
                        "lag1_autocorrelation_delta": _metric_delta(positive, control, "lag1_autocorrelation"),
                        "linear_ar_forecast_mae_delta": _metric_delta(positive, control, "linear_ar_forecast_mae"),
                        "nearest_neighbor_forecast_mae_delta": _metric_delta(positive, control, "nearest_neighbor_forecast_mae"),
                        "backlog_adjusted_productivity_delta": _metric_delta(positive, control, "backlog_adjusted_productivity"),
                        "gate_status": gate_status,
                        "interpretation": _contrast_interpretation(gate_status),
                    }
                )
    return rows


def _field_ranges(rows: list[dict[str, str]]) -> dict[str, float]:
    ranges: dict[str, float] = {}
    for field_name in A7_FIELD_VALUES:
        metric_name = f"a7_{field_name}_tick"
        values = [_float_cell(row.get(metric_name)) for row in rows if metric_name in row]
        if values:
            ranges[field_name] = round(max(values) - min(values), 6)
    return ranges


def _float_cell(value: str | None) -> float:
    if value in {None, ""}:
        return 0.0
    return float(value)


def _paired_status(
    positive: dict[str, Any] | None,
    control: dict[str, Any] | None,
) -> str:
    if positive is None or control is None:
        return "paired_seed_incomplete"
    if positive["status"] == "missing_required_fields" or control["status"] == "missing_required_fields":
        return "missing_required_fields"
    if positive["status"] == "insufficient_horizon" or control["status"] == "insufficient_horizon":
        return "insufficient_horizon"
    return "computed"


def _gate_status(
    positive: dict[str, Any] | None,
    control: dict[str, Any] | None,
    status: str,
) -> str:
    if status != "computed":
        return status
    if _as_float(positive["backlog_adjusted_productivity"]) < _as_float(control["backlog_adjusted_productivity"]):
        return "fail_closed_productivity_degrades"
    if _as_float(positive["lag1_autocorrelation"]) <= _as_float(control["lag1_autocorrelation"]):
        return "fail_closed_no_residual_autocorrelation_advantage"
    if _as_float(positive["nearest_neighbor_forecast_mae"]) >= _as_float(control["nearest_neighbor_forecast_mae"]):
        return "fail_closed_no_nonlinear_forecastability_advantage"
    return "eligible_for_cross_seed_direction_check"


def _contrast_interpretation(gate_status: str) -> str:
    if gate_status == "insufficient_horizon":
        return "existing A7 smoke horizon is too short; no residual/null interpretation is allowed"
    if gate_status == "missing_required_fields":
        return "required residualization fields are missing"
    if gate_status == "paired_seed_incomplete":
        return "paired A7 condition/seed artifact is incomplete"
    if gate_status == "fail_closed_productivity_degrades":
        return "positive condition cannot promote when backlog-adjusted productivity degrades"
    if gate_status == "fail_closed_no_residual_autocorrelation_advantage":
        return "positive condition does not beat the paired null on residual autocorrelation"
    if gate_status == "fail_closed_no_nonlinear_forecastability_advantage":
        return "positive condition does not beat the paired null on nonlinear forecastability"
    return "computed row only; all nulls and cross-seed agreement are still required"


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


def _backlog_adjusted_productivity(metrics: list[dict[str, str]]) -> float:
    if not metrics:
        return 0.0
    completed = _float_cell(metrics[-1].get("tasks_completed_total"))
    queue_depth = _float_cell(metrics[-1].get("queue_depth"))
    work_actions = sum(_float_cell(row.get("a7_work_actions_tick")) for row in metrics)
    return _round(completed / (1.0 + queue_depth + work_actions))


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
    rows: list[dict[str, str | int]],
    residual_rows: list[dict[str, Any]],
    contrast_rows: list[dict[str, Any]],
    conditions: list[str],
) -> str:
    if not rows:
        return "fail_closed_no_runs"
    missing_conditions = set(A7_CONDITIONS) - set(conditions)
    if missing_conditions:
        return "fail_closed_missing_conditions"
    if any(row["status"] == "fail_closed" for row in rows):
        return "fail_closed_missing_schema"
    if any(row["status"] == "insufficient_horizon" for row in residual_rows):
        return "fail_closed_insufficient_horizon"
    if not contrast_rows or any(
        row["gate_status"] != "eligible_for_cross_seed_direction_check"
        for row in contrast_rows
    ):
        return "fail_closed_residual_null_gate"
    return "computed_no_promotion_cross_seed_review_required"


def _ensure_output_paths_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [name for name in _A7_OUTPUT_NAMES if (output_path / name).exists()]
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
    rows: list[dict[str, str | int]],
    smoke_rows: list[dict[str, str | int | float]],
    residual_rows: list[dict[str, Any]],
    contrast_rows: list[dict[str, Any]],
    manifest: dict[str, str | int],
) -> str:
    fail_closed = sum(1 for row in rows if row["status"] == "fail_closed")
    source_pass = sum(
        1 for row in smoke_rows if row["source_reconstruction_status"] == "pass"
    )
    field_variation_pass = sum(
        1 for row in smoke_rows if row["field_variation_status"] == "pass"
    )
    competition_pass = sum(
        1
        for row in smoke_rows
        if row["prediction_work_budget_competition_status"] == "pass"
    )
    residual_statuses = _counts(str(row["status"]) for row in residual_rows)
    gate_statuses = _counts(str(row["gate_status"]) for row in contrast_rows)
    return "\n".join(
        [
            "# A7 Semantic-Field Residual/Null Gate",
            "",
            f"- Compare directory: `{compare_path}`",
            f"- Runs inspected: {manifest['run_count']}",
            f"- Status: `{manifest['status']}`",
            f"- Fail-closed rows: {fail_closed}",
            f"- Source reconstruction pass rows: {source_pass}",
            f"- Field variation pass rows: {field_variation_pass}",
            f"- Prediction/work-budget competition pass rows: {competition_pass}",
            f"- Residual row status: {_format_counts(residual_statuses)}",
            f"- Null-contrast gate status: {_format_counts(gate_statuses)}",
            "",
            "This analyzer is read-only and consumes existing A7 artifacts only.",
            "Positive interpretation remains blocked unless source reconstruction,",
            "residualization, all preregistered null contrasts, productivity safeguards,",
            "and paired-seed direction checks all pass.",
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
        description="Fail-closed read-only A7 semantic-field analyzer skeleton."
    )
    parser.add_argument("--compare-dir", default=str(DEFAULT_A7_COMPARE_DIR))
    parser.add_argument("--out", default=str(DEFAULT_A7_OUT_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    run_a7_semantic_field_analysis(args.compare_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
