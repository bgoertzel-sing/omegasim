"""Read A6 logistic-appraisal artifacts and emit gate-control outputs."""

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
    "final_latent_focus_mean",
    "final_latent_fatigue_mean",
    "final_latent_prediction_error_abs_mean",
    "final_artifact_novelty",
    "final_artifact_coherence",
    "final_artifact_actionability",
    "final_artifact_provenance_debt",
    "final_artifact_risk",
    "final_artifact_contradiction",
    "final_artifact_readiness",
    "final_artifact_implementation_maturity",
    "final_artifact_communication_maturity",
    "final_artifact_utility",
    "handoff_attempts_total",
    "handoff_successes_total",
    "handoff_failures_total",
    "prediction_budget_spent_total",
    "tasks_created_total",
    "tasks_completed_total",
    "tasks_worked_total",
    "messages_sent_total",
    "completion_fraction",
    "queue_depth",
    "queue_delta_tick",
    "queued_task_age_mean_final",
    "action_opportunity_total",
    "idle_total",
    "message_total",
    "create_task_total",
    "work_task_total",
    "synthesize_total",
    "review_total",
    "formalize_total",
    "maintain_total",
    "predict_total",
    "communicate_total",
    "pause_total",
)
A6_CONTROL_DELTA_FIELDS = (
    "contrast",
    "seed",
    "control_condition",
    "paired",
    "missing_required_fields",
    *(
        f"{field}_delta"
        for field in A6_ANALYSIS_ENDPOINT_FIELDS
        if field not in {"condition", "seed"}
    ),
)
_OUTPUT_NAMES = (
    "a6_logistic_appraisal_endpoints.csv",
    "a6_logistic_appraisal_manifest.csv",
    "a6_logistic_appraisal_control_deltas.csv",
    "summary.md",
)
_A6_CONTROL_PAIRS = (
    ("logistic_vs_linear", "linear"),
    ("logistic_vs_phase_shuffled", "phase_shuffled"),
    ("logistic_vs_threshold_shuffled", "threshold_shuffled"),
)
_A6_REQUIRED_CONTROL_FIELDS = (
    "tick",
    "queue_depth",
    "queue_delta_tick",
    "tasks_created_total",
    "tasks_completed_total",
    "tasks_worked_tick",
    "messages_sent_tick",
    "a6_prediction_budget_spent_tick",
    "a6_latent_activation_mean_tick",
    "a6_latent_focus_mean_tick",
    "a6_latent_fatigue_mean_tick",
    "a6_latent_prediction_error_mean_tick",
    "a6_artifact_readiness_tick",
    "a6_handoff_attempts_tick",
    "a6_handoff_successes_tick",
    "a6_handoff_failures_tick",
)
_A6_ACTIONS = (
    "idle",
    "message",
    "create_task",
    "work_task",
    "synthesize",
    "review",
    "formalize",
    "maintain",
    "predict",
    "communicate",
    "pause",
)


def run_a6_logistic_appraisal_analysis(
    compare_dir: str | Path = DEFAULT_A6_COMPARE_DIR,
    out_dir: str | Path = DEFAULT_A6_ANALYSIS_OUT_DIR,
) -> dict[str, Any]:
    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs, missing_required_fields = _read_a6_runs(compare_path)
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    control_delta_rows = _control_delta_rows(runs, missing_required_fields)
    manifest_rows = [
        {
            "control_level": control_level,
            "compare_dir": str(compare_path),
            "condition_count": len(conditions),
            "seed_count": len(seeds),
            "status": _control_level_status(control_level, control_delta_rows, missing_required_fields),
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
    _write_csv(
        output_path / "a6_logistic_appraisal_control_deltas.csv",
        control_delta_rows,
        A6_CONTROL_DELTA_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(compare_path, runs, manifest_rows, control_delta_rows, missing_required_fields)
    )
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "condition_count": len(conditions),
        "seed_count": len(seeds),
        "run_count": len(runs),
        "control_delta_count": len(control_delta_rows),
        "missing_required_fields": sorted(missing_required_fields),
    }


def _read_a6_runs(compare_path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    if not compare_path.exists():
        raise FileNotFoundError(f"A6 comparison/artifact directory does not exist: {compare_path}")
    run_dirs = sorted(path for path in compare_path.iterdir() if path.is_dir())
    if not run_dirs:
        raise ValueError(f"A6 comparison/artifact directory contains no run subdirectories: {compare_path}")

    rows = []
    missing_required_fields: set[str] = set()
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
        missing_required_fields.update(
            field for field in _A6_REQUIRED_CONTROL_FIELDS if field not in metrics[0]
        )
        seed = int((yaml.safe_load(manifest_path.read_text()) or {}).get("seed", -1))
        last = metrics[-1]
        rows.append(
            {
                "condition": condition,
                "seed": seed,
                "tick_count": len(metrics),
                "final_latent_activation_mean": _number(last, "a6_latent_activation_mean_tick"),
                "final_latent_focus_mean": _number(last, "a6_latent_focus_mean_tick"),
                "final_latent_fatigue_mean": _number(last, "a6_latent_fatigue_mean_tick"),
                "final_latent_prediction_error_abs_mean": abs(
                    _number(last, "a6_latent_prediction_error_mean_tick")
                ),
                "final_artifact_novelty": _number(last, "a6_artifact_novelty_tick"),
                "final_artifact_coherence": _number(last, "a6_artifact_coherence_tick"),
                "final_artifact_actionability": _number(last, "a6_artifact_actionability_tick"),
                "final_artifact_provenance_debt": _number(
                    last, "a6_artifact_provenance_debt_tick"
                ),
                "final_artifact_risk": _number(last, "a6_artifact_risk_tick"),
                "final_artifact_contradiction": _number(last, "a6_artifact_contradiction_tick"),
                "final_artifact_readiness": _number(last, "a6_artifact_readiness_tick"),
                "final_artifact_implementation_maturity": _number(
                    last, "a6_artifact_implementation_maturity_tick"
                ),
                "final_artifact_communication_maturity": _number(
                    last, "a6_artifact_communication_maturity_tick"
                ),
                "final_artifact_utility": _artifact_utility(last),
                "handoff_attempts_total": sum(
                    _number(row, "a6_handoff_attempts_tick") for row in metrics
                ),
                "handoff_successes_total": sum(
                    _number(row, "a6_handoff_successes_tick") for row in metrics
                ),
                "handoff_failures_total": sum(
                    _number(row, "a6_handoff_failures_tick") for row in metrics
                ),
                "prediction_budget_spent_total": sum(
                    _number(row, "a6_prediction_budget_spent_tick") for row in metrics
                ),
                "tasks_created_total": _number(last, "tasks_created_total"),
                "tasks_completed_total": _number(last, "tasks_completed_total"),
                "tasks_worked_total": sum(_number(row, "tasks_worked_tick") for row in metrics),
                "messages_sent_total": sum(_number(row, "messages_sent_tick") for row in metrics),
                "completion_fraction": _safe_ratio(
                    _number(last, "tasks_completed_total"),
                    _number(last, "tasks_created_total"),
                ),
                "queue_depth": _number(last, "queue_depth"),
                "queue_delta_tick": _number(last, "queue_delta_tick"),
                "queued_task_age_mean_final": _number(last, "queued_task_age_mean_tick"),
                "action_opportunity_total": _action_opportunity_total(metrics),
                **{
                    f"{action}_total": _action_total(metrics, action)
                    for action in _A6_ACTIONS
                },
            }
        )
    if not rows:
        raise ValueError(f"No A6 logistic_appraisal run artifacts found in {compare_path}")
    return rows, missing_required_fields


def _control_delta_rows(
    runs: list[dict[str, Any]],
    missing_required_fields: set[str],
) -> list[dict[str, Any]]:
    by_condition_seed = {
        (str(row["condition"]), int(row["seed"])): row
        for row in runs
    }
    seeds = sorted({int(row["seed"]) for row in runs})
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        logistic = by_condition_seed.get(("logistic", seed))
        for contrast, control_condition in _A6_CONTROL_PAIRS:
            control = by_condition_seed.get((control_condition, seed))
            row: dict[str, Any] = {
                "contrast": contrast,
                "seed": seed,
                "control_condition": control_condition,
                "paired": str(logistic is not None and control is not None).lower(),
                "missing_required_fields": "|".join(sorted(missing_required_fields)),
            }
            for field in A6_ANALYSIS_ENDPOINT_FIELDS:
                if field in {"condition", "seed"}:
                    continue
                row[f"{field}_delta"] = (
                    round(float(logistic[field]) - float(control[field]), 6)
                    if logistic is not None and control is not None
                    else ""
                )
            rows.append(row)
    return rows


def _control_level_status(
    control_level: str,
    control_delta_rows: list[dict[str, Any]],
    missing_required_fields: set[str],
) -> str:
    complete_pairs = [row for row in control_delta_rows if row["paired"] == "true"]
    if missing_required_fields:
        return "control_delta_preflight_missing_fields"
    if not complete_pairs:
        return "control_delta_preflight_incomplete_pairs"
    if control_level in {
        "load_service_action_opportunity",
        "amplitude_matched_linear",
        "phase_shuffled",
        "threshold_shuffled",
        "paired_seed_uncertainty",
    }:
        return "paired_delta_preflight_complete"
    if control_level == "clock_queue_residualized":
        return "residualization_not_yet_computed"
    return "promotion_not_evaluated"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows(rows)


def _number(row: dict[str, str], field: str) -> float:
    value = row.get(field, "")
    return float(value) if value not in {"", None} else 0.0


def _safe_ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _artifact_utility(row: dict[str, str]) -> float:
    positive = (
        _number(row, "a6_artifact_readiness_tick")
        + _number(row, "a6_artifact_coherence_tick")
        + _number(row, "a6_artifact_actionability_tick")
        + _number(row, "a6_artifact_implementation_maturity_tick")
        + _number(row, "a6_artifact_communication_maturity_tick")
    )
    negative = (
        _number(row, "a6_artifact_provenance_debt_tick")
        + _number(row, "a6_artifact_risk_tick")
        + _number(row, "a6_artifact_contradiction_tick")
    )
    return round((positive - negative) / 5.0, 6)


def _action_opportunity_total(metrics: list[dict[str, str]]) -> float:
    return sum(
        _number(row, field)
        for row in metrics
        for field in row
        if field.startswith("role_") and field.endswith("_tick")
    )


def _action_total(metrics: list[dict[str, str]], action: str) -> float:
    suffix = f"_{action}_tick"
    return sum(
        _number(row, field)
        for row in metrics
        for field in row
        if field.startswith("role_") and field.endswith(suffix)
    )


def _summary(
    compare_path: Path,
    runs: list[dict[str, Any]],
    manifest_rows: list[dict[str, Any]],
    control_delta_rows: list[dict[str, Any]],
    missing_required_fields: set[str],
) -> str:
    conditions = sorted({str(row["condition"]) for row in runs})
    seeds = sorted({int(row["seed"]) for row in runs})
    lines = [
        "# A6 Logistic-Appraisal Analysis Gate",
        "",
        f"- compare dir: {compare_path}",
        f"- run artifacts read: {len(runs)}",
        f"- conditions observed: {', '.join(conditions)}",
        f"- seeds observed: {', '.join(str(seed) for seed in seeds)}",
        "- reran simulations: no",
        f"- paired control delta rows: {len(control_delta_rows)}",
        "- status: read-only control-delta preflight; not promotion evidence",
        "- missing required fields: "
        + ("none" if not missing_required_fields else ", ".join(sorted(missing_required_fields))),
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
            "- Paired deltas are logistic minus the named control within the same seed.",
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
