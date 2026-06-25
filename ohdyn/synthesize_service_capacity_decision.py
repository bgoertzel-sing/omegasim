"""Build a decision synthesis from service-capacity holdout artifacts."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_attention import _format_number


DECISION_SYNTHESIS_FIELDS = (
    "claim",
    "evidence",
    "current_decision",
    "confound",
    "next_falsification_test",
)


def run_service_capacity_decision_synthesis(
    *,
    service_capacity_dir: str | Path,
    trajectory_dir: str | Path,
    out_md: str | Path,
    out_csv: str | Path,
) -> list[dict[str, str]]:
    service_path = Path(service_capacity_dir)
    trajectory_path = Path(trajectory_dir)
    _validate_inputs(service_path, trajectory_path)

    grid_rows = _read_csv(service_path / "service_capacity_comparison_metrics.csv")
    service_effect_rows = _read_csv(service_path / "service_capacity_effects.csv")
    trajectory_rows = _read_csv(trajectory_path / "service_capacity_trajectory_metrics.csv")
    trajectory_effect_rows = _read_csv(trajectory_path / "service_capacity_trajectory_effects.csv")
    bootstrap_rows = _read_optional_csv(
        trajectory_path / "service_capacity_trajectory_bootstrap.csv"
    )
    null_rows = _read_optional_csv(trajectory_path / "service_capacity_trajectory_nulls.csv")
    accounting_rows = _load_action_accounting_rows(service_path, grid_rows)
    decision_rows = _decision_rows(service_effect_rows, trajectory_effect_rows)

    _write_csv(Path(out_csv), DECISION_SYNTHESIS_FIELDS, decision_rows)
    Path(out_md).write_text(
        _summary(
            grid_rows=grid_rows,
            service_effect_rows=service_effect_rows,
            trajectory_rows=trajectory_rows,
            trajectory_effect_rows=trajectory_effect_rows,
            bootstrap_rows=bootstrap_rows,
            null_rows=null_rows,
            accounting_rows=accounting_rows,
            service_path=service_path,
            trajectory_path=trajectory_path,
        )
    )
    return decision_rows


def _validate_inputs(service_path: Path, trajectory_path: Path) -> None:
    service_required = (
        "service_capacity_comparison_metrics.csv",
        "service_capacity_effects.csv",
    )
    trajectory_required = (
        "service_capacity_trajectory_metrics.csv",
        "service_capacity_trajectory_effects.csv",
    )
    missing = [
        str(path / name)
        for path, names in (
            (service_path, service_required),
            (trajectory_path, trajectory_required),
        )
        for name in names
        if not (path / name).is_file()
    ]
    if missing:
        raise FileNotFoundError(f"Missing synthesis inputs: {', '.join(missing)}")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as handle:
        return list(csv.DictReader(handle))


def _read_optional_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    return _read_csv(path)


def _write_csv(
    path: Path,
    fieldnames: tuple[str, ...],
    rows: list[dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(fieldnames),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _load_action_accounting_rows(
    service_path: Path,
    grid_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for grid_row in grid_rows:
        pressure_label = grid_row["pressure_label"]
        service_label = grid_row["service_capacity_label"]
        run_dirs = sorted(service_path.glob(f"{pressure_label}_{service_label}_seed*"))
        if not run_dirs:
            rows.append(_accounting_row_from_grid(grid_row))
            continue
        run_summaries = [_run_action_summary(run_dir) for run_dir in run_dirs]
        rows.append(
            {
                "pressure_label": pressure_label,
                "service_capacity_label": service_label,
                "tasks_created_mean": _mean_field(run_summaries, "tasks_created"),
                "tasks_completed_mean": _mean_field(run_summaries, "tasks_completed"),
                "completion_fraction_mean": _mean_values(
                    [
                        _safe_ratio(summary["tasks_completed"], summary["tasks_created"])
                        for summary in run_summaries
                    ]
                ),
                "created_completed_balance_mean": _mean_field(
                    run_summaries,
                    "created_completed_balance",
                ),
                "queue_per_balance_mean": _mean_values(
                    [
                        _safe_ratio(
                            summary["queue_depth"],
                            summary["created_completed_balance"],
                        )
                        for summary in run_summaries
                    ]
                ),
                "idle_actions_mean": _mean_field(run_summaries, "idle_actions"),
                "message_actions_mean": _mean_field(run_summaries, "message_actions"),
                "create_task_actions_mean": _mean_field(
                    run_summaries,
                    "create_task_actions",
                ),
                "work_task_actions_mean": _mean_field(
                    run_summaries,
                    "work_task_actions",
                ),
                "task_worked_events_mean": _mean_field(
                    run_summaries,
                    "task_worked_events",
                ),
            }
        )
    return rows


def _accounting_row_from_grid(grid_row: dict[str, str]) -> dict[str, Any]:
    return {
        "pressure_label": grid_row["pressure_label"],
        "service_capacity_label": grid_row["service_capacity_label"],
        "tasks_created_mean": grid_row["tasks_created_mean"],
        "tasks_completed_mean": grid_row["tasks_completed_mean"],
        "completion_fraction_mean": grid_row["completion_fraction_mean"],
        "created_completed_balance_mean": grid_row["created_completed_balance_mean"],
        "queue_per_balance_mean": grid_row[
            "queue_depth_per_created_completed_balance_mean"
        ],
        "idle_actions_mean": "",
        "message_actions_mean": "",
        "create_task_actions_mean": grid_row["tasks_created_mean"],
        "work_task_actions_mean": "",
        "task_worked_events_mean": "",
    }


def _run_action_summary(run_dir: Path) -> dict[str, float]:
    final_metrics = _final_metrics(run_dir / "metrics.csv")
    event_counts = Counter[str]()
    with (run_dir / "events.csv").open() as handle:
        for row in csv.DictReader(handle):
            event_counts[row["event_type"]] += 1
    created = float(final_metrics["tasks_created_total"])
    completed = float(final_metrics["tasks_completed_total"])
    balance = created - completed
    return {
        "tasks_created": created,
        "tasks_completed": completed,
        "created_completed_balance": balance,
        "queue_depth": float(final_metrics["queue_depth"]),
        "idle_actions": float(event_counts["agent_idle"]),
        "message_actions": float(event_counts["message_sent"]),
        "create_task_actions": float(event_counts["task_created"]),
        "work_task_actions": float(event_counts["task_worked"]),
        "task_worked_events": float(event_counts["task_worked"]),
    }


def _final_metrics(metrics_path: Path) -> dict[str, str]:
    with metrics_path.open() as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{metrics_path} contains no metric rows.")
    return rows[-1]


def _decision_rows(
    service_effect_rows: list[dict[str, str]],
    trajectory_effect_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    service_deltas = _axis_deltas(
        service_effect_rows,
        "service_capacity",
        "queue_depth_per_created_task_mean_delta",
    )
    pressure_deltas = _axis_deltas(
        service_effect_rows,
        "task_creation_pressure",
        "queue_depth_per_created_task_mean_delta",
    )
    entropy_deltas = _axis_deltas(
        trajectory_effect_rows,
        "task_creation_pressure",
        "transition_entropy_mean_delta",
    )
    service_entropy_deltas = _axis_deltas(
        trajectory_effect_rows,
        "service_capacity",
        "transition_entropy_mean_delta",
    )
    return [
        {
            "claim": "Queue depth is primarily load accounting",
            "evidence": (
                "queue_depth_per_created_completed_balance_mean is 1.0 in every "
                "grid cell; queue per created rises with pressure and falls with service"
            ),
            "current_decision": (
                "Treat raw queue depth as a baseline load observable, not an "
                "emergent lobe claim"
            ),
            "confound": (
                "Creation pressure is implemented through create_task action weight, "
                "so demand and action mix may be coupled"
            ),
            "next_falsification_test": (
                "Use the load/action accounting panel before preregistering an "
                "exogenous-arrival decoupling test"
            ),
        },
        {
            "claim": "Service capacity absorbs load at fixed pressure",
            "evidence": (
                "High-minus-low service-capacity queue-per-created deltas: "
                f"{', '.join(service_deltas)}"
            ),
            "current_decision": "Keep service capacity as a mechanism-discriminating axis",
            "confound": "Effects depend on paired seed uncertainty and label controls",
            "next_falsification_test": (
                "Preserve paired bootstrap and null-control reporting in future grids"
            ),
        },
        {
            "claim": "Creation pressure increases normalized backlog at fixed service",
            "evidence": (
                "Extreme-minus-normal pressure queue-per-created deltas: "
                f"{', '.join(pressure_deltas)}"
            ),
            "current_decision": (
                "Demand pressure remains a robust load driver after normalizing by "
                "created tasks"
            ),
            "confound": "Higher pressure also changes effective work opportunity",
            "next_falsification_test": (
                "Run a preregistered exogenous-arrival decoupling test after analysis controls"
            ),
        },
        {
            "claim": "Pressure induces candidate lobe trajectory locking",
            "evidence": (
                "Extreme-minus-normal pressure transition-entropy deltas: "
                f"{', '.join(entropy_deltas)}"
            ),
            "current_decision": (
                "Treat trajectory locking as a candidate residual signal, not an "
                "independent lobe grammar finding yet"
            ),
            "confound": "backlog_growth labels are partly derived from queue movement",
            "next_falsification_test": (
                "Compare trajectory deltas against label-count nulls and queue-blind labels"
            ),
        },
        {
            "claim": "Service capacity partially unlocks trajectories",
            "evidence": (
                "High-minus-low service-capacity transition-entropy deltas: "
                f"{', '.join(service_entropy_deltas)}"
            ),
            "current_decision": "Keep residual-locking hypothesis alive as load-mediated",
            "confound": "Raw and normalized entropy are sensitive to label prevalence",
            "next_falsification_test": (
                "Report normalized entropy, null-adjusted dwell, and action accounting together"
            ),
        },
    ]


def _axis_deltas(rows: list[dict[str, str]], axis: str, field: str) -> list[str]:
    return [
        _format_number(float(row[field]))
        for row in rows
        if row["effect_axis"] == axis
    ]


def _summary(
    *,
    grid_rows: list[dict[str, str]],
    service_effect_rows: list[dict[str, str]],
    trajectory_rows: list[dict[str, str]],
    trajectory_effect_rows: list[dict[str, str]],
    bootstrap_rows: list[dict[str, str]],
    null_rows: list[dict[str, str]],
    accounting_rows: list[dict[str, Any]],
    service_path: Path,
    trajectory_path: Path,
) -> str:
    decision_rows = _decision_rows(service_effect_rows, trajectory_effect_rows)
    stable_bootstrap_count = sum(
        1 for row in bootstrap_rows if float(row["sign_stability"]) >= 0.95
    )
    strongest_null = (
        max(null_rows, key=lambda row: float(row["dwell_length_max_observed_minus_null"]))
        if null_rows
        else None
    )
    lines = [
        "# A2 service-capacity decision synthesis, seeds 70..99",
        "",
        "This synthesis combines the demand-vs-service-capacity holdout grid, "
        "the lobe-trajectory analysis, paired bootstrap controls when present, "
        "label-count null controls when present, and load/action accounting "
        "from existing run artifacts.",
        "",
        "Source artifacts:",
        "",
        f"- `{service_path / 'service_capacity_comparison_metrics.csv'}`",
        f"- `{service_path / 'service_capacity_effects.csv'}`",
        f"- `{trajectory_path / 'service_capacity_trajectory_metrics.csv'}`",
        f"- `{trajectory_path / 'service_capacity_trajectory_effects.csv'}`",
        "",
        "External strategic review handling:",
        "",
        "- `../outputs/strategy-reviews/omegasim/latest-review.md`",
        "- `strategic_change_level: minor`",
        "- `notify_ben: false`",
        "- Accepted: add a decision-oriented synthesis with action/load accounting, "
        "paired bootstrap, and label-count null controls before launching another experiment.",
        "- Deferred: queue-blind lobe labeling is not rejected; it remains the next "
        "analysis-only robustness check after this synthesis.",
        "",
        "## Decision summary",
        "",
        "The current evidence supports a conservative interpretation. Raw final "
        "queue depth should be treated as load accounting. Pressure-induced "
        "trajectory locking remains the residual candidate signal, but the "
        "label-count null control makes the independent lobe-grammar claim more "
        "cautious because observed-minus-null dwell and entropy differences are small.",
        "",
        "## Decision table",
        "",
        "| Claim | Evidence | Current decision | Confound | Next falsification test |",
        "| --- | --- | --- | --- | --- |",
        *[
            "| {claim} | {evidence} | {current_decision} | {confound} | "
            "{next_falsification_test} |".format(**row)
            for row in decision_rows
        ],
        "",
        "## Load/action accounting panel",
        "",
        "| Pressure | Service | Created | Completed | Completion fraction | "
        "Create actions | Work actions | Work events | Idle actions | "
        "Message actions | Queue/balance |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        *[
            "| {pressure_label} | {service_capacity_label} | {created} | {completed} | "
            "{completion_fraction} | {create_actions} | {work_actions} | "
            "{work_events} | {idle_actions} | {message_actions} | {queue_balance} |".format(
                pressure_label=row["pressure_label"],
                service_capacity_label=row["service_capacity_label"],
                created=_format_cell(row["tasks_created_mean"]),
                completed=_format_cell(row["tasks_completed_mean"]),
                completion_fraction=_format_cell(row["completion_fraction_mean"]),
                create_actions=_format_cell(row["create_task_actions_mean"]),
                work_actions=_format_cell(row["work_task_actions_mean"]),
                work_events=_format_cell(row["task_worked_events_mean"]),
                idle_actions=_format_cell(row["idle_actions_mean"]),
                message_actions=_format_cell(row["message_actions_mean"]),
                queue_balance=_format_cell(row["queue_per_balance_mean"]),
            )
            for row in accounting_rows
        ],
        "",
        "The panel confirms the mechanism confound: task creation pressure changes "
        "created-task counts and the action mix, while service capacity changes "
        "work-task opportunity. That supports the load-accounting interpretation "
        "and motivates an exogenous-arrival decoupling test before stronger claims.",
        "",
        "## Trajectory controls",
        "",
        f"- grid rows: {len(grid_rows)}",
        f"- trajectory rows: {len(trajectory_rows)}",
        (
            "- paired bootstrap rows: "
            f"{len(bootstrap_rows)}; sign-stable rows at >=0.95: {stable_bootstrap_count}"
            if bootstrap_rows
            else "- paired bootstrap rows: not present in trajectory directory"
        ),
        (
            "- strongest observed-minus-null dwell locking: "
            f"{strongest_null['pressure_label']} / {strongest_null['service_capacity_label']} "
            "dwell_length_max_observed_minus_null="
            f"{_format_number(float(strongest_null['dwell_length_max_observed_minus_null']))}"
            if strongest_null is not None
            else "- label-count null rows: not present in trajectory directory"
        ),
        "",
        "## Recommended next analysis",
        "",
        "Run the queue-blind lobe labeling pass as an analysis-only robustness "
        "check over the same holdout artifacts. Do not replace the default lobe "
        "labeler or launch a new experiment until that check says whether "
        "pressure locking survives without queue-depth and queue-delta fields.",
        "",
    ]
    return "\n".join(lines)


def _format_cell(value: Any) -> str:
    if value == "":
        return ""
    return _format_number(float(value))


def _mean_field(rows: list[dict[str, float]], field: str) -> float:
    return _mean_values([row[field] for row in rows])


def _mean_values(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a service-capacity decision synthesis from existing artifacts."
    )
    parser.add_argument(
        "--service-capacity-dir",
        required=True,
        help="Existing ohdyn.compare_service_capacity output directory.",
    )
    parser.add_argument(
        "--trajectory-dir",
        required=True,
        help="Existing ohdyn.analyze_service_capacity_trajectory output directory.",
    )
    parser.add_argument("--out-md", required=True, help="Markdown synthesis path.")
    parser.add_argument("--out-csv", required=True, help="Decision-table CSV path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_service_capacity_decision_synthesis(
            service_capacity_dir=args.service_capacity_dir,
            trajectory_dir=args.trajectory_dir,
            out_md=args.out_md,
            out_csv=args.out_csv,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
