"""Deterministic comparison runner for A2 attention-policy fixtures."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

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
    }


def _mean_metric(result: SimulationResult, field: str) -> float:
    return round(
        sum(float(row[field]) for row in result.metrics) / len(result.metrics),
        6,
    )


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
        )
        for policy in tuple(dict.fromkeys(row["policy"] for row in rows))
        for policy_rows in ([row for row in rows if row["policy"] == policy],)
    }


def _mean(rows: list[dict[str, Any]], field: str) -> float:
    return round(sum(float(row[field]) for row in rows) / len(rows), 6)


def _comparison_summary(
    *,
    baseline_config: Path,
    variant_config: Path,
    internal_improvement_config: Path | None,
    seeds: tuple[int, ...],
    aggregates: dict[str, PolicyAggregate],
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
        f"housekeeping_completed_mean={aggregate.housekeeping_completed_mean}",
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
