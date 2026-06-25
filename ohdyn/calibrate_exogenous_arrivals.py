"""Calibrate opt-in exogenous arrival rates against coupled-pressure targets."""

from __future__ import annotations

import argparse
import csv
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_attention import DEFAULT_SEEDS, _format_number
from ohdyn.config import ExogenousArrivalsConfig, OmegaConfig, load_config
from ohdyn.run import run_experiment
from ohdyn.sim import SimulationResult


DEFAULT_CONTROL_CONFIG = Path("configs/a2_attention_smoke.yaml")
DEFAULT_HIGH_PRESSURE_TARGET_CONFIG = Path("configs/a2_attention_high_pressure.yaml")
DEFAULT_EXTREME_PRESSURE_TARGET_CONFIG = Path(
    "configs/a2_attention_extreme_pressure.yaml"
)
DEFAULT_CANDIDATE_RATES = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
BASELINE_ARRIVAL_SHARES = {
    "near_term_external": 0.45,
    "long_term_research": 0.25,
    "internal_improvement": 0.2,
    "housekeeping": 0.1,
}

EXOGENOUS_CALIBRATION_FIELDS = (
    "condition",
    "rate_per_tick",
    "target_label",
    "target_created_mean",
    "target_created_delta_from_control",
    "target_match_abs_error",
    "target_match_rank",
    "seed_count",
    "run_count",
    "agent_tasks_created_mean",
    "exogenous_tasks_created_mean",
    "tasks_created_mean",
    "tasks_completed_mean",
    "work_events_mean",
    "final_queue_mean",
    "queue_per_created_mean",
    "completion_fraction_mean",
    "create_task_actions_mean",
    "work_task_actions_mean",
    "message_actions_mean",
    "idle_actions_mean",
)


def run_exogenous_arrival_calibration(
    *,
    control_config: str | Path = DEFAULT_CONTROL_CONFIG,
    high_pressure_target_config: str | Path = DEFAULT_HIGH_PRESSURE_TARGET_CONFIG,
    extreme_pressure_target_config: str | Path = DEFAULT_EXTREME_PRESSURE_TARGET_CONFIG,
    candidate_rates: tuple[float, ...] = DEFAULT_CANDIDATE_RATES,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    out_dir: str | Path,
) -> list[dict[str, Any]]:
    _validate_seeds(seeds)
    _validate_candidate_rates(candidate_rates)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    control_path = Path(control_config)
    high_target_path = Path(high_pressure_target_config)
    extreme_target_path = Path(extreme_pressure_target_config)
    control_cfg = load_config(control_path)
    high_target_cfg = load_config(high_target_path)
    extreme_target_cfg = load_config(extreme_target_path)
    _validate_configs(
        control_path,
        control_cfg,
        high_target_path,
        high_target_cfg,
        extreme_target_path,
        extreme_target_cfg,
    )

    control_results = _run_config(control_path, seeds, output_path / "target_control")
    high_target_results = _run_config(
        high_target_path, seeds, output_path / "target_high_pressure"
    )
    extreme_target_results = _run_config(
        extreme_target_path,
        seeds,
        output_path / "target_extreme_pressure",
    )
    control_created_mean = _created_mean(control_results)
    targets = {
        "endogenous_control": control_created_mean,
        "low_exogenous_target": round(
            (control_created_mean + _created_mean(high_target_results)) / 2.0,
            6,
        ),
        "high_pressure_target": _created_mean(high_target_results),
        "extreme_pressure_target": _created_mean(extreme_target_results),
    }

    rows: list[dict[str, Any]] = []
    for rate in candidate_rates:
        condition = _condition_label(rate)
        candidate_config = _exogenous_config(control_cfg, rate)
        results = []
        for seed in seeds:
            run_dir = output_path / condition / f"seed{seed}"
            results.append(_run_config_object(candidate_config, seed, run_dir))
        rows.append(
            _aggregate_candidate_row(
                condition=condition,
                rate=rate,
                results=results,
                targets=targets,
                control_created_mean=control_created_mean,
            )
        )

    _rank_target_matches(rows)
    _write_csv(output_path / "exogenous_arrival_calibration.csv", rows)
    report = _summary(
        rows=rows,
        seeds=seeds,
        candidate_rates=candidate_rates,
        control_config=control_path,
        high_pressure_target_config=high_target_path,
        extreme_pressure_target_config=extreme_target_path,
        targets=targets,
    )
    (output_path / "summary.md").write_text(report)
    return rows


def _run_config(
    config_path: Path, seeds: tuple[int, ...], out_dir: Path
) -> list[SimulationResult]:
    return [
        run_experiment(config_path, seed=seed, out_dir=out_dir / f"seed{seed}")
        for seed in seeds
    ]


def _run_config_object(
    config: OmegaConfig, seed: int, out_dir: Path
) -> SimulationResult:
    from ohdyn.io import write_outputs
    from ohdyn.sim import simulate

    result = simulate(config, seed)
    write_outputs(result, out_dir)
    return result


def _exogenous_config(control_config: OmegaConfig, rate: float) -> OmegaConfig:
    return replace(
        control_config,
        run=replace(
            control_config.run,
            experiment_id=f"a2_exogenous_arrival_calibration_rate_{_rate_slug(rate)}",
        ),
        model=replace(control_config.model, task_creation_pressure=1.0),
        exogenous_arrivals=ExogenousArrivalsConfig(
            enabled=True,
            rate_per_tick=rate,
            **BASELINE_ARRIVAL_SHARES,
        ),
    )


def _aggregate_candidate_row(
    *,
    condition: str,
    rate: float,
    results: list[SimulationResult],
    targets: dict[str, float],
    control_created_mean: float,
) -> dict[str, Any]:
    last_rows = [result.metrics[-1] for result in results]
    total_created_mean = _mean_values(
        [float(row["tasks_created_total"]) for row in last_rows]
    )
    target_label, target_created_mean = _nearest_target(total_created_mean, targets)
    action_totals = [_action_totals(result) for result in results]
    return {
        "condition": condition,
        "rate_per_tick": rate,
        "target_label": target_label,
        "target_created_mean": target_created_mean,
        "target_created_delta_from_control": round(
            target_created_mean - control_created_mean, 6
        ),
        "target_match_abs_error": round(
            abs(total_created_mean - target_created_mean), 6
        ),
        "target_match_rank": 0,
        "seed_count": len(results),
        "run_count": len(results),
        "agent_tasks_created_mean": _mean(last_rows, "agent_tasks_created_total"),
        "exogenous_tasks_created_mean": _mean(
            last_rows, "exogenous_tasks_created_total"
        ),
        "tasks_created_mean": total_created_mean,
        "tasks_completed_mean": _mean(last_rows, "tasks_completed_total"),
        "work_events_mean": _mean_values(
            [float(totals["work_task"]) for totals in action_totals]
        ),
        "final_queue_mean": _mean(last_rows, "queue_depth"),
        "queue_per_created_mean": _mean_values(
            [
                _safe_ratio(
                    float(row["queue_depth"]), float(row["tasks_created_total"])
                )
                for row in last_rows
            ]
        ),
        "completion_fraction_mean": _mean_values(
            [
                _safe_ratio(
                    float(row["tasks_completed_total"]),
                    float(row["tasks_created_total"]),
                )
                for row in last_rows
            ]
        ),
        "create_task_actions_mean": _mean_values(
            [float(totals["create_task"]) for totals in action_totals]
        ),
        "work_task_actions_mean": _mean_values(
            [float(totals["work_task"]) for totals in action_totals]
        ),
        "message_actions_mean": _mean_values(
            [float(totals["message"]) for totals in action_totals]
        ),
        "idle_actions_mean": _mean_values(
            [float(totals["idle"]) for totals in action_totals]
        ),
    }


def _rank_target_matches(rows: list[dict[str, Any]]) -> None:
    for target_label in sorted({str(row["target_label"]) for row in rows}):
        matching = [row for row in rows if row["target_label"] == target_label]
        for rank, row in enumerate(
            sorted(
                matching,
                key=lambda item: (
                    float(item["target_match_abs_error"]),
                    float(item["rate_per_tick"]),
                ),
            ),
            start=1,
        ):
            row["target_match_rank"] = rank


def _action_totals(result: SimulationResult) -> dict[str, int]:
    totals = {"create_task": 0, "work_task": 0, "message": 0, "idle": 0}
    for row in result.metrics:
        totals["create_task"] += int(
            row.get("agent_tasks_created_tick", row["tasks_created_tick"])
        )
        totals["work_task"] += int(row["tasks_worked_tick"])
        totals["message"] += int(row["messages_sent_tick"])
        totals["idle"] += int(row["idle_tick"])
    return totals


def _created_mean(results: list[SimulationResult]) -> float:
    return _mean([result.metrics[-1] for result in results], "tasks_created_total")


def _nearest_target(
    total_created_mean: float, targets: dict[str, float]
) -> tuple[str, float]:
    label = min(
        targets,
        key=lambda key: (abs(total_created_mean - targets[key]), key),
    )
    return label, targets[label]


def _condition_label(rate: float) -> str:
    return (
        "endogenous_control_rate0"
        if rate == 0.0
        else f"exogenous_rate_{_rate_slug(rate)}"
    )


def _rate_slug(rate: float) -> str:
    return str(rate).replace(".", "p")


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


def _validate_candidate_rates(candidate_rates: tuple[float, ...]) -> None:
    if not candidate_rates:
        raise ValueError("At least one candidate rate is required.")
    if any(rate < 0.0 for rate in candidate_rates):
        raise ValueError("Candidate rates must be non-negative.")
    if len(set(candidate_rates)) != len(candidate_rates):
        raise ValueError("Candidate rates must not contain duplicates.")
    if tuple(sorted(candidate_rates)) != candidate_rates:
        raise ValueError("Candidate rates must be sorted in increasing order.")


def _validate_configs(
    control_path: Path,
    control_cfg: OmegaConfig,
    high_target_path: Path,
    high_target_cfg: OmegaConfig,
    extreme_target_path: Path,
    extreme_target_cfg: OmegaConfig,
) -> None:
    if control_cfg.attention_policy is None:
        raise ValueError(f"{control_path} must enable attention_policy.")
    if control_cfg.attention_policy.shares() != BASELINE_ARRIVAL_SHARES:
        raise ValueError(f"{control_path} must use baseline attention shares.")
    if control_cfg.attention_policy.selection_strategy != "quota_balance":
        raise ValueError(f"{control_path} must use quota_balance selection_strategy.")
    if control_cfg.model.task_creation_pressure != 1.0:
        raise ValueError(f"{control_path} must use task_creation_pressure 1.0.")
    if control_cfg.model.work_service_capacity != 1.0:
        raise ValueError(f"{control_path} must use work_service_capacity 1.0.")
    if not (
        control_cfg.model.task_creation_pressure
        < high_target_cfg.model.task_creation_pressure
        < extreme_target_cfg.model.task_creation_pressure
    ):
        raise ValueError(
            "Target configs must have increasing task_creation_pressure values."
        )
    for path, cfg in (
        (high_target_path, high_target_cfg),
        (extreme_target_path, extreme_target_cfg),
    ):
        if cfg.attention_policy is None:
            raise ValueError(f"{path} must enable attention_policy.")
        if cfg.attention_policy.shares() != BASELINE_ARRIVAL_SHARES:
            raise ValueError(f"{path} must use baseline attention shares.")
        if cfg.attention_policy.selection_strategy != "quota_balance":
            raise ValueError(f"{path} must use quota_balance selection_strategy.")
        if cfg.model.work_service_capacity != 1.0:
            raise ValueError(f"{path} must use work_service_capacity 1.0.")


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(
            f"Output path {output_path} exists and is not a directory."
        )
    collisions = [
        artifact_name
        for artifact_name in ("exogenous_arrival_calibration.csv", "summary.md")
        if (output_path / artifact_name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(
            f"Output path {output_path} already contains calibration artifacts: {names}"
        )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(EXOGENOUS_CALIBRATION_FIELDS),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    *,
    rows: list[dict[str, Any]],
    seeds: tuple[int, ...],
    candidate_rates: tuple[float, ...],
    control_config: Path,
    high_pressure_target_config: Path,
    extreme_pressure_target_config: Path,
    targets: dict[str, float],
) -> str:
    selected = [
        row
        for row in rows
        if row["target_label"] != "endogenous_control" and row["target_match_rank"] == 1
    ]
    lines = [
        "# A2 exogenous-arrival calibration",
        "",
        f"- seeds: {', '.join(str(seed) for seed in seeds)}",
        f"- candidate rates: {', '.join(_format_number(rate) for rate in candidate_rates)}",
        f"- control config: {control_config}",
        f"- high-pressure target config: {high_pressure_target_config}",
        f"- extreme-pressure target config: {extreme_pressure_target_config}",
        "- calibration criterion: total created-task mean only; no lobe, entropy, or value outcomes are used for rate selection",
        "",
        "## Coupled-pressure targets",
        "",
        *[
            f"- {label}: created_mean={_format_number(value)}"
            for label, value in targets.items()
        ],
        "",
        "## Candidate accounting",
        "",
        *[
            f"- {row['condition']}: rate={_format_number(float(row['rate_per_tick']))}, "
            f"target={row['target_label']}, "
            f"target_error={_format_number(float(row['target_match_abs_error']))}, "
            f"agent_created_mean={_format_number(float(row['agent_tasks_created_mean']))}, "
            f"exogenous_created_mean={_format_number(float(row['exogenous_tasks_created_mean']))}, "
            f"total_created_mean={_format_number(float(row['tasks_created_mean']))}, "
            f"completed_mean={_format_number(float(row['tasks_completed_mean']))}, "
            f"work_events_mean={_format_number(float(row['work_events_mean']))}, "
            f"final_queue_mean={_format_number(float(row['final_queue_mean']))}, "
            f"queue_per_created={_format_number(float(row['queue_per_created_mean']))}"
            for row in rows
        ],
        "",
        "## Provisional frozen rates",
        "",
        *[
            f"- {row['target_label']}: rate_per_tick={_format_number(float(row['rate_per_tick']))}, "
            f"created_mean={_format_number(float(row['tasks_created_mean']))}, "
            f"target_error={_format_number(float(row['target_match_abs_error']))}"
            for row in selected
        ],
        "",
        "## Interpretation",
        "",
        "- These rates are calibration fixtures for the next exogenous-arrival holdout; they do not by themselves test lobe dynamics.",
        "- Candidate selection used load/accounting targets only, following the preregistered decoupling plan.",
        "",
    ]
    return "\n".join(lines)


def _mean(rows: list[dict[str, Any]], field: str) -> float:
    return _mean_values([float(row[field]) for row in rows])


def _mean_values(values: list[float]) -> float:
    return round(sum(values) / len(values), 6)


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calibrate exogenous task-arrival rates against coupled-pressure targets."
    )
    parser.add_argument("--control-config", default=str(DEFAULT_CONTROL_CONFIG))
    parser.add_argument(
        "--high-pressure-target-config",
        default=str(DEFAULT_HIGH_PRESSURE_TARGET_CONFIG),
    )
    parser.add_argument(
        "--extreme-pressure-target-config",
        default=str(DEFAULT_EXTREME_PRESSURE_TARGET_CONFIG),
    )
    parser.add_argument(
        "--candidate-rates",
        nargs="+",
        type=float,
        default=list(DEFAULT_CANDIDATE_RATES),
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_SEEDS),
        help="Deterministic seed set to run for each target and candidate rate.",
    )
    parser.add_argument(
        "--out", required=True, help="Output directory for calibration artifacts."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_exogenous_arrival_calibration(
            control_config=args.control_config,
            high_pressure_target_config=args.high_pressure_target_config,
            extreme_pressure_target_config=args.extreme_pressure_target_config,
            candidate_rates=tuple(args.candidate_rates),
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
