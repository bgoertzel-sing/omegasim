"""Read A6 logistic-appraisal artifacts and emit gate-control skeleton outputs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml


DEFAULT_A6_COMPARE_DIR = Path("runs/a6_logistic_appraisal_compare")
DEFAULT_A6_ANALYSIS_OUT_DIR = Path("runs/a6_logistic_appraisal_analysis")
A6_REQUIRED_CONDITIONS = (
    "logistic",
    "linear",
    "threshold_shuffled",
    "phase_shuffled",
)
A6_ANALYSIS_CONTROL_LEVELS = (
    "load_service_action_opportunity",
    "clock_queue_residualized",
    "amplitude_matched_linear",
    "phase_shuffled",
    "threshold_shuffled",
    "paired_seed_uncertainty",
    "promotion_closure_rules",
)
A6_ANALYSIS_MANIFEST_FIELDS = (
    "control_level",
    "compare_dir",
    "condition_count",
    "seed_count",
    "status",
)
A6_ANALYSIS_ENDPOINT_FIELDS = (
    "condition",
    "seed",
    "tick_count",
    "final_latent_activation_mean",
    "final_latent_fatigue_mean",
    "final_artifact_readiness",
    "handoff_attempts_total",
    "handoff_successes_total",
    "handoff_failures_total",
)
_OUTPUT_NAMES = (
    "a6_logistic_appraisal_endpoints.csv",
    "a6_logistic_appraisal_manifest.csv",
    "summary.md",
)


def run_a6_logistic_appraisal_analysis(
    compare_dir: str | Path = DEFAULT_A6_COMPARE_DIR,
    out_dir: str | Path = DEFAULT_A6_ANALYSIS_OUT_DIR,
) -> dict[str, Any]:
    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs = _read_a6_runs(compare_path)
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    manifest_rows = [
        {
            "control_level": control_level,
            "compare_dir": str(compare_path),
            "condition_count": len(conditions),
            "seed_count": len(seeds),
            "status": "skeleton_pending_confirmatory_comparison",
        }
        for control_level in A6_ANALYSIS_CONTROL_LEVELS
    ]

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "a6_logistic_appraisal_endpoints.csv",
        runs,
        A6_ANALYSIS_ENDPOINT_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_manifest.csv",
        manifest_rows,
        A6_ANALYSIS_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(_summary(compare_path, runs, manifest_rows))
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "condition_count": len(conditions),
        "seed_count": len(seeds),
        "run_count": len(runs),
    }


def _read_a6_runs(compare_path: Path) -> list[dict[str, Any]]:
    if not compare_path.exists():
        raise FileNotFoundError(f"A6 comparison/artifact directory does not exist: {compare_path}")
    run_dirs = sorted(path for path in compare_path.iterdir() if path.is_dir())
    if not run_dirs:
        raise ValueError(f"A6 comparison/artifact directory contains no run subdirectories: {compare_path}")

    rows = []
    for run_dir in run_dirs:
        config_path = run_dir / "config.yaml"
        metrics_path = run_dir / "metrics.csv"
        manifest_path = run_dir / "manifest.yaml"
        if not config_path.exists() or not metrics_path.exists() or not manifest_path.exists():
            continue
        config = yaml.safe_load(config_path.read_text()) or {}
        logistic_appraisal = config.get("logistic_appraisal")
        if not isinstance(logistic_appraisal, dict):
            continue
        condition = str(logistic_appraisal.get("condition", ""))
        metrics = _read_csv(metrics_path)
        if not metrics:
            continue
        seed = int((yaml.safe_load(manifest_path.read_text()) or {}).get("seed", -1))
        last = metrics[-1]
        rows.append(
            {
                "condition": condition,
                "seed": seed,
                "tick_count": len(metrics),
                "final_latent_activation_mean": last.get("a6_latent_activation_mean_tick", "0"),
                "final_latent_fatigue_mean": last.get("a6_latent_fatigue_mean_tick", "0"),
                "final_artifact_readiness": last.get("a6_artifact_readiness_tick", "0"),
                "handoff_attempts_total": sum(
                    int(row.get("a6_handoff_attempts_tick", 0)) for row in metrics
                ),
                "handoff_successes_total": sum(
                    int(row.get("a6_handoff_successes_tick", 0)) for row in metrics
                ),
                "handoff_failures_total": sum(
                    int(row.get("a6_handoff_failures_tick", 0)) for row in metrics
                ),
            }
        )
    if not rows:
        raise ValueError(f"No A6 logistic_appraisal run artifacts found in {compare_path}")
    return rows


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    compare_path: Path,
    runs: list[dict[str, Any]],
    manifest_rows: list[dict[str, Any]],
) -> str:
    conditions = sorted({str(row["condition"]) for row in runs})
    seeds = sorted({int(row["seed"]) for row in runs})
    lines = [
        "# A6 Logistic-Appraisal Analysis Skeleton",
        "",
        f"- compare dir: {compare_path}",
        f"- run artifacts read: {len(runs)}",
        f"- conditions observed: {', '.join(conditions)}",
        f"- seeds observed: {', '.join(str(seed) for seed in seeds)}",
        "- reran simulations: no",
        "- status: skeleton pending confirmatory comparison artifacts",
        "",
        "## Control Levels",
        "",
    ]
    for row in manifest_rows:
        lines.append(f"- {row['control_level']}: {row['status']}")
    lines.extend(
        [
            "",
            "## Gate Reminder",
            "",
            "- Do not promote A6 from smoke artifacts alone.",
            "- Residual latent/artifact recurrence must beat linear, phase-shuffled, and threshold-shuffled controls.",
            "- Load, service, action opportunity, work budget, clock trend, and queue variables remain accounting controls.",
            "",
        ]
    )
    return "\n".join(lines)


def _ensure_output_paths_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        output_name
        for output_name in _OUTPUT_NAMES
        if (output_path / output_name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains A6 analysis artifacts: {names}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze existing A6 logistic-appraisal artifacts without rerunning simulations."
    )
    parser.add_argument(
        "--compare-dir",
        default=str(DEFAULT_A6_COMPARE_DIR),
        help="Directory containing existing A6 run artifact subdirectories.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A6_ANALYSIS_OUT_DIR),
        help="Output directory for derived A6 analysis skeleton artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_a6_logistic_appraisal_analysis(args.compare_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
