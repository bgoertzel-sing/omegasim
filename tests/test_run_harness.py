from __future__ import annotations

from collections import Counter, deque
from pathlib import Path
import csv
import subprocess
import sys

import pytest
import yaml

from ohdyn.sim import (
    BASELINE_EVENT_TYPES,
    BASELINE_LOBE_LABELS,
    BASELINE_LOBE_TRANSITION_FIELDS,
    BASELINE_ROLES,
    EVENT_FIELDS,
    QUEUE_PRESSURE_METRIC_FIELDS,
    QUEUED_TASK_AGE_METRIC_FIELDS,
    metrics_fieldnames,
    role_action_metric_fields,
)
from ohdyn.config import load_config
from ohdyn.run import run_experiment


CONFIG = Path("configs/a0_smoke.yaml")
DEFAULT_OUTPUTS = Path("configs/a0_default_outputs.yaml")
CONFIG_ONLY = Path("configs/a0_config_only.yaml")
MANIFEST_ONLY = Path("configs/a0_manifest_only.yaml")
NO_MANIFEST = Path("configs/a0_no_manifest.yaml")

A0_FULL_ARTIFACTS = [
    "config.yaml",
    "manifest.yaml",
    "metrics.csv",
    "events.csv",
    "summary.md",
]
CONFIG_ONLY_ARTIFACTS = ["config.yaml"]
MANIFEST_ONLY_ARTIFACTS = ["config.yaml", "manifest.yaml"]
NO_MANIFEST_ARTIFACTS = ["config.yaml", "metrics.csv", "events.csv", "summary.md"]
OUTPUT_FIXTURE_ARTIFACTS = {
    CONFIG: A0_FULL_ARTIFACTS,
    DEFAULT_OUTPUTS: A0_FULL_ARTIFACTS,
    CONFIG_ONLY: CONFIG_ONLY_ARTIFACTS,
    MANIFEST_ONLY: MANIFEST_ONLY_ARTIFACTS,
    NO_MANIFEST: NO_MANIFEST_ARTIFACTS,
}


def _expected_artifacts(config_path: Path) -> list[str]:
    return list(OUTPUT_FIXTURE_ARTIFACTS[config_path])


def _run_documented_cli(
    config_path: Path,
    out_dir: Path,
    *,
    seed: int = 1,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
            "--seed",
            str(seed),
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    return completed


def test_loads_a0_smoke_config() -> None:
    config = load_config(CONFIG)

    assert config.run.experiment_id == "a0_smoke"
    assert config.run.ticks == 100
    assert config.model.agent_count == 15
    assert set(config.model.actions) == {"idle", "message", "create_task", "work_task"}


def test_loads_a0_default_outputs_fixture() -> None:
    config = load_config(DEFAULT_OUTPUTS)

    assert config.run.experiment_id == "a0_default_outputs"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("idle", "message", "create_task", "work_task")
    assert config.outputs.write_manifest is True
    assert config.outputs.write_metrics is True
    assert config.outputs.write_events is True
    assert config.outputs.write_summary is True


def test_loads_a0_config_only_fixture() -> None:
    config = load_config(CONFIG_ONLY)

    assert config.run.experiment_id == "a0_config_only"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("idle", "message", "create_task", "work_task")
    assert config.outputs.write_manifest is False
    assert config.outputs.write_metrics is False
    assert config.outputs.write_events is False
    assert config.outputs.write_summary is False


def test_loads_a0_manifest_only_fixture() -> None:
    config = load_config(MANIFEST_ONLY)

    assert config.run.experiment_id == "a0_manifest_only"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("idle", "message", "create_task", "work_task")
    assert config.outputs.write_manifest is True
    assert config.outputs.write_metrics is False
    assert config.outputs.write_events is False
    assert config.outputs.write_summary is False


def test_loads_a0_no_manifest_fixture() -> None:
    config = load_config(NO_MANIFEST)

    assert config.run.experiment_id == "a0_no_manifest"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("idle", "message", "create_task", "work_task")
    assert config.outputs.write_manifest is False
    assert config.outputs.write_metrics is True
    assert config.outputs.write_events is True
    assert config.outputs.write_summary is True


def test_run_writes_required_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    result = run_experiment(CONFIG, seed=1, out_dir=out_dir)

    assert result.bus_graph.number_of_nodes() == 16
    assert result.bus_graph.number_of_edges() == 15
    assert len(result.agents) == 15
    assert len(result.metrics) == 100
    assert len(result.events) == 1500
    assert result.metrics[0]["bus_density"] == 0.125
    assert result.metrics[0]["bus_mean_degree"] == 1.875
    assert result.metrics[0]["bus_degree_centralization"] == 1.0
    assert (out_dir / "manifest.yaml").is_file()
    assert (out_dir / "metrics.csv").is_file()
    assert (out_dir / "events.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["seed"] == 1
    assert manifest["agent_count"] == 15
    assert manifest["model"]["bus_edges"] == 15


def test_metrics_csv_records_bus_graph_summary(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    metrics_header = (out_dir / "metrics.csv").read_text().splitlines()[0].split(",")
    first_row = (out_dir / "metrics.csv").read_text().splitlines()[1].split(",")
    row = dict(zip(metrics_header, first_row))

    assert row["bus_density"] == "0.125"
    assert row["bus_mean_degree"] == "1.875"
    assert row["bus_degree_centralization"] == "1.0"
    assert "- bus density: 0.125" in (out_dir / "summary.md").read_text()
    assert "- bus mean degree: 1.875" in (out_dir / "summary.md").read_text()


def test_metrics_csv_records_role_action_counts(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    metrics_lines = (out_dir / "metrics.csv").read_text().splitlines()
    metrics_header = metrics_lines[0].split(",")
    first_row = dict(zip(metrics_header, metrics_lines[1].split(",")))
    actions = ("idle", "message", "create_task", "work_task")

    for role in BASELINE_ROLES:
        assert {f"role_{role}_{action}_tick" for action in actions} <= set(metrics_header)
        assert sum(int(first_row[f"role_{role}_{action}_tick"]) for action in actions) == 3

    assert sum(int(first_row[f"role_{role}_message_tick"]) for role in BASELINE_ROLES) == int(
        first_row["messages_sent_tick"]
    )
    assert sum(int(first_row[f"role_{role}_create_task_tick"]) for role in BASELINE_ROLES) == int(
        first_row["tasks_created_tick"]
    )
    assert sum(int(first_row[f"role_{role}_work_task_tick"]) for role in BASELINE_ROLES) == int(
        first_row["tasks_worked_tick"]
    )
    assert sum(int(first_row[f"role_{role}_idle_tick"]) for role in BASELINE_ROLES) == int(
        first_row["idle_tick"]
    )

    summary = (out_dir / "summary.md").read_text()
    assert "## Role action totals" in summary
    assert "- coordinator: idle=" in summary


def test_metrics_and_events_headers_match_documented_a0_schema(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))

    assert metrics_header == list(metrics_fieldnames(("idle", "message", "create_task", "work_task")))
    assert events_header == list(EVENT_FIELDS)


def test_summary_records_event_type_totals(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    result = run_experiment(CONFIG, seed=1, out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()
    assert "## Event type totals" in summary
    for event_type, count in sorted(Counter(event["event_type"] for event in result.events).items()):
        assert f"- {event_type}: {count}" in summary


def test_metrics_csv_records_baseline_lobe_labels(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert set(row["baseline_lobe_label"] for row in rows) <= set(BASELINE_LOBE_LABELS)
    assert any(row["baseline_lobe_label"] == "backlog_growth" for row in rows)
    assert any(row["baseline_lobe_label"] == "execution" for row in rows)

    previous_queue_depth = 0
    for row in rows:
        queue_depth = int(row["queue_depth"])
        queue_delta = int(row["queue_delta_tick"])
        assert queue_depth - previous_queue_depth == queue_delta
        previous_queue_depth = queue_depth

    summary = (out_dir / "summary.md").read_text()
    assert "## Baseline lobe totals" in summary
    assert "- backlog_growth: " in summary


def test_metrics_csv_records_queue_pressure_balances(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    created_completed_balance = 0
    created_worked_balance = 0
    work_completion_gap = 0
    for row in rows:
        created = int(row["tasks_created_tick"])
        worked = int(row["tasks_worked_tick"])
        completed = int(row["tasks_completed_tick"])

        assert int(row["created_completed_balance_tick"]) == created - completed
        assert int(row["created_worked_balance_tick"]) == created - worked
        assert int(row["work_completion_gap_tick"]) == worked - completed
        assert int(row["backlog_pressure_tick"]) == int(row["queue_depth"])

        created_completed_balance += int(row["created_completed_balance_tick"])
        created_worked_balance += int(row["created_worked_balance_tick"])
        work_completion_gap += int(row["work_completion_gap_tick"])

    last = rows[-1]
    assert created_completed_balance == int(last["queue_depth"])
    assert created_completed_balance == created_worked_balance + work_completion_gap

    summary = (out_dir / "summary.md").read_text()
    assert f"- final backlog pressure: {last['queue_depth']}" in summary
    assert f"- created-completed balance: {created_completed_balance}" in summary
    assert f"- created-worked balance: {created_worked_balance}" in summary
    assert f"- work-completion gap: {work_completion_gap}" in summary


def test_metrics_csv_records_queued_task_age(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metrics_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    summary = (out_dir / "summary.md").read_text()

    _assert_event_replay_reproduces_queued_task_age_metrics(
        metric_rows=metrics_rows,
        event_rows=event_rows,
    )
    _assert_queued_task_age_summary_matches_metrics(
        summary,
        metric_rows=metrics_rows,
    )


def test_metrics_csv_records_baseline_lobe_transitions(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["baseline_lobe_previous_label"] == ""
    assert rows[0]["baseline_lobe_transition"] == "start"
    assert rows[0]["baseline_lobe_transition_tick"] == "0"

    transition_counts: dict[str, int] = {}
    previous_label = rows[0]["baseline_lobe_label"]
    for row in rows[1:]:
        current_label = row["baseline_lobe_label"]
        expected_transition = (
            "stable"
            if previous_label == current_label
            else f"{previous_label}->{current_label}"
        )
        assert row["baseline_lobe_previous_label"] == previous_label
        assert row["baseline_lobe_transition"] == expected_transition
        assert row["baseline_lobe_transition_tick"] == str(int(previous_label != current_label))
        if expected_transition != "stable":
            transition_counts[expected_transition] = transition_counts.get(expected_transition, 0) + 1
        previous_label = current_label

    assert transition_counts
    summary = (out_dir / "summary.md").read_text()
    assert "## Baseline lobe transitions" in summary
    for transition, count in transition_counts.items():
        assert f"- {transition}: {count}" in summary


def test_metrics_csv_records_baseline_lobe_run_state(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert rows[0]["baseline_lobe_run_id"] == "1"
    assert rows[0]["baseline_lobe_current_run_length"] == "1"

    previous_label = ""
    expected_run_id = 0
    expected_run_length = 0
    completed_runs: list[tuple[int, str, int]] = []
    for row in rows:
        label = row["baseline_lobe_label"]
        if label == previous_label:
            expected_run_length += 1
        else:
            if previous_label:
                completed_runs.append((expected_run_id, previous_label, expected_run_length))
            expected_run_id += 1
            expected_run_length = 1

        assert int(row["baseline_lobe_run_id"]) == expected_run_id
        assert int(row["baseline_lobe_current_run_length"]) == expected_run_length
        previous_label = label

    completed_runs.append((expected_run_id, previous_label, expected_run_length))
    assert expected_run_id == sum(dwell["runs"] for dwell in _lobe_dwell_runs(rows).values())
    assert max(run_length for _, _, run_length in completed_runs) == max(
        dwell["max_run"] for dwell in _lobe_dwell_runs(rows).values()
    )


def test_summary_records_baseline_lobe_dwell_runs(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    result = run_experiment(CONFIG, seed=1, out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()
    assert "## Baseline lobe dwell runs" in summary
    for label, dwell in _lobe_dwell_runs(result.metrics).items():
        assert (
            f"- {label}: runs={dwell['runs']}, total_ticks={dwell['total_ticks']}, "
            f"max_run={dwell['max_run']}, mean_run={dwell['mean_run']}"
        ) in summary


def test_manifest_records_environment_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    environment = manifest["environment"]

    assert environment["git_commit"]
    assert environment["python_version"] == sys.version.split()[0]
    assert set(environment["package_versions"]) == {
        "mesa",
        "networkx",
        "numpy",
        "pandas",
        "pydantic",
        "pyyaml",
    }


def test_manifest_and_config_match_documented_a0_provenance_schema(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())

    actions = ["idle", "message", "create_task", "work_task"]
    agent_ids = [f"agent_{index:02d}" for index in range(1, 16)]
    roles = {
        agent_id: BASELINE_ROLES[(index - 1) % len(BASELINE_ROLES)]
        for index, agent_id in enumerate(agent_ids, start=1)
    }
    expected_config = {
        "run": {
            "experiment_id": "a0_smoke",
            "ticks": 100,
        },
        "model": {
            "agent_count": 15,
            "actions": actions,
        },
        "outputs": {
            "write_manifest": True,
            "write_metrics": True,
            "write_events": True,
            "write_summary": True,
        },
    }

    assert normalized_config == expected_config
    assert set(manifest) == {
        "experiment_id",
        "seed",
        "ticks",
        "agent_count",
        "actions",
        "outputs",
        "artifacts",
        "environment",
        "model",
        "config",
    }
    assert manifest["experiment_id"] == "a0_smoke"
    assert manifest["seed"] == 1
    assert manifest["ticks"] == 100
    assert manifest["agent_count"] == 15
    assert manifest["actions"] == actions
    assert manifest["outputs"] == expected_config["outputs"]
    assert manifest["artifacts"] == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]
    assert manifest["config"] == normalized_config
    assert manifest["model"] == {
        "agent_ids": agent_ids,
        "roles": roles,
        "bus_nodes": 16,
        "bus_edges": 15,
        "baseline_lobes": {
            "labels": list(BASELINE_LOBE_LABELS),
            "transition_fields": list(BASELINE_LOBE_TRANSITION_FIELDS),
        },
        "queue_dynamics_metrics": {
            "pressure_fields": list(QUEUE_PRESSURE_METRIC_FIELDS),
            "queued_task_age_fields": list(QUEUED_TASK_AGE_METRIC_FIELDS),
        },
        "events": {
            "types": list(BASELINE_EVENT_TYPES),
            "fields": list(EVENT_FIELDS),
        },
        "metrics": {
            "fields": list(metrics_fieldnames(tuple(actions))),
        },
        "role_action_metrics": {
            "roles": list(BASELINE_ROLES),
            "actions": actions,
            "fields": list(role_action_metric_fields(tuple(actions))),
        },
    }


def test_manifest_records_baseline_lobe_metric_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    baseline_lobes = manifest["model"]["baseline_lobes"]
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    assert baseline_lobes == {
        "labels": list(BASELINE_LOBE_LABELS),
        "transition_fields": list(BASELINE_LOBE_TRANSITION_FIELDS),
    }
    assert "baseline_lobe_label" in metrics_header
    for field in baseline_lobes["transition_fields"]:
        assert field in metrics_header


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_manifest_lobe_transition_fields_exactly_match_metrics_columns_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    emitted_transition_fields = [
        field
        for field in metrics_header
        if field.startswith("baseline_lobe_") and field != "baseline_lobe_label"
    ]

    assert manifest["model"]["baseline_lobes"]["transition_fields"] == emitted_transition_fields
    assert emitted_transition_fields == list(BASELINE_LOBE_TRANSITION_FIELDS)


def test_manifest_records_role_action_metric_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    role_action_metrics = manifest["model"]["role_action_metrics"]
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    expected_fields = list(role_action_metric_fields(tuple(manifest["actions"])))
    assert role_action_metrics == {
        "roles": list(BASELINE_ROLES),
        "actions": manifest["actions"],
        "fields": expected_fields,
    }
    for field in role_action_metrics["fields"]:
        assert field in metrics_header


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_manifest_role_action_fields_exactly_match_metrics_columns_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    emitted_role_action_fields = [
        field for field in metrics_header if field.startswith("role_")
    ]

    assert manifest["model"]["role_action_metrics"]["fields"] == emitted_role_action_fields
    assert emitted_role_action_fields == list(role_action_metric_fields(tuple(manifest["actions"])))


def test_manifest_records_queue_dynamics_metric_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    queue_dynamics_metrics = manifest["model"]["queue_dynamics_metrics"]
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    assert queue_dynamics_metrics == {
        "pressure_fields": list(QUEUE_PRESSURE_METRIC_FIELDS),
        "queued_task_age_fields": list(QUEUED_TASK_AGE_METRIC_FIELDS),
    }
    for field in [
        *queue_dynamics_metrics["pressure_fields"],
        *queue_dynamics_metrics["queued_task_age_fields"],
    ]:
        assert field in metrics_header


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_manifest_queue_dynamics_fields_exactly_match_metrics_columns_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    queue_dynamics_metrics = manifest["model"]["queue_dynamics_metrics"]
    emitted_pressure_fields = [
        field for field in metrics_header if field in QUEUE_PRESSURE_METRIC_FIELDS
    ]
    emitted_queued_task_age_fields = [
        field for field in metrics_header if field in QUEUED_TASK_AGE_METRIC_FIELDS
    ]

    assert queue_dynamics_metrics["pressure_fields"] == emitted_pressure_fields
    assert queue_dynamics_metrics["queued_task_age_fields"] == emitted_queued_task_age_fields
    assert emitted_pressure_fields == list(QUEUE_PRESSURE_METRIC_FIELDS)
    assert emitted_queued_task_age_fields == list(QUEUED_TASK_AGE_METRIC_FIELDS)


def test_manifest_records_full_metrics_schema_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    expected_fields = list(metrics_fieldnames(tuple(manifest["actions"])))
    assert manifest["model"]["metrics"] == {"fields": expected_fields}
    assert metrics_header == expected_fields


def test_manifest_records_event_schema_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    event_schema = manifest["model"]["events"]
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    assert event_schema == {
        "types": list(BASELINE_EVENT_TYPES),
        "fields": list(EVENT_FIELDS),
    }
    assert event_rows
    assert list(event_rows[0]) == list(EVENT_FIELDS)
    assert set(event["event_type"] for event in event_rows) <= set(BASELINE_EVENT_TYPES)
    assert set(event["event_type"] for event in event_rows) == set(BASELINE_EVENT_TYPES)


def test_summary_records_artifact_schema_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))
    summary = (out_dir / "summary.md").read_text()

    _assert_summary_records_artifact_schema_provenance(
        summary,
        metrics_header=metrics_header,
        events_header=events_header,
        actions=tuple(manifest["actions"]),
    )
    assert manifest["model"]["metrics"]["fields"] == metrics_header
    assert manifest["model"]["events"]["fields"] == events_header


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_summary_schema_provenance_counts_match_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    _assert_summary_schema_provenance_counts_match_manifest(summary, manifest)


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_schema_provenance_counts_match_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_schema_counts"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    _assert_summary_schema_provenance_counts_match_manifest(summary, manifest)


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_artifacts_and_output_flags_match_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_artifacts_outputs"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    assert _summary_written_artifacts(summary) == manifest["artifacts"]
    assert manifest["artifacts"] == _expected_artifacts(config_path)
    assert manifest["outputs"] == normalized_config["outputs"]
    _assert_summary_output_flags_match_config(summary, normalized_config["outputs"])


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_config_manifest_and_summary_run_fields_match_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_run_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    _assert_config_manifest_and_summary_run_fields_match(
        normalized_config,
        manifest=manifest,
        summary=summary,
        seed=1,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_agent_identity_and_roles_match_baseline_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_agent_identity_roles"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())

    _assert_manifest_agent_identity_and_roles_match_baseline(manifest)


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_bus_counts_match_summary_and_first_metrics_row_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_bus_counts"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        first_metrics_row = next(csv.DictReader(handle))

    _assert_manifest_bus_counts_match_summary_and_metrics_row(
        manifest,
        summary=summary,
        metrics_row=first_metrics_row,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_static_bus_metrics_match_first_metrics_row_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_static_bus_metrics"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        first_metrics_row = next(csv.DictReader(handle))

    _assert_summary_static_bus_metrics_match_metrics_row(
        summary,
        metrics_row=first_metrics_row,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_first_row_queue_pressure_fields_match_summary_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_first_row_queue_pressure"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_first_row_queue_pressure_fields_match_summary(
        summary,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_queued_task_age_summary_matches_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_queued_task_age"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_queued_task_age_summary_matches_metrics(
        summary,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_event_type_totals_match_events_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_event_type_totals"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_summary_event_type_totals_match_events(summary, event_rows=event_rows)


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_top_level_totals_match_metrics_and_events_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_top_level_totals"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_summary_top_level_totals_match_metrics_and_events(
        summary,
        metric_rows=metric_rows,
        event_rows=event_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_bus_graph_fields_match_metrics_and_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_bus_graph"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_bus_graph_fields_match_metrics_and_manifest(
        summary,
        metric_rows=metric_rows,
        manifest=manifest,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_role_action_totals_match_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_role_action_totals"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_role_action_totals_match_metrics(
        summary,
        metric_rows=metric_rows,
        actions=tuple(manifest["actions"]),
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_queue_dynamics_match_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_queue_dynamics"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_queue_dynamics_match_metrics(summary, metric_rows=metric_rows)


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_lobe_aggregates_match_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_lobe_aggregates"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_lobe_aggregates_match_metrics(summary, metric_rows=metric_rows)


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_lobe_dwell_runs_summary_matches_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_lobe_dwell_runs"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_lobe_dwell_run_summary_matches_metrics(summary, metric_rows=metric_rows)


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_lobe_run_state_matches_recomputed_dwell_runs_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_lobe_run_state"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_lobe_run_state_matches_recomputed_dwell_runs(metric_rows)


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_lobe_transitions_match_adjacent_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_lobe_transitions"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_lobe_transitions_match_adjacent_labels(metric_rows)


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_lobe_transition_totals_match_adjacent_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_lobe_transition_totals"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_lobe_transition_totals_match_adjacent_labels(
        summary,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_lobe_transition_endpoints_use_only_manifest_lobe_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_lobe_transition_manifest_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_lobe_transition_endpoints_use_only_manifest_lobe_labels(
        summary,
        manifest=manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_lobe_labels_cover_observed_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_lobe_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_manifest_lobe_labels_cover_observed_metrics(
        manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_lobe_labels_cover_previous_metrics_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_previous_lobe_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_manifest_lobe_labels_cover_previous_metrics_labels(
        manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_lobe_labels_cover_metrics_transition_endpoints_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_transition_lobe_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_manifest_lobe_labels_cover_metrics_transition_endpoints(
        manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_lobe_label_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_lobe_label_sequence_first"
    second = tmp_path / f"{config_path.stem}_cli_lobe_label_sequence_second"

    _run_documented_cli(config_path, first, seed=17)
    _run_documented_cli(config_path, second, seed=17)

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_label_sequence(first_metric_rows)
    second_sequence = _lobe_label_sequence(second_metric_rows)

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_lobe_label_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_lobe_label_sequence_seed1"
    second = tmp_path / f"{config_path.stem}_cli_lobe_label_sequence_seed2"

    _run_documented_cli(config_path, first, seed=1)
    _run_documented_cli(config_path, second, seed=2)

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_label_sequence(first_metric_rows)
    second_sequence = _lobe_label_sequence(second_metric_rows)

    assert first_sequence
    assert second_sequence
    assert first_sequence != second_sequence


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_lobe_transition_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_transition_sequence_first"
    second = tmp_path / f"{config_path.stem}_cli_transition_sequence_second"

    _run_documented_cli(config_path, first, seed=17)
    _run_documented_cli(config_path, second, seed=17)

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_transition_sequence(first_metric_rows)
    second_sequence = _lobe_transition_sequence(second_metric_rows)

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_lobe_transition_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_transition_sequence_seed1"
    second = tmp_path / f"{config_path.stem}_cli_transition_sequence_seed2"

    _run_documented_cli(config_path, first, seed=1)
    _run_documented_cli(config_path, second, seed=2)

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_transition_field_sequence(first_metric_rows)
    second_sequence = _lobe_transition_field_sequence(second_metric_rows)

    assert first_sequence
    assert second_sequence
    assert first_sequence != second_sequence


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_lobe_run_state_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_run_state_sequence_first"
    second = tmp_path / f"{config_path.stem}_cli_run_state_sequence_second"

    _run_documented_cli(config_path, first, seed=17)
    _run_documented_cli(config_path, second, seed=17)

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_run_state_sequence(first_metric_rows)
    second_sequence = _lobe_run_state_sequence(second_metric_rows)

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_lobe_run_state_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_run_state_sequence_seed1"
    second = tmp_path / f"{config_path.stem}_cli_run_state_sequence_seed2"

    _run_documented_cli(config_path, first, seed=1)
    _run_documented_cli(config_path, second, seed=2)

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_run_state_sequence(first_metric_rows)
    second_sequence = _lobe_run_state_sequence(second_metric_rows)

    assert first_sequence
    assert second_sequence
    assert first_sequence != second_sequence


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_lobe_dwell_run_summary_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_dwell_run_summary_seed1"
    second = tmp_path / f"{config_path.stem}_cli_dwell_run_summary_seed2"

    _run_documented_cli(config_path, first, seed=1)
    _run_documented_cli(config_path, second, seed=2)

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_dwell_runs = _summary_lobe_dwell_runs(first_summary)
    second_dwell_runs = _summary_lobe_dwell_runs(second_summary)

    assert first_dwell_runs == _lobe_dwell_runs(first_metric_rows)
    assert second_dwell_runs == _lobe_dwell_runs(second_metric_rows)
    assert first_dwell_runs
    assert second_dwell_runs
    assert first_dwell_runs != second_dwell_runs


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_role_action_summary_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_role_action_summary_first"
    second = tmp_path / f"{config_path.stem}_cli_role_action_summary_second"

    _run_documented_cli(config_path, first, seed=17)
    _run_documented_cli(config_path, second, seed=17)

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_role_action_totals = _summary_role_action_totals(first_summary)
    second_role_action_totals = _summary_role_action_totals(second_summary)
    actions = ("idle", "message", "create_task", "work_task")

    assert first_role_action_totals == _role_action_totals_from_metrics(
        first_metric_rows,
        actions,
    )
    assert second_role_action_totals == _role_action_totals_from_metrics(
        second_metric_rows,
        actions,
    )
    assert first_role_action_totals
    assert first_role_action_totals == second_role_action_totals


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_role_action_metric_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_role_action_sequence_first"
    second = tmp_path / f"{config_path.stem}_cli_role_action_sequence_second"

    _run_documented_cli(config_path, first, seed=17)
    _run_documented_cli(config_path, second, seed=17)

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _role_action_metric_sequence(
        first_metric_rows,
        ("idle", "message", "create_task", "work_task"),
    )
    second_sequence = _role_action_metric_sequence(
        second_metric_rows,
        ("idle", "message", "create_task", "work_task"),
    )

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_role_action_counts_sum_to_role_population_for_every_metrics_row_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_role_action_row_population"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    actions = tuple(manifest["actions"])
    role_populations = Counter(manifest["model"]["roles"].values())

    assert metric_rows
    assert role_populations == {role: 3 for role in BASELINE_ROLES}
    for row in metric_rows:
        for role, population in role_populations.items():
            assert (
                sum(int(row[f"role_{role}_{action}_tick"]) for action in actions)
                == population
            )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_role_action_counts_sum_to_top_level_action_totals_for_every_metrics_row_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_role_action_row_action_totals"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    actions = tuple(manifest["actions"])
    top_level_action_fields = {
        "idle": "idle_tick",
        "message": "messages_sent_tick",
        "create_task": "tasks_created_tick",
        "work_task": "tasks_worked_tick",
    }

    assert metric_rows
    assert set(actions) == set(top_level_action_fields)
    for row in metric_rows:
        for action in actions:
            assert sum(
                int(row[f"role_{role}_{action}_tick"])
                for role in BASELINE_ROLES
            ) == int(row[top_level_action_fields[action]])


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_events_per_tick_action_counts_match_metrics_top_level_action_totals_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_metrics_row_action_totals"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_per_tick_action_counts_match_metrics_top_level_action_totals(
        metric_rows=metric_rows,
        event_rows=event_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_events_per_tick_counts_match_configured_agent_population_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_tick_population"

    _run_documented_cli(config_path, out_dir)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_per_tick_counts_match_configured_agent_population(
        event_rows=event_rows,
        ticks=normalized_config["run"]["ticks"],
        agent_count=normalized_config["model"]["agent_count"],
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_events_per_tick_agent_ids_match_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_tick_manifest_agents"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_per_tick_agent_ids_match_manifest(
        event_rows=event_rows,
        ticks=manifest["ticks"],
        manifest_agent_ids=manifest["model"]["agent_ids"],
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_events_replay_to_role_action_metrics_through_manifest_roles_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_role_action_metrics"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_replay_to_role_action_metrics_through_manifest_roles(
        metric_rows=metric_rows,
        event_rows=event_rows,
        manifest_roles=manifest["model"]["roles"],
        actions=tuple(manifest["actions"]),
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_events_per_tick_task_lifecycle_matches_queue_and_task_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_task_lifecycle_metrics"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_per_tick_task_lifecycle_matches_queue_and_task_metrics(
        metric_rows=metric_rows,
        event_rows=event_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_event_replay_reproduces_queued_task_age_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_event_replay_queue_age"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_event_replay_reproduces_queued_task_age_metrics(
        metric_rows=metric_rows,
        event_rows=event_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_role_action_summary_totals_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_role_action_summary_seed1"
    second = tmp_path / f"{config_path.stem}_cli_role_action_summary_seed2"

    _run_documented_cli(config_path, first, seed=1)
    _run_documented_cli(config_path, second, seed=2)

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_role_action_totals = _summary_role_action_totals(first_summary)
    second_role_action_totals = _summary_role_action_totals(second_summary)
    actions = ("idle", "message", "create_task", "work_task")

    assert first_role_action_totals == _role_action_totals_from_metrics(
        first_metric_rows,
        actions,
    )
    assert second_role_action_totals == _role_action_totals_from_metrics(
        second_metric_rows,
        actions,
    )
    assert first_role_action_totals
    assert second_role_action_totals
    assert first_role_action_totals != second_role_action_totals


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_role_action_metric_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_role_action_sequence_seed1"
    second = tmp_path / f"{config_path.stem}_cli_role_action_sequence_seed2"

    _run_documented_cli(config_path, first, seed=1)
    _run_documented_cli(config_path, second, seed=2)

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
        first_header = list(first_metric_rows[0])
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
        second_header = list(second_metric_rows[0])

    actions = ("idle", "message", "create_task", "work_task")
    expected_fields = list(role_action_metric_fields(actions))
    first_sequence = _role_action_metric_sequence(first_metric_rows, actions)
    second_sequence = _role_action_metric_sequence(second_metric_rows, actions)

    assert first_manifest["model"]["role_action_metrics"]["fields"] == expected_fields
    assert second_manifest["model"]["role_action_metrics"]["fields"] == expected_fields
    assert [field for field in first_header if field.startswith("role_")] == expected_fields
    assert [field for field in second_header if field.startswith("role_")] == expected_fields
    assert first_sequence
    assert second_sequence
    assert first_sequence != second_sequence


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_lobe_totals_use_only_manifest_lobe_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_lobe_manifest_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_lobe_totals_use_only_manifest_lobe_labels(
        summary,
        manifest=manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_summary_lobe_dwell_runs_use_only_manifest_lobe_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_lobe_dwell_manifest_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_lobe_dwell_runs_use_only_manifest_lobe_labels(
        summary,
        manifest=manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_lobe_fields_match_metrics_header_and_observed_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_lobe_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    _assert_manifest_lobe_fields_match_metrics_header_and_observed_labels(
        manifest,
        metrics_header=metrics_header,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_event_types_cover_observed_events_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_event_types"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_manifest_event_types_cover_observed_events(
        manifest,
        event_rows=event_rows,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_metrics_fields_exactly_match_metrics_header_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_metrics_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    _assert_manifest_metrics_fields_match_metrics_header(
        manifest,
        metrics_header=metrics_header,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_role_action_fields_exactly_match_metrics_header_subset_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_role_action_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    _assert_manifest_role_action_fields_match_metrics_header_subset(
        manifest,
        metrics_header=metrics_header,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_queue_dynamics_fields_exactly_match_metrics_header_subsets_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_queue_dynamics_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    _assert_manifest_queue_dynamics_fields_match_metrics_header_subsets(
        manifest,
        metrics_header=metrics_header,
    )


@pytest.mark.parametrize("config_path", [CONFIG, DEFAULT_OUTPUTS])
def test_documented_cli_manifest_event_fields_exactly_match_events_header_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_event_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))

    _assert_manifest_event_fields_match_events_header(
        manifest,
        events_header=events_header,
    )


def test_summary_records_written_artifacts_and_output_flags(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()
    assert "## Run artifacts and outputs" in summary
    assert "- written artifacts: config.yaml, manifest.yaml, metrics.csv, events.csv, summary.md" in summary
    assert "- write_manifest: enabled" in summary
    assert "- write_metrics: enabled" in summary
    assert "- write_events: enabled" in summary
    assert "- write_summary: enabled" in summary


def test_summary_written_artifacts_match_manifest_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    summary_artifacts = _summary_written_artifacts(summary)

    assert summary_artifacts == manifest["artifacts"]


def test_summary_written_artifacts_match_output_directory_contents(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    _assert_summary_written_artifacts_match_output_directory(out_dir)


def test_summary_written_artifacts_match_output_directory_contents_without_manifest(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest"

    run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)

    summary_artifacts = _assert_summary_written_artifacts_match_output_directory(out_dir)

    assert "manifest.yaml" not in summary_artifacts


@pytest.mark.parametrize(
    ("config_path", "expected_artifacts"),
    [
        (DEFAULT_OUTPUTS, _expected_artifacts(DEFAULT_OUTPUTS)),
        (CONFIG_ONLY, _expected_artifacts(CONFIG_ONLY)),
        (MANIFEST_ONLY, _expected_artifacts(MANIFEST_ONLY)),
        (NO_MANIFEST, _expected_artifacts(NO_MANIFEST)),
    ],
)
def test_artifact_indexes_match_directory_contents_across_output_flag_fixtures(
    tmp_path: Path,
    config_path: Path,
    expected_artifacts: list[str],
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    _assert_artifact_indexes_match_directory_contents(out_dir, expected_artifacts)


def test_summary_records_disabled_manifest_output_flag(tmp_path: Path) -> None:
    out_dir = tmp_path / "no_manifest"

    run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()
    assert "- written artifacts: config.yaml, metrics.csv, events.csv, summary.md" in summary
    assert "- write_manifest: disabled" in summary
    assert "- write_metrics: enabled" in summary
    assert "- write_events: enabled" in summary
    assert "- write_summary: enabled" in summary
    assert not (out_dir / "manifest.yaml").exists()


def test_manifest_lists_only_written_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "manifest_only"

    run_experiment(MANIFEST_ONLY, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_manifest_artifacts_match_output_directory_contents_when_manifest_only(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only"

    run_experiment(MANIFEST_ONLY, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())

    _assert_artifacts_match_output_directory(out_dir, manifest["artifacts"])
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)


def test_manifest_only_records_full_schema_provenance_without_disabled_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_schema"

    run_experiment(MANIFEST_ONLY, seed=1, out_dir=out_dir)

    _assert_manifest_only_preserves_full_schema_provenance(out_dir)


def test_documented_cli_manifest_only_artifacts_match_output_directory_contents(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_cli"

    _run_documented_cli(MANIFEST_ONLY, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())

    _assert_artifacts_match_output_directory(out_dir, manifest["artifacts"])
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_documented_cli_manifest_only_records_full_schema_provenance_without_disabled_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_cli_schema"

    _run_documented_cli(MANIFEST_ONLY, out_dir)

    _assert_manifest_only_preserves_full_schema_provenance(out_dir)


def test_documented_cli_manifest_only_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_cli_stale_disabled"
    stale_disabled_artifacts = _write_manifest_only_disabled_artifact_sentinels(out_dir)

    _run_documented_cli(MANIFEST_ONLY, out_dir)
    _assert_manifest_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)
    assert manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["seed"] == 1
    assert manifest["experiment_id"] == "a0_manifest_only"


@pytest.mark.parametrize("collision_artifact", ["config.yaml", "manifest.yaml"])
def test_documented_cli_manifest_only_refuses_enabled_artifact_collisions_while_preserving_stale_disabled_artifacts(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    out_dir = tmp_path / f"manifest_only_cli_collision_{collision_artifact.replace('.', '_')}"
    stale_disabled_artifacts, collision_content = _write_manifest_only_collision_sentinels(
        out_dir,
        collision_artifact,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(MANIFEST_ONLY),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "already contains run artifacts" in completed.stderr
    assert collision_artifact in completed.stderr
    assert "metrics.csv" not in completed.stderr
    assert "events.csv" not in completed.stderr
    assert "summary.md" not in completed.stderr
    assert "Traceback" not in completed.stderr
    _assert_manifest_only_collision_preserves_stale_disabled_artifacts(
        out_dir,
        collision_artifact,
        stale_disabled_artifacts=stale_disabled_artifacts,
        collision_content=collision_content,
    )


def test_documented_cli_config_only_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_cli_stale_disabled"
    stale_disabled_artifacts = _write_config_only_disabled_artifact_sentinels(out_dir)

    _run_documented_cli(CONFIG_ONLY, out_dir)
    _assert_config_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )
    _assert_config_only_writes_normalized_config(out_dir)


def test_run_api_config_only_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_api_stale_disabled"
    stale_disabled_artifacts = _write_config_only_disabled_artifact_sentinels(out_dir)

    result = run_experiment(CONFIG_ONLY, seed=1, out_dir=out_dir)

    assert result.config.run.experiment_id == "a0_config_only"
    assert result.seed == 1
    assert len(result.metrics) == 3
    assert len(result.events) == 45
    _assert_config_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )
    _assert_config_only_writes_normalized_config(out_dir)


def test_run_api_manifest_only_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_api_stale_disabled"
    stale_disabled_artifacts = _write_manifest_only_disabled_artifact_sentinels(out_dir)

    result = run_experiment(MANIFEST_ONLY, seed=1, out_dir=out_dir)

    assert result.config.run.experiment_id == "a0_manifest_only"
    assert result.seed == 1
    assert len(result.metrics) == 3
    assert len(result.events) == 45
    _assert_manifest_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)
    assert manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["seed"] == 1
    assert manifest["experiment_id"] == "a0_manifest_only"


@pytest.mark.parametrize("collision_artifact", ["config.yaml", "manifest.yaml"])
def test_run_api_manifest_only_refuses_enabled_artifact_collisions_while_preserving_stale_disabled_artifacts(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    out_dir = tmp_path / f"manifest_only_api_collision_{collision_artifact.replace('.', '_')}"
    stale_disabled_artifacts, collision_content = _write_manifest_only_collision_sentinels(
        out_dir,
        collision_artifact,
    )

    with pytest.raises(FileExistsError, match="already contains run artifacts") as exc_info:
        run_experiment(MANIFEST_ONLY, seed=1, out_dir=out_dir)

    message = str(exc_info.value)
    assert str(out_dir) in message
    assert collision_artifact in message
    assert "metrics.csv" not in message
    assert "events.csv" not in message
    assert "summary.md" not in message
    _assert_manifest_only_collision_preserves_stale_disabled_artifacts(
        out_dir,
        collision_artifact,
        stale_disabled_artifacts=stale_disabled_artifacts,
        collision_content=collision_content,
    )


def test_documented_cli_no_manifest_summary_artifacts_match_output_directory_contents(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_cli"

    _run_documented_cli(NO_MANIFEST, out_dir)

    _assert_summary_written_artifacts_match_output_directory(out_dir)
    _assert_no_manifest_writes_enabled_artifacts(out_dir)


def test_documented_cli_no_manifest_emitted_artifacts_preserve_schema_provenance(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_cli_schema"

    _run_documented_cli(NO_MANIFEST, out_dir)

    _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)


def test_documented_cli_no_manifest_preserves_stale_manifest_sentinel(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_cli_stale_manifest"
    stale_manifest = _write_no_manifest_disabled_manifest_sentinel(out_dir)

    _run_documented_cli(NO_MANIFEST, out_dir)
    _assert_no_manifest_preserves_stale_disabled_manifest(
        out_dir,
        stale_manifest=stale_manifest,
    )


@pytest.mark.parametrize("collision_artifact", ["config.yaml", "metrics.csv", "events.csv", "summary.md"])
def test_documented_cli_no_manifest_refuses_enabled_artifact_collisions_while_preserving_stale_manifest(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    out_dir = tmp_path / f"no_manifest_cli_collision_{collision_artifact.replace('.', '_')}"
    stale_manifest, collision_content = _write_no_manifest_collision_sentinels(
        out_dir,
        collision_artifact,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(NO_MANIFEST),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "already contains run artifacts" in completed.stderr
    assert collision_artifact in completed.stderr
    assert "manifest.yaml" not in completed.stderr
    assert "Traceback" not in completed.stderr
    _assert_no_manifest_collision_preserves_stale_manifest(
        out_dir,
        collision_artifact,
        stale_manifest=stale_manifest,
        collision_content=collision_content,
    )


def test_run_api_no_manifest_preserves_stale_disabled_manifest_sentinel(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_api_stale_manifest"
    stale_manifest = _write_no_manifest_disabled_manifest_sentinel(out_dir)

    result = run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)

    assert result.config.run.experiment_id == "a0_no_manifest"
    assert result.seed == 1
    assert result.config.outputs.write_manifest is False
    assert len(result.metrics) == 3
    assert len(result.events) == 45
    _assert_no_manifest_preserves_stale_disabled_manifest(
        out_dir,
        stale_manifest=stale_manifest,
    )

    with (out_dir / "metrics.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 3
    with (out_dir / "events.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 45


def test_run_api_no_manifest_emitted_artifacts_preserve_schema_provenance(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_api_schema"

    result = run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)

    assert result.config.run.experiment_id == "a0_no_manifest"
    assert result.seed == 1
    assert result.config.outputs.write_manifest is False

    _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)


@pytest.mark.parametrize("collision_artifact", ["config.yaml", "metrics.csv", "events.csv", "summary.md"])
def test_run_api_no_manifest_refuses_enabled_artifact_collisions_while_ignoring_stale_manifest(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    out_dir = tmp_path / f"no_manifest_api_collision_{collision_artifact.replace('.', '_')}"
    stale_manifest, collision_content = _write_no_manifest_collision_sentinels(
        out_dir,
        collision_artifact,
    )

    with pytest.raises(FileExistsError, match=collision_artifact):
        run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)

    _assert_no_manifest_collision_preserves_stale_manifest(
        out_dir,
        collision_artifact,
        stale_manifest=stale_manifest,
        collision_content=collision_content,
    )


def test_output_flags_must_be_yaml_booleans(tmp_path: Path) -> None:
    config_path = tmp_path / "string_bool.yaml"
    config_path.write_text(
        """
run:
  experiment_id: string_bool
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_metrics: "false"
"""
    )

    with pytest.raises(ValueError, match="outputs.write_metrics"):
        load_config(config_path)


@pytest.mark.parametrize(
    ("config_text", "message"),
    [
        (
            """
model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task
""",
            "section 'run'",
        ),
        (
            """
run:
  experiment_id: missing_model
  ticks: 3
""",
            "section 'model'",
        ),
        (
            """
run:
  experiment_id: list_outputs
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  - write_metrics
""",
            "section 'outputs'",
        ),
    ],
)
def test_required_config_sections_must_be_yaml_mappings(
    tmp_path: Path,
    config_text: str,
    message: str,
) -> None:
    config_path = tmp_path / "invalid_section.yaml"
    config_path.write_text(config_text)

    with pytest.raises(ValueError, match=message):
        load_config(config_path)


@pytest.mark.parametrize(
    ("actions_yaml", "message"),
    [
        (
            """
    - idle
    - message
    - create_task
""",
            "missing required baseline actions: work_task",
        ),
        (
            """
    - idle
    - message
    - create_task
    - work_task
    - browse_web
""",
            "unsupported baseline actions: browse_web",
        ),
        (
            """
    - idle
    - message
    - create_task
    - work_task
    - work_task
""",
            "must not contain duplicates",
        ),
    ],
)
def test_baseline_actions_must_be_required_unique_and_supported(
    tmp_path: Path,
    actions_yaml: str,
    message: str,
) -> None:
    config_path = tmp_path / "invalid_actions.yaml"
    config_path.write_text(
        f"""
run:
  experiment_id: invalid_actions
  ticks: 3

model:
  agent_count: 15
  actions:{actions_yaml}
"""
    )

    with pytest.raises(ValueError, match=message):
        load_config(config_path)


def test_documented_cli_smoke_writes_required_a0_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"
    expected_artifacts = _expected_artifacts(CONFIG)

    _run_documented_cli(CONFIG, out_dir)
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == expected_artifacts
    assert manifest["seed"] == 1
    assert manifest["experiment_id"] == "a0_smoke"


def test_documented_cli_omitted_outputs_defaults_to_full_a0_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "default_outputs_seed1"
    expected_artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    _run_documented_cli(DEFAULT_OUTPUTS, out_dir)
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert normalized_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert manifest["outputs"] == normalized_config["outputs"]
    assert manifest["artifacts"] == expected_artifacts
    assert manifest["experiment_id"] == "a0_default_outputs"


def test_documented_cli_omitted_outputs_same_seed_reproduces_byte_identical_artifacts(
    tmp_path: Path,
) -> None:
    first = tmp_path / "default_outputs_seed17_first"
    second = tmp_path / "default_outputs_seed17_second"
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    for out_dir in [first, second]:
        _run_documented_cli(DEFAULT_OUTPUTS, out_dir, seed=17)
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    assert first_manifest["experiment_id"] == "a0_default_outputs"
    assert second_manifest["experiment_id"] == "a0_default_outputs"
    assert first_manifest["outputs"] == second_manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_documented_cli_omitted_outputs_refuses_collision_without_partial_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "default_outputs_collision"
    out_dir.mkdir()
    sentinels = {
        "config.yaml": "sentinel config\n",
        "events.csv": "sentinel events\n",
    }
    for artifact, content in sentinels.items():
        (out_dir / artifact).write_text(content)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(DEFAULT_OUTPUTS),
            "--seed",
            "17",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "already contains run artifacts" in completed.stderr
    assert "config.yaml" in completed.stderr
    assert "events.csv" in completed.stderr
    assert "Traceback" not in completed.stderr
    _assert_artifacts_match_output_directory(out_dir, list(sentinels))
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_run_api_omitted_outputs_defaults_to_full_a0_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "default_outputs_api_seed1"
    expected_artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    result = run_experiment(DEFAULT_OUTPUTS, seed=1, out_dir=out_dir)

    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)
    assert result.config.outputs.write_manifest is True
    assert result.config.outputs.write_metrics is True
    assert result.config.outputs.write_events is True
    assert result.config.outputs.write_summary is True
    assert len(result.metrics) == 3
    assert len(result.events) == 45

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert normalized_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert manifest["outputs"] == normalized_config["outputs"]
    assert manifest["artifacts"] == expected_artifacts
    assert manifest["experiment_id"] == "a0_default_outputs"
    with (out_dir / "metrics.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 3
    with (out_dir / "events.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 45
    assert "# a0_default_outputs" in (out_dir / "summary.md").read_text()


def test_run_api_omitted_outputs_same_seed_reproduces_byte_identical_artifacts(
    tmp_path: Path,
) -> None:
    first = tmp_path / "default_outputs_api_seed17_first"
    second = tmp_path / "default_outputs_api_seed17_second"
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    first_result = run_experiment(DEFAULT_OUTPUTS, seed=17, out_dir=first)
    second_result = run_experiment(DEFAULT_OUTPUTS, seed=17, out_dir=second)

    _assert_artifacts_match_output_directory(first, artifacts)
    _assert_artifacts_match_output_directory(second, artifacts)
    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == second_result.seed == 17
    assert first_result.metrics == second_result.metrics
    assert first_result.events == second_result.events
    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_run_api_omitted_outputs_refuses_collision_without_partial_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "default_outputs_api_collision"
    out_dir.mkdir()
    sentinels = {
        "config.yaml": "sentinel config\n",
        "events.csv": "sentinel events\n",
    }
    for artifact, content in sentinels.items():
        (out_dir / artifact).write_text(content)

    with pytest.raises(FileExistsError, match="already contains run artifacts") as exc_info:
        run_experiment(DEFAULT_OUTPUTS, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert str(out_dir) in message
    assert "config.yaml" in message
    assert "events.csv" in message
    _assert_artifacts_match_output_directory(out_dir, list(sentinels))
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_documented_cli_smoke_writes_expected_metrics_and_events_rows(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    _run_documented_cli(CONFIG, out_dir)

    config = load_config(CONFIG)
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    assert len(metric_rows) == config.run.ticks
    assert len(event_rows) == config.run.ticks * config.model.agent_count
    assert [int(row["tick"]) for row in metric_rows] == list(range(config.run.ticks))

    events_by_tick = Counter(int(row["tick"]) for row in event_rows)
    assert events_by_tick == {
        tick: config.model.agent_count
        for tick in range(config.run.ticks)
    }


def test_documented_cli_smoke_writes_core_a0_summary_sections(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    _run_documented_cli(CONFIG, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    for heading in [
        "## Artifact schema provenance",
        "## Event type totals",
        "## Baseline lobe totals",
        "## Baseline lobe transitions",
        "## Baseline lobe dwell runs",
        "## Role action totals",
    ]:
        assert heading in summary

    event_type_totals = Counter(row["event_type"] for row in event_rows)
    lobe_totals = Counter(row["baseline_lobe_label"] for row in metric_rows)
    lobe_transitions = Counter(
        row["baseline_lobe_transition"]
        for row in metric_rows
        if row["baseline_lobe_transition"] not in {"start", "stable"}
    )
    role_action_totals = {
        role: {
            action: sum(int(row[f"role_{role}_{action}_tick"]) for row in metric_rows)
            for action in ("idle", "message", "create_task", "work_task")
        }
        for role in BASELINE_ROLES
    }

    assert event_type_totals
    assert lobe_totals
    assert lobe_transitions
    for event_type, count in sorted(event_type_totals.items()):
        assert f"- {event_type}: {count}" in summary
    for label, count in sorted(lobe_totals.items()):
        assert f"- {label}: {count}" in summary
    for transition, count in sorted(lobe_transitions.items()):
        assert f"- {transition}: {count}" in summary
    for label, dwell in _lobe_dwell_runs(metric_rows).items():
        assert (
            f"- {label}: runs={dwell['runs']}, total_ticks={dwell['total_ticks']}, "
            f"max_run={dwell['max_run']}, mean_run={dwell['mean_run']}"
        ) in summary
    for role, totals in role_action_totals.items():
        assert (
            f"- {role}: idle={totals['idle']}, message={totals['message']}, "
            f"create_task={totals['create_task']}, work_task={totals['work_task']}"
        ) in summary


def test_documented_cli_same_seed_reproduces_byte_identical_a0_artifacts(tmp_path: Path) -> None:
    first = tmp_path / "a0_seed17_first"
    second = tmp_path / "a0_seed17_second"
    artifacts = _expected_artifacts(CONFIG)

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG, out_dir, seed=17)
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_documented_cli_refuses_to_overwrite_complete_run_directory(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed17"
    artifacts = _expected_artifacts(CONFIG)
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(CONFIG),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = _artifact_bytes_snapshot(out_dir, artifacts)

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert "already contains run artifacts" in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(out_dir, artifacts)
    _assert_output_directory_preserved(out_dir, before)


def test_documented_cli_respects_disabled_optional_outputs(tmp_path: Path) -> None:
    out_dir = tmp_path / "manifest_only_cli_outputs"
    expected_artifacts = _expected_artifacts(MANIFEST_ONLY)

    _run_documented_cli(MANIFEST_ONLY, out_dir, seed=17)
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == expected_artifacts
    assert manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["seed"] == 17
    assert manifest["experiment_id"] == "a0_manifest_only"
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_documented_cli_respects_disabled_manifest_output(tmp_path: Path) -> None:
    out_dir = tmp_path / "no_manifest_cli_outputs"

    _run_documented_cli(NO_MANIFEST, out_dir, seed=17)
    _assert_no_manifest_writes_enabled_artifacts(out_dir)
    assert "# a0_no_manifest" in (out_dir / "summary.md").read_text()


def test_run_api_respects_no_manifest_fixture_outputs(tmp_path: Path) -> None:
    out_dir = tmp_path / "no_manifest_api_outputs"
    out_dir.mkdir()
    stale_manifest = "stale manifest sentinel\n"
    (out_dir / "manifest.yaml").write_text(stale_manifest)
    expected_artifacts = [*_expected_artifacts(NO_MANIFEST), "manifest.yaml"]

    result = run_experiment(NO_MANIFEST, seed=17, out_dir=out_dir)

    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)
    assert (out_dir / "manifest.yaml").read_text() == stale_manifest
    assert result.config.outputs.write_manifest is False
    assert len(result.metrics) == 3
    assert len(result.events) == 45
    _assert_no_manifest_writes_enabled_artifacts(
        out_dir,
        stale_manifest=stale_manifest.encode(),
    )
    assert "# a0_no_manifest" in (out_dir / "summary.md").read_text()


def test_run_api_without_manifest_refuses_enabled_artifact_collisions(tmp_path: Path) -> None:
    out_dir = tmp_path / "no_manifest_api_collision"
    out_dir.mkdir()
    sentinels = {
        "manifest.yaml": "ignored stale manifest\n",
        "metrics.csv": "sentinel metrics\n",
        "summary.md": "sentinel summary\n",
    }
    for artifact, content in sentinels.items():
        (out_dir / artifact).write_text(content)

    with pytest.raises(FileExistsError, match="already contains run artifacts") as exc_info:
        run_experiment(NO_MANIFEST, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert str(out_dir) in message
    assert "metrics.csv" in message
    assert "summary.md" in message
    assert "manifest.yaml" not in message
    _assert_artifacts_match_output_directory(out_dir, list(sentinels))
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "config.yaml").exists()
    assert not (out_dir / "events.csv").exists()


def test_documented_cli_same_seed_without_manifest_reproduces_byte_identical_artifacts(
    tmp_path: Path,
) -> None:
    first = tmp_path / "no_manifest_repro_first"
    second = tmp_path / "no_manifest_repro_second"
    artifacts = [
        "config.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    for out_dir in [first, second]:
        _run_documented_cli(NO_MANIFEST, out_dir, seed=17)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_documented_cli_without_manifest_refuses_partial_output_directory(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_partial_collision"
    out_dir.mkdir()
    sentinels = {
        "config.yaml": "sentinel config\n",
        "events.csv": "sentinel events\n",
    }
    for artifact, content in sentinels.items():
        (out_dir / artifact).write_text(content)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(NO_MANIFEST),
            "--seed",
            "17",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "already contains run artifacts" in completed.stderr
    assert "config.yaml" in completed.stderr
    assert "events.csv" in completed.stderr
    assert "manifest.yaml" not in completed.stderr
    assert "Traceback" not in completed.stderr
    _assert_artifacts_match_output_directory(out_dir, list(sentinels))
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "summary.md").exists()
    assert not (out_dir / "manifest.yaml").exists()


def test_documented_cli_different_seeds_change_events_but_preserve_schema(tmp_path: Path) -> None:
    first = tmp_path / "a0_seed17"
    second = tmp_path / "a0_seed18"

    for seed, out_dir in [(17, first), (18, second)]:
        _run_documented_cli(CONFIG, out_dir, seed=seed)

    with (first / "metrics.csv").open() as handle:
        first_metrics = list(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics = list(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events = list(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events = list(csv.reader(handle))

    assert first_metrics[0] == second_metrics[0]
    assert first_events[0] == second_events[0]
    assert len(first_metrics) == len(second_metrics) == 101
    assert len(first_events) == len(second_events) == 1501
    assert first_events[1:] != second_events[1:]

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    assert first_manifest["seed"] == 17
    assert second_manifest["seed"] == 18
    assert first_manifest["actions"] == second_manifest["actions"]
    assert first_manifest["model"] == second_manifest["model"]


def test_cli_validation_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid_actions.yaml"
    out_dir = tmp_path / "invalid_run"
    config_path.write_text(
        """
run:
  experiment_id: invalid_actions
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task
    - browse_web
"""
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error: model.actions contains unsupported baseline actions: browse_web" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert not out_dir.exists()


def test_cli_invalid_seed_error_does_not_write_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "invalid_seed_run"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(CONFIG),
            "--seed",
            "-1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error: seed must be a non-negative integer." in completed.stderr
    assert "Traceback" not in completed.stderr
    assert not out_dir.exists()


@pytest.mark.parametrize("seed", [-1, True, "1"])
def test_run_experiment_invalid_seed_error_does_not_write_artifacts(
    tmp_path: Path,
    seed: object,
) -> None:
    out_dir = tmp_path / "invalid_seed_run"

    with pytest.raises(ValueError, match="seed must be a non-negative integer"):
        run_experiment(tmp_path / "missing_config.yaml", seed=seed, out_dir=out_dir)  # type: ignore[arg-type]

    assert not out_dir.exists()


def test_run_experiment_missing_config_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "missing.yaml"
    out_dir = tmp_path / "missing_config_run"

    with pytest.raises(FileNotFoundError, match="missing.yaml"):
        run_experiment(config_path, seed=1, out_dir=out_dir)

    assert not out_dir.exists()


def test_run_experiment_malformed_yaml_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "malformed.yaml"
    out_dir = tmp_path / "malformed_run"
    config_path.write_text(
        """
run:
  experiment_id: malformed
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task
    - [unterminated
"""
    )

    with pytest.raises(ValueError, match="invalid YAML"):
        run_experiment(config_path, seed=1, out_dir=out_dir)

    assert not out_dir.exists()


def test_run_experiment_invalid_config_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid_actions.yaml"
    out_dir = tmp_path / "invalid_run"
    config_path.write_text(
        """
run:
  experiment_id: invalid_actions
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task
    - browse_web
"""
    )

    with pytest.raises(ValueError, match="unsupported baseline actions: browse_web"):
        run_experiment(config_path, seed=1, out_dir=out_dir)

    assert not out_dir.exists()


def test_run_experiment_refuses_to_overwrite_complete_run_directory(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed17"
    artifacts = [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    run_experiment(CONFIG, seed=17, out_dir=out_dir)
    before = _artifact_bytes_snapshot(out_dir, artifacts)

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        run_experiment(CONFIG, seed=17, out_dir=out_dir)

    _assert_artifacts_match_output_directory(out_dir, artifacts)
    _assert_output_directory_preserved(out_dir, before)


def test_run_experiment_refuses_partial_output_directory_without_writing_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "partial_collision"
    out_dir.mkdir()
    sentinels = {
        "config.yaml": "sentinel config\n",
        "events.csv": "sentinel events\n",
    }
    for artifact, content in sentinels.items():
        (out_dir / artifact).write_text(content)

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        run_experiment(CONFIG, seed=17, out_dir=out_dir)

    _assert_artifacts_match_output_directory(out_dir, list(sentinels))
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_run_experiment_output_path_file_does_not_overwrite(tmp_path: Path) -> None:
    out_path = tmp_path / "file_output"
    out_path.write_text("sentinel output path\n")

    with pytest.raises(FileExistsError, match="exists and is not a directory"):
        run_experiment(CONFIG, seed=17, out_dir=out_path)

    assert out_path.read_text() == "sentinel output path\n"


def test_run_experiment_output_artifact_collision_does_not_write_partial_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "collision_run"
    out_dir.mkdir()
    existing_metrics = out_dir / "metrics.csv"
    existing_metrics.write_text("sentinel metrics\n")

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        run_experiment(CONFIG, seed=1, out_dir=out_dir)

    assert existing_metrics.read_text() == "sentinel metrics\n"
    _assert_artifacts_match_output_directory(out_dir, ["metrics.csv"])
    assert not (out_dir / "config.yaml").exists()
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_run_experiment_ignores_disabled_output_collisions_but_blocks_enabled_artifacts(
    tmp_path: Path,
) -> None:
    success_dir = tmp_path / "disabled_optional_collisions_success"
    blocked_dir = tmp_path / "disabled_optional_collisions_blocked"
    disabled_sentinels = {
        "metrics.csv": "sentinel disabled metrics\n",
        "events.csv": "sentinel disabled events\n",
        "summary.md": "sentinel disabled summary\n",
    }
    success_dir.mkdir()
    for artifact, content in disabled_sentinels.items():
        (success_dir / artifact).write_text(content)

    run_experiment(MANIFEST_ONLY, seed=17, out_dir=success_dir)

    assert (success_dir / "config.yaml").is_file()
    assert (success_dir / "manifest.yaml").is_file()
    for artifact, content in disabled_sentinels.items():
        assert (success_dir / artifact).read_text() == content
    manifest = yaml.safe_load((success_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)

    blocked_dir.mkdir()
    for artifact, content in disabled_sentinels.items():
        (blocked_dir / artifact).write_text(content)
    (blocked_dir / "manifest.yaml").write_text("sentinel enabled manifest\n")

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        run_experiment(MANIFEST_ONLY, seed=17, out_dir=blocked_dir)

    assert (blocked_dir / "manifest.yaml").read_text() == "sentinel enabled manifest\n"
    _assert_artifacts_match_output_directory(blocked_dir, [*disabled_sentinels, "manifest.yaml"])
    assert not (blocked_dir / "config.yaml").exists()
    for artifact, content in disabled_sentinels.items():
        assert (blocked_dir / artifact).read_text() == content


def test_run_experiment_config_artifact_collision_blocks_when_all_optional_outputs_disabled(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_collision"
    stale_disabled_artifacts, collision_content = _write_config_only_collision_sentinels(out_dir)

    with pytest.raises(FileExistsError, match="already contains run artifacts: config.yaml"):
        run_experiment(CONFIG_ONLY, seed=17, out_dir=out_dir)

    _assert_config_only_collision_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
        collision_content=collision_content,
    )


def test_run_experiment_config_only_outputs_succeed_and_are_byte_stable(
    tmp_path: Path,
) -> None:
    first = tmp_path / "config_only_first"
    second = tmp_path / "config_only_second"

    first_result = run_experiment(CONFIG_ONLY, seed=17, out_dir=first)
    second_result = run_experiment(CONFIG_ONLY, seed=17, out_dir=second)

    artifacts = _expected_artifacts(CONFIG_ONLY)
    _assert_artifacts_match_output_directory(first, artifacts)
    _assert_artifacts_match_output_directory(second, artifacts)
    _assert_artifacts_are_byte_identical(first, second, artifacts)
    normalized_config = yaml.safe_load((first / "config.yaml").read_text())
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"
    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == second_result.seed == 17
    assert len(first_result.metrics) == len(second_result.metrics) == 3
    assert len(first_result.events) == len(second_result.events) == 45


def test_run_experiment_config_only_rerun_refuses_to_overwrite_existing_config(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_rerun"

    run_experiment(CONFIG_ONLY, seed=17, out_dir=out_dir)
    before = _artifact_bytes_snapshot(out_dir, _expected_artifacts(CONFIG_ONLY))

    with pytest.raises(FileExistsError, match="already contains run artifacts: config.yaml"):
        run_experiment(CONFIG_ONLY, seed=17, out_dir=out_dir)

    _assert_artifacts_match_output_directory(out_dir, _expected_artifacts(CONFIG_ONLY))
    _assert_output_directory_preserved(out_dir, before)
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_run_experiment_config_only_rerun_preserves_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_rerun_with_disabled_sentinels"
    disabled_sentinels = {
        "manifest.yaml": b"sentinel disabled manifest\n",
        "metrics.csv": b"sentinel disabled metrics\n",
        "events.csv": b"sentinel disabled events\n",
        "summary.md": b"sentinel disabled summary\n",
    }

    run_experiment(CONFIG_ONLY, seed=17, out_dir=out_dir)
    for artifact, content in disabled_sentinels.items():
        (out_dir / artifact).write_bytes(content)
    before = _artifact_bytes_snapshot(out_dir)

    with pytest.raises(FileExistsError) as exc_info:
        run_experiment(CONFIG_ONLY, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert "already contains run artifacts: config.yaml" in message
    assert "manifest.yaml" not in message
    assert "metrics.csv" not in message
    assert "events.csv" not in message
    assert "summary.md" not in message
    _assert_artifacts_match_output_directory(
        out_dir,
        [*_expected_artifacts(CONFIG_ONLY), *disabled_sentinels],
    )
    _assert_output_directory_preserved(out_dir, before)
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_cli_malformed_yaml_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "malformed.yaml"
    out_dir = tmp_path / "malformed_run"
    config_path.write_text(
        """
run:
  experiment_id: malformed
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task
    - [unterminated
"""
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(config_path) in completed.stderr
    assert "expected ',' or ']'" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert not out_dir.exists()


def test_cli_missing_config_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "missing.yaml"
    out_dir = tmp_path / "missing_config_run"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(config_path) in completed.stderr
    assert "No such file or directory" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert not out_dir.exists()


def test_cli_output_artifact_collision_does_not_write_partial_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "collision_run"
    out_dir.mkdir()
    existing_metrics = out_dir / "metrics.csv"
    existing_metrics.write_text("sentinel metrics\n")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(CONFIG),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "metrics.csv" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert existing_metrics.read_text() == "sentinel metrics\n"
    assert not (out_dir / "config.yaml").exists()
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_cli_ignores_disabled_output_collisions_but_blocks_enabled_artifacts(
    tmp_path: Path,
) -> None:
    success_dir = tmp_path / "disabled_optional_cli_collisions_success"
    blocked_dir = tmp_path / "disabled_optional_cli_collisions_blocked"
    disabled_sentinels = {
        "metrics.csv": "sentinel disabled metrics\n",
        "events.csv": "sentinel disabled events\n",
        "summary.md": "sentinel disabled summary\n",
    }
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(MANIFEST_ONLY),
        "--seed",
        "17",
    ]
    success_dir.mkdir()
    for artifact, content in disabled_sentinels.items():
        (success_dir / artifact).write_text(content)

    success = subprocess.run(
        [*command, "--out", str(success_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert success.returncode == 0
    assert success.stderr == ""
    assert (success_dir / "config.yaml").is_file()
    assert (success_dir / "manifest.yaml").is_file()
    for artifact, content in disabled_sentinels.items():
        assert (success_dir / artifact).read_text() == content
    manifest = yaml.safe_load((success_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)

    blocked_dir.mkdir()
    for artifact, content in disabled_sentinels.items():
        (blocked_dir / artifact).write_text(content)
    (blocked_dir / "manifest.yaml").write_text("sentinel enabled manifest\n")

    blocked = subprocess.run(
        [*command, "--out", str(blocked_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert blocked.returncode != 0
    assert "error:" in blocked.stderr
    assert str(blocked_dir) in blocked.stderr
    assert "manifest.yaml" in blocked.stderr
    assert "metrics.csv" not in blocked.stderr
    assert "events.csv" not in blocked.stderr
    assert "summary.md" not in blocked.stderr
    assert "Traceback" not in blocked.stderr
    assert (blocked_dir / "manifest.yaml").read_text() == "sentinel enabled manifest\n"
    _assert_artifacts_match_output_directory(blocked_dir, [*disabled_sentinels, "manifest.yaml"])
    assert not (blocked_dir / "config.yaml").exists()
    for artifact, content in disabled_sentinels.items():
        assert (blocked_dir / artifact).read_text() == content


def test_cli_config_artifact_collision_blocks_when_all_optional_outputs_disabled(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_cli_collision"
    stale_disabled_artifacts, collision_content = _write_config_only_collision_sentinels(out_dir)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(CONFIG_ONLY),
            "--seed",
            "17",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "config.yaml" in completed.stderr
    assert "manifest.yaml" not in completed.stderr
    assert "metrics.csv" not in completed.stderr
    assert "events.csv" not in completed.stderr
    assert "summary.md" not in completed.stderr
    assert "Traceback" not in completed.stderr
    _assert_config_only_collision_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
        collision_content=collision_content,
    )


def test_cli_config_only_outputs_succeed_and_are_byte_stable(tmp_path: Path) -> None:
    first = tmp_path / "config_only_cli_first"
    second = tmp_path / "config_only_cli_second"

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG_ONLY, out_dir, seed=17)
        _assert_artifacts_match_output_directory(out_dir, _expected_artifacts(CONFIG_ONLY))

    _assert_artifacts_are_byte_identical(first, second, _expected_artifacts(CONFIG_ONLY))
    normalized_config = yaml.safe_load((first / "config.yaml").read_text())
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"


def test_cli_config_only_rerun_refuses_to_overwrite_existing_config(tmp_path: Path) -> None:
    out_dir = tmp_path / "config_only_cli_rerun"
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(CONFIG_ONLY),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = _artifact_bytes_snapshot(out_dir, _expected_artifacts(CONFIG_ONLY))

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert str(out_dir) in second.stderr
    assert "already contains run artifacts" in second.stderr
    assert "config.yaml" in second.stderr
    assert "manifest.yaml" not in second.stderr
    assert "metrics.csv" not in second.stderr
    assert "events.csv" not in second.stderr
    assert "summary.md" not in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(out_dir, _expected_artifacts(CONFIG_ONLY))
    _assert_output_directory_preserved(out_dir, before)
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_cli_config_only_rerun_preserves_disabled_artifact_sentinels(tmp_path: Path) -> None:
    out_dir = tmp_path / "config_only_cli_rerun_with_disabled_sentinels"
    disabled_sentinels = {
        "manifest.yaml": b"sentinel disabled manifest\n",
        "metrics.csv": b"sentinel disabled metrics\n",
        "events.csv": b"sentinel disabled events\n",
        "summary.md": b"sentinel disabled summary\n",
    }
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(CONFIG_ONLY),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    for artifact, content in disabled_sentinels.items():
        (out_dir / artifact).write_bytes(content)
    before = _artifact_bytes_snapshot(out_dir)

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert str(out_dir) in second.stderr
    assert "already contains run artifacts: config.yaml" in second.stderr
    assert "manifest.yaml" not in second.stderr
    assert "metrics.csv" not in second.stderr
    assert "events.csv" not in second.stderr
    assert "summary.md" not in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(
        out_dir,
        [*_expected_artifacts(CONFIG_ONLY), *disabled_sentinels],
    )
    _assert_output_directory_preserved(out_dir, before)
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_cli_output_path_file_does_not_overwrite_or_traceback(tmp_path: Path) -> None:
    out_path = tmp_path / "file_output"
    out_path.write_text("sentinel output path\n")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(CONFIG),
            "--seed",
            "1",
            "--out",
            str(out_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_path) in completed.stderr
    assert "exists and is not a directory" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert out_path.read_text() == "sentinel output path\n"


def test_a0_baseline_requires_fifteen_agents(tmp_path: Path) -> None:
    config_path = tmp_path / "wrong_agent_count.yaml"
    config_path.write_text(
        """
run:
  experiment_id: wrong_agent_count
  ticks: 3

model:
  agent_count: 14
  actions:
    - idle
    - message
    - create_task
    - work_task
"""
    )

    with pytest.raises(ValueError, match="model.agent_count"):
        load_config(config_path)


def test_same_seed_reproduces_byte_stable_outputs(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_experiment(CONFIG, seed=17, out_dir=first)
    run_experiment(CONFIG, seed=17, out_dir=second)

    _assert_artifacts_are_byte_identical(
        first,
        second,
        ["manifest.yaml", "config.yaml", "metrics.csv", "events.csv", "summary.md"],
    )


def test_different_seed_changes_events(tmp_path: Path) -> None:
    first = tmp_path / "seed1"
    second = tmp_path / "seed2"

    run_experiment(CONFIG, seed=1, out_dir=first)
    run_experiment(CONFIG, seed=2, out_dir=second)

    assert (first / "events.csv").read_text() != (second / "events.csv").read_text()


def test_fixed_seed_lobe_and_transition_totals_are_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "lobes": {
                "backlog_growth": 44,
                "coordination": 25,
                "execution": 29,
                "low_activity": 2,
            },
            "transitions": {
                "backlog_growth->coordination": 10,
                "backlog_growth->execution": 11,
                "backlog_growth->low_activity": 2,
                "coordination->backlog_growth": 8,
                "coordination->execution": 9,
                "execution->backlog_growth": 15,
                "execution->coordination": 6,
                "low_activity->coordination": 1,
                "low_activity->execution": 1,
            },
        },
        2: {
            "lobes": {
                "backlog_growth": 49,
                "coordination": 16,
                "execution": 31,
                "low_activity": 4,
            },
            "transitions": {
                "backlog_growth->coordination": 8,
                "backlog_growth->execution": 18,
                "backlog_growth->low_activity": 1,
                "coordination->backlog_growth": 8,
                "coordination->execution": 5,
                "execution->backlog_growth": 18,
                "execution->coordination": 3,
                "execution->low_activity": 3,
                "low_activity->backlog_growth": 1,
                "low_activity->coordination": 2,
                "low_activity->execution": 1,
            },
        },
        17: {
            "lobes": {
                "backlog_growth": 52,
                "coordination": 24,
                "execution": 22,
                "low_activity": 2,
            },
            "transitions": {
                "backlog_growth->coordination": 14,
                "backlog_growth->execution": 9,
                "backlog_growth->low_activity": 2,
                "coordination->backlog_growth": 12,
                "coordination->execution": 6,
                "execution->backlog_growth": 11,
                "execution->coordination": 4,
                "low_activity->backlog_growth": 2,
            },
        },
    }

    observed = {}
    for seed in expected:
        result = run_experiment(CONFIG, seed=seed, out_dir=tmp_path / f"seed{seed}")
        lobe_totals = Counter(row["baseline_lobe_label"] for row in result.metrics)
        transition_totals = Counter(
            row["baseline_lobe_transition"]
            for row in result.metrics
            if row["baseline_lobe_transition"] not in {"start", "stable"}
        )
        observed[seed] = {
            "lobes": dict(sorted(lobe_totals.items())),
            "transitions": dict(sorted(transition_totals.items())),
        }

    assert observed == expected
    assert len({tuple(seed_totals["lobes"].items()) for seed_totals in observed.values()}) == len(expected)


def test_fixed_seed_lobe_dwell_runs_are_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "backlog_growth": {"runs": 24, "total_ticks": 44, "max_run": 6, "mean_run": 1.833333},
            "coordination": {"runs": 17, "total_ticks": 25, "max_run": 3, "mean_run": 1.470588},
            "execution": {"runs": 21, "total_ticks": 29, "max_run": 4, "mean_run": 1.380952},
            "low_activity": {"runs": 2, "total_ticks": 2, "max_run": 1, "mean_run": 1.0},
        },
        2: {
            "backlog_growth": {"runs": 28, "total_ticks": 49, "max_run": 5, "mean_run": 1.75},
            "coordination": {"runs": 13, "total_ticks": 16, "max_run": 3, "mean_run": 1.230769},
            "execution": {"runs": 24, "total_ticks": 31, "max_run": 3, "mean_run": 1.291667},
            "low_activity": {"runs": 4, "total_ticks": 4, "max_run": 1, "mean_run": 1.0},
        },
        17: {
            "backlog_growth": {"runs": 25, "total_ticks": 52, "max_run": 4, "mean_run": 2.08},
            "coordination": {"runs": 19, "total_ticks": 24, "max_run": 2, "mean_run": 1.263158},
            "execution": {"runs": 15, "total_ticks": 22, "max_run": 3, "mean_run": 1.466667},
            "low_activity": {"runs": 2, "total_ticks": 2, "max_run": 1, "mean_run": 1.0},
        },
    }

    observed = {}
    for seed in expected:
        out_dir = tmp_path / f"seed{seed}"
        result = run_experiment(CONFIG, seed=seed, out_dir=out_dir)
        summary = (out_dir / "summary.md").read_text()
        observed[seed] = _lobe_dwell_runs(result.metrics)

        for label, dwell in expected[seed].items():
            assert (
                f"- {label}: runs={dwell['runs']}, total_ticks={dwell['total_ticks']}, "
                f"max_run={dwell['max_run']}, mean_run={dwell['mean_run']}"
            ) in summary

    assert observed == expected


def test_fixed_seed_lobe_run_state_is_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "final_label": "backlog_growth",
            "final_run_id": 64,
            "final_run_length": 1,
        },
        2: {
            "final_label": "backlog_growth",
            "final_run_id": 69,
            "final_run_length": 3,
        },
        17: {
            "final_label": "coordination",
            "final_run_id": 61,
            "final_run_length": 1,
        },
    }

    observed = {}
    for seed in expected:
        result = run_experiment(CONFIG, seed=seed, out_dir=tmp_path / f"seed{seed}")
        final = result.metrics[-1]
        observed[seed] = {
            "final_label": final["baseline_lobe_label"],
            "final_run_id": final["baseline_lobe_run_id"],
            "final_run_length": final["baseline_lobe_current_run_length"],
        }

    assert observed == expected


def test_fixed_seed_queue_age_summaries_are_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "final_max_age": 47,
            "final_mean_age": 18.4,
            "peak_max_age": 47,
            "mean_mean_age": 8.038303,
        },
        2: {
            "final_max_age": 63,
            "final_mean_age": 25.142857,
            "peak_max_age": 64,
            "mean_mean_age": 13.034658,
        },
        17: {
            "final_max_age": 73,
            "final_mean_age": 29.914439,
            "peak_max_age": 73,
            "mean_mean_age": 15.881428,
        },
    }

    observed = {}
    for seed in expected:
        out_dir = tmp_path / f"seed{seed}"
        result = run_experiment(CONFIG, seed=seed, out_dir=out_dir)
        final_metrics = result.metrics[-1]
        summary = (out_dir / "summary.md").read_text()

        observed[seed] = {
            "final_max_age": final_metrics["queued_task_age_max_tick"],
            "final_mean_age": final_metrics["queued_task_age_mean_tick"],
            "peak_max_age": max(
                int(row["queued_task_age_max_tick"])
                for row in result.metrics
            ),
            "mean_mean_age": round(
                sum(float(row["queued_task_age_mean_tick"]) for row in result.metrics)
                / len(result.metrics),
                6,
            ),
        }

        assert f"- final queued task max age: {expected[seed]['final_max_age']}" in summary
        assert f"- final queued task mean age: {expected[seed]['final_mean_age']}" in summary
        assert f"- peak queued task max age: {expected[seed]['peak_max_age']}" in summary
        assert f"- mean queued task mean age: {expected[seed]['mean_mean_age']}" in summary

    assert observed == expected


def _lobe_dwell_runs(metrics: list[dict[str, object]]) -> dict[str, dict[str, int | float]]:
    runs_by_label: dict[str, list[int]] = {label: [] for label in BASELINE_LOBE_LABELS}
    previous_label = ""
    current_run_length = 0

    for row in metrics:
        label = str(row["baseline_lobe_label"])
        if label == previous_label:
            current_run_length += 1
        else:
            if previous_label:
                runs_by_label[previous_label].append(current_run_length)
            previous_label = label
            current_run_length = 1

    if previous_label:
        runs_by_label[previous_label].append(current_run_length)

    return {
        label: {
            "runs": len(runs),
            "total_ticks": sum(runs),
            "max_run": max(runs),
            "mean_run": round(sum(runs) / len(runs), 6),
        }
        for label, runs in runs_by_label.items()
        if runs
    }


def _assert_manifest_only_preserves_full_schema_provenance(out_dir: Path) -> None:
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    actions = ("idle", "message", "create_task", "work_task")

    assert manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()
    assert manifest["model"]["baseline_lobes"] == {
        "labels": list(BASELINE_LOBE_LABELS),
        "transition_fields": list(BASELINE_LOBE_TRANSITION_FIELDS),
    }
    assert manifest["model"]["queue_dynamics_metrics"] == {
        "pressure_fields": list(QUEUE_PRESSURE_METRIC_FIELDS),
        "queued_task_age_fields": list(QUEUED_TASK_AGE_METRIC_FIELDS),
    }
    assert manifest["model"]["events"] == {
        "types": list(BASELINE_EVENT_TYPES),
        "fields": list(EVENT_FIELDS),
    }
    assert manifest["model"]["metrics"] == {
        "fields": list(metrics_fieldnames(actions)),
    }
    assert manifest["model"]["role_action_metrics"] == {
        "roles": list(BASELINE_ROLES),
        "actions": list(actions),
        "fields": list(role_action_metric_fields(actions)),
    }


def _write_manifest_only_disabled_artifact_sentinels(out_dir: Path) -> dict[str, bytes]:
    out_dir.mkdir()
    stale_disabled_artifacts = {
        "metrics.csv": b"stale disabled metrics sentinel\n",
        "events.csv": b"stale disabled events sentinel\n",
        "summary.md": b"stale disabled summary sentinel\n",
    }

    for artifact, content in stale_disabled_artifacts.items():
        (out_dir / artifact).write_bytes(content)

    return stale_disabled_artifacts


def _assert_manifest_only_preserves_stale_disabled_artifacts(
    out_dir: Path,
    *,
    stale_disabled_artifacts: dict[str, bytes],
) -> None:
    assert (out_dir / "config.yaml").is_file()
    assert (out_dir / "manifest.yaml").is_file()
    _assert_stale_artifacts_preserved(
        out_dir,
        stale_disabled_artifacts,
        expected_artifacts=[*_expected_artifacts(MANIFEST_ONLY), *stale_disabled_artifacts],
    )


def _write_manifest_only_collision_sentinels(
    out_dir: Path,
    collision_artifact: str,
) -> tuple[dict[str, bytes], bytes]:
    stale_disabled_artifacts = _write_manifest_only_disabled_artifact_sentinels(out_dir)
    collision_content = f"preexisting enabled {collision_artifact} sentinel\n".encode()

    (out_dir / collision_artifact).write_bytes(collision_content)

    return stale_disabled_artifacts, collision_content


def _assert_manifest_only_collision_preserves_stale_disabled_artifacts(
    out_dir: Path,
    collision_artifact: str,
    *,
    stale_disabled_artifacts: dict[str, bytes],
    collision_content: bytes,
) -> None:
    _assert_stale_artifacts_preserved(
        out_dir,
        {**stale_disabled_artifacts, collision_artifact: collision_content},
        expected_artifacts=[*stale_disabled_artifacts, collision_artifact],
    )


def _assert_config_only_writes_normalized_config(out_dir: Path) -> None:
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())

    assert normalized_config == {
        "run": {
            "experiment_id": "a0_config_only",
            "ticks": 3,
        },
        "model": {
            "agent_count": 15,
            "actions": ["idle", "message", "create_task", "work_task"],
        },
        "outputs": {
            "write_manifest": False,
            "write_metrics": False,
            "write_events": False,
            "write_summary": False,
        },
    }


def _write_config_only_disabled_artifact_sentinels(out_dir: Path) -> dict[str, bytes]:
    out_dir.mkdir()
    stale_disabled_artifacts = {
        "manifest.yaml": b"stale disabled manifest sentinel\n",
        "metrics.csv": b"stale disabled metrics sentinel\n",
        "events.csv": b"stale disabled events sentinel\n",
        "summary.md": b"stale disabled summary sentinel\n",
    }

    for artifact, content in stale_disabled_artifacts.items():
        (out_dir / artifact).write_bytes(content)

    return stale_disabled_artifacts


def _assert_config_only_preserves_stale_disabled_artifacts(
    out_dir: Path,
    *,
    stale_disabled_artifacts: dict[str, bytes],
) -> None:
    assert (out_dir / "config.yaml").is_file()
    _assert_stale_artifacts_preserved(
        out_dir,
        stale_disabled_artifacts,
        expected_artifacts=[*_expected_artifacts(CONFIG_ONLY), *stale_disabled_artifacts],
    )


def _write_config_only_collision_sentinels(out_dir: Path) -> tuple[dict[str, bytes], bytes]:
    stale_disabled_artifacts = _write_config_only_disabled_artifact_sentinels(out_dir)
    collision_content = b"sentinel mandatory config\n"

    (out_dir / "config.yaml").write_bytes(collision_content)

    return stale_disabled_artifacts, collision_content


def _assert_config_only_collision_preserves_stale_disabled_artifacts(
    out_dir: Path,
    *,
    stale_disabled_artifacts: dict[str, bytes],
    collision_content: bytes,
) -> None:
    _assert_stale_artifacts_preserved(
        out_dir,
        {**stale_disabled_artifacts, "config.yaml": collision_content},
        expected_artifacts=[*_expected_artifacts(CONFIG_ONLY), *stale_disabled_artifacts],
    )


def _assert_no_manifest_writes_enabled_artifacts(
    out_dir: Path,
    *,
    stale_manifest: bytes | None = None,
) -> None:
    expected_artifacts = _expected_artifacts(NO_MANIFEST)
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    summary_artifacts = _summary_written_artifacts(summary)

    assert summary_artifacts == expected_artifacts
    _assert_artifacts_match_output_directory(
        out_dir,
        [*expected_artifacts, *(["manifest.yaml"] if stale_manifest is not None else [])],
    )
    assert normalized_config["outputs"] == expected_outputs
    assert "- write_manifest: disabled" in summary
    assert "- write_metrics: enabled" in summary
    assert "- write_events: enabled" in summary
    assert "- write_summary: enabled" in summary
    _assert_no_manifest_enabled_artifact_row_counts(out_dir)
    if stale_manifest is None:
        assert not (out_dir / "manifest.yaml").exists()
    else:
        assert (out_dir / "manifest.yaml").read_bytes() == stale_manifest


def _assert_no_manifest_enabled_artifact_row_counts(out_dir: Path) -> None:
    with (out_dir / "metrics.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 3
    with (out_dir / "events.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 45


def _summary_written_artifacts(summary: str) -> list[str]:
    written_artifacts_line = next(
        line for line in summary.splitlines() if line.startswith("- written artifacts: ")
    )
    return written_artifacts_line.removeprefix("- written artifacts: ").split(", ")


def _assert_summary_output_flags_match_config(
    summary: str,
    output_flags: dict[str, bool],
) -> None:
    for name, enabled in output_flags.items():
        state = "enabled" if enabled else "disabled"
        assert f"- {name}: {state}" in summary


def _assert_config_manifest_and_summary_run_fields_match(
    normalized_config: dict[str, object],
    *,
    manifest: dict[str, object],
    summary: str,
    seed: int,
) -> None:
    run_config = normalized_config["run"]
    model_config = normalized_config["model"]
    assert isinstance(run_config, dict)
    assert isinstance(model_config, dict)

    assert manifest["config"] == normalized_config
    assert manifest["experiment_id"] == run_config["experiment_id"]
    assert manifest["seed"] == seed
    assert manifest["ticks"] == run_config["ticks"]
    assert manifest["agent_count"] == model_config["agent_count"]
    assert manifest["actions"] == model_config["actions"]

    assert f"# {run_config['experiment_id']}" in summary
    assert f"- seed: {seed}" in summary
    assert f"- ticks: {run_config['ticks']}" in summary
    assert f"- agents: {model_config['agent_count']}" in summary


def _assert_manifest_agent_identity_and_roles_match_baseline(
    manifest: dict[str, object],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)

    agent_count = manifest["agent_count"]
    assert isinstance(agent_count, int)
    expected_agent_ids = [
        f"agent_{index:02d}"
        for index in range(1, agent_count + 1)
    ]
    expected_roles = {
        agent_id: BASELINE_ROLES[(index - 1) % len(BASELINE_ROLES)]
        for index, agent_id in enumerate(expected_agent_ids, start=1)
    }

    assert agent_count == 15
    assert model["agent_ids"] == expected_agent_ids
    assert model["roles"] == expected_roles
    assert model["role_action_metrics"]["roles"] == list(BASELINE_ROLES)


def _assert_manifest_bus_counts_match_summary_and_metrics_row(
    manifest: dict[str, object],
    *,
    summary: str,
    metrics_row: dict[str, str],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)

    bus_nodes = model["bus_nodes"]
    bus_edges = model["bus_edges"]

    assert int(metrics_row["bus_nodes"]) == bus_nodes
    assert int(metrics_row["bus_edges"]) == bus_edges
    assert f"- bus graph: {bus_nodes} nodes, {bus_edges} edges" in summary


def _assert_summary_static_bus_metrics_match_metrics_row(
    summary: str,
    *,
    metrics_row: dict[str, str],
) -> None:
    assert f"- bus density: {metrics_row['bus_density']}" in summary
    assert f"- bus mean degree: {metrics_row['bus_mean_degree']}" in summary
    assert (
        f"- bus degree centralization: "
        f"{metrics_row['bus_degree_centralization']}"
    ) in summary


def _directory_artifacts(out_dir: Path) -> list[str]:
    return sorted(path.name for path in out_dir.iterdir() if path.is_file())


def _assert_artifacts_match_output_directory(
    out_dir: Path,
    artifacts: list[str],
) -> None:
    assert sorted(artifacts) == _directory_artifacts(out_dir)


def _assert_stale_artifacts_preserved(
    out_dir: Path,
    expected_contents: dict[str, bytes],
    *,
    expected_artifacts: list[str],
) -> None:
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)
    for artifact, content in expected_contents.items():
        assert (out_dir / artifact).read_bytes() == content


def _artifact_bytes_snapshot(
    out_dir: Path,
    artifacts: list[str] | None = None,
) -> dict[str, bytes]:
    artifact_names = artifacts if artifacts is not None else _directory_artifacts(out_dir)
    return {artifact: (out_dir / artifact).read_bytes() for artifact in artifact_names}


def _assert_output_directory_preserved(
    out_dir: Path,
    before: dict[str, bytes],
) -> None:
    assert _artifact_bytes_snapshot(out_dir) == before


def _assert_artifacts_are_byte_identical(
    first: Path,
    second: Path,
    artifacts: list[str],
) -> None:
    for artifact in artifacts:
        assert (first / artifact).read_bytes() == (second / artifact).read_bytes()


def _assert_summary_written_artifacts_match_output_directory(out_dir: Path) -> list[str]:
    summary_artifacts = _summary_written_artifacts((out_dir / "summary.md").read_text())
    _assert_artifacts_match_output_directory(out_dir, summary_artifacts)
    return summary_artifacts


def _assert_artifact_indexes_match_directory_contents(
    out_dir: Path,
    expected_artifacts: list[str],
) -> None:
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)

    if (out_dir / "manifest.yaml").exists():
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        assert manifest["artifacts"] == expected_artifacts

    if (out_dir / "summary.md").exists():
        assert _summary_written_artifacts((out_dir / "summary.md").read_text()) == expected_artifacts


def _write_no_manifest_disabled_manifest_sentinel(out_dir: Path) -> bytes:
    out_dir.mkdir()
    stale_manifest = b"stale disabled manifest sentinel\n"
    (out_dir / "manifest.yaml").write_bytes(stale_manifest)
    return stale_manifest


def _assert_no_manifest_preserves_stale_disabled_manifest(
    out_dir: Path,
    *,
    stale_manifest: bytes,
) -> None:
    _assert_no_manifest_writes_enabled_artifacts(
        out_dir,
        stale_manifest=stale_manifest,
    )


def _write_no_manifest_collision_sentinels(
    out_dir: Path,
    collision_artifact: str,
) -> tuple[bytes, bytes]:
    out_dir.mkdir()
    stale_manifest = b"stale disabled manifest sentinel\n"
    collision_content = f"preexisting enabled {collision_artifact} sentinel\n".encode()

    (out_dir / "manifest.yaml").write_bytes(stale_manifest)
    (out_dir / collision_artifact).write_bytes(collision_content)

    return stale_manifest, collision_content


def _assert_no_manifest_collision_preserves_stale_manifest(
    out_dir: Path,
    collision_artifact: str,
    *,
    stale_manifest: bytes,
    collision_content: bytes,
) -> None:
    _assert_stale_artifacts_preserved(
        out_dir,
        {
            "manifest.yaml": stale_manifest,
            collision_artifact: collision_content,
        },
        expected_artifacts=["manifest.yaml", collision_artifact],
    )


def _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(
    out_dir: Path,
) -> None:
    actions = ("idle", "message", "create_task", "work_task")

    assert not (out_dir / "manifest.yaml").exists()
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))
        event_rows = list(csv.DictReader(handle, fieldnames=events_header))
    summary = (out_dir / "summary.md").read_text()

    assert metrics_header == list(metrics_fieldnames(actions))
    assert events_header == list(EVENT_FIELDS)
    assert event_rows
    assert set(event["event_type"] for event in event_rows) <= set(BASELINE_EVENT_TYPES)
    _assert_summary_records_artifact_schema_provenance(
        summary,
        metrics_header=metrics_header,
        events_header=events_header,
        actions=actions,
    )


def _assert_summary_records_artifact_schema_provenance(
    summary: str,
    *,
    metrics_header: list[str],
    events_header: list[str],
    actions: tuple[str, ...],
) -> None:
    assert "## Artifact schema provenance" in summary
    assert f"- metrics fields: {len(metrics_header)}" in summary
    assert f"- event fields: {len(events_header)}" in summary
    assert f"- event types: {len(BASELINE_EVENT_TYPES)}" in summary
    assert f"- baseline lobe labels: {len(BASELINE_LOBE_LABELS)}" in summary
    assert f"- baseline lobe transition fields: {len(BASELINE_LOBE_TRANSITION_FIELDS)}" in summary
    assert f"- queue pressure fields: {len(QUEUE_PRESSURE_METRIC_FIELDS)}" in summary
    assert f"- queued task age fields: {len(QUEUED_TASK_AGE_METRIC_FIELDS)}" in summary
    assert f"- role/action fields: {len(role_action_metric_fields(actions))}" in summary
    assert "- metrics schema source: ohdyn.sim.metrics_fieldnames" in summary
    assert "- events schema source: ohdyn.sim.EVENT_FIELDS" in summary
    assert "- manifest mirrors emitted artifact schemas: yes" in summary


def _assert_summary_schema_provenance_counts_match_manifest(
    summary: str,
    manifest: dict[str, object],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)

    metrics = model["metrics"]
    events = model["events"]
    baseline_lobes = model["baseline_lobes"]
    queue_dynamics = model["queue_dynamics_metrics"]
    role_action_metrics = model["role_action_metrics"]
    assert isinstance(metrics, dict)
    assert isinstance(events, dict)
    assert isinstance(baseline_lobes, dict)
    assert isinstance(queue_dynamics, dict)
    assert isinstance(role_action_metrics, dict)

    assert f"- metrics fields: {len(metrics['fields'])}" in summary
    assert f"- event fields: {len(events['fields'])}" in summary
    assert f"- event types: {len(events['types'])}" in summary
    assert f"- baseline lobe labels: {len(baseline_lobes['labels'])}" in summary
    assert (
        f"- baseline lobe transition fields: "
        f"{len(baseline_lobes['transition_fields'])}"
    ) in summary
    assert f"- queue pressure fields: {len(queue_dynamics['pressure_fields'])}" in summary
    assert (
        f"- queued task age fields: "
        f"{len(queue_dynamics['queued_task_age_fields'])}"
    ) in summary
    assert f"- role/action fields: {len(role_action_metrics['fields'])}" in summary


def _assert_summary_event_type_totals_match_events(
    summary: str,
    *,
    event_rows: list[dict[str, str]],
) -> None:
    assert event_rows
    assert "## Event type totals" in summary

    event_type_totals = Counter(row["event_type"] for row in event_rows)
    for event_type, count in sorted(event_type_totals.items()):
        assert f"- {event_type}: {count}" in summary


def _assert_summary_top_level_totals_match_metrics_and_events(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert event_rows
    final = metric_rows[-1]

    messages_sent = sum(int(row["messages_sent_tick"]) for row in metric_rows)
    task_work_events = sum(int(row["tasks_worked_tick"]) for row in metric_rows)
    tasks_created = sum(int(row["tasks_created_tick"]) for row in metric_rows)
    tasks_completed = sum(int(row["tasks_completed_tick"]) for row in metric_rows)

    event_type_totals = Counter(row["event_type"] for row in event_rows)
    assert messages_sent == event_type_totals["message_sent"]
    assert task_work_events == event_type_totals["task_worked"]
    assert tasks_created == event_type_totals["task_created"]
    assert tasks_created == int(final["tasks_created_total"])
    assert tasks_completed == int(final["tasks_completed_total"])

    assert f"- events: {len(event_rows)}" in summary
    assert f"- messages sent: {messages_sent}" in summary
    assert f"- task work events: {task_work_events}" in summary
    assert f"- tasks created: {tasks_created}" in summary
    assert f"- tasks completed: {tasks_completed}" in summary
    assert f"- final queue depth: {final['queue_depth']}" in summary


def _assert_events_per_tick_action_counts_match_metrics_top_level_action_totals(
    *,
    metric_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert event_rows

    event_type_metric_fields = {
        "agent_idle": "idle_tick",
        "message_sent": "messages_sent_tick",
        "task_created": "tasks_created_tick",
        "task_worked": "tasks_worked_tick",
    }
    expected_ticks = [int(row["tick"]) for row in metric_rows]
    observed_event_ticks = sorted({int(event["tick"]) for event in event_rows})
    event_counts_by_tick = {
        tick: Counter(
            event["event_type"]
            for event in event_rows
            if int(event["tick"]) == tick
        )
        for tick in expected_ticks
    }

    assert set(event_type_metric_fields) == set(BASELINE_EVENT_TYPES)
    assert observed_event_ticks == expected_ticks
    assert sorted(event_counts_by_tick) == expected_ticks
    for row in metric_rows:
        tick = int(row["tick"])
        event_counts = event_counts_by_tick[tick]

        for event_type, metric_field in event_type_metric_fields.items():
            assert event_counts[event_type] == int(row[metric_field])
        assert sum(event_counts.values()) == int(row["agent_count"])


def _assert_events_per_tick_counts_match_configured_agent_population(
    *,
    event_rows: list[dict[str, str]],
    ticks: int,
    agent_count: int,
) -> None:
    assert event_rows

    expected_ticks = list(range(ticks))
    events_by_tick = Counter(int(row["tick"]) for row in event_rows)

    assert sorted(events_by_tick) == expected_ticks
    assert events_by_tick == {
        tick: agent_count
        for tick in expected_ticks
    }
    assert len(event_rows) == ticks * agent_count


def _assert_events_per_tick_agent_ids_match_manifest(
    *,
    event_rows: list[dict[str, str]],
    ticks: int,
    manifest_agent_ids: list[str],
) -> None:
    assert event_rows

    expected_ticks = list(range(ticks))
    expected_agent_ids = sorted(manifest_agent_ids)
    agent_ids_by_tick = {
        tick: [
            event["agent_id"]
            for event in event_rows
            if int(event["tick"]) == tick
        ]
        for tick in expected_ticks
    }

    assert sorted({int(event["tick"]) for event in event_rows}) == expected_ticks
    for tick, agent_ids in agent_ids_by_tick.items():
        assert len(agent_ids) == len(expected_agent_ids), tick
        assert len(set(agent_ids)) == len(expected_agent_ids), tick
        assert sorted(agent_ids) == expected_agent_ids


def _assert_events_replay_to_role_action_metrics_through_manifest_roles(
    *,
    metric_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
    manifest_roles: dict[str, str],
    actions: tuple[str, ...],
) -> None:
    assert metric_rows
    assert event_rows

    expected_ticks = [int(row["tick"]) for row in metric_rows]
    role_action_counts_by_tick = {
        tick: Counter(
            (manifest_roles[event["agent_id"]], event["action"])
            for event in event_rows
            if int(event["tick"]) == tick
        )
        for tick in expected_ticks
    }

    assert sorted({int(event["tick"]) for event in event_rows}) == expected_ticks
    assert set(actions) == {"idle", "message", "create_task", "work_task"}
    assert set(manifest_roles.values()) == set(BASELINE_ROLES)
    for event in event_rows:
        assert event["agent_id"] in manifest_roles
        assert event["action"] in actions

    for row in metric_rows:
        tick = int(row["tick"])
        role_action_counts = role_action_counts_by_tick[tick]
        for role in BASELINE_ROLES:
            for action in actions:
                assert role_action_counts[(role, action)] == int(
                    row[f"role_{role}_{action}_tick"]
                )


def _assert_events_per_tick_task_lifecycle_matches_queue_and_task_metrics(
    *,
    metric_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert event_rows

    events_by_tick: dict[int, list[dict[str, str]]] = {
        int(row["tick"]): [] for row in metric_rows
    }
    for event in event_rows:
        events_by_tick[int(event["tick"])].append(event)

    expected_ticks = [int(row["tick"]) for row in metric_rows]
    assert sorted(events_by_tick) == expected_ticks

    created_total = 0
    completed_total = 0
    previous_queue_depth = 0
    created_task_ids: set[str] = set()
    worked_task_ids: set[str] = set()

    for row in metric_rows:
        tick = int(row["tick"])
        tick_events = events_by_tick[tick]
        created_events = [
            event for event in tick_events if event["event_type"] == "task_created"
        ]
        worked_events = [
            event for event in tick_events if event["event_type"] == "task_worked"
        ]
        completed_events = [
            event for event in worked_events if event["completed"] == "True"
        ]

        for event in created_events:
            assert event["task_id"]
            assert int(event["work_units"]) > 0
            created_task_ids.add(event["task_id"])
        for event in worked_events:
            assert event["task_id"]
            assert int(event["remaining_work"]) >= 0
            assert event["completed"] in {"False", "True"}
            worked_task_ids.add(event["task_id"])

        created_total += len(created_events)
        completed_total += len(completed_events)
        queue_depth = int(row["queue_depth"])

        assert len(created_events) == int(row["tasks_created_tick"])
        assert len(worked_events) == int(row["tasks_worked_tick"])
        assert len(completed_events) == int(row["tasks_completed_tick"])
        assert created_total == int(row["tasks_created_total"])
        assert completed_total == int(row["tasks_completed_total"])
        assert queue_depth - previous_queue_depth == int(row["queue_delta_tick"])
        assert int(row["queue_delta_tick"]) == len(created_events) - len(completed_events)
        assert queue_depth == created_total - completed_total

        previous_queue_depth = queue_depth

    assert worked_task_ids <= created_task_ids


def _assert_event_replay_reproduces_queued_task_age_metrics(
    *,
    metric_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert event_rows

    events_by_tick: dict[int, list[dict[str, str]]] = {
        int(row["tick"]): [] for row in metric_rows
    }
    for event in event_rows:
        events_by_tick[int(event["tick"])].append(event)

    expected_ticks = [int(row["tick"]) for row in metric_rows]
    assert sorted(events_by_tick) == expected_ticks

    task_queue: deque[dict[str, int | str]] = deque()
    for row in metric_rows:
        tick = int(row["tick"])
        for event in events_by_tick[tick]:
            if event["event_type"] == "task_created":
                task_queue.append(
                    {
                        "task_id": event["task_id"],
                        "created_tick": tick,
                        "remaining_work": int(event["work_units"]),
                    }
                )
            elif event["event_type"] == "task_worked":
                task = task_queue.popleft()
                assert task["task_id"] == event["task_id"]
                task["remaining_work"] = int(event["remaining_work"])
                if event["completed"] != "True":
                    task_queue.append(task)

        ages = [tick - int(task["created_tick"]) for task in task_queue]
        expected_max_age = max(ages, default=0)
        expected_mean_age = round(sum(ages) / len(ages), 6) if ages else 0.0

        assert int(row["queued_task_age_max_tick"]) == expected_max_age
        assert float(row["queued_task_age_mean_tick"]) == expected_mean_age


def _assert_summary_bus_graph_fields_match_metrics_and_manifest(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
    manifest: dict[str, object],
) -> None:
    assert metric_rows
    final = metric_rows[-1]
    model = manifest["model"]
    assert isinstance(model, dict)

    assert int(final["bus_nodes"]) == model["bus_nodes"]
    assert int(final["bus_edges"]) == model["bus_edges"]
    assert f"- bus graph: {model['bus_nodes']} nodes, {model['bus_edges']} edges" in summary
    assert f"- bus density: {final['bus_density']}" in summary
    assert f"- bus degree centralization: {final['bus_degree_centralization']}" in summary


def _assert_summary_role_action_totals_match_metrics(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
    actions: tuple[str, ...],
) -> None:
    assert "## Role action totals" in summary

    for role, totals in _role_action_totals_from_metrics(metric_rows, actions).items():
        assert (
            f"- {role}: idle={totals['idle']}, message={totals['message']}, "
            f"create_task={totals['create_task']}, work_task={totals['work_task']}"
        ) in summary


def _role_action_totals_from_metrics(
    metric_rows: list[dict[str, str]],
    actions: tuple[str, ...],
) -> dict[str, dict[str, int]]:
    return {
        role: {
            action: sum(int(row[f"role_{role}_{action}_tick"]) for row in metric_rows)
            for action in actions
        }
        for role in BASELINE_ROLES
    }


def _assert_summary_queue_dynamics_match_metrics(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    final = metric_rows[-1]
    pressure_totals = _queue_pressure_totals_from_metrics(metric_rows)
    peak_queued_task_age = max(
        int(row["queued_task_age_max_tick"]) for row in metric_rows
    )
    mean_queued_task_mean_age = round(
        sum(float(row["queued_task_age_mean_tick"]) for row in metric_rows)
        / len(metric_rows),
        6,
    )

    assert f"- final backlog pressure: {final['backlog_pressure_tick']}" in summary
    assert f"- final queued task max age: {final['queued_task_age_max_tick']}" in summary
    assert f"- final queued task mean age: {final['queued_task_age_mean_tick']}" in summary
    assert f"- peak queued task max age: {peak_queued_task_age}" in summary
    assert f"- mean queued task mean age: {mean_queued_task_mean_age}" in summary
    assert (
        f"- created-completed balance: "
        f"{pressure_totals['created_completed_balance_tick']}"
    ) in summary
    assert (
        f"- created-worked balance: "
        f"{pressure_totals['created_worked_balance_tick']}"
    ) in summary
    assert f"- work-completion gap: {pressure_totals['work_completion_gap_tick']}" in summary


def _assert_first_row_queue_pressure_fields_match_summary(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    first = metric_rows[0]
    pressure_totals = _queue_pressure_totals_from_metrics(metric_rows)

    created = int(first["tasks_created_tick"])
    worked = int(first["tasks_worked_tick"])
    completed = int(first["tasks_completed_tick"])

    assert int(first["created_completed_balance_tick"]) == created - completed
    assert int(first["created_worked_balance_tick"]) == created - worked
    assert int(first["work_completion_gap_tick"]) == worked - completed
    assert first["backlog_pressure_tick"] == first["queue_depth"]

    assert f"- final backlog pressure: {metric_rows[-1]['backlog_pressure_tick']}" in summary
    assert (
        f"- created-completed balance: "
        f"{pressure_totals['created_completed_balance_tick']}"
    ) in summary
    assert (
        f"- created-worked balance: "
        f"{pressure_totals['created_worked_balance_tick']}"
    ) in summary
    assert f"- work-completion gap: {pressure_totals['work_completion_gap_tick']}" in summary


def _assert_queued_task_age_summary_matches_metrics(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    final = metric_rows[-1]
    peak_queued_task_age = max(
        int(row["queued_task_age_max_tick"]) for row in metric_rows
    )
    mean_queued_task_mean_age = round(
        sum(float(row["queued_task_age_mean_tick"]) for row in metric_rows)
        / len(metric_rows),
        6,
    )

    assert f"- final queued task max age: {final['queued_task_age_max_tick']}" in summary
    assert f"- final queued task mean age: {final['queued_task_age_mean_tick']}" in summary
    assert f"- peak queued task max age: {peak_queued_task_age}" in summary
    assert f"- mean queued task mean age: {mean_queued_task_mean_age}" in summary


def _queue_pressure_totals_from_metrics(
    metric_rows: list[dict[str, str]],
) -> dict[str, int]:
    return {
        field: sum(int(row[field]) for row in metric_rows)
        for field in QUEUE_PRESSURE_METRIC_FIELDS
        if field != "backlog_pressure_tick"
    }


def _assert_summary_lobe_aggregates_match_metrics(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert "## Baseline lobe totals" in summary
    assert "## Baseline lobe transitions" in summary
    assert "## Baseline lobe dwell runs" in summary

    lobe_totals = Counter(row["baseline_lobe_label"] for row in metric_rows)
    lobe_transitions = Counter(
        row["baseline_lobe_transition"]
        for row in metric_rows
        if row["baseline_lobe_transition"] not in {"start", "stable"}
    )

    for label, count in sorted(lobe_totals.items()):
        assert f"- {label}: {count}" in summary
    for transition, count in sorted(lobe_transitions.items()):
        assert f"- {transition}: {count}" in summary
    _assert_lobe_dwell_run_summary_matches_metrics(summary, metric_rows=metric_rows)


def _assert_lobe_dwell_run_summary_matches_metrics(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert "## Baseline lobe dwell runs" in summary

    for label, dwell in _lobe_dwell_runs(metric_rows).items():
        assert (
            f"- {label}: runs={dwell['runs']}, total_ticks={dwell['total_ticks']}, "
            f"max_run={dwell['max_run']}, mean_run={dwell['mean_run']}"
        ) in summary


def _assert_lobe_run_state_matches_recomputed_dwell_runs(
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows

    previous_label = ""
    expected_run_id = 0
    expected_run_length = 0
    completed_run_lengths: list[int] = []
    completed_run_labels: list[str] = []

    for row in metric_rows:
        label = row["baseline_lobe_label"]
        if label == previous_label:
            expected_run_length += 1
        else:
            if previous_label:
                completed_run_labels.append(previous_label)
                completed_run_lengths.append(expected_run_length)
            expected_run_id += 1
            expected_run_length = 1

        assert int(row["baseline_lobe_run_id"]) == expected_run_id
        assert int(row["baseline_lobe_current_run_length"]) == expected_run_length
        previous_label = label

    completed_run_labels.append(previous_label)
    completed_run_lengths.append(expected_run_length)

    dwell_runs = _lobe_dwell_runs(metric_rows)
    assert expected_run_id == sum(dwell["runs"] for dwell in dwell_runs.values())
    assert len(completed_run_lengths) == expected_run_id
    assert sum(completed_run_lengths) == len(metric_rows)
    assert max(completed_run_lengths) == max(dwell["max_run"] for dwell in dwell_runs.values())
    assert set(completed_run_labels) == set(dwell_runs)


def _assert_lobe_transitions_match_adjacent_labels(
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows

    assert metric_rows[0]["baseline_lobe_previous_label"] == ""
    assert metric_rows[0]["baseline_lobe_transition"] == "start"
    assert metric_rows[0]["baseline_lobe_transition_tick"] == "0"

    previous_label = metric_rows[0]["baseline_lobe_label"]
    for row in metric_rows[1:]:
        current_label = row["baseline_lobe_label"]
        changed = previous_label != current_label
        expected_transition = (
            f"{previous_label}->{current_label}"
            if changed
            else "stable"
        )

        assert row["baseline_lobe_previous_label"] == previous_label
        assert row["baseline_lobe_transition"] == expected_transition
        assert row["baseline_lobe_transition_tick"] == str(int(changed))
        previous_label = current_label


def _assert_summary_lobe_transition_totals_match_adjacent_labels(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert "## Baseline lobe transitions" in summary

    assert _summary_lobe_transition_totals(summary) == _lobe_transition_totals_from_adjacent_labels(
        metric_rows
    )


def _assert_summary_lobe_transition_endpoints_use_only_manifest_lobe_labels(
    summary: str,
    *,
    manifest: dict[str, object],
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = set(baseline_lobes["labels"])
    summary_totals = _summary_lobe_transition_totals(summary)
    observed_totals = _lobe_transition_totals_from_adjacent_labels(metric_rows)

    assert summary_totals
    assert summary_totals == observed_totals
    for transition in summary_totals:
        source_label, target_label = transition.split("->", maxsplit=1)
        assert source_label in manifest_labels
        assert target_label in manifest_labels


def _assert_manifest_lobe_labels_cover_observed_metrics(
    manifest: dict[str, object],
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = baseline_lobes["labels"]
    assert manifest_labels == list(BASELINE_LOBE_LABELS)
    assert set(row["baseline_lobe_label"] for row in metric_rows) <= set(manifest_labels)


def _assert_manifest_lobe_labels_cover_previous_metrics_labels(
    manifest: dict[str, object],
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = baseline_lobes["labels"]
    previous_labels = [row["baseline_lobe_previous_label"] for row in metric_rows]

    assert manifest_labels == list(BASELINE_LOBE_LABELS)
    assert previous_labels[0] == ""
    assert "" not in previous_labels[1:]
    assert set(previous_labels[1:]) <= set(manifest_labels)


def _assert_manifest_lobe_labels_cover_metrics_transition_endpoints(
    manifest: dict[str, object],
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = baseline_lobes["labels"]
    transitions = [
        row["baseline_lobe_transition"]
        for row in metric_rows
        if row["baseline_lobe_transition"] not in {"start", "stable"}
    ]

    assert manifest_labels == list(BASELINE_LOBE_LABELS)
    assert transitions
    for transition in transitions:
        source_label, target_label = transition.split("->", maxsplit=1)
        assert source_label in manifest_labels
        assert target_label in manifest_labels


def _assert_summary_lobe_totals_use_only_manifest_lobe_labels(
    summary: str,
    *,
    manifest: dict[str, object],
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = set(baseline_lobes["labels"])
    observed_totals = Counter(row["baseline_lobe_label"] for row in metric_rows)
    summary_totals = _summary_lobe_totals(summary)

    assert summary_totals
    assert set(summary_totals) <= manifest_labels
    assert set(summary_totals) == set(observed_totals)
    assert summary_totals == dict(sorted(observed_totals.items()))


def _assert_summary_lobe_dwell_runs_use_only_manifest_lobe_labels(
    summary: str,
    *,
    manifest: dict[str, object],
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = set(baseline_lobes["labels"])
    observed_dwell_runs = _lobe_dwell_runs(metric_rows)
    summary_dwell_runs = _summary_lobe_dwell_runs(summary)

    assert summary_dwell_runs
    assert set(summary_dwell_runs) <= manifest_labels
    assert set(summary_dwell_runs) == set(observed_dwell_runs)
    assert summary_dwell_runs == dict(sorted(observed_dwell_runs.items()))


def _assert_manifest_lobe_fields_match_metrics_header_and_observed_labels(
    manifest: dict[str, object],
    *,
    metrics_header: list[str],
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    emitted_transition_fields = [
        field
        for field in metrics_header
        if field.startswith("baseline_lobe_") and field != "baseline_lobe_label"
    ]

    assert baseline_lobes["labels"] == list(BASELINE_LOBE_LABELS)
    assert baseline_lobes["transition_fields"] == emitted_transition_fields
    assert emitted_transition_fields == list(BASELINE_LOBE_TRANSITION_FIELDS)
    assert set(row["baseline_lobe_label"] for row in metric_rows) <= set(BASELINE_LOBE_LABELS)


def _assert_manifest_event_types_cover_observed_events(
    manifest: dict[str, object],
    *,
    event_rows: list[dict[str, str]],
) -> None:
    assert event_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    events = model["events"]
    assert isinstance(events, dict)

    manifest_event_types = events["types"]
    assert manifest_event_types == list(BASELINE_EVENT_TYPES)
    assert set(event["event_type"] for event in event_rows) <= set(manifest_event_types)


def _assert_manifest_metrics_fields_match_metrics_header(
    manifest: dict[str, object],
    *,
    metrics_header: list[str],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)
    metrics = model["metrics"]
    assert isinstance(metrics, dict)

    manifest_metrics_fields = metrics["fields"]
    assert manifest_metrics_fields == metrics_header
    assert metrics_header == list(metrics_fieldnames(tuple(manifest["actions"])))


def _assert_manifest_role_action_fields_match_metrics_header_subset(
    manifest: dict[str, object],
    *,
    metrics_header: list[str],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)
    role_action_metrics = model["role_action_metrics"]
    assert isinstance(role_action_metrics, dict)

    emitted_role_action_fields = [
        field for field in metrics_header if field.startswith("role_")
    ]
    manifest_role_action_fields = role_action_metrics["fields"]
    assert manifest_role_action_fields == emitted_role_action_fields
    assert emitted_role_action_fields == list(role_action_metric_fields(tuple(manifest["actions"])))


def _assert_manifest_queue_dynamics_fields_match_metrics_header_subsets(
    manifest: dict[str, object],
    *,
    metrics_header: list[str],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)
    queue_dynamics_metrics = model["queue_dynamics_metrics"]
    assert isinstance(queue_dynamics_metrics, dict)

    emitted_pressure_fields = [
        field for field in metrics_header if field in QUEUE_PRESSURE_METRIC_FIELDS
    ]
    emitted_queued_task_age_fields = [
        field for field in metrics_header if field in QUEUED_TASK_AGE_METRIC_FIELDS
    ]

    assert queue_dynamics_metrics["pressure_fields"] == emitted_pressure_fields
    assert queue_dynamics_metrics["queued_task_age_fields"] == emitted_queued_task_age_fields
    assert emitted_pressure_fields == list(QUEUE_PRESSURE_METRIC_FIELDS)
    assert emitted_queued_task_age_fields == list(QUEUED_TASK_AGE_METRIC_FIELDS)


def _assert_manifest_event_fields_match_events_header(
    manifest: dict[str, object],
    *,
    events_header: list[str],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)
    events = model["events"]
    assert isinstance(events, dict)

    manifest_event_fields = events["fields"]
    assert manifest_event_fields == events_header
    assert events_header == list(EVENT_FIELDS)


def _summary_lobe_transition_totals(summary: str) -> dict[str, int]:
    totals: dict[str, int] = {}
    in_section = False

    for line in summary.splitlines():
        if line == "## Baseline lobe transitions":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- "):
            continue

        transition, count = line.removeprefix("- ").split(": ", maxsplit=1)
        totals[transition] = int(count)

    return totals


def _summary_lobe_totals(summary: str) -> dict[str, int]:
    totals: dict[str, int] = {}
    in_section = False

    for line in summary.splitlines():
        if line == "## Baseline lobe totals":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- "):
            continue

        label, count = line.removeprefix("- ").split(": ", maxsplit=1)
        totals[label] = int(count)

    return totals


def _summary_lobe_dwell_runs(summary: str) -> dict[str, dict[str, int | float]]:
    dwell_runs: dict[str, dict[str, int | float]] = {}
    in_section = False

    for line in summary.splitlines():
        if line == "## Baseline lobe dwell runs":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- "):
            continue

        label, raw_fields = line.removeprefix("- ").split(": ", maxsplit=1)
        fields = dict(field.split("=", maxsplit=1) for field in raw_fields.split(", "))
        dwell_runs[label] = {
            "runs": int(fields["runs"]),
            "total_ticks": int(fields["total_ticks"]),
            "max_run": int(fields["max_run"]),
            "mean_run": float(fields["mean_run"]),
        }

    return dwell_runs


def _summary_role_action_totals(summary: str) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = {}
    in_section = False

    for line in summary.splitlines():
        if line == "## Role action totals":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- "):
            continue

        role, raw_fields = line.removeprefix("- ").split(": ", maxsplit=1)
        fields = dict(field.split("=", maxsplit=1) for field in raw_fields.split(", "))
        totals[role] = {
            "idle": int(fields["idle"]),
            "message": int(fields["message"]),
            "create_task": int(fields["create_task"]),
            "work_task": int(fields["work_task"]),
        }

    return totals


def _lobe_transition_totals_from_adjacent_labels(
    metric_rows: list[dict[str, str]],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    previous_label = metric_rows[0]["baseline_lobe_label"]

    for row in metric_rows[1:]:
        current_label = row["baseline_lobe_label"]
        if previous_label != current_label:
            counts[f"{previous_label}->{current_label}"] += 1
        previous_label = current_label

    return dict(sorted(counts.items()))


def _lobe_transition_sequence(metric_rows: list[dict[str, str]]) -> list[str]:
    return [
        row["baseline_lobe_transition"]
        for row in metric_rows
        if row["baseline_lobe_transition"] not in {"start", "stable"}
    ]


def _lobe_transition_field_sequence(metric_rows: list[dict[str, str]]) -> list[str]:
    return [row["baseline_lobe_transition"] for row in metric_rows]


def _lobe_label_sequence(metric_rows: list[dict[str, str]]) -> list[str]:
    return [row["baseline_lobe_label"] for row in metric_rows]


def _lobe_run_state_sequence(metric_rows: list[dict[str, str]]) -> list[tuple[int, int]]:
    return [
        (
            int(row["baseline_lobe_run_id"]),
            int(row["baseline_lobe_current_run_length"]),
        )
        for row in metric_rows
    ]


def _role_action_metric_sequence(
    metric_rows: list[dict[str, str]],
    actions: tuple[str, ...],
) -> list[tuple[int, ...]]:
    fields = role_action_metric_fields(actions)
    return [
        tuple(int(row[field]) for field in fields)
        for row in metric_rows
    ]


def test_fixed_seed_role_action_totals_are_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "coordinator": {"idle": 58, "message": 102, "create_task": 61, "work_task": 79},
            "researcher": {"idle": 42, "message": 106, "create_task": 57, "work_task": 95},
            "architect": {"idle": 51, "message": 93, "create_task": 82, "work_task": 74},
            "implementer": {"idle": 54, "message": 114, "create_task": 56, "work_task": 76},
            "reviewer": {"idle": 43, "message": 117, "create_task": 63, "work_task": 77},
        },
        2: {
            "coordinator": {"idle": 51, "message": 99, "create_task": 60, "work_task": 90},
            "researcher": {"idle": 54, "message": 95, "create_task": 63, "work_task": 88},
            "architect": {"idle": 69, "message": 94, "create_task": 62, "work_task": 75},
            "implementer": {"idle": 63, "message": 100, "create_task": 76, "work_task": 61},
            "reviewer": {"idle": 52, "message": 104, "create_task": 71, "work_task": 73},
        },
        17: {
            "coordinator": {"idle": 56, "message": 110, "create_task": 72, "work_task": 62},
            "researcher": {"idle": 54, "message": 107, "create_task": 71, "work_task": 68},
            "architect": {"idle": 59, "message": 107, "create_task": 56, "work_task": 78},
            "implementer": {"idle": 53, "message": 102, "create_task": 69, "work_task": 76},
            "reviewer": {"idle": 45, "message": 125, "create_task": 68, "work_task": 62},
        },
    }
    actions = ("idle", "message", "create_task", "work_task")

    observed = {}
    for seed in expected:
        out_dir = tmp_path / f"seed{seed}"
        result = run_experiment(CONFIG, seed=seed, out_dir=out_dir)
        summary = (out_dir / "summary.md").read_text()

        observed[seed] = {
            role: {
                action: sum(int(row[f"role_{role}_{action}_tick"]) for row in result.metrics)
                for action in actions
            }
            for role in BASELINE_ROLES
        }

        for role, totals in expected[seed].items():
            assert (
                f"- {role}: idle={totals['idle']}, message={totals['message']}, "
                f"create_task={totals['create_task']}, work_task={totals['work_task']}"
            ) in summary

    assert observed == expected


def test_fixed_seed_event_type_totals_are_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "agent_idle": 248,
            "message_sent": 532,
            "task_created": 319,
            "task_worked": 401,
        },
        2: {
            "agent_idle": 289,
            "message_sent": 492,
            "task_created": 332,
            "task_worked": 387,
        },
        17: {
            "agent_idle": 267,
            "message_sent": 551,
            "task_created": 336,
            "task_worked": 346,
        },
    }

    observed = {}
    for seed in expected:
        out_dir = tmp_path / f"seed{seed}"
        result = run_experiment(CONFIG, seed=seed, out_dir=out_dir)
        with (out_dir / "events.csv").open() as handle:
            event_rows = list(csv.DictReader(handle))

        observed[seed] = dict(sorted(Counter(event["event_type"] for event in result.events).items()))
        assert dict(sorted(Counter(row["event_type"] for row in event_rows).items())) == expected[seed]
        assert sum(observed[seed].values()) == 1500
        summary = (out_dir / "summary.md").read_text()
        for event_type, count in expected[seed].items():
            assert f"- {event_type}: {count}" in summary

    assert observed == expected
