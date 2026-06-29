"""Read-only A7.3 residual-analysis skeleton.

This module intentionally emits smoke-scale diagnostics only. It requires an
eligible A7.3 preflight manifest and never promotes a scientific result.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import yaml

from ohdyn.a7_3_dimensionless_contract import (
    A7_3_CONDITIONS,
    A7_3_NULL_CONDITIONS,
    A7_3_POSITIVE_CONDITION,
    A7_3_SMOKE_PARAMETERS,
)
from ohdyn.analyze_a7_3_preflight import (
    A7_3_PREFLIGHT_STATUS_ELIGIBLE,
    DEFAULT_A7_3_PREFLIGHT_DIR,
)
from ohdyn.compare_a7_3_dimensionless_delayed import DEFAULT_A7_3_SMOKE_DIR


DEFAULT_A7_3_RESIDUAL_DIR = Path("runs/a7_3_residual_skeleton_seed1_2")
A7_3_RESIDUAL_STATUS_SMOKE_SCALE = "fail_closed_smoke_scale_no_promotion"
A7_3_RESIDUAL_STATUS_PREFLIGHT_REQUIRED = "fail_closed_preflight_not_eligible"
A7_3_RESIDUAL_STATUS_MISSING_COVERAGE = "fail_closed_missing_condition_seed_coverage"

A7_3_RESIDUAL_TARGET_FIELDS = (
    "artifact_readiness",
    "artifact_coherence",
    "contradiction_risk",
    "prediction_error",
    "prediction_uncertainty",
    "fatigue",
    "memory_pressure",
    "work_backlog",
)
A7_3_RESIDUAL_CONTROL_FIELDS = (
    "demand_phase",
    "task_arrivals",
    "service_capacity",
    "action_opportunity",
    "work_budget",
    "work_backlog",
    "queued_age",
    "completion_fraction",
    "prediction_spend",
    "lost_work_opportunity_from_prediction",
    "memory_pressure",
)
A7_3_RESIDUAL_METRIC_FIELDS = (
    "condition",
    "seed",
    "target_field",
    "row_count",
    "preflight_status",
    "control_fields_used",
    "residual_variance",
    "lag1_autocorrelation",
    "delay_embedded_recurrence_rate",
    "linear_ar_forecast_mae",
    "naive_forecast_mae",
    "status",
    "interpretation",
)
A7_3_RESIDUAL_CONTRAST_FIELDS = (
    "seed",
    "target_field",
    "positive_condition",
    "null_condition",
    "paired",
    "positive_status",
    "null_status",
    "residual_variance_delta",
    "recurrence_rate_delta",
    "linear_ar_forecast_mae_delta",
    "gate_status",
    "interpretation",
)
A7_3_RESIDUAL_MANIFEST_FIELDS = (
    "compare_dir",
    "preflight_dir",
    "out_dir",
    "preflight_status",
    "condition_count",
    "seed_count",
    "run_count",
    "residual_metric_rows",
    "null_contrast_rows",
    "status",
)
_OUTPUT_NAMES = (
    "a7_3_residual_skeleton_metrics.csv",
    "a7_3_residual_skeleton_contrasts.csv",
    "a7_3_residual_skeleton_manifest.csv",
    "summary.md",
)
_MIN_ROWS_FOR_RECURRENCE = 96


def run_a7_3_residual_skeleton_analysis(
    compare_dir: str | Path = DEFAULT_A7_3_SMOKE_DIR,
    preflight_dir: str | Path = DEFAULT_A7_3_PREFLIGHT_DIR,
    out_dir: str | Path = DEFAULT_A7_3_RESIDUAL_DIR,
) -> dict[str, Any]:
    """Emit conservative residual skeleton artifacts over existing A7.3 smoke output."""

    compare_path = Path(compare_dir)
    preflight_path = Path(preflight_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    preflight_status = _read_preflight_status(preflight_path)
    runs = _read_runs(compare_path)
    residual_rows = [
        _residual_row(run, target, preflight_status)
        for run in runs
        for target in A7_3_RESIDUAL_TARGET_FIELDS
    ]
    contrast_rows = _contrast_rows(residual_rows)
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    status = _overall_status(preflight_status, conditions, seeds, residual_rows)
    manifest_row = {
        "compare_dir": str(compare_path),
        "preflight_dir": str(preflight_path),
        "out_dir": str(output_path),
        "preflight_status": preflight_status,
        "condition_count": len(conditions),
        "seed_count": len(seeds),
        "run_count": len(runs),
        "residual_metric_rows": len(residual_rows),
        "null_contrast_rows": len(contrast_rows),
        "status": status,
    }

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "a7_3_residual_skeleton_metrics.csv",
        residual_rows,
        A7_3_RESIDUAL_METRIC_FIELDS,
    )
    _write_csv(
        output_path / "a7_3_residual_skeleton_contrasts.csv",
        contrast_rows,
        A7_3_RESIDUAL_CONTRAST_FIELDS,
    )
    _write_csv(
        output_path / "a7_3_residual_skeleton_manifest.csv",
        [manifest_row],
        A7_3_RESIDUAL_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(compare_path, preflight_path, residual_rows, contrast_rows, manifest_row)
    )
    return {
        "compare_dir": str(compare_path),
        "preflight_dir": str(preflight_path),
        "out_dir": str(output_path),
        "run_count": len(runs),
        "residual_metric_rows": len(residual_rows),
        "null_contrast_rows": len(contrast_rows),
        "status": status,
    }


def _read_preflight_status(preflight_path: Path) -> str:
    manifest_path = preflight_path / "a7_3_preflight_manifest.csv"
    if not manifest_path.exists():
        return "missing_preflight_manifest"
    rows = _read_csv_rows(manifest_path)
    if not rows:
        return "missing_preflight_manifest"
    return rows[0].get("status") or "missing_preflight_status"


def _read_runs(compare_path: Path) -> list[dict[str, Any]]:
    if not compare_path.exists():
        raise FileNotFoundError(f"A7.3 smoke directory does not exist: {compare_path}")
    runs: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        manifest = _read_manifest(run_dir / "manifest.yaml")
        condition = str(manifest.get("condition") or _condition_from_name(run_dir.name))
        seed = int(manifest.get("seed", _seed_from_name(run_dir.name)))
        metrics = _read_csv_rows(run_dir / "metrics.csv")
        if metrics:
            runs.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "run_dir": run_dir,
                    "metrics": metrics,
                }
            )
    return runs


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def _condition_from_name(name: str) -> str:
    for condition in A7_3_CONDITIONS:
        if name.startswith(condition):
            return condition
    return name.rsplit("_seed", 1)[0]


def _seed_from_name(name: str) -> int:
    if "_seed" not in name:
        return 0
    suffix = name.rsplit("_seed", 1)[1]
    digits = "".join(char for char in suffix if char.isdigit())
    return int(digits) if digits else 0


def _residual_row(
    run: dict[str, Any],
    target: str,
    preflight_status: str,
) -> dict[str, str | int | float]:
    values = [_float_cell(row.get(target)) for row in run["metrics"]]
    residuals = _demean(values)
    row_count = len(values)
    residual_variance = _variance(residuals)
    status = (
        A7_3_RESIDUAL_STATUS_SMOKE_SCALE
        if preflight_status == A7_3_PREFLIGHT_STATUS_ELIGIBLE
        else A7_3_RESIDUAL_STATUS_PREFLIGHT_REQUIRED
    )
    recurrence_status = (
        _recurrence_rate(residuals)
        if row_count >= _MIN_ROWS_FOR_RECURRENCE
        else 0.0
    )
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "target_field": target,
        "row_count": row_count,
        "preflight_status": preflight_status,
        "control_fields_used": "|".join(A7_3_RESIDUAL_CONTROL_FIELDS),
        "residual_variance": _round(residual_variance),
        "lag1_autocorrelation": _round(_lag1_autocorrelation(residuals)),
        "delay_embedded_recurrence_rate": _round(recurrence_status),
        "linear_ar_forecast_mae": _round(_linear_ar_forecast_mae(residuals)),
        "naive_forecast_mae": _round(_naive_forecast_mae(residuals)),
        "status": status,
        "interpretation": (
            "smoke-scale residual skeleton only; horizon is below the preregistered recurrence gate"
            if preflight_status == A7_3_PREFLIGHT_STATUS_ELIGIBLE
            else "A7.3 residual analysis is blocked until preflight is eligible"
        ),
    }


def _contrast_rows(
    residual_rows: list[dict[str, str | int | float]],
) -> list[dict[str, str | int | float]]:
    by_key = {
        (str(row["condition"]), int(row["seed"]), str(row["target_field"])): row
        for row in residual_rows
    }
    rows: list[dict[str, str | int | float]] = []
    for seed in A7_3_SMOKE_PARAMETERS["seeds"]:
        for target in A7_3_RESIDUAL_TARGET_FIELDS:
            positive = by_key.get((A7_3_POSITIVE_CONDITION, int(seed), target))
            for null in A7_3_NULL_CONDITIONS:
                control = by_key.get((null, int(seed), target))
                paired = positive is not None and control is not None
                positive_status = str(positive["status"]) if positive else "missing_positive"
                null_status = str(control["status"]) if control else "missing_null"
                status = (
                    A7_3_RESIDUAL_STATUS_SMOKE_SCALE
                    if paired
                    and positive_status == A7_3_RESIDUAL_STATUS_SMOKE_SCALE
                    and null_status == A7_3_RESIDUAL_STATUS_SMOKE_SCALE
                    else A7_3_RESIDUAL_STATUS_PREFLIGHT_REQUIRED
                )
                rows.append(
                    {
                        "seed": int(seed),
                        "target_field": target,
                        "positive_condition": A7_3_POSITIVE_CONDITION,
                        "null_condition": null,
                        "paired": paired,
                        "positive_status": positive_status,
                        "null_status": null_status,
                        "residual_variance_delta": _round(
                            _metric_delta(positive, control, "residual_variance")
                        ),
                        "recurrence_rate_delta": _round(
                            _metric_delta(positive, control, "delay_embedded_recurrence_rate")
                        ),
                        "linear_ar_forecast_mae_delta": _round(
                            _metric_delta(positive, control, "linear_ar_forecast_mae")
                        ),
                        "gate_status": status,
                        "interpretation": (
                            "null contrast is recorded for future analyzer wiring only; no A7.3 promotion is allowed"
                            if paired
                            else "null contrast is incomplete and fail-closed"
                        ),
                    }
                )
    return rows


def _overall_status(
    preflight_status: str,
    conditions: list[str],
    seeds: list[int],
    residual_rows: list[dict[str, str | int | float]],
) -> str:
    expected_conditions = set(A7_3_CONDITIONS)
    expected_seeds = {int(seed) for seed in A7_3_SMOKE_PARAMETERS["seeds"]}
    if set(conditions) != expected_conditions or set(seeds) != expected_seeds:
        return A7_3_RESIDUAL_STATUS_MISSING_COVERAGE
    if preflight_status != A7_3_PREFLIGHT_STATUS_ELIGIBLE:
        return A7_3_RESIDUAL_STATUS_PREFLIGHT_REQUIRED
    if not residual_rows:
        return A7_3_RESIDUAL_STATUS_MISSING_COVERAGE
    return A7_3_RESIDUAL_STATUS_SMOKE_SCALE


def _metric_delta(
    positive: dict[str, str | int | float] | None,
    control: dict[str, str | int | float] | None,
    field: str,
) -> float:
    if positive is None or control is None:
        return 0.0
    return float(positive[field]) - float(control[field])


def _demean(values: list[float]) -> list[float]:
    if not values:
        return []
    mean = sum(values) / len(values)
    return [value - mean for value in values]


def _variance(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / len(values)


def _lag1_autocorrelation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    left = values[:-1]
    right = values[1:]
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_var = sum((a - left_mean) ** 2 for a in left)
    right_var = sum((b - right_mean) ** 2 for b in right)
    denominator = math.sqrt(left_var * right_var)
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def _recurrence_rate(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    radius = math.sqrt(_variance(values)) * 0.15
    if radius == 0.0:
        return 0.0
    pairs = [(values[index], values[index + 1]) for index in range(len(values) - 1)]
    comparisons = 0
    hits = 0
    for left_index, left in enumerate(pairs):
        for right_index, right in enumerate(pairs):
            if abs(left_index - right_index) <= 1:
                continue
            comparisons += 1
            distance = math.sqrt((left[0] - right[0]) ** 2 + (left[1] - right[1]) ** 2)
            if distance <= radius:
                hits += 1
    return hits / comparisons if comparisons else 0.0


def _linear_ar_forecast_mae(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    lag = values[:-1]
    current = values[1:]
    denominator = sum(value * value for value in lag)
    coefficient = sum(a * b for a, b in zip(lag, current)) / denominator if denominator else 0.0
    errors = [abs(actual - coefficient * previous) for previous, actual in zip(lag, current)]
    return sum(errors) / len(errors)


def _naive_forecast_mae(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    errors = [abs(actual - previous) for previous, actual in zip(values[:-1], values[1:])]
    return sum(errors) / len(errors)


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _float_cell(value: str | None) -> float:
    if value in {None, ""}:
        return 0.0
    return float(value)


def _round(value: float) -> float:
    return round(value, 6)


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
    for name in _OUTPUT_NAMES:
        if (output_path / name).exists():
            raise FileExistsError(
                f"Output path {output_path} already contains A7.3 residual skeleton artifacts."
            )


def _summary(
    compare_path: Path,
    preflight_path: Path,
    residual_rows: list[dict[str, str | int | float]],
    contrast_rows: list[dict[str, str | int | float]],
    manifest_row: dict[str, str | int],
) -> str:
    return "\n".join(
        [
            "# A7.3 Residual Skeleton",
            "",
            f"- Compare dir: `{compare_path}`",
            f"- Preflight dir: `{preflight_path}`",
            f"- Residual rows: {len(residual_rows)}",
            f"- Null contrast rows: {len(contrast_rows)}",
            f"- Status: `{manifest_row['status']}`",
            "",
            "This analyzer is read-only and gated by the A7.3 preflight manifest.",
            "It records smoke-scale residual/null wiring only. The 64-tick smoke horizon",
            "is below the preregistered recurrence gate, so no promotion endpoint,",
            "scientific interpretation, sweep, or strange-attractor-like claim is allowed.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only residual skeleton analyzer for A7.3 smoke artifacts."
    )
    parser.add_argument(
        "--compare-dir",
        default=str(DEFAULT_A7_3_SMOKE_DIR),
        help="Existing A7.3 smoke artifact directory.",
    )
    parser.add_argument(
        "--preflight-dir",
        default=str(DEFAULT_A7_3_PREFLIGHT_DIR),
        help="Existing eligible A7.3 preflight artifact directory.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A7_3_RESIDUAL_DIR),
        help="Output directory for read-only A7.3 residual skeleton artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_a7_3_residual_skeleton_analysis(
            compare_dir=args.compare_dir,
            preflight_dir=args.preflight_dir,
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    print(yaml.safe_dump(result, sort_keys=True), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
