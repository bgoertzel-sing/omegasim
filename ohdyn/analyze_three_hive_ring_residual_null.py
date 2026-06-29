"""Read-only three-hive ring residual/null and source-ledger analyzer."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_three_hive_ring_mechanics import (
    DEFAULT_THREE_HIVE_RING_MECHANICS_DIR,
)
from ohdyn.three_hive_ring_contract import (
    THREE_HIVE_RING_ANALYZER_COMPLETENESS_FIELDS,
    THREE_HIVE_RING_ANALYZER_GUARDRAIL_FIELDS,
    THREE_HIVE_RING_ANALYZER_MANIFEST_FIELDS,
    THREE_HIVE_RING_ANALYZER_NULL_CONTRAST_FIELDS,
    THREE_HIVE_RING_ANALYZER_RESIDUAL_FIELDS,
    THREE_HIVE_RING_ANALYZER_SOURCE_LEDGER_FIELDS,
    THREE_HIVE_RING_CONDITIONS,
    THREE_HIVE_RING_NULL_CONDITIONS,
    THREE_HIVE_RING_POSITIVE_CONDITION,
    THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS,
    THREE_HIVE_RING_RESIDUAL_CONTROLS,
    THREE_HIVE_RING_SMOKE_PARAMETERS,
    THREE_HIVE_RING_SOURCE_LEDGER_CSV_FIELDS,
    THREE_HIVE_RING_SOURCE_LEDGER_FIELDS,
    three_hive_ring_required_event_fields,
    three_hive_ring_required_metric_fields,
)


DEFAULT_THREE_HIVE_RING_RESIDUAL_NULL_DIR = Path(
    "runs/three_hive_ring_residual_null_analysis_seed1_2"
)
_OUTPUT_NAMES = (
    "three_hive_ring_residual_null_completeness.csv",
    "three_hive_ring_residual_null_source_ledger.csv",
    "three_hive_ring_residual_null_metrics.csv",
    "three_hive_ring_residual_null_contrasts.csv",
    "three_hive_ring_residual_null_productivity_guardrails.csv",
    "three_hive_ring_residual_null_manifest.csv",
    "summary.md",
)
_TARGET_FIELDS = (
    "artifact_readiness",
    "artifact_coherence",
    "artifact_contradiction",
    "artifact_risk",
    "artifact_revision_pressure",
    "cross_hive_forecast_error_lag",
)
_NUMERIC_CONTROLS = tuple(
    field
    for field in THREE_HIVE_RING_RESIDUAL_CONTROLS
    if field not in {"role_bias", "source_hive", "target_hive"}
)
_LEDGER_ROUNDING_TOLERANCE = 5e-6


def run_three_hive_ring_residual_null_analysis(
    compare_dir: str | Path = DEFAULT_THREE_HIVE_RING_MECHANICS_DIR,
    out_dir: str | Path = DEFAULT_THREE_HIVE_RING_RESIDUAL_NULL_DIR,
) -> dict[str, Any]:
    """Analyze existing three-hive mechanics artifacts without rerunning them."""

    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs = _read_runs(compare_path)
    completeness_rows = [_completeness_row(run) for run in runs]
    source_ledger_rows = [_source_ledger_row(run) for run in runs]
    residual_rows = [
        _residual_metric_row(run, target)
        for run in runs
        for target in _TARGET_FIELDS
    ]
    contrast_rows = _null_contrast_rows(residual_rows)
    guardrail_rows = _guardrail_rows(runs, source_ledger_rows)
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    status = _overall_status(
        completeness_rows,
        source_ledger_rows,
        residual_rows,
        contrast_rows,
        guardrail_rows,
        conditions,
        seeds,
    )
    manifest_row = {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "condition_count": len(conditions),
        "seed_count": len(seeds),
        "run_count": len(runs),
        "status": status,
    }

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "three_hive_ring_residual_null_completeness.csv",
        completeness_rows,
        THREE_HIVE_RING_ANALYZER_COMPLETENESS_FIELDS,
    )
    _write_csv(
        output_path / "three_hive_ring_residual_null_source_ledger.csv",
        source_ledger_rows,
        THREE_HIVE_RING_ANALYZER_SOURCE_LEDGER_FIELDS,
    )
    _write_csv(
        output_path / "three_hive_ring_residual_null_metrics.csv",
        residual_rows,
        THREE_HIVE_RING_ANALYZER_RESIDUAL_FIELDS,
    )
    _write_csv(
        output_path / "three_hive_ring_residual_null_contrasts.csv",
        contrast_rows,
        THREE_HIVE_RING_ANALYZER_NULL_CONTRAST_FIELDS,
    )
    _write_csv(
        output_path / "three_hive_ring_residual_null_productivity_guardrails.csv",
        guardrail_rows,
        THREE_HIVE_RING_ANALYZER_GUARDRAIL_FIELDS,
    )
    _write_csv(
        output_path / "three_hive_ring_residual_null_manifest.csv",
        [manifest_row],
        THREE_HIVE_RING_ANALYZER_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(
            compare_path,
            completeness_rows,
            source_ledger_rows,
            residual_rows,
            contrast_rows,
            guardrail_rows,
            manifest_row,
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
        raise FileNotFoundError(
            f"Three-hive ring mechanics directory does not exist: {compare_path}"
        )
    runs: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        manifest = _read_manifest(run_dir / "manifest.yaml")
        condition = str(manifest.get("condition") or _condition_from_name(run_dir.name))
        seed = int(manifest.get("seed", _seed_from_name(run_dir.name)))
        runs.append(
            {
                "condition": condition,
                "seed": seed,
                "run_dir": run_dir,
                "metrics_path": run_dir / "metrics.csv",
                "events_path": run_dir / "events.csv",
                "source_ledger_path": run_dir / "source_ledger.csv",
                "metrics": _read_csv_rows(run_dir / "metrics.csv"),
                "events": _read_csv_rows(run_dir / "events.csv"),
                "source_ledger": _read_csv_rows(run_dir / "source_ledger.csv"),
            }
        )
    return runs


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def _condition_from_name(name: str) -> str:
    for condition in THREE_HIVE_RING_CONDITIONS:
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
    metric_header, metric_rows = _csv_header_and_row_count(Path(run["metrics_path"]))
    event_header, event_rows = _csv_header_and_row_count(Path(run["events_path"]))
    source_header, source_rows = _csv_header_and_row_count(Path(run["source_ledger_path"]))
    missing = (
        *missing_fields(metric_header, ("condition", "seed", "hive_id", *three_hive_ring_required_metric_fields())),
        *missing_fields(event_header, three_hive_ring_required_event_fields()),
        *missing_fields(source_header, THREE_HIVE_RING_SOURCE_LEDGER_CSV_FIELDS),
    )
    status = "pass" if not missing and metric_rows and event_rows and source_rows else "fail_closed"
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "metrics_path": str(run["metrics_path"]),
        "events_path": str(run["events_path"]),
        "source_ledger_path": str(run["source_ledger_path"]),
        "metric_row_count": metric_rows,
        "event_row_count": event_rows,
        "source_ledger_row_count": source_rows,
        "required_field_status": "pass" if not missing else "missing_fields",
        "missing_required_fields": "|".join(missing),
        "status": status,
        "interpretation": (
            "three-hive mechanics artifacts are present for residual/null analysis"
            if status == "pass"
            else "required three-hive mechanics artifacts are incomplete"
        ),
    }


def _source_ledger_row(run: dict[str, Any]) -> dict[str, str | int]:
    event_status = _event_ledger_status(run["events"])
    hive_status = _hive_ledger_status(run["source_ledger"])
    status = "pass" if event_status == "pass" and hive_status == "pass" else "fail_closed"
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "event_ledger_status": event_status,
        "hive_ledger_status": hive_status,
        "status": status,
        "interpretation": (
            "source ledgers reconstruct event and per-hive artifact deltas"
            if status == "pass"
            else "source ledger reconstruction failed; no three-hive interpretation is allowed"
        ),
    }


def _event_ledger_status(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "missing_events"
    for row in rows:
        for field in THREE_HIVE_RING_SOURCE_LEDGER_FIELDS:
            _float_cell(row.get(field))
        artifact_total = abs(_float_cell(row.get("source_ledger_artifact_delta")))
        component_total = sum(
            abs(_float_cell(row.get(field)))
            for field in (
                "source_ledger_artifact_readiness_delta",
                "source_ledger_artifact_coherence_delta",
                "source_ledger_artifact_contradiction_delta",
                "source_ledger_artifact_risk_delta",
            )
        )
        if abs(artifact_total - component_total) > _LEDGER_ROUNDING_TOLERANCE:
            return "fail_event_artifact_delta"
        if abs(_float_cell(row.get("source_ledger_clip_residual"))) > 1e-9:
            return "fail_clip_residual"
    return "pass"


def _hive_ledger_status(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "missing_source_ledger"
    for row in rows:
        for field in THREE_HIVE_RING_SOURCE_LEDGER_FIELDS:
            _float_cell(row.get(field))
        artifact_total = abs(_float_cell(row.get("source_ledger_artifact_delta")))
        component_total = sum(
            abs(_float_cell(row.get(field)))
            for field in (
                "source_ledger_artifact_readiness_delta",
                "source_ledger_artifact_coherence_delta",
                "source_ledger_artifact_contradiction_delta",
                "source_ledger_artifact_risk_delta",
            )
        )
        if abs(artifact_total - component_total) > _LEDGER_ROUNDING_TOLERANCE:
            return "fail_hive_artifact_delta"
        if abs(_float_cell(row.get("source_ledger_clip_residual"))) > 1e-9:
            return "fail_clip_residual"
    return "pass"


def _residual_metric_row(run: dict[str, Any], target_field: str) -> dict[str, Any]:
    metrics = run["metrics"]
    missing = _missing_residual_fields(metrics, target_field)
    base = {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "target_field": target_field,
        "row_count": len(metrics),
        "missing_required_fields": "|".join(missing),
        "control_fields_used": "|".join(_NUMERIC_CONTROLS),
        "residualization_status": "",
        "residual_variance": "",
        "lag1_autocorrelation": "",
        "nearest_neighbor_forecast_mae": "",
        "transition_compressibility_proxy": "",
        "status": "",
        "interpretation": "",
    }
    if missing:
        return {
            **base,
            "residualization_status": "missing_required_fields",
            "status": "missing_required_fields",
            "interpretation": "required three-hive target/control fields are absent",
        }
    values = [_float_cell(row.get(target_field)) for row in metrics]
    controls = [[_float_cell(row.get(field)) for field in _NUMERIC_CONTROLS] for row in metrics]
    residuals = _residualize(values, controls)
    forecast_mae = _nearest_neighbor_mae(residuals)
    return {
        **base,
        "residualization_status": "computed",
        "residual_variance": _round(_variance(residuals)),
        "lag1_autocorrelation": _round(_lag1_autocorrelation(residuals)),
        "nearest_neighbor_forecast_mae": _round(forecast_mae),
        "transition_compressibility_proxy": _round(1.0 / (1.0 + forecast_mae)),
        "status": "computed",
        "interpretation": "residual preflight metric computed; promotion requires all null, ledger, guardrail, and paired-seed gates",
    }


def _missing_residual_fields(metrics: list[dict[str, str]], target_field: str) -> list[str]:
    if not metrics:
        return sorted({target_field, *_NUMERIC_CONTROLS})
    fields = set(metrics[0])
    return sorted(({target_field} | set(_NUMERIC_CONTROLS)) - fields)


def _null_contrast_rows(residual_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {
        (str(row["condition"]), int(row["seed"]), str(row["target_field"])): row
        for row in residual_rows
    }
    seeds = sorted({int(row["seed"]) for row in residual_rows})
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        for target_field in _TARGET_FIELDS:
            positive = by_key.get((THREE_HIVE_RING_POSITIVE_CONDITION, seed, target_field))
            for control_condition in THREE_HIVE_RING_NULL_CONDITIONS:
                control = by_key.get((control_condition, seed, target_field))
                status = _paired_status(positive, control)
                gate_status = _gate_status(positive, control, status)
                rows.append(
                    {
                        "contrast": f"{THREE_HIVE_RING_POSITIVE_CONDITION}_vs_{control_condition}",
                        "seed": seed,
                        "control_condition": control_condition,
                        "target_field": target_field,
                        "paired": str(positive is not None and control is not None).lower(),
                        "status": status,
                        "positive_status": "" if positive is None else positive["status"],
                        "control_status": "" if control is None else control["status"],
                        "lag1_autocorrelation_delta": _metric_delta(positive, control, "lag1_autocorrelation"),
                        "nearest_neighbor_forecast_mae_delta": _metric_delta(positive, control, "nearest_neighbor_forecast_mae"),
                        "transition_compressibility_delta": _metric_delta(positive, control, "transition_compressibility_proxy"),
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
        return "fail_closed_no_residual_predictability_advantage"
    if _as_float(positive["transition_compressibility_proxy"]) <= _as_float(control["transition_compressibility_proxy"]):
        return "fail_closed_no_transition_compressibility_advantage"
    return "eligible_for_guardrail_and_cross_seed_review"


def _contrast_interpretation(gate_status: str) -> str:
    if gate_status == "missing_required_fields":
        return "required residualization fields are missing"
    if gate_status == "paired_seed_incomplete":
        return "paired three-hive condition/seed artifact is incomplete"
    if gate_status == "fail_closed_no_residual_autocorrelation_advantage":
        return "candidate does not beat the paired null on residual autocorrelation"
    if gate_status == "fail_closed_no_residual_predictability_advantage":
        return "candidate does not beat the paired null on residual predictability"
    if gate_status == "fail_closed_no_transition_compressibility_advantage":
        return "candidate does not beat the paired null on transition compressibility"
    return "computed analyzer row only; source ledgers, guardrails, and cross-seed agreement are still required"


def _guardrail_rows(
    runs: list[dict[str, Any]],
    source_ledger_rows: list[dict[str, str | int]],
) -> list[dict[str, Any]]:
    by_key = {(str(run["condition"]), int(run["seed"])): run for run in runs}
    source_status = {
        (str(row["condition"]), int(row["seed"])): str(row["status"])
        for row in source_ledger_rows
    }
    seeds = sorted({int(run["seed"]) for run in runs})
    return [
        _guardrail_row(
            seed,
            by_key.get((THREE_HIVE_RING_POSITIVE_CONDITION, seed)),
            by_key.get(("no_coupling", seed)),
            source_status.get((THREE_HIVE_RING_POSITIVE_CONDITION, seed), "missing"),
        )
        for seed in seeds
    ]


def _guardrail_row(
    seed: int,
    positive: dict[str, Any] | None,
    baseline: dict[str, Any] | None,
    source_status: str,
) -> dict[str, Any]:
    if positive is None or baseline is None:
        return {
            "seed": seed,
            "baseline_condition": "no_coupling",
            "completion_fraction_ratio": "",
            "backlog_ratio": "",
            "queued_age_ratio": "",
            "prediction_or_transfer_cost_fraction": "",
            "accepted_transfer_volume_min_per_directed_edge": "",
            "source_ledger_reconstruction_status": source_status,
            "status": "paired_seed_incomplete",
            "interpretation": "positive or no_coupling baseline artifact is incomplete",
        }
    positive_summary = _run_summary_stats(positive["metrics"], positive["events"])
    baseline_summary = _run_summary_stats(baseline["metrics"], baseline["events"])
    completion_ratio = _ratio(
        positive_summary["completion_fraction"],
        baseline_summary["completion_fraction"],
    )
    backlog_ratio = _ratio(positive_summary["backlog"], baseline_summary["backlog"])
    queued_age_ratio = _ratio(
        positive_summary["queued_age"],
        baseline_summary["queued_age"],
    )
    failures = []
    if completion_ratio < THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS["mean_completion_fraction_min_baseline_ratio"]:
        failures.append("completion_fraction")
    if backlog_ratio > THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS["mean_backlog_max_baseline_ratio"]:
        failures.append("backlog")
    if queued_age_ratio > THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS["mean_queued_age_max_baseline_ratio"]:
        failures.append("queued_age")
    if positive_summary["cost_fraction"] > THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS["prediction_or_transfer_cost_fraction_max"]:
        failures.append("prediction_or_transfer_cost_fraction")
    if positive_summary["min_edge_transfer"] < THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS["accepted_transfer_volume_min_per_directed_edge"]:
        failures.append("accepted_transfer_volume")
    if source_status != THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS["source_ledger_reconstruction_status_required"]:
        failures.append("source_ledger")
    return {
        "seed": seed,
        "baseline_condition": "no_coupling",
        "completion_fraction_ratio": _round(completion_ratio),
        "backlog_ratio": _round(backlog_ratio),
        "queued_age_ratio": _round(queued_age_ratio),
        "prediction_or_transfer_cost_fraction": _round(positive_summary["cost_fraction"]),
        "accepted_transfer_volume_min_per_directed_edge": _round(positive_summary["min_edge_transfer"]),
        "source_ledger_reconstruction_status": source_status,
        "status": "pass" if not failures else "fail_closed_" + "|".join(failures),
        "interpretation": (
            "productivity guardrails passed for the positive condition"
            if not failures
            else "candidate violates preregistered productivity guardrail(s): "
            + ", ".join(failures)
        ),
    }


def _run_summary_stats(metrics: list[dict[str, str]], events: list[dict[str, str]]) -> dict[str, float]:
    if not metrics:
        return {
            "completion_fraction": 0.0,
            "backlog": 0.0,
            "queued_age": 0.0,
            "cost_fraction": 0.0,
            "min_edge_transfer": 0.0,
        }
    cost = sum(
        _float_cell(row.get("local_prediction_spend")) + _float_cell(row.get("transfer_work_cost"))
        for row in metrics
    )
    work = sum(_float_cell(row.get("local_work_budget")) for row in metrics)
    by_edge: dict[str, float] = {}
    for row in events:
        edge_id = str(row.get("edge_id", ""))
        by_edge[edge_id] = by_edge.get(edge_id, 0.0) + _float_cell(row.get("accepted_transfer_volume"))
    return {
        "completion_fraction": _mean([_float_cell(row.get("completion_fraction")) for row in metrics]),
        "backlog": _mean([_float_cell(row.get("local_backlog")) for row in metrics]),
        "queued_age": _mean([_float_cell(row.get("local_queued_age")) for row in metrics]),
        "cost_fraction": cost / work if work > 0.0 else 0.0,
        "min_edge_transfer": min(by_edge.values()) if by_edge else 0.0,
    }


def _overall_status(
    completeness_rows: list[dict[str, str | int]],
    source_ledger_rows: list[dict[str, str | int]],
    residual_rows: list[dict[str, Any]],
    contrast_rows: list[dict[str, Any]],
    guardrail_rows: list[dict[str, Any]],
    conditions: list[str],
    seeds: list[int],
) -> str:
    if not completeness_rows:
        return "fail_closed_no_runs"
    if set(conditions) != set(THREE_HIVE_RING_CONDITIONS):
        return "fail_closed_missing_conditions"
    if tuple(seeds) != tuple(THREE_HIVE_RING_SMOKE_PARAMETERS["seeds"]):
        return "fail_closed_unregistered_seeds"
    if any(row["status"] != "pass" for row in completeness_rows):
        return "fail_closed_missing_schema_or_metrics_events"
    if any(row["status"] != "pass" for row in source_ledger_rows):
        return "fail_closed_source_ledger"
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


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _csv_header_and_row_count(path: Path) -> tuple[frozenset[str], int]:
    if not path.exists():
        return frozenset(), 0
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return frozenset(reader.fieldnames or ()), sum(1 for _ in reader)


def missing_fields(
    observed: set[str] | frozenset[str],
    required: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(field for field in required if field not in observed)


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


def _ratio(numerator: float, denominator: float) -> float:
    if abs(denominator) <= 1e-12:
        return 0.0 if abs(numerator) <= 1e-12 else float("inf")
    return numerator / denominator


def _float_cell(value: str | None) -> float:
    if value in {None, ""}:
        return 0.0
    return float(value)


def _as_float(value: Any) -> float:
    if value in {"", None}:
        return 0.0
    return float(value)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _round(value: float) -> float:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return 0.0
    return round(value, 6)


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[str(value)] = counts.get(str(value), 0) + 1
    return counts


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def _summary(
    compare_path: Path,
    completeness_rows: list[dict[str, str | int]],
    source_ledger_rows: list[dict[str, str | int]],
    residual_rows: list[dict[str, Any]],
    contrast_rows: list[dict[str, Any]],
    guardrail_rows: list[dict[str, Any]],
    manifest: dict[str, str | int],
) -> str:
    schema_pass = sum(1 for row in completeness_rows if row["status"] == "pass")
    ledger_statuses = _counts(row["status"] for row in source_ledger_rows)
    residual_statuses = _counts(row["status"] for row in residual_rows)
    gate_statuses = _counts(row["gate_status"] for row in contrast_rows)
    guardrail_statuses = _counts(row["status"] for row in guardrail_rows)
    return "\n".join(
        [
            "# Three-Hive Ring Residual/Null Analyzer",
            "",
            f"- Compare directory: `{compare_path}`",
            f"- Runs inspected: {manifest['run_count']}",
            f"- Status: `{manifest['status']}`",
            f"- Schema/metrics/events/source-ledger pass rows: {schema_pass}",
            f"- Source-ledger status: {_format_counts(ledger_statuses)}",
            f"- Residual row status: {_format_counts(residual_statuses)}",
            f"- Null-contrast gate status: {_format_counts(gate_statuses)}",
            f"- Productivity guardrail status: {_format_counts(guardrail_statuses)}",
            "",
            "This analyzer is read-only and consumes existing three-hive mechanics artifacts only.",
            "Positive interpretation remains blocked unless every preregistered null contrast,",
            "source-ledger reconstruction, productivity guardrail, and paired-seed direction gate",
            "passes without tuning.",
            "",
        ]
    )


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: tuple[str, ...],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _ensure_output_paths_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [name for name in _OUTPUT_NAMES if (output_path / name).exists()]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains artifacts: {names}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the fail-closed read-only three-hive ring residual/null analyzer."
    )
    parser.add_argument("--compare-dir", default=str(DEFAULT_THREE_HIVE_RING_MECHANICS_DIR))
    parser.add_argument("--out", default=str(DEFAULT_THREE_HIVE_RING_RESIDUAL_NULL_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_three_hive_ring_residual_null_analysis(args.compare_dir, args.out)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
