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

from ohdyn.config import ATTENTION_CLASSES
from ohdyn.sim import (
    ATTENTION_EVENT_TYPES,
    BASELINE_EVENT_TYPES,
    BASELINE_LOBE_LABELS,
    BASELINE_LOBE_TRANSITION_FIELDS,
    BASELINE_ROLES,
    COUPLING_EVENT_FIELDS,
    CROSS_HIVE_METRIC_FIELDS,
    EVENT_FIELDS,
    EXOGENOUS_ARRIVAL_EVENT_TYPES,
    EXOGENOUS_ARRIVAL_METRIC_FIELDS,
    HIVE_EVENT_FIELDS,
    MULTI_HIVE_QUEUE_FLOW_METRIC_FIELDS,
    QUEUE_PRESSURE_METRIC_FIELDS,
    QUEUED_TASK_AGE_METRIC_FIELDS,
    SimulationResult,
    attention_policy_metric_fields,
    metrics_fieldnames,
    role_action_metric_fields,
)


def write_outputs(result: SimulationResult, out_dir: str | Path) -> None:
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path, _artifact_names(result))
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "config.yaml").write_text(
        yaml.safe_dump(result.config.to_dict(), sort_keys=True)
    )

    if result.config.outputs.write_manifest:
        (output_path / "manifest.yaml").write_text(
            yaml.safe_dump(_manifest(result), sort_keys=True)
        )
    if result.config.outputs.write_metrics:
        _write_csv(
            output_path / "metrics.csv",
            result.metrics,
            fieldnames=_metrics_fieldnames(result),
        )
        if _multi_hive_enabled(result):
            _write_csv(
                output_path / "hive_metrics.csv",
                result.hive_metrics or [],
                fieldnames=("hive_id", *_metrics_fieldnames(result)),
            )
            _write_csv(
                output_path / "cross_hive_metrics.csv",
                result.cross_hive_metrics or [],
                fieldnames=_cross_hive_metric_fieldnames(result),
            )
    if result.config.outputs.write_events:
        _write_csv(output_path / "events.csv", result.events, fieldnames=EVENT_FIELDS)
        if _multi_hive_enabled(result):
            _write_csv(
                output_path / "hive_events.csv",
                result.hive_events or [],
                fieldnames=HIVE_EVENT_FIELDS,
            )
            _write_csv(
                output_path / "coupling_events.csv",
                result.coupling_events or [],
                fieldnames=COUPLING_EVENT_FIELDS,
            )
    if result.config.outputs.write_summary:
        (output_path / "summary.md").write_text(_summary(result))


def _ensure_output_paths_available(output_path: Path, artifact_names: list[str]) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")

    collisions = [
        artifact_name
        for artifact_name in artifact_names
        if (output_path / artifact_name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains run artifacts: {names}")


def _manifest(result: SimulationResult) -> dict[str, Any]:
    manifest = {
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
            "baseline_lobes": {
                "labels": list(BASELINE_LOBE_LABELS),
                "transition_fields": list(BASELINE_LOBE_TRANSITION_FIELDS),
            },
            "queue_dynamics_metrics": {
                "pressure_fields": list(QUEUE_PRESSURE_METRIC_FIELDS),
                "queued_task_age_fields": list(QUEUED_TASK_AGE_METRIC_FIELDS),
            },
            "events": {
                "types": list(_event_types(result)),
                "fields": list(EVENT_FIELDS),
            },
            "metrics": {
                "fields": list(_metrics_fieldnames(result)),
            },
            "role_action_metrics": {
                "roles": list(BASELINE_ROLES),
                "actions": list(result.config.model.actions),
                "fields": list(role_action_metric_fields(result.config.model.actions)),
            },
        },
        "config": result.config.to_dict(),
    }
    if result.config.attention_policy is not None:
        manifest["model"]["attention_policy"] = {
            "classes": list(ATTENTION_CLASSES),
            "selection_strategy": result.config.attention_policy.selection_strategy,
            "fields": list(attention_policy_metric_fields()),
        }
    if _exogenous_arrivals_enabled(result) and result.config.exogenous_arrivals is not None:
        assert result.config.exogenous_arrivals is not None
        manifest["model"]["exogenous_arrivals"] = {
            "enabled": result.config.exogenous_arrivals.enabled,
            "rate_per_tick": result.config.exogenous_arrivals.rate_per_tick,
            "task_class_shares": result.config.exogenous_arrivals.task_class_shares(),
            "rng_stream": {
                "agent_action_stream": "numpy.default_rng(seed)",
                "exogenous_arrival_stream": (
                    "numpy.default_rng(SeedSequence([seed, 0xE906E, 0xA2]))"
                ),
                "separated_from_agent_actions": True,
            },
            "event_types": list(EXOGENOUS_ARRIVAL_EVENT_TYPES),
            "fields": list(EXOGENOUS_ARRIVAL_METRIC_FIELDS),
        }
    if _multi_hive_enabled(result):
        assert result.config.coupling is not None
        manifest["hive_count"] = len(result.config.hives)
        manifest["hive_ids"] = [hive.hive_id for hive in result.config.hives]
        manifest["coupling_mode"] = result.config.coupling.mode
        manifest["model"]["multi_hive"] = {
            "hive_count": len(result.config.hives),
            "hive_ids": [hive.hive_id for hive in result.config.hives],
            "coupling_mode": result.config.coupling.mode,
            "hive_seed_streams": {
                hive.hive_id: f"cli_seed + {hive.seed_offset}"
                for hive in result.config.hives
            },
            "coupling_seed_stream": (
                f"cli_seed + {result.config.coupling.shuffle_seed_offset}"
            ),
            "coupling_event_fields": list(COUPLING_EVENT_FIELDS),
            "cross_hive_metric_fields": list(_cross_hive_metric_fieldnames(result)),
        }
    return manifest


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
    if _multi_hive_enabled(result):
        if result.config.outputs.write_metrics:
            artifacts.extend(["hive_metrics.csv", "cross_hive_metrics.csv"])
        if result.config.outputs.write_events:
            artifacts.extend(["hive_events.csv", "coupling_events.csv"])
    return artifacts


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    *,
    fieldnames: tuple[str, ...] | None = None,
) -> None:
    if not rows:
        if fieldnames is None:
            path.write_text("")
            return
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
            writer.writeheader()
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames or rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _metrics_fieldnames(result: SimulationResult) -> tuple[str, ...]:
    fields = metrics_fieldnames(
        result.config.model.actions,
        include_attention_policy=result.config.attention_policy is not None,
        include_exogenous_arrivals=_exogenous_arrivals_enabled(result),
    )
    if _multi_hive_enabled(result):
        return (*fields, *MULTI_HIVE_QUEUE_FLOW_METRIC_FIELDS)
    return fields


def _event_types(result: SimulationResult) -> tuple[str, ...]:
    event_types = list(BASELINE_EVENT_TYPES)
    if result.config.attention_policy is not None:
        event_types.extend(ATTENTION_EVENT_TYPES)
    if _exogenous_arrivals_enabled(result):
        event_types.extend(EXOGENOUS_ARRIVAL_EVENT_TYPES)
    return tuple(event_types)


def _multi_hive_enabled(result: SimulationResult) -> bool:
    return bool(result.config.hives)


def _cross_hive_metric_fieldnames(result: SimulationResult) -> tuple[str, ...]:
    return (
        *CROSS_HIVE_METRIC_FIELDS,
        *(
            f"{hive.hive_id}_load_normalized_backlog_tick"
            for hive in result.config.hives
        ),
    )


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
        f"- bus mean degree: {last.get('bus_mean_degree', 0)}",
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
        "## Run artifacts and outputs",
        "",
        *_artifact_output_summary(result),
        "",
        "## Artifact schema provenance",
        "",
        *_artifact_schema_provenance(result),
        "",
        "## Event type totals",
        "",
    ]
    for event_type, count in _event_type_totals(result).items():
        lines.append(f"- {event_type}: {count}")
    lines.extend(
        [
            "",
            "## Baseline lobe totals",
            "",
        ]
    )
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
            "## Baseline lobe dwell runs",
            "",
        ]
    )
    for label, dwell in _baseline_lobe_dwell_runs(result).items():
        lines.append(
            f"- {label}: runs={dwell['runs']}, total_ticks={dwell['total_ticks']}, "
            f"max_run={dwell['max_run']}, mean_run={dwell['mean_run']}"
        )
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
    if _multi_hive_enabled(result):
        assert result.config.coupling is not None
        lines.extend(
            [
                "",
                "## Multi-hive coupling",
                "",
                f"- hive count: {len(result.config.hives)}",
                f"- hive ids: {', '.join(hive.hive_id for hive in result.config.hives)}",
                f"- coupling mode: {result.config.coupling.mode}",
                f"- transfer probability: {result.config.coupling.transfer_probability}",
                f"- delay ticks: {result.config.coupling.delay_ticks}",
                f"- completed transfers: {_completed_transfer_count(result)}",
                "",
                "## Hive summaries",
                "",
                *_hive_summary(result),
            ]
        )
    if result.config.attention_policy is not None:
        lines.extend(
            [
                "",
                "## Attention policy totals",
                "",
                *_attention_policy_summary(result),
            ]
        )
    if _exogenous_arrivals_enabled(result) and result.config.exogenous_arrivals is not None:
        lines.extend(
            [
                "",
                "## Exogenous arrival totals",
                "",
                *_exogenous_arrival_summary(result),
            ]
        )
    lines.append("")
    return "\n".join(lines)


def _completed_transfer_count(result: SimulationResult) -> int:
    return sum(
        int(bool(event.get("transfer_decision")))
        for event in (result.coupling_events or [])
    )


def _exogenous_arrivals_enabled(result: SimulationResult) -> bool:
    return (
        result.config.exogenous_arrivals is not None
        and result.config.exogenous_arrivals.enabled
    ) or any(_exogenous_arrivals_enabled(hive_result) for hive_result in result.hive_results)


def _hive_summary(result: SimulationResult) -> list[str]:
    lines = []
    for hive, hive_result in zip(result.config.hives, result.hive_results, strict=True):
        last = hive_result.metrics[-1] if hive_result.metrics else {}
        lines.append(
            f"- {hive.hive_id}: seed_offset={hive.seed_offset}, "
            f"exogenous_arrival_rate={hive.exogenous_arrival_rate}, "
            f"work_service_capacity={hive.work_service_capacity}, "
            f"tasks_created={last.get('tasks_created_total', 0)}, "
            f"tasks_completed={last.get('tasks_completed_total', 0)}, "
            f"final_queue_depth={last.get('queue_depth', 0)}"
        )
    return lines


def _baseline_lobe_totals(result: SimulationResult) -> dict[str, int]:
    counts = Counter(str(row.get("baseline_lobe_label", "")) for row in result.metrics)
    return {
        label: counts[label]
        for label in BASELINE_LOBE_LABELS
        if counts[label] > 0
    }


def _event_type_totals(result: SimulationResult) -> dict[str, int]:
    counts = Counter(str(event.get("event_type", "")) for event in result.events)
    return dict(sorted((event_type, count) for event_type, count in counts.items() if event_type))


def _artifact_output_summary(result: SimulationResult) -> list[str]:
    output_flags = asdict(result.config.outputs)
    return [
        f"- written artifacts: {', '.join(_artifact_names(result))}",
        *[
            f"- {name}: {'enabled' if enabled else 'disabled'}"
            for name, enabled in output_flags.items()
        ],
    ]


def _artifact_schema_provenance(result: SimulationResult) -> list[str]:
    metrics_fields = _metrics_fieldnames(result)
    event_fields = EVENT_FIELDS
    role_action_fields = role_action_metric_fields(result.config.model.actions)
    event_types = _event_types(result)
    return [
        f"- metrics fields: {len(metrics_fields)}",
        f"- event fields: {len(event_fields)}",
        f"- event types: {len(event_types)}",
        f"- baseline lobe labels: {len(BASELINE_LOBE_LABELS)}",
        f"- baseline lobe transition fields: {len(BASELINE_LOBE_TRANSITION_FIELDS)}",
        f"- queue pressure fields: {len(QUEUE_PRESSURE_METRIC_FIELDS)}",
        f"- queued task age fields: {len(QUEUED_TASK_AGE_METRIC_FIELDS)}",
        *(
            [f"- attention policy fields: {len(attention_policy_metric_fields())}"]
            if result.config.attention_policy is not None
            else []
        ),
        *(
            [f"- exogenous arrival fields: {len(EXOGENOUS_ARRIVAL_METRIC_FIELDS)}"]
            if _exogenous_arrivals_enabled(result)
            else []
        ),
        f"- role/action fields: {len(role_action_fields)}",
        "- metrics schema source: ohdyn.sim.metrics_fieldnames",
        "- events schema source: ohdyn.sim.EVENT_FIELDS",
        "- manifest mirrors emitted artifact schemas: yes",
    ]


def _baseline_lobe_transition_totals(result: SimulationResult) -> dict[str, int]:
    counts = Counter(
        str(row.get("baseline_lobe_transition", ""))
        for row in result.metrics
        if row.get("baseline_lobe_transition") not in {"", "start", "stable"}
    )
    return dict(sorted(counts.items()))


def _baseline_lobe_dwell_runs(result: SimulationResult) -> dict[str, dict[str, int | float]]:
    runs_by_label: dict[str, list[int]] = {label: [] for label in BASELINE_LOBE_LABELS}
    previous_label = ""
    current_run_length = 0

    for row in result.metrics:
        label = str(row.get("baseline_lobe_label", ""))
        if not label:
            continue
        if label == previous_label:
            current_run_length += 1
        else:
            if previous_label:
                runs_by_label.setdefault(previous_label, []).append(current_run_length)
            previous_label = label
            current_run_length = 1

    if previous_label:
        runs_by_label.setdefault(previous_label, []).append(current_run_length)

    dwell: dict[str, dict[str, int | float]] = {}
    for label in BASELINE_LOBE_LABELS:
        runs = runs_by_label.get(label, [])
        if not runs:
            continue
        dwell[label] = {
            "runs": len(runs),
            "total_ticks": sum(runs),
            "max_run": max(runs),
            "mean_run": round(sum(runs) / len(runs), 6),
        }
    return dwell


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


def _attention_policy_summary(result: SimulationResult) -> list[str]:
    last = result.metrics[-1] if result.metrics else {}
    lines = []
    lines.append(
        "- selection strategy: "
        f"{result.config.attention_policy.selection_strategy}"
    )
    for class_name in ATTENTION_CLASSES:
        completed = last.get(f"attention_{class_name}_completed_total", 0)
        worked = last.get(f"attention_{class_name}_worked_total", 0)
        queued = last.get(f"attention_{class_name}_queued_tick", 0)
        target = last.get(f"attention_{class_name}_target_share", 0)
        mean_age = last.get(f"attention_{class_name}_queued_age_mean_tick", 0)
        capture_pressure = last.get(f"attention_{class_name}_capture_pressure_tick", 0)
        lines.append(
            f"- {class_name}: target_share={target}, completed={completed}, "
            f"worked={worked}, queued={queued}, final_mean_age={mean_age}, "
            f"capture_pressure={capture_pressure}"
        )
    lines.append(
        "- max capture pressure: "
        f"{last.get('attention_capture_pressure_max_tick', 0)}"
    )
    lines.append(
        "- value-weighted completed work: "
        f"{last.get('attention_value_weighted_completed_total', 0)}"
    )
    lines.append(
        "- value per completed task: "
        f"{last.get('attention_value_per_completed_task_total', 0)}"
    )
    lines.append(
        "- value per work event: "
        f"{last.get('attention_value_per_work_event_total', 0)}"
    )
    return lines


def _exogenous_arrival_summary(result: SimulationResult) -> list[str]:
    last = result.metrics[-1] if result.metrics else {}
    assert result.config.exogenous_arrivals is not None
    return [
        f"- enabled: {result.config.exogenous_arrivals.enabled}",
        f"- rate per tick: {result.config.exogenous_arrivals.rate_per_tick}",
        f"- task class shares: {result.config.exogenous_arrivals.task_class_shares()}",
        f"- agent-created tasks: {last.get('agent_tasks_created_total', 0)}",
        f"- exogenous tasks: {last.get('exogenous_tasks_created_total', 0)}",
        f"- total created tasks: {last.get('tasks_created_total', 0)}",
    ]


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
