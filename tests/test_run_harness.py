from __future__ import annotations

from collections import Counter
from pathlib import Path
import csv
import sys

import pytest
import yaml

from ohdyn.sim import BASELINE_LOBE_LABELS, BASELINE_ROLES
from ohdyn.config import load_config
from ohdyn.run import run_experiment


CONFIG = Path("configs/a0_smoke.yaml")


def test_loads_a0_smoke_config() -> None:
    config = load_config(CONFIG)

    assert config.run.experiment_id == "a0_smoke"
    assert config.run.ticks == 100
    assert config.model.agent_count == 15
    assert set(config.model.actions) == {"idle", "message", "create_task", "work_task"}


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


def test_manifest_lists_only_written_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "minimal_outputs.yaml"
    out_dir = tmp_path / "minimal_outputs"
    config_path.write_text(
        """
run:
  experiment_id: minimal_outputs
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_manifest: true
  write_metrics: false
  write_events: false
  write_summary: false
"""
    )

    run_experiment(config_path, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == ["config.yaml", "manifest.yaml"]
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


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

    for artifact in ["manifest.yaml", "config.yaml", "metrics.csv", "events.csv", "summary.md"]:
        assert (first / artifact).read_text() == (second / artifact).read_text()


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
