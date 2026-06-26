"""Compare A5 predictive-control conditions under matched demand streams."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_attention import DEFAULT_SEEDS, _format_number
from ohdyn.config import ATTENTION_CLASSES, load_config
from ohdyn.run import run_experiment
from ohdyn.sim import SimulationResult


DEFAULT_BASE_CONFIG = Path("configs/a5_predictive_linear_smoke.yaml")

A5_PREDICTIVE_CONDITIONS = (
    ("reactive", 0.0),
    ("linear", 0.35),
    ("nonlinear", 0.65),
    ("oracle", 1.0),
    ("shuffled", 0.35),
    ("nonlinear_shuffled", 0.65),
)

A5_PREDICTIVE_COMPARISON_FIELDS = (
    "condition",
    "config",
    "prediction_budget",
    "lead_ticks",
    "signal_period",
    "signal_amplitude",
    "seed_count",
    "run_count",
    "forecast_abs_error_final_mean",
    "forecast_skill_final_mean",
    "forecast_skill_per_budget_final_mean",
    "work_forecast_alignment_final_mean",
    "work_future_demand_alignment_final_mean",
    "allocation_future_residual_abs_final_mean",
    "tasks_created_mean",
    "tasks_completed_mean",
    "completion_fraction_mean",
    "queue_depth_mean",
    "queued_task_age_mean_final_mean",
    "attention_capture_pressure_max_final_mean",
)

A5_PREDICTIVE_EFFECT_FIELDS = (
    "effect_axis",
    "low_label",
    "high_label",
    "forecast_skill_final_mean_delta",
    "forecast_skill_per_budget_final_mean_delta",
    "work_future_demand_alignment_final_mean_delta",
    "allocation_future_residual_abs_final_mean_delta",
    "completion_fraction_mean_delta",
    "queue_depth_mean_delta",
    "queued_task_age_mean_final_mean_delta",
    "interpretation",
)


def run_predictive_control_comparison(
    *,
    base_config: str | Path = DEFAULT_BASE_CONFIG,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    out_dir: str | Path,
) -> list[dict[str, Any]]:
    _validate_seeds(seeds)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_configs = _write_condition_configs(Path(base_config), output_path / "configs")
    rows: list[dict[str, Any]] = []
    for condition, config_path in generated_configs:
        results: list[SimulationResult] = []
        for seed in seeds:
            run_dir = output_path / f"{condition}_seed{seed}"
            results.append(run_experiment(config_path, seed=seed, out_dir=run_dir))
        rows.append(_aggregate_row(condition, config_path, results))

    effect_rows = _effect_rows(rows)
    _write_csv(
        output_path / "predictive_control_comparison_metrics.csv",
        A5_PREDICTIVE_COMPARISON_FIELDS,
        rows,
    )
    _write_csv(
        output_path / "predictive_control_effects.csv",
        A5_PREDICTIVE_EFFECT_FIELDS,
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
    collisions = [
        name
        for name in (
            "predictive_control_comparison_metrics.csv",
            "predictive_control_effects.csv",
            "summary.md",
        )
        if (output_path / name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(
            f"Output path {output_path} already contains A5 predictive-control artifacts: {names}"
        )


def _write_condition_configs(
    base_config: Path,
    config_dir: Path,
) -> tuple[tuple[str, Path], ...]:
    cfg = load_config(base_config)
    if cfg.predictive_control is None:
        raise ValueError(f"{base_config} must enable predictive_control.")
    if cfg.attention_policy is None:
        raise ValueError(f"{base_config} must enable attention_policy.")
    if cfg.hives:
        raise ValueError(f"{base_config} must be a single-hive config.")

    raw = yaml.safe_load(base_config.read_text()) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{base_config} must contain a YAML mapping.")

    config_dir.mkdir(parents=True, exist_ok=True)
    generated = []
    for condition, budget in A5_PREDICTIVE_CONDITIONS:
        condition_raw = dict(raw)
        condition_raw["run"] = dict(raw["run"])
        condition_raw["run"]["experiment_id"] = f"a5_predictive_{condition}_comparison"
        condition_raw["predictive_control"] = dict(raw["predictive_control"])
        condition_raw["predictive_control"]["condition"] = condition
        condition_raw["predictive_control"]["prediction_budget"] = budget
        path = config_dir / f"a5_predictive_{condition}.yaml"
        path.write_text(yaml.safe_dump(condition_raw, sort_keys=False))
        generated.append((condition, path))
    return tuple(generated)


def _aggregate_row(
    condition: str,
    config_path: Path,
    results: list[SimulationResult],
) -> dict[str, Any]:
    last_rows = [result.metrics[-1] for result in results]
    cfg = results[0].config
    assert cfg.predictive_control is not None
    created_values = [float(row["tasks_created_total"]) for row in last_rows]
    completed_values = [float(row["tasks_completed_total"]) for row in last_rows]
    residual_abs_values = [
        sum(
            abs(float(row[f"a5_{class_name}_allocation_future_residual_tick"]))
            for class_name in ATTENTION_CLASSES
        )
        / len(ATTENTION_CLASSES)
        for row in last_rows
    ]
    return {
        "condition": condition,
        "config": str(Path("configs") / config_path.name),
        "prediction_budget": cfg.predictive_control.prediction_budget,
        "lead_ticks": cfg.predictive_control.lead_ticks,
        "signal_period": cfg.predictive_control.signal_period,
        "signal_amplitude": cfg.predictive_control.signal_amplitude,
        "seed_count": len(results),
        "run_count": len(results),
        "forecast_abs_error_final_mean": _mean_metric(last_rows, "a5_forecast_abs_error_tick"),
        "forecast_skill_final_mean": _mean_metric(last_rows, "a5_forecast_skill_tick"),
        "forecast_skill_per_budget_final_mean": _mean_metric(
            last_rows,
            "a5_forecast_skill_per_budget_tick",
        ),
        "work_forecast_alignment_final_mean": _mean_metric(
            last_rows,
            "a5_work_forecast_alignment_tick",
        ),
        "work_future_demand_alignment_final_mean": _mean_metric(
            last_rows,
            "a5_work_future_demand_alignment_tick",
        ),
        "allocation_future_residual_abs_final_mean": _mean_values(residual_abs_values),
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
        "attention_capture_pressure_max_final_mean": _mean_metric(
            last_rows,
            "attention_capture_pressure_max_tick",
        ),
    }


def _effect_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_condition = {str(row["condition"]): row for row in rows}
    pairs = (
        ("condition_vs_reactive", "reactive", "linear"),
        ("condition_vs_reactive", "reactive", "nonlinear"),
        ("condition_vs_reactive", "reactive", "oracle"),
        ("condition_vs_shuffled", "shuffled", "linear"),
        ("condition_vs_budget_matched_shuffled", "nonlinear_shuffled", "nonlinear"),
        ("oracle_vs_nonlinear", "nonlinear", "oracle"),
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
    for field in A5_PREDICTIVE_EFFECT_FIELDS:
        if field.endswith("_delta"):
            base_field = field.removesuffix("_delta")
            row[field] = _as_float(high[base_field]) - _as_float(low[base_field])
    row["interpretation"] = _interpret_effect(row)
    return row


def _interpret_effect(row: dict[str, Any]) -> str:
    skill_delta = _as_float(row["forecast_skill_final_mean_delta"])
    residual_delta = _as_float(row["allocation_future_residual_abs_final_mean_delta"])
    queue_delta = _as_float(row["queue_depth_mean_delta"])
    if skill_delta > 0.0 and residual_delta < 0.0:
        return "forecast skill improves with closer allocation to future demand"
    if skill_delta > 0.0 and queue_delta <= 0.0:
        return "forecast skill improves without higher final queue depth"
    if skill_delta <= 0.0:
        return "no forecast-skill improvement"
    return "forecast skill improves but allocation/load controls need follow-up"


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
        "# A5 Predictive-Control Comparison",
        "",
        f"- seeds: {', '.join(str(seed) for seed in seeds)}",
        f"- run count: {sum(int(row['run_count']) for row in rows)}",
        "- scope: single-hive matched-demand pilot; no multi-hive coupling or external services",
        "",
        "## Condition Means",
        "",
    ]
    for row in rows:
        lines.append(
            "- "
            f"{row['condition']}: budget={_format_number(row['prediction_budget'])}, "
            f"forecast_skill={_format_number(row['forecast_skill_final_mean'])}, "
            f"skill_per_budget={_format_number(row['forecast_skill_per_budget_final_mean'])}, "
            f"future_alignment={_format_number(row['work_future_demand_alignment_final_mean'])}, "
            f"residual_abs={_format_number(row['allocation_future_residual_abs_final_mean'])}, "
            f"completion_fraction={_format_number(row['completion_fraction_mean'])}, "
            f"queue_depth={_format_number(row['queue_depth_mean'])}"
        )
    lines.extend(["", "## Effects", ""])
    for row in effect_rows:
        lines.append(
            "- "
            f"{row['high_label']} minus {row['low_label']}: "
            f"forecast_skill_delta={_format_number(row['forecast_skill_final_mean_delta'])}, "
            f"residual_abs_delta={_format_number(row['allocation_future_residual_abs_final_mean_delta'])}, "
            f"queue_depth_delta={_format_number(row['queue_depth_mean_delta'])}; "
            f"{row['interpretation']}"
        )
    lines.extend(
        [
            "",
            "## Conservative Use",
            "",
            (
                "This pilot compares forecast modes under matched task-arrival, action, "
                "service, and deterministic demand-signal settings. Treat throughput and "
                "queue changes as guardrails, not as evidence for structured dynamics. "
                "`shuffled` is the linear-budget timing-broken null; "
                "`nonlinear_shuffled` is the nonlinear-budget timing-broken null."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


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
        description="Run a matched A5 predictive-control comparison."
    )
    parser.add_argument(
        "--base-config",
        default=str(DEFAULT_BASE_CONFIG),
        help="Base A5 predictive-control YAML config.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_SEEDS),
        help="Deterministic paired seeds.",
    )
    parser.add_argument("--out", required=True, help="Output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_predictive_control_comparison(
            base_config=args.base_config,
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
