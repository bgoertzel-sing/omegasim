"""Read A5 predictive-control artifacts and emit residual accounting endpoints."""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import random
import zlib
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ohdyn.config import ATTENTION_CLASSES


DEFAULT_A5_COMPARE_DIR = Path("runs/a5_predictive_control_compare")
DEFAULT_A5_RESIDUAL_OUT_DIR = Path("runs/a5_residual_accounting")
DEFAULT_A5_PERMUTATION_REPS = 512
DEFAULT_A5_PERMUTATION_SEED = 5505
A5_REQUIRED_CONDITIONS = (
    "reactive",
    "linear",
    "nonlinear",
    "oracle",
    "shuffled",
    "nonlinear_shuffled",
)
A5_INTERMEDIATE_CONDITIONS = ("linear", "nonlinear")
A5_TIMING_BROKEN_NULL_BY_CONDITION = {
    "linear": "shuffled",
    "nonlinear": "nonlinear_shuffled",
}
A5_CONFIRMATORY_GUARDRAIL_TOLERANCES = {
    "completion_fraction_final": 0.01,
    "queue_depth_final": 1.0,
    "queued_age_final": 0.5,
    "attention_completed_total": 1.0,
    "capture_pressure_peak": 0.05,
}
A5_CONTROL_LEVELS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("raw", (), "uncontrolled observed trajectories"),
    (
        "clock_demand",
        (
            "tick",
            "tick_squared",
            *(
                f"a5_{class_name}_demand_share_tick"
                for class_name in ATTENTION_CLASSES
            ),
            *(
                f"a5_{class_name}_future_demand_share_tick"
                for class_name in ATTENTION_CLASSES
            ),
        ),
        "tick, tick squared, current demand shares, and future demand shares",
    ),
    (
        "load_opportunity",
        (
            "tick",
            "tick_squared",
            *(
                f"a5_{class_name}_demand_share_tick"
                for class_name in ATTENTION_CLASSES
            ),
            *(
                f"a5_{class_name}_future_demand_share_tick"
                for class_name in ATTENTION_CLASSES
            ),
            "queue_depth",
            "queued_task_age_mean_tick",
            "queued_task_age_max_tick",
            "tasks_created_total",
            "tasks_completed_total",
            "tasks_created_tick",
            "tasks_completed_tick",
            "idle_tick",
            "messages_sent_tick",
            "agent_tasks_created_tick",
            "tasks_worked_tick",
        ),
        "clock, demand, backlog, age, task-flow, and action-opportunity fields",
    ),
    (
        "full_accounting",
        (
            "tick",
            "tick_squared",
            *(
                f"a5_{class_name}_demand_share_tick"
                for class_name in ATTENTION_CLASSES
            ),
            *(
                f"a5_{class_name}_future_demand_share_tick"
                for class_name in ATTENTION_CLASSES
            ),
            "queue_depth",
            "queued_task_age_mean_tick",
            "queued_task_age_max_tick",
            "tasks_created_total",
            "tasks_completed_total",
            "tasks_created_tick",
            "tasks_completed_tick",
            "idle_tick",
            "messages_sent_tick",
            "agent_tasks_created_tick",
            "tasks_worked_tick",
            "attention_capture_pressure_max_tick",
            *(
                f"attention_{class_name}_completed_total"
                for class_name in ATTENTION_CLASSES
            ),
            *(
                f"attention_{class_name}_worked_total"
                for class_name in ATTENTION_CLASSES
            ),
        ),
        "clock, demand, load, action opportunity, capture pressure, and class work accounting",
    ),
)
A5_RESIDUAL_ACCOUNTING_METRIC_FIELDS = (
    "condition",
    "seed",
    "control_level",
    "endpoint",
    "value",
)
A5_RESIDUAL_ACCOUNTING_EFFECT_FIELDS = (
    "contrast",
    "control_level",
    "endpoint",
    "high_condition",
    "low_condition",
    "paired_seed_count",
    "high_mean",
    "low_mean",
    "mean_delta",
    "positive_delta_rate",
    "label_permutation_ci_low",
    "label_permutation_ci_high",
    "outside_label_permutation_ci",
    "interpretation",
)
A5_RESIDUAL_ACCOUNTING_MANIFEST_FIELDS = (
    "control_level",
    "covariates",
    "description",
    "compare_dir",
    "condition_count",
    "seed_count",
)
_A5_GUARDRAIL_POLICY = (
    "Preregistered confirmatory guardrails versus reactive under matched "
    "seeds: completion fraction may not drop by more than 0.01, final queue "
    "depth may not rise by more than 1.0 task, final queued mean age may not "
    "rise by more than 0.5 tick, no attention class may lose more than one "
    "completed task, and peak capture pressure may not rise by more than "
    "0.05. Fresh confirmatory A5 runs must compare each predictor against a "
    "timing-broken null with the same prediction budget."
)
_OUTPUT_NAMES = (
    "a5_residual_accounting_metrics.csv",
    "a5_residual_accounting_effects.csv",
    "a5_residual_accounting_manifest.csv",
    "summary.md",
)
_STRUCTURE_FIELDS = (
    *(
        f"a5_{class_name}_forecast_error_tick"
        for class_name in ATTENTION_CLASSES
    ),
    *(
        f"a5_{class_name}_allocation_future_residual_tick"
        for class_name in ATTENTION_CLASSES
    ),
    "queue_depth",
    "queued_task_age_mean_tick",
    "attention_capture_pressure_max_tick",
    "completion_fraction_tick",
)


def run_a5_residual_accounting_analysis(
    *,
    compare_dir: str | Path = DEFAULT_A5_COMPARE_DIR,
    out_dir: str | Path = DEFAULT_A5_RESIDUAL_OUT_DIR,
    permutation_reps: int = DEFAULT_A5_PERMUTATION_REPS,
    permutation_seed: int = DEFAULT_A5_PERMUTATION_SEED,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Analyze an existing A5 comparison directory without running simulations."""

    _validate_permutation_options(permutation_reps, permutation_seed)
    source_path = Path(compare_dir)
    output_path = Path(out_dir)
    run_index = _validate_source(source_path)
    _ensure_outputs_available(output_path, overwrite=overwrite)
    output_path.mkdir(parents=True, exist_ok=True)

    metric_rows: list[dict[str, Any]] = []
    for condition in A5_REQUIRED_CONDITIONS:
        for seed, run_path in sorted(run_index[condition].items()):
            metrics = _read_metrics(run_path / "metrics.csv")
            metric_rows.extend(_endpoint_rows(condition, seed, metrics))

    effect_rows = _effect_rows(
        metric_rows,
        permutation_reps=permutation_reps,
        permutation_seed=permutation_seed,
    )
    manifest_rows = [
        {
            "control_level": name,
            "covariates": "|".join(covariates) if covariates else "none",
            "description": description,
            "compare_dir": str(source_path),
            "condition_count": len(A5_REQUIRED_CONDITIONS),
            "seed_count": len(next(iter(run_index.values()))),
        }
        for name, covariates, description in A5_CONTROL_LEVELS
    ]
    _write_csv(
        output_path / "a5_residual_accounting_metrics.csv",
        A5_RESIDUAL_ACCOUNTING_METRIC_FIELDS,
        metric_rows,
    )
    _write_csv(
        output_path / "a5_residual_accounting_effects.csv",
        A5_RESIDUAL_ACCOUNTING_EFFECT_FIELDS,
        effect_rows,
    )
    _write_csv(
        output_path / "a5_residual_accounting_manifest.csv",
        A5_RESIDUAL_ACCOUNTING_MANIFEST_FIELDS,
        manifest_rows,
    )
    (output_path / "summary.md").write_text(_summary(source_path, metric_rows, effect_rows))
    return {
        "out_dir": str(output_path),
        "condition_count": len(A5_REQUIRED_CONDITIONS),
        "seed_count": len(next(iter(run_index.values()))),
        "metric_rows": len(metric_rows),
        "effect_rows": len(effect_rows),
        "control_levels": tuple(level[0] for level in A5_CONTROL_LEVELS),
        "permutation_reps": permutation_reps,
        "permutation_seed": permutation_seed,
    }


def _validate_permutation_options(permutation_reps: int, permutation_seed: int) -> None:
    if isinstance(permutation_reps, bool) or not isinstance(permutation_reps, int):
        raise ValueError("permutation_reps must be an integer.")
    if permutation_reps <= 0:
        raise ValueError("permutation_reps must be positive.")
    if isinstance(permutation_seed, bool) or not isinstance(permutation_seed, int):
        raise ValueError("permutation_seed must be an integer.")


def _validate_source(source_path: Path) -> dict[str, dict[int, Path]]:
    if not source_path.is_dir():
        raise FileNotFoundError(f"A5 comparison directory does not exist: {source_path}")
    for artifact in (
        "predictive_control_comparison_metrics.csv",
        "predictive_control_effects.csv",
        "summary.md",
    ):
        if not (source_path / artifact).is_file():
            raise FileNotFoundError(f"A5 comparison source is missing {artifact}: {source_path}")

    run_index: dict[str, dict[int, Path]] = {condition: {} for condition in A5_REQUIRED_CONDITIONS}
    for child in source_path.iterdir():
        if not child.is_dir():
            continue
        for condition in A5_REQUIRED_CONDITIONS:
            prefix = f"{condition}_seed"
            if child.name.startswith(prefix):
                seed_text = child.name.removeprefix(prefix)
                if seed_text.isdigit():
                    run_index[condition][int(seed_text)] = child

    missing_conditions = [
        condition for condition, runs in run_index.items() if not runs
    ]
    if missing_conditions:
        raise FileNotFoundError(
            "A5 comparison source is missing condition run directories: "
            f"{', '.join(missing_conditions)}"
        )
    seed_sets = {condition: set(runs) for condition, runs in run_index.items()}
    reference_seeds = seed_sets[A5_REQUIRED_CONDITIONS[0]]
    mismatches = [
        condition
        for condition, seeds in seed_sets.items()
        if seeds != reference_seeds
    ]
    if mismatches:
        raise ValueError(f"A5 comparison seeds are not paired across conditions: {mismatches}")

    missing: list[str] = []
    for condition_runs in run_index.values():
        for run_path in condition_runs.values():
            for artifact in ("metrics.csv", "events.csv", "manifest.yaml", "summary.md"):
                if not (run_path / artifact).is_file():
                    missing.append(str(run_path / artifact))
            manifest_path = run_path / "manifest.yaml"
            if manifest_path.is_file():
                manifest = yaml.safe_load(manifest_path.read_text()) or {}
                if manifest.get("model", {}).get("predictive_control") is None:
                    missing.append(f"{manifest_path}: model.predictive_control")
    if missing:
        sample = ", ".join(missing[:6])
        suffix = "" if len(missing) <= 6 else f", ... ({len(missing)} missing total)"
        raise FileNotFoundError(f"A5 comparison source is missing artifacts: {sample}{suffix}")
    return run_index


def _ensure_outputs_available(output_path: Path, *, overwrite: bool) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [name for name in _OUTPUT_NAMES if (output_path / name).exists()]
    if collisions and not overwrite:
        raise FileExistsError(
            f"Output path {output_path} already contains A5 residual artifacts: "
            f"{', '.join(collisions)}"
        )


def _read_metrics(path: Path) -> list[dict[str, float | str]]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"A5 metrics file is empty: {path}")
    enriched = []
    for row in rows:
        parsed: dict[str, float | str] = dict(row)
        created = _float(row.get("tasks_created_total", "0"))
        completed = _float(row.get("tasks_completed_total", "0"))
        parsed["completion_fraction_tick"] = _safe_ratio(completed, created)
        tick = _float(row.get("tick", "0"))
        parsed["tick_squared"] = tick * tick
        enriched.append(parsed)
    return enriched


def _endpoint_rows(
    condition: str,
    seed: int,
    metrics: list[dict[str, float | str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for level_name, covariates, _description in A5_CONTROL_LEVELS:
        state = _residual_state(metrics, covariates)
        endpoints = {
            "forecast_skill_mean": _mean(_series(metrics, "a5_forecast_skill_tick")),
            "forecast_skill_per_budget_mean": _mean(
                _series(metrics, "a5_forecast_skill_per_budget_tick")
            ),
            "forecast_error_abs_mean": _mean_abs_residual_group(
                metrics,
                tuple(
                    f"a5_{class_name}_forecast_error_tick"
                    for class_name in ATTENTION_CLASSES
                ),
                covariates,
            ),
            "allocation_future_residual_abs_mean": _mean_abs_residual_group(
                metrics,
                tuple(
                    f"a5_{class_name}_allocation_future_residual_tick"
                    for class_name in ATTENTION_CLASSES
                ),
                covariates,
            ),
            "residual_state_lag1_autocorr": _lag1_autocorr(state),
            "residual_state_lag2_autocorr": _lag_autocorr(state, lag=2),
            "residual_state_return_distance_mean": _return_distance_mean(state),
            "residual_state_return_time_mean": _return_time_mean(state),
            "residual_state_return_time_entropy": _return_time_entropy(state),
            "residual_state_predictability_r2": _lag1_predictability_r2(state),
            "residual_state_compression_ratio": _compression_ratio(state),
            "completion_fraction_final": _series(metrics, "completion_fraction_tick")[-1],
            "queue_depth_final": _series(metrics, "queue_depth")[-1],
            "queued_age_final": _series(metrics, "queued_task_age_mean_tick")[-1],
            "attention_starvation_count_final": _starvation_count_final(metrics),
            "capture_pressure_peak": max(_series(metrics, "attention_capture_pressure_max_tick")),
            **{
                f"attention_{class_name}_completed_final": _series(
                    metrics,
                    f"attention_{class_name}_completed_total",
                )[-1]
                for class_name in ATTENTION_CLASSES
            },
        }
        for endpoint, value in endpoints.items():
            rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "control_level": level_name,
                    "endpoint": endpoint,
                    "value": round(float(value), 6),
                }
            )
    return rows


def _residual_state(
    metrics: list[dict[str, float | str]],
    covariates: tuple[str, ...],
) -> np.ndarray:
    columns = []
    for field in _STRUCTURE_FIELDS:
        if field not in metrics[0]:
            continue
        values = np.array(_series(metrics, field), dtype=float)
        columns.append(_residualize(values, metrics, covariates, target_field=field))
    if not columns:
        return np.zeros((len(metrics), 1), dtype=float)
    matrix = np.column_stack(columns)
    return _standardize_columns(matrix)


def _mean_abs_residual_group(
    metrics: list[dict[str, float | str]],
    fields: tuple[str, ...],
    covariates: tuple[str, ...],
) -> float:
    values = []
    for field in fields:
        residual = _residualize(
            np.array(_series(metrics, field), dtype=float),
            metrics,
            covariates,
            target_field=field,
        )
        values.append(np.abs(residual))
    return float(np.mean(np.column_stack(values))) if values else 0.0


def _starvation_count_final(metrics: list[dict[str, float | str]]) -> float:
    final = metrics[-1]
    count = 0
    for class_name in ATTENTION_CLASSES:
        queued = _float(final.get(f"attention_{class_name}_queued_tick", "0"))
        completed = _float(final.get(f"attention_{class_name}_completed_total", "0"))
        if queued > 0.0 and completed <= 0.0:
            count += 1
    return float(count)


def _residualize(
    y: np.ndarray,
    metrics: list[dict[str, float | str]],
    covariates: tuple[str, ...],
    *,
    target_field: str,
) -> np.ndarray:
    usable = [
        field
        for field in covariates
        if field != target_field and field in metrics[0] and _is_numeric(metrics[0][field])
    ]
    if not usable:
        return y.astype(float)
    controls = [np.ones(len(y), dtype=float)]
    controls.extend(np.array(_series(metrics, field), dtype=float) for field in usable)
    x = np.column_stack(controls)
    try:
        coefficients, *_ = np.linalg.lstsq(x, y, rcond=None)
    except np.linalg.LinAlgError:
        return y.astype(float)
    return y - (x @ coefficients)


def _standardize_columns(matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return matrix
    centered = matrix - np.mean(matrix, axis=0)
    scale = np.std(centered, axis=0)
    scale[scale == 0.0] = 1.0
    return centered / scale


def _lag1_autocorr(state: np.ndarray) -> float:
    return _lag_autocorr(state, lag=1)


def _lag_autocorr(state: np.ndarray, *, lag: int) -> float:
    if lag <= 0:
        raise ValueError("lag must be positive.")
    if state.shape[0] < 3:
        return 0.0
    if state.shape[0] <= lag + 1:
        return 0.0
    values = []
    for index in range(state.shape[1]):
        left = state[:-lag, index]
        right = state[lag:, index]
        if np.std(left) == 0.0 or np.std(right) == 0.0:
            continue
        values.append(float(np.corrcoef(left, right)[0, 1]))
    return _mean(values)


def _nearest_return_distances_and_times(state: np.ndarray) -> tuple[list[float], list[int]]:
    if state.shape[0] < 4:
        return [], []
    distances = []
    return_times = []
    for index in range(state.shape[0]):
        candidates = sorted(
            (
                float(np.linalg.norm(state[index] - state[other])),
                abs(index - other),
            )
            for other in range(state.shape[0])
            if abs(index - other) > 1
        )
        if candidates:
            distance, return_time = candidates[0]
            distances.append(distance)
            return_times.append(return_time)
    return distances, return_times


def _return_distance_mean(state: np.ndarray) -> float:
    distances, _return_times = _nearest_return_distances_and_times(state)
    return _mean(distances)


def _return_time_mean(state: np.ndarray) -> float:
    _distances, return_times = _nearest_return_distances_and_times(state)
    return _mean([float(value) for value in return_times])


def _return_time_entropy(state: np.ndarray) -> float:
    _distances, return_times = _nearest_return_distances_and_times(state)
    if not return_times:
        return 0.0
    counts: dict[int, int] = defaultdict(int)
    for value in return_times:
        counts[value] += 1
    total = float(sum(counts.values()))
    return float(
        -sum((count / total) * math.log2(count / total) for count in counts.values())
    )


def _lag1_predictability_r2(state: np.ndarray) -> float:
    if state.shape[0] < 3:
        return 0.0
    observed = state[1:]
    predicted = state[:-1]
    mse = float(np.mean((observed - predicted) ** 2))
    variance = float(np.var(observed))
    if variance == 0.0:
        return 0.0
    return 1.0 - (mse / variance)


def _compression_ratio(state: np.ndarray) -> float:
    rounded = np.round(state, 3)
    payload = ";".join(",".join(f"{value:.3f}" for value in row) for row in rounded)
    if not payload:
        return 0.0
    compressed = zlib.compress(payload.encode("utf-8"), level=9)
    return len(compressed) / len(payload.encode("utf-8"))


def _effect_rows(
    metric_rows: list[dict[str, Any]],
    *,
    permutation_reps: int,
    permutation_seed: int,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[int, float]] = defaultdict(dict)
    for row in metric_rows:
        grouped[
            (str(row["condition"]), str(row["control_level"]), str(row["endpoint"]))
        ][int(row["seed"])] = float(row["value"])

    contrasts = [
        *(
            (f"{condition}_minus_reactive", condition, "reactive")
            for condition in A5_INTERMEDIATE_CONDITIONS
        ),
        *(
            (
                f"{condition}_minus_{A5_TIMING_BROKEN_NULL_BY_CONDITION[condition]}",
                condition,
                A5_TIMING_BROKEN_NULL_BY_CONDITION[condition],
            )
            for condition in A5_INTERMEDIATE_CONDITIONS
        ),
        ("oracle_minus_linear", "oracle", "linear"),
        ("oracle_minus_nonlinear", "oracle", "nonlinear"),
    ]
    rows = []
    for contrast, high_condition, low_condition in contrasts:
        for control_level, _covariates, _description in A5_CONTROL_LEVELS:
            endpoints = sorted(
                endpoint
                for condition, level, endpoint in grouped
                if condition == high_condition and level == control_level
            )
            for endpoint in endpoints:
                high = grouped[(high_condition, control_level, endpoint)]
                low = grouped[(low_condition, control_level, endpoint)]
                seeds = sorted(set(high) & set(low))
                deltas = [high[seed] - low[seed] for seed in seeds]
                null = _label_permutation_deltas(
                    deltas,
                    reps=permutation_reps,
                    seed=permutation_seed,
                    salt=f"{contrast}:{control_level}:{endpoint}",
                )
                ci_low = _quantile(null, 0.025)
                ci_high = _quantile(null, 0.975)
                mean_delta = _mean(deltas)
                rows.append(
                    {
                        "contrast": contrast,
                        "control_level": control_level,
                        "endpoint": endpoint,
                        "high_condition": high_condition,
                        "low_condition": low_condition,
                        "paired_seed_count": len(seeds),
                        "high_mean": _mean([high[seed] for seed in seeds]),
                        "low_mean": _mean([low[seed] for seed in seeds]),
                        "mean_delta": mean_delta,
                        "positive_delta_rate": _mean(
                            [1.0 if delta > 0.0 else 0.0 for delta in deltas]
                        ),
                        "label_permutation_ci_low": ci_low,
                        "label_permutation_ci_high": ci_high,
                        "outside_label_permutation_ci": mean_delta < ci_low
                        or mean_delta > ci_high,
                        "interpretation": _interpret_effect(endpoint, mean_delta, ci_low, ci_high),
                    }
                )
    return rows


def _label_permutation_deltas(
    deltas: list[float],
    *,
    reps: int,
    seed: int,
    salt: str,
) -> list[float]:
    if not deltas:
        return [0.0]
    if len(deltas) <= 10:
        return [
            _mean([delta * sign for delta, sign in zip(deltas, signs, strict=True)])
            for signs in itertools.product((-1.0, 1.0), repeat=len(deltas))
        ]
    rng = random.Random(f"{seed}:{salt}")
    values = []
    for _ in range(reps):
        values.append(
            _mean([
                delta * (-1.0 if rng.random() < 0.5 else 1.0)
                for delta in deltas
            ])
        )
    return values


def _interpret_effect(endpoint: str, mean_delta: float, ci_low: float, ci_high: float) -> str:
    if ci_low <= mean_delta <= ci_high:
        return "inside paired label-permutation interval"
    if endpoint in {
        "forecast_error_abs_mean",
        "allocation_future_residual_abs_mean",
        "queue_depth_final",
        "queued_age_final",
        "capture_pressure_peak",
        "residual_state_compression_ratio",
        "residual_state_return_distance_mean",
    }:
        return "lower endpoint outside paired label-permutation interval" if mean_delta < 0.0 else (
            "higher endpoint outside paired label-permutation interval"
        )
    return "higher endpoint outside paired label-permutation interval" if mean_delta > 0.0 else (
        "lower endpoint outside paired label-permutation interval"
    )


def _summary(
    source_path: Path,
    metric_rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
) -> str:
    rows_by_endpoint = {
        (row["contrast"], row["control_level"], row["endpoint"]): row
        for row in effect_rows
    }
    promotion_rows = _promotion_rule_rows(rows_by_endpoint)
    lines = [
        "# A5 Residual Accounting Analysis",
        "",
        f"- source comparison: `{source_path}`",
        f"- metric rows: {len(metric_rows)}",
        f"- effect rows: {len(effect_rows)}",
        "- scope: read-only single-hive A5 diagnostics; no simulator reruns or multi-hive coupling",
        "",
        "## Primary Contrasts",
        "",
    ]
    for condition in A5_INTERMEDIATE_CONDITIONS:
        for baseline in ("reactive", A5_TIMING_BROKEN_NULL_BY_CONDITION[condition]):
            contrast = f"{condition}_minus_{baseline}"
            row = rows_by_endpoint.get(
                (contrast, "full_accounting", "residual_state_predictability_r2")
            )
            if row is None:
                continue
            lines.append(
                "- "
                f"{condition} vs {baseline}, full accounting predictability: "
                f"delta={_format_number(row['mean_delta'])}, "
                f"positive_rate={_format_number(row['positive_delta_rate'])}, "
                f"{row['interpretation']}"
            )
    lines.extend(
        [
            "",
            "## Promotion Rule Audit",
            "",
            _A5_GUARDRAIL_POLICY,
            "",
        ]
    )
    for row in promotion_rows:
        lines.append(
            "- "
            f"{row['condition']}: "
            f"skill_vs_reactive={row['skill_vs_reactive']}, "
            f"skill_vs_shuffled={row['skill_vs_shuffled']}, "
            f"residual_vs_reactive={row['residual_vs_reactive']}, "
            f"residual_vs_shuffled={row['residual_vs_shuffled']}, "
            f"nontrivial_vs_oracle={row['nontrivial_vs_oracle']}, "
            f"guardrails_ok={row['guardrails_ok']}; "
            f"promotion_satisfied={row['promotion_satisfied']}"
        )
    if not any(row["promotion_satisfied"] for row in promotion_rows):
        lines.append("")
        lines.append(
            "Promotion decision: fail closed; no intermediate-budget condition "
            "satisfies all preregistered criteria."
        )
    else:
        promoted = ", ".join(
            str(row["condition"]) for row in promotion_rows if row["promotion_satisfied"]
        )
        lines.append("")
        lines.append(f"Promotion decision: candidate condition(s) requiring review: {promoted}.")
    lines.extend(
        [
            "",
            "## Conservative Use",
            "",
            (
                "Treat this as a fail-closed diagnostic. Intermediate prediction budgets "
                "only become scientifically interesting if forecast skill, residual "
                "structure, and guardrails survive the preregistered accounting controls "
                "and shuffled/reactive null contrasts."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def _promotion_rule_rows(
    rows_by_endpoint: dict[tuple[Any, Any, Any], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for condition in A5_INTERMEDIATE_CONDITIONS:
        skill_vs_reactive = _effect_positive(
            rows_by_endpoint,
            f"{condition}_minus_reactive",
            "full_accounting",
            "forecast_skill_mean",
        )
        skill_vs_shuffled = _effect_positive(
            rows_by_endpoint,
            f"{condition}_minus_{A5_TIMING_BROKEN_NULL_BY_CONDITION[condition]}",
            "full_accounting",
            "forecast_skill_mean",
        )
        residual_vs_reactive = _effect_positive_outside_null(
            rows_by_endpoint,
            f"{condition}_minus_reactive",
            "full_accounting",
            "residual_state_predictability_r2",
        )
        residual_vs_shuffled = _effect_positive_outside_null(
            rows_by_endpoint,
            f"{condition}_minus_{A5_TIMING_BROKEN_NULL_BY_CONDITION[condition]}",
            "full_accounting",
            "residual_state_predictability_r2",
        )
        oracle_delta = _effect_delta(
            rows_by_endpoint,
            f"oracle_minus_{condition}",
            "full_accounting",
            "residual_state_predictability_r2",
        )
        nontrivial_vs_oracle = oracle_delta is not None and oracle_delta < 0.0
        guardrails_ok = _guardrails_ok(rows_by_endpoint, condition)
        promotion_satisfied = all(
            (
                skill_vs_reactive,
                skill_vs_shuffled,
                residual_vs_reactive,
                residual_vs_shuffled,
                nontrivial_vs_oracle,
                guardrails_ok,
            )
        )
        rows.append(
            {
                "condition": condition,
                "skill_vs_reactive": skill_vs_reactive,
                "skill_vs_shuffled": skill_vs_shuffled,
                "residual_vs_reactive": residual_vs_reactive,
                "residual_vs_shuffled": residual_vs_shuffled,
                "nontrivial_vs_oracle": nontrivial_vs_oracle,
                "guardrails_ok": guardrails_ok,
                "promotion_satisfied": promotion_satisfied,
            }
        )
    return rows


def _guardrails_ok(
    rows_by_endpoint: dict[tuple[Any, Any, Any], dict[str, Any]],
    condition: str,
) -> bool:
    contrast = f"{condition}_minus_reactive"
    queue_delta = _effect_delta(
        rows_by_endpoint,
        contrast,
        "full_accounting",
        "queue_depth_final",
    )
    age_delta = _effect_delta(
        rows_by_endpoint,
        contrast,
        "full_accounting",
        "queued_age_final",
    )
    completion_delta = _effect_delta(
        rows_by_endpoint,
        contrast,
        "full_accounting",
        "completion_fraction_final",
    )
    capture_delta = _effect_delta(
        rows_by_endpoint,
        contrast,
        "full_accounting",
        "capture_pressure_peak",
    )
    if (
        queue_delta is None
        or age_delta is None
        or completion_delta is None
        or capture_delta is None
    ):
        return False
    class_completion_ok = True
    for class_name in ATTENTION_CLASSES:
        class_delta = _effect_delta(
            rows_by_endpoint,
            contrast,
            "full_accounting",
            f"attention_{class_name}_completed_final",
        )
        if class_delta is None or class_delta < -A5_CONFIRMATORY_GUARDRAIL_TOLERANCES[
            "attention_completed_total"
        ]:
            class_completion_ok = False
            break
    return (
        queue_delta <= A5_CONFIRMATORY_GUARDRAIL_TOLERANCES["queue_depth_final"]
        and age_delta <= A5_CONFIRMATORY_GUARDRAIL_TOLERANCES["queued_age_final"]
        and completion_delta >= -A5_CONFIRMATORY_GUARDRAIL_TOLERANCES[
            "completion_fraction_final"
        ]
        and capture_delta <= A5_CONFIRMATORY_GUARDRAIL_TOLERANCES["capture_pressure_peak"]
        and class_completion_ok
    )


def _effect_positive(
    rows_by_endpoint: dict[tuple[Any, Any, Any], dict[str, Any]],
    contrast: str,
    control_level: str,
    endpoint: str,
) -> bool:
    delta = _effect_delta(rows_by_endpoint, contrast, control_level, endpoint)
    return delta is not None and delta > 0.0


def _effect_positive_outside_null(
    rows_by_endpoint: dict[tuple[Any, Any, Any], dict[str, Any]],
    contrast: str,
    control_level: str,
    endpoint: str,
) -> bool:
    row = rows_by_endpoint.get((contrast, control_level, endpoint))
    if row is None:
        return False
    return float(row["mean_delta"]) > 0.0 and bool(row["outside_label_permutation_ci"])


def _effect_delta(
    rows_by_endpoint: dict[tuple[Any, Any, Any], dict[str, Any]],
    contrast: str,
    control_level: str,
    endpoint: str,
) -> float | None:
    row = rows_by_endpoint.get((contrast, control_level, endpoint))
    return None if row is None else float(row["mean_delta"])


def _series(metrics: list[dict[str, float | str]], field: str) -> list[float]:
    return [_float(row.get(field, "0")) for row in metrics]


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _safe_ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    return float(value)


def _is_numeric(value: Any) -> bool:
    try:
        _float(value)
    except (TypeError, ValueError):
        return False
    return True


def _mean(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return float(ordered[int(index)])
    weight = index - lower
    return float(ordered[lower] * (1.0 - weight) + ordered[upper] * weight)


def _format_number(value: Any) -> str:
    number = float(value)
    if number == 0.0:
        return "0"
    if abs(number) >= 1000 or abs(number) < 0.001:
        return f"{number:.3e}"
    return f"{number:.3f}".rstrip("0").rstrip(".")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze A5 predictive-control residual accounting artifacts."
    )
    parser.add_argument(
        "--compare-dir",
        default=str(DEFAULT_A5_COMPARE_DIR),
        help="Existing ohdyn.compare_predictive_control output directory.",
    )
    parser.add_argument("--out", default=str(DEFAULT_A5_RESIDUAL_OUT_DIR), help="Output directory.")
    parser.add_argument(
        "--permutation-reps",
        type=int,
        default=DEFAULT_A5_PERMUTATION_REPS,
        help="Monte Carlo sign-flip replicates when exact enumeration is too large.",
    )
    parser.add_argument(
        "--permutation-seed",
        type=int,
        default=DEFAULT_A5_PERMUTATION_SEED,
        help="Deterministic seed for sampled label permutations.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing A5 residual accounting outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a5_residual_accounting_analysis(
            compare_dir=args.compare_dir,
            out_dir=args.out,
            permutation_reps=args.permutation_reps,
            permutation_seed=args.permutation_seed,
            overwrite=args.overwrite,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
