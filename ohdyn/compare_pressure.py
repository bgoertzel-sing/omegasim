"""Compare A2 attention-policy sets across task-creation pressure levels."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.config import ATTENTION_CLASSES
from ohdyn.compare_attention import (
    DEFAULT_BASELINE_CONFIG,
    DEFAULT_INTERNAL_IMPROVEMENT_CONFIG,
    DEFAULT_SEEDS,
    DEFAULT_VARIANT_CONFIG,
    _format_regime_count_deltas,
    _format_regime_rate_deltas,
    _mean,
    _phase_space_regime_counts,
    run_comparison,
)


DEFAULT_HIGH_PRESSURE_BASELINE_CONFIG = Path("configs/a2_attention_high_pressure.yaml")
DEFAULT_HIGH_PRESSURE_VARIANT_CONFIG = Path(
    "configs/a2_attention_research_heavy_high_pressure.yaml"
)
DEFAULT_HIGH_PRESSURE_INTERNAL_IMPROVEMENT_CONFIG = Path(
    "configs/a2_attention_internal_improvement_high_pressure.yaml"
)
DEFAULT_MEDIUM_PRESSURE_BASELINE_CONFIG = Path("configs/a2_attention_medium_pressure.yaml")
DEFAULT_MEDIUM_PRESSURE_VARIANT_CONFIG = Path(
    "configs/a2_attention_research_heavy_medium_pressure.yaml"
)
DEFAULT_MEDIUM_PRESSURE_INTERNAL_IMPROVEMENT_CONFIG = Path(
    "configs/a2_attention_internal_improvement_medium_pressure.yaml"
)
NORMAL_PRESSURE_VALUE = 1.0
MEDIUM_PRESSURE_VALUE = 1.4
HIGH_PRESSURE_VALUE = 1.8
PRESSURE_COMPARISON_FIELDS = (
    "policy",
    "normal_total_steps",
    "medium_pressure_total_steps",
    "high_pressure_total_steps",
    "regime_rate_deltas",
    "regime_count_deltas",
    "value_weighted_completed_mean_delta",
    "tasks_completed_mean_delta",
    "queue_depth_mean_delta",
    "queued_task_age_mean_final_delta",
    "queued_task_age_mean_over_ticks_delta",
    "queued_task_age_max_peak_delta",
    "attention_capture_pressure_max_final_delta",
    "attention_capture_pressure_mean_over_ticks_delta",
    "attention_capture_pressure_peak_delta",
    *(
        field
        for class_name in ATTENTION_CLASSES
        for field in (
            f"{class_name}_capture_pressure_final_delta",
            f"{class_name}_capture_pressure_mean_over_ticks_delta",
            f"{class_name}_capture_pressure_peak_delta",
        )
    ),
    "value_weighted_completed_normal_to_medium_slope",
    "value_weighted_completed_medium_to_high_slope",
    "value_weighted_completed_pressure_curvature",
    "tasks_completed_normal_to_medium_slope",
    "tasks_completed_medium_to_high_slope",
    "tasks_completed_pressure_curvature",
    "queue_depth_normal_to_medium_slope",
    "queue_depth_medium_to_high_slope",
    "queue_depth_pressure_curvature",
    "queued_task_age_mean_final_normal_to_medium_slope",
    "queued_task_age_mean_final_medium_to_high_slope",
    "queued_task_age_mean_final_pressure_curvature",
    "queued_task_age_max_peak_normal_to_medium_slope",
    "queued_task_age_max_peak_medium_to_high_slope",
    "queued_task_age_max_peak_pressure_curvature",
    "attention_capture_pressure_max_final_normal_to_medium_slope",
    "attention_capture_pressure_max_final_medium_to_high_slope",
    "attention_capture_pressure_max_final_pressure_curvature",
    "attention_capture_pressure_mean_over_ticks_normal_to_medium_slope",
    "attention_capture_pressure_mean_over_ticks_medium_to_high_slope",
    "attention_capture_pressure_mean_over_ticks_pressure_curvature",
    "attention_capture_pressure_peak_normal_to_medium_slope",
    "attention_capture_pressure_peak_medium_to_high_slope",
    "attention_capture_pressure_peak_pressure_curvature",
    *(
        field
        for class_name in ATTENTION_CLASSES
        for field in (
            f"{class_name}_capture_pressure_final_normal_to_medium_slope",
            f"{class_name}_capture_pressure_final_medium_to_high_slope",
            f"{class_name}_capture_pressure_final_pressure_curvature",
            f"{class_name}_capture_pressure_mean_over_ticks_normal_to_medium_slope",
            f"{class_name}_capture_pressure_mean_over_ticks_medium_to_high_slope",
            f"{class_name}_capture_pressure_mean_over_ticks_pressure_curvature",
            f"{class_name}_capture_pressure_peak_normal_to_medium_slope",
            f"{class_name}_capture_pressure_peak_medium_to_high_slope",
            f"{class_name}_capture_pressure_peak_pressure_curvature",
        )
    ),
)
PRESSURE_RESPONSE_SELECTION_FIELDS = (
    "selection_scope",
    "seeds",
    "stable_with_full",
    "instability_causes",
    "policy",
    "observable",
    "metric",
    "field",
    "source_field",
    "value",
    "abs_value",
    "normal_mean",
    "medium_mean",
    "high_mean",
    "normal_to_medium_slope",
    "medium_to_high_slope",
    "curvature",
    "high_minus_normal_delta",
    "source_metric_normal_mean",
    "source_metric_normal_min",
    "source_metric_normal_max",
    "source_metric_normal_per_seed_values",
    "source_metric_medium_mean",
    "source_metric_medium_min",
    "source_metric_medium_max",
    "source_metric_medium_per_seed_values",
    "source_metric_high_mean",
    "source_metric_high_min",
    "source_metric_high_max",
    "source_metric_high_per_seed_values",
)
PRESSURE_STABILITY_AGREEMENT_FIELDS = (
    "full_seeds",
    "prefix_seeds",
    "global_stable_with_full",
    "class_stable_with_full",
    "stable_together",
    "global_instability_causes",
    "class_instability_causes",
    "global_policy",
    "global_observable",
    "global_metric",
    "global_field",
    "class_policy",
    "class_observable",
    "class_metric",
    "class_field",
)
PRESSURE_STABILITY_CONVERGENCE_FIELDS = (
    "full_seeds",
    "prefix_count",
    "global_stable_prefixes",
    "class_stable_prefixes",
    "stable_together_prefixes",
    "both_stable_prefixes",
    "first_global_stable_prefix",
    "first_class_stable_prefix",
    "first_stable_together_prefix",
    "first_both_stable_prefix",
    "last_prefix",
    "last_global_stable",
    "last_class_stable",
    "last_stable_together",
    "last_both_stable",
)
PRESSURE_CURVE_OBSERVABLES = (
    (
        "value_weighted_completed",
        "value-weighted completed work",
        "value_weighted_completed_total",
    ),
    ("tasks_completed", "tasks completed", "tasks_completed_total"),
    ("queue_depth", "final queue depth", "queue_depth"),
    ("queued_task_age_mean_final", "final queued task mean age", "queued_task_age_mean_final"),
    ("queued_task_age_max_peak", "peak queued task max age", "queued_task_age_max_peak"),
    (
        "attention_capture_pressure_max_final",
        "final attention capture pressure",
        "attention_capture_pressure_max_final",
    ),
    (
        "attention_capture_pressure_mean_over_ticks",
        "mean attention capture pressure",
        "attention_capture_pressure_mean_over_ticks",
    ),
    (
        "attention_capture_pressure_peak",
        "peak attention capture pressure",
        "attention_capture_pressure_peak",
    ),
    *(
        observable
        for class_name in ATTENTION_CLASSES
        for observable in (
            (
                f"{class_name}_capture_pressure_final",
                f"final {class_name.replace('_', ' ')} capture pressure",
                f"{class_name}_capture_pressure_final",
            ),
            (
                f"{class_name}_capture_pressure_mean_over_ticks",
                f"mean {class_name.replace('_', ' ')} capture pressure",
                f"{class_name}_capture_pressure_mean_over_ticks",
            ),
            (
                f"{class_name}_capture_pressure_peak",
                f"peak {class_name.replace('_', ' ')} capture pressure",
                f"{class_name}_capture_pressure_peak",
            ),
        )
    ),
)
PRESSURE_CURVE_METRICS = (
    ("normal_to_medium_slope", "normal_to_medium_slope"),
    ("medium_to_high_slope", "medium_to_high_slope"),
    ("pressure_curvature", "curvature"),
)


def run_pressure_comparison(
    *,
    normal_baseline_config: str | Path = DEFAULT_BASELINE_CONFIG,
    normal_variant_config: str | Path = DEFAULT_VARIANT_CONFIG,
    normal_internal_improvement_config: str | Path | None = DEFAULT_INTERNAL_IMPROVEMENT_CONFIG,
    medium_pressure_baseline_config: str | Path = DEFAULT_MEDIUM_PRESSURE_BASELINE_CONFIG,
    medium_pressure_variant_config: str | Path = DEFAULT_MEDIUM_PRESSURE_VARIANT_CONFIG,
    medium_pressure_internal_improvement_config: str | Path | None = (
        DEFAULT_MEDIUM_PRESSURE_INTERNAL_IMPROVEMENT_CONFIG
    ),
    high_pressure_baseline_config: str | Path = DEFAULT_HIGH_PRESSURE_BASELINE_CONFIG,
    high_pressure_variant_config: str | Path = DEFAULT_HIGH_PRESSURE_VARIANT_CONFIG,
    high_pressure_internal_improvement_config: str | Path | None = (
        DEFAULT_HIGH_PRESSURE_INTERNAL_IMPROVEMENT_CONFIG
    ),
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    out_dir: str | Path,
) -> list[dict[str, Any]]:
    output_path = Path(out_dir)
    _ensure_pressure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    normal_rows = run_comparison(
        baseline_config=normal_baseline_config,
        variant_config=normal_variant_config,
        internal_improvement_config=normal_internal_improvement_config,
        seeds=seeds,
        out_dir=output_path / "normal_pressure",
    )
    medium_pressure_rows = run_comparison(
        baseline_config=medium_pressure_baseline_config,
        variant_config=medium_pressure_variant_config,
        internal_improvement_config=medium_pressure_internal_improvement_config,
        seeds=seeds,
        out_dir=output_path / "medium_pressure",
    )
    high_pressure_rows = run_comparison(
        baseline_config=high_pressure_baseline_config,
        variant_config=high_pressure_variant_config,
        internal_improvement_config=high_pressure_internal_improvement_config,
        seeds=seeds,
        out_dir=output_path / "high_pressure",
    )

    rows = _pressure_rows(normal_rows, medium_pressure_rows, high_pressure_rows)
    stability_agreement_rows = _pressure_stability_agreement_rows(
        seeds=seeds,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    _write_pressure_comparison_csv(output_path / "pressure_comparison_metrics.csv", rows)
    _write_pressure_response_selection_csv(
        output_path / "pressure_response_selection.csv",
        _pressure_response_selection_rows(
            seeds=seeds,
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
        ),
    )
    _write_pressure_stability_agreement_csv(
        output_path / "pressure_stability_agreement.csv",
        stability_agreement_rows,
    )
    _write_pressure_stability_convergence_csv(
        output_path / "pressure_stability_convergence.csv",
        _pressure_stability_convergence_rows(stability_agreement_rows),
    )
    (output_path / "summary.md").write_text(
        _pressure_summary(
            normal_baseline_config=Path(normal_baseline_config),
            normal_variant_config=Path(normal_variant_config),
            normal_internal_improvement_config=(
                Path(normal_internal_improvement_config)
                if normal_internal_improvement_config is not None
                else None
            ),
            medium_pressure_baseline_config=Path(medium_pressure_baseline_config),
            medium_pressure_variant_config=Path(medium_pressure_variant_config),
            medium_pressure_internal_improvement_config=(
                Path(medium_pressure_internal_improvement_config)
                if medium_pressure_internal_improvement_config is not None
                else None
            ),
            high_pressure_baseline_config=Path(high_pressure_baseline_config),
            high_pressure_variant_config=Path(high_pressure_variant_config),
            high_pressure_internal_improvement_config=(
                Path(high_pressure_internal_improvement_config)
                if high_pressure_internal_improvement_config is not None
                else None
            ),
            seeds=seeds,
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
            stability_agreement_rows=stability_agreement_rows,
        )
    )
    return rows


def _ensure_pressure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        artifact_name
        for artifact_name in (
            "pressure_comparison_metrics.csv",
            "pressure_response_selection.csv",
            "pressure_stability_agreement.csv",
            "pressure_stability_convergence.csv",
            "summary.md",
        )
        if (output_path / artifact_name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains pressure comparison artifacts: {names}")


def _pressure_rows(
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    policies = tuple(dict.fromkeys(row["policy"] for row in normal_rows))
    medium_pressure_policies = {row["policy"] for row in medium_pressure_rows}
    high_pressure_policies = {row["policy"] for row in high_pressure_rows}
    _raise_missing_policies(
        "Medium-pressure comparison",
        policies,
        medium_pressure_policies,
    )
    _raise_missing_policies(
        "High-pressure comparison",
        policies,
        high_pressure_policies,
    )

    return [
        _pressure_row(
            policy,
            [row for row in normal_rows if row["policy"] == policy],
            [row for row in medium_pressure_rows if row["policy"] == policy],
            [row for row in high_pressure_rows if row["policy"] == policy],
        )
        for policy in policies
    ]


def _raise_missing_policies(
    label: str,
    expected_policies: tuple[str, ...],
    available_policies: set[str],
) -> None:
    missing = [policy for policy in expected_policies if policy not in available_policies]
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"{label} is missing policies: {names}")


def _pressure_row(
    policy: str,
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    normal_counts, normal_total_steps = _phase_space_regime_counts(normal_rows)
    _, medium_total_steps = _phase_space_regime_counts(medium_pressure_rows)
    high_counts, high_total_steps = _phase_space_regime_counts(high_pressure_rows)
    labels = sorted(set(normal_counts) | set(high_counts))
    row = {
        "policy": policy,
        "normal_total_steps": normal_total_steps,
        "medium_pressure_total_steps": medium_total_steps,
        "high_pressure_total_steps": high_total_steps,
        "regime_rate_deltas": _format_regime_rate_deltas(
            high_counts,
            high_total_steps,
            normal_counts,
            normal_total_steps,
            labels,
        ),
        "regime_count_deltas": _format_regime_count_deltas(
            high_counts,
            normal_counts,
            labels,
        ),
        "value_weighted_completed_mean_delta": _metric_mean_delta(
            high_pressure_rows,
            normal_rows,
            "value_weighted_completed_total",
        ),
        "tasks_completed_mean_delta": _metric_mean_delta(
            high_pressure_rows,
            normal_rows,
            "tasks_completed_total",
        ),
        "queue_depth_mean_delta": _metric_mean_delta(
            high_pressure_rows,
            normal_rows,
            "queue_depth",
        ),
        "queued_task_age_mean_final_delta": _metric_mean_delta(
            high_pressure_rows,
            normal_rows,
            "queued_task_age_mean_final",
        ),
        "queued_task_age_mean_over_ticks_delta": _metric_mean_delta(
            high_pressure_rows,
            normal_rows,
            "queued_task_age_mean_over_ticks",
        ),
        "queued_task_age_max_peak_delta": _metric_mean_delta(
            high_pressure_rows,
            normal_rows,
            "queued_task_age_max_peak",
        ),
        "attention_capture_pressure_max_final_delta": _metric_mean_delta(
            high_pressure_rows,
            normal_rows,
            "attention_capture_pressure_max_final",
        ),
        "attention_capture_pressure_mean_over_ticks_delta": _metric_mean_delta(
            high_pressure_rows,
            normal_rows,
            "attention_capture_pressure_mean_over_ticks",
        ),
        "attention_capture_pressure_peak_delta": _metric_mean_delta(
            high_pressure_rows,
            normal_rows,
            "attention_capture_pressure_peak",
        ),
    }
    for class_name in ATTENTION_CLASSES:
        row.update(
            {
                f"{class_name}_capture_pressure_final_delta": _metric_mean_delta(
                    high_pressure_rows,
                    normal_rows,
                    f"{class_name}_capture_pressure_final",
                ),
                f"{class_name}_capture_pressure_mean_over_ticks_delta": (
                    _metric_mean_delta(
                        high_pressure_rows,
                        normal_rows,
                        f"{class_name}_capture_pressure_mean_over_ticks",
                    )
                ),
                f"{class_name}_capture_pressure_peak_delta": _metric_mean_delta(
                    high_pressure_rows,
                    normal_rows,
                    f"{class_name}_capture_pressure_peak",
                ),
            }
        )
    row.update(
        _pressure_curve_metrics(
            normal_rows,
            medium_pressure_rows,
            high_pressure_rows,
            source_field="value_weighted_completed_total",
            output_prefix="value_weighted_completed",
        )
    )
    row.update(
        _pressure_curve_metrics(
            normal_rows,
            medium_pressure_rows,
            high_pressure_rows,
            source_field="tasks_completed_total",
            output_prefix="tasks_completed",
        )
    )
    row.update(
        _pressure_curve_metrics(
            normal_rows,
            medium_pressure_rows,
            high_pressure_rows,
            source_field="queue_depth",
            output_prefix="queue_depth",
        )
    )
    row.update(
        _pressure_curve_metrics(
            normal_rows,
            medium_pressure_rows,
            high_pressure_rows,
            source_field="queued_task_age_mean_final",
            output_prefix="queued_task_age_mean_final",
        )
    )
    row.update(
        _pressure_curve_metrics(
            normal_rows,
            medium_pressure_rows,
            high_pressure_rows,
            source_field="queued_task_age_max_peak",
            output_prefix="queued_task_age_max_peak",
        )
    )
    row.update(
        _pressure_curve_metrics(
            normal_rows,
            medium_pressure_rows,
            high_pressure_rows,
            source_field="attention_capture_pressure_max_final",
            output_prefix="attention_capture_pressure_max_final",
        )
    )
    row.update(
        _pressure_curve_metrics(
            normal_rows,
            medium_pressure_rows,
            high_pressure_rows,
            source_field="attention_capture_pressure_mean_over_ticks",
            output_prefix="attention_capture_pressure_mean_over_ticks",
        )
    )
    row.update(
        _pressure_curve_metrics(
            normal_rows,
            medium_pressure_rows,
            high_pressure_rows,
            source_field="attention_capture_pressure_peak",
            output_prefix="attention_capture_pressure_peak",
        )
    )
    for class_name in ATTENTION_CLASSES:
        for statistic in ("final", "mean_over_ticks", "peak"):
            row.update(
                _pressure_curve_metrics(
                    normal_rows,
                    medium_pressure_rows,
                    high_pressure_rows,
                    source_field=f"{class_name}_capture_pressure_{statistic}",
                    output_prefix=f"{class_name}_capture_pressure_{statistic}",
                )
            )
    return row


def _metric_mean_delta(
    high_pressure_rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    field: str,
) -> float:
    return round(_mean(high_pressure_rows, field) - _mean(normal_rows, field), 6)


def _pressure_curve_metrics(
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
    *,
    source_field: str,
    output_prefix: str,
) -> dict[str, float]:
    normal_mean = _mean(normal_rows, source_field)
    medium_mean = _mean(medium_pressure_rows, source_field)
    high_mean = _mean(high_pressure_rows, source_field)
    normal_to_medium_slope = _pressure_slope(
        normal_mean,
        medium_mean,
        NORMAL_PRESSURE_VALUE,
        MEDIUM_PRESSURE_VALUE,
    )
    medium_to_high_slope = _pressure_slope(
        medium_mean,
        high_mean,
        MEDIUM_PRESSURE_VALUE,
        HIGH_PRESSURE_VALUE,
    )
    return {
        f"{output_prefix}_normal_to_medium_slope": normal_to_medium_slope,
        f"{output_prefix}_medium_to_high_slope": medium_to_high_slope,
        f"{output_prefix}_pressure_curvature": round(
            medium_to_high_slope - normal_to_medium_slope,
            6,
        ),
    }


def _pressure_slope(
    start_value: float,
    end_value: float,
    start_pressure: float,
    end_pressure: float,
) -> float:
    return round((end_value - start_value) / (end_pressure - start_pressure), 6)


def _write_pressure_comparison_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(PRESSURE_COMPARISON_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def _write_pressure_response_selection_csv(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(PRESSURE_RESPONSE_SELECTION_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def _write_pressure_stability_agreement_csv(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(PRESSURE_STABILITY_AGREEMENT_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def _write_pressure_stability_convergence_csv(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(PRESSURE_STABILITY_CONVERGENCE_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def _pressure_stability_convergence_rows(
    agreement_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not agreement_rows:
        return []

    last_row = agreement_rows[-1]
    return [
        {
            "full_seeds": last_row["full_seeds"],
            "prefix_count": len(agreement_rows),
            "global_stable_prefixes": _count_true(
                agreement_rows,
                "global_stable_with_full",
            ),
            "class_stable_prefixes": _count_true(
                agreement_rows,
                "class_stable_with_full",
            ),
            "stable_together_prefixes": _count_true(
                agreement_rows,
                "stable_together",
            ),
            "both_stable_prefixes": sum(
                1
                for row in agreement_rows
                if _is_true(row["global_stable_with_full"])
                and _is_true(row["class_stable_with_full"])
            ),
            "first_global_stable_prefix": _first_true_prefix(
                agreement_rows,
                "global_stable_with_full",
            ),
            "first_class_stable_prefix": _first_true_prefix(
                agreement_rows,
                "class_stable_with_full",
            ),
            "first_stable_together_prefix": _first_true_prefix(
                agreement_rows,
                "stable_together",
            ),
            "first_both_stable_prefix": _first_both_stable_prefix(agreement_rows),
            "last_prefix": last_row["prefix_seeds"],
            "last_global_stable": last_row["global_stable_with_full"],
            "last_class_stable": last_row["class_stable_with_full"],
            "last_stable_together": last_row["stable_together"],
            "last_both_stable": str(
                _is_true(last_row["global_stable_with_full"])
                and _is_true(last_row["class_stable_with_full"])
            ).lower(),
        }
    ]


def _count_true(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if _is_true(row[field]))


def _first_true_prefix(rows: list[dict[str, Any]], field: str) -> str:
    for row in rows:
        if _is_true(row[field]):
            return str(row["prefix_seeds"])
    return "none"


def _first_both_stable_prefix(rows: list[dict[str, Any]]) -> str:
    for row in rows:
        if _is_true(row["global_stable_with_full"]) and _is_true(
            row["class_stable_with_full"]
        ):
            return str(row["prefix_seeds"])
    return "none"


def _is_true(value: Any) -> bool:
    return str(value).lower() == "true"


def _pressure_response_selection_rows(
    *,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates = _pressure_curve_response_candidates(rows)
    if not candidates:
        return []

    full_top = candidates[0]
    selection_rows = [
        _pressure_response_selection_row(
            selection_scope="full",
            seeds=seeds,
            candidate=full_top,
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
            stable_with_full=True,
            instability_causes="none",
        )
    ]
    for comparison in _prefix_pressure_response_comparisons(
        seeds=seeds,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    ):
        prefix_seed_set = set(comparison["prefix_seeds"])
        selection_rows.append(
            _pressure_response_selection_row(
                selection_scope="prefix",
                seeds=comparison["prefix_seeds"],
                candidate=comparison["top_response"],
                rows=_pressure_rows(
                    _rows_for_seeds(normal_rows, prefix_seed_set),
                    _rows_for_seeds(medium_pressure_rows, prefix_seed_set),
                    _rows_for_seeds(high_pressure_rows, prefix_seed_set),
                ),
                normal_rows=_rows_for_seeds(normal_rows, prefix_seed_set),
                medium_pressure_rows=_rows_for_seeds(
                    medium_pressure_rows,
                    prefix_seed_set,
                ),
                high_pressure_rows=_rows_for_seeds(high_pressure_rows, prefix_seed_set),
                stable_with_full=bool(comparison["stable_with_full"]),
                instability_causes=str(comparison["instability_causes"]),
            )
        )
    selection_rows.extend(
        _per_class_capture_pressure_selection_rows(
            seeds=seeds,
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
        )
    )
    return selection_rows


def _pressure_stability_agreement_rows(
    *,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if (
        len(seeds) < 2
        or not _pressure_curve_response_candidates(rows)
        or not _per_class_capture_pressure_candidates(rows)
    ):
        return []

    global_comparisons = _prefix_pressure_response_comparisons(
        seeds=seeds,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    class_comparisons = _prefix_per_class_capture_pressure_comparisons(
        seeds=seeds,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    return [
        _pressure_stability_agreement_row(
            seeds=seeds,
            global_comparison=global_comparison,
            class_comparison=class_comparison,
        )
        for global_comparison, class_comparison in zip(
            global_comparisons,
            class_comparisons,
            strict=True,
        )
    ]


def _pressure_stability_agreement_row(
    *,
    seeds: tuple[int, ...],
    global_comparison: dict[str, Any],
    class_comparison: dict[str, Any],
) -> dict[str, Any]:
    global_top = global_comparison["top_response"]
    class_top = class_comparison["top_response"]
    return {
        "full_seeds": _format_seed_set(seeds),
        "prefix_seeds": _format_seed_set(global_comparison["prefix_seeds"]),
        "global_stable_with_full": str(global_comparison["stable_with_full"]).lower(),
        "class_stable_with_full": str(class_comparison["stable_with_full"]).lower(),
        "stable_together": str(
            _stable_together(global_comparison, class_comparison)
        ).lower(),
        "global_instability_causes": global_comparison["instability_causes"],
        "class_instability_causes": class_comparison["instability_causes"],
        "global_policy": global_top["policy"],
        "global_observable": global_top["observable"],
        "global_metric": global_top["metric"],
        "global_field": global_top["field"],
        "class_policy": class_top["policy"],
        "class_observable": class_top["observable"],
        "class_metric": class_top["metric"],
        "class_field": class_top["field"],
    }


def _per_class_capture_pressure_selection_rows(
    *,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates = _per_class_capture_pressure_candidates(rows)
    if not candidates:
        return []

    full_top = candidates[0]
    selection_rows = [
        _pressure_response_selection_row(
            selection_scope="class_full",
            seeds=seeds,
            candidate=full_top,
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
            stable_with_full=True,
            instability_causes="none",
        )
    ]
    for comparison in _prefix_per_class_capture_pressure_comparisons(
        seeds=seeds,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    ):
        prefix_seed_set = set(comparison["prefix_seeds"])
        selection_rows.append(
            _pressure_response_selection_row(
                selection_scope="class_prefix",
                seeds=comparison["prefix_seeds"],
                candidate=comparison["top_response"],
                rows=_pressure_rows(
                    _rows_for_seeds(normal_rows, prefix_seed_set),
                    _rows_for_seeds(medium_pressure_rows, prefix_seed_set),
                    _rows_for_seeds(high_pressure_rows, prefix_seed_set),
                ),
                normal_rows=_rows_for_seeds(normal_rows, prefix_seed_set),
                medium_pressure_rows=_rows_for_seeds(
                    medium_pressure_rows,
                    prefix_seed_set,
                ),
                high_pressure_rows=_rows_for_seeds(high_pressure_rows, prefix_seed_set),
                stable_with_full=bool(comparison["stable_with_full"]),
                instability_causes=str(comparison["instability_causes"]),
            )
        )
    return selection_rows


def _pressure_response_selection_row(
    *,
    selection_scope: str,
    seeds: tuple[int, ...],
    candidate: dict[str, Any],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
    stable_with_full: bool,
    instability_causes: str,
) -> dict[str, Any]:
    details = _pressure_response_condition_details(
        candidate,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    source_metric_details = _pressure_response_source_metric_details(
        candidate,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    return {
        "selection_scope": selection_scope,
        "seeds": _format_seed_set(seeds),
        "stable_with_full": str(stable_with_full).lower(),
        "instability_causes": instability_causes,
        "policy": candidate["policy"],
        "observable": candidate["observable"],
        "metric": candidate["metric"],
        "field": candidate["field"],
        "source_field": candidate["source_field"],
        "value": round(float(candidate["value"]), 6),
        "abs_value": round(float(candidate["abs_value"]), 6),
        "normal_mean": details["normal_mean"],
        "medium_mean": details["medium_mean"],
        "high_mean": details["high_mean"],
        "normal_to_medium_slope": details["normal_to_medium_slope"],
        "medium_to_high_slope": details["medium_to_high_slope"],
        "curvature": details["curvature"],
        "high_minus_normal_delta": details["high_minus_normal_delta"],
        **source_metric_details,
    }


def _pressure_summary(
    *,
    normal_baseline_config: Path,
    normal_variant_config: Path,
    normal_internal_improvement_config: Path | None,
    medium_pressure_baseline_config: Path,
    medium_pressure_variant_config: Path,
    medium_pressure_internal_improvement_config: Path | None,
    high_pressure_baseline_config: Path,
    high_pressure_variant_config: Path,
    high_pressure_internal_improvement_config: Path | None,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
    stability_agreement_rows: list[dict[str, Any]],
) -> str:
    lines = [
        "# A2 attention pressure comparison",
        "",
        f"- normal baseline config: {normal_baseline_config}",
        f"- normal research-heavy config: {normal_variant_config}",
        *(
            [f"- normal internal-improvement config: {normal_internal_improvement_config}"]
            if normal_internal_improvement_config is not None
            else []
        ),
        f"- medium-pressure baseline config: {medium_pressure_baseline_config}",
        f"- medium-pressure research-heavy config: {medium_pressure_variant_config}",
        *(
            [f"- medium-pressure internal-improvement config: {medium_pressure_internal_improvement_config}"]
            if medium_pressure_internal_improvement_config is not None
            else []
        ),
        f"- high-pressure baseline config: {high_pressure_baseline_config}",
        f"- high-pressure research-heavy config: {high_pressure_variant_config}",
        *(
            [f"- high-pressure internal-improvement config: {high_pressure_internal_improvement_config}"]
            if high_pressure_internal_improvement_config is not None
            else []
        ),
        f"- seeds: {', '.join(str(seed) for seed in seeds)}",
        f"- policy rows: {len(rows)}",
        "",
        "## Fixed-policy pressure deltas",
        "",
        *[
            line
            for row in rows
            for line in _pressure_delta_lines(row)
        ],
        "",
        "## Most pressure-sensitive curve metric",
        "",
        _most_pressure_sensitive_curve_metric_line(rows),
        "",
        "## Pressure-curve response ranking",
        "",
        *_pressure_curve_response_ranking_lines(rows),
        "",
        "## Top pressure-response explanation",
        "",
        *_top_pressure_response_explanation_lines(
            rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
        ),
        "",
        "## Pressure-response interpretation",
        "",
        *_pressure_response_interpretation_lines(
            seeds=seeds,
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
        ),
        "",
        "## Pressure-condition source metric comparison",
        "",
        *_pressure_condition_source_metric_comparison_lines(
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
        ),
        "",
        "## Per-class capture-pressure interpretation",
        "",
        *_per_class_capture_pressure_interpretation_lines(
            rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
        ),
        "",
        "## Per-class capture-pressure prefix comparison",
        "",
        *_per_class_capture_pressure_prefix_comparison_lines(
            seeds=seeds,
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
        ),
        "",
        "## Pressure-response stability agreement",
        "",
        *_pressure_response_stability_agreement_lines(
            seeds=seeds,
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
        ),
        "",
        "## Pressure-stability convergence inspection",
        "",
        *_pressure_stability_convergence_lines(stability_agreement_rows, rows),
        "",
        "## Seed-set sensitivity",
        "",
        *_seed_set_sensitivity_lines(
            seeds=seeds,
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
        ),
        "",
        "## Fixed-policy pressure curves",
        "",
        *[
            line
            for row in rows
            for line in _pressure_curve_lines(row)
        ],
        "",
    ]
    return "\n".join(lines)


def _pressure_stability_convergence_lines(
    agreement_rows: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> list[str]:
    convergence_rows = _pressure_stability_convergence_rows(agreement_rows)
    if not convergence_rows:
        return ["- unavailable: no pressure stability agreement rows available."]

    row = convergence_rows[0]
    top_responses = _pressure_curve_response_candidates(rows)
    top_response_note = (
        _format_pressure_response_subject(top_responses[0])
        if top_responses
        else "unavailable"
    )
    return [
        (
            f"- full_seeds={row['full_seeds']}, prefix_count={row['prefix_count']}, "
            f"last_prefix={row['last_prefix']}"
        ),
        (
            f"- stable prefix counts: global={row['global_stable_prefixes']}, "
            f"class={row['class_stable_prefixes']}, "
            f"stable_together={row['stable_together_prefixes']}, "
            f"both_stable={row['both_stable_prefixes']}"
        ),
        (
            f"- first convergence prefixes: global={row['first_global_stable_prefix']}, "
            f"class={row['first_class_stable_prefix']}, "
            f"stable_together={row['first_stable_together_prefix']}, "
            f"both_stable={row['first_both_stable_prefix']}"
        ),
        (
            f"- last prefix state: global_stable={row['last_global_stable']}, "
            f"class_stable={row['last_class_stable']}, "
            f"stable_together={row['last_stable_together']}, "
            f"both_stable={row['last_both_stable']}"
        ),
        (
            "- convergence vs interpretation: pressure-response interpretation selects "
            f"{top_response_note}; first_global_stable_prefix="
            f"{row['first_global_stable_prefix']}, last_prefix={row['last_prefix']}, "
            f"last_global_stable={row['last_global_stable']}."
        ),
    ]


def _per_class_capture_pressure_prefix_comparison_lines(
    *,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[str]:
    if len(seeds) < 2:
        return ["- unavailable: at least two seeds are required for prefix comparison."]

    full_candidates = _per_class_capture_pressure_candidates(rows)
    if not full_candidates:
        return ["- no per-class capture-pressure responses available for prefix comparison."]

    prefix_comparisons = _prefix_per_class_capture_pressure_comparisons(
        seeds=seeds,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    last_prefix = prefix_comparisons[-1]
    full_top = full_candidates[0]
    prefix_top = last_prefix["top_response"]

    return [
        (
            f"- comparison: full_seeds={_format_seed_set(seeds)}, "
            f"prefix_seeds={_format_seed_set(last_prefix['prefix_seeds'])}"
        ),
        f"- full class top response: {_format_pressure_response_candidate(full_top)}",
        f"- prefix class top response: {_format_pressure_response_candidate(prefix_top)}",
        (
            "- class top response stable across prefix: "
            f"{str(last_prefix['stable_with_full']).lower()}"
        ),
        (
            "- class top response stable across all prefixes: "
            f"{str(all(comparison['stable_with_full'] for comparison in prefix_comparisons)).lower()}"
        ),
        f"- class prefix instability causes: {last_prefix['instability_causes']}",
        "",
        "| prefix_seeds | class_top_response | stable_with_full | instability_causes |",
        "| --- | --- | --- | --- |",
        *[
            (
                f"| {_format_seed_set(comparison['prefix_seeds'])} | "
                f"{_format_pressure_response_candidate(comparison['top_response'])} | "
                f"{str(comparison['stable_with_full']).lower()} | "
                f"{comparison['instability_causes']} |"
            )
            for comparison in prefix_comparisons
        ],
    ]


def _pressure_response_stability_agreement_lines(
    *,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[str]:
    if len(seeds) < 2:
        return ["- unavailable: at least two seeds are required for stability agreement."]
    if not _pressure_curve_response_candidates(rows):
        return ["- no pressure-curve responses available for stability agreement."]
    if not _per_class_capture_pressure_candidates(rows):
        return [
            "- no per-class capture-pressure responses available for stability agreement."
        ]

    global_comparisons = _prefix_pressure_response_comparisons(
        seeds=seeds,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    class_comparisons = _prefix_per_class_capture_pressure_comparisons(
        seeds=seeds,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    comparison_pairs = list(zip(global_comparisons, class_comparisons, strict=True))
    last_global, last_class = comparison_pairs[-1]

    return [
        (
            f"- comparison: full_seeds={_format_seed_set(seeds)}, "
            f"prefix_seeds={_format_seed_set(last_global['prefix_seeds'])}"
        ),
        (
            "- last prefix stable together: "
            f"{str(_stable_together(last_global, last_class)).lower()}"
        ),
        (
            "- all prefixes stable together: "
            f"{str(all(_stable_together(global_row, class_row) for global_row, class_row in comparison_pairs)).lower()}"
        ),
        (
            "- last prefix details: global_stable="
            f"{str(last_global['stable_with_full']).lower()}, "
            f"class_stable={str(last_class['stable_with_full']).lower()}"
        ),
        "",
        (
            "| prefix_seeds | global_stable_with_full | class_stable_with_full | "
            "stable_together | global_instability_causes | class_instability_causes |"
        ),
        "| --- | --- | --- | --- | --- | --- |",
        *[
            (
                f"| {_format_seed_set(global_row['prefix_seeds'])} | "
                f"{str(global_row['stable_with_full']).lower()} | "
                f"{str(class_row['stable_with_full']).lower()} | "
                f"{str(_stable_together(global_row, class_row)).lower()} | "
                f"{global_row['instability_causes']} | "
                f"{class_row['instability_causes']} |"
            )
            for global_row, class_row in comparison_pairs
        ],
    ]


def _stable_together(
    global_comparison: dict[str, Any],
    class_comparison: dict[str, Any],
) -> bool:
    return bool(global_comparison["stable_with_full"]) == bool(
        class_comparison["stable_with_full"]
    )


def _prefix_per_class_capture_pressure_comparisons(
    *,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    full_top = _per_class_capture_pressure_candidates(rows)[0]
    comparisons: list[dict[str, Any]] = []
    for prefix_length in range(1, len(seeds)):
        prefix_seeds = seeds[:prefix_length]
        prefix_seed_set = set(prefix_seeds)
        prefix_rows = _pressure_rows(
            _rows_for_seeds(normal_rows, prefix_seed_set),
            _rows_for_seeds(medium_pressure_rows, prefix_seed_set),
            _rows_for_seeds(high_pressure_rows, prefix_seed_set),
        )
        prefix_top = _per_class_capture_pressure_candidates(prefix_rows)[0]
        comparisons.append(
            {
                "prefix_seeds": prefix_seeds,
                "top_response": prefix_top,
                "stable_with_full": _same_pressure_response(full_top, prefix_top),
                "instability_causes": _pressure_response_instability_causes(
                    full_top,
                    prefix_top,
                ),
            }
        )
    return comparisons


def _per_class_capture_pressure_interpretation_lines(
    rows: list[dict[str, Any]],
    *,
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[str]:
    candidates = _per_class_capture_pressure_candidates(rows)
    if not candidates:
        return ["- no per-class capture-pressure responses available for interpretation."]

    policies = tuple(dict.fromkeys(str(row["policy"]) for row in rows))
    return [
        _format_per_class_capture_pressure_interpretation_line(
            "overall class response",
            candidates[0],
            rows=rows,
            normal_rows=normal_rows,
            medium_pressure_rows=medium_pressure_rows,
            high_pressure_rows=high_pressure_rows,
        ),
        *[
            _format_per_class_capture_pressure_interpretation_line(
                f"{policy} class response",
                next(candidate for candidate in candidates if candidate["policy"] == policy),
                rows=rows,
                normal_rows=normal_rows,
                medium_pressure_rows=medium_pressure_rows,
                high_pressure_rows=high_pressure_rows,
            )
            for policy in policies
            if any(candidate["policy"] == policy for candidate in candidates)
        ],
    ]


def _per_class_capture_pressure_candidates(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    class_prefixes = tuple(
        f"{class_name}_capture_pressure_"
        for class_name in ATTENTION_CLASSES
    )
    return [
        candidate
        for candidate in _pressure_curve_response_candidates(rows)
        if str(candidate["observable_prefix"]).startswith(class_prefixes)
    ]


def _format_per_class_capture_pressure_interpretation_line(
    label: str,
    candidate: dict[str, Any],
    *,
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> str:
    class_name, statistic = _per_class_capture_pressure_dimensions(candidate)
    details = _pressure_response_condition_details(
        candidate,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    return (
        f"- {label}: policy={candidate['policy']}, "
        f"class={class_name.replace('_', ' ')}, statistic={statistic.replace('_', ' ')}, "
        f"metric={candidate['metric']}; condition means move "
        f"{details['normal_mean']} -> {details['medium_mean']} -> {details['high_mean']} "
        f"with normal_to_medium_slope={details['normal_to_medium_slope']}, "
        f"medium_to_high_slope={details['medium_to_high_slope']}, "
        f"curvature={details['curvature']}, and high_minus_normal_delta="
        f"{details['high_minus_normal_delta']}."
    )


def _per_class_capture_pressure_dimensions(
    candidate: dict[str, Any],
) -> tuple[str, str]:
    observable_prefix = str(candidate["observable_prefix"])
    for class_name in ATTENTION_CLASSES:
        prefix = f"{class_name}_capture_pressure_"
        if observable_prefix.startswith(prefix):
            return class_name, observable_prefix.removeprefix(prefix)
    raise ValueError(f"Not a per-class capture-pressure response: {observable_prefix}")


def _pressure_response_interpretation_lines(
    *,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[str]:
    candidates = _pressure_curve_response_candidates(rows)
    if not candidates:
        return ["- no pressure-curve responses available for interpretation."]

    full_top = candidates[0]
    full_details = _pressure_response_condition_details(
        full_top,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )

    lines = [
        (
            "- full-seed interpretation: "
            f"{_format_pressure_response_subject(full_top)} is the largest absolute "
            f"pressure response; condition means move "
            f"{full_details['normal_mean']} -> {full_details['medium_mean']} -> "
            f"{full_details['high_mean']} with normal_to_medium_slope="
            f"{full_details['normal_to_medium_slope']}, medium_to_high_slope="
            f"{full_details['medium_to_high_slope']}, curvature="
            f"{full_details['curvature']}, and high_minus_normal_delta="
            f"{full_details['high_minus_normal_delta']}."
        )
    ]

    if len(seeds) < 2:
        lines.append(
            "- prefix interpretation: unavailable because at least two seeds are required."
        )
        return lines

    prefix_comparisons = _prefix_pressure_response_comparisons(
        seeds=seeds,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    last_prefix = prefix_comparisons[-1]
    if last_prefix["stable_with_full"]:
        lines.append(
            (
                "- prefix interpretation: the last prefix selects the same policy, "
                "observable, and metric, so the leading pressure-response explanation "
                "is stable for the checked prefix."
            )
        )
        return lines

    prefix_top = last_prefix["top_response"]
    prefix_seed_set = set(last_prefix["prefix_seeds"])
    prefix_rows = _pressure_rows(
        _rows_for_seeds(normal_rows, prefix_seed_set),
        _rows_for_seeds(medium_pressure_rows, prefix_seed_set),
        _rows_for_seeds(high_pressure_rows, prefix_seed_set),
    )
    prefix_details = _pressure_response_condition_details(
        prefix_top,
        rows=prefix_rows,
        normal_rows=_rows_for_seeds(normal_rows, prefix_seed_set),
        medium_pressure_rows=_rows_for_seeds(medium_pressure_rows, prefix_seed_set),
        high_pressure_rows=_rows_for_seeds(high_pressure_rows, prefix_seed_set),
    )
    lines.append(
        (
            "- prefix interpretation: instability causes="
            f"{last_prefix['instability_causes']} because prefix_seeds="
            f"{_format_seed_set(last_prefix['prefix_seeds'])} select "
            f"{_format_pressure_response_subject(prefix_top)} with condition means "
            f"{prefix_details['normal_mean']} -> {prefix_details['medium_mean']} -> "
            f"{prefix_details['high_mean']}, normal_to_medium_slope="
            f"{prefix_details['normal_to_medium_slope']}, medium_to_high_slope="
            f"{prefix_details['medium_to_high_slope']}, curvature="
            f"{prefix_details['curvature']}, and high_minus_normal_delta="
            f"{prefix_details['high_minus_normal_delta']}; the full seed set selects "
            f"{_format_pressure_response_subject(full_top)}."
        )
    )
    return lines


def _pressure_condition_source_metric_comparison_lines(
    *,
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[str]:
    candidates = _pressure_curve_response_candidates(rows)
    if not candidates:
        return ["- no pressure-curve responses available for condition comparison."]

    top = candidates[0]
    policy = str(top["policy"])
    source_field = str(top["source_field"])
    return [
        (
            f"- selected source metric: {_format_pressure_response_subject(top)} "
            f"source_field={source_field}"
        ),
        (
            "| pressure_condition | source_metric_mean | source_metric_min | "
            "source_metric_max | per_seed_values |"
        ),
        "| --- | ---: | ---: | ---: | --- |",
        _pressure_condition_source_metric_row(
            "normal",
            normal_rows,
            policy=policy,
            source_field=source_field,
        ),
        _pressure_condition_source_metric_row(
            "medium",
            medium_pressure_rows,
            policy=policy,
            source_field=source_field,
        ),
        _pressure_condition_source_metric_row(
            "high",
            high_pressure_rows,
            policy=policy,
            source_field=source_field,
        ),
    ]


def _pressure_condition_source_metric_row(
    pressure_condition: str,
    rows: list[dict[str, Any]],
    *,
    policy: str,
    source_field: str,
) -> str:
    policy_rows = sorted(
        [row for row in rows if row["policy"] == policy],
        key=lambda row: int(row["seed"]),
    )
    values = [float(row[source_field]) for row in policy_rows]
    per_seed_values = ", ".join(
        f"{row['seed']}:{round(float(row[source_field]), 6)}"
        for row in policy_rows
    )
    return (
        f"| {pressure_condition} | {round(sum(values) / len(values), 6)} | "
        f"{round(min(values), 6)} | {round(max(values), 6)} | {per_seed_values} |"
    )


def _pressure_response_source_metric_details(
    candidate: dict[str, Any],
    *,
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    policy = str(candidate["policy"])
    source_field = str(candidate["source_field"])
    return {
        **_source_metric_condition_details(
            "normal",
            normal_rows,
            policy=policy,
            source_field=source_field,
        ),
        **_source_metric_condition_details(
            "medium",
            medium_pressure_rows,
            policy=policy,
            source_field=source_field,
        ),
        **_source_metric_condition_details(
            "high",
            high_pressure_rows,
            policy=policy,
            source_field=source_field,
        ),
    }


def _source_metric_condition_details(
    pressure_condition: str,
    rows: list[dict[str, Any]],
    *,
    policy: str,
    source_field: str,
) -> dict[str, Any]:
    policy_rows = sorted(
        [row for row in rows if row["policy"] == policy],
        key=lambda row: int(row["seed"]),
    )
    values = [float(row[source_field]) for row in policy_rows]
    return {
        f"source_metric_{pressure_condition}_mean": round(sum(values) / len(values), 6),
        f"source_metric_{pressure_condition}_min": round(min(values), 6),
        f"source_metric_{pressure_condition}_max": round(max(values), 6),
        f"source_metric_{pressure_condition}_per_seed_values": "|".join(
            f"{row['seed']}:{round(float(row[source_field]), 6)}"
            for row in policy_rows
        ),
    }


def _pressure_response_condition_details(
    candidate: dict[str, Any],
    *,
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> dict[str, float]:
    policy = str(candidate["policy"])
    source_field = str(candidate["source_field"])
    observable_prefix = str(candidate["observable_prefix"])
    pressure_row = next(row for row in rows if row["policy"] == policy)
    return {
        "normal_mean": _policy_condition_mean(normal_rows, policy, source_field),
        "medium_mean": _policy_condition_mean(
            medium_pressure_rows,
            policy,
            source_field,
        ),
        "high_mean": _policy_condition_mean(high_pressure_rows, policy, source_field),
        "normal_to_medium_slope": float(
            pressure_row[f"{observable_prefix}_normal_to_medium_slope"]
        ),
        "medium_to_high_slope": float(
            pressure_row[f"{observable_prefix}_medium_to_high_slope"]
        ),
        "curvature": float(pressure_row[f"{observable_prefix}_pressure_curvature"]),
        "high_minus_normal_delta": float(
            pressure_row[_pressure_delta_field(observable_prefix)]
        ),
    }


def _format_pressure_response_subject(candidate: dict[str, Any]) -> str:
    return (
        f"policy={candidate['policy']} observable={candidate['observable']} "
        f"metric={candidate['metric']}"
    )


def _seed_set_sensitivity_lines(
    *,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[str]:
    if len(seeds) < 2:
        return ["- unavailable: at least two seeds are required for prefix sensitivity."]

    prefix_comparisons = _prefix_pressure_response_comparisons(
        seeds=seeds,
        rows=rows,
        normal_rows=normal_rows,
        medium_pressure_rows=medium_pressure_rows,
        high_pressure_rows=high_pressure_rows,
    )
    last_prefix = prefix_comparisons[-1]
    full_top = _pressure_curve_response_candidates(rows)[0]
    prefix_top = last_prefix["top_response"]

    return [
        (
            f"- comparison: full_seeds={_format_seed_set(seeds)}, "
            f"prefix_seeds={_format_seed_set(last_prefix['prefix_seeds'])}"
        ),
        f"- full top response: {_format_pressure_response_candidate(full_top)}",
        f"- prefix top response: {_format_pressure_response_candidate(prefix_top)}",
        f"- top response stable across prefix: {str(last_prefix['stable_with_full']).lower()}",
        (
            "- top response stable across all prefixes: "
            f"{str(all(comparison['stable_with_full'] for comparison in prefix_comparisons)).lower()}"
        ),
        f"- prefix instability causes: {last_prefix['instability_causes']}",
        "",
        "| prefix_seeds | top_response | stable_with_full | instability_causes |",
        "| --- | --- | --- | --- |",
        *[
            (
                f"| {_format_seed_set(comparison['prefix_seeds'])} | "
                f"{_format_pressure_response_candidate(comparison['top_response'])} | "
                f"{str(comparison['stable_with_full']).lower()} | "
                f"{comparison['instability_causes']} |"
            )
            for comparison in prefix_comparisons
        ],
    ]


def _prefix_pressure_response_comparisons(
    *,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    full_top = _pressure_curve_response_candidates(rows)[0]
    comparisons: list[dict[str, Any]] = []
    for prefix_length in range(1, len(seeds)):
        prefix_seeds = seeds[:prefix_length]
        prefix_seed_set = set(prefix_seeds)
        prefix_rows = _pressure_rows(
            _rows_for_seeds(normal_rows, prefix_seed_set),
            _rows_for_seeds(medium_pressure_rows, prefix_seed_set),
            _rows_for_seeds(high_pressure_rows, prefix_seed_set),
        )
        prefix_top = _pressure_curve_response_candidates(prefix_rows)[0]
        comparisons.append(
            {
                "prefix_seeds": prefix_seeds,
                "top_response": prefix_top,
                "stable_with_full": _same_pressure_response(full_top, prefix_top),
                "instability_causes": _pressure_response_instability_causes(
                    full_top,
                    prefix_top,
                ),
            }
        )
    return comparisons


def _pressure_response_instability_causes(
    full_top: dict[str, Any],
    prefix_top: dict[str, Any],
) -> str:
    changed = []
    if full_top["policy"] != prefix_top["policy"]:
        changed.append("policy")
    if full_top["observable_prefix"] != prefix_top["observable_prefix"]:
        changed.append("observable")
    if full_top["metric_suffix"] != prefix_top["metric_suffix"]:
        changed.append("metric")
    if not changed:
        return "none"
    return ",".join(changed)


def _same_pressure_response(
    first: dict[str, Any],
    second: dict[str, Any],
) -> bool:
    return (
        first["policy"],
        first["observable_prefix"],
        first["metric_suffix"],
    ) == (
        second["policy"],
        second["observable_prefix"],
        second["metric_suffix"],
    )


def _rows_for_seeds(
    rows: list[dict[str, Any]],
    seeds: set[int],
) -> list[dict[str, Any]]:
    return [row for row in rows if int(row["seed"]) in seeds]


def _format_seed_set(seeds: tuple[int, ...]) -> str:
    return ",".join(str(seed) for seed in seeds)


def _format_pressure_response_candidate(candidate: dict[str, Any]) -> str:
    return (
        f"policy={candidate['policy']}, observable={candidate['observable']}, "
        f"metric={candidate['metric']}, field={candidate['field']}, "
        f"value={round(float(candidate['value']), 6)}, "
        f"abs_value={round(float(candidate['abs_value']), 6)}"
    )


def _most_pressure_sensitive_curve_metric_line(rows: list[dict[str, Any]]) -> str:
    candidates = _pressure_curve_response_candidates(rows)
    if not candidates:
        return "- none: no pressure curve rows available"

    top = candidates[0]
    return (
        f"- policy={top['policy']}, observable={top['observable']}, "
        f"metric={top['metric']}, field={top['field']}, "
        f"value={round(float(top['value']), 6)}, "
        f"abs_value={round(float(top['abs_value']), 6)}"
    )


def _pressure_curve_response_ranking_lines(rows: list[dict[str, Any]]) -> list[str]:
    candidates = _pressure_curve_response_candidates(rows)
    if not candidates:
        return ["- none: no pressure curve rows available"]

    return [
        "| rank | policy | observable | metric | field | value | abs_value |",
        "| ---: | --- | --- | --- | --- | ---: | ---: |",
        *[
            "| "
            f"{rank} | {candidate['policy']} | {candidate['observable']} | "
            f"{candidate['metric']} | {candidate['field']} | "
            f"{round(float(candidate['value']), 6)} | "
            f"{round(float(candidate['abs_value']), 6)} |"
            for rank, candidate in enumerate(candidates, start=1)
        ],
    ]


def _pressure_curve_response_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for row in rows:
        for observable_prefix, observable_label, source_field in PRESSURE_CURVE_OBSERVABLES:
            for metric_suffix, metric_label in PRESSURE_CURVE_METRICS:
                field = f"{observable_prefix}_{metric_suffix}"
                value = float(row[field])
                candidates.append(
                    {
                        "policy": row["policy"],
                        "observable": observable_label,
                        "observable_prefix": observable_prefix,
                        "source_field": source_field,
                        "metric": metric_label,
                        "metric_suffix": metric_suffix,
                        "field": field,
                        "value": value,
                        "abs_value": abs(value),
                    }
                )

    candidates.sort(
        key=lambda candidate: (
            -float(candidate["abs_value"]),
            str(candidate["policy"]),
            str(candidate["observable"]),
            str(candidate["metric"]),
        )
    )
    return candidates


def _top_pressure_response_explanation_lines(
    rows: list[dict[str, Any]],
    *,
    normal_rows: list[dict[str, Any]],
    medium_pressure_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[str]:
    candidates = _pressure_curve_response_candidates(rows)
    if not candidates:
        return ["- none: no pressure curve rows available"]

    top = candidates[0]
    policy = str(top["policy"])
    source_field = str(top["source_field"])
    pressure_row = next(row for row in rows if row["policy"] == policy)
    normal_mean = _policy_condition_mean(normal_rows, policy, source_field)
    medium_mean = _policy_condition_mean(medium_pressure_rows, policy, source_field)
    high_mean = _policy_condition_mean(high_pressure_rows, policy, source_field)
    observable_prefix = str(top["observable_prefix"])
    delta_field = _pressure_delta_field(str(top["observable_prefix"]))
    normal_to_medium_field = f"{observable_prefix}_normal_to_medium_slope"
    medium_to_high_field = f"{observable_prefix}_medium_to_high_slope"
    curvature_field = f"{observable_prefix}_pressure_curvature"

    return [
        (
            f"- selected response: policy={policy}, observable={top['observable']}, "
            f"metric={top['metric']}, field={top['field']}"
        ),
        (
            f"- condition means: normal={normal_mean}, "
            f"medium_pressure={medium_mean}, high_pressure={high_mean}"
        ),
        (
            f"- pressure curve: normal_to_medium_slope="
            f"{pressure_row[normal_to_medium_field]}, "
            f"medium_to_high_slope={pressure_row[medium_to_high_field]}, "
            f"curvature={pressure_row[curvature_field]}"
        ),
        (
            f"- high-minus-normal delta: {pressure_row[delta_field]} "
            f"({delta_field})"
        ),
    ]


def _policy_condition_mean(
    rows: list[dict[str, Any]],
    policy: str,
    source_field: str,
) -> float:
    policy_rows = [row for row in rows if row["policy"] == policy]
    return _mean(policy_rows, source_field)


def _pressure_delta_field(observable_prefix: str) -> str:
    delta_fields = {
        "value_weighted_completed": "value_weighted_completed_mean_delta",
        "tasks_completed": "tasks_completed_mean_delta",
        "queue_depth": "queue_depth_mean_delta",
        "queued_task_age_mean_final": "queued_task_age_mean_final_delta",
        "queued_task_age_max_peak": "queued_task_age_max_peak_delta",
        "attention_capture_pressure_max_final": "attention_capture_pressure_max_final_delta",
        "attention_capture_pressure_mean_over_ticks": (
            "attention_capture_pressure_mean_over_ticks_delta"
        ),
        "attention_capture_pressure_peak": "attention_capture_pressure_peak_delta",
    }
    delta_fields.update(
        {
            f"{class_name}_capture_pressure_{statistic}": (
                f"{class_name}_capture_pressure_{statistic}_delta"
            )
            for class_name in ATTENTION_CLASSES
            for statistic in ("final", "mean_over_ticks", "peak")
        }
    )
    return delta_fields[observable_prefix]


def _pressure_delta_lines(row: dict[str, Any]) -> list[str]:
    return [
        f"- {row['policy']}: normal_total_steps={row['normal_total_steps']}, "
        f"medium_pressure_total_steps={row['medium_pressure_total_steps']}, "
        f"high_pressure_total_steps={row['high_pressure_total_steps']}, "
        f"regime_rate_deltas={row['regime_rate_deltas']}, "
        f"regime_count_deltas={row['regime_count_deltas']}",
        f"- {row['policy']} value-weighted completed work mean pressure delta: "
        f"{row['value_weighted_completed_mean_delta']}",
        f"- {row['policy']} tasks completed mean pressure delta: "
        f"{row['tasks_completed_mean_delta']}",
        f"- {row['policy']} final queue depth mean pressure delta: "
        f"{row['queue_depth_mean_delta']}",
        f"- {row['policy']} final queued task mean age pressure delta: "
        f"{row['queued_task_age_mean_final_delta']}",
        f"- {row['policy']} mean queued task mean age pressure delta: "
        f"{row['queued_task_age_mean_over_ticks_delta']}",
        f"- {row['policy']} peak queued task max age pressure delta: "
        f"{row['queued_task_age_max_peak_delta']}",
        f"- {row['policy']} final attention capture pressure delta: "
        f"{row['attention_capture_pressure_max_final_delta']}",
        f"- {row['policy']} mean attention capture pressure delta: "
        f"{row['attention_capture_pressure_mean_over_ticks_delta']}",
        f"- {row['policy']} peak attention capture pressure delta: "
        f"{row['attention_capture_pressure_peak_delta']}",
        *[
            f"- {row['policy']} {class_name.replace('_', ' ')} {label} capture pressure delta: "
            f"{row[f'{class_name}_capture_pressure_{statistic}_delta']}"
            for class_name in ATTENTION_CLASSES
            for statistic, label in (
                ("final", "final"),
                ("mean_over_ticks", "mean"),
                ("peak", "peak"),
            )
        ],
    ]


def _pressure_curve_lines(row: dict[str, Any]) -> list[str]:
    return [
        f"- {row['policy']} value-weighted completed work pressure curve: "
        f"normal_to_medium_slope={row['value_weighted_completed_normal_to_medium_slope']}, "
        f"medium_to_high_slope={row['value_weighted_completed_medium_to_high_slope']}, "
        f"curvature={row['value_weighted_completed_pressure_curvature']}",
        f"- {row['policy']} tasks completed pressure curve: "
        f"normal_to_medium_slope={row['tasks_completed_normal_to_medium_slope']}, "
        f"medium_to_high_slope={row['tasks_completed_medium_to_high_slope']}, "
        f"curvature={row['tasks_completed_pressure_curvature']}",
        f"- {row['policy']} final queue depth pressure curve: "
        f"normal_to_medium_slope={row['queue_depth_normal_to_medium_slope']}, "
        f"medium_to_high_slope={row['queue_depth_medium_to_high_slope']}, "
        f"curvature={row['queue_depth_pressure_curvature']}",
        f"- {row['policy']} final queued task mean age pressure curve: "
        f"normal_to_medium_slope={row['queued_task_age_mean_final_normal_to_medium_slope']}, "
        f"medium_to_high_slope={row['queued_task_age_mean_final_medium_to_high_slope']}, "
        f"curvature={row['queued_task_age_mean_final_pressure_curvature']}",
        f"- {row['policy']} peak queued task max age pressure curve: "
        f"normal_to_medium_slope={row['queued_task_age_max_peak_normal_to_medium_slope']}, "
        f"medium_to_high_slope={row['queued_task_age_max_peak_medium_to_high_slope']}, "
        f"curvature={row['queued_task_age_max_peak_pressure_curvature']}",
        f"- {row['policy']} final attention capture pressure curve: "
        f"normal_to_medium_slope={row['attention_capture_pressure_max_final_normal_to_medium_slope']}, "
        f"medium_to_high_slope={row['attention_capture_pressure_max_final_medium_to_high_slope']}, "
        f"curvature={row['attention_capture_pressure_max_final_pressure_curvature']}",
        f"- {row['policy']} mean attention capture pressure curve: "
        f"normal_to_medium_slope={row['attention_capture_pressure_mean_over_ticks_normal_to_medium_slope']}, "
        f"medium_to_high_slope={row['attention_capture_pressure_mean_over_ticks_medium_to_high_slope']}, "
        f"curvature={row['attention_capture_pressure_mean_over_ticks_pressure_curvature']}",
        f"- {row['policy']} peak attention capture pressure curve: "
        f"normal_to_medium_slope={row['attention_capture_pressure_peak_normal_to_medium_slope']}, "
        f"medium_to_high_slope={row['attention_capture_pressure_peak_medium_to_high_slope']}, "
        f"curvature={row['attention_capture_pressure_peak_pressure_curvature']}",
        *[
            f"- {row['policy']} {class_name.replace('_', ' ')} {label} capture pressure curve: "
            f"normal_to_medium_slope={row[f'{class_name}_capture_pressure_{statistic}_normal_to_medium_slope']}, "
            f"medium_to_high_slope={row[f'{class_name}_capture_pressure_{statistic}_medium_to_high_slope']}, "
            f"curvature={row[f'{class_name}_capture_pressure_{statistic}_pressure_curvature']}"
            for class_name in ATTENTION_CLASSES
            for statistic, label in (
                ("final", "final"),
                ("mean_over_ticks", "mean"),
                ("peak", "peak"),
            )
        ],
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare normal, medium, and high-pressure A2 attention-policy fixtures."
    )
    parser.add_argument("--normal-baseline-config", default=str(DEFAULT_BASELINE_CONFIG))
    parser.add_argument("--normal-variant-config", default=str(DEFAULT_VARIANT_CONFIG))
    parser.add_argument(
        "--normal-internal-improvement-config",
        default=str(DEFAULT_INTERNAL_IMPROVEMENT_CONFIG),
        help="Optional normal-pressure third policy config; pass an empty string to skip it.",
    )
    parser.add_argument(
        "--medium-pressure-baseline-config",
        default=str(DEFAULT_MEDIUM_PRESSURE_BASELINE_CONFIG),
    )
    parser.add_argument(
        "--medium-pressure-variant-config",
        default=str(DEFAULT_MEDIUM_PRESSURE_VARIANT_CONFIG),
    )
    parser.add_argument(
        "--medium-pressure-internal-improvement-config",
        default=str(DEFAULT_MEDIUM_PRESSURE_INTERNAL_IMPROVEMENT_CONFIG),
        help="Optional medium-pressure third policy config; pass an empty string to skip it.",
    )
    parser.add_argument(
        "--high-pressure-baseline-config",
        default=str(DEFAULT_HIGH_PRESSURE_BASELINE_CONFIG),
    )
    parser.add_argument(
        "--high-pressure-variant-config",
        default=str(DEFAULT_HIGH_PRESSURE_VARIANT_CONFIG),
    )
    parser.add_argument(
        "--high-pressure-internal-improvement-config",
        default=str(DEFAULT_HIGH_PRESSURE_INTERNAL_IMPROVEMENT_CONFIG),
        help="Optional high-pressure third policy config; pass an empty string to skip it.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_SEEDS),
        help="Deterministic seed set to run for each policy and pressure condition.",
    )
    parser.add_argument("--out", required=True, help="Output directory for pressure comparison artifacts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_pressure_comparison(
            normal_baseline_config=args.normal_baseline_config,
            normal_variant_config=args.normal_variant_config,
            normal_internal_improvement_config=args.normal_internal_improvement_config or None,
            medium_pressure_baseline_config=args.medium_pressure_baseline_config,
            medium_pressure_variant_config=args.medium_pressure_variant_config,
            medium_pressure_internal_improvement_config=(
                args.medium_pressure_internal_improvement_config or None
            ),
            high_pressure_baseline_config=args.high_pressure_baseline_config,
            high_pressure_variant_config=args.high_pressure_variant_config,
            high_pressure_internal_improvement_config=(
                args.high_pressure_internal_improvement_config or None
            ),
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
