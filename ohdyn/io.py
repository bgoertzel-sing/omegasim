"""Output writers for OmegaSim run artifacts."""

from __future__ import annotations

import csv
import subprocess
import sys
from collections import Counter
from dataclasses import asdict
from importlib import metadata
from pathlib import Path
from typing import Any

import yaml

from ohdyn.sim import BASELINE_LOBE_LABELS, BASELINE_ROLES, SimulationResult


def write_outputs(result: SimulationResult, out_dir: str | Path) -> None:
    output_path = Path(out_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "config.yaml").write_text(
        yaml.safe_dump(result.config.to_dict(), sort_keys=True)
    )

    if result.config.outputs.write_manifest:
        (output_path / "manifest.yaml").write_text(
            yaml.safe_dump(_manifest(result), sort_keys=True)
        )
    if result.config.outputs.write_metrics:
        _write_csv(output_path / "metrics.csv", result.metrics)
    if result.config.outputs.write_events:
        _write_csv(output_path / "events.csv", result.events)
    if result.config.outputs.write_summary:
        (output_path / "summary.md").write_text(_summary(result))


def _manifest(result: SimulationResult) -> dict[str, Any]:
    return {
        "experiment_id": result.config.run.experiment_id,
        "seed": result.seed,
        "ticks": result.config.run.ticks,
        "agent_count": result.config.model.agent_count,
        "actions": list(result.config.model.actions),
        "outputs": asdict(result.config.outputs),
        "artifacts": _artifact_names(result),
        "environment": _environment_manifest(),
        "model": {
            "agent_ids": [agent.agent_id for agent in result.agents],
            "roles": {agent.agent_id: agent.role for agent in result.agents},
            "bus_nodes": result.bus_graph.number_of_nodes(),
            "bus_edges": result.bus_graph.number_of_edges(),
        },
        "config": result.config.to_dict(),
    }


def _environment_manifest() -> dict[str, Any]:
    return {
        "git_commit": _git_commit(),
        "python_version": sys.version.split()[0],
        "package_versions": _package_versions(
            [
                "mesa",
                "networkx",
                "numpy",
                "pandas",
                "pydantic",
                "pyyaml",
            ]
        ),
    }


def _git_commit() -> str:
    project_root = Path(__file__).resolve().parents[1]
    try:
        completed = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _package_versions(packages: list[str]) -> dict[str, str]:
    versions = {}
    for package in packages:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = "not-installed"
    return versions


def _artifact_names(result: SimulationResult) -> list[str]:
    artifacts = ["config.yaml"]
    if result.config.outputs.write_manifest:
        artifacts.append("manifest.yaml")
    if result.config.outputs.write_metrics:
        artifacts.append("metrics.csv")
    if result.config.outputs.write_events:
        artifacts.append("events.csv")
    if result.config.outputs.write_summary:
        artifacts.append("summary.md")
    return artifacts


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _summary(result: SimulationResult) -> str:
    last = result.metrics[-1] if result.metrics else {}
    total_events = len(result.events)
    total_messages = sum(1 for event in result.events if event["event_type"] == "message_sent")
    total_work = sum(1 for event in result.events if event["event_type"] == "task_worked")
    lines = [
        f"# {result.config.run.experiment_id}",
        "",
        f"- seed: {result.seed}",
        f"- ticks: {result.config.run.ticks}",
        f"- agents: {result.config.model.agent_count}",
        f"- bus graph: {result.bus_graph.number_of_nodes()} nodes, {result.bus_graph.number_of_edges()} edges",
        f"- bus density: {last.get('bus_density', 0)}",
        f"- bus degree centralization: {last.get('bus_degree_centralization', 0)}",
        f"- events: {total_events}",
        f"- messages sent: {total_messages}",
        f"- task work events: {total_work}",
        f"- tasks created: {last.get('tasks_created_total', 0)}",
        f"- tasks completed: {last.get('tasks_completed_total', 0)}",
        f"- final queue depth: {last.get('queue_depth', 0)}",
        f"- final backlog pressure: {last.get('backlog_pressure_tick', 0)}",
        f"- final queued task max age: {last.get('queued_task_age_max_tick', 0)}",
        f"- final queued task mean age: {last.get('queued_task_age_mean_tick', 0)}",
        f"- peak queued task max age: {_peak_queued_task_age(result)}",
        f"- mean queued task mean age: {_mean_queued_task_mean_age(result)}",
        f"- created-completed balance: {_created_completed_balance(result)}",
        f"- created-worked balance: {_created_worked_balance(result)}",
        f"- work-completion gap: {_work_completion_gap(result)}",
        "",
        "## Baseline lobe totals",
        "",
    ]
    for label, count in _baseline_lobe_totals(result).items():
        lines.append(f"- {label}: {count}")
    lines.extend(
        [
            "",
            "## Baseline lobe transitions",
            "",
        ]
    )
    for transition, count in _baseline_lobe_transition_totals(result).items():
        lines.append(f"- {transition}: {count}")
    lines.extend(
        [
            "",
            "## Role action totals",
            "",
        ]
    )
    for role, totals in _role_action_totals(result).items():
        lines.append(
            f"- {role}: idle={totals['idle']}, message={totals['message']}, "
            f"create_task={totals['create_task']}, work_task={totals['work_task']}"
        )
    lines.append("")
    return "\n".join(lines)


def _baseline_lobe_totals(result: SimulationResult) -> dict[str, int]:
    counts = Counter(str(row.get("baseline_lobe_label", "")) for row in result.metrics)
    return {
        label: counts[label]
        for label in BASELINE_LOBE_LABELS
        if counts[label] > 0
    }


def _baseline_lobe_transition_totals(result: SimulationResult) -> dict[str, int]:
    counts = Counter(
        str(row.get("baseline_lobe_transition", ""))
        for row in result.metrics
        if row.get("baseline_lobe_transition") not in {"", "start", "stable"}
    )
    return dict(sorted(counts.items()))


def _role_action_totals(result: SimulationResult) -> dict[str, dict[str, int]]:
    return {
        role: {
            action: sum(
                int(row.get(f"role_{role}_{action}_tick", 0))
                for row in result.metrics
            )
            for action in result.config.model.actions
        }
        for role in BASELINE_ROLES
    }


def _created_completed_balance(result: SimulationResult) -> int:
    return sum(int(row.get("created_completed_balance_tick", 0)) for row in result.metrics)


def _created_worked_balance(result: SimulationResult) -> int:
    return sum(int(row.get("created_worked_balance_tick", 0)) for row in result.metrics)


def _work_completion_gap(result: SimulationResult) -> int:
    return sum(int(row.get("work_completion_gap_tick", 0)) for row in result.metrics)


def _peak_queued_task_age(result: SimulationResult) -> int:
    return max((int(row.get("queued_task_age_max_tick", 0)) for row in result.metrics), default=0)


def _mean_queued_task_mean_age(result: SimulationResult) -> float:
    if not result.metrics:
        return 0.0
    return round(
        sum(float(row.get("queued_task_age_mean_tick", 0.0)) for row in result.metrics)
        / len(result.metrics),
        6,
    )
