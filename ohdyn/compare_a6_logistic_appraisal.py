"""Run a bounded A6 logistic-appraisal smoke comparison."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_attention import _format_number
from ohdyn.config import LOGISTIC_APPRAISAL_CONDITIONS, load_config
from ohdyn.run import run_experiment
from ohdyn.sim import SimulationResult


DEFAULT_A6_SEEDS = (1, 2)
DEFAULT_A6_COMPARE_DIR = Path("runs/a6_logistic_appraisal_compare")
A6_SMOKE_CONFIGS = (
    ("logistic", Path("configs/a6_logistic_appraisal_smoke.yaml")),
    ("linear", Path("configs/a6_linear_appraisal_smoke.yaml")),
    ("threshold_shuffled", Path("configs/a6_threshold_shuffled_smoke.yaml")),
    ("phase_shuffled", Path("configs/a6_phase_shuffled_smoke.yaml")),
)

A6_COMPARISON_FIELDS = (
    "condition",
    "config",
    "seed_count",
    "run_count",
    "tick_count",
    "appraisal_gain",
    "sigmoid_slope",
    "prediction_budget",
    "final_latent_activation_mean",
    "final_latent_focus_mean",
    "final_latent_fatigue_mean",
    "final_latent_prediction_error_abs_mean",
    "final_artifact_readiness_mean",
    "final_artifact_utility_mean",
    "handoff_attempts_total_mean",
    "handoff_successes_total_mean",
    "handoff_failures_total_mean",
    "prediction_budget_spent_total_mean",
    "tasks_created_mean",
    "tasks_completed_mean",
    "completion_fraction_mean",
    "queue_depth_mean",
    "queued_task_age_mean_final_mean",
)

A6_EFFECT_FIELDS = (
    "effect_axis",
    "low_label",
    "high_label",
    "final_latent_activation_mean_delta",
    "final_latent_fatigue_mean_delta",
    "final_latent_prediction_error_abs_mean_delta",
    "final_artifact_readiness_mean_delta",
    "final_artifact_utility_mean_delta",
    "handoff_successes_total_mean_delta",
    "handoff_failures_total_mean_delta",
    "prediction_budget_spent_total_mean_delta",
    "completion_fraction_mean_delta",
    "queue_depth_mean_delta",
    "queued_task_age_mean_final_mean_delta",
    "interpretation",
)

_OUTPUT_NAMES = (
    "a6_logistic_appraisal_comparison_metrics.csv",
    "a6_logistic_appraisal_effects.csv",
    "summary.md",
)


def run_a6_logistic_appraisal_comparison(
    *,
    seeds: tuple[int, ...] = DEFAULT_A6_SEEDS,
    out_dir: str | Path = DEFAULT_A6_COMPARE_DIR,
) -> list[dict[str, Any]]:
    _validate_seeds(seeds)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    _validate_smoke_configs()
    output_path.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for condition, config_path in A6_SMOKE_CONFIGS:
        results: list[SimulationResult] = []
        for seed in seeds:
            run_dir = output_path / f"{condition}_seed{seed}"
            results.append(run_experiment(config_path, seed=seed, out_dir=run_dir))
        rows.append(_aggregate_row(condition, config_path, results))

    effect_rows = _effect_rows(rows)
    _write_csv(
        output_path / "a6_logistic_appraisal_comparison_metrics.csv",
        A6_COMPARISON_FIELDS,
        rows,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_effects.csv",
        A6_EFFECT_FIELDS,
        effect_rows,
    )
    (output_path / "summary.md").write_text(_summary(rows, effect_rows, seeds))
    return rows


def _validate_seeds(seeds: tuple[int, ...]) -> None:
    if not seeds:
        raise ValueError("At least one seed is required.")
    invalid = [
        seed
        for seed in seeds
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0
    ]
    if invalid:
        raise ValueError("Seeds must be non-negative integers.")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must not contain duplicates.")


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [name for name in _OUTPUT_NAMES if (output_path / name).exists()]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains A6 artifacts: {names}")


def _validate_smoke_configs() -> None:
    expected_conditions = set(LOGISTIC_APPRAISAL_CONDITIONS)
    observed_conditions = {condition for condition, _ in A6_SMOKE_CONFIGS}
    if observed_conditions != expected_conditions:
        raise ValueError("A6 smoke comparison must include exactly the preregistered conditions.")

    for condition, config_path in A6_SMOKE_CONFIGS:
        cfg = load_config(config_path)
        if cfg.logistic_appraisal is None:
            raise ValueError(f"{config_path} must enable logistic_appraisal.")
        if cfg.logistic_appraisal.condition != condition:
            raise ValueError(
                f"{config_path} condition {cfg.logistic_appraisal.condition!r} "
                f"does not match {condition!r}."
            )
        if cfg.hives:
            raise ValueError(f"{config_path} must remain single-hive for A6 smoke.")


def _aggregate_row(
    condition: str,
    config_path: Path,
    results: list[SimulationResult],
) -> dict[str, Any]:
    cfg = results[0].config
    assert cfg.logistic_appraisal is not None
    last_rows = [result.metrics[-1] for result in results]
    created_values = [float(row["tasks_created_total"]) for row in last_rows]
    completed_values = [float(row["tasks_completed_total"]) for row in last_rows]
    handoff_attempt_totals = [
        sum(float(row["a6_handoff_attempts_tick"]) for row in result.metrics)
        for result in results
    ]
    handoff_success_totals = [
        sum(float(row["a6_handoff_successes_tick"]) for row in result.metrics)
        for result in results
    ]
    handoff_failure_totals = [
        sum(float(row["a6_handoff_failures_tick"]) for row in result.metrics)
        for result in results
    ]
    prediction_spend_totals = [
        sum(float(row["a6_prediction_budget_spent_tick"]) for row in result.metrics)
        for result in results
    ]

    return {
        "condition": condition,
        "config": str(config_path),
        "seed_count": len(results),
        "run_count": len(results),
        "tick_count": cfg.run.ticks,
        "appraisal_gain": cfg.logistic_appraisal.appraisal_gain,
        "sigmoid_slope": cfg.logistic_appraisal.sigmoid_slope,
        "prediction_budget": cfg.logistic_appraisal.prediction_budget,
        "final_latent_activation_mean": _mean_metric(
            last_rows, "a6_latent_activation_mean_tick"
        ),
        "final_latent_focus_mean": _mean_metric(last_rows, "a6_latent_focus_mean_tick"),
        "final_latent_fatigue_mean": _mean_metric(last_rows, "a6_latent_fatigue_mean_tick"),
        "final_latent_prediction_error_abs_mean": _mean_values(
            [abs(float(row["a6_latent_prediction_error_mean_tick"])) for row in last_rows]
        ),
        "final_artifact_readiness_mean": _mean_metric(last_rows, "a6_artifact_readiness_tick"),
        "final_artifact_utility_mean": _mean_values(
            [_artifact_utility(row) for row in last_rows]
        ),
        "handoff_attempts_total_mean": _mean_values(handoff_attempt_totals),
        "handoff_successes_total_mean": _mean_values(handoff_success_totals),
        "handoff_failures_total_mean": _mean_values(handoff_failure_totals),
        "prediction_budget_spent_total_mean": _mean_values(prediction_spend_totals),
        "tasks_created_mean": _mean_values(created_values),
        "tasks_completed_mean": _mean_values(completed_values),
        "completion_fraction_mean": _mean_values(
            [
                _safe_ratio(completed, created)
                for created, completed in zip(created_values, completed_values, strict=True)
            ]
        ),
        "queue_depth_mean": _mean_metric(last_rows, "queue_depth"),
        "queued_task_age_mean_final_mean": _mean_metric(last_rows, "queued_task_age_mean_tick"),
    }


def _artifact_utility(row: dict[str, Any]) -> float:
    positive = (
        float(row["a6_artifact_readiness_tick"])
        + float(row["a6_artifact_coherence_tick"])
        + float(row["a6_artifact_actionability_tick"])
        + float(row["a6_artifact_implementation_maturity_tick"])
        + float(row["a6_artifact_communication_maturity_tick"])
    )
    negative = (
        float(row["a6_artifact_provenance_debt_tick"])
        + float(row["a6_artifact_risk_tick"])
        + float(row["a6_artifact_contradiction_tick"])
    )
    return round((positive - negative) / 5.0, 6)


def _effect_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_condition = {str(row["condition"]): row for row in rows}
    pairs = (
        ("logistic_vs_linear", "linear", "logistic"),
        ("logistic_vs_phase_shuffled", "phase_shuffled", "logistic"),
        ("logistic_vs_threshold_shuffled", "threshold_shuffled", "logistic"),
    )
    return [
        _effect_row(effect_axis, by_condition[low_label], by_condition[high_label])
        for effect_axis, low_label, high_label in pairs
    ]


def _effect_row(
    effect_axis: str,
    low: dict[str, Any],
    high: dict[str, Any],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "effect_axis": effect_axis,
        "low_label": low["condition"],
        "high_label": high["condition"],
    }
    for field in A6_EFFECT_FIELDS:
        if field.endswith("_delta"):
            base_field = field.removesuffix("_delta")
            row[field] = _as_float(high[base_field]) - _as_float(low[base_field])
    row["interpretation"] = _interpret_effect(row)
    return row


def _interpret_effect(row: dict[str, Any]) -> str:
    utility_delta = _as_float(row["final_artifact_utility_mean_delta"])
    queue_delta = _as_float(row["queue_depth_mean_delta"])
    failure_delta = _as_float(row["handoff_failures_total_mean_delta"])
    if utility_delta > 0.0 and queue_delta <= 0.0 and failure_delta <= 0.0:
        return "smoke guardrails improve, but residual recurrence remains unanalyzed"
    if utility_delta <= 0.0:
        return "artifact-utility guardrail does not improve in smoke comparison"
    if queue_delta > 0.0:
        return "artifact utility improves with higher queue load; treat as accounting risk"
    return "smoke comparison only; read-only residual analysis required before interpretation"


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    seeds: tuple[int, ...],
) -> str:
    lines = [
        "# A6 Logistic-Appraisal Smoke Comparison",
        "",
        f"- seeds: {', '.join(str(seed) for seed in seeds)}",
        f"- run count: {sum(int(row['run_count']) for row in rows)}",
        "- scope: four checked-in single-hive smoke fixtures only; no broad sweep",
        "- scientific status: smoke artifact comparison, not promotion evidence",
        "",
        "## Condition Means",
        "",
    ]
    for row in rows:
        lines.append(
            "- "
            f"{row['condition']}: "
            f"readiness={_format_number(row['final_artifact_readiness_mean'])}, "
            f"artifact_utility={_format_number(row['final_artifact_utility_mean'])}, "
            f"handoff_successes={_format_number(row['handoff_successes_total_mean'])}, "
            f"handoff_failures={_format_number(row['handoff_failures_total_mean'])}, "
            f"prediction_spent={_format_number(row['prediction_budget_spent_total_mean'])}, "
            f"completion_fraction={_format_number(row['completion_fraction_mean'])}, "
            f"queue_depth={_format_number(row['queue_depth_mean'])}"
        )
    lines.extend(["", "## Effects", ""])
    for row in effect_rows:
        lines.append(
            "- "
            f"{row['high_label']} minus {row['low_label']}: "
            f"artifact_utility_delta={_format_number(row['final_artifact_utility_mean_delta'])}, "
            f"handoff_success_delta={_format_number(row['handoff_successes_total_mean_delta'])}, "
            f"queue_depth_delta={_format_number(row['queue_depth_mean_delta'])}; "
            f"{row['interpretation']}"
        )
    lines.extend(
        [
            "",
            "## Conservative Use",
            "",
            (
                "This helper is limited to the preregistered A6 smoke fixtures. "
                "Use these artifacts to exercise schemas and the read-only analyzer; "
                "do not treat them as evidence for residual latent-state attractors."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _mean_metric(rows: list[dict[str, Any]], field: str) -> float:
    return _mean_values([float(row[field]) for row in rows])


def _mean_values(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def _safe_ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _as_float(value: Any) -> float:
    return float(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the bounded A6 logistic-appraisal smoke comparison."
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_A6_SEEDS),
        help="Deterministic paired smoke seeds.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A6_COMPARE_DIR),
        help="Output directory for A6 smoke comparison artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a6_logistic_appraisal_comparison(
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
