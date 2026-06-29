"""Read-only A7.3 long-horizon residual/recurrence analyzer."""

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
    A7_3_VALIDATION_PARAMETERS,
    A7_3_VALIDATION_RESIDUAL_CONTROLS,
    A7_3_VALIDATION_TARGET_FIELDS,
)
from ohdyn.analyze_a7_3_preflight import (
    A7_3_PREFLIGHT_STATUS_ELIGIBLE,
)
from ohdyn.compare_a7_3_dimensionless_delayed import DEFAULT_A7_3_VALIDATION_DIR


DEFAULT_A7_3_VALIDATION_PREFLIGHT_DIR = Path("runs/a7_3_validation_preflight_seed1_2")
DEFAULT_A7_3_RESIDUAL_RECURRENCE_DIR = Path(
    "runs/a7_3_residual_recurrence_validation_seed1_2"
)
A7_3_RECURRENCE_STATUS_FAIL_CLOSED = "fail_closed_no_a7_3_promotion"
A7_3_RECURRENCE_STATUS_PREFLIGHT_REQUIRED = "fail_closed_preflight_not_eligible"
A7_3_RECURRENCE_STATUS_MISSING_COVERAGE = "fail_closed_missing_condition_seed_coverage"
A7_3_RECURRENCE_STATUS_INSUFFICIENT_ROWS = "fail_closed_insufficient_rows"
A7_3_RECURRENCE_STATUS_PROMOTED = "promoted_all_preregistered_gates_passed"

A7_3_RECURRENCE_METRIC_FIELDS = (
    "condition",
    "seed",
    "target_field",
    "row_count",
    "train_rows",
    "holdout_rows",
    "preflight_status",
    "control_fields_used",
    "residualization_status",
    "missing_required_fields",
    "residual_variance",
    "lag1_autocorrelation",
    "heldout_ar_mae",
    "heldout_naive_mae",
    "heldout_residual_forecast_improvement",
    "embedding_lags",
    "recurrence_radius",
    "delay_embedding_recurrence_rate",
    "phase_surrogate_recurrence_mean",
    "phase_surrogate_recurrence_delta",
    "threshold_surrogate_recurrence_mean",
    "threshold_surrogate_recurrence_delta",
    "finite_time_local_divergence",
    "status",
    "interpretation",
)
A7_3_RECURRENCE_CONTRAST_FIELDS = (
    "seed",
    "target_field",
    "positive_condition",
    "null_condition",
    "paired",
    "positive_status",
    "null_status",
    "heldout_improvement_delta",
    "recurrence_rate_delta",
    "phase_surrogate_delta_delta",
    "threshold_surrogate_delta_delta",
    "local_divergence_delta",
    "gate_status",
    "interpretation",
)
A7_3_RECURRENCE_GATE_FIELDS = (
    "gate",
    "status",
    "detail",
)
A7_3_RECURRENCE_MANIFEST_FIELDS = (
    "compare_dir",
    "preflight_dir",
    "out_dir",
    "preflight_status",
    "condition_count",
    "seed_count",
    "run_count",
    "metric_rows",
    "contrast_rows",
    "gate_rows",
    "status",
)
_OUTPUT_NAMES = (
    "a7_3_residual_recurrence_metrics.csv",
    "a7_3_residual_recurrence_contrasts.csv",
    "a7_3_residual_recurrence_gates.csv",
    "a7_3_residual_recurrence_manifest.csv",
    "summary.md",
)
_MAX_PAIRWISE_VECTORS = 24


def run_a7_3_residual_recurrence_analysis(
    compare_dir: str | Path = DEFAULT_A7_3_VALIDATION_DIR,
    preflight_dir: str | Path = DEFAULT_A7_3_VALIDATION_PREFLIGHT_DIR,
    out_dir: str | Path = DEFAULT_A7_3_RESIDUAL_RECURRENCE_DIR,
) -> dict[str, Any]:
    """Analyze existing fixed A7.3 validation artifacts without rerunning them."""

    compare_path = Path(compare_dir)
    preflight_path = Path(preflight_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    preflight_status = _read_preflight_status(preflight_path)
    runs = _read_runs(compare_path)
    metric_rows = [
        _metric_row(run, target, preflight_status)
        for run in runs
        for target in A7_3_VALIDATION_TARGET_FIELDS
    ]
    contrast_rows = _contrast_rows(metric_rows)
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    gate_rows = _gate_rows(
        preflight_status,
        conditions,
        seeds,
        metric_rows,
        contrast_rows,
    )
    status = (
        A7_3_RECURRENCE_STATUS_PROMOTED
        if gate_rows and all(row["status"] == "pass" for row in gate_rows)
        else _fail_status(preflight_status, conditions, seeds, metric_rows)
    )
    manifest_row = {
        "compare_dir": str(compare_path),
        "preflight_dir": str(preflight_path),
        "out_dir": str(output_path),
        "preflight_status": preflight_status,
        "condition_count": len(conditions),
        "seed_count": len(seeds),
        "run_count": len(runs),
        "metric_rows": len(metric_rows),
        "contrast_rows": len(contrast_rows),
        "gate_rows": len(gate_rows),
        "status": status,
    }

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "a7_3_residual_recurrence_metrics.csv",
        metric_rows,
        A7_3_RECURRENCE_METRIC_FIELDS,
    )
    _write_csv(
        output_path / "a7_3_residual_recurrence_contrasts.csv",
        contrast_rows,
        A7_3_RECURRENCE_CONTRAST_FIELDS,
    )
    _write_csv(
        output_path / "a7_3_residual_recurrence_gates.csv",
        gate_rows,
        A7_3_RECURRENCE_GATE_FIELDS,
    )
    _write_csv(
        output_path / "a7_3_residual_recurrence_manifest.csv",
        [manifest_row],
        A7_3_RECURRENCE_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(compare_path, preflight_path, metric_rows, contrast_rows, gate_rows, manifest_row)
    )
    return {
        "compare_dir": str(compare_path),
        "preflight_dir": str(preflight_path),
        "out_dir": str(output_path),
        "run_count": len(runs),
        "metric_rows": len(metric_rows),
        "contrast_rows": len(contrast_rows),
        "gate_rows": len(gate_rows),
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
        raise FileNotFoundError(f"A7.3 validation directory does not exist: {compare_path}")
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


def _metric_row(
    run: dict[str, Any],
    target: str,
    preflight_status: str,
) -> dict[str, str | int | float]:
    rows = run["metrics"]
    missing_fields = _missing_fields(rows, target)
    values = [_float_cell(row.get(target)) for row in rows]
    control_fields = tuple(
        field for field in A7_3_VALIDATION_RESIDUAL_CONTROLS if field != target
    )
    residuals, residualization_status = _residualize(rows, values, control_fields)
    min_rows = int(A7_3_VALIDATION_PARAMETERS["minimum_rows_for_recurrence"])
    train_rows = int(len(residuals) * float(A7_3_VALIDATION_PARAMETERS["train_fraction"]))
    holdout_rows = max(0, len(residuals) - train_rows)
    if preflight_status != A7_3_PREFLIGHT_STATUS_ELIGIBLE:
        status = A7_3_RECURRENCE_STATUS_PREFLIGHT_REQUIRED
    elif missing_fields:
        status = A7_3_RECURRENCE_STATUS_FAIL_CLOSED
    elif len(residuals) < min_rows:
        status = A7_3_RECURRENCE_STATUS_INSUFFICIENT_ROWS
    else:
        status = A7_3_RECURRENCE_STATUS_FAIL_CLOSED
    recurrence_rate, radius = _recurrence_rate_and_radius(residuals)
    phase_mean = _phase_surrogate_recurrence_mean(residuals)
    threshold_mean = _threshold_surrogate_recurrence_mean(residuals)
    ar_mae, naive_mae = _heldout_forecast_mae(residuals)
    divergence = _local_divergence(residuals)
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "target_field": target,
        "row_count": len(residuals),
        "train_rows": train_rows,
        "holdout_rows": holdout_rows,
        "preflight_status": preflight_status,
        "control_fields_used": "|".join(control_fields),
        "residualization_status": residualization_status,
        "missing_required_fields": "|".join(missing_fields),
        "residual_variance": _round(_variance(residuals)),
        "lag1_autocorrelation": _round(_lag1_autocorrelation(residuals)),
        "heldout_ar_mae": _round(ar_mae),
        "heldout_naive_mae": _round(naive_mae),
        "heldout_residual_forecast_improvement": _round(naive_mae - ar_mae),
        "embedding_lags": "|".join(str(lag) for lag in A7_3_VALIDATION_PARAMETERS["embedding_lags"]),
        "recurrence_radius": _round(radius),
        "delay_embedding_recurrence_rate": _round(recurrence_rate),
        "phase_surrogate_recurrence_mean": _round(phase_mean),
        "phase_surrogate_recurrence_delta": _round(recurrence_rate - phase_mean),
        "threshold_surrogate_recurrence_mean": _round(threshold_mean),
        "threshold_surrogate_recurrence_delta": _round(recurrence_rate - threshold_mean),
        "finite_time_local_divergence": _round(divergence),
        "status": status,
        "interpretation": (
            "long-horizon rows computed read-only; promotion remains fail-closed unless all gates pass"
            if status == A7_3_RECURRENCE_STATUS_FAIL_CLOSED
            else "A7.3 recurrence analysis blocked by preregistered input gate"
        ),
    }


def _missing_fields(rows: list[dict[str, str]], target: str) -> list[str]:
    if not rows:
        return [target, *A7_3_VALIDATION_RESIDUAL_CONTROLS]
    header = set(rows[0])
    required = {target, *A7_3_VALIDATION_RESIDUAL_CONTROLS}
    return sorted(field for field in required if field not in header)


def _residualize(
    rows: list[dict[str, str]],
    values: list[float],
    control_fields: tuple[str, ...],
) -> tuple[list[float], str]:
    if not values:
        return [], "fail_missing_target"
    usable_controls = [
        field for field in control_fields if rows and field in rows[0]
    ]
    if not usable_controls:
        return _demean(values), "demeaned_no_controls"
    matrix = [
        [1.0, *[_float_cell(row.get(field)) for field in usable_controls]]
        for row in rows
    ]
    coefficients = _least_squares(matrix, values)
    if coefficients is None:
        return _demean(values), "demeaned_singular_controls"
    residuals = [
        y - sum(coef * x for coef, x in zip(coefficients, row))
        for y, row in zip(values, matrix)
    ]
    return residuals, "ols_controls"


def _least_squares(matrix: list[list[float]], values: list[float]) -> list[float] | None:
    if not matrix:
        return None
    cols = len(matrix[0])
    xtx = [[0.0 for _ in range(cols)] for _ in range(cols)]
    xty = [0.0 for _ in range(cols)]
    for row, y in zip(matrix, values):
        for i in range(cols):
            xty[i] += row[i] * y
            for j in range(cols):
                xtx[i][j] += row[i] * row[j]
    ridge = 1e-8
    for i in range(cols):
        xtx[i][i] += ridge
    return _solve_linear_system(xtx, xty)


def _solve_linear_system(matrix: list[list[float]], rhs: list[float]) -> list[float] | None:
    n = len(rhs)
    augmented = [row[:] + [rhs[index]] for index, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            return None
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        pivot_value = augmented[col][col]
        augmented[col] = [value / pivot_value for value in augmented[col]]
        for row_index in range(n):
            if row_index == col:
                continue
            factor = augmented[row_index][col]
            augmented[row_index] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(augmented[row_index], augmented[col])
            ]
    return [augmented[row][n] for row in range(n)]


def _heldout_forecast_mae(values: list[float]) -> tuple[float, float]:
    lags = tuple(int(lag) for lag in A7_3_VALIDATION_PARAMETERS["embedding_lags"])
    max_lag = max(lags)
    if len(values) <= max_lag + 4:
        return 0.0, 0.0
    split = int(len(values) * float(A7_3_VALIDATION_PARAMETERS["train_fraction"]))
    train_points = [
        ([1.0, *[values[index - lag] for lag in lags]], values[index])
        for index in range(max_lag, split)
    ]
    if not train_points:
        return 0.0, 0.0
    coefficients = _least_squares(
        [features for features, _ in train_points],
        [actual for _, actual in train_points],
    )
    if coefficients is None:
        coefficients = [0.0 for _ in train_points[0][0]]
    ar_errors: list[float] = []
    naive_errors: list[float] = []
    for index in range(max(max_lag, split), len(values)):
        features = [1.0, *[values[index - lag] for lag in lags]]
        prediction = sum(coef * feature for coef, feature in zip(coefficients, features))
        ar_errors.append(abs(values[index] - prediction))
        naive_errors.append(abs(values[index] - values[index - 1]))
    return _mean(ar_errors), _mean(naive_errors)


def _recurrence_rate_and_radius(values: list[float]) -> tuple[float, float]:
    lags = tuple(int(lag) for lag in A7_3_VALIDATION_PARAMETERS["embedding_lags"])
    vectors = _sample_vectors(_embedding_vectors(values, lags), _MAX_PAIRWISE_VECTORS)
    if len(vectors) < 3:
        return 0.0, 0.0
    distances: list[float] = []
    for left_index, left in enumerate(vectors):
        for right_index in range(left_index + 1, len(vectors)):
            if right_index - left_index <= max(lags):
                continue
            distances.append(_euclidean(left, vectors[right_index]))
    if not distances:
        return 0.0, 0.0
    radius = _quantile(distances, float(A7_3_VALIDATION_PARAMETERS["recurrence_radius_quantile"]))
    hits = sum(1 for distance in distances if distance <= radius)
    return hits / len(distances), radius


def _embedding_vectors(values: list[float], lags: tuple[int, ...]) -> list[tuple[float, ...]]:
    if len(values) <= max(lags):
        return []
    return [
        tuple(values[index - lag] for lag in lags)
        for index in range(max(lags), len(values))
    ]


def _phase_surrogate_recurrence_mean(values: list[float]) -> float:
    repetitions = int(A7_3_VALIDATION_PARAMETERS["surrogate_repetitions"])
    if not values or repetitions <= 0:
        return 0.0
    rates: list[float] = []
    for rep in range(repetitions):
        shift = 1 + ((rep * 17) % (len(values) - 1))
        shifted = values[shift:] + values[:shift]
        rate, _ = _recurrence_rate_and_radius(shifted)
        rates.append(rate)
    return _mean(rates)


def _threshold_surrogate_recurrence_mean(values: list[float]) -> float:
    repetitions = int(A7_3_VALIDATION_PARAMETERS["surrogate_repetitions"])
    if not values or repetitions <= 0:
        return 0.0
    ranked = sorted(values)
    rates: list[float] = []
    for rep in range(repetitions):
        stride = 3 + (rep % 7)
        permuted = [ranked[(index * stride + rep) % len(ranked)] for index in range(len(values))]
        rate, _ = _recurrence_rate_and_radius(permuted)
        rates.append(rate)
    return _mean(rates)


def _local_divergence(values: list[float]) -> float:
    lags = tuple(int(lag) for lag in A7_3_VALIDATION_PARAMETERS["embedding_lags"])
    vectors = _sample_vectors(_embedding_vectors(values, lags), _MAX_PAIRWISE_VECTORS)
    horizon = max(lags)
    if len(vectors) <= horizon + 2:
        return 0.0
    neighbor_count = int(A7_3_VALIDATION_PARAMETERS["local_divergence_neighbor_count"])
    ratios: list[float] = []
    for index, vector in enumerate(vectors[:-horizon]):
        candidates = [
            (_euclidean(vector, other), other_index)
            for other_index, other in enumerate(vectors[:-horizon])
            if abs(other_index - index) > horizon
        ]
        for initial_distance, other_index in sorted(candidates)[:neighbor_count]:
            if initial_distance <= 1e-12:
                continue
            future_distance = _euclidean(vectors[index + horizon], vectors[other_index + horizon])
            ratios.append(math.log((future_distance + 1e-12) / initial_distance))
    return _mean(ratios)


def _sample_vectors(
    vectors: list[tuple[float, ...]],
    maximum: int,
) -> list[tuple[float, ...]]:
    if len(vectors) <= maximum:
        return vectors
    stride = (len(vectors) - 1) / (maximum - 1)
    return [vectors[int(round(index * stride))] for index in range(maximum)]


def _contrast_rows(
    metric_rows: list[dict[str, str | int | float]],
) -> list[dict[str, str | int | float]]:
    by_key = {
        (str(row["condition"]), int(row["seed"]), str(row["target_field"])): row
        for row in metric_rows
    }
    rows: list[dict[str, str | int | float]] = []
    for seed in A7_3_VALIDATION_PARAMETERS["seeds"]:
        for target in A7_3_VALIDATION_TARGET_FIELDS:
            positive = by_key.get((A7_3_POSITIVE_CONDITION, int(seed), target))
            for null in A7_3_NULL_CONDITIONS:
                control = by_key.get((null, int(seed), target))
                paired = positive is not None and control is not None
                gate_status = (
                    "pass"
                    if paired and _beats_null(positive, control, null)
                    else "fail_closed"
                )
                rows.append(
                    {
                        "seed": int(seed),
                        "target_field": target,
                        "positive_condition": A7_3_POSITIVE_CONDITION,
                        "null_condition": null,
                        "paired": paired,
                        "positive_status": str(positive["status"]) if positive else "missing_positive",
                        "null_status": str(control["status"]) if control else "missing_null",
                        "heldout_improvement_delta": _round(
                            _metric_delta(positive, control, "heldout_residual_forecast_improvement")
                        ),
                        "recurrence_rate_delta": _round(
                            _metric_delta(positive, control, "delay_embedding_recurrence_rate")
                        ),
                        "phase_surrogate_delta_delta": _round(
                            _metric_delta(positive, control, "phase_surrogate_recurrence_delta")
                        ),
                        "threshold_surrogate_delta_delta": _round(
                            _metric_delta(positive, control, "threshold_surrogate_recurrence_delta")
                        ),
                        "local_divergence_delta": _round(
                            _metric_delta(positive, control, "finite_time_local_divergence")
                        ),
                        "gate_status": gate_status,
                        "interpretation": (
                            "full delayed logistic passed this preregistered paired contrast"
                            if gate_status == "pass"
                            else "paired null contrast failed closed; no A7.3 promotion claim is allowed"
                        ),
                    }
                )
    return rows


def _beats_null(
    positive: dict[str, str | int | float] | None,
    control: dict[str, str | int | float] | None,
    null_condition: str,
) -> bool:
    if positive is None or control is None:
        return False
    if str(positive["status"]) != A7_3_RECURRENCE_STATUS_FAIL_CLOSED:
        return False
    if str(control["status"]) != A7_3_RECURRENCE_STATUS_FAIL_CLOSED:
        return False
    improvement_ok = (
        float(positive["heldout_residual_forecast_improvement"])
        > float(control["heldout_residual_forecast_improvement"])
    )
    recurrence_ok = (
        float(positive["delay_embedding_recurrence_rate"])
        > float(control["delay_embedding_recurrence_rate"])
    )
    surrogate_ok = (
        float(positive["phase_surrogate_recurrence_delta"]) > 0.0
        and float(positive["threshold_surrogate_recurrence_delta"]) > 0.0
    )
    divergence_ok = True
    if null_condition == "low_gain_contraction":
        divergence_ok = (
            float(positive["finite_time_local_divergence"])
            > float(control["finite_time_local_divergence"])
        )
    return improvement_ok and recurrence_ok and surrogate_ok and divergence_ok


def _gate_rows(
    preflight_status: str,
    conditions: list[str],
    seeds: list[int],
    metric_rows: list[dict[str, str | int | float]],
    contrast_rows: list[dict[str, str | int | float]],
) -> list[dict[str, str]]:
    rows = [
        _gate(
            "preflight_manifest_status_eligible",
            preflight_status == A7_3_PREFLIGHT_STATUS_ELIGIBLE,
            preflight_status,
        ),
        _gate(
            "all_conditions_and_seeds_present",
            set(conditions) == set(A7_3_CONDITIONS)
            and set(seeds) == {int(seed) for seed in A7_3_VALIDATION_PARAMETERS["seeds"]},
            f"conditions={len(conditions)} seeds={len(seeds)}",
        ),
        _gate(
            "minimum_rows_for_recurrence",
            bool(metric_rows)
            and all(
                int(row["row_count"])
                >= int(A7_3_VALIDATION_PARAMETERS["minimum_rows_for_recurrence"])
                for row in metric_rows
            ),
            f"minimum={A7_3_VALIDATION_PARAMETERS['minimum_rows_for_recurrence']}",
        ),
    ]
    for null in A7_3_NULL_CONDITIONS:
        null_rows = [row for row in contrast_rows if row["null_condition"] == null]
        rows.append(
            _gate(
                f"full_mechanism_beats_{null}",
                bool(null_rows) and all(row["gate_status"] == "pass" for row in null_rows),
                f"passed={sum(row['gate_status'] == 'pass' for row in null_rows)}/{len(null_rows)}",
            )
        )
    low_gain_rows = [
        row
        for row in contrast_rows
        if row["null_condition"] == "low_gain_contraction"
    ]
    rows.append(
        _gate(
            "finite_time_divergence_exceeds_low_gain_baseline",
            bool(low_gain_rows)
            and all(float(row["local_divergence_delta"]) > 0.0 for row in low_gain_rows),
            f"positive_delta={sum(float(row['local_divergence_delta']) > 0.0 for row in low_gain_rows)}/{len(low_gain_rows)}",
        )
    )
    return rows


def _gate(name: str, passed: bool, detail: str) -> dict[str, str]:
    return {"gate": name, "status": "pass" if passed else "fail_closed", "detail": detail}


def _fail_status(
    preflight_status: str,
    conditions: list[str],
    seeds: list[int],
    metric_rows: list[dict[str, str | int | float]],
) -> str:
    if preflight_status != A7_3_PREFLIGHT_STATUS_ELIGIBLE:
        return A7_3_RECURRENCE_STATUS_PREFLIGHT_REQUIRED
    if set(conditions) != set(A7_3_CONDITIONS) or set(seeds) != {
        int(seed) for seed in A7_3_VALIDATION_PARAMETERS["seeds"]
    }:
        return A7_3_RECURRENCE_STATUS_MISSING_COVERAGE
    if any(
        int(row["row_count"]) < int(A7_3_VALIDATION_PARAMETERS["minimum_rows_for_recurrence"])
        for row in metric_rows
    ):
        return A7_3_RECURRENCE_STATUS_INSUFFICIENT_ROWS
    return A7_3_RECURRENCE_STATUS_FAIL_CLOSED


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
    return numerator / denominator if denominator else 0.0


def _quantile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * quantile))))
    return ordered[index]


def _euclidean(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _float_cell(value: str | None) -> float:
    if value in {None, ""}:
        return 0.0
    return float(value)


def _round(value: float) -> float:
    return round(value, 6)


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


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
                f"Output path {output_path} already contains A7.3 recurrence artifacts."
            )


def _summary(
    compare_path: Path,
    preflight_path: Path,
    metric_rows: list[dict[str, str | int | float]],
    contrast_rows: list[dict[str, str | int | float]],
    gate_rows: list[dict[str, str]],
    manifest_row: dict[str, str | int],
) -> str:
    passed_gates = sum(row["status"] == "pass" for row in gate_rows)
    return "\n".join(
        [
            "# A7.3 Residual/Recurrence Validation",
            "",
            f"- Compare dir: `{compare_path}`",
            f"- Preflight dir: `{preflight_path}`",
            f"- Residual/recurrence rows: {len(metric_rows)}",
            f"- Null contrast rows: {len(contrast_rows)}",
            f"- Gate rows: {len(gate_rows)} ({passed_gates} pass)",
            f"- Status: `{manifest_row['status']}`",
            "",
            "This analyzer is read-only over fixed 256-tick A7.3 validation artifacts.",
            "It does not rerun simulations, tune parameters, infer missing ledgers, or repair artifacts.",
            "Promotion is fail-closed unless every preregistered preflight, null, surrogate,",
            "forecast, productivity/source-ledger, and divergence gate passes.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only residual/recurrence analyzer for A7.3 validation artifacts."
    )
    parser.add_argument(
        "--compare-dir",
        default=str(DEFAULT_A7_3_VALIDATION_DIR),
        help="Existing fixed A7.3 validation artifact directory.",
    )
    parser.add_argument(
        "--preflight-dir",
        default=str(DEFAULT_A7_3_VALIDATION_PREFLIGHT_DIR),
        help="Existing eligible A7.3 preflight artifact directory.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A7_3_RESIDUAL_RECURRENCE_DIR),
        help="Output directory for read-only A7.3 residual/recurrence artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_a7_3_residual_recurrence_analysis(
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
