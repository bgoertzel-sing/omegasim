"""Compare normal-pressure and high-pressure A2 attention-policy sets."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

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
PRESSURE_COMPARISON_FIELDS = (
    "policy",
    "normal_total_steps",
    "high_pressure_total_steps",
    "regime_rate_deltas",
    "regime_count_deltas",
    "value_weighted_completed_mean_delta",
    "tasks_completed_mean_delta",
    "queue_depth_mean_delta",
    "queued_task_age_mean_final_delta",
    "queued_task_age_mean_over_ticks_delta",
    "queued_task_age_max_peak_delta",
)


def run_pressure_comparison(
    *,
    normal_baseline_config: str | Path = DEFAULT_BASELINE_CONFIG,
    normal_variant_config: str | Path = DEFAULT_VARIANT_CONFIG,
    normal_internal_improvement_config: str | Path | None = DEFAULT_INTERNAL_IMPROVEMENT_CONFIG,
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
    high_pressure_rows = run_comparison(
        baseline_config=high_pressure_baseline_config,
        variant_config=high_pressure_variant_config,
        internal_improvement_config=high_pressure_internal_improvement_config,
        seeds=seeds,
        out_dir=output_path / "high_pressure",
    )

    rows = _pressure_rows(normal_rows, high_pressure_rows)
    _write_csv(output_path / "pressure_comparison_metrics.csv", rows)
    (output_path / "summary.md").write_text(
        _pressure_summary(
            normal_baseline_config=Path(normal_baseline_config),
            normal_variant_config=Path(normal_variant_config),
            normal_internal_improvement_config=(
                Path(normal_internal_improvement_config)
                if normal_internal_improvement_config is not None
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
        )
    )
    return rows


def _ensure_pressure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        artifact_name
        for artifact_name in ("pressure_comparison_metrics.csv", "summary.md")
        if (output_path / artifact_name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains pressure comparison artifacts: {names}")


def _pressure_rows(
    normal_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    policies = tuple(dict.fromkeys(row["policy"] for row in normal_rows))
    high_pressure_policies = {row["policy"] for row in high_pressure_rows}
    missing = [policy for policy in policies if policy not in high_pressure_policies]
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"High-pressure comparison is missing policies: {names}")

    return [
        _pressure_row(
            policy,
            [row for row in normal_rows if row["policy"] == policy],
            [row for row in high_pressure_rows if row["policy"] == policy],
        )
        for policy in policies
    ]


def _pressure_row(
    policy: str,
    normal_rows: list[dict[str, Any]],
    high_pressure_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    normal_counts, normal_total_steps = _phase_space_regime_counts(normal_rows)
    high_counts, high_total_steps = _phase_space_regime_counts(high_pressure_rows)
    labels = sorted(set(normal_counts) | set(high_counts))
    return {
        "policy": policy,
        "normal_total_steps": normal_total_steps,
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
    }


def _metric_mean_delta(
    high_pressure_rows: list[dict[str, Any]],
    normal_rows: list[dict[str, Any]],
    field: str,
) -> float:
    return round(_mean(high_pressure_rows, field) - _mean(normal_rows, field), 6)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(PRESSURE_COMPARISON_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def _pressure_summary(
    *,
    normal_baseline_config: Path,
    normal_variant_config: Path,
    normal_internal_improvement_config: Path | None,
    high_pressure_baseline_config: Path,
    high_pressure_variant_config: Path,
    high_pressure_internal_improvement_config: Path | None,
    seeds: tuple[int, ...],
    rows: list[dict[str, Any]],
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
    ]
    return "\n".join(lines)


def _pressure_delta_lines(row: dict[str, Any]) -> list[str]:
    return [
        f"- {row['policy']}: normal_total_steps={row['normal_total_steps']}, "
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
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare normal-pressure and high-pressure A2 attention-policy fixtures."
    )
    parser.add_argument("--normal-baseline-config", default=str(DEFAULT_BASELINE_CONFIG))
    parser.add_argument("--normal-variant-config", default=str(DEFAULT_VARIANT_CONFIG))
    parser.add_argument(
        "--normal-internal-improvement-config",
        default=str(DEFAULT_INTERNAL_IMPROVEMENT_CONFIG),
        help="Optional normal-pressure third policy config; pass an empty string to skip it.",
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
