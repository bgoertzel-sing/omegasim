"""Deterministic comparison runner for A2 attention-policy fixtures."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from ohdyn.config import ATTENTION_CLASSES
from ohdyn.run import run_experiment
from ohdyn.sim import SimulationResult


DEFAULT_BASELINE_CONFIG = Path("configs/a2_attention_smoke.yaml")
DEFAULT_VARIANT_CONFIG = Path("configs/a2_attention_research_heavy.yaml")
DEFAULT_INTERNAL_IMPROVEMENT_CONFIG = Path("configs/a2_attention_internal_improvement.yaml")
DEFAULT_SEEDS = (1, 2, 3)
COMPARISON_FIELDS = (
    "policy",
    "config",
    "seed",
    "run_dir",
    "value_weighted_completed_total",
    "tasks_completed_total",
    "queue_depth",
    "queued_task_age_mean_final",
    "queued_task_age_mean_over_ticks",
    "queued_task_age_max_peak",
    "near_term_external_completed_total",
    "long_term_research_completed_total",
    "internal_improvement_completed_total",
    "housekeeping_completed_total",
    "queue_depth_trajectory",
    "queued_task_age_mean_trajectory",
    "value_weighted_completed_total_trajectory",
    "attention_capture_pressure_max_final",
    "attention_capture_pressure_mean_over_ticks",
    "attention_capture_pressure_peak",
    "attention_capture_pressure_max_trajectory",
    "queue_depth_step_deltas",
    "queued_task_age_mean_step_deltas",
    "value_weighted_completed_total_step_deltas",
    "attention_capture_pressure_max_step_deltas",
    "near_term_external_completed_total_trajectory",
    "long_term_research_completed_total_trajectory",
    "internal_improvement_completed_total_trajectory",
    "housekeeping_completed_total_trajectory",
    "near_term_external_capture_pressure_trajectory",
    "long_term_research_capture_pressure_trajectory",
    "internal_improvement_capture_pressure_trajectory",
    "housekeeping_capture_pressure_trajectory",
)


@dataclass(frozen=True)
class PolicyAggregate:
    policy: str
    seeds: int
    value_weighted_completed_mean: float
    tasks_completed_mean: float
    queue_depth_mean: float
    queued_task_age_mean_final_mean: float
    queued_task_age_mean_over_ticks_mean: float
    queued_task_age_max_peak_mean: float
    near_term_external_completed_mean: float
    long_term_research_completed_mean: float
    internal_improvement_completed_mean: float
    housekeeping_completed_mean: float
    queue_depth_final_trajectory_mean: float
    queued_task_age_mean_trajectory_final_mean: float
    value_weighted_trajectory_final_mean: float
    attention_capture_pressure_max_final_mean: float
    attention_capture_pressure_mean_over_ticks_mean: float
    attention_capture_pressure_peak_mean: float
    queue_depth_step_delta_mean: float
    queue_depth_step_delta_min: float
    queue_depth_step_delta_max: float
    queued_task_age_mean_step_delta_mean: float
    queued_task_age_mean_step_delta_min: float
    queued_task_age_mean_step_delta_max: float
    value_weighted_step_delta_mean: float
    value_weighted_step_delta_min: float
    value_weighted_step_delta_max: float
    attention_capture_pressure_max_step_delta_mean: float
    attention_capture_pressure_max_step_delta_min: float
    attention_capture_pressure_max_step_delta_max: float


def run_comparison(
    *,
    baseline_config: str | Path = DEFAULT_BASELINE_CONFIG,
    variant_config: str | Path = DEFAULT_VARIANT_CONFIG,
    internal_improvement_config: str | Path | None = DEFAULT_INTERNAL_IMPROVEMENT_CONFIG,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    out_dir: str | Path,
) -> list[dict[str, Any]]:
    _validate_seeds(seeds)
    output_path = Path(out_dir)
    _ensure_comparison_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    policies = [
        ("baseline", Path(baseline_config)),
        ("research_heavy", Path(variant_config)),
    ]
    if internal_improvement_config is not None:
        policies.append(("internal_improvement", Path(internal_improvement_config)))

    for policy, config_path in policies:
        for seed in seeds:
            run_dir = output_path / f"{policy}_seed{seed}"
            result = run_experiment(config_path, seed=seed, out_dir=run_dir)
            rows.append(_comparison_row(policy, config_path, seed, run_dir, result))

    _write_csv(output_path / "comparison_metrics.csv", rows)
    aggregates = _policy_aggregates(rows)
    (output_path / "summary.md").write_text(
        _comparison_summary(
            baseline_config=Path(baseline_config),
            variant_config=Path(variant_config),
            internal_improvement_config=(
                Path(internal_improvement_config)
                if internal_improvement_config is not None
                else None
            ),
            seeds=seeds,
            aggregates=aggregates,
            rows=rows,
        )
    )
    return rows


def _validate_seeds(seeds: tuple[int, ...]) -> None:
    if not seeds:
        raise ValueError("At least one seed is required.")
    invalid = [seed for seed in seeds if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0]
    if invalid:
        raise ValueError("Seeds must be non-negative integers.")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must not contain duplicates.")


def _ensure_comparison_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        artifact_name
        for artifact_name in ("comparison_metrics.csv", "summary.md")
        if (output_path / artifact_name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains comparison artifacts: {names}")


def _comparison_row(
    policy: str,
    config_path: Path,
    seed: int,
    run_dir: Path,
    result: SimulationResult,
) -> dict[str, Any]:
    last = result.metrics[-1]
    return {
        "policy": policy,
        "config": str(config_path),
        "seed": seed,
        "run_dir": run_dir.name,
        "value_weighted_completed_total": last["attention_value_weighted_completed_total"],
        "tasks_completed_total": last["tasks_completed_total"],
        "queue_depth": last["queue_depth"],
        "queued_task_age_mean_final": last["queued_task_age_mean_tick"],
        "queued_task_age_mean_over_ticks": _mean_metric(result, "queued_task_age_mean_tick"),
        "queued_task_age_max_peak": max(
            int(row["queued_task_age_max_tick"])
            for row in result.metrics
        ),
        "near_term_external_completed_total": last[
            "attention_near_term_external_completed_total"
        ],
        "long_term_research_completed_total": last[
            "attention_long_term_research_completed_total"
        ],
        "internal_improvement_completed_total": last[
            "attention_internal_improvement_completed_total"
        ],
        "housekeeping_completed_total": last[
            "attention_housekeeping_completed_total"
        ],
        "queue_depth_trajectory": _trajectory(result, "queue_depth"),
        "queued_task_age_mean_trajectory": _trajectory(
            result,
            "queued_task_age_mean_tick",
        ),
        "value_weighted_completed_total_trajectory": _trajectory(
            result,
            "attention_value_weighted_completed_total",
        ),
        "attention_capture_pressure_max_final": last["attention_capture_pressure_max_tick"],
        "attention_capture_pressure_mean_over_ticks": _mean_metric(
            result,
            "attention_capture_pressure_max_tick",
        ),
        "attention_capture_pressure_peak": max(
            float(row["attention_capture_pressure_max_tick"])
            for row in result.metrics
        ),
        "attention_capture_pressure_max_trajectory": _trajectory(
            result,
            "attention_capture_pressure_max_tick",
        ),
        "queue_depth_step_deltas": _trajectory_step_deltas(result, "queue_depth"),
        "queued_task_age_mean_step_deltas": _trajectory_step_deltas(
            result,
            "queued_task_age_mean_tick",
        ),
        "value_weighted_completed_total_step_deltas": _trajectory_step_deltas(
            result,
            "attention_value_weighted_completed_total",
        ),
        "attention_capture_pressure_max_step_deltas": _trajectory_step_deltas(
            result,
            "attention_capture_pressure_max_tick",
        ),
        "near_term_external_completed_total_trajectory": _trajectory(
            result,
            "attention_near_term_external_completed_total",
        ),
        "long_term_research_completed_total_trajectory": _trajectory(
            result,
            "attention_long_term_research_completed_total",
        ),
        "internal_improvement_completed_total_trajectory": _trajectory(
            result,
            "attention_internal_improvement_completed_total",
        ),
        "housekeeping_completed_total_trajectory": _trajectory(
            result,
            "attention_housekeeping_completed_total",
        ),
        **{
            f"{class_name}_capture_pressure_trajectory": _trajectory(
                result,
                f"attention_{class_name}_capture_pressure_tick",
            )
            for class_name in ATTENTION_CLASSES
        },
    }


def _mean_metric(result: SimulationResult, field: str) -> float:
    return round(
        sum(float(row[field]) for row in result.metrics) / len(result.metrics),
        6,
    )


def _trajectory(result: SimulationResult, field: str) -> str:
    return "|".join(str(row[field]) for row in result.metrics)


def _trajectory_step_deltas(result: SimulationResult, field: str) -> str:
    values = [float(row[field]) for row in result.metrics]
    deltas = (
        _format_number(values[index] - values[index - 1])
        for index in range(1, len(values))
    )
    return "|".join(deltas)


def _format_number(value: float) -> str:
    rounded = round(value, 6)
    if rounded.is_integer():
        return str(int(rounded))
    return str(rounded)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(COMPARISON_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def _policy_aggregates(rows: list[dict[str, Any]]) -> dict[str, PolicyAggregate]:
    return {
        policy: PolicyAggregate(
            policy=policy,
            seeds=len(policy_rows),
            value_weighted_completed_mean=_mean(policy_rows, "value_weighted_completed_total"),
            tasks_completed_mean=_mean(policy_rows, "tasks_completed_total"),
            queue_depth_mean=_mean(policy_rows, "queue_depth"),
            queued_task_age_mean_final_mean=_mean(policy_rows, "queued_task_age_mean_final"),
            queued_task_age_mean_over_ticks_mean=_mean(policy_rows, "queued_task_age_mean_over_ticks"),
            queued_task_age_max_peak_mean=_mean(policy_rows, "queued_task_age_max_peak"),
            near_term_external_completed_mean=_mean(policy_rows, "near_term_external_completed_total"),
            long_term_research_completed_mean=_mean(policy_rows, "long_term_research_completed_total"),
            internal_improvement_completed_mean=_mean(policy_rows, "internal_improvement_completed_total"),
            housekeeping_completed_mean=_mean(policy_rows, "housekeeping_completed_total"),
            queue_depth_final_trajectory_mean=_mean_trajectory_final(
                policy_rows,
                "queue_depth_trajectory",
            ),
            queued_task_age_mean_trajectory_final_mean=_mean_trajectory_final(
                policy_rows,
                "queued_task_age_mean_trajectory",
            ),
            value_weighted_trajectory_final_mean=_mean_trajectory_final(
                policy_rows,
                "value_weighted_completed_total_trajectory",
            ),
            attention_capture_pressure_max_final_mean=_mean(
                policy_rows,
                "attention_capture_pressure_max_final",
            ),
            attention_capture_pressure_mean_over_ticks_mean=_mean(
                policy_rows,
                "attention_capture_pressure_mean_over_ticks",
            ),
            attention_capture_pressure_peak_mean=_mean(
                policy_rows,
                "attention_capture_pressure_peak",
            ),
            queue_depth_step_delta_mean=_mean_step_delta(
                policy_rows,
                "queue_depth_step_deltas",
            ),
            queue_depth_step_delta_min=_min_step_delta(
                policy_rows,
                "queue_depth_step_deltas",
            ),
            queue_depth_step_delta_max=_max_step_delta(
                policy_rows,
                "queue_depth_step_deltas",
            ),
            queued_task_age_mean_step_delta_mean=_mean_step_delta(
                policy_rows,
                "queued_task_age_mean_step_deltas",
            ),
            queued_task_age_mean_step_delta_min=_min_step_delta(
                policy_rows,
                "queued_task_age_mean_step_deltas",
            ),
            queued_task_age_mean_step_delta_max=_max_step_delta(
                policy_rows,
                "queued_task_age_mean_step_deltas",
            ),
            value_weighted_step_delta_mean=_mean_step_delta(
                policy_rows,
                "value_weighted_completed_total_step_deltas",
            ),
            value_weighted_step_delta_min=_min_step_delta(
                policy_rows,
                "value_weighted_completed_total_step_deltas",
            ),
            value_weighted_step_delta_max=_max_step_delta(
                policy_rows,
                "value_weighted_completed_total_step_deltas",
            ),
            attention_capture_pressure_max_step_delta_mean=_mean_step_delta(
                policy_rows,
                "attention_capture_pressure_max_step_deltas",
            ),
            attention_capture_pressure_max_step_delta_min=_min_step_delta(
                policy_rows,
                "attention_capture_pressure_max_step_deltas",
            ),
            attention_capture_pressure_max_step_delta_max=_max_step_delta(
                policy_rows,
                "attention_capture_pressure_max_step_deltas",
            ),
        )
        for policy in tuple(dict.fromkeys(row["policy"] for row in rows))
        for policy_rows in ([row for row in rows if row["policy"] == policy],)
    }


def _mean(rows: list[dict[str, Any]], field: str) -> float:
    return round(sum(float(row[field]) for row in rows) / len(rows), 6)


def _mean_trajectory_final(rows: list[dict[str, Any]], field: str) -> float:
    return round(
        sum(float(str(row[field]).split("|")[-1]) for row in rows) / len(rows),
        6,
    )


def _step_delta_values(rows: list[dict[str, Any]], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        values.extend(float(value) for value in str(row[field]).split("|") if value)
    return values


def _mean_step_delta(rows: list[dict[str, Any]], field: str) -> float:
    values = _step_delta_values(rows, field)
    return round(sum(values) / len(values), 6)


def _min_step_delta(rows: list[dict[str, Any]], field: str) -> float:
    return round(min(_step_delta_values(rows, field)), 6)


def _max_step_delta(rows: list[dict[str, Any]], field: str) -> float:
    return round(max(_step_delta_values(rows, field)), 6)


def _comparison_summary(
    *,
    baseline_config: Path,
    variant_config: Path,
    internal_improvement_config: Path | None,
    seeds: tuple[int, ...],
    aggregates: dict[str, PolicyAggregate],
    rows: list[dict[str, Any]],
) -> str:
    baseline = aggregates["baseline"]
    lines = [
        "# A2 attention policy comparison",
        "",
        f"- baseline config: {baseline_config}",
        f"- research-heavy config: {variant_config}",
        *(
            [f"- internal-improvement config: {internal_improvement_config}"]
            if internal_improvement_config is not None
            else []
        ),
        f"- seeds: {', '.join(str(seed) for seed in seeds)}",
        f"- per-seed rows: {sum(aggregate.seeds for aggregate in aggregates.values())}",
        "",
        "## Policy means",
        "",
        *[
            line
            for policy in aggregates
            for line in _aggregate_lines(aggregates[policy])
        ],
        "",
        "## Phase-space regimes",
        "",
        *[
            line
            for policy in aggregates
            for line in _phase_space_regime_lines(aggregates[policy])
        ],
        "",
        "## Phase-space regime counts",
        "",
        *[
            line
            for policy in aggregates
            for line in _phase_space_regime_count_lines(
                policy,
                [row for row in rows if row["policy"] == policy],
            )
        ],
        "",
        "## Phase-space regime distribution deltas vs baseline",
        "",
        *[
            line
            for policy in aggregates
            if policy != "baseline"
            for line in _phase_space_regime_distribution_delta_lines(
                policy,
                [row for row in rows if row["policy"] == policy],
                [row for row in rows if row["policy"] == "baseline"],
            )
        ],
        "",
        "## Policy deltas vs baseline",
        "",
        *[
            line
            for policy, aggregate in aggregates.items()
            if policy != "baseline"
            for line in _delta_lines(aggregate, baseline)
        ],
        "",
    ]
    return "\n".join(lines)


def _phase_space_regime_lines(aggregate: PolicyAggregate) -> list[str]:
    queue_label, queue_sign = _axis_label(
        aggregate.queue_depth_step_delta_mean,
        positive="queue_growth",
        negative="queue_relief",
        zero="queue_flat",
    )
    age_label, age_sign = _axis_label(
        aggregate.queued_task_age_mean_step_delta_mean,
        positive="stale_age_rising",
        negative="stale_age_falling",
        zero="stale_age_flat",
    )
    value_label, value_sign = _axis_label(
        aggregate.value_weighted_step_delta_mean,
        positive="value_throughput_rising",
        negative="value_throughput_falling",
        zero="value_throughput_flat",
    )
    return [
        f"- {aggregate.policy}: label={queue_label}+{age_label}+{value_label}, "
        f"queue_depth_step_delta_sign={queue_sign}, "
        f"queued_age_step_delta_sign={age_sign}, "
        f"value_throughput_step_delta_sign={value_sign}",
    ]


def _phase_space_regime_count_lines(
    policy: str,
    rows: list[dict[str, Any]],
) -> list[str]:
    counts, total_steps = _phase_space_regime_counts(rows)

    if total_steps == 0:
        return [f"- {policy}: total_steps=0"]

    return [
        f"- {policy}: total_steps={total_steps}, "
        f"regime_counts={_format_regime_counts(counts)}, "
        f"regime_rates={_format_regime_rates(counts, total_steps)}",
    ]


def _phase_space_regime_counts(
    rows: list[dict[str, Any]],
) -> tuple[Counter[str], int]:
    counts: Counter[str] = Counter()
    total_steps = 0
    for row in rows:
        run_labels = _run_phase_space_regime_labels(row)
        counts.update(run_labels)
        total_steps += len(run_labels)
    return counts, total_steps


def _phase_space_regime_distribution_delta_lines(
    policy: str,
    rows: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]],
) -> list[str]:
    counts, total_steps = _phase_space_regime_counts(rows)
    baseline_counts, baseline_total_steps = _phase_space_regime_counts(baseline_rows)
    if total_steps == 0 or baseline_total_steps == 0:
        return [f"- {policy}: total_steps={total_steps}, baseline_total_steps={baseline_total_steps}"]

    labels = sorted(set(counts) | set(baseline_counts))
    return [
        f"- {policy}: total_steps={total_steps}, baseline_total_steps={baseline_total_steps}, "
        f"regime_rate_deltas={_format_regime_rate_deltas(counts, total_steps, baseline_counts, baseline_total_steps, labels)}, "
        f"regime_count_deltas={_format_regime_count_deltas(counts, baseline_counts, labels)}",
    ]


def _run_phase_space_regime_labels(row: dict[str, Any]) -> list[str]:
    queue_deltas = _parse_delta_series(row["queue_depth_step_deltas"])
    age_deltas = _parse_delta_series(row["queued_task_age_mean_step_deltas"])
    value_deltas = _parse_delta_series(row["value_weighted_completed_total_step_deltas"])
    if not (len(queue_deltas) == len(age_deltas) == len(value_deltas)):
        raise ValueError("Phase-space delta trajectories must have matching lengths.")
    return [
        _phase_space_regime_label(queue_delta, age_delta, value_delta)
        for queue_delta, age_delta, value_delta in zip(
            queue_deltas,
            age_deltas,
            value_deltas,
        )
    ]


def _parse_delta_series(value: Any) -> list[float]:
    return [float(item) for item in str(value).split("|") if item]


def _phase_space_regime_label(
    queue_delta: float,
    age_delta: float,
    value_delta: float,
) -> str:
    queue_label, _ = _axis_label(
        queue_delta,
        positive="queue_growth",
        negative="queue_relief",
        zero="queue_flat",
    )
    age_label, _ = _axis_label(
        age_delta,
        positive="stale_age_rising",
        negative="stale_age_falling",
        zero="stale_age_flat",
    )
    value_label, _ = _axis_label(
        value_delta,
        positive="value_throughput_rising",
        negative="value_throughput_falling",
        zero="value_throughput_flat",
    )
    return f"{queue_label}+{age_label}+{value_label}"


def _format_regime_counts(counts: Counter[str]) -> str:
    return "|".join(
        f"{label}:{counts[label]}"
        for label in sorted(counts)
    )


def _format_regime_rates(counts: Counter[str], total_steps: int) -> str:
    return "|".join(
        f"{label}:{round(counts[label] / total_steps, 6)}"
        for label in sorted(counts)
    )


def _format_regime_rate_deltas(
    counts: Counter[str],
    total_steps: int,
    baseline_counts: Counter[str],
    baseline_total_steps: int,
    labels: list[str],
) -> str:
    return "|".join(
        (
            f"{label}:"
            f"{round((counts[label] / total_steps) - (baseline_counts[label] / baseline_total_steps), 6)}"
        )
        for label in labels
    )


def _format_regime_count_deltas(
    counts: Counter[str],
    baseline_counts: Counter[str],
    labels: list[str],
) -> str:
    return "|".join(
        f"{label}:{counts[label] - baseline_counts[label]}"
        for label in labels
    )


def _axis_label(
    value: float,
    *,
    positive: str,
    negative: str,
    zero: str,
) -> tuple[str, str]:
    if value > 0:
        return positive, "positive"
    if value < 0:
        return negative, "negative"
    return zero, "zero"


def _aggregate_lines(aggregate: PolicyAggregate) -> list[str]:
    return [
        f"- {aggregate.policy}: seeds={aggregate.seeds}, "
        f"value_weighted_completed_mean={aggregate.value_weighted_completed_mean}, "
        f"tasks_completed_mean={aggregate.tasks_completed_mean}, "
        f"queue_depth_mean={aggregate.queue_depth_mean}, "
        f"queued_task_age_mean_final_mean={aggregate.queued_task_age_mean_final_mean}, "
        f"queued_task_age_mean_over_ticks_mean={aggregate.queued_task_age_mean_over_ticks_mean}, "
        f"queued_task_age_max_peak_mean={aggregate.queued_task_age_max_peak_mean}, "
        f"near_term_external_completed_mean={aggregate.near_term_external_completed_mean}, "
        f"long_term_research_completed_mean={aggregate.long_term_research_completed_mean}, "
        f"internal_improvement_completed_mean={aggregate.internal_improvement_completed_mean}, "
        f"housekeeping_completed_mean={aggregate.housekeeping_completed_mean}, "
        f"trajectory_final_queue_depth_mean={aggregate.queue_depth_final_trajectory_mean}, "
        f"trajectory_final_queued_task_age_mean={aggregate.queued_task_age_mean_trajectory_final_mean}, "
        f"trajectory_final_value_weighted_completed_mean={aggregate.value_weighted_trajectory_final_mean}, "
        f"capture_pressure_max_final_mean={aggregate.attention_capture_pressure_max_final_mean}, "
        f"capture_pressure_mean_over_ticks_mean={aggregate.attention_capture_pressure_mean_over_ticks_mean}, "
        f"capture_pressure_peak_mean={aggregate.attention_capture_pressure_peak_mean}, "
        f"queue_depth_step_delta_mean={aggregate.queue_depth_step_delta_mean}, "
        f"queue_depth_step_delta_min={aggregate.queue_depth_step_delta_min}, "
        f"queue_depth_step_delta_max={aggregate.queue_depth_step_delta_max}, "
        f"queued_task_age_mean_step_delta_mean={aggregate.queued_task_age_mean_step_delta_mean}, "
        f"queued_task_age_mean_step_delta_min={aggregate.queued_task_age_mean_step_delta_min}, "
        f"queued_task_age_mean_step_delta_max={aggregate.queued_task_age_mean_step_delta_max}, "
        f"value_weighted_step_delta_mean={aggregate.value_weighted_step_delta_mean}, "
        f"value_weighted_step_delta_min={aggregate.value_weighted_step_delta_min}, "
        f"value_weighted_step_delta_max={aggregate.value_weighted_step_delta_max}, "
        f"capture_pressure_max_step_delta_mean={aggregate.attention_capture_pressure_max_step_delta_mean}, "
        f"capture_pressure_max_step_delta_min={aggregate.attention_capture_pressure_max_step_delta_min}, "
        f"capture_pressure_max_step_delta_max={aggregate.attention_capture_pressure_max_step_delta_max}",
    ]


def _delta_lines(variant: PolicyAggregate, baseline: PolicyAggregate) -> list[str]:
    return [
        f"- {variant.policy} value-weighted completed work mean: {_delta(variant.value_weighted_completed_mean, baseline.value_weighted_completed_mean)}",
        f"- {variant.policy} tasks completed mean: {_delta(variant.tasks_completed_mean, baseline.tasks_completed_mean)}",
        f"- {variant.policy} final queue depth mean: {_delta(variant.queue_depth_mean, baseline.queue_depth_mean)}",
        f"- {variant.policy} final queued task mean age: {_delta(variant.queued_task_age_mean_final_mean, baseline.queued_task_age_mean_final_mean)}",
        f"- {variant.policy} mean queued task mean age: {_delta(variant.queued_task_age_mean_over_ticks_mean, baseline.queued_task_age_mean_over_ticks_mean)}",
        f"- {variant.policy} peak queued task max age mean: {_delta(variant.queued_task_age_max_peak_mean, baseline.queued_task_age_max_peak_mean)}",
        f"- {variant.policy} near-term external completions mean: {_delta(variant.near_term_external_completed_mean, baseline.near_term_external_completed_mean)}",
        f"- {variant.policy} long-term research completions mean: {_delta(variant.long_term_research_completed_mean, baseline.long_term_research_completed_mean)}",
        f"- {variant.policy} internal-improvement completions mean: {_delta(variant.internal_improvement_completed_mean, baseline.internal_improvement_completed_mean)}",
        f"- {variant.policy} housekeeping completions mean: {_delta(variant.housekeeping_completed_mean, baseline.housekeeping_completed_mean)}",
        f"- {variant.policy} queue-depth step delta mean: {_delta(variant.queue_depth_step_delta_mean, baseline.queue_depth_step_delta_mean)}",
        f"- {variant.policy} queued-age step delta mean: {_delta(variant.queued_task_age_mean_step_delta_mean, baseline.queued_task_age_mean_step_delta_mean)}",
        f"- {variant.policy} value-throughput step delta mean: {_delta(variant.value_weighted_step_delta_mean, baseline.value_weighted_step_delta_mean)}",
        f"- {variant.policy} final capture pressure mean: {_delta(variant.attention_capture_pressure_max_final_mean, baseline.attention_capture_pressure_max_final_mean)}",
        f"- {variant.policy} mean capture pressure: {_delta(variant.attention_capture_pressure_mean_over_ticks_mean, baseline.attention_capture_pressure_mean_over_ticks_mean)}",
        f"- {variant.policy} peak capture pressure mean: {_delta(variant.attention_capture_pressure_peak_mean, baseline.attention_capture_pressure_peak_mean)}",
        f"- {variant.policy} capture-pressure step delta mean: {_delta(variant.attention_capture_pressure_max_step_delta_mean, baseline.attention_capture_pressure_max_step_delta_mean)}",
    ]


def _delta(variant_value: float, baseline_value: float) -> float:
    return round(variant_value - baseline_value, 6)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare deterministic A2 attention-policy fixtures.")
    parser.add_argument("--baseline-config", default=str(DEFAULT_BASELINE_CONFIG))
    parser.add_argument("--variant-config", default=str(DEFAULT_VARIANT_CONFIG))
    parser.add_argument(
        "--internal-improvement-config",
        default=str(DEFAULT_INTERNAL_IMPROVEMENT_CONFIG),
        help="Optional third policy config; pass an empty string to skip it.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_SEEDS),
        help="Deterministic seed set to run for each policy.",
    )
    parser.add_argument("--out", required=True, help="Output directory for comparison artifacts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_comparison(
            baseline_config=args.baseline_config,
            variant_config=args.variant_config,
            internal_improvement_config=args.internal_improvement_config or None,
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
