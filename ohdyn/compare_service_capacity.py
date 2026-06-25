"""Compare demand pressure against deterministic work service capacity."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_attention import DEFAULT_SEEDS, _format_number, _format_regime_counts
from ohdyn.config import load_config
from ohdyn.run import run_experiment
from ohdyn.sim import SimulationResult


DEFAULT_NORMAL_LOW_SERVICE_CONFIG = Path("configs/a2_attention_low_service_capacity.yaml")
DEFAULT_NORMAL_BASELINE_SERVICE_CONFIG = Path("configs/a2_attention_smoke.yaml")
DEFAULT_NORMAL_HIGH_SERVICE_CONFIG = Path("configs/a2_attention_high_service_capacity.yaml")
DEFAULT_HIGH_PRESSURE_LOW_SERVICE_CONFIG = Path(
    "configs/a2_attention_low_service_capacity_high_pressure.yaml"
)
DEFAULT_HIGH_PRESSURE_BASELINE_SERVICE_CONFIG = Path("configs/a2_attention_high_pressure.yaml")
DEFAULT_HIGH_PRESSURE_HIGH_SERVICE_CONFIG = Path(
    "configs/a2_attention_high_service_capacity_high_pressure.yaml"
)
DEFAULT_EXTREME_PRESSURE_LOW_SERVICE_CONFIG = Path(
    "configs/a2_attention_low_service_capacity_extreme_pressure.yaml"
)
DEFAULT_EXTREME_PRESSURE_BASELINE_SERVICE_CONFIG = Path(
    "configs/a2_attention_extreme_pressure.yaml"
)
DEFAULT_EXTREME_PRESSURE_HIGH_SERVICE_CONFIG = Path(
    "configs/a2_attention_high_service_capacity_extreme_pressure.yaml"
)
BASELINE_ATTENTION_SHARES = {
    "near_term_external": 0.45,
    "long_term_research": 0.25,
    "internal_improvement": 0.2,
    "housekeeping": 0.1,
}

SERVICE_CAPACITY_COMPARISON_FIELDS = (
    "pressure_label",
    "service_capacity_label",
    "task_creation_pressure",
    "work_service_capacity",
    "config",
    "seed_count",
    "run_count",
    "tasks_created_mean",
    "tasks_completed_mean",
    "created_completed_balance_mean",
    "completion_fraction_mean",
    "queue_depth_mean",
    "queue_depth_per_created_task_mean",
    "queue_depth_per_created_completed_balance_mean",
    "queued_task_age_mean_final_mean",
    "queued_task_age_mean_over_ticks_mean",
    "queued_task_age_max_peak_mean",
    "value_per_work_event_mean",
    "attention_capture_pressure_max_final_mean",
    "attention_capture_pressure_mean_over_ticks_mean",
    "attention_capture_pressure_peak_mean",
    "baseline_lobe_transition_count_mean",
    "baseline_lobe_longest_dwell_ticks_mean",
    "baseline_lobe_longest_dwell_label_counts",
)


def run_service_capacity_comparison(
    *,
    normal_low_service_config: str | Path = DEFAULT_NORMAL_LOW_SERVICE_CONFIG,
    normal_baseline_service_config: str | Path = DEFAULT_NORMAL_BASELINE_SERVICE_CONFIG,
    normal_high_service_config: str | Path = DEFAULT_NORMAL_HIGH_SERVICE_CONFIG,
    high_pressure_low_service_config: str | Path = DEFAULT_HIGH_PRESSURE_LOW_SERVICE_CONFIG,
    high_pressure_baseline_service_config: str | Path = (
        DEFAULT_HIGH_PRESSURE_BASELINE_SERVICE_CONFIG
    ),
    high_pressure_high_service_config: str | Path = DEFAULT_HIGH_PRESSURE_HIGH_SERVICE_CONFIG,
    extreme_pressure_low_service_config: str | Path = DEFAULT_EXTREME_PRESSURE_LOW_SERVICE_CONFIG,
    extreme_pressure_baseline_service_config: str | Path = (
        DEFAULT_EXTREME_PRESSURE_BASELINE_SERVICE_CONFIG
    ),
    extreme_pressure_high_service_config: str | Path = DEFAULT_EXTREME_PRESSURE_HIGH_SERVICE_CONFIG,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    out_dir: str | Path,
) -> list[dict[str, Any]]:
    _validate_seeds(seeds)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    grid = (
        (
            "normal_pressure",
            (
                ("low_service", Path(normal_low_service_config)),
                ("baseline_service", Path(normal_baseline_service_config)),
                ("high_service", Path(normal_high_service_config)),
            ),
        ),
        (
            "high_pressure",
            (
                ("low_service", Path(high_pressure_low_service_config)),
                ("baseline_service", Path(high_pressure_baseline_service_config)),
                ("high_service", Path(high_pressure_high_service_config)),
            ),
        ),
        (
            "extreme_pressure",
            (
                ("low_service", Path(extreme_pressure_low_service_config)),
                ("baseline_service", Path(extreme_pressure_baseline_service_config)),
                ("high_service", Path(extreme_pressure_high_service_config)),
            ),
        ),
    )
    _validate_grid(grid)

    rows: list[dict[str, Any]] = []
    for pressure_label, service_configs in grid:
        for service_label, config_path in service_configs:
            results: list[SimulationResult] = []
            for seed in seeds:
                run_dir = output_path / f"{pressure_label}_{service_label}_seed{seed}"
                results.append(run_experiment(config_path, seed=seed, out_dir=run_dir))
            rows.append(_aggregate_row(pressure_label, service_label, config_path, results))

    _write_csv(output_path / "service_capacity_comparison_metrics.csv", rows)
    (output_path / "summary.md").write_text(_summary(rows, seeds))
    return rows


def _validate_seeds(seeds: tuple[int, ...]) -> None:
    if not seeds:
        raise ValueError("At least one seed is required.")
    invalid = [seed for seed in seeds if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0]
    if invalid:
        raise ValueError("Seeds must be non-negative integers.")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must not contain duplicates.")


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        artifact_name
        for artifact_name in ("service_capacity_comparison_metrics.csv", "summary.md")
        if (output_path / artifact_name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(
            f"Output path {output_path} already contains service-capacity artifacts: {names}"
        )


def _validate_grid(
    grid: tuple[tuple[str, tuple[tuple[str, Path], ...]], ...],
) -> None:
    pressure_values: list[float] = []
    expected_service_values: tuple[float, ...] | None = None
    for pressure_label, service_configs in grid:
        configs = [(service_label, config_path, load_config(config_path)) for service_label, config_path in service_configs]
        row_pressure_values = [cfg.model.task_creation_pressure for _, _, cfg in configs]
        first_pressure = row_pressure_values[0]
        if any(value != first_pressure for value in row_pressure_values[1:]):
            joined = ", ".join(
                f"{path}={cfg.model.task_creation_pressure}"
                for _, path, cfg in configs
            )
            raise ValueError(
                f"{pressure_label} configs must share task_creation_pressure: {joined}"
            )
        pressure_values.append(first_pressure)

        service_values = tuple(cfg.model.work_service_capacity for _, _, cfg in configs)
        if not service_values[0] < service_values[1] < service_values[2]:
            joined = ", ".join(
                f"{path}={cfg.model.work_service_capacity}"
                for _, path, cfg in configs
            )
            raise ValueError(
                f"{pressure_label} configs must have increasing work_service_capacity: {joined}"
            )
        if expected_service_values is None:
            expected_service_values = service_values
        elif service_values != expected_service_values:
            joined = ", ".join(
                f"{path}={cfg.model.work_service_capacity}"
                for _, path, cfg in configs
            )
            raise ValueError(
                "Service-capacity rows must use the same capacity axis across pressure "
                f"conditions: {joined}"
            )
        for _, path, cfg in configs:
            if cfg.attention_policy is None:
                raise ValueError(f"{path} must enable attention_policy.")
            if cfg.attention_policy.shares() != BASELINE_ATTENTION_SHARES:
                raise ValueError(f"{path} must use baseline attention shares.")
            if cfg.attention_policy.selection_strategy != "quota_balance":
                raise ValueError(f"{path} must use quota_balance selection_strategy.")

    if not pressure_values[0] < pressure_values[1] < pressure_values[2]:
        raise ValueError(
            "Service-capacity comparison configs must have strictly increasing "
            "task_creation_pressure values across pressure conditions."
        )


def _aggregate_row(
    pressure_label: str,
    service_label: str,
    config_path: Path,
    results: list[SimulationResult],
) -> dict[str, Any]:
    last_rows = [result.metrics[-1] for result in results]
    lobe_summaries = [_lobe_summary(result) for result in results]
    created_values = [float(row["tasks_created_total"]) for row in last_rows]
    completed_values = [float(row["tasks_completed_total"]) for row in last_rows]
    queue_values = [float(row["queue_depth"]) for row in last_rows]
    balance_values = [
        created - completed
        for created, completed in zip(created_values, completed_values, strict=True)
    ]
    cfg = results[0].config
    return {
        "pressure_label": pressure_label,
        "service_capacity_label": service_label,
        "task_creation_pressure": cfg.model.task_creation_pressure,
        "work_service_capacity": cfg.model.work_service_capacity,
        "config": str(config_path),
        "seed_count": len(results),
        "run_count": len(results),
        "tasks_created_mean": _mean_values(created_values),
        "tasks_completed_mean": _mean_values(completed_values),
        "created_completed_balance_mean": _mean_values(balance_values),
        "completion_fraction_mean": _mean_values(
            [
                _safe_ratio(completed, created)
                for created, completed in zip(created_values, completed_values, strict=True)
            ]
        ),
        "queue_depth_mean": _mean_values(queue_values),
        "queue_depth_per_created_task_mean": _mean_values(
            [
                _safe_ratio(queue, created)
                for queue, created in zip(queue_values, created_values, strict=True)
            ]
        ),
        "queue_depth_per_created_completed_balance_mean": _mean_values(
            [
                _safe_ratio(queue, balance)
                for queue, balance in zip(queue_values, balance_values, strict=True)
            ]
        ),
        "queued_task_age_mean_final_mean": _mean(last_rows, "queued_task_age_mean_tick"),
        "queued_task_age_mean_over_ticks_mean": _mean_values(
            [_mean(result.metrics, "queued_task_age_mean_tick") for result in results]
        ),
        "queued_task_age_max_peak_mean": _mean_values(
            [
                max(float(row["queued_task_age_max_tick"]) for row in result.metrics)
                for result in results
            ]
        ),
        "value_per_work_event_mean": _mean(
            last_rows,
            "attention_value_per_work_event_total",
        ),
        "attention_capture_pressure_max_final_mean": _mean(
            last_rows,
            "attention_capture_pressure_max_tick",
        ),
        "attention_capture_pressure_mean_over_ticks_mean": _mean_values(
            [_mean(result.metrics, "attention_capture_pressure_max_tick") for result in results]
        ),
        "attention_capture_pressure_peak_mean": _mean_values(
            [
                max(float(row["attention_capture_pressure_max_tick"]) for row in result.metrics)
                for result in results
            ]
        ),
        "baseline_lobe_transition_count_mean": _mean_values(
            [summary["transition_count"] for summary in lobe_summaries]
        ),
        "baseline_lobe_longest_dwell_ticks_mean": _mean_values(
            [summary["longest_dwell_ticks"] for summary in lobe_summaries]
        ),
        "baseline_lobe_longest_dwell_label_counts": _format_regime_counts(
            Counter(str(summary["longest_dwell_label"]) for summary in lobe_summaries)
        ),
    }


def _lobe_summary(result: SimulationResult) -> dict[str, Any]:
    labels = [str(row["baseline_lobe_label"]) for row in result.metrics]
    longest_label = ""
    longest_length = 0
    current_label = ""
    current_length = 0
    for label in labels:
        if label == current_label:
            current_length += 1
        else:
            current_label = label
            current_length = 1
        if current_length > longest_length:
            longest_label = current_label
            longest_length = current_length
    return {
        "transition_count": sum(int(row["baseline_lobe_transition_tick"]) for row in result.metrics),
        "longest_dwell_label": longest_label,
        "longest_dwell_ticks": longest_length,
    }


def _mean(rows: list[dict[str, Any]], field: str) -> float:
    return _mean_values([float(row[field]) for row in rows])


def _mean_values(values: list[float]) -> float:
    return round(sum(values) / len(values), 6)


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(SERVICE_CAPACITY_COMPARISON_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def _summary(rows: list[dict[str, Any]], seeds: tuple[int, ...]) -> str:
    lines = [
        "# A2 demand vs service-capacity comparison",
        "",
        f"- seeds: {', '.join(str(seed) for seed in seeds)}",
        f"- grid rows: {len(rows)}",
        "- scheduler: quota_balance",
        "- attention shares: baseline",
        "",
        "## Load-normalized backlog",
        "",
        *[
            f"- {row['pressure_label']} / {row['service_capacity_label']}: "
            f"pressure={row['task_creation_pressure']}, "
            f"service_capacity={row['work_service_capacity']}, "
            f"created_mean={row['tasks_created_mean']}, "
            f"completed_mean={row['tasks_completed_mean']}, "
            f"completion_fraction_mean={row['completion_fraction_mean']}, "
            f"queue_depth_mean={row['queue_depth_mean']}, "
            f"queue_per_created_mean={row['queue_depth_per_created_task_mean']}, "
            f"queue_per_balance_mean={row['queue_depth_per_created_completed_balance_mean']}"
            for row in rows
        ],
        "",
        "## Queue age, value, and capture pressure",
        "",
        *[
            f"- {row['pressure_label']} / {row['service_capacity_label']}: "
            f"queued_age_final_mean={row['queued_task_age_mean_final_mean']}, "
            f"queued_age_over_ticks_mean={row['queued_task_age_mean_over_ticks_mean']}, "
            f"queued_age_peak_mean={row['queued_task_age_max_peak_mean']}, "
            f"value_per_work_event_mean={row['value_per_work_event_mean']}, "
            f"capture_pressure_final_mean={row['attention_capture_pressure_max_final_mean']}, "
            f"capture_pressure_over_ticks_mean={row['attention_capture_pressure_mean_over_ticks_mean']}, "
            f"capture_pressure_peak_mean={row['attention_capture_pressure_peak_mean']}"
            for row in rows
        ],
        "",
        "## Baseline lobe transition and dwell",
        "",
        *[
            f"- {row['pressure_label']} / {row['service_capacity_label']}: "
            f"transition_count_mean={_format_number(float(row['baseline_lobe_transition_count_mean']))}, "
            f"longest_dwell_ticks_mean={_format_number(float(row['baseline_lobe_longest_dwell_ticks_mean']))}, "
            f"longest_dwell_labels={row['baseline_lobe_longest_dwell_label_counts']}"
            for row in rows
        ],
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare A2 task-creation pressure against work service capacity."
    )
    parser.add_argument("--normal-low-service-config", default=str(DEFAULT_NORMAL_LOW_SERVICE_CONFIG))
    parser.add_argument(
        "--normal-baseline-service-config",
        default=str(DEFAULT_NORMAL_BASELINE_SERVICE_CONFIG),
    )
    parser.add_argument("--normal-high-service-config", default=str(DEFAULT_NORMAL_HIGH_SERVICE_CONFIG))
    parser.add_argument(
        "--high-pressure-low-service-config",
        default=str(DEFAULT_HIGH_PRESSURE_LOW_SERVICE_CONFIG),
    )
    parser.add_argument(
        "--high-pressure-baseline-service-config",
        default=str(DEFAULT_HIGH_PRESSURE_BASELINE_SERVICE_CONFIG),
    )
    parser.add_argument(
        "--high-pressure-high-service-config",
        default=str(DEFAULT_HIGH_PRESSURE_HIGH_SERVICE_CONFIG),
    )
    parser.add_argument(
        "--extreme-pressure-low-service-config",
        default=str(DEFAULT_EXTREME_PRESSURE_LOW_SERVICE_CONFIG),
    )
    parser.add_argument(
        "--extreme-pressure-baseline-service-config",
        default=str(DEFAULT_EXTREME_PRESSURE_BASELINE_SERVICE_CONFIG),
    )
    parser.add_argument(
        "--extreme-pressure-high-service-config",
        default=str(DEFAULT_EXTREME_PRESSURE_HIGH_SERVICE_CONFIG),
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_SEEDS),
        help="Deterministic seed set to run for each pressure/service grid cell.",
    )
    parser.add_argument("--out", required=True, help="Output directory for comparison artifacts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_service_capacity_comparison(
            normal_low_service_config=args.normal_low_service_config,
            normal_baseline_service_config=args.normal_baseline_service_config,
            normal_high_service_config=args.normal_high_service_config,
            high_pressure_low_service_config=args.high_pressure_low_service_config,
            high_pressure_baseline_service_config=args.high_pressure_baseline_service_config,
            high_pressure_high_service_config=args.high_pressure_high_service_config,
            extreme_pressure_low_service_config=args.extreme_pressure_low_service_config,
            extreme_pressure_baseline_service_config=args.extreme_pressure_baseline_service_config,
            extreme_pressure_high_service_config=args.extreme_pressure_high_service_config,
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
