from __future__ import annotations

from pathlib import Path

import pytest
import yaml

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
    assert (out_dir / "manifest.yaml").is_file()
    assert (out_dir / "metrics.csv").is_file()
    assert (out_dir / "events.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["seed"] == 1
    assert manifest["agent_count"] == 15
    assert manifest["model"]["bus_edges"] == 15


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
