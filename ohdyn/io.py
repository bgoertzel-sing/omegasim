"""Output writers for OmegaSim run artifacts."""

from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from ohdyn.sim import SimulationResult


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
        "model": {
            "agent_ids": [agent.agent_id for agent in result.agents],
            "roles": {agent.agent_id: agent.role for agent in result.agents},
            "bus_nodes": result.bus_graph.number_of_nodes(),
            "bus_edges": result.bus_graph.number_of_edges(),
        },
        "config": result.config.to_dict(),
    }


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
    return "\n".join(
        [
            f"# {result.config.run.experiment_id}",
            "",
            f"- seed: {result.seed}",
            f"- ticks: {result.config.run.ticks}",
            f"- agents: {result.config.model.agent_count}",
            f"- bus graph: {result.bus_graph.number_of_nodes()} nodes, {result.bus_graph.number_of_edges()} edges",
            f"- events: {total_events}",
            f"- messages sent: {total_messages}",
            f"- task work events: {total_work}",
            f"- tasks created: {last.get('tasks_created_total', 0)}",
            f"- tasks completed: {last.get('tasks_completed_total', 0)}",
            f"- final queue depth: {last.get('queue_depth', 0)}",
            "",
        ]
    )
