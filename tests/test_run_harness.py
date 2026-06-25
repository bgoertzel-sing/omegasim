from __future__ import annotations

from collections import Counter, deque
from pathlib import Path
import csv
import subprocess
import sys

import pytest
import yaml

from ohdyn.sim import (
    ATTENTION_EVENT_TYPES,
    BASELINE_EVENT_TYPES,
    BASELINE_LOBE_LABELS,
    BASELINE_LOBE_TRANSITION_FIELDS,
    BASELINE_ROLES,
    EVENT_FIELDS,
    EXOGENOUS_ARRIVAL_EVENT_TYPES,
    EXOGENOUS_ARRIVAL_METRIC_FIELDS,
    QUEUE_PRESSURE_METRIC_FIELDS,
    QUEUED_TASK_AGE_METRIC_FIELDS,
    SimulationResult,
    attention_policy_metric_fields,
    metrics_fieldnames,
    role_action_metric_fields,
    simulate,
)
from ohdyn.config import (
    ATTENTION_CLASSES,
    ExogenousArrivalsConfig,
    OmegaConfig,
    load_config,
)
from ohdyn.analyze_pressure import (
    INTERPRETATION_FIELDS,
    PRESSURE_BOOTSTRAP_RANK_STABILITY_FIELDS,
    TRAJECTORY_PRESSURE_RANKING_FIELDS,
    VALUE_YIELD_DIVERGENCE_STABILITY_FIELDS,
    VALUE_YIELD_DIVERGENCE_RANKING_FIELDS,
    _yield_divergence_interpretation,
    run_analysis,
)
from ohdyn.analyze_service_capacity_trajectory import (
    SERVICE_CAPACITY_TRAJECTORY_BOOTSTRAP_FIELDS,
    SERVICE_CAPACITY_TRAJECTORY_EFFECT_FIELDS,
    SERVICE_CAPACITY_TRAJECTORY_FIELDS,
    SERVICE_CAPACITY_TRAJECTORY_NULL_FIELDS,
    run_service_capacity_trajectory_analysis,
)
from ohdyn.analyze_queue_blind_lobes import (
    QUEUE_BLIND_LOBE_EFFECT_FIELDS,
    QUEUE_BLIND_LOBE_FIELDS,
    _queue_blind_label,
    run_queue_blind_lobe_analysis,
)
from ohdyn.compare_attention import run_comparison
from ohdyn.compare_pressure import (
    PRESSURE_COMPARISON_FIELDS,
    PRESSURE_RESPONSE_SELECTION_FIELDS,
    PRESSURE_STABILITY_AGREEMENT_FIELDS,
    PRESSURE_STABILITY_CONVERGENCE_FIELDS,
    PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
    run_pressure_comparison,
)
from ohdyn.compare_service_capacity import (
    SERVICE_CAPACITY_COMPARISON_FIELDS,
    SERVICE_CAPACITY_EFFECT_FIELDS,
    run_service_capacity_comparison,
)
from ohdyn.synthesize_service_capacity_decision import (
    DECISION_SYNTHESIS_FIELDS,
    run_service_capacity_decision_synthesis,
)
from ohdyn.run import run_experiment


CONFIG = Path("configs/a0_smoke.yaml")
A2_ATTENTION = Path("configs/a2_attention_smoke.yaml")
A2_ATTENTION_RANDOM_AVAILABLE = Path("configs/a2_attention_random_available.yaml")
A2_ATTENTION_RESEARCH_HEAVY = Path("configs/a2_attention_research_heavy.yaml")
A2_ATTENTION_INTERNAL_IMPROVEMENT = Path("configs/a2_attention_internal_improvement.yaml")
A2_ATTENTION_MEDIUM_PRESSURE = Path("configs/a2_attention_medium_pressure.yaml")
A2_ATTENTION_RESEARCH_HEAVY_MEDIUM_PRESSURE = Path(
    "configs/a2_attention_research_heavy_medium_pressure.yaml"
)
A2_ATTENTION_INTERNAL_IMPROVEMENT_MEDIUM_PRESSURE = Path(
    "configs/a2_attention_internal_improvement_medium_pressure.yaml"
)
A2_ATTENTION_HIGH_PRESSURE = Path("configs/a2_attention_high_pressure.yaml")
A2_ATTENTION_RANDOM_AVAILABLE_HIGH_PRESSURE = Path(
    "configs/a2_attention_random_available_high_pressure.yaml"
)
A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE = Path(
    "configs/a2_attention_research_heavy_high_pressure.yaml"
)
A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE = Path(
    "configs/a2_attention_internal_improvement_high_pressure.yaml"
)
A2_ATTENTION_EXTREME_PRESSURE = Path("configs/a2_attention_extreme_pressure.yaml")
A2_ATTENTION_LOW_SERVICE_CAPACITY = Path("configs/a2_attention_low_service_capacity.yaml")
A2_ATTENTION_HIGH_SERVICE_CAPACITY = Path("configs/a2_attention_high_service_capacity.yaml")
A2_ATTENTION_LOW_SERVICE_CAPACITY_HIGH_PRESSURE = Path(
    "configs/a2_attention_low_service_capacity_high_pressure.yaml"
)
A2_ATTENTION_HIGH_SERVICE_CAPACITY_HIGH_PRESSURE = Path(
    "configs/a2_attention_high_service_capacity_high_pressure.yaml"
)
A2_ATTENTION_LOW_SERVICE_CAPACITY_EXTREME_PRESSURE = Path(
    "configs/a2_attention_low_service_capacity_extreme_pressure.yaml"
)
A2_ATTENTION_HIGH_SERVICE_CAPACITY_EXTREME_PRESSURE = Path(
    "configs/a2_attention_high_service_capacity_extreme_pressure.yaml"
)
A2_ATTENTION_RANDOM_AVAILABLE_EXTREME_PRESSURE = Path(
    "configs/a2_attention_random_available_extreme_pressure.yaml"
)
A2_ATTENTION_RESEARCH_HEAVY_EXTREME_PRESSURE = Path(
    "configs/a2_attention_research_heavy_extreme_pressure.yaml"
)
A2_ATTENTION_INTERNAL_IMPROVEMENT_EXTREME_PRESSURE = Path(
    "configs/a2_attention_internal_improvement_extreme_pressure.yaml"
)
A2_EXOGENOUS_ARRIVALS = Path("configs/a2_exogenous_arrivals_smoke.yaml")
DEFAULT_OUTPUTS = Path("configs/a0_default_outputs.yaml")
REORDERED_ACTIONS = Path("configs/a0_reordered_actions.yaml")
CONFIG_ONLY = Path("configs/a0_config_only.yaml")
CONFIG_ONLY_REORDERED_ACTIONS = Path("configs/a0_config_only_reordered_actions.yaml")
MANIFEST_ONLY = Path("configs/a0_manifest_only.yaml")
MANIFEST_ONLY_REORDERED_ACTIONS = Path("configs/a0_manifest_only_reordered_actions.yaml")
NO_MANIFEST = Path("configs/a0_no_manifest.yaml")
NO_MANIFEST_REORDERED_ACTIONS = Path("configs/a0_no_manifest_reordered_actions.yaml")
FULL_OUTPUT_FIXTURES = (CONFIG, DEFAULT_OUTPUTS, REORDERED_ACTIONS)
CONFIG_ONLY_FIXTURES = (CONFIG_ONLY, CONFIG_ONLY_REORDERED_ACTIONS)
MANIFEST_ONLY_FIXTURES = (MANIFEST_ONLY, MANIFEST_ONLY_REORDERED_ACTIONS)
NO_MANIFEST_FIXTURES = (NO_MANIFEST, NO_MANIFEST_REORDERED_ACTIONS)

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
    A2_ATTENTION: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RANDOM_AVAILABLE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RESEARCH_HEAVY: A0_FULL_ARTIFACTS,
    A2_ATTENTION_INTERNAL_IMPROVEMENT: A0_FULL_ARTIFACTS,
    A2_ATTENTION_MEDIUM_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RESEARCH_HEAVY_MEDIUM_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_INTERNAL_IMPROVEMENT_MEDIUM_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RANDOM_AVAILABLE_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RANDOM_AVAILABLE_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RESEARCH_HEAVY_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_INTERNAL_IMPROVEMENT_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_LOW_SERVICE_CAPACITY: A0_FULL_ARTIFACTS,
    A2_ATTENTION_HIGH_SERVICE_CAPACITY: A0_FULL_ARTIFACTS,
    A2_ATTENTION_LOW_SERVICE_CAPACITY_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_HIGH_SERVICE_CAPACITY_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_LOW_SERVICE_CAPACITY_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_HIGH_SERVICE_CAPACITY_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_EXOGENOUS_ARRIVALS: A0_FULL_ARTIFACTS,
    DEFAULT_OUTPUTS: A0_FULL_ARTIFACTS,
    REORDERED_ACTIONS: A0_FULL_ARTIFACTS,
    CONFIG_ONLY: CONFIG_ONLY_ARTIFACTS,
    CONFIG_ONLY_REORDERED_ACTIONS: CONFIG_ONLY_ARTIFACTS,
    MANIFEST_ONLY: MANIFEST_ONLY_ARTIFACTS,
    MANIFEST_ONLY_REORDERED_ACTIONS: MANIFEST_ONLY_ARTIFACTS,
    NO_MANIFEST: NO_MANIFEST_ARTIFACTS,
    NO_MANIFEST_REORDERED_ACTIONS: NO_MANIFEST_ARTIFACTS,
}


def _expected_artifacts(config_path: Path) -> list[str]:
    return list(OUTPUT_FIXTURE_ARTIFACTS[config_path])


def _actions_from_normalized_config(normalized_config: dict[str, object]) -> list[str]:
    model = normalized_config["model"]
    assert isinstance(model, dict)
    actions = model["actions"]
    assert isinstance(actions, list)
    return actions


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


def _run_documented_pressure_cli(
    out_dir: Path,
    *,
    seeds: tuple[int, ...] = (1, 2),
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.compare_pressure",
            "--seeds",
            *(str(seed) for seed in seeds),
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


def _run_documented_pressure_analysis_cli(
    pressure_dir: Path,
    out_dir: Path,
    *,
    limit: int = 5,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(out_dir),
            "--limit",
            str(limit),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    return completed


def _run_documented_cli_pair(
    config_path: Path,
    tmp_path: Path,
    *,
    first_seed: int,
    second_seed: int,
    first_name: str,
    second_name: str,
) -> tuple[Path, Path, subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    first = tmp_path / first_name
    second = tmp_path / second_name
    artifacts = _expected_artifacts(config_path)

    first_completed = _run_documented_cli(config_path, first, seed=first_seed)
    second_completed = _run_documented_cli(config_path, second, seed=second_seed)

    _assert_artifacts_match_output_directory(first, artifacts)
    _assert_artifacts_match_output_directory(second, artifacts)
    return first, second, first_completed, second_completed


def test_loads_a0_smoke_config() -> None:
    config = load_config(CONFIG)

    assert config.run.experiment_id == "a0_smoke"
    assert config.run.ticks == 100
    assert config.model.agent_count == 15
    assert config.model.task_creation_pressure == 1.0
    assert config.model.work_service_capacity == 1.0
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


def test_loads_a0_reordered_actions_fixture() -> None:
    config = load_config(REORDERED_ACTIONS)

    assert config.run.experiment_id == "a0_reordered_actions"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("work_task", "create_task", "message", "idle")
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


def test_loads_a0_config_only_reordered_actions_fixture() -> None:
    config = load_config(CONFIG_ONLY_REORDERED_ACTIONS)

    assert config.run.experiment_id == "a0_config_only_reordered_actions"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("work_task", "create_task", "message", "idle")
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


def test_loads_a0_manifest_only_reordered_actions_fixture() -> None:
    config = load_config(MANIFEST_ONLY_REORDERED_ACTIONS)

    assert config.run.experiment_id == "a0_manifest_only_reordered_actions"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("work_task", "create_task", "message", "idle")
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


def test_loads_a0_no_manifest_reordered_actions_fixture() -> None:
    config = load_config(NO_MANIFEST_REORDERED_ACTIONS)

    assert config.run.experiment_id == "a0_no_manifest_reordered_actions"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("work_task", "create_task", "message", "idle")
    assert config.outputs.write_manifest is False
    assert config.outputs.write_metrics is True
    assert config.outputs.write_events is True
    assert config.outputs.write_summary is True


def test_loads_a2_attention_smoke_config() -> None:
    config = load_config(A2_ATTENTION)

    assert config.run.experiment_id == "a2_attention_smoke"
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.attention_policy is not None
    assert config.attention_policy.shares() == {
        "near_term_external": 0.45,
        "long_term_research": 0.25,
        "internal_improvement": 0.2,
        "housekeeping": 0.1,
    }
    assert config.attention_policy.selection_strategy == "quota_balance"


def test_loads_a2_attention_random_available_config() -> None:
    config = load_config(A2_ATTENTION_RANDOM_AVAILABLE)

    assert config.run.experiment_id == "a2_attention_random_available"
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.attention_policy is not None
    assert config.attention_policy.shares() == {
        "near_term_external": 0.45,
        "long_term_research": 0.25,
        "internal_improvement": 0.2,
        "housekeeping": 0.1,
    }
    assert config.attention_policy.selection_strategy == "random_available"


def test_loads_a2_attention_research_heavy_config() -> None:
    config = load_config(A2_ATTENTION_RESEARCH_HEAVY)

    assert config.run.experiment_id == "a2_attention_research_heavy"
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.attention_policy is not None
    assert config.attention_policy.shares() == {
        "near_term_external": 0.2,
        "long_term_research": 0.55,
        "internal_improvement": 0.15,
        "housekeeping": 0.1,
    }


def test_loads_a2_attention_internal_improvement_config() -> None:
    config = load_config(A2_ATTENTION_INTERNAL_IMPROVEMENT)

    assert config.run.experiment_id == "a2_attention_internal_improvement"
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.attention_policy is not None
    assert config.attention_policy.shares() == {
        "near_term_external": 0.2,
        "long_term_research": 0.15,
        "internal_improvement": 0.55,
        "housekeeping": 0.1,
    }


@pytest.mark.parametrize(
    ("config_path", "experiment_id", "task_creation_pressure"),
    [
        (
            A2_ATTENTION_MEDIUM_PRESSURE,
            "a2_attention_medium_pressure",
            1.4,
        ),
        (
            A2_ATTENTION_RESEARCH_HEAVY_MEDIUM_PRESSURE,
            "a2_attention_research_heavy_medium_pressure",
            1.4,
        ),
        (
            A2_ATTENTION_INTERNAL_IMPROVEMENT_MEDIUM_PRESSURE,
            "a2_attention_internal_improvement_medium_pressure",
            1.4,
        ),
        (A2_ATTENTION_HIGH_PRESSURE, "a2_attention_high_pressure", 1.8),
        (
            A2_ATTENTION_RANDOM_AVAILABLE_HIGH_PRESSURE,
            "a2_attention_random_available_high_pressure",
            1.8,
        ),
        (
            A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE,
            "a2_attention_research_heavy_high_pressure",
            1.8,
        ),
        (
            A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE,
            "a2_attention_internal_improvement_high_pressure",
            1.8,
        ),
        (A2_ATTENTION_EXTREME_PRESSURE, "a2_attention_extreme_pressure", 2.2),
        (
            A2_ATTENTION_RANDOM_AVAILABLE_EXTREME_PRESSURE,
            "a2_attention_random_available_extreme_pressure",
            2.2,
        ),
        (
            A2_ATTENTION_RESEARCH_HEAVY_EXTREME_PRESSURE,
            "a2_attention_research_heavy_extreme_pressure",
            2.2,
        ),
        (
            A2_ATTENTION_INTERNAL_IMPROVEMENT_EXTREME_PRESSURE,
            "a2_attention_internal_improvement_extreme_pressure",
            2.2,
        ),
    ],
)
def test_loads_a2_attention_pressure_fixtures(
    config_path: Path,
    experiment_id: str,
    task_creation_pressure: float,
) -> None:
    config = load_config(config_path)

    assert config.run.experiment_id == experiment_id
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.model.task_creation_pressure == task_creation_pressure
    assert config.model.work_service_capacity == 1.0
    assert config.attention_policy is not None


@pytest.mark.parametrize(
    ("config_path", "experiment_id", "task_creation_pressure", "work_service_capacity"),
    [
        (
            A2_ATTENTION_LOW_SERVICE_CAPACITY,
            "a2_attention_low_service_capacity",
            1.0,
            0.7,
        ),
        (
            A2_ATTENTION_HIGH_SERVICE_CAPACITY,
            "a2_attention_high_service_capacity",
            1.0,
            1.3,
        ),
        (
            A2_ATTENTION_LOW_SERVICE_CAPACITY_HIGH_PRESSURE,
            "a2_attention_low_service_capacity_high_pressure",
            1.8,
            0.7,
        ),
        (
            A2_ATTENTION_HIGH_SERVICE_CAPACITY_HIGH_PRESSURE,
            "a2_attention_high_service_capacity_high_pressure",
            1.8,
            1.3,
        ),
        (
            A2_ATTENTION_LOW_SERVICE_CAPACITY_EXTREME_PRESSURE,
            "a2_attention_low_service_capacity_extreme_pressure",
            2.2,
            0.7,
        ),
        (
            A2_ATTENTION_HIGH_SERVICE_CAPACITY_EXTREME_PRESSURE,
            "a2_attention_high_service_capacity_extreme_pressure",
            2.2,
            1.3,
        ),
    ],
)
def test_loads_a2_attention_service_capacity_fixtures(
    config_path: Path,
    experiment_id: str,
    task_creation_pressure: float,
    work_service_capacity: float,
) -> None:
    config = load_config(config_path)

    assert config.run.experiment_id == experiment_id
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.model.task_creation_pressure == task_creation_pressure
    assert config.model.work_service_capacity == work_service_capacity
    assert config.attention_policy is not None
    assert config.attention_policy.selection_strategy == "quota_balance"


def test_loads_a2_exogenous_arrivals_fixture() -> None:
    config = load_config(A2_EXOGENOUS_ARRIVALS)

    assert config.run.experiment_id == "a2_exogenous_arrivals_smoke"
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.model.task_creation_pressure == 1.0
    assert config.model.work_service_capacity == 1.0
    assert config.attention_policy is not None
    assert config.attention_policy.selection_strategy == "quota_balance"
    assert config.exogenous_arrivals is not None
    assert config.exogenous_arrivals.enabled is True
    assert config.exogenous_arrivals.rate_per_tick == 1.0
    assert config.exogenous_arrivals.task_class_shares() == {
        "near_term_external": 0.45,
        "long_term_research": 0.25,
        "internal_improvement": 0.2,
        "housekeeping": 0.1,
    }


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


def test_a2_attention_run_records_policy_metrics_and_summary(tmp_path: Path) -> None:
    out_dir = tmp_path / "a2_attention_seed1"

    result = run_experiment(A2_ATTENTION, seed=1, out_dir=out_dir)

    assert result.config.attention_policy is not None
    assert len(result.metrics) == 12
    with (out_dir / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    assert rows
    assert event_rows
    assert manifest["config"]["attention_policy"] == {
        "near_term_external": 0.45,
        "long_term_research": 0.25,
        "internal_improvement": 0.2,
        "housekeeping": 0.1,
        "selection_strategy": "quota_balance",
    }
    assert manifest["model"]["attention_policy"] == {
        "classes": list(ATTENTION_CLASSES),
        "selection_strategy": "quota_balance",
        "fields": list(attention_policy_metric_fields()),
    }
    assert manifest["model"]["events"]["types"] == list(
        BASELINE_EVENT_TYPES + ATTENTION_EVENT_TYPES
    )
    assert set(attention_policy_metric_fields()) <= set(rows[0])
    assert "## Attention policy totals" in summary
    assert "- attention policy fields: " in summary
    assert "- selection strategy: quota_balance" in summary
    assert "- value-weighted completed work: " in summary
    assert "- value per completed task: " in summary
    assert "- value per work event: " in summary
    assert rows[-1]["attention_value_per_completed_task_total"]
    assert rows[-1]["attention_value_per_work_event_total"]
    for class_name in ATTENTION_CLASSES:
        assert f"attention_{class_name}_queued_tick" in rows[0]
        assert f"attention_{class_name}_worked_total" in rows[0]
        assert f"attention_{class_name}_spent_share_tick" in rows[0]
        assert f"attention_{class_name}_capture_pressure_tick" in rows[0]
        assert f"- {class_name}: target_share=" in summary
        assert "worked=" in summary
        assert "capture_pressure=" in summary
    assert rows[-1]["attention_capture_pressure_max_tick"] == "0.188889"
    capture_events = [
        row for row in event_rows
        if row["event_type"] == "attention_capture_pressure"
    ]
    assert len(capture_events) == 41
    assert capture_events[0]["attention_selected_class"] in ATTENTION_CLASSES
    assert capture_events[0]["attention_pressure_class"] in ATTENTION_CLASSES
    assert float(capture_events[0]["attention_capture_pressure"]) > 0.0
    assert "- max capture pressure: 0.188889" in summary


def test_a2_exogenous_arrivals_run_records_accounting_and_reproduces(
    tmp_path: Path,
) -> None:
    first = run_experiment(
        A2_EXOGENOUS_ARRIVALS,
        seed=23,
        out_dir=tmp_path / "first",
    )
    second = run_experiment(
        A2_EXOGENOUS_ARRIVALS,
        seed=23,
        out_dir=tmp_path / "second",
    )

    with (tmp_path / "first" / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (tmp_path / "first" / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))
    manifest = yaml.safe_load((tmp_path / "first" / "manifest.yaml").read_text())
    summary = (tmp_path / "first" / "summary.md").read_text()

    assert first.metrics == second.metrics
    assert first.events == second.events
    assert (tmp_path / "first" / "metrics.csv").read_text() == (
        tmp_path / "second" / "metrics.csv"
    ).read_text()
    assert set(EXOGENOUS_ARRIVAL_METRIC_FIELDS) <= set(rows[0])
    assert manifest["config"]["exogenous_arrivals"] == {
        "enabled": True,
        "rate_per_tick": 1.0,
        "task_class_shares": {
            "near_term_external": 0.45,
            "long_term_research": 0.25,
            "internal_improvement": 0.2,
            "housekeeping": 0.1,
        },
    }
    assert manifest["model"]["exogenous_arrivals"]["rng_stream"] == {
        "agent_action_stream": "numpy.default_rng(seed)",
        "exogenous_arrival_stream": (
            "numpy.default_rng(SeedSequence([seed, 0xE906E, 0xA2]))"
        ),
        "separated_from_agent_actions": True,
    }
    assert manifest["model"]["exogenous_arrivals"]["event_types"] == list(
        EXOGENOUS_ARRIVAL_EVENT_TYPES
    )
    assert manifest["model"]["exogenous_arrivals"]["fields"] == list(
        EXOGENOUS_ARRIVAL_METRIC_FIELDS
    )
    assert "exogenous_task_arrived" in manifest["model"]["events"]["types"]
    exogenous_events = [
        row for row in event_rows
        if row["event_type"] == "exogenous_task_arrived"
    ]
    assert exogenous_events
    assert exogenous_events[0]["action"] == "exogenous_arrival"
    assert exogenous_events[0]["task_class"] in ATTENTION_CLASSES
    assert int(rows[-1]["exogenous_tasks_created_total"]) == len(exogenous_events)
    assert int(rows[-1]["tasks_created_total"]) == (
        int(rows[-1]["agent_tasks_created_total"])
        + int(rows[-1]["exogenous_tasks_created_total"])
    )
    assert "## Exogenous arrival totals" in summary
    assert "- exogenous tasks: " in summary


def test_a2_exogenous_arrivals_use_independent_rng_stream_for_agent_actions() -> None:
    baseline_config = load_config(A2_ATTENTION)
    exogenous_config = OmegaConfig(
        run=baseline_config.run,
        model=baseline_config.model,
        outputs=baseline_config.outputs,
        attention_policy=baseline_config.attention_policy,
        exogenous_arrivals=ExogenousArrivalsConfig(
            enabled=True,
            rate_per_tick=0.0,
            near_term_external=0.45,
            long_term_research=0.25,
            internal_improvement=0.2,
            housekeeping=0.1,
        ),
    )

    baseline = simulate(baseline_config, seed=17)
    exogenous_zero_rate = simulate(exogenous_config, seed=17)

    assert exogenous_zero_rate.events == baseline.events
    for baseline_row, exogenous_row in zip(
        baseline.metrics,
        exogenous_zero_rate.metrics,
        strict=True,
    ):
        common_fields = set(baseline_row) & set(exogenous_row)
        assert {
            field: exogenous_row[field]
            for field in common_fields
        } == {
            field: baseline_row[field]
            for field in common_fields
        }
        assert exogenous_row["exogenous_tasks_created_tick"] == 0
        assert exogenous_row["agent_tasks_created_tick"] == baseline_row[
            "tasks_created_tick"
        ]


def test_queue_blind_label_uses_agent_created_count_when_available() -> None:
    row = {
        "tasks_worked_tick": "1",
        "tasks_created_tick": "12",
        "agent_tasks_created_tick": "0",
        "messages_sent_tick": "2",
        "idle_tick": "0",
    }

    assert _queue_blind_label(row) == "coordination"


def test_a2_attention_cli_reproduces_metrics_across_same_seed(tmp_path: Path) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        A2_ATTENTION,
        tmp_path,
        first_seed=23,
        second_seed=23,
        first_name="a2_attention_first",
        second_name="a2_attention_second",
    )

    assert (first / "metrics.csv").read_text() == (second / "metrics.csv").read_text()
    assert (first / "events.csv").read_text() == (second / "events.csv").read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_random_available_scheduler_is_seeded_and_distinct(
    tmp_path: Path,
) -> None:
    quota = run_experiment(A2_ATTENTION, seed=23, out_dir=tmp_path / "quota")
    random_first = run_experiment(
        A2_ATTENTION_RANDOM_AVAILABLE,
        seed=23,
        out_dir=tmp_path / "random_first",
    )
    random_second = run_experiment(
        A2_ATTENTION_RANDOM_AVAILABLE,
        seed=23,
        out_dir=tmp_path / "random_second",
    )

    random_manifest = yaml.safe_load((tmp_path / "random_first" / "manifest.yaml").read_text())
    random_summary = (tmp_path / "random_first" / "summary.md").read_text()

    assert random_first.config.attention_policy is not None
    assert random_first.config.attention_policy.selection_strategy == "random_available"
    assert random_first.metrics == random_second.metrics
    assert random_first.events == random_second.events
    assert [event["task_id"] for event in random_first.events if event["event_type"] == "task_worked"] != [
        event["task_id"] for event in quota.events if event["event_type"] == "task_worked"
    ]
    assert random_manifest["model"]["attention_policy"]["selection_strategy"] == "random_available"
    assert random_manifest["config"]["attention_policy"]["selection_strategy"] == "random_available"
    assert "- selection strategy: random_available" in random_summary


def test_a2_attention_comparison_shifts_work_toward_research(tmp_path: Path) -> None:
    smoke = run_experiment(A2_ATTENTION, seed=23, out_dir=tmp_path / "a2_attention_smoke")
    research_heavy = run_experiment(
        A2_ATTENTION_RESEARCH_HEAVY,
        seed=23,
        out_dir=tmp_path / "a2_attention_research_heavy",
    )

    smoke_last = smoke.metrics[-1]
    research_last = research_heavy.metrics[-1]

    assert (
        research_last["attention_long_term_research_completed_total"]
        > smoke_last["attention_long_term_research_completed_total"]
    )
    assert (
        research_last["attention_near_term_external_completed_total"]
        < smoke_last["attention_near_term_external_completed_total"]
    )
    assert (
        research_last["attention_value_weighted_completed_total"]
        < smoke_last["attention_value_weighted_completed_total"]
    )
    assert (
        research_last["queued_task_age_mean_tick"]
        > smoke_last["queued_task_age_mean_tick"]
    )
    assert (
        "## Attention policy totals"
        in (tmp_path / "a2_attention_research_heavy" / "summary.md").read_text()
    )


def test_a2_attention_comparison_runner_writes_aggregate_summary(tmp_path: Path) -> None:
    out_dir = tmp_path / "a2_attention_compare"

    rows = run_comparison(seeds=(1, 2), out_dir=out_dir)

    assert len(rows) == 6
    assert {row["policy"] for row in rows} == {
        "baseline",
        "research_heavy",
        "internal_improvement",
    }
    assert (out_dir / "comparison_metrics.csv").is_file()
    assert (out_dir / "summary.md").is_file()
    for policy in ("baseline", "research_heavy", "internal_improvement"):
        for seed in (1, 2):
            assert (out_dir / f"{policy}_seed{seed}" / "metrics.csv").is_file()

    with (out_dir / "comparison_metrics.csv").open() as handle:
        csv_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(csv_rows) == 6
    assert csv_rows[0]["value_weighted_completed_total"]
    assert csv_rows[0]["value_per_completed_task_total"]
    assert csv_rows[0]["value_per_work_event_total"]
    assert csv_rows[0]["queue_depth_trajectory"].count("|") == 11
    assert csv_rows[0]["queued_task_age_mean_trajectory"].count("|") == 11
    assert csv_rows[0]["value_weighted_completed_total_trajectory"].count("|") == 11
    assert csv_rows[0]["value_per_completed_task_total_trajectory"].count("|") == 11
    assert csv_rows[0]["value_per_work_event_total_trajectory"].count("|") == 11
    assert csv_rows[0]["attention_capture_pressure_max_trajectory"].count("|") == 11
    assert csv_rows[0]["queue_depth_step_deltas"].count("|") == 10
    assert csv_rows[0]["queued_task_age_mean_step_deltas"].count("|") == 10
    assert csv_rows[0]["value_weighted_completed_total_step_deltas"].count("|") == 10
    assert csv_rows[0]["value_per_completed_task_total_step_deltas"].count("|") == 10
    assert csv_rows[0]["value_per_work_event_total_step_deltas"].count("|") == 10
    assert csv_rows[0]["attention_capture_pressure_max_step_deltas"].count("|") == 10
    assert csv_rows[0]["phase_space_regime_dwell_runs"]
    assert csv_rows[0]["phase_space_longest_dwell_label"] in csv_rows[0][
        "phase_space_regime_dwell_runs"
    ]
    assert int(csv_rows[0]["phase_space_longest_dwell_steps"]) >= 1
    assert int(csv_rows[0]["phase_space_turning_point_count"]) >= 0
    assert _step_deltas(csv_rows[0]["queue_depth_trajectory"]) == csv_rows[0][
        "queue_depth_step_deltas"
    ]
    assert _step_deltas(csv_rows[0]["queued_task_age_mean_trajectory"]) == csv_rows[0][
        "queued_task_age_mean_step_deltas"
    ]
    assert _step_deltas(csv_rows[0]["value_weighted_completed_total_trajectory"]) == csv_rows[0][
        "value_weighted_completed_total_step_deltas"
    ]
    assert _step_deltas(csv_rows[0]["value_per_completed_task_total_trajectory"]) == csv_rows[0][
        "value_per_completed_task_total_step_deltas"
    ]
    assert _step_deltas(csv_rows[0]["value_per_work_event_total_trajectory"]) == csv_rows[0][
        "value_per_work_event_total_step_deltas"
    ]
    assert _step_deltas(csv_rows[0]["attention_capture_pressure_max_trajectory"]) == csv_rows[0][
        "attention_capture_pressure_max_step_deltas"
    ]
    assert csv_rows[0]["attention_capture_pressure_max_trajectory"].split("|")[-1] == csv_rows[0][
        "attention_capture_pressure_max_final"
    ]
    assert csv_rows[0]["attention_capture_pressure_peak"] == str(
        max(float(value) for value in csv_rows[0]["attention_capture_pressure_max_trajectory"].split("|"))
    )
    for class_name in ATTENTION_CLASSES:
        trajectory_field = f"{class_name}_completed_total_trajectory"
        assert csv_rows[0][trajectory_field].count("|") == 11
        assert csv_rows[0][trajectory_field].split("|")[-1] == csv_rows[0][
            f"{class_name}_completed_total"
        ]
        worked_trajectory_field = f"{class_name}_worked_total_trajectory"
        assert csv_rows[0][worked_trajectory_field].count("|") == 11
        assert csv_rows[0][worked_trajectory_field].split("|")[-1] == csv_rows[0][
            f"{class_name}_worked_total"
        ]
        capture_trajectory_field = f"{class_name}_capture_pressure_trajectory"
        assert csv_rows[0][capture_trajectory_field].count("|") == 11
    assert "## Policy means" in summary
    assert "## Phase-space regimes" in summary
    assert "## Phase-space regime counts" in summary
    assert "## Phase-space regime distribution deltas vs baseline" in summary
    assert "## Phase-space dwell and turning points" in summary
    assert "## Policy deltas vs baseline" in summary
    assert "trajectory_final_queue_depth_mean=" in summary
    assert "trajectory_final_value_weighted_completed_mean=" in summary
    assert "trajectory_final_value_per_completed_task_mean=" in summary
    assert "trajectory_final_value_per_work_event_mean=" in summary
    assert "capture_pressure_max_final_mean=" in summary
    assert "capture_pressure_mean_over_ticks_mean=" in summary
    assert "capture_pressure_peak_mean=" in summary
    assert "queue_depth_step_delta_mean=" in summary
    assert "queued_task_age_mean_step_delta_mean=" in summary
    assert "value_weighted_step_delta_mean=" in summary
    assert "value_per_completed_task_step_delta_mean=" in summary
    assert "value_per_work_event_step_delta_mean=" in summary
    assert "capture_pressure_max_step_delta_mean=" in summary
    assert (
        "- baseline: label=queue_growth+stale_age_rising+value_throughput_rising, "
        "queue_depth_step_delta_sign=positive, queued_age_step_delta_sign=positive, "
        "value_throughput_step_delta_sign=positive"
    ) in summary
    assert "- baseline: total_steps=22, regime_counts=" in summary
    assert "regime_rates=" in summary
    assert (
        "queue_growth+stale_age_rising+value_throughput_rising:"
    ) in summary
    assert (
        "- research_heavy: total_steps=22, baseline_total_steps=22, "
        "regime_rate_deltas="
    ) in summary
    assert (
        "queue_growth+stale_age_rising+value_throughput_rising:0.045455"
    ) in summary
    assert "regime_count_deltas=" in summary
    assert (
        "- internal_improvement: total_steps=22, baseline_total_steps=22, "
        "regime_rate_deltas="
    ) in summary
    assert "- baseline: runs=2, turning_points_mean=" in summary
    assert "longest_dwell_labels=" in summary
    assert "- research_heavy queue-depth step delta mean: " in summary
    assert "- research_heavy queued-age step delta mean: " in summary
    assert "- research_heavy value-throughput step delta mean: " in summary
    assert "- research_heavy value-yield step delta mean: " in summary
    assert "- research_heavy value-effort step delta mean: " in summary
    assert "- research_heavy mean capture pressure: " in summary
    assert "- research_heavy peak capture pressure mean: " in summary
    assert "- research_heavy long-term research completions mean: " in summary
    assert "- research_heavy long-term research work events mean: " in summary
    assert "- internal_improvement internal-improvement completions mean: " in summary
    assert "- internal_improvement capture-pressure step delta mean: " in summary


def test_a2_attention_comparison_runner_is_reproducible(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_comparison(seeds=(1, 2), out_dir=first)
    run_comparison(seeds=(1, 2), out_dir=second)

    assert (first / "comparison_metrics.csv").read_text() == (
        second / "comparison_metrics.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_attention_comparison_runner_aggregates_research_heavy_shift(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_compare"

    run_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    baseline_research = _mean_csv_metric(
        rows,
        policy="baseline",
        field="long_term_research_completed_total",
    )
    research_heavy_research = _mean_csv_metric(
        rows,
        policy="research_heavy",
        field="long_term_research_completed_total",
    )
    baseline_value = _mean_csv_metric(
        rows,
        policy="baseline",
        field="value_weighted_completed_total",
    )
    research_heavy_value = _mean_csv_metric(
        rows,
        policy="research_heavy",
        field="value_weighted_completed_total",
    )

    assert research_heavy_research > baseline_research
    assert research_heavy_value < baseline_value


def test_a2_attention_comparison_runner_aggregates_internal_improvement_shift(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_compare"

    run_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    baseline_internal = _mean_csv_metric(
        rows,
        policy="baseline",
        field="internal_improvement_completed_total",
    )
    internal_heavy = _mean_csv_metric(
        rows,
        policy="internal_improvement",
        field="internal_improvement_completed_total",
    )
    baseline_near_term = _mean_csv_metric(
        rows,
        policy="baseline",
        field="near_term_external_completed_total",
    )
    internal_heavy_near_term = _mean_csv_metric(
        rows,
        policy="internal_improvement",
        field="near_term_external_completed_total",
    )

    assert internal_heavy > baseline_internal
    assert internal_heavy_near_term < baseline_near_term


def test_a2_attention_high_pressure_increases_creation_pressure(tmp_path: Path) -> None:
    baseline = run_experiment(A2_ATTENTION, seed=23, out_dir=tmp_path / "baseline")
    high_pressure = run_experiment(
        A2_ATTENTION_HIGH_PRESSURE,
        seed=23,
        out_dir=tmp_path / "high_pressure",
    )

    baseline_last = baseline.metrics[-1]
    high_pressure_last = high_pressure.metrics[-1]

    assert high_pressure.config.model.task_creation_pressure == 1.8
    assert (
        high_pressure_last["tasks_created_total"]
        > baseline_last["tasks_created_total"]
    )
    assert high_pressure_last["queue_depth"] > baseline_last["queue_depth"]


def test_a2_attention_medium_pressure_sits_between_normal_and_high_pressure(
    tmp_path: Path,
) -> None:
    normal = run_experiment(A2_ATTENTION, seed=23, out_dir=tmp_path / "normal")
    medium = run_experiment(
        A2_ATTENTION_MEDIUM_PRESSURE,
        seed=23,
        out_dir=tmp_path / "medium",
    )
    high = run_experiment(
        A2_ATTENTION_HIGH_PRESSURE,
        seed=23,
        out_dir=tmp_path / "high",
    )

    normal_last = normal.metrics[-1]
    medium_last = medium.metrics[-1]
    high_last = high.metrics[-1]

    assert medium.config.model.task_creation_pressure == 1.4
    assert (
        normal_last["tasks_created_total"]
        < medium_last["tasks_created_total"]
        < high_last["tasks_created_total"]
    )
    assert normal_last["queue_depth"] < medium_last["queue_depth"] < high_last["queue_depth"]


def test_a2_attention_service_capacity_changes_work_absorption(
    tmp_path: Path,
) -> None:
    low = run_experiment(
        A2_ATTENTION_LOW_SERVICE_CAPACITY_HIGH_PRESSURE,
        seed=23,
        out_dir=tmp_path / "low",
    )
    baseline = run_experiment(
        A2_ATTENTION_HIGH_PRESSURE,
        seed=23,
        out_dir=tmp_path / "baseline",
    )
    high = run_experiment(
        A2_ATTENTION_HIGH_SERVICE_CAPACITY_HIGH_PRESSURE,
        seed=23,
        out_dir=tmp_path / "high",
    )

    low_work = sum(int(row["tasks_worked_tick"]) for row in low.metrics)
    baseline_work = sum(int(row["tasks_worked_tick"]) for row in baseline.metrics)
    high_work = sum(int(row["tasks_worked_tick"]) for row in high.metrics)

    assert low.config.model.work_service_capacity == 0.7
    assert baseline.config.model.work_service_capacity == 1.0
    assert high.config.model.work_service_capacity == 1.3
    assert low_work < baseline_work < high_work
    assert low.metrics[-1]["queue_depth"] > baseline.metrics[-1]["queue_depth"] > high.metrics[-1]["queue_depth"]


def test_a2_service_capacity_comparison_runner_writes_grid_summary(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_service_capacity_compare"

    rows = run_service_capacity_comparison(seeds=(1, 2), out_dir=out_dir)

    assert len(rows) == 9
    assert {
        (row["task_creation_pressure"], row["work_service_capacity"])
        for row in rows
    } == {
        (1.0, 0.7),
        (1.0, 1.0),
        (1.0, 1.3),
        (1.8, 0.7),
        (1.8, 1.0),
        (1.8, 1.3),
        (2.2, 0.7),
        (2.2, 1.0),
        (2.2, 1.3),
    }
    assert (out_dir / "service_capacity_comparison_metrics.csv").is_file()
    assert (out_dir / "service_capacity_effects.csv").is_file()
    assert (out_dir / "summary.md").is_file()
    assert (out_dir / "normal_pressure_low_service_seed1" / "metrics.csv").is_file()
    assert (
        out_dir / "extreme_pressure_high_service_seed2" / "summary.md"
    ).is_file()

    with (out_dir / "service_capacity_comparison_metrics.csv").open() as handle:
        csv_rows = list(csv.DictReader(handle))
    with (out_dir / "service_capacity_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(csv_rows) == 9
    assert len(effect_rows) == 6
    assert {
        (row["effect_axis"], row["fixed_label"])
        for row in effect_rows
    } == {
        ("service_capacity", "normal_pressure"),
        ("service_capacity", "high_pressure"),
        ("service_capacity", "extreme_pressure"),
        ("task_creation_pressure", "low_service"),
        ("task_creation_pressure", "baseline_service"),
        ("task_creation_pressure", "high_service"),
    }
    assert effect_rows[0]["queue_depth_per_created_task_mean_delta"]
    assert effect_rows[0]["baseline_lobe_longest_dwell_ticks_mean_delta"]
    assert csv_rows[0]["queue_depth_per_created_task_mean"]
    assert csv_rows[0]["queue_depth_per_created_completed_balance_mean"]
    assert csv_rows[0]["value_per_work_event_mean"]
    assert csv_rows[0]["attention_capture_pressure_peak_mean"]
    assert csv_rows[0]["baseline_lobe_transition_count_mean"]
    assert csv_rows[0]["baseline_lobe_longest_dwell_label_counts"]
    assert "## Load-normalized backlog" in summary
    assert "## Queue age, value, and capture pressure" in summary
    assert "## Baseline lobe transition and dwell" in summary
    assert "## Fixed-pressure service-capacity effects" in summary
    assert "## Fixed-service demand-pressure effects" in summary
    assert "## Interpretation" in summary


def test_a2_service_capacity_comparison_metrics_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_service_capacity_compare"

    run_service_capacity_comparison(seeds=(1,), out_dir=out_dir)

    with (out_dir / "service_capacity_comparison_metrics.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_COMPARISON_FIELDS)

    with (out_dir / "service_capacity_effects.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_EFFECT_FIELDS)


def test_a2_service_capacity_comparison_runner_is_reproducible(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=first)
    run_service_capacity_comparison(seeds=(1, 2), out_dir=second)

    assert (first / "service_capacity_comparison_metrics.csv").read_text() == (
        second / "service_capacity_comparison_metrics.csv"
    ).read_text()
    assert (first / "service_capacity_effects.csv").read_text() == (
        second / "service_capacity_effects.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_service_capacity_trajectory_analysis_writes_grid_summary(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    out_dir = tmp_path / "a2_service_capacity_trajectory"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=source_dir)
    rows = run_service_capacity_trajectory_analysis(
        service_capacity_dir=source_dir,
        out_dir=out_dir,
    )

    assert len(rows) == 9
    assert (out_dir / "service_capacity_trajectory_metrics.csv").is_file()
    assert (out_dir / "service_capacity_trajectory_effects.csv").is_file()
    assert (out_dir / "service_capacity_trajectory_bootstrap.csv").is_file()
    assert (out_dir / "service_capacity_trajectory_nulls.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "service_capacity_trajectory_metrics.csv").open() as handle:
        trajectory_rows = list(csv.DictReader(handle))
    with (out_dir / "service_capacity_trajectory_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    with (out_dir / "service_capacity_trajectory_bootstrap.csv").open() as handle:
        bootstrap_rows = list(csv.DictReader(handle))
    with (out_dir / "service_capacity_trajectory_nulls.csv").open() as handle:
        null_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(trajectory_rows) == 9
    assert len(effect_rows) == 6
    assert len(bootstrap_rows) == 30
    assert len(null_rows) == 9
    assert trajectory_rows[0]["transition_entropy_mean"]
    assert trajectory_rows[0]["transition_entropy_normalized_mean"]
    assert trajectory_rows[0]["dwell_length_histogram"]
    assert trajectory_rows[0]["transition_pair_counts"]
    assert effect_rows[0]["backlog_growth_dwell_share_mean_delta"]
    assert bootstrap_rows[0]["ci_low"]
    assert bootstrap_rows[0]["ci_high"]
    assert bootstrap_rows[0]["sign_stability"]
    assert null_rows[0]["transition_entropy_observed_minus_null"]
    assert null_rows[0]["dwell_length_max_observed_minus_null"]
    assert "## Grid trajectory metrics" in summary
    assert "## Fixed-pressure service-capacity trajectory effects" in summary
    assert "## Fixed-service demand-pressure trajectory effects" in summary
    assert "## Paired bootstrap uncertainty" in summary
    assert "## Label-count null control" in summary


def test_a2_service_capacity_trajectory_analysis_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    out_dir = tmp_path / "a2_service_capacity_trajectory"

    run_service_capacity_comparison(seeds=(1,), out_dir=source_dir)
    run_service_capacity_trajectory_analysis(
        service_capacity_dir=source_dir,
        out_dir=out_dir,
    )

    with (out_dir / "service_capacity_trajectory_metrics.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_TRAJECTORY_FIELDS)

    with (out_dir / "service_capacity_trajectory_effects.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_TRAJECTORY_EFFECT_FIELDS)

    with (out_dir / "service_capacity_trajectory_bootstrap.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_TRAJECTORY_BOOTSTRAP_FIELDS)

    with (out_dir / "service_capacity_trajectory_nulls.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_TRAJECTORY_NULL_FIELDS)


def test_a2_service_capacity_trajectory_analysis_is_reproducible(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=source_dir)
    run_service_capacity_trajectory_analysis(
        service_capacity_dir=source_dir,
        out_dir=first,
    )
    run_service_capacity_trajectory_analysis(
        service_capacity_dir=source_dir,
        out_dir=second,
    )

    assert (first / "service_capacity_trajectory_metrics.csv").read_text() == (
        second / "service_capacity_trajectory_metrics.csv"
    ).read_text()
    assert (first / "service_capacity_trajectory_effects.csv").read_text() == (
        second / "service_capacity_trajectory_effects.csv"
    ).read_text()
    assert (first / "service_capacity_trajectory_bootstrap.csv").read_text() == (
        second / "service_capacity_trajectory_bootstrap.csv"
    ).read_text()
    assert (first / "service_capacity_trajectory_nulls.csv").read_text() == (
        second / "service_capacity_trajectory_nulls.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_queue_blind_lobe_analysis_writes_grid_summary(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    out_dir = tmp_path / "a2_queue_blind_lobes"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=source_dir)
    rows = run_queue_blind_lobe_analysis(
        service_capacity_dir=source_dir,
        out_dir=out_dir,
    )

    assert len(rows) == 9
    assert (out_dir / "queue_blind_lobe_metrics.csv").is_file()
    assert (out_dir / "queue_blind_lobe_effects.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "queue_blind_lobe_metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "queue_blind_lobe_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(metric_rows) == 9
    assert len(effect_rows) == 6
    assert metric_rows[0]["transition_entropy_mean"]
    assert metric_rows[0]["task_generation_dwell_share_mean"]
    assert metric_rows[0]["execution_dwell_share_mean"]
    assert metric_rows[0]["dominant_queue_blind_lobe_counts"]
    assert effect_rows[0]["task_generation_dwell_share_mean_delta"]
    assert effect_rows[0]["execution_dwell_share_mean_delta"]
    assert "## Grid queue-blind lobe metrics" in summary
    assert "## Fixed-service pressure queue-blind effects" in summary
    assert "excluded inputs: queue_depth, queue_delta_tick, baseline_lobe_label" in summary


def test_a2_queue_blind_lobe_analysis_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    out_dir = tmp_path / "a2_queue_blind_lobes"

    run_service_capacity_comparison(seeds=(1,), out_dir=source_dir)
    run_queue_blind_lobe_analysis(
        service_capacity_dir=source_dir,
        out_dir=out_dir,
    )

    with (out_dir / "queue_blind_lobe_metrics.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(QUEUE_BLIND_LOBE_FIELDS)

    with (out_dir / "queue_blind_lobe_effects.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(QUEUE_BLIND_LOBE_EFFECT_FIELDS)


def test_a2_queue_blind_lobe_analysis_is_reproducible(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=source_dir)
    run_queue_blind_lobe_analysis(service_capacity_dir=source_dir, out_dir=first)
    run_queue_blind_lobe_analysis(service_capacity_dir=source_dir, out_dir=second)

    assert (first / "queue_blind_lobe_metrics.csv").read_text() == (
        second / "queue_blind_lobe_metrics.csv"
    ).read_text()
    assert (first / "queue_blind_lobe_effects.csv").read_text() == (
        second / "queue_blind_lobe_effects.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_service_capacity_decision_synthesis_adds_action_accounting_panel(
    tmp_path: Path,
) -> None:
    service_dir = tmp_path / "a2_service_capacity_compare"
    trajectory_dir = tmp_path / "a2_service_capacity_trajectory"
    out_md = tmp_path / "decision_synthesis.md"
    out_csv = tmp_path / "decision_synthesis.csv"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=service_dir)
    run_service_capacity_trajectory_analysis(
        service_capacity_dir=service_dir,
        out_dir=trajectory_dir,
    )
    rows = run_service_capacity_decision_synthesis(
        service_capacity_dir=service_dir,
        trajectory_dir=trajectory_dir,
        out_md=out_md,
        out_csv=out_csv,
    )

    assert len(rows) == 5
    with out_csv.open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(DECISION_SYNTHESIS_FIELDS)
    summary = out_md.read_text()

    assert "# A2 service-capacity decision synthesis" in summary
    assert "## Load/action accounting panel" in summary
    assert "| normal_pressure | low_service |" in summary
    assert "Create actions" in summary
    assert "Work events" in summary
    assert "paired bootstrap rows: 30" in summary
    assert "strongest observed-minus-null dwell locking" in summary


def test_a2_attention_high_pressure_comparison_runner_is_reproducible(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_comparison(
        baseline_config=A2_ATTENTION_HIGH_PRESSURE,
        variant_config=A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE,
        internal_improvement_config=A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE,
        seeds=(1, 2),
        out_dir=first,
    )
    run_comparison(
        baseline_config=A2_ATTENTION_HIGH_PRESSURE,
        variant_config=A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE,
        internal_improvement_config=A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE,
        seeds=(1, 2),
        out_dir=second,
    )

    assert (first / "comparison_metrics.csv").read_text() == (
        second / "comparison_metrics.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()
    summary = (first / "summary.md").read_text()
    assert "configs/a2_attention_high_pressure.yaml" in summary
    assert "## Phase-space regime distribution deltas vs baseline" in summary


def test_a2_attention_pressure_comparison_runner_writes_fixed_policy_deltas(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    rows = run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    assert len(rows) == 3
    assert {row["policy"] for row in rows} == {
        "baseline",
        "research_heavy",
        "internal_improvement",
    }
    assert (out_dir / "normal_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "medium_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "high_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "pressure_comparison_metrics.csv").is_file()
    assert (out_dir / "pressure_response_selection.csv").is_file()
    assert (out_dir / "pressure_stability_agreement.csv").is_file()
    assert (out_dir / "pressure_stability_convergence.csv").is_file()
    assert (out_dir / "pressure_trajectory_structure.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        csv_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(csv_rows) == 3
    assert csv_rows[0]["normal_total_steps"] == "22"
    assert csv_rows[0]["medium_pressure_total_steps"] == "22"
    assert csv_rows[0]["high_pressure_total_steps"] == "22"
    assert csv_rows[0]["regime_rate_deltas"]
    assert csv_rows[0]["regime_count_deltas"]
    assert csv_rows[0]["queue_depth_mean_delta"]
    assert csv_rows[0]["value_per_completed_task_mean_delta"]
    assert csv_rows[0]["value_per_work_event_mean_delta"]
    assert csv_rows[0]["queue_depth_normal_to_medium_slope"]
    assert csv_rows[0]["queue_depth_medium_to_high_slope"]
    assert csv_rows[0]["queue_depth_pressure_curvature"]
    assert csv_rows[0]["value_per_completed_task_normal_to_medium_slope"]
    assert csv_rows[0]["value_per_completed_task_medium_to_high_slope"]
    assert csv_rows[0]["value_per_completed_task_pressure_curvature"]
    assert csv_rows[0]["value_per_work_event_normal_to_medium_slope"]
    assert csv_rows[0]["value_per_work_event_medium_to_high_slope"]
    assert csv_rows[0]["value_per_work_event_pressure_curvature"]
    assert csv_rows[0]["attention_capture_pressure_max_final_delta"]
    assert csv_rows[0]["attention_capture_pressure_mean_over_ticks_delta"]
    assert csv_rows[0]["attention_capture_pressure_peak_delta"]
    assert csv_rows[0]["attention_capture_pressure_max_final_normal_to_medium_slope"]
    assert csv_rows[0]["attention_capture_pressure_max_final_medium_to_high_slope"]
    assert csv_rows[0]["attention_capture_pressure_max_final_pressure_curvature"]
    assert csv_rows[0]["near_term_external_capture_pressure_final_delta"]
    assert csv_rows[0]["near_term_external_capture_pressure_mean_over_ticks_delta"]
    assert csv_rows[0]["near_term_external_capture_pressure_peak_delta"]
    assert csv_rows[0]["near_term_external_capture_pressure_final_normal_to_medium_slope"]
    assert csv_rows[0]["near_term_external_capture_pressure_final_medium_to_high_slope"]
    assert csv_rows[0]["near_term_external_capture_pressure_final_pressure_curvature"]
    assert "## Fixed-policy pressure deltas" in summary
    assert "## Most pressure-sensitive curve metric" in summary
    assert "## Pressure-curve response ranking" in summary
    assert "## Pressure-condition trajectory structure" in summary
    assert "## Value throughput vs effort interpretation" in summary
    assert "## Per-class capture-pressure interpretation" in summary
    assert "## Fixed-policy pressure curves" in summary
    assert (
        "- baseline: normal_total_steps=22, medium_pressure_total_steps=22, "
        "high_pressure_total_steps=22, "
    ) in summary
    assert "regime_rate_deltas=" in summary
    assert "- research_heavy final queue depth mean pressure delta: " in summary
    assert "- research_heavy value per completed task mean pressure delta: " in summary
    assert "- research_heavy value per work event mean pressure delta: " in summary
    assert "- baseline: value_throughput normal=" in summary
    assert "value_per_completed_task normal=" in summary
    assert "value_per_work_event normal=" in summary
    assert "- baseline reading: pressure " in summary
    assert "- internal_improvement peak queued task max age pressure delta: " in summary
    assert "- baseline final attention capture pressure delta: " in summary
    assert "- baseline mean attention capture pressure delta: " in summary
    assert "- baseline peak attention capture pressure delta: " in summary
    assert "- baseline near term external final capture pressure delta: " in summary
    assert "- baseline near term external mean capture pressure delta: " in summary
    assert "- baseline near term external peak capture pressure delta: " in summary
    assert "- baseline final queue depth pressure curve: " in summary
    assert "- baseline value per completed task pressure curve: " in summary
    assert "- baseline value per work event pressure curve: " in summary
    assert "- baseline final attention capture pressure curve: " in summary
    assert "- baseline mean attention capture pressure curve: " in summary
    assert "- baseline peak attention capture pressure curve: " in summary
    assert "- baseline near term external final capture pressure curve: " in summary
    assert "- baseline near term external mean capture pressure curve: " in summary
    assert "- baseline near term external peak capture pressure curve: " in summary
    assert "- baseline: turning_points_mean normal=" in summary
    assert "- baseline: longest_dwell_steps_mean normal=" in summary
    assert "- baseline: longest_dwell_labels normal=" in summary
    assert "normal_to_medium_slope=" in summary
    assert "medium_to_high_slope=" in summary
    assert "curvature=" in summary


def test_a2_attention_pressure_summary_includes_trajectory_structure(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "normal_pressure" / "comparison_metrics.csv").open() as handle:
        normal_rows = list(csv.DictReader(handle))

    baseline_rows = [row for row in normal_rows if row["policy"] == "baseline"]
    expected_turning_mean = round(
        sum(float(row["phase_space_turning_point_count"]) for row in baseline_rows)
        / len(baseline_rows),
        6,
    )
    expected_dwell_mean = round(
        sum(float(row["phase_space_longest_dwell_steps"]) for row in baseline_rows)
        / len(baseline_rows),
        6,
    )

    assert "## Pressure-condition trajectory structure" in summary
    assert f"- baseline: turning_points_mean normal={expected_turning_mean}" in summary
    assert f"- baseline: longest_dwell_steps_mean normal={expected_dwell_mean}" in summary
    for policy in ("baseline", "research_heavy", "internal_improvement"):
        assert f"- {policy}: longest_dwell_labels normal=" in summary


def test_a2_attention_pressure_trajectory_structure_csv_matches_condition_rows(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_trajectory_structure.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (out_dir / "normal_pressure" / "comparison_metrics.csv").open() as handle:
        normal_rows = list(csv.DictReader(handle))
    with (out_dir / "medium_pressure" / "comparison_metrics.csv").open() as handle:
        medium_rows = list(csv.DictReader(handle))
    with (out_dir / "high_pressure" / "comparison_metrics.csv").open() as handle:
        high_rows = list(csv.DictReader(handle))

    assert rows
    assert list(rows[0]) == list(PRESSURE_TRAJECTORY_STRUCTURE_FIELDS)
    assert [row["policy"] for row in rows] == [
        "baseline",
        "research_heavy",
        "internal_improvement",
    ]

    baseline = rows[0]
    normal_summary = _trajectory_structure_summary_from_csv(normal_rows, "baseline")
    medium_summary = _trajectory_structure_summary_from_csv(medium_rows, "baseline")
    high_summary = _trajectory_structure_summary_from_csv(high_rows, "baseline")

    assert baseline["normal_turning_points_mean"] == str(
        normal_summary["turning_points_mean"]
    )
    assert baseline["medium_pressure_turning_points_mean"] == str(
        medium_summary["turning_points_mean"]
    )
    assert baseline["high_pressure_turning_points_mean"] == str(
        high_summary["turning_points_mean"]
    )
    assert baseline["turning_points_high_minus_normal_delta"] == str(
        round(
            high_summary["turning_points_mean"]
            - normal_summary["turning_points_mean"],
            6,
        )
    )
    assert baseline["normal_longest_dwell_steps_mean"] == str(
        normal_summary["longest_dwell_steps_mean"]
    )
    assert baseline["medium_pressure_longest_dwell_steps_mean"] == str(
        medium_summary["longest_dwell_steps_mean"]
    )
    assert baseline["high_pressure_longest_dwell_steps_mean"] == str(
        high_summary["longest_dwell_steps_mean"]
    )
    assert baseline["longest_dwell_steps_high_minus_normal_delta"] == str(
        round(
            high_summary["longest_dwell_steps_mean"]
            - normal_summary["longest_dwell_steps_mean"],
            6,
        )
    )
    assert baseline["normal_longest_dwell_label_counts"] == normal_summary[
        "longest_dwell_labels"
    ]
    assert baseline["medium_pressure_longest_dwell_label_counts"] == medium_summary[
        "longest_dwell_labels"
    ]
    assert baseline["high_pressure_longest_dwell_label_counts"] == high_summary[
        "longest_dwell_labels"
    ]


def test_a2_attention_pressure_summary_interprets_per_class_capture_pressure(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()
    class_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if "_capture_pressure_" in field
        and any(field.startswith(f"{class_name}_") for class_name in ATTENTION_CLASSES)
        and field.endswith(
            (
                "_normal_to_medium_slope",
                "_medium_to_high_slope",
                "_pressure_curvature",
            )
        )
    ]
    candidates = [
        (
            -abs(float(row[field])),
            row["policy"],
            field,
            float(row[field]),
        )
        for row in rows
        for field in class_fields
    ]
    _, expected_policy, expected_field, _ = sorted(candidates)[0]
    expected_class = next(
        class_name
        for class_name in ATTENTION_CLASSES
        if expected_field.startswith(f"{class_name}_capture_pressure_")
    )
    statistic_and_metric = expected_field.removeprefix(
        f"{expected_class}_capture_pressure_"
    )
    metric_labels = {
        "normal_to_medium_slope": "normal_to_medium_slope",
        "medium_to_high_slope": "medium_to_high_slope",
        "pressure_curvature": "curvature",
    }
    expected_metric_suffix = next(
        suffix
        for suffix in metric_labels
        if statistic_and_metric.endswith(f"_{suffix}")
    )
    statistic = statistic_and_metric.removesuffix(f"_{expected_metric_suffix}")

    assert "## Per-class capture-pressure interpretation" in summary
    assert (
        f"- overall class response: policy={expected_policy}, "
        f"class={expected_class.replace('_', ' ')}, "
        f"statistic={statistic.replace('_', ' ')}, "
    ) in summary
    assert f"metric={metric_labels[expected_metric_suffix]}; condition means move " in summary
    for policy in ("baseline", "research_heavy", "internal_improvement"):
        assert f"- {policy} class response: policy={policy}, " in summary


def test_a2_attention_pressure_summary_compares_per_class_prefix_responses(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"
    readme = Path("README.md").read_text()

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()
    class_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if "_capture_pressure_" in field
        and any(field.startswith(f"{class_name}_") for class_name in ATTENTION_CLASSES)
        and field.endswith(
            (
                "_normal_to_medium_slope",
                "_medium_to_high_slope",
                "_pressure_curvature",
            )
        )
    ]
    candidates = [
        (
            -abs(float(row[field])),
            row["policy"],
            field,
            float(row[field]),
        )
        for row in rows
        for field in class_fields
    ]
    _, expected_policy, expected_field, expected_value = sorted(candidates)[0]

    assert "`Per-class capture-pressure prefix comparison`" in readme
    assert "class-specific pressure-response ranking" in readme
    assert "## Per-class capture-pressure prefix comparison" in summary
    assert "- comparison: full_seeds=1,2,3, prefix_seeds=1,2" in summary
    assert (
        f"- full class top response: policy={expected_policy}, "
    ) in summary
    assert f"field={expected_field}" in summary
    assert f"value={round(expected_value, 6)}" in summary
    assert "- class top response stable across prefix: " in summary
    assert "- class top response stable across all prefixes: " in summary
    assert "- class prefix instability causes: " in summary
    assert (
        "| prefix_seeds | class_top_response | stable_with_full | "
        "instability_causes |"
    ) in summary
    assert "| 1 | policy=" in summary
    assert "| 1,2 | policy=" in summary


def test_a2_attention_pressure_summary_identifies_most_sensitive_curve_metric(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()
    curve_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if field.endswith(
            (
                "_normal_to_medium_slope",
                "_medium_to_high_slope",
                "_pressure_curvature",
            )
        )
    ]
    candidates = [
        (
            -abs(float(row[field])),
            row["policy"],
            field,
            float(row[field]),
        )
        for row in rows
        for field in curve_fields
    ]
    _, expected_policy, expected_field, expected_value = sorted(candidates)[0]

    assert "## Most pressure-sensitive curve metric" in summary
    assert f"policy={expected_policy}" in summary
    assert f"field={expected_field}" in summary
    assert f"value={round(expected_value, 6)}" in summary
    assert f"abs_value={round(abs(expected_value), 6)}" in summary


def test_a2_attention_pressure_summary_ranks_all_curve_responses(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()
    curve_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if field.endswith(
            (
                "_normal_to_medium_slope",
                "_medium_to_high_slope",
                "_pressure_curvature",
            )
        )
    ]
    candidates = [
        (
            -abs(float(row[field])),
            row["policy"],
            field,
            float(row[field]),
        )
        for row in rows
        for field in curve_fields
    ]
    _, expected_policy, expected_field, expected_value = sorted(candidates)[0]
    ranking_section = summary.split("## Pressure-curve response ranking", maxsplit=1)[1]
    ranking_section = ranking_section.split("## Top pressure-response explanation", maxsplit=1)[0]
    table_lines = [
        line
        for line in ranking_section.splitlines()
        if line.startswith("| ") and not line.startswith("| ---")
    ]

    assert "## Pressure-curve response ranking" in summary
    assert table_lines[0] == (
        "| rank | policy | observable | metric | field | value | abs_value |"
    )
    assert len(table_lines) == len(candidates) + 1
    assert table_lines[1].startswith(
        f"| 1 | {expected_policy} | "
    )
    assert f" | {expected_field} | " in table_lines[1]
    assert f" | {round(expected_value, 6)} | " in table_lines[1]
    assert f" | {round(abs(expected_value), 6)} |" in table_lines[1]


def test_a2_attention_pressure_summary_explains_top_curve_response(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()
    curve_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if field.endswith(
            (
                "_normal_to_medium_slope",
                "_medium_to_high_slope",
                "_pressure_curvature",
            )
        )
    ]
    candidates = [
        (
            -abs(float(row[field])),
            row["policy"],
            field,
            float(row[field]),
        )
        for row in rows
        for field in curve_fields
    ]
    _, expected_policy, expected_field, _ = sorted(candidates)[0]
    observable_source_fields = {
        "value_weighted_completed": "value_weighted_completed_total",
        "tasks_completed": "tasks_completed_total",
        "queue_depth": "queue_depth",
        "queued_task_age_mean_final": "queued_task_age_mean_final",
        "queued_task_age_max_peak": "queued_task_age_max_peak",
        "attention_capture_pressure_max_final": "attention_capture_pressure_max_final",
        "attention_capture_pressure_mean_over_ticks": (
            "attention_capture_pressure_mean_over_ticks"
        ),
        "attention_capture_pressure_peak": "attention_capture_pressure_peak",
    }
    expected_prefix = next(
        prefix
        for prefix in observable_source_fields
        if expected_field.startswith(f"{prefix}_")
    )
    source_field = observable_source_fields[expected_prefix]
    condition_means = {}
    for condition in ("normal_pressure", "medium_pressure", "high_pressure"):
        with (out_dir / condition / "comparison_metrics.csv").open() as handle:
            condition_rows = [
                row for row in csv.DictReader(handle)
                if row["policy"] == expected_policy
            ]
        condition_means[condition] = _mean_csv_metric(
            condition_rows,
            policy=expected_policy,
            field=source_field,
        )

    assert "## Top pressure-response explanation" in summary
    assert (
        f"- selected response: policy={expected_policy}, "
    ) in summary
    assert f"field={expected_field}" in summary
    assert (
        f"- condition means: normal={round(condition_means['normal_pressure'], 6)}, "
        f"medium_pressure={round(condition_means['medium_pressure'], 6)}, "
        f"high_pressure={round(condition_means['high_pressure'], 6)}"
    ) in summary


def test_a2_attention_pressure_summary_interprets_unstable_prefix_response(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()

    assert "## Pressure-response interpretation" in summary
    assert (
        "- full-seed interpretation: policy=internal_improvement "
        "observable=final queue depth metric=normal_to_medium_slope "
        "is the largest absolute pressure response; condition means move"
    ) in summary
    assert "normal_to_medium_slope=46.666665" in summary
    assert "medium_to_high_slope=15.833335" in summary
    assert "curvature=-30.83333" in summary
    assert "high_minus_normal_delta=25.0" in summary
    assert (
        "- prefix interpretation: instability causes=policy,observable,metric "
        "because prefix_seeds=1,2 select policy=baseline "
        "observable=value-weighted completed work metric=curvature "
        "with condition means"
    ) in summary
    assert (
        "the full seed set selects policy=internal_improvement "
        "observable=final queue depth metric=normal_to_medium_slope."
    ) in summary


def test_a2_attention_pressure_summary_compares_selected_source_metric_by_condition(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"
    readme = Path("README.md").read_text()

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()

    assert "`Pressure-condition source metric comparison`" in readme
    assert "source metric behind the selected top pressure response" in readme
    assert "## Pressure-condition source metric comparison" in summary
    assert (
        "- selected source metric: policy=internal_improvement "
        "observable=final queue depth metric=normal_to_medium_slope "
        "source_field=queue_depth"
    ) in summary
    assert (
        "| pressure_condition | source_metric_mean | source_metric_min | "
        "source_metric_max | per_seed_values |"
    ) in summary
    assert "| normal | 20.666667 | " in summary
    assert "| medium | 39.333333 | " in summary
    assert "| high | 45.666667 | " in summary
    assert "1:" in summary
    assert "2:" in summary
    assert "3:" in summary


def test_a2_attention_pressure_summary_interprets_stable_prefix_response(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"
    readme = Path("README.md").read_text()

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()

    assert "`Pressure-response interpretation` restates the full seed set" in readme
    assert "Stable prefixes report that the leading explanation is stable" in readme
    assert "## Pressure-response interpretation" in summary
    assert (
        "- full-seed interpretation: policy=baseline "
        "observable=value-weighted completed work metric=curvature "
        "is the largest absolute pressure response; condition means move "
        "56.5 -> 45.0 -> 57.5 with normal_to_medium_slope=-28.75, "
        "medium_to_high_slope=31.25, curvature=60.0, and "
        "high_minus_normal_delta=1.0."
    ) in summary
    assert (
        "- prefix interpretation: the last prefix selects the same policy, "
        "observable, and metric, so the leading pressure-response explanation "
        "is stable for the checked prefix."
    ) in summary


def test_a2_attention_pressure_summary_reports_seed_set_sensitivity(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"
    readme = Path("README.md").read_text()

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()

    assert "`Seed-set sensitivity` is a deterministic prefix check" in readme
    assert "`full_seeds` is `1,2,3` and `prefix_seeds` is `1,2`" in readme
    assert "a prefix table for every proper prefix of the configured seed set" in readme
    assert "`top response stable across prefix: true`" in readme
    assert "`top response stable across all prefixes: true`" in readme
    assert "`prefix instability causes` reports which top-response dimensions changed" in readme
    assert "pressure-response ranking should be treated as seed-set-sensitive" in readme
    assert "## Seed-set sensitivity" in summary
    assert "- comparison: full_seeds=1,2,3, prefix_seeds=1,2" in summary
    assert (
        "- full top response: policy=internal_improvement, "
        "observable=final queue depth, metric=normal_to_medium_slope, "
        "field=queue_depth_normal_to_medium_slope"
    ) in summary
    assert (
        "- prefix top response: policy=baseline, "
        "observable=value-weighted completed work, metric=curvature, "
        "field=value_weighted_completed_pressure_curvature"
    ) in summary
    assert "- top response stable across prefix: false" in summary
    assert "- top response stable across all prefixes: false" in summary
    assert "- prefix instability causes: policy,observable,metric" in summary
    assert "| prefix_seeds | top_response | stable_with_full | instability_causes |" in summary
    assert (
        "| 1 | policy=baseline, observable=value-weighted completed work, "
        "metric=curvature, field=value_weighted_completed_pressure_curvature"
    ) in summary
    assert (
        "| 1 | policy=baseline, observable=value-weighted completed work, "
        "metric=curvature, field=value_weighted_completed_pressure_curvature, "
        "value="
    ) in summary
    assert "false | policy,observable,metric |" in summary
    assert (
        "| 1,2 | policy=baseline, observable=value-weighted completed work, "
        "metric=curvature, field=value_weighted_completed_pressure_curvature"
    ) in summary


def test_a2_attention_pressure_summary_compares_global_and_class_stability(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"
    readme = Path("README.md").read_text()

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()

    assert "`Pressure-response stability agreement`" in readme
    assert "global top-response prefix stability" in readme
    assert "class-specific capture-pressure prefix stability" in readme
    assert "## Pressure-response stability agreement" in summary
    assert "## Pressure-stability convergence inspection" in summary
    assert "- comparison: full_seeds=1,2,3, prefix_seeds=1,2" in summary
    assert "- last prefix stable together: " in summary
    assert "- all prefixes stable together: " in summary
    assert "- last prefix details: global_stable=" in summary
    assert (
        "| prefix_seeds | global_stable_with_full | class_stable_with_full | "
        "stable_together | global_instability_causes | class_instability_causes |"
    ) in summary
    assert "| 1 | false | " in summary
    assert "| 1,2 | false | " in summary


def test_a2_attention_pressure_stability_agreement_csv_records_prefix_rows(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "pressure_stability_agreement.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert list(rows[0]) == list(PRESSURE_STABILITY_AGREEMENT_FIELDS)
    assert [row["full_seeds"] for row in rows] == ["1,2,3", "1,2,3"]
    assert [row["prefix_seeds"] for row in rows] == ["1", "1,2"]
    assert rows[0]["global_stable_with_full"] == "false"
    assert rows[0]["class_stable_with_full"] in {"true", "false"}
    assert rows[0]["stable_together"] in {"true", "false"}
    assert rows[0]["global_instability_causes"]
    assert rows[0]["class_instability_causes"]
    assert rows[0]["global_policy"]
    assert rows[0]["global_observable"]
    assert rows[0]["global_metric"]
    assert rows[0]["global_field"]
    assert rows[0]["class_policy"]
    assert rows[0]["class_observable"]
    assert rows[0]["class_metric"]
    assert rows[0]["class_field"].startswith(
        tuple(f"{class_name}_capture_pressure_" for class_name in ATTENTION_CLASSES)
    )


def test_a2_attention_pressure_stability_convergence_csv_summarizes_prefix_rows(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "pressure_stability_agreement.csv").open() as handle:
        agreement_rows = list(csv.DictReader(handle))
    with (out_dir / "pressure_stability_convergence.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert list(rows[0]) == list(PRESSURE_STABILITY_CONVERGENCE_FIELDS)
    assert rows[0]["full_seeds"] == "1,2,3"
    assert rows[0]["prefix_count"] == str(len(agreement_rows))
    assert rows[0]["last_prefix"] == agreement_rows[-1]["prefix_seeds"]
    assert rows[0]["last_global_stable"] == agreement_rows[-1][
        "global_stable_with_full"
    ]
    assert rows[0]["last_class_stable"] == agreement_rows[-1][
        "class_stable_with_full"
    ]
    assert rows[0]["last_stable_together"] == agreement_rows[-1]["stable_together"]
    assert rows[0]["last_both_stable"] in {"true", "false"}
    assert rows[0]["first_global_stable_prefix"]
    assert rows[0]["first_class_stable_prefix"]
    assert rows[0]["first_stable_together_prefix"]
    assert rows[0]["first_both_stable_prefix"]
    summary = (out_dir / "summary.md").read_text()
    assert (
        "- convergence vs interpretation: pressure-response interpretation selects "
        "policy=internal_improvement observable=final queue depth "
        "metric=normal_to_medium_slope; first_global_stable_prefix="
    ) in summary
    assert (
        f"last_prefix={rows[0]['last_prefix']}, "
        f"last_global_stable={rows[0]['last_global_stable']}."
    ) in summary


def test_a2_attention_pressure_comparison_metrics_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        header = next(csv.reader(handle))

    assert header == list(PRESSURE_COMPARISON_FIELDS)


def test_a2_attention_pressure_response_selection_csv_records_full_and_prefix_top_responses(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "pressure_response_selection.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert list(rows[0]) == list(PRESSURE_RESPONSE_SELECTION_FIELDS)
    assert [row["selection_scope"] for row in rows] == [
        "full",
        "prefix",
        "prefix",
        "class_full",
        "class_prefix",
        "class_prefix",
    ]
    assert [row["seeds"] for row in rows] == ["1,2,3", "1", "1,2", "1,2,3", "1", "1,2"]
    assert rows[0]["policy"] == "internal_improvement"
    assert rows[0]["observable"] == "final queue depth"
    assert rows[0]["metric"] == "normal_to_medium_slope"
    assert rows[0]["field"] == "queue_depth_normal_to_medium_slope"
    assert rows[0]["source_field"] == "queue_depth"
    assert rows[0]["stable_with_full"] == "true"
    assert rows[0]["instability_causes"] == "none"
    assert rows[0]["normal_mean"] == "20.666667"
    assert rows[0]["medium_mean"] == "39.333333"
    assert rows[0]["high_mean"] == "45.666667"
    assert rows[0]["normal_to_medium_slope"] == "46.666665"
    assert rows[0]["medium_to_high_slope"] == "15.833335"
    assert rows[0]["curvature"] == "-30.83333"
    assert rows[0]["high_minus_normal_delta"] == "25.0"
    assert rows[0]["source_metric_normal_mean"] == "20.666667"
    assert rows[0]["source_metric_medium_mean"] == "39.333333"
    assert rows[0]["source_metric_high_mean"] == "45.666667"
    assert rows[0]["source_metric_normal_per_seed_values"].startswith("1:")
    assert "|2:" in rows[0]["source_metric_normal_per_seed_values"]
    assert "|3:" in rows[0]["source_metric_normal_per_seed_values"]
    assert rows[0]["source_metric_medium_min"]
    assert rows[0]["source_metric_high_max"]
    assert rows[2]["policy"] == "baseline"
    assert rows[2]["observable"] == "value-weighted completed work"
    assert rows[2]["metric"] == "curvature"
    assert rows[2]["stable_with_full"] == "false"
    assert rows[2]["instability_causes"] == "policy,observable,metric"
    assert rows[3]["selection_scope"] == "class_full"
    assert rows[3]["field"].startswith(
        tuple(f"{class_name}_capture_pressure_" for class_name in ATTENTION_CLASSES)
    )
    assert rows[3]["stable_with_full"] == "true"
    assert rows[3]["instability_causes"] == "none"
    assert rows[5]["selection_scope"] == "class_prefix"
    assert rows[5]["field"].startswith(
        tuple(f"{class_name}_capture_pressure_" for class_name in ATTENTION_CLASSES)
    )
    assert rows[5]["stable_with_full"] in {"true", "false"}
    assert rows[5]["normal_mean"]
    assert rows[5]["high_minus_normal_delta"]


def test_a2_attention_pressure_stability_agreement_csv_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_stability_agreement.csv").open() as handle:
        header = next(csv.reader(handle))

    assert header == list(PRESSURE_STABILITY_AGREEMENT_FIELDS)


def test_a2_attention_pressure_stability_convergence_csv_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_stability_convergence.csv").open() as handle:
        header = next(csv.reader(handle))

    assert header == list(PRESSURE_STABILITY_CONVERGENCE_FIELDS)


def test_a2_attention_pressure_comparison_curve_metrics_match_condition_means(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    rows = run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)
    baseline_row = next(row for row in rows if row["policy"] == "baseline")
    means = {}
    class_means = {}
    for condition in ("normal_pressure", "medium_pressure", "high_pressure"):
        with (out_dir / condition / "comparison_metrics.csv").open() as handle:
            condition_rows = [
                row for row in csv.DictReader(handle)
                if row["policy"] == "baseline"
            ]
        means[condition] = _mean_csv_metric(
            condition_rows,
            policy="baseline",
            field="queue_depth",
        )
        class_means[condition] = round(
            _mean_csv_metric(
                condition_rows,
                policy="baseline",
                field="near_term_external_capture_pressure_final",
            ),
            6,
        )

    normal_to_medium = round(
        (means["medium_pressure"] - means["normal_pressure"]) / 0.4,
        6,
    )
    medium_to_high = round(
        (means["high_pressure"] - means["medium_pressure"]) / 0.4,
        6,
    )

    assert baseline_row["queue_depth_normal_to_medium_slope"] == normal_to_medium
    assert baseline_row["queue_depth_medium_to_high_slope"] == medium_to_high
    assert baseline_row["queue_depth_pressure_curvature"] == round(
        medium_to_high - normal_to_medium,
        6,
    )

    class_normal_to_medium = round(
        (class_means["medium_pressure"] - class_means["normal_pressure"]) / 0.4,
        6,
    )
    class_medium_to_high = round(
        (class_means["high_pressure"] - class_means["medium_pressure"]) / 0.4,
        6,
    )

    assert (
        baseline_row["near_term_external_capture_pressure_final_normal_to_medium_slope"]
        == pytest.approx(class_normal_to_medium, abs=2e-6)
    )
    assert (
        baseline_row["near_term_external_capture_pressure_final_medium_to_high_slope"]
        == pytest.approx(class_medium_to_high, abs=2e-6)
    )
    assert baseline_row[
        "near_term_external_capture_pressure_final_pressure_curvature"
    ] == pytest.approx(
        round(
            class_medium_to_high - class_normal_to_medium,
            6,
        ),
        abs=2e-6,
    )


def test_a2_attention_pressure_comparison_uses_custom_pressure_axis(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_extreme_pressure_compare"

    rows = run_pressure_comparison(
        medium_pressure_baseline_config=A2_ATTENTION_HIGH_PRESSURE,
        medium_pressure_variant_config=A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE,
        medium_pressure_internal_improvement_config=(
            A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE
        ),
        high_pressure_baseline_config=A2_ATTENTION_EXTREME_PRESSURE,
        high_pressure_variant_config=A2_ATTENTION_RESEARCH_HEAVY_EXTREME_PRESSURE,
        high_pressure_internal_improvement_config=(
            A2_ATTENTION_INTERNAL_IMPROVEMENT_EXTREME_PRESSURE
        ),
        seeds=(1,),
        out_dir=out_dir,
    )
    baseline_row = next(row for row in rows if row["policy"] == "baseline")
    means = {}
    for condition in ("medium_pressure", "high_pressure"):
        with (out_dir / condition / "comparison_metrics.csv").open() as handle:
            condition_rows = [
                row for row in csv.DictReader(handle)
                if row["policy"] == "baseline"
            ]
        means[condition] = _mean_csv_metric(
            condition_rows,
            policy="baseline",
            field="queue_depth",
        )

    expected_slope = round(
        (means["high_pressure"] - means["medium_pressure"]) / (2.2 - 1.8),
        6,
    )

    assert baseline_row["queue_depth_medium_to_high_slope"] == expected_slope


def test_a2_attention_pressure_comparison_runner_is_reproducible(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_pressure_comparison(seeds=(1, 2), out_dir=first)
    run_pressure_comparison(seeds=(1, 2), out_dir=second)

    assert (first / "pressure_comparison_metrics.csv").read_text() == (
        second / "pressure_comparison_metrics.csv"
    ).read_text()
    assert (first / "pressure_response_selection.csv").read_text() == (
        second / "pressure_response_selection.csv"
    ).read_text()
    assert (first / "pressure_stability_agreement.csv").read_text() == (
        second / "pressure_stability_agreement.csv"
    ).read_text()
    assert (first / "pressure_stability_convergence.csv").read_text() == (
        second / "pressure_stability_convergence.csv"
    ).read_text()
    assert (first / "pressure_trajectory_structure.csv").read_text() == (
        second / "pressure_trajectory_structure.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_documented_pressure_cli_writes_pressure_layout_and_curve_summary(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare_cli"
    readme = Path("README.md").read_text()

    _run_documented_pressure_cli(out_dir, seeds=(1, 2))

    assert (out_dir / "normal_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "normal_pressure" / "summary.md").is_file()
    assert (out_dir / "medium_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "medium_pressure" / "summary.md").is_file()
    assert (out_dir / "high_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "high_pressure" / "summary.md").is_file()
    assert (out_dir / "pressure_comparison_metrics.csv").is_file()
    assert (out_dir / "pressure_response_selection.csv").is_file()
    assert (out_dir / "pressure_stability_agreement.csv").is_file()
    assert (out_dir / "pressure_stability_convergence.csv").is_file()
    assert (out_dir / "pressure_trajectory_structure.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (out_dir / "pressure_trajectory_structure.csv").open() as handle:
        trajectory_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert "treat `policy` as the stable join key" in readme
    assert "`pressure_comparison_metrics.csv`" in readme
    assert "`pressure_trajectory_structure.csv`" in readme
    assert len(rows) == 3
    assert [row["policy"] for row in trajectory_rows] == [row["policy"] for row in rows]
    assert {row["policy"] for row in rows} == {
        "baseline",
        "research_heavy",
        "internal_improvement",
    }
    assert rows[0]["normal_total_steps"] == "22"
    assert rows[0]["medium_pressure_total_steps"] == "22"
    assert rows[0]["high_pressure_total_steps"] == "22"
    assert "## Fixed-policy pressure deltas" in summary
    assert "## Most pressure-sensitive curve metric" in summary
    assert "## Pressure-curve response ranking" in summary
    assert "## Fixed-policy pressure curves" in summary
    assert "- medium-pressure baseline config: configs/a2_attention_medium_pressure.yaml" in summary
    assert "- baseline final queue depth pressure curve: " in summary
    assert "- baseline final attention capture pressure curve: " in summary
    assert "normal_to_medium_slope=" in summary
    assert "medium_to_high_slope=" in summary
    assert "curvature=" in summary


def test_documented_pressure_cli_reproduces_top_level_artifacts(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    _run_documented_pressure_cli(first, seeds=(1, 2))
    _run_documented_pressure_cli(second, seeds=(1, 2))

    _assert_artifacts_are_byte_identical(
        first,
        second,
        [
            "pressure_comparison_metrics.csv",
            "pressure_response_selection.csv",
            "pressure_stability_agreement.csv",
            "pressure_stability_convergence.csv",
            "pressure_trajectory_structure.csv",
            "summary.md",
        ],
    )


def test_documented_pressure_cli_reproduces_source_metric_selection_fields(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    source_metric_fields = [
        field
        for field in PRESSURE_RESPONSE_SELECTION_FIELDS
        if field == "source_field" or field.startswith("source_metric_")
    ]

    _run_documented_pressure_cli(first, seeds=(1, 2, 3))
    _run_documented_pressure_cli(second, seeds=(1, 2, 3))

    with (first / "pressure_response_selection.csv").open() as first_handle:
        first_rows = list(csv.DictReader(first_handle))
    with (second / "pressure_response_selection.csv").open() as second_handle:
        second_rows = list(csv.DictReader(second_handle))

    assert first_rows
    assert len(first_rows) == len(second_rows)
    assert (first / "pressure_response_selection.csv").read_bytes() == (
        second / "pressure_response_selection.csv"
    ).read_bytes()
    assert [
        {field: row[field] for field in source_metric_fields}
        for row in first_rows
    ] == [
        {field: row[field] for field in source_metric_fields}
        for row in second_rows
    ]
    assert first_rows[0]["selection_scope"] == "full"
    assert first_rows[0]["source_field"] == "queue_depth"
    assert first_rows[0]["source_metric_normal_mean"] == "20.666667"
    assert first_rows[0]["source_metric_medium_mean"] == "39.333333"
    assert first_rows[0]["source_metric_high_mean"] == "45.666667"


def test_pressure_analysis_reads_joined_csv_pair_and_ranks_responses(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"

    run_pressure_comparison(seeds=(1, 2), out_dir=pressure_dir)
    rows = run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert len(rows) == 5
    assert (analysis_dir / "trajectory_pressure_ranking.csv").is_file()
    assert (analysis_dir / "value_yield_divergence_ranking.csv").is_file()
    assert (analysis_dir / "value_yield_divergence_stability.csv").is_file()
    assert (analysis_dir / "pressure_bootstrap_rank_stability.csv").is_file()
    assert (analysis_dir / "interpretation.csv").is_file()
    assert (analysis_dir / "summary.md").is_file()

    with (analysis_dir / "trajectory_pressure_ranking.csv").open() as handle:
        csv_rows = list(csv.DictReader(handle))
    with (analysis_dir / "value_yield_divergence_ranking.csv").open() as handle:
        divergence_rows = list(csv.DictReader(handle))
    with (analysis_dir / "value_yield_divergence_stability.csv").open() as handle:
        stability_rows = list(csv.DictReader(handle))
    with (analysis_dir / "pressure_bootstrap_rank_stability.csv").open() as handle:
        bootstrap_rows = list(csv.DictReader(handle))
    with (analysis_dir / "interpretation.csv").open() as handle:
        interpretation_rows = list(csv.DictReader(handle))
    summary = (analysis_dir / "summary.md").read_text()

    assert list(csv_rows[0]) == list(TRAJECTORY_PRESSURE_RANKING_FIELDS)
    assert list(divergence_rows[0]) == list(VALUE_YIELD_DIVERGENCE_RANKING_FIELDS)
    assert list(stability_rows[0]) == list(VALUE_YIELD_DIVERGENCE_STABILITY_FIELDS)
    assert list(bootstrap_rows[0]) == list(PRESSURE_BOOTSTRAP_RANK_STABILITY_FIELDS)
    assert list(interpretation_rows[0]) == list(INTERPRETATION_FIELDS)
    assert [row["rank"] for row in csv_rows] == ["1", "2", "3", "4", "5"]
    assert [row["rank"] for row in divergence_rows] == ["1", "2", "3", "4", "5"]
    assert csv_rows[0]["response_field"] == rows[0]["response_field"]
    assert csv_rows[0]["response_abs_value"]
    assert csv_rows[0]["trajectory_abs_delta_total"]
    assert divergence_rows[0]["value_per_completed_task_field"]
    assert divergence_rows[0]["value_per_work_event_field"]
    assert divergence_rows[0]["abs_divergence"]
    assert stability_rows[0]["full_seeds"] == "1,2"
    assert stability_rows[0]["prefix_seeds"] == "1"
    assert stability_rows[0]["stable_with_full"] in {"true", "false"}
    assert {row["selection_scope"] for row in bootstrap_rows} == {
        "class_capture_pressure",
        "global",
        "value_yield_divergence",
    }
    assert bootstrap_rows[0]["full_seeds"] == "1,2"
    assert bootstrap_rows[0]["resamples"] == "200"
    assert bootstrap_rows[0]["bootstrap_seed"] == "1"
    assert float(bootstrap_rows[0]["top_selection_probability"]) >= 0.0
    assert float(bootstrap_rows[0]["sign_stability"]) >= 0.0
    assert len(interpretation_rows) == 1
    assert interpretation_rows[0]["top_divergence_policy"] == divergence_rows[0]["policy"]
    assert interpretation_rows[0]["top_divergence_metric"] == divergence_rows[0]["metric"]
    assert (
        interpretation_rows[0]["top_divergence_stable_last_prefix"]
        == stability_rows[-1]["stable_with_full"]
    )
    assert (
        interpretation_rows[0]["top_trajectory_response_field"]
        == csv_rows[0]["response_field"]
    )
    assert "## Ranking" in summary
    assert "## Value-yield divergence ranking" in summary
    assert "## Top value-yield divergence interpretation" in summary
    assert "## Value-yield divergence prefix stability" in summary
    assert "## Bootstrap rank stability" in summary
    assert "- top divergence: " in summary
    assert "- top divergence stable across last prefix: " in summary
    assert "completion-normalized yield" in summary
    assert "effort-normalized yield" in summary
    assert "pressure_comparison_metrics.csv" not in summary


def test_pressure_analysis_five_seed_interpretation_regression(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"

    run_pressure_comparison(seeds=(1, 2, 3, 4, 5), out_dir=pressure_dir)
    run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=10)

    with (analysis_dir / "interpretation.csv").open() as handle:
        interpretation_rows = list(csv.DictReader(handle))
    summary = (analysis_dir / "summary.md").read_text()

    assert interpretation_rows == [
        {
            "top_divergence_policy": "baseline",
            "top_divergence_metric": "curvature",
            "top_divergence_value_per_completed_task_response": "0.147768",
            "top_divergence_value_per_work_event_response": "0.65523",
            "top_divergence": "-0.507462",
            "top_divergence_abs": "0.507462",
            "top_divergence_stable_last_prefix": "true",
            "top_divergence_stable_all_prefixes": "false",
            "top_divergence_full_seeds": "1,2,3,4,5",
            "top_divergence_last_prefix_seeds": "1,2,3,4",
            "top_divergence_last_prefix_instability_causes": "none",
            "top_trajectory_policy": "internal_improvement",
            "top_trajectory_response_observable": "final queue depth",
            "top_trajectory_response_metric": "normal_to_medium_slope",
            "top_trajectory_response_field": "queue_depth_normal_to_medium_slope",
            "top_trajectory_response_value": "45.0",
            "top_trajectory_response_abs_value": "45.0",
            "top_trajectory_abs_delta_total": "4.2",
        }
    ]
    assert (
        "pressure improves both yield normalizations, with a larger "
        "effort-normalized response; this is a same-direction divergence, not a "
        "completion-vs-effort tradeoff."
    ) in summary


@pytest.mark.parametrize(
    ("completed_response", "work_response", "expected"),
    [
        (
            0.25,
            -0.75,
            (
                "pressure improves completion-normalized yield while degrading "
                "effort-normalized yield"
            ),
        ),
        (
            -0.25,
            0.75,
            (
                "pressure degrades completion-normalized yield while improving "
                "effort-normalized yield"
            ),
        ),
        (
            0.0,
            0.0,
            "pressure leaves both yield normalizations unchanged",
        ),
        (
            0.0,
            0.75,
            (
                "pressure leaves completion-normalized yield unchanged while "
                "improves effort-normalized yield"
            ),
        ),
        (
            0.0,
            -0.75,
            (
                "pressure leaves completion-normalized yield unchanged while "
                "degrades effort-normalized yield"
            ),
        ),
        (
            0.25,
            0.0,
            (
                "pressure improves completion-normalized yield while leaving "
                "effort-normalized yield unchanged"
            ),
        ),
        (
            -0.25,
            0.0,
            (
                "pressure degrades completion-normalized yield while leaving "
                "effort-normalized yield unchanged"
            ),
        ),
    ],
)
def test_pressure_analysis_value_yield_branch_wording(
    completed_response: float,
    work_response: float,
    expected: str,
) -> None:
    assert _yield_divergence_interpretation(completed_response, work_response) == expected


def test_pressure_analysis_requires_pressure_input_csv_pair(tmp_path: Path) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="pressure_comparison_metrics.csv"):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert not analysis_dir.exists()


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_pressure_analysis_rejects_invalid_limit_without_partial_outputs(
    tmp_path: Path,
    limit: object,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    with pytest.raises(ValueError, match="limit must be a positive integer"):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=limit)  # type: ignore[arg-type]

    assert not analysis_dir.exists()


def test_pressure_analysis_reports_malformed_pressure_csv_schema_without_partial_outputs(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()
    pressure_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if field != "queue_depth_pressure_curvature"
    ]

    _write_pressure_analysis_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        pressure_fields,
        {"policy": "baseline"},
    )
    _write_pressure_analysis_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        {"policy": "baseline"},
    )

    with pytest.raises(
        ValueError,
        match="pressure_comparison_metrics.csv is missing required fields: "
        "queue_depth_pressure_curvature",
    ):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert not analysis_dir.exists()


def test_pressure_analysis_reports_policy_mismatch_without_partial_outputs(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    _write_pressure_analysis_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        PRESSURE_COMPARISON_FIELDS,
        {"policy": "baseline"},
    )
    _write_pressure_analysis_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        {"policy": "research_heavy"},
    )

    with pytest.raises(
        ValueError,
        match=(
            "Policy mismatch between pressure_comparison_metrics.csv and "
            "pressure_trajectory_structure.csv: missing policies in trajectory: "
            "baseline; extra policies in trajectory: research_heavy"
        ),
    ):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert not analysis_dir.exists()


@pytest.mark.parametrize(
    ("artifact_name", "pressure_overrides", "trajectory_overrides", "error"),
    [
        (
            "pressure_comparison_metrics.csv",
            [{"policy": ""}],
            [{"policy": "baseline"}],
            "pressure_comparison_metrics.csv contains a row without policy",
        ),
        (
            "pressure_comparison_metrics.csv",
            [{"policy": "baseline"}, {"policy": "baseline"}],
            [{"policy": "baseline"}],
            "pressure_comparison_metrics.csv contains duplicate policy: baseline",
        ),
        (
            "pressure_trajectory_structure.csv",
            [{"policy": "baseline"}],
            [{"policy": ""}],
            "pressure_trajectory_structure.csv contains a row without policy",
        ),
        (
            "pressure_trajectory_structure.csv",
            [{"policy": "baseline"}],
            [{"policy": "baseline"}, {"policy": "baseline"}],
            "pressure_trajectory_structure.csv contains duplicate policy: baseline",
        ),
    ],
)
def test_pressure_analysis_rejects_blank_or_duplicate_policy_keys_without_partial_outputs(
    tmp_path: Path,
    artifact_name: str,
    pressure_overrides: list[dict[str, str]],
    trajectory_overrides: list[dict[str, str]],
    error: str,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    _write_pressure_analysis_rows_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        PRESSURE_COMPARISON_FIELDS,
        pressure_overrides,
    )
    _write_pressure_analysis_rows_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        trajectory_overrides,
    )

    assert artifact_name in error
    with pytest.raises(ValueError, match=error):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert not analysis_dir.exists()


@pytest.mark.parametrize(
    "collision_artifact",
    [
        "trajectory_pressure_ranking.csv",
        "value_yield_divergence_ranking.csv",
        "value_yield_divergence_stability.csv",
        "pressure_bootstrap_rank_stability.csv",
        "interpretation.csv",
        "summary.md",
    ],
)
def test_pressure_analysis_refuses_existing_output_artifacts_without_modifying_them(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    sentinel = f"preexisting {collision_artifact} sentinel\n"

    analysis_dir.mkdir()
    (analysis_dir / collision_artifact).write_text(sentinel)

    with pytest.raises(FileExistsError, match=collision_artifact):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert (analysis_dir / collision_artifact).read_text() == sentinel
    assert sorted(path.name for path in analysis_dir.iterdir()) == [collision_artifact]


def test_documented_pressure_analysis_cli_reproduces_ranking_artifacts(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    first = tmp_path / "first"
    second = tmp_path / "second"

    _run_documented_pressure_cli(pressure_dir, seeds=(1, 2))
    _run_documented_pressure_analysis_cli(pressure_dir, first, limit=5)
    _run_documented_pressure_analysis_cli(pressure_dir, second, limit=5)

    _assert_artifacts_are_byte_identical(
        first,
        second,
        [
            "trajectory_pressure_ranking.csv",
            "value_yield_divergence_ranking.csv",
            "value_yield_divergence_stability.csv",
            "pressure_bootstrap_rank_stability.csv",
            "interpretation.csv",
            "summary.md",
        ],
    )


def test_documented_pressure_analysis_cli_reports_missing_input_without_partial_outputs(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "pressure_comparison_metrics.csv" in completed.stderr
    assert not analysis_dir.exists()


@pytest.mark.parametrize("limit", ["0", "-1"])
def test_documented_pressure_analysis_cli_rejects_invalid_limit_without_partial_outputs(
    tmp_path: Path,
    limit: str,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            limit,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "limit must be a positive integer" in completed.stderr
    assert not analysis_dir.exists()


def test_documented_pressure_analysis_cli_reports_malformed_schema_without_partial_outputs(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()
    pressure_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if field != "queue_depth_pressure_curvature"
    ]

    _write_pressure_analysis_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        pressure_fields,
        {"policy": "baseline"},
    )
    _write_pressure_analysis_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        {"policy": "baseline"},
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert (
        "pressure_comparison_metrics.csv is missing required fields: "
        "queue_depth_pressure_curvature"
    ) in completed.stderr
    assert not analysis_dir.exists()


def test_documented_pressure_analysis_cli_reports_policy_mismatch_without_partial_outputs(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    _write_pressure_analysis_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        PRESSURE_COMPARISON_FIELDS,
        {"policy": "baseline"},
    )
    _write_pressure_analysis_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        {"policy": "research_heavy"},
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert (
        "Policy mismatch between pressure_comparison_metrics.csv and "
        "pressure_trajectory_structure.csv: missing policies in trajectory: "
        "baseline; extra policies in trajectory: research_heavy"
    ) in completed.stderr
    assert not analysis_dir.exists()


@pytest.mark.parametrize(
    ("artifact_name", "pressure_overrides", "trajectory_overrides", "error"),
    [
        (
            "pressure_comparison_metrics.csv",
            [{"policy": ""}],
            [{"policy": "baseline"}],
            "pressure_comparison_metrics.csv contains a row without policy",
        ),
        (
            "pressure_comparison_metrics.csv",
            [{"policy": "baseline"}, {"policy": "baseline"}],
            [{"policy": "baseline"}],
            "pressure_comparison_metrics.csv contains duplicate policy: baseline",
        ),
        (
            "pressure_trajectory_structure.csv",
            [{"policy": "baseline"}],
            [{"policy": ""}],
            "pressure_trajectory_structure.csv contains a row without policy",
        ),
        (
            "pressure_trajectory_structure.csv",
            [{"policy": "baseline"}],
            [{"policy": "baseline"}, {"policy": "baseline"}],
            "pressure_trajectory_structure.csv contains duplicate policy: baseline",
        ),
    ],
)
def test_documented_pressure_analysis_cli_reports_blank_or_duplicate_policy_keys_without_partial_outputs(
    tmp_path: Path,
    artifact_name: str,
    pressure_overrides: list[dict[str, str]],
    trajectory_overrides: list[dict[str, str]],
    error: str,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    _write_pressure_analysis_rows_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        PRESSURE_COMPARISON_FIELDS,
        pressure_overrides,
    )
    _write_pressure_analysis_rows_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        trajectory_overrides,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert artifact_name in error
    assert completed.returncode != 0
    assert error in completed.stderr
    assert not analysis_dir.exists()


@pytest.mark.parametrize(
    "collision_artifact",
    [
        "trajectory_pressure_ranking.csv",
        "value_yield_divergence_ranking.csv",
        "value_yield_divergence_stability.csv",
        "pressure_bootstrap_rank_stability.csv",
        "interpretation.csv",
        "summary.md",
    ],
)
def test_documented_pressure_analysis_cli_refuses_existing_output_artifacts_without_modifying_them(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    sentinel = f"preexisting {collision_artifact} sentinel\n"

    analysis_dir.mkdir()
    (analysis_dir / collision_artifact).write_text(sentinel)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert collision_artifact in completed.stderr
    assert (analysis_dir / collision_artifact).read_text() == sentinel
    assert sorted(path.name for path in analysis_dir.iterdir()) == [collision_artifact]


def test_documented_pressure_cli_refuses_existing_top_level_artifacts_without_modifying_them(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare_cli"

    _run_documented_pressure_cli(out_dir, seeds=(1, 2))
    original_metrics = (out_dir / "pressure_comparison_metrics.csv").read_bytes()
    original_selection = (out_dir / "pressure_response_selection.csv").read_bytes()
    original_agreement = (out_dir / "pressure_stability_agreement.csv").read_bytes()
    original_convergence = (
        out_dir / "pressure_stability_convergence.csv"
    ).read_bytes()
    original_trajectory = (out_dir / "pressure_trajectory_structure.csv").read_bytes()
    original_summary = (out_dir / "summary.md").read_bytes()

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.compare_pressure",
            "--seeds",
            "1",
            "2",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert completed.stdout == ""
    assert "already contains pressure comparison artifacts" in completed.stderr
    assert (out_dir / "pressure_comparison_metrics.csv").read_bytes() == original_metrics
    assert (out_dir / "pressure_response_selection.csv").read_bytes() == original_selection
    assert (
        (out_dir / "pressure_stability_agreement.csv").read_bytes()
        == original_agreement
    )
    assert (
        (out_dir / "pressure_stability_convergence.csv").read_bytes()
        == original_convergence
    )
    assert (
        (out_dir / "pressure_trajectory_structure.csv").read_bytes()
        == original_trajectory
    )
    assert (out_dir / "summary.md").read_bytes() == original_summary


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


def _write_pressure_analysis_csv(
    path: Path,
    fieldnames: tuple[str, ...] | list[str],
    overrides: dict[str, str],
) -> None:
    _write_pressure_analysis_rows_csv(path, fieldnames, [overrides])


def _write_pressure_analysis_rows_csv(
    path: Path,
    fieldnames: tuple[str, ...] | list[str],
    overrides_rows: list[dict[str, str]],
) -> None:
    row = {field: "0" for field in fieldnames}
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for overrides in overrides_rows:
            output_row = dict(row)
            output_row.update(overrides)
            writer.writerow(output_row)


def _mean_csv_metric(
    rows: list[dict[str, str]],
    *,
    policy: str,
    field: str,
) -> float:
    policy_rows = [row for row in rows if row["policy"] == policy]
    return sum(float(row[field]) for row in policy_rows) / len(policy_rows)


def _trajectory_structure_summary_from_csv(
    rows: list[dict[str, str]],
    policy: str,
) -> dict[str, float | str]:
    policy_rows = [row for row in rows if row["policy"] == policy]
    turning_points = [
        float(row["phase_space_turning_point_count"])
        for row in policy_rows
    ]
    dwell_steps = [
        float(row["phase_space_longest_dwell_steps"])
        for row in policy_rows
    ]
    labels = Counter(row["phase_space_longest_dwell_label"] for row in policy_rows)

    return {
        "turning_points_mean": round(sum(turning_points) / len(turning_points), 6),
        "longest_dwell_steps_mean": round(sum(dwell_steps) / len(dwell_steps), 6),
        "longest_dwell_labels": "|".join(
            f"{label}:{labels[label]}"
            for label in sorted(labels)
        ),
    }


def _step_deltas(trajectory: str) -> str:
    values = [float(value) for value in trajectory.split("|")]
    deltas = [
        _format_number(values[index] - values[index - 1])
        for index in range(1, len(values))
    ]
    return "|".join(deltas)


def _format_number(value: float) -> str:
    rounded = round(value, 6)
    if rounded.is_integer():
        return str(int(rounded))
    return str(rounded)


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

    actions = _actions_from_normalized_config(normalized_config)
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
            "task_creation_pressure": 1.0,
            "work_service_capacity": 1.0,
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


def test_reordered_action_fixture_keeps_config_manifest_and_metrics_schema_aligned(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_reordered_actions"

    run_experiment(REORDERED_ACTIONS, seed=1, out_dir=out_dir)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    actions = _actions_from_normalized_config(normalized_config)
    expected_role_action_fields = list(role_action_metric_fields(tuple(actions)))
    expected_metrics_fields = list(metrics_fieldnames(tuple(actions)))

    assert actions == ["work_task", "create_task", "message", "idle"]
    assert manifest["actions"] == actions
    assert manifest["config"]["model"]["actions"] == actions
    assert manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert manifest["model"]["role_action_metrics"]["actions"] == actions
    assert manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert metrics_header == expected_metrics_fields
    assert [
        field for field in metrics_header if field.startswith("role_")
    ] == expected_role_action_fields


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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_summary_schema_provenance_counts_match_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    _assert_summary_schema_provenance_counts_match_manifest(summary, manifest)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_schema_provenance_counts_match_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_schema_counts"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    _assert_summary_schema_provenance_counts_match_manifest(summary, manifest)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_agent_identity_and_roles_match_baseline_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_agent_identity_roles"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())

    _assert_manifest_agent_identity_and_roles_match_baseline(manifest)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_run_state_matches_recomputed_dwell_runs_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_lobe_run_state"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_lobe_run_state_matches_recomputed_dwell_runs(metric_rows)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_transitions_match_adjacent_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_lobe_transitions"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_lobe_transitions_match_adjacent_labels(metric_rows)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_label_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_lobe_label_sequence_first",
        second_name=f"{config_path.stem}_cli_lobe_label_sequence_second",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_label_sequence(first_metric_rows)
    second_sequence = _lobe_label_sequence(second_metric_rows)

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_label_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_lobe_label_sequence_seed1",
        second_name=f"{config_path.stem}_cli_lobe_label_sequence_seed2",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_label_sequence(first_metric_rows)
    second_sequence = _lobe_label_sequence(second_metric_rows)

    assert first_sequence
    assert second_sequence
    assert first_sequence != second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_transition_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_transition_sequence_first",
        second_name=f"{config_path.stem}_cli_transition_sequence_second",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_transition_sequence(first_metric_rows)
    second_sequence = _lobe_transition_sequence(second_metric_rows)

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_transition_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_transition_sequence_seed1",
        second_name=f"{config_path.stem}_cli_transition_sequence_seed2",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_transition_field_sequence(first_metric_rows)
    second_sequence = _lobe_transition_field_sequence(second_metric_rows)

    assert first_sequence
    assert second_sequence
    assert first_sequence != second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_run_state_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_run_state_sequence_first",
        second_name=f"{config_path.stem}_cli_run_state_sequence_second",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_run_state_sequence(first_metric_rows)
    second_sequence = _lobe_run_state_sequence(second_metric_rows)

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_run_state_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_run_state_sequence_seed1",
        second_name=f"{config_path.stem}_cli_run_state_sequence_seed2",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_run_state_sequence(first_metric_rows)
    second_sequence = _lobe_run_state_sequence(second_metric_rows)
    first_state_signature = (_lobe_label_sequence(first_metric_rows), first_sequence)
    second_state_signature = (_lobe_label_sequence(second_metric_rows), second_sequence)

    assert first_sequence
    assert second_sequence
    assert first_state_signature != second_state_signature


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_dwell_run_summary_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_dwell_run_summary_seed1",
        second_name=f"{config_path.stem}_cli_dwell_run_summary_seed2",
    )

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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_role_action_summary_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_role_action_summary_first",
        second_name=f"{config_path.stem}_cli_role_action_summary_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_role_action_totals = _summary_role_action_totals(first_summary)
    second_role_action_totals = _summary_role_action_totals(second_summary)
    first_actions = tuple(first_manifest["actions"])
    second_actions = tuple(second_manifest["actions"])

    assert first_role_action_totals == _role_action_totals_from_metrics(
        first_metric_rows,
        first_actions,
    )
    assert second_role_action_totals == _role_action_totals_from_metrics(
        second_metric_rows,
        second_actions,
    )
    assert first_role_action_totals
    assert first_role_action_totals == second_role_action_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_role_action_metric_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_role_action_sequence_first",
        second_name=f"{config_path.stem}_cli_role_action_sequence_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _role_action_metric_sequence(
        first_metric_rows,
        tuple(first_manifest["actions"]),
    )
    second_sequence = _role_action_metric_sequence(
        second_metric_rows,
        tuple(second_manifest["actions"]),
    )

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_events_replay_to_summary_role_action_totals_through_manifest_roles_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_summary_role_action_totals"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_replay_to_summary_role_action_totals_through_manifest_roles(
        summary,
        event_rows=event_rows,
        manifest_roles=manifest["model"]["roles"],
        actions=tuple(manifest["actions"]),
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_role_action_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_event_replayed_role_action_first",
        second_name=f"{config_path.stem}_cli_event_replayed_role_action_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_totals = _role_action_totals_from_events(
        first_event_rows,
        manifest_roles=first_manifest["model"]["roles"],
        actions=tuple(first_manifest["actions"]),
    )
    second_replayed_totals = _role_action_totals_from_events(
        second_event_rows,
        manifest_roles=second_manifest["model"]["roles"],
        actions=tuple(second_manifest["actions"]),
    )

    assert first_replayed_totals == _summary_role_action_totals(first_summary)
    assert second_replayed_totals == _summary_role_action_totals(second_summary)
    assert first_replayed_totals
    assert first_replayed_totals == second_replayed_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_role_action_totals_change_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_event_replayed_role_action_seed1",
        second_name=f"{config_path.stem}_cli_event_replayed_role_action_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_totals = _role_action_totals_from_events(
        first_event_rows,
        manifest_roles=first_manifest["model"]["roles"],
        actions=tuple(first_manifest["actions"]),
    )
    second_replayed_totals = _role_action_totals_from_events(
        second_event_rows,
        manifest_roles=second_manifest["model"]["roles"],
        actions=tuple(second_manifest["actions"]),
    )

    assert first_replayed_totals == _summary_role_action_totals(first_summary)
    assert second_replayed_totals == _summary_role_action_totals(second_summary)
    assert first_replayed_totals
    assert second_replayed_totals
    assert first_replayed_totals != second_replayed_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_role_action_metric_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_event_replayed_role_action_sequence_seed1",
        second_name=f"{config_path.stem}_cli_event_replayed_role_action_sequence_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_actions = tuple(first_manifest["actions"])
    second_actions = tuple(second_manifest["actions"])
    first_replayed_sequence = _role_action_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
        manifest_roles=first_manifest["model"]["roles"],
        actions=first_actions,
    )
    second_replayed_sequence = _role_action_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
        manifest_roles=second_manifest["model"]["roles"],
        actions=second_actions,
    )

    assert first_replayed_sequence == _role_action_metric_sequence(
        first_metric_rows,
        first_actions,
    )
    assert second_replayed_sequence == _role_action_metric_sequence(
        second_metric_rows,
        second_actions,
    )
    assert first_replayed_sequence
    assert second_replayed_sequence
    assert first_replayed_sequence != second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_top_level_metric_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_event_replayed_top_level_sequence_first",
        second_name=f"{config_path.stem}_cli_event_replayed_top_level_sequence_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _top_level_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _top_level_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _top_level_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _top_level_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert first_replayed_sequence == second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_top_level_metric_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_event_replayed_top_level_sequence_seed1",
        second_name=f"{config_path.stem}_cli_event_replayed_top_level_sequence_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _top_level_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _top_level_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _top_level_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _top_level_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert second_replayed_sequence
    assert first_replayed_sequence != second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_queue_pressure_metric_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_event_replayed_queue_pressure_first",
        second_name=f"{config_path.stem}_cli_event_replayed_queue_pressure_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _queue_pressure_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _queue_pressure_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _queue_pressure_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _queue_pressure_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert first_replayed_sequence == second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_queue_pressure_metric_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_event_replayed_queue_pressure_seed1",
        second_name=f"{config_path.stem}_cli_event_replayed_queue_pressure_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _queue_pressure_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _queue_pressure_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _queue_pressure_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _queue_pressure_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert second_replayed_sequence
    assert first_replayed_sequence != second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_queue_pressure_totals_change_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_queue_pressure_seed1",
        second_name=f"{config_path.stem}_cli_summary_queue_pressure_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_queue_pressure_totals(first_summary)
    second_summary_totals = _summary_queue_pressure_totals(second_summary)

    assert first_summary_totals == _queue_pressure_totals_from_metrics(first_metric_rows)
    assert second_summary_totals == _queue_pressure_totals_from_metrics(second_metric_rows)
    assert first_summary_totals
    assert second_summary_totals
    assert first_summary_totals != second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_queue_pressure_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_queue_pressure_first",
        second_name=f"{config_path.stem}_cli_summary_queue_pressure_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_queue_pressure_totals(first_summary)
    second_summary_totals = _summary_queue_pressure_totals(second_summary)

    assert first_summary_totals == _queue_pressure_totals_from_metrics(first_metric_rows)
    assert second_summary_totals == _queue_pressure_totals_from_metrics(second_metric_rows)
    assert first_summary_totals
    assert first_summary_totals == second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_task_and_queue_totals_change_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_task_queue_totals_seed1",
        second_name=f"{config_path.stem}_cli_summary_task_queue_totals_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_task_and_queue_totals(first_summary)
    second_summary_totals = _summary_task_and_queue_totals(second_summary)

    assert first_summary_totals == _task_and_queue_totals_from_metrics(first_metric_rows)
    assert second_summary_totals == _task_and_queue_totals_from_metrics(second_metric_rows)
    assert first_summary_totals
    assert second_summary_totals
    assert first_summary_totals != second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_task_and_queue_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_task_queue_totals_first",
        second_name=f"{config_path.stem}_cli_summary_task_queue_totals_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_task_and_queue_totals(first_summary)
    second_summary_totals = _summary_task_and_queue_totals(second_summary)

    assert first_summary_totals == _task_and_queue_totals_from_metrics(first_metric_rows)
    assert second_summary_totals == _task_and_queue_totals_from_metrics(second_metric_rows)
    assert first_summary_totals
    assert first_summary_totals == second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_event_type_totals_change_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_event_type_totals_seed1",
        second_name=f"{config_path.stem}_cli_summary_event_type_totals_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_event_type_totals(first_summary)
    second_summary_totals = _summary_event_type_totals(second_summary)

    assert first_summary_totals == _event_type_totals_from_events(first_event_rows)
    assert second_summary_totals == _event_type_totals_from_events(second_event_rows)
    assert first_summary_totals
    assert second_summary_totals
    assert first_summary_totals != second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_event_type_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_event_type_totals_first",
        second_name=f"{config_path.stem}_cli_summary_event_type_totals_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_event_type_totals(first_summary)
    second_summary_totals = _summary_event_type_totals(second_summary)

    assert first_summary_totals == _event_type_totals_from_events(first_event_rows)
    assert second_summary_totals == _event_type_totals_from_events(second_event_rows)
    assert first_summary_totals
    assert first_summary_totals == second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_queued_task_age_aggregates_change_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_queued_task_age_seed1",
        second_name=f"{config_path.stem}_cli_summary_queued_task_age_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_aggregates = _summary_queued_task_age_aggregates(first_summary)
    second_summary_aggregates = _summary_queued_task_age_aggregates(second_summary)

    assert first_summary_aggregates == _queued_task_age_aggregates_from_metrics(
        first_metric_rows
    )
    assert second_summary_aggregates == _queued_task_age_aggregates_from_metrics(
        second_metric_rows
    )
    assert first_summary_aggregates
    assert second_summary_aggregates
    assert first_summary_aggregates != second_summary_aggregates


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_queued_task_age_aggregates_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_queued_task_age_first",
        second_name=f"{config_path.stem}_cli_summary_queued_task_age_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_aggregates = _summary_queued_task_age_aggregates(first_summary)
    second_summary_aggregates = _summary_queued_task_age_aggregates(second_summary)

    assert first_summary_aggregates == _queued_task_age_aggregates_from_metrics(
        first_metric_rows
    )
    assert second_summary_aggregates == _queued_task_age_aggregates_from_metrics(
        second_metric_rows
    )
    assert first_summary_aggregates
    assert first_summary_aggregates == second_summary_aggregates


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_task_queue_pressure_and_age_aggregates_match_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_queue_integrity"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    summary_task_queue_totals = _summary_task_and_queue_totals(summary)
    summary_queue_pressure_totals = _summary_queue_pressure_totals(summary)
    summary_age_aggregates = _summary_queued_task_age_aggregates(summary)

    assert summary_task_queue_totals == _task_and_queue_totals_from_metrics(metric_rows)
    assert summary_queue_pressure_totals == _queue_pressure_totals_from_metrics(metric_rows)
    assert summary_age_aggregates == _queued_task_age_aggregates_from_metrics(metric_rows)
    assert (
        summary_task_queue_totals["queue_depth"]
        == summary_queue_pressure_totals["created_completed_balance_tick"]
    )
    assert (
        summary_age_aggregates["final_queued_task_max_age"]
        >= summary_age_aggregates["final_queued_task_mean_age"]
    )
    assert (
        summary_age_aggregates["peak_queued_task_max_age"]
        >= summary_age_aggregates["final_queued_task_max_age"]
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_task_queue_pressure_and_age_aggregate_tuple_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_queue_integrity_first",
        second_name=f"{config_path.stem}_cli_summary_queue_integrity_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_tuple = _summary_task_queue_pressure_and_age_aggregate_tuple(first_summary)
    second_tuple = _summary_task_queue_pressure_and_age_aggregate_tuple(second_summary)

    assert first_tuple == _task_queue_pressure_and_age_aggregate_tuple_from_metrics(
        first_metric_rows
    )
    assert second_tuple == _task_queue_pressure_and_age_aggregate_tuple_from_metrics(
        second_metric_rows
    )
    assert first_tuple["task_queue_totals"]
    assert first_tuple["queue_pressure_totals"]
    assert first_tuple["queued_task_age_aggregates"]
    assert first_tuple == second_tuple


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_integrated_summary_aggregate_bundle_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_bundle_first",
        second_name=f"{config_path.stem}_cli_summary_bundle_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=tuple(first_manifest["actions"]),
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=tuple(second_manifest["actions"]),
    )

    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=tuple(first_manifest["actions"]),
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=tuple(second_manifest["actions"]),
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert first_bundle == second_bundle


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_integrated_summary_aggregate_bundle_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_bundle_seed1",
        second_name=f"{config_path.stem}_cli_summary_bundle_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=tuple(first_manifest["actions"]),
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=tuple(second_manifest["actions"]),
    )

    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=tuple(first_manifest["actions"]),
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=tuple(second_manifest["actions"]),
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert second_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert second_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert second_bundle["role_action_totals"]
    assert first_bundle != second_bundle


@pytest.mark.parametrize("config_path", NO_MANIFEST_FIXTURES)
def test_documented_cli_no_manifest_integrated_summary_aggregate_bundle_matches_metrics_with_config_actions(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_bundle"

    _run_documented_cli(config_path, out_dir)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    actions = tuple(normalized_config["model"]["actions"])
    summary_bundle = _summary_integrated_aggregate_bundle(summary, actions=actions)
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert not (out_dir / "manifest.yaml").exists()
    assert _summary_written_artifacts(summary) == _expected_artifacts(config_path)
    assert normalized_config["outputs"]["write_manifest"] is False
    assert metrics_header == expected_metrics_fields
    assert [
        field for field in metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert summary_bundle == _integrated_aggregate_bundle_from_metrics(
        metric_rows,
        actions=actions,
    )
    assert summary_bundle["task_queue_pressure_and_age"]
    assert summary_bundle["lobe_aggregates"]
    assert summary_bundle["role_action_totals"]


def test_run_api_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_matches_metrics(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_no_manifest_reordered_actions_api_summary_bundle"

    result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=1, out_dir=out_dir)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    actions = tuple(normalized_config["model"]["actions"])
    summary_bundle = _summary_integrated_aggregate_bundle(summary, actions=actions)
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert result.config.to_dict() == normalized_config
    assert result.seed == 1
    assert actions == ("work_task", "create_task", "message", "idle")
    assert normalized_config["outputs"]["write_manifest"] is False
    assert not (out_dir / "manifest.yaml").exists()
    assert _summary_written_artifacts(summary) == _expected_artifacts(
        NO_MANIFEST_REORDERED_ACTIONS
    )
    assert metrics_header == expected_metrics_fields
    assert [
        field for field in metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert summary_bundle == _integrated_aggregate_bundle_from_metrics(
        metric_rows,
        actions=actions,
    )
    assert summary_bundle["task_queue_pressure_and_age"]
    assert summary_bundle["lobe_aggregates"]
    assert summary_bundle["role_action_totals"]


def test_run_api_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reproduces_across_same_seed(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_api_summary_bundle_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_api_summary_bundle_second"

    first_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=first)
    second_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=second)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_actions = tuple(first_config["model"]["actions"])
    second_actions = tuple(second_config["model"]["actions"])
    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=first_actions,
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=second_actions,
    )

    assert first_result.seed == second_result.seed == 17
    assert first_result.config.to_dict() == first_config
    assert second_result.config.to_dict() == second_config
    assert first_result.metrics == second_result.metrics
    assert first_result.events == second_result.events
    assert first_actions == second_actions == ("work_task", "create_task", "message", "idle")
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert not (first / "manifest.yaml").exists()
    assert not (second / "manifest.yaml").exists()
    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=first_actions,
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=second_actions,
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert first_bundle == second_bundle


def test_run_api_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_changes_across_different_seeds(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_api_summary_bundle_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_api_summary_bundle_seed2"

    first_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=1, out_dir=first)
    second_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=2, out_dir=second)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_actions = tuple(first_config["model"]["actions"])
    second_actions = tuple(second_config["model"]["actions"])
    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=first_actions,
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=second_actions,
    )

    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == 1
    assert second_result.seed == 2
    assert first_actions == second_actions == ("work_task", "create_task", "message", "idle")
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert not (first / "manifest.yaml").exists()
    assert not (second / "manifest.yaml").exists()
    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=first_actions,
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=second_actions,
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert second_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert second_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert second_bundle["role_action_totals"]
    assert first_bundle != second_bundle


def test_documented_cli_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reproduces_across_same_seed(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_summary_bundle_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_summary_bundle_second"

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=17)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=17)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_actions = tuple(first_config["model"]["actions"])
    second_actions = tuple(second_config["model"]["actions"])
    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=first_actions,
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=second_actions,
    )

    assert first_config == second_config
    assert first_metric_rows == second_metric_rows
    assert first_actions == second_actions == ("work_task", "create_task", "message", "idle")
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert not (first / "manifest.yaml").exists()
    assert not (second / "manifest.yaml").exists()
    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=first_actions,
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=second_actions,
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert first_bundle == second_bundle


def test_documented_cli_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reconstructs_from_events(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_event_bundle_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_event_bundle_second"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=17)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=17)

    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        first,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest_reordered_actions",
        expected_actions=("work_task", "create_task", "message", "idle"),
    )
    second_event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        second,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest_reordered_actions",
        expected_actions=("work_task", "create_task", "message", "idle"),
    )

    assert first_event_rows == second_event_rows
    assert first_event_bundle["task_queue_pressure_and_age"]
    assert first_event_bundle["lobe_aggregates"]
    assert first_event_bundle["role_action_totals"]
    assert first_event_bundle == second_event_bundle


def test_documented_cli_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_changes_across_different_seeds(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_summary_bundle_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_summary_bundle_seed2"

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=1)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=2)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_actions = tuple(first_config["model"]["actions"])
    second_actions = tuple(second_config["model"]["actions"])
    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=first_actions,
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=second_actions,
    )

    assert first_config == second_config
    assert first_actions == second_actions == ("work_task", "create_task", "message", "idle")
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert not (first / "manifest.yaml").exists()
    assert not (second / "manifest.yaml").exists()
    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=first_actions,
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=second_actions,
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert second_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert second_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert second_bundle["role_action_totals"]
    assert first_bundle != second_bundle


def test_documented_cli_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reconstructs_from_events_across_different_seeds(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_event_bundle_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_event_bundle_seed2"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=1)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=2)

    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        first,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest_reordered_actions",
        expected_actions=("work_task", "create_task", "message", "idle"),
    )
    second_event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        second,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest_reordered_actions",
        expected_actions=("work_task", "create_task", "message", "idle"),
    )

    assert first_event_rows != second_event_rows
    assert first_event_bundle["task_queue_pressure_and_age"]
    assert second_event_bundle["task_queue_pressure_and_age"]
    assert first_event_bundle["lobe_aggregates"]
    assert second_event_bundle["lobe_aggregates"]
    assert first_event_bundle["role_action_totals"]
    assert second_event_bundle["role_action_totals"]
    assert first_event_bundle != second_event_bundle


def test_documented_cli_no_manifest_reordered_actions_per_tick_sequences_reconstruct_from_events(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_event_sequences_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_event_sequences_seed2"

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=1)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=2)

    first_replay = _no_manifest_reordered_actions_event_replay_sequences(first)
    second_replay = _no_manifest_reordered_actions_event_replay_sequences(second)

    assert first_replay["config"] == second_replay["config"]
    assert first_replay["top_level"] == _top_level_metric_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["top_level"] == _top_level_metric_sequence(
        second_replay["metric_rows"]
    )
    assert first_replay["queue_pressure"] == _queue_pressure_metric_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["queue_pressure"] == _queue_pressure_metric_sequence(
        second_replay["metric_rows"]
    )
    assert first_replay["queue_age"] == _queued_task_age_metric_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["queue_age"] == _queued_task_age_metric_sequence(
        second_replay["metric_rows"]
    )
    assert first_replay["role_action"] == _role_action_metric_sequence(
        first_replay["metric_rows"],
        first_replay["actions"],
    )
    assert second_replay["role_action"] == _role_action_metric_sequence(
        second_replay["metric_rows"],
        second_replay["actions"],
    )
    assert first_replay["top_level"]
    assert first_replay["queue_pressure"]
    assert first_replay["queue_age"]
    assert first_replay["role_action"]
    assert (
        first_replay["top_level"],
        first_replay["queue_pressure"],
        first_replay["queue_age"],
        first_replay["role_action"],
    ) != (
        second_replay["top_level"],
        second_replay["queue_pressure"],
        second_replay["queue_age"],
        second_replay["role_action"],
    )


def test_documented_cli_no_manifest_reordered_actions_lobe_sequences_reconstruct_from_events(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_lobe_sequences_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_lobe_sequences_seed2"

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=1)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=2)

    first_replay = _no_manifest_reordered_actions_event_replay_sequences(first)
    second_replay = _no_manifest_reordered_actions_event_replay_sequences(second)
    first_event_lobe_rows = first_replay["event_lobe_rows"]
    second_event_lobe_rows = second_replay["event_lobe_rows"]

    assert first_replay["config"] == second_replay["config"]
    assert set(_lobe_label_sequence(first_event_lobe_rows)) <= set(BASELINE_LOBE_LABELS)
    assert set(_lobe_label_sequence(second_event_lobe_rows)) <= set(BASELINE_LOBE_LABELS)
    assert first_replay["lobe_labels"] == _lobe_label_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["lobe_labels"] == _lobe_label_sequence(
        second_replay["metric_rows"]
    )
    assert first_replay["lobe_transitions"] == _lobe_transition_field_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["lobe_transitions"] == _lobe_transition_field_sequence(
        second_replay["metric_rows"]
    )
    assert first_replay["lobe_run_state"] == _lobe_run_state_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["lobe_run_state"] == _lobe_run_state_sequence(
        second_replay["metric_rows"]
    )
    _assert_lobe_transitions_match_adjacent_labels(first_event_lobe_rows)
    _assert_lobe_transitions_match_adjacent_labels(second_event_lobe_rows)
    _assert_lobe_run_state_matches_recomputed_dwell_runs(first_event_lobe_rows)
    _assert_lobe_run_state_matches_recomputed_dwell_runs(second_event_lobe_rows)
    assert (
        first_replay["lobe_labels"],
        first_replay["lobe_transitions"],
        first_replay["lobe_run_state"],
    ) != (
        second_replay["lobe_labels"],
        second_replay["lobe_transitions"],
        second_replay["lobe_run_state"],
    )


def test_readme_no_manifest_reordered_actions_lobe_replay_smoke_command(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_no_manifest_reordered_actions_readme_smoke"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_no_manifest_reordered_actions.yaml "
        "--seed 1 --out runs/a0_no_manifest_reordered_actions_seed1"
    )

    assert expected_command in readme

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, out_dir, seed=1)

    event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        out_dir,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest_reordered_actions",
        expected_actions=("work_task", "create_task", "message", "idle"),
    )

    assert event_bundle["task_queue_pressure_and_age"]
    assert event_bundle["lobe_aggregates"]
    assert event_bundle["role_action_totals"]


def test_readme_no_manifest_reordered_actions_same_seed_reproduces_enabled_artifacts(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_readme_seed1_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_readme_seed1_second"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_no_manifest_reordered_actions.yaml "
        "--seed 1 --out runs/a0_no_manifest_reordered_actions_seed1"
    )

    assert expected_command in readme
    assert "manifest.yaml" not in artifacts

    for out_dir in [first, second]:
        _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_config_only_same_seed_preserves_normalized_config_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_config_only_readme_seed1_first"
    second = tmp_path / "a0_config_only_readme_seed1_second"
    artifacts = _expected_artifacts(CONFIG_ONLY)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_config_only.yaml "
        "--seed 1 --out runs/a0_config_only_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml"]

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG_ONLY, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        _assert_config_only_writes_normalized_config(out_dir)
        assert not (out_dir / "manifest.yaml").exists()
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_config_only_reordered_actions_same_seed_preserves_normalized_config_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_config_only_reordered_actions_readme_seed1_first"
    second = tmp_path / "a0_config_only_reordered_actions_readme_seed1_second"
    artifacts = _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_config_only_reordered_actions.yaml "
        "--seed 1 --out runs/a0_config_only_reordered_actions_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml"]

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG_ONLY_REORDERED_ACTIONS, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        _assert_config_only_writes_normalized_config(
            out_dir,
            experiment_id="a0_config_only_reordered_actions",
            actions=["work_task", "create_task", "message", "idle"],
        )
        assert not (out_dir / "manifest.yaml").exists()
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_manifest_only_same_seed_preserves_manifest_provenance(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_manifest_only_readme_seed1_first"
    second = tmp_path / "a0_manifest_only_readme_seed1_second"
    artifacts = _expected_artifacts(MANIFEST_ONLY)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_manifest_only.yaml "
        "--seed 1 --out runs/a0_manifest_only_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml", "manifest.yaml"]

    for out_dir in [first, second]:
        _run_documented_cli(MANIFEST_ONLY, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        _assert_manifest_only_preserves_full_schema_provenance(out_dir, MANIFEST_ONLY)

        normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        actions = _actions_from_normalized_config(normalized_config)

        assert normalized_config["run"]["experiment_id"] == "a0_manifest_only"
        assert actions == ["idle", "message", "create_task", "work_task"]
        assert manifest["experiment_id"] == normalized_config["run"]["experiment_id"]
        assert manifest["seed"] == 1
        assert manifest["actions"] == actions
        assert manifest["config"] == normalized_config
        assert manifest["model"]["metrics"]["fields"] == list(
            metrics_fieldnames(tuple(actions))
        )
        assert manifest["model"]["role_action_metrics"]["fields"] == list(
            role_action_metric_fields(tuple(actions))
        )
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_manifest_only_reordered_actions_same_seed_preserves_manifest_provenance(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_manifest_only_reordered_actions_readme_seed1_first"
    second = tmp_path / "a0_manifest_only_reordered_actions_readme_seed1_second"
    artifacts = _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_manifest_only_reordered_actions.yaml "
        "--seed 1 --out runs/a0_manifest_only_reordered_actions_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml", "manifest.yaml"]

    for out_dir in [first, second]:
        _run_documented_cli(MANIFEST_ONLY_REORDERED_ACTIONS, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        _assert_manifest_only_preserves_full_schema_provenance(
            out_dir,
            MANIFEST_ONLY_REORDERED_ACTIONS,
        )

        normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        actions = _actions_from_normalized_config(normalized_config)

        assert normalized_config["run"]["experiment_id"] == "a0_manifest_only_reordered_actions"
        assert actions == ["work_task", "create_task", "message", "idle"]
        assert manifest["experiment_id"] == normalized_config["run"]["experiment_id"]
        assert manifest["seed"] == 1
        assert manifest["actions"] == actions
        assert manifest["config"] == normalized_config
        assert manifest["model"]["metrics"]["fields"] == list(
            metrics_fieldnames(tuple(actions))
        )
        assert manifest["model"]["role_action_metrics"]["fields"] == list(
            role_action_metric_fields(tuple(actions))
        )

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_no_manifest_same_seed_preserves_emitted_schema_provenance(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_readme_seed1_first"
    second = tmp_path / "a0_no_manifest_readme_seed1_second"
    artifacts = _expected_artifacts(NO_MANIFEST)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_no_manifest.yaml "
        "--seed 1 --out runs/a0_no_manifest_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml", "metrics.csv", "events.csv", "summary.md"]

    for out_dir in [first, second]:
        _run_documented_cli(NO_MANIFEST, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)

        normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
        actions = _actions_from_normalized_config(normalized_config)
        summary = (out_dir / "summary.md").read_text()
        with (out_dir / "metrics.csv").open() as handle:
            metrics_header = next(csv.reader(handle))
        with (out_dir / "events.csv").open() as handle:
            events_header = next(csv.reader(handle))

        assert normalized_config["run"]["experiment_id"] == "a0_no_manifest"
        assert normalized_config["outputs"] == {
            "write_manifest": False,
            "write_metrics": True,
            "write_events": True,
            "write_summary": True,
        }
        assert actions == ["idle", "message", "create_task", "work_task"]
        assert metrics_header == list(metrics_fieldnames(tuple(actions)))
        assert [
            field for field in metrics_header if field.startswith("role_")
        ] == list(role_action_metric_fields(tuple(actions)))
        assert events_header == list(EVENT_FIELDS)
        assert _summary_written_artifacts(summary) == artifacts
        assert "- manifest mirrors emitted artifact schemas: yes" in summary
        assert not (out_dir / "manifest.yaml").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_no_manifest_default_actions_event_replay_bundle_reproducibility(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_readme_event_bundle_first"
    second = tmp_path / "a0_no_manifest_readme_event_bundle_second"
    different = tmp_path / "a0_no_manifest_readme_event_bundle_different"
    artifacts = _expected_artifacts(NO_MANIFEST)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_no_manifest.yaml "
        "--seed 1 --out runs/a0_no_manifest_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml", "metrics.csv", "events.csv", "summary.md"]

    _run_documented_cli(NO_MANIFEST, first, seed=17)
    _run_documented_cli(NO_MANIFEST, second, seed=17)
    _run_documented_cli(NO_MANIFEST, different, seed=18)

    bundles = []
    for out_dir in [first, second, different]:
        bundles.append(
            _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
                out_dir,
                expected_artifacts=artifacts,
                expected_experiment_id="a0_no_manifest",
                expected_actions=("idle", "message", "create_task", "work_task"),
            )
        )

    assert bundles[0]
    assert bundles[0] == bundles[1]
    assert bundles[0] != bundles[2]


def test_documented_cli_no_manifest_default_actions_event_replay_reconstructs_lobes_queue_and_roles(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_no_manifest_default_actions_event_replay"
    artifacts = _expected_artifacts(NO_MANIFEST)

    _run_documented_cli(NO_MANIFEST, out_dir, seed=1)
    _assert_artifacts_match_output_directory(out_dir, artifacts)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        out_dir,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest",
        expected_actions=("idle", "message", "create_task", "work_task"),
    )

    assert normalized_config["run"]["experiment_id"] == "a0_no_manifest"
    assert normalized_config["outputs"]["write_manifest"] is False
    assert not (out_dir / "manifest.yaml").exists()
    assert event_bundle["task_queue_pressure_and_age"]
    assert event_bundle["lobe_aggregates"]
    assert event_bundle["role_action_totals"]


def test_run_api_no_manifest_default_actions_event_replay_reconstructs_lobes_queue_and_roles(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_no_manifest_default_actions_api_event_replay"
    artifacts = _expected_artifacts(NO_MANIFEST)

    result = run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)
    _assert_artifacts_match_output_directory(out_dir, artifacts)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        out_dir,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest",
        expected_actions=("idle", "message", "create_task", "work_task"),
    )

    assert result.config.to_dict() == normalized_config
    assert result.seed == 1
    assert normalized_config["run"]["experiment_id"] == "a0_no_manifest"
    assert normalized_config["outputs"]["write_manifest"] is False
    assert not (out_dir / "manifest.yaml").exists()
    assert len(result.metrics) == normalized_config["run"]["ticks"]
    assert len(result.events) == (
        normalized_config["run"]["ticks"] * normalized_config["model"]["agent_count"]
    )
    assert event_bundle["task_queue_pressure_and_age"]
    assert event_bundle["lobe_aggregates"]
    assert event_bundle["role_action_totals"]


def test_run_api_no_manifest_default_actions_event_replay_bundle_reproducibility(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_default_actions_api_event_bundle_first"
    second = tmp_path / "a0_no_manifest_default_actions_api_event_bundle_second"
    different = tmp_path / "a0_no_manifest_default_actions_api_event_bundle_different"
    artifacts = _expected_artifacts(NO_MANIFEST)

    run_experiment(NO_MANIFEST, seed=17, out_dir=first)
    run_experiment(NO_MANIFEST, seed=17, out_dir=second)
    run_experiment(NO_MANIFEST, seed=18, out_dir=different)

    bundles = []
    for out_dir in [first, second, different]:
        bundles.append(
            _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
                out_dir,
                expected_artifacts=artifacts,
                expected_experiment_id="a0_no_manifest",
                expected_actions=("idle", "message", "create_task", "work_task"),
            )
        )

    assert bundles[0]
    assert bundles[0] == bundles[1]
    assert bundles[0] != bundles[2]


def test_documented_cli_no_manifest_default_actions_event_replay_bundle_reproducibility(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_default_actions_cli_event_bundle_first"
    second = tmp_path / "a0_no_manifest_default_actions_cli_event_bundle_second"
    different = tmp_path / "a0_no_manifest_default_actions_cli_event_bundle_different"
    artifacts = _expected_artifacts(NO_MANIFEST)

    _run_documented_cli(NO_MANIFEST, first, seed=17)
    _run_documented_cli(NO_MANIFEST, second, seed=17)
    _run_documented_cli(NO_MANIFEST, different, seed=18)

    bundles = []
    for out_dir in [first, second, different]:
        bundles.append(
            _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
                out_dir,
                expected_artifacts=artifacts,
                expected_experiment_id="a0_no_manifest",
                expected_actions=("idle", "message", "create_task", "work_task"),
            )
        )

    assert bundles[0]
    assert bundles[0] == bundles[1]
    assert bundles[0] != bundles[2]


def test_readme_default_outputs_same_seed_preserves_full_schema_provenance(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_default_outputs_readme_seed1_first"
    second = tmp_path / "a0_default_outputs_readme_seed1_second"
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_default_outputs.yaml "
        "--seed 1 --out runs/a0_default_outputs_seed1"
    )

    assert expected_command in readme
    assert artifacts == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    for out_dir in [first, second]:
        _run_documented_cli(DEFAULT_OUTPUTS, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)

        normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        summary = (out_dir / "summary.md").read_text()
        with (out_dir / "metrics.csv").open() as handle:
            metrics_header = next(csv.reader(handle))
        with (out_dir / "events.csv").open() as handle:
            events_header = next(csv.reader(handle))

        actions = _actions_from_normalized_config(normalized_config)

        assert normalized_config["run"]["experiment_id"] == "a0_default_outputs"
        assert normalized_config["outputs"] == {
            "write_manifest": True,
            "write_metrics": True,
            "write_events": True,
            "write_summary": True,
        }
        assert actions == ["idle", "message", "create_task", "work_task"]
        assert manifest["experiment_id"] == normalized_config["run"]["experiment_id"]
        assert manifest["seed"] == 1
        assert manifest["actions"] == actions
        assert manifest["outputs"] == normalized_config["outputs"]
        assert manifest["artifacts"] == artifacts
        assert manifest["config"] == normalized_config
        assert manifest["model"]["metrics"]["fields"] == list(
            metrics_fieldnames(tuple(actions))
        )
        assert manifest["model"]["role_action_metrics"]["actions"] == actions
        assert manifest["model"]["role_action_metrics"]["fields"] == list(
            role_action_metric_fields(tuple(actions))
        )
        assert metrics_header == manifest["model"]["metrics"]["fields"]
        assert [
            field for field in metrics_header if field.startswith("role_")
        ] == manifest["model"]["role_action_metrics"]["fields"]
        assert events_header == manifest["model"]["events"]["fields"]
        assert _summary_written_artifacts(summary) == artifacts
        _assert_summary_schema_provenance_counts_match_manifest(summary, manifest)
        _assert_summary_output_flags_match_config(summary, normalized_config["outputs"])

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_a0_smoke_first_milestone_command_preserves_full_schema_provenance(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_smoke_readme_seed1"
    artifacts = _expected_artifacts(CONFIG)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_smoke.yaml "
        "--seed 1 --out runs/a0_seed1"
    )

    assert expected_command in readme
    assert artifacts == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    _run_documented_cli(CONFIG, out_dir, seed=1)
    _assert_artifacts_match_output_directory(out_dir, artifacts)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
        metric_rows = list(csv.DictReader(handle, fieldnames=metrics_header))
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))
        event_rows = list(csv.DictReader(handle, fieldnames=events_header))

    actions = _actions_from_normalized_config(normalized_config)

    assert normalized_config["run"]["experiment_id"] == "a0_smoke"
    assert normalized_config["run"]["ticks"] == 100
    assert normalized_config["model"]["agent_count"] == 15
    assert normalized_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert len(metric_rows) == normalized_config["run"]["ticks"]
    assert len(event_rows) == (
        normalized_config["run"]["ticks"] * normalized_config["model"]["agent_count"]
    )
    assert manifest["experiment_id"] == normalized_config["run"]["experiment_id"]
    assert manifest["seed"] == 1
    assert manifest["ticks"] == normalized_config["run"]["ticks"]
    assert manifest["agent_count"] == normalized_config["model"]["agent_count"]
    assert manifest["actions"] == actions
    assert manifest["outputs"] == normalized_config["outputs"]
    assert manifest["artifacts"] == artifacts
    assert manifest["config"] == normalized_config
    assert manifest["model"]["metrics"]["fields"] == list(metrics_fieldnames(tuple(actions)))
    assert manifest["model"]["events"]["fields"] == list(EVENT_FIELDS)
    assert manifest["model"]["role_action_metrics"]["fields"] == list(
        role_action_metric_fields(tuple(actions))
    )
    assert metrics_header == manifest["model"]["metrics"]["fields"]
    assert events_header == manifest["model"]["events"]["fields"]
    assert _summary_written_artifacts(summary) == artifacts
    _assert_config_manifest_and_summary_run_fields_match(
        normalized_config,
        manifest=manifest,
        summary=summary,
        seed=1,
    )
    _assert_manifest_agent_identity_and_roles_match_baseline(manifest)
    _assert_summary_schema_provenance_counts_match_manifest(summary, manifest)
    _assert_summary_output_flags_match_config(summary, normalized_config["outputs"])


def test_readme_a0_smoke_same_seed_reproduces_full_first_milestone_artifacts(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_smoke_readme_seed1_first"
    second = tmp_path / "a0_smoke_readme_seed1_second"
    artifacts = _expected_artifacts(CONFIG)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_smoke.yaml "
        "--seed 1 --out runs/a0_seed1"
    )

    assert expected_command in readme
    assert artifacts == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)

        normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        with (out_dir / "metrics.csv").open() as handle:
            metric_rows = list(csv.DictReader(handle))
        with (out_dir / "events.csv").open() as handle:
            event_rows = list(csv.DictReader(handle))

        assert normalized_config["run"]["experiment_id"] == "a0_smoke"
        assert normalized_config["run"]["ticks"] == 100
        assert normalized_config["model"]["agent_count"] == 15
        assert manifest["seed"] == 1
        assert manifest["artifacts"] == artifacts
        assert len(metric_rows) == normalized_config["run"]["ticks"]
        assert len(event_rows) == (
            normalized_config["run"]["ticks"] * normalized_config["model"]["agent_count"]
        )

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_a0_smoke_different_seed_changes_dynamics_preserving_provenance(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_smoke_readme_seed1"
    second = tmp_path / "a0_smoke_readme_seed2"
    artifacts = _expected_artifacts(CONFIG)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_smoke.yaml "
        "--seed 1 --out runs/a0_seed1"
    )

    assert expected_command in readme
    assert artifacts == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    _run_documented_cli(CONFIG, first, seed=1)
    _run_documented_cli(CONFIG, second, seed=2)

    for out_dir in [first, second]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()

    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
        first_metric_rows = list(csv.DictReader(handle, fieldnames=first_metrics_header))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
        second_metric_rows = list(csv.DictReader(handle, fieldnames=second_metrics_header))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
        first_event_rows = list(csv.DictReader(handle, fieldnames=first_events_header))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))
        second_event_rows = list(csv.DictReader(handle, fieldnames=second_events_header))

    actions = tuple(_actions_from_normalized_config(first_config))

    assert first_config == second_config
    assert first_manifest["seed"] == 1
    assert second_manifest["seed"] == 2
    assert first_manifest["config"] == second_manifest["config"] == first_config
    assert first_manifest["actions"] == second_manifest["actions"] == list(actions)
    assert first_manifest["outputs"] == second_manifest["outputs"] == first_config["outputs"]
    assert first_manifest["artifacts"] == second_manifest["artifacts"] == artifacts
    assert first_manifest["model"] == second_manifest["model"]
    assert first_metrics_header == second_metrics_header == list(metrics_fieldnames(actions))
    assert first_events_header == second_events_header == list(EVENT_FIELDS)
    assert len(first_metric_rows) == len(second_metric_rows) == first_config["run"]["ticks"]
    assert len(first_event_rows) == len(second_event_rows) == (
        first_config["run"]["ticks"] * first_config["model"]["agent_count"]
    )
    _assert_summary_schema_provenance_counts_match_manifest(first_summary, first_manifest)
    _assert_summary_schema_provenance_counts_match_manifest(second_summary, second_manifest)

    assert first_metric_rows != second_metric_rows
    assert first_event_rows != second_event_rows
    assert _summary_integrated_aggregate_bundle(
        first_summary,
        actions=actions,
    ) != _summary_integrated_aggregate_bundle(
        second_summary,
        actions=actions,
    )


def test_readme_a0_smoke_event_replay_reconstructs_first_milestone_summaries(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_smoke_readme_event_replay"
    artifacts = _expected_artifacts(CONFIG)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_smoke.yaml "
        "--seed 1 --out runs/a0_seed1"
    )

    assert expected_command in readme
    assert artifacts == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    _run_documented_cli(CONFIG, out_dir, seed=1)
    _assert_artifacts_match_output_directory(out_dir, artifacts)

    _assert_full_output_event_replay_matches_metrics_and_summary(
        out_dir,
        expected_experiment_id="a0_smoke",
        expected_ticks=100,
        expected_artifacts=artifacts,
    )


@pytest.mark.parametrize("config_path", (DEFAULT_OUTPUTS, REORDERED_ACTIONS))
def test_documented_cli_full_output_fixture_event_replay_reconstructs_summaries(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_event_replay"
    artifacts = _expected_artifacts(config_path)
    expected_ticks = load_config(config_path).run.ticks

    _run_documented_cli(config_path, out_dir, seed=1)
    _assert_artifacts_match_output_directory(out_dir, artifacts)

    _assert_full_output_event_replay_matches_metrics_and_summary(
        out_dir,
        expected_experiment_id=config_path.stem,
        expected_ticks=expected_ticks,
        expected_artifacts=artifacts,
    )


def test_documented_cli_no_manifest_reordered_actions_seed_difference_preserves_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_seed2"

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=1)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=2)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = tuple(first_config["model"]["actions"])
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert actions == ("work_task", "create_task", "message", "idle")
    assert second_config["model"]["actions"] == list(actions)
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert not (first / "manifest.yaml").exists()
    assert not (second / "manifest.yaml").exists()
    assert _summary_written_artifacts(first_summary) == _expected_artifacts(
        NO_MANIFEST_REORDERED_ACTIONS
    )
    assert _summary_written_artifacts(second_summary) == _expected_artifacts(
        NO_MANIFEST_REORDERED_ACTIONS
    )
    assert first_metrics_header == expected_metrics_fields
    assert second_metrics_header == expected_metrics_fields
    assert first_events_header == list(EVENT_FIELDS)
    assert second_events_header == list(EVENT_FIELDS)
    assert [
        field for field in first_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert [
        field for field in second_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


def test_documented_cli_no_manifest_reordered_actions_same_seed_reproduces_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_seed17_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_seed17_second"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    for out_dir in [first, second]:
        _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, out_dir, seed=17)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = tuple(first_config["model"]["actions"])
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert actions == ("work_task", "create_task", "message", "idle")
    assert second_config["model"]["actions"] == list(actions)
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert _summary_written_artifacts(first_summary) == artifacts
    assert _summary_written_artifacts(second_summary) == artifacts
    assert first_metrics_header == expected_metrics_fields
    assert second_metrics_header == expected_metrics_fields
    assert first_events_header == list(EVENT_FIELDS)
    assert second_events_header == list(EVENT_FIELDS)
    assert [
        field for field in first_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert [
        field for field in second_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_run_api_no_manifest_reordered_actions_same_seed_reproduces_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_api_seed17_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_api_seed17_second"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    first_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=first)
    second_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=second)

    for out_dir in [first, second]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = tuple(first_config["model"]["actions"])
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == second_result.seed == 17
    assert first_result.metrics == second_result.metrics
    assert first_result.events == second_result.events
    assert actions == ("work_task", "create_task", "message", "idle")
    assert second_config["model"]["actions"] == list(actions)
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert _summary_written_artifacts(first_summary) == artifacts
    assert _summary_written_artifacts(second_summary) == artifacts
    assert first_metrics_header == expected_metrics_fields
    assert second_metrics_header == expected_metrics_fields
    assert first_events_header == list(EVENT_FIELDS)
    assert second_events_header == list(EVENT_FIELDS)
    assert [
        field for field in first_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert [
        field for field in second_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_run_api_no_manifest_reordered_actions_seed_difference_preserves_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_api_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_api_seed2"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    first_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=1, out_dir=first)
    second_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=2, out_dir=second)

    for out_dir in [first, second]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = tuple(first_config["model"]["actions"])
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == 1
    assert second_result.seed == 2
    assert actions == ("work_task", "create_task", "message", "idle")
    assert second_config["model"]["actions"] == list(actions)
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert _summary_written_artifacts(first_summary) == artifacts
    assert _summary_written_artifacts(second_summary) == artifacts
    assert first_metrics_header == expected_metrics_fields
    assert second_metrics_header == expected_metrics_fields
    assert first_events_header == list(EVENT_FIELDS)
    assert second_events_header == list(EVENT_FIELDS)
    assert [
        field for field in first_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert [
        field for field in second_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert (
        first_result.metrics != second_result.metrics
        or first_result.events != second_result.events
    )
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_task_queue_pressure_and_age_aggregate_tuple_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_queue_integrity_seed1",
        second_name=f"{config_path.stem}_cli_summary_queue_integrity_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_tuple = _summary_task_queue_pressure_and_age_aggregate_tuple(first_summary)
    second_tuple = _summary_task_queue_pressure_and_age_aggregate_tuple(second_summary)

    assert first_tuple == _task_queue_pressure_and_age_aggregate_tuple_from_metrics(
        first_metric_rows
    )
    assert second_tuple == _task_queue_pressure_and_age_aggregate_tuple_from_metrics(
        second_metric_rows
    )
    assert first_tuple["task_queue_totals"]
    assert second_tuple["task_queue_totals"]
    assert first_tuple["queue_pressure_totals"]
    assert second_tuple["queue_pressure_totals"]
    assert first_tuple["queued_task_age_aggregates"]
    assert second_tuple["queued_task_age_aggregates"]
    assert first_tuple != second_tuple


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_queued_task_age_metric_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_event_replayed_queue_age_first",
        second_name=f"{config_path.stem}_cli_event_replayed_queue_age_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _queued_task_age_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _queued_task_age_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _queued_task_age_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _queued_task_age_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert first_replayed_sequence == second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_queued_task_age_metric_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_event_replayed_queue_age_seed1",
        second_name=f"{config_path.stem}_cli_event_replayed_queue_age_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _queued_task_age_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _queued_task_age_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _queued_task_age_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _queued_task_age_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert second_replayed_sequence
    assert first_replayed_sequence != second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_role_action_summary_totals_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_role_action_summary_seed1",
        second_name=f"{config_path.stem}_cli_role_action_summary_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_role_action_totals = _summary_role_action_totals(first_summary)
    second_role_action_totals = _summary_role_action_totals(second_summary)
    first_actions = tuple(first_manifest["actions"])
    second_actions = tuple(second_manifest["actions"])

    assert first_role_action_totals == _role_action_totals_from_metrics(
        first_metric_rows,
        first_actions,
    )
    assert second_role_action_totals == _role_action_totals_from_metrics(
        second_metric_rows,
        second_actions,
    )
    assert first_role_action_totals
    assert second_role_action_totals
    assert first_role_action_totals != second_role_action_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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

    first_actions = tuple(first_manifest["actions"])
    second_actions = tuple(second_manifest["actions"])
    first_expected_fields = list(role_action_metric_fields(first_actions))
    second_expected_fields = list(role_action_metric_fields(second_actions))
    first_sequence = _role_action_metric_sequence(first_metric_rows, first_actions)
    second_sequence = _role_action_metric_sequence(second_metric_rows, second_actions)

    assert first_manifest["model"]["role_action_metrics"]["fields"] == first_expected_fields
    assert second_manifest["model"]["role_action_metrics"]["fields"] == second_expected_fields
    assert [field for field in first_header if field.startswith("role_")] == first_expected_fields
    assert [field for field in second_header if field.startswith("role_")] == second_expected_fields
    assert first_sequence
    assert second_sequence
    assert first_sequence != second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
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
        (
            CONFIG_ONLY_REORDERED_ACTIONS,
            _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
        ),
        (MANIFEST_ONLY, _expected_artifacts(MANIFEST_ONLY)),
        (
            MANIFEST_ONLY_REORDERED_ACTIONS,
            _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS),
        ),
        (NO_MANIFEST, _expected_artifacts(NO_MANIFEST)),
        (
            NO_MANIFEST_REORDERED_ACTIONS,
            _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS),
        ),
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


@pytest.mark.parametrize("config_path", MANIFEST_ONLY_FIXTURES)
def test_manifest_only_records_full_schema_provenance_without_disabled_artifacts(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_schema"

    run_experiment(config_path, seed=1, out_dir=out_dir)

    _assert_manifest_only_preserves_full_schema_provenance(out_dir, config_path)


def test_manifest_only_reordered_actions_records_schema_order_without_disabled_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_reordered_actions_schema"

    run_experiment(MANIFEST_ONLY_REORDERED_ACTIONS, seed=1, out_dir=out_dir)

    _assert_manifest_only_preserves_full_schema_provenance(
        out_dir,
        MANIFEST_ONLY_REORDERED_ACTIONS,
    )

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    actions = _actions_from_normalized_config(normalized_config)
    expected_role_action_fields = list(role_action_metric_fields(tuple(actions)))
    expected_metrics_fields = list(metrics_fieldnames(tuple(actions)))

    assert actions == ["work_task", "create_task", "message", "idle"]
    assert manifest["actions"] == actions
    assert manifest["config"]["model"]["actions"] == actions
    assert manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert manifest["model"]["role_action_metrics"]["actions"] == actions
    assert manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields


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


@pytest.mark.parametrize("config_path", MANIFEST_ONLY_FIXTURES)
def test_documented_cli_manifest_only_records_full_schema_provenance_without_disabled_artifacts(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_schema"

    _run_documented_cli(config_path, out_dir)

    _assert_manifest_only_preserves_full_schema_provenance(out_dir, config_path)


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


@pytest.mark.parametrize("config_path", NO_MANIFEST_FIXTURES)
def test_documented_cli_no_manifest_emitted_artifacts_preserve_schema_provenance(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_schema"

    _run_documented_cli(config_path, out_dir)

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


@pytest.mark.parametrize("config_path", NO_MANIFEST_FIXTURES)
def test_run_api_no_manifest_emitted_artifacts_preserve_schema_provenance(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_api_schema"

    result = run_experiment(config_path, seed=1, out_dir=out_dir)

    assert result.config.run.experiment_id == load_config(config_path).run.experiment_id
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
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)
    first, second, _, _ = _run_documented_cli_pair(
        DEFAULT_OUTPUTS,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name="default_outputs_seed17_first",
        second_name="default_outputs_seed17_second",
    )

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


@pytest.mark.parametrize("config_path", (DEFAULT_OUTPUTS, REORDERED_ACTIONS))
def test_documented_cli_full_output_fixture_same_seed_reproduces_byte_identical_enabled_artifacts(
    tmp_path: Path,
    config_path: Path,
) -> None:
    artifacts = _expected_artifacts(config_path)

    assert artifacts == A0_FULL_ARTIFACTS

    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_full_output_seed17_first",
        second_name=f"{config_path.stem}_full_output_seed17_second",
    )

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    actions = _actions_from_normalized_config(first_config)

    assert first_config == second_config
    assert first_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert first_manifest["experiment_id"] == first_config["run"]["experiment_id"]
    assert second_manifest["experiment_id"] == second_config["run"]["experiment_id"]
    assert first_manifest["actions"] == second_manifest["actions"] == actions
    assert first_manifest["artifacts"] == second_manifest["artifacts"] == artifacts

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_documented_cli_reordered_actions_different_seed_preserves_full_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_reordered_actions_seed1"
    second = tmp_path / "a0_reordered_actions_seed2"
    artifacts = _expected_artifacts(REORDERED_ACTIONS)

    for seed, out_dir in [(1, first), (2, second)]:
        _run_documented_cli(REORDERED_ACTIONS, out_dir, seed=seed)
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = _actions_from_normalized_config(first_config)
    expected_metrics_fields = list(metrics_fieldnames(tuple(actions)))

    assert actions == ["work_task", "create_task", "message", "idle"]
    assert first_config == second_config
    assert first_manifest["seed"] == 1
    assert second_manifest["seed"] == 2
    assert first_manifest["config"] == second_manifest["config"] == first_config
    assert first_manifest["actions"] == second_manifest["actions"] == actions
    assert first_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert second_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert first_manifest["model"]["events"]["fields"] == list(EVENT_FIELDS)
    assert second_manifest["model"]["events"]["fields"] == list(EVENT_FIELDS)
    assert first_metrics_header == second_metrics_header == expected_metrics_fields
    assert first_events_header == second_events_header == list(EVENT_FIELDS)
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


def test_documented_cli_default_outputs_different_seed_preserves_full_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_default_outputs_seed1"
    second = tmp_path / "a0_default_outputs_seed2"
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    for seed, out_dir in [(1, first), (2, second)]:
        _run_documented_cli(DEFAULT_OUTPUTS, out_dir, seed=seed)
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = _actions_from_normalized_config(first_config)
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(tuple(actions)))

    assert artifacts == A0_FULL_ARTIFACTS
    assert actions == ["idle", "message", "create_task", "work_task"]
    assert first_config == second_config
    assert first_config["outputs"] == expected_outputs
    assert first_manifest["seed"] == 1
    assert second_manifest["seed"] == 2
    assert first_manifest["outputs"] == second_manifest["outputs"] == expected_outputs
    assert first_manifest["config"] == second_manifest["config"] == first_config
    assert first_manifest["actions"] == second_manifest["actions"] == actions
    assert first_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert second_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert first_manifest["model"]["events"]["fields"] == list(EVENT_FIELDS)
    assert second_manifest["model"]["events"]["fields"] == list(EVENT_FIELDS)
    assert first_metrics_header == second_metrics_header == expected_metrics_fields
    assert first_events_header == second_events_header == list(EVENT_FIELDS)
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


def test_documented_cli_no_manifest_different_seed_preserves_emitted_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_seed1"
    second = tmp_path / "a0_no_manifest_seed2"
    artifacts = _expected_artifacts(NO_MANIFEST)

    for seed, out_dir in [(1, first), (2, second)]:
        _run_documented_cli(NO_MANIFEST, out_dir, seed=seed)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = _actions_from_normalized_config(first_config)
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(tuple(actions)))

    assert artifacts == NO_MANIFEST_ARTIFACTS
    assert actions == ["idle", "message", "create_task", "work_task"]
    assert first_config == second_config
    assert first_config["outputs"] == expected_outputs
    assert second_config["outputs"] == expected_outputs
    assert first_metrics_header == second_metrics_header == expected_metrics_fields
    assert first_events_header == second_events_header == list(EVENT_FIELDS)
    assert _summary_written_artifacts(first_summary) == artifacts
    assert _summary_written_artifacts(second_summary) == artifacts
    for summary in [first_summary, second_summary]:
        _assert_summary_records_artifact_schema_provenance(
            summary,
            metrics_header=first_metrics_header,
            events_header=first_events_header,
            actions=tuple(actions),
        )
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


def test_run_api_no_manifest_different_seed_preserves_emitted_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_api_seed1"
    second = tmp_path / "a0_no_manifest_api_seed2"
    artifacts = _expected_artifacts(NO_MANIFEST)

    first_result = run_experiment(NO_MANIFEST, seed=1, out_dir=first)
    second_result = run_experiment(NO_MANIFEST, seed=2, out_dir=second)

    for out_dir in [first, second]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()
        _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = tuple(first_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))

    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == 1
    assert second_result.seed == 2
    assert artifacts == NO_MANIFEST_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert second_config["model"]["actions"] == list(actions)
    assert first_config["outputs"] == expected_outputs
    assert second_config["outputs"] == expected_outputs
    assert first_metrics_header == second_metrics_header == expected_metrics_fields
    assert first_events_header == second_events_header == list(EVENT_FIELDS)
    assert _summary_written_artifacts(first_summary) == artifacts
    assert _summary_written_artifacts(second_summary) == artifacts
    assert (
        first_result.metrics != second_result.metrics
        or first_result.events != second_result.events
    )
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


def test_documented_cli_and_run_api_default_outputs_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_default_outputs_cli_seed1"
    api_out = tmp_path / "a0_default_outputs_api_seed1"
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    _run_documented_cli(DEFAULT_OUTPUTS, cli_out, seed=1)
    result = run_experiment(DEFAULT_OUTPUTS, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    cli_manifest = yaml.safe_load((cli_out / "manifest.yaml").read_text())
    api_manifest = yaml.safe_load((api_out / "manifest.yaml").read_text())
    with (api_out / "metrics.csv").open() as handle:
        api_metrics_header = next(csv.reader(handle))
    with (api_out / "events.csv").open() as handle:
        api_events_header = next(csv.reader(handle))
    api_summary = (api_out / "summary.md").read_text()
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    assert artifacts == A0_FULL_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert cli_config == api_config
    assert cli_manifest == api_manifest
    assert api_config["outputs"] == expected_outputs
    assert api_manifest["outputs"] == expected_outputs
    assert api_manifest["artifacts"] == artifacts
    assert api_manifest["actions"] == list(actions)
    assert api_manifest["config"] == api_config
    assert api_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert api_manifest["model"]["role_action_metrics"]["actions"] == list(actions)
    assert api_manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert api_metrics_header == expected_metrics_fields
    assert api_events_header == list(EVENT_FIELDS)
    assert _summary_written_artifacts(api_summary) == artifacts
    _assert_summary_records_artifact_schema_provenance(
        api_summary,
        metrics_header=api_metrics_header,
        events_header=api_events_header,
        actions=actions,
    )
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_smoke_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_smoke_cli_seed1"
    api_out = tmp_path / "a0_smoke_api_seed1"
    artifacts = _expected_artifacts(CONFIG)

    _run_documented_cli(CONFIG, cli_out, seed=1)
    result = run_experiment(CONFIG, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    cli_manifest = yaml.safe_load((cli_out / "manifest.yaml").read_text())
    api_manifest = yaml.safe_load((api_out / "manifest.yaml").read_text())
    with (api_out / "metrics.csv").open() as handle:
        api_metrics_rows = list(csv.reader(handle))
    with (api_out / "events.csv").open() as handle:
        api_events_rows = list(csv.reader(handle))
    api_metrics_header = api_metrics_rows[0]
    api_events_header = api_events_rows[0]
    api_summary = (api_out / "summary.md").read_text()
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    assert artifacts == A0_FULL_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert cli_config == api_config
    assert cli_manifest == api_manifest
    assert api_config["run"]["experiment_id"] == "a0_smoke"
    assert api_config["run"]["ticks"] == 100
    assert api_config["outputs"] == expected_outputs
    assert api_manifest["experiment_id"] == "a0_smoke"
    assert api_manifest["seed"] == 1
    assert api_manifest["ticks"] == 100
    assert api_manifest["outputs"] == expected_outputs
    assert api_manifest["artifacts"] == artifacts
    assert api_manifest["actions"] == list(actions)
    assert api_manifest["config"] == api_config
    assert api_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert api_manifest["model"]["role_action_metrics"]["actions"] == list(actions)
    assert api_manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert len(api_metrics_rows) == 101
    assert len(api_events_rows) == 1501
    assert len(result.metrics) == 100
    assert len(result.events) == 1500
    assert api_metrics_header == expected_metrics_fields
    assert api_events_header == list(EVENT_FIELDS)
    assert _summary_written_artifacts(api_summary) == artifacts
    _assert_summary_records_artifact_schema_provenance(
        api_summary,
        metrics_header=api_metrics_header,
        events_header=api_events_header,
        actions=actions,
    )
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_reordered_actions_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_reordered_actions_cli_seed1"
    api_out = tmp_path / "a0_reordered_actions_api_seed1"
    artifacts = _expected_artifacts(REORDERED_ACTIONS)

    _run_documented_cli(REORDERED_ACTIONS, cli_out, seed=1)
    result = run_experiment(REORDERED_ACTIONS, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    cli_manifest = yaml.safe_load((cli_out / "manifest.yaml").read_text())
    api_manifest = yaml.safe_load((api_out / "manifest.yaml").read_text())
    with (api_out / "metrics.csv").open() as handle:
        api_metrics_header = next(csv.reader(handle))
    with (api_out / "events.csv").open() as handle:
        api_events_header = next(csv.reader(handle))
    api_summary = (api_out / "summary.md").read_text()
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    assert artifacts == A0_FULL_ARTIFACTS
    assert actions == ("work_task", "create_task", "message", "idle")
    assert cli_config == api_config
    assert cli_manifest == api_manifest
    assert api_config["outputs"] == expected_outputs
    assert api_manifest["outputs"] == expected_outputs
    assert api_manifest["artifacts"] == artifacts
    assert api_manifest["actions"] == list(actions)
    assert api_manifest["config"] == api_config
    assert api_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert api_manifest["model"]["role_action_metrics"]["actions"] == list(actions)
    assert api_manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert api_metrics_header == expected_metrics_fields
    assert api_events_header == list(EVENT_FIELDS)
    assert _summary_written_artifacts(api_summary) == artifacts
    _assert_summary_records_artifact_schema_provenance(
        api_summary,
        metrics_header=api_metrics_header,
        events_header=api_events_header,
        actions=actions,
    )
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_no_manifest_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_no_manifest_cli_seed1"
    api_out = tmp_path / "a0_no_manifest_api_seed1"
    artifacts = _expected_artifacts(NO_MANIFEST)

    _run_documented_cli(NO_MANIFEST, cli_out, seed=1)
    result = run_experiment(NO_MANIFEST, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    with (api_out / "metrics.csv").open() as handle:
        api_metrics_rows = list(csv.reader(handle))
    with (api_out / "events.csv").open() as handle:
        api_events_rows = list(csv.reader(handle))
    api_metrics_header = api_metrics_rows[0]
    api_events_header = api_events_rows[0]
    api_summary = (api_out / "summary.md").read_text()
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()
        _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)

    assert artifacts == NO_MANIFEST_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert cli_config == api_config
    assert api_config["run"]["experiment_id"] == "a0_no_manifest"
    assert api_config["run"]["ticks"] == 3
    assert api_config["outputs"] == expected_outputs
    assert api_metrics_header == expected_metrics_fields
    assert api_events_header == list(EVENT_FIELDS)
    assert [
        field for field in api_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert len(api_metrics_rows) == 4
    assert len(api_events_rows) == 46
    assert len(result.metrics) == 3
    assert len(result.events) == 45
    assert _summary_written_artifacts(api_summary) == artifacts
    _assert_summary_records_artifact_schema_provenance(
        api_summary,
        metrics_header=api_metrics_header,
        events_header=api_events_header,
        actions=actions,
    )
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_no_manifest_reordered_actions_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_no_manifest_reordered_actions_cli_seed1"
    api_out = tmp_path / "a0_no_manifest_reordered_actions_api_seed1"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, cli_out, seed=1)
    result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()
        _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)

    assert artifacts == NO_MANIFEST_ARTIFACTS
    assert actions == ("work_task", "create_task", "message", "idle")
    assert cli_config == api_config
    assert api_config["outputs"] == expected_outputs
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_config_only_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_config_only_cli_seed1"
    api_out = tmp_path / "a0_config_only_api_seed1"
    artifacts = _expected_artifacts(CONFIG_ONLY)

    _run_documented_cli(CONFIG_ONLY, cli_out, seed=1)
    result = run_experiment(CONFIG_ONLY, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    assert artifacts == CONFIG_ONLY_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert cli_config == api_config
    assert api_config["outputs"] == expected_outputs
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_config_only_reordered_actions_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_config_only_reordered_actions_cli_seed1"
    api_out = tmp_path / "a0_config_only_reordered_actions_api_seed1"
    artifacts = _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS)

    _run_documented_cli(CONFIG_ONLY_REORDERED_ACTIONS, cli_out, seed=1)
    result = run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    assert artifacts == CONFIG_ONLY_ARTIFACTS
    assert actions == ("work_task", "create_task", "message", "idle")
    assert cli_config == api_config
    assert api_config["outputs"] == expected_outputs
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_manifest_only_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_manifest_only_cli_seed1"
    api_out = tmp_path / "a0_manifest_only_api_seed1"
    artifacts = _expected_artifacts(MANIFEST_ONLY)

    _run_documented_cli(MANIFEST_ONLY, cli_out, seed=1)
    result = run_experiment(MANIFEST_ONLY, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    cli_manifest = yaml.safe_load((cli_out / "manifest.yaml").read_text())
    api_manifest = yaml.safe_load((api_out / "manifest.yaml").read_text())
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    assert artifacts == MANIFEST_ONLY_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert cli_config == api_config
    assert cli_manifest == api_manifest
    assert api_config["outputs"] == expected_outputs
    assert api_manifest["outputs"] == expected_outputs
    assert api_manifest["artifacts"] == artifacts
    assert api_manifest["actions"] == list(actions)
    assert api_manifest["config"] == api_config
    assert api_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert api_manifest["model"]["role_action_metrics"]["actions"] == list(actions)
    assert api_manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_manifest_only_reordered_actions_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_manifest_only_reordered_actions_cli_seed1"
    api_out = tmp_path / "a0_manifest_only_reordered_actions_api_seed1"
    artifacts = _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS)

    _run_documented_cli(MANIFEST_ONLY_REORDERED_ACTIONS, cli_out, seed=1)
    result = run_experiment(MANIFEST_ONLY_REORDERED_ACTIONS, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    cli_manifest = yaml.safe_load((cli_out / "manifest.yaml").read_text())
    api_manifest = yaml.safe_load((api_out / "manifest.yaml").read_text())
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    assert artifacts == MANIFEST_ONLY_ARTIFACTS
    assert actions == ("work_task", "create_task", "message", "idle")
    assert cli_config == api_config
    assert cli_manifest == api_manifest
    assert api_config["outputs"] == expected_outputs
    assert api_manifest["outputs"] == expected_outputs
    assert api_manifest["artifacts"] == artifacts
    assert api_manifest["actions"] == list(actions)
    assert api_manifest["config"] == api_config
    assert api_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert api_manifest["model"]["role_action_metrics"]["actions"] == list(actions)
    assert api_manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


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
    first, second, first_result, second_result = _run_api_pair(
        DEFAULT_OUTPUTS,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name="default_outputs_api_seed17_first",
        second_name="default_outputs_api_seed17_second",
    )
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

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
    artifacts = _expected_artifacts(CONFIG)
    first, second, _, _ = _run_documented_cli_pair(
        CONFIG,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name="a0_seed17_first",
        second_name="a0_seed17_second",
    )

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
    artifacts = _expected_artifacts(NO_MANIFEST)
    first, second, _, _ = _run_documented_cli_pair(
        NO_MANIFEST,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name="no_manifest_repro_first",
        second_name="no_manifest_repro_second",
    )

    for out_dir in [first, second]:
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


def test_config_only_reordered_actions_writes_only_normalized_config_with_yaml_action_order(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions"

    result = run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    actions = _actions_from_normalized_config(normalized_config)

    _assert_artifacts_match_output_directory(
        out_dir,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )
    assert actions == ["work_task", "create_task", "message", "idle"]
    assert result.config.model.actions == tuple(actions)
    assert normalized_config["run"]["experiment_id"] == "a0_config_only_reordered_actions"
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_run_experiment_config_only_reordered_actions_outputs_are_byte_stable(
    tmp_path: Path,
) -> None:
    first = tmp_path / "config_only_reordered_actions_first"
    second = tmp_path / "config_only_reordered_actions_second"

    first_result = run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=first)
    second_result = run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=second)

    artifacts = _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS)
    _assert_artifacts_match_output_directory(first, artifacts)
    _assert_artifacts_match_output_directory(second, artifacts)
    _assert_artifacts_are_byte_identical(first, second, artifacts)
    _assert_config_only_writes_normalized_config(
        first,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )
    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == second_result.seed == 17
    assert len(first_result.metrics) == len(second_result.metrics) == 3
    assert len(first_result.events) == len(second_result.events) == 45


def test_run_experiment_config_only_reordered_actions_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions_api_stale_disabled"
    stale_disabled_artifacts = _write_config_only_disabled_artifact_sentinels(out_dir)

    result = run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)

    _assert_config_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )
    _assert_config_only_writes_normalized_config(
        out_dir,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )
    assert result.config.model.actions == ("work_task", "create_task", "message", "idle")
    assert result.seed == 17
    assert len(result.metrics) == 3
    assert len(result.events) == 45


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


def test_run_experiment_config_only_reordered_actions_rerun_refuses_to_overwrite_existing_config(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions_rerun"

    run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)
    before = _artifact_bytes_snapshot(
        out_dir,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )

    with pytest.raises(FileExistsError) as exc_info:
        run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert "already contains run artifacts: config.yaml" in message
    assert "manifest.yaml" not in message
    assert "metrics.csv" not in message
    assert "events.csv" not in message
    assert "summary.md" not in message
    _assert_artifacts_match_output_directory(
        out_dir,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )
    _assert_output_directory_preserved(out_dir, before)
    _assert_config_only_writes_normalized_config(
        out_dir,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )


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


def test_cli_config_only_reordered_actions_outputs_succeed_and_are_byte_stable(
    tmp_path: Path,
) -> None:
    first = tmp_path / "config_only_reordered_actions_cli_first"
    second = tmp_path / "config_only_reordered_actions_cli_second"

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG_ONLY_REORDERED_ACTIONS, out_dir, seed=17)
        _assert_artifacts_match_output_directory(
            out_dir,
            _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
        )

    _assert_artifacts_are_byte_identical(
        first,
        second,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )
    normalized_config = yaml.safe_load((first / "config.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_config_only_reordered_actions"
    assert _actions_from_normalized_config(normalized_config) == [
        "work_task",
        "create_task",
        "message",
        "idle",
    ]
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_cli_config_only_reordered_actions_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions_cli_stale_disabled"
    stale_disabled_artifacts = _write_config_only_disabled_artifact_sentinels(out_dir)

    _run_documented_cli(CONFIG_ONLY_REORDERED_ACTIONS, out_dir, seed=17)

    _assert_config_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )
    _assert_config_only_writes_normalized_config(
        out_dir,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )


def test_cli_config_only_reordered_actions_rerun_preserves_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions_cli_rerun_with_disabled_sentinels"
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
        str(CONFIG_ONLY_REORDERED_ACTIONS),
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
        [*_expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS), *disabled_sentinels],
    )
    _assert_output_directory_preserved(out_dir, before)
    _assert_config_only_writes_normalized_config(
        out_dir,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )


def test_cli_config_only_reordered_actions_rerun_refuses_to_overwrite_existing_config(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions_cli_rerun"
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(CONFIG_ONLY_REORDERED_ACTIONS),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = _artifact_bytes_snapshot(
        out_dir,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )

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
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )
    _assert_output_directory_preserved(out_dir, before)
    _assert_config_only_writes_normalized_config(
        out_dir,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )


def test_cli_manifest_only_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_reordered_actions_cli_rerun"
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(MANIFEST_ONLY_REORDERED_ACTIONS),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = _artifact_bytes_snapshot(
        out_dir,
        _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS),
    )

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert str(out_dir) in second.stderr
    assert "already contains run artifacts: config.yaml, manifest.yaml" in second.stderr
    assert "metrics.csv" not in second.stderr
    assert "events.csv" not in second.stderr
    assert "summary.md" not in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(
        out_dir,
        _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS),
    )
    _assert_output_directory_preserved(out_dir, before)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_manifest_only_reordered_actions"
    assert _actions_from_normalized_config(normalized_config) == [
        "work_task",
        "create_task",
        "message",
        "idle",
    ]
    assert normalized_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["experiment_id"] == "a0_manifest_only_reordered_actions"
    assert manifest["actions"] == _actions_from_normalized_config(normalized_config)
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS)
    assert manifest["outputs"] == normalized_config["outputs"]


def test_run_api_manifest_only_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_reordered_actions_api_rerun"

    first = run_experiment(MANIFEST_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)
    before = _artifact_bytes_snapshot(
        out_dir,
        _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS),
    )

    with pytest.raises(FileExistsError, match="already contains run artifacts") as exc_info:
        run_experiment(MANIFEST_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert first.config.run.experiment_id == "a0_manifest_only_reordered_actions"
    assert first.seed == 17
    assert str(out_dir) in message
    assert "config.yaml, manifest.yaml" in message
    assert "metrics.csv" not in message
    assert "events.csv" not in message
    assert "summary.md" not in message
    _assert_artifacts_match_output_directory(
        out_dir,
        _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS),
    )
    _assert_output_directory_preserved(out_dir, before)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    actions = _actions_from_normalized_config(normalized_config)

    assert actions == ["work_task", "create_task", "message", "idle"]
    assert normalized_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["experiment_id"] == "a0_manifest_only_reordered_actions"
    assert manifest["actions"] == actions
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS)
    assert manifest["outputs"] == normalized_config["outputs"]


def test_cli_no_manifest_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts_and_preserves_stale_manifest(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_reordered_actions_cli_rerun"
    stale_manifest = _write_no_manifest_disabled_manifest_sentinel(out_dir)
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(NO_MANIFEST_REORDERED_ACTIONS),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = _artifact_bytes_snapshot(
        out_dir,
        [*_expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS), "manifest.yaml"],
    )

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert str(out_dir) in second.stderr
    assert (
        "already contains run artifacts: config.yaml, metrics.csv, events.csv, summary.md"
        in second.stderr
    )
    assert "manifest.yaml" not in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(
        out_dir,
        [*_expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS), "manifest.yaml"],
    )
    _assert_output_directory_preserved(out_dir, before)
    _assert_no_manifest_preserves_stale_disabled_manifest(
        out_dir,
        stale_manifest=stale_manifest,
    )

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    actions = _actions_from_normalized_config(normalized_config)

    assert normalized_config["run"]["experiment_id"] == "a0_no_manifest_reordered_actions"
    assert actions == ["work_task", "create_task", "message", "idle"]
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert _summary_written_artifacts(summary) == _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)
    assert "manifest.yaml" not in _summary_written_artifacts(summary)
    assert f"role_{BASELINE_ROLES[0]}_work_task_tick" in (out_dir / "metrics.csv").read_text()


def test_run_api_no_manifest_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts_and_preserves_stale_manifest(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_reordered_actions_api_rerun"
    stale_manifest = _write_no_manifest_disabled_manifest_sentinel(out_dir)

    first = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=out_dir)
    before = _artifact_bytes_snapshot(
        out_dir,
        [*_expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS), "manifest.yaml"],
    )

    with pytest.raises(FileExistsError) as exc_info:
        run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert first.config.run.experiment_id == "a0_no_manifest_reordered_actions"
    assert first.seed == 17
    assert str(out_dir) in message
    assert "already contains run artifacts: config.yaml, metrics.csv, events.csv, summary.md" in message
    assert "manifest.yaml" not in message
    _assert_artifacts_match_output_directory(
        out_dir,
        [*_expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS), "manifest.yaml"],
    )
    _assert_output_directory_preserved(out_dir, before)
    _assert_no_manifest_preserves_stale_disabled_manifest(
        out_dir,
        stale_manifest=stale_manifest,
    )

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    actions = _actions_from_normalized_config(normalized_config)

    assert actions == ["work_task", "create_task", "message", "idle"]
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert _summary_written_artifacts(summary) == _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)
    assert "manifest.yaml" not in _summary_written_artifacts(summary)
    assert f"role_{BASELINE_ROLES[0]}_work_task_tick" in (out_dir / "metrics.csv").read_text()


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
    first, second, _, _ = _run_api_pair(
        CONFIG,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name="first",
        second_name="second",
    )

    _assert_artifacts_are_byte_identical(
        first,
        second,
        _expected_artifacts(CONFIG),
    )


def test_different_seed_changes_events(tmp_path: Path) -> None:
    first, second, _, _ = _run_api_pair(
        CONFIG,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name="seed1",
        second_name="seed2",
    )

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


def _assert_manifest_only_preserves_full_schema_provenance(
    out_dir: Path,
    config_path: Path,
) -> None:
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    actions = tuple(normalized_config["model"]["actions"])

    assert manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["artifacts"] == _expected_artifacts(config_path)
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


def _assert_config_only_writes_normalized_config(
    out_dir: Path,
    *,
    experiment_id: str = "a0_config_only",
    actions: list[str] | None = None,
) -> None:
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    expected_actions = actions or ["idle", "message", "create_task", "work_task"]

    assert normalized_config == {
        "run": {
            "experiment_id": experiment_id,
            "ticks": 3,
        },
        "model": {
            "agent_count": 15,
            "task_creation_pressure": 1.0,
            "work_service_capacity": 1.0,
            "actions": expected_actions,
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


def _baseline_roles_for_agent_count(agent_count: int) -> dict[str, str]:
    assert agent_count == 15
    return {
        f"agent_{index:02d}": BASELINE_ROLES[(index - 1) % len(BASELINE_ROLES)]
        for index in range(1, agent_count + 1)
    }


def _assert_full_output_event_replay_matches_metrics_and_summary(
    out_dir: Path,
    *,
    expected_experiment_id: str,
    expected_ticks: int,
    expected_artifacts: list[str],
) -> None:
    replay = _event_replay_context(out_dir, require_manifest=True)
    normalized_config = replay["config"]
    manifest = replay["manifest"]
    summary = replay["summary"]
    metric_rows = replay["metric_rows"]
    event_rows = replay["event_rows"]
    actions = replay["actions"]
    ticks = replay["ticks"]
    agent_count = replay["agent_count"]
    roles = replay["roles"]
    event_lobe_rows = replay["event_lobe_rows"]
    event_bundle = _integrated_aggregate_bundle_from_events(
        event_rows,
        ticks=ticks,
        roles=roles,
        actions=actions,
    )

    assert normalized_config["run"]["experiment_id"] == expected_experiment_id
    assert ticks == expected_ticks
    assert agent_count == 15
    assert manifest["config"] == normalized_config
    assert manifest["actions"] == list(actions)
    assert manifest["artifacts"] == expected_artifacts
    assert len(metric_rows) == ticks
    assert len(event_rows) == ticks * agent_count
    assert _top_level_metric_sequence_from_events(
        event_rows,
        ticks=ticks,
    ) == _top_level_metric_sequence(metric_rows)
    assert _queue_pressure_metric_sequence_from_events(
        event_rows,
        ticks=ticks,
    ) == _queue_pressure_metric_sequence(metric_rows)
    assert _queued_task_age_metric_sequence_from_events(
        event_rows,
        ticks=ticks,
    ) == _queued_task_age_metric_sequence(metric_rows)
    assert _role_action_metric_sequence_from_events(
        event_rows,
        ticks=ticks,
        manifest_roles=roles,
        actions=actions,
    ) == _role_action_metric_sequence(metric_rows, actions)
    assert _lobe_label_sequence(event_lobe_rows) == _lobe_label_sequence(metric_rows)
    assert _lobe_transition_field_sequence(event_lobe_rows) == _lobe_transition_field_sequence(
        metric_rows
    )
    assert _lobe_run_state_sequence(event_lobe_rows) == _lobe_run_state_sequence(metric_rows)
    assert event_bundle == _integrated_aggregate_bundle_from_metrics(
        metric_rows,
        actions=actions,
    )
    assert event_bundle == _summary_integrated_aggregate_bundle(
        summary,
        actions=actions,
    )


def _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
    out_dir: Path,
    *,
    expected_artifacts: list[str],
    expected_experiment_id: str,
    expected_actions: tuple[str, ...],
) -> dict[str, object]:
    replay = _no_manifest_event_replay_context(out_dir)
    normalized_config = replay["config"]
    summary = replay["summary"]
    metric_rows = replay["metric_rows"]
    event_rows = replay["event_rows"]
    actions = replay["actions"]
    ticks = replay["ticks"]
    agent_count = replay["agent_count"]
    event_lobe_rows = replay["event_lobe_rows"]
    event_bundle = _integrated_aggregate_bundle_from_events(
        event_rows,
        ticks=ticks,
        roles=replay["roles"],
        actions=actions,
    )
    metrics_bundle = _integrated_aggregate_bundle_from_metrics(
        metric_rows,
        actions=actions,
    )
    summary_bundle = _summary_integrated_aggregate_bundle(summary, actions=actions)

    assert normalized_config["run"]["experiment_id"] == expected_experiment_id
    assert normalized_config["outputs"]["write_manifest"] is False
    assert actions == expected_actions
    assert len(metric_rows) == ticks
    assert len(event_rows) == ticks * agent_count
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)
    assert not (out_dir / "manifest.yaml").exists()
    assert _summary_written_artifacts(summary) == expected_artifacts
    assert _lobe_label_sequence(event_lobe_rows) == _lobe_label_sequence(metric_rows)
    assert _lobe_transition_field_sequence(event_lobe_rows) == _lobe_transition_field_sequence(
        metric_rows
    )
    assert _lobe_dwell_runs(event_lobe_rows) == _lobe_dwell_runs(metric_rows)
    assert event_bundle == metrics_bundle
    assert event_bundle == summary_bundle
    return event_bundle


def _no_manifest_reordered_actions_event_replay_sequences(
    out_dir: Path,
) -> dict[str, object]:
    replay = _no_manifest_event_replay_context(out_dir)
    normalized_config = replay["config"]
    metric_rows = replay["metric_rows"]
    event_rows = replay["event_rows"]
    actions = replay["actions"]
    ticks = replay["ticks"]
    roles = replay["roles"]
    event_lobe_rows = replay["event_lobe_rows"]

    assert actions == ("work_task", "create_task", "message", "idle")

    return {
        "config": normalized_config,
        "metric_rows": metric_rows,
        "event_lobe_rows": event_lobe_rows,
        "actions": actions,
        "top_level": _top_level_metric_sequence_from_events(
            event_rows,
            ticks=ticks,
        ),
        "queue_pressure": _queue_pressure_metric_sequence_from_events(
            event_rows,
            ticks=ticks,
        ),
        "queue_age": _queued_task_age_metric_sequence_from_events(
            event_rows,
            ticks=ticks,
        ),
        "role_action": _role_action_metric_sequence_from_events(
            event_rows,
            ticks=ticks,
            manifest_roles=roles,
            actions=actions,
        ),
        "lobe_labels": _lobe_label_sequence(event_lobe_rows),
        "lobe_transitions": _lobe_transition_field_sequence(event_lobe_rows),
        "lobe_run_state": _lobe_run_state_sequence(event_lobe_rows),
    }


def _no_manifest_event_replay_context(out_dir: Path) -> dict[str, object]:
    replay = _event_replay_context(out_dir, require_manifest=False)
    normalized_config = replay["config"]

    assert normalized_config["outputs"]["write_manifest"] is False
    assert not (out_dir / "manifest.yaml").exists()

    return replay


def _event_replay_context(
    out_dir: Path,
    *,
    require_manifest: bool,
) -> dict[str, object]:
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = (
        yaml.safe_load((out_dir / "manifest.yaml").read_text())
        if require_manifest
        else None
    )
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    actions = tuple(_actions_from_normalized_config(normalized_config))
    ticks = normalized_config["run"]["ticks"]
    agent_count = normalized_config["model"]["agent_count"]
    roles = (
        manifest["model"]["roles"]
        if manifest is not None
        else _baseline_roles_for_agent_count(agent_count)
    )
    event_lobe_rows = _lobe_metric_rows_from_events(event_rows, ticks=ticks)

    assert len(metric_rows) == ticks
    assert len(event_rows) == ticks * agent_count

    return {
        "config": normalized_config,
        "manifest": manifest,
        "summary": summary,
        "metric_rows": metric_rows,
        "event_rows": event_rows,
        "event_lobe_rows": event_lobe_rows,
        "actions": actions,
        "ticks": ticks,
        "agent_count": agent_count,
        "roles": roles,
    }


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


def _run_api_pair(
    config_path: Path,
    tmp_path: Path,
    *,
    first_seed: int,
    second_seed: int,
    first_name: str,
    second_name: str,
) -> tuple[Path, Path, SimulationResult, SimulationResult]:
    first = tmp_path / first_name
    second = tmp_path / second_name
    artifacts = _expected_artifacts(config_path)

    first_result = run_experiment(config_path, seed=first_seed, out_dir=first)
    second_result = run_experiment(config_path, seed=second_seed, out_dir=second)

    _assert_artifacts_match_output_directory(first, artifacts)
    _assert_artifacts_match_output_directory(second, artifacts)
    return first, second, first_result, second_result


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
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    actions = tuple(normalized_config["model"]["actions"])

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


def _assert_events_replay_to_summary_role_action_totals_through_manifest_roles(
    summary: str,
    *,
    event_rows: list[dict[str, str]],
    manifest_roles: dict[str, str],
    actions: tuple[str, ...],
) -> None:
    assert _summary_role_action_totals(summary) == _role_action_totals_from_events(
        event_rows,
        manifest_roles=manifest_roles,
        actions=actions,
    )


def _role_action_totals_from_events(
    event_rows: list[dict[str, str]],
    *,
    manifest_roles: dict[str, str],
    actions: tuple[str, ...],
) -> dict[str, dict[str, int]]:
    assert event_rows
    assert set(actions) == {"idle", "message", "create_task", "work_task"}
    assert set(manifest_roles.values()) == set(BASELINE_ROLES)
    for event in event_rows:
        assert event["agent_id"] in manifest_roles
        assert event["action"] in actions

    role_action_counts = Counter(
        (manifest_roles[event["agent_id"]], event["action"])
        for event in event_rows
    )
    return {
        role: {
            action: role_action_counts[(role, action)]
            for action in actions
        }
        for role in BASELINE_ROLES
    }


def _role_action_metric_sequence_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
    manifest_roles: dict[str, str],
    actions: tuple[str, ...],
) -> list[tuple[int, ...]]:
    assert event_rows
    assert set(actions) == {"idle", "message", "create_task", "work_task"}
    assert set(manifest_roles.values()) == set(BASELINE_ROLES)
    for event in event_rows:
        assert event["agent_id"] in manifest_roles
        assert event["action"] in actions

    fields = [
        (role, action)
        for role in BASELINE_ROLES
        for action in actions
    ]
    role_action_counts_by_tick = {
        tick: Counter(
            (manifest_roles[event["agent_id"]], event["action"])
            for event in event_rows
            if int(event["tick"]) == tick
        )
        for tick in range(ticks)
    }

    assert sorted({int(event["tick"]) for event in event_rows}) == list(range(ticks))
    return [
        tuple(role_action_counts_by_tick[tick][field] for field in fields)
        for tick in range(ticks)
    ]


def _top_level_metric_sequence_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> list[tuple[int, ...]]:
    assert event_rows

    events_by_tick: dict[int, list[dict[str, str]]] = {
        tick: [] for tick in range(ticks)
    }
    for event in event_rows:
        events_by_tick[int(event["tick"])].append(event)

    assert sorted({int(event["tick"]) for event in event_rows}) == list(range(ticks))

    sequence: list[tuple[int, ...]] = []
    created_total = 0
    completed_total = 0
    previous_queue_depth = 0
    for tick in range(ticks):
        tick_events = events_by_tick[tick]
        event_type_counts = Counter(event["event_type"] for event in tick_events)
        tasks_created_tick = event_type_counts["task_created"]
        tasks_worked_tick = event_type_counts["task_worked"]
        tasks_completed_tick = sum(
            1
            for event in tick_events
            if event["event_type"] == "task_worked" and event["completed"] == "True"
        )
        created_total += tasks_created_tick
        completed_total += tasks_completed_tick
        queue_depth = created_total - completed_total
        queue_delta = queue_depth - previous_queue_depth

        sequence.append(
            (
                queue_depth,
                queue_delta,
                created_total,
                completed_total,
                tasks_completed_tick,
                event_type_counts["message_sent"],
                tasks_created_tick,
                tasks_worked_tick,
                event_type_counts["agent_idle"],
                tasks_created_tick - tasks_completed_tick,
                tasks_created_tick - tasks_worked_tick,
                tasks_worked_tick - tasks_completed_tick,
                queue_depth,
            )
        )
        previous_queue_depth = queue_depth

    return sequence


def _queue_pressure_metric_sequence_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> list[tuple[int, ...]]:
    return [
        row[-len(QUEUE_PRESSURE_METRIC_FIELDS):]
        for row in _top_level_metric_sequence_from_events(event_rows, ticks=ticks)
    ]


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

    assert _queued_task_age_metric_sequence_from_events(
        event_rows,
        ticks=len(metric_rows),
    ) == _queued_task_age_metric_sequence(metric_rows)


def _queued_task_age_metric_sequence_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> list[tuple[int, float]]:
    assert event_rows

    events_by_tick: dict[int, list[dict[str, str]]] = {
        tick: [] for tick in range(ticks)
    }
    for event in event_rows:
        events_by_tick[int(event["tick"])].append(event)

    assert sorted({int(event["tick"]) for event in event_rows}) == list(range(ticks))

    task_queue: deque[dict[str, int | str]] = deque()
    sequence: list[tuple[int, float]] = []
    for tick in range(ticks):
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

        sequence.append((expected_max_age, expected_mean_age))

    return sequence


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


def _summary_queue_pressure_totals(summary: str) -> dict[str, int]:
    labels = {
        "created-completed balance": "created_completed_balance_tick",
        "created-worked balance": "created_worked_balance_tick",
        "work-completion gap": "work_completion_gap_tick",
    }
    totals: dict[str, int] = {}
    for line in summary.splitlines():
        for label, field in labels.items():
            prefix = f"- {label}: "
            if line.startswith(prefix):
                totals[field] = int(line.removeprefix(prefix))

    assert set(totals) == set(labels.values())
    return totals


def _task_and_queue_totals_from_metrics(
    metric_rows: list[dict[str, str]],
) -> dict[str, int]:
    assert metric_rows
    final = metric_rows[-1]
    return {
        "tasks_created_total": int(final["tasks_created_total"]),
        "tasks_completed_total": int(final["tasks_completed_total"]),
        "queue_depth": int(final["queue_depth"]),
    }


def _summary_task_and_queue_totals(summary: str) -> dict[str, int]:
    labels = {
        "tasks created": "tasks_created_total",
        "tasks completed": "tasks_completed_total",
        "final queue depth": "queue_depth",
    }
    totals: dict[str, int] = {}
    for line in summary.splitlines():
        for label, field in labels.items():
            prefix = f"- {label}: "
            if line.startswith(prefix):
                totals[field] = int(line.removeprefix(prefix))

    assert set(totals) == set(labels.values())
    return totals


def _event_type_totals_from_events(
    event_rows: list[dict[str, str]],
) -> dict[str, int]:
    assert event_rows
    return dict(sorted(Counter(row["event_type"] for row in event_rows).items()))


def _summary_event_type_totals(summary: str) -> dict[str, int]:
    totals: dict[str, int] = {}
    in_section = False
    for line in summary.splitlines():
        if line == "## Event type totals":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- "):
            continue

        event_type, count = line.removeprefix("- ").split(": ", maxsplit=1)
        totals[event_type] = int(count)

    assert totals
    return dict(sorted(totals.items()))


def _queued_task_age_aggregates_from_metrics(
    metric_rows: list[dict[str, str]],
) -> dict[str, float]:
    assert metric_rows
    final = metric_rows[-1]
    return {
        "final_queued_task_max_age": float(final["queued_task_age_max_tick"]),
        "final_queued_task_mean_age": float(final["queued_task_age_mean_tick"]),
        "peak_queued_task_max_age": float(
            max(int(row["queued_task_age_max_tick"]) for row in metric_rows)
        ),
        "mean_queued_task_mean_age": round(
            sum(float(row["queued_task_age_mean_tick"]) for row in metric_rows)
            / len(metric_rows),
            6,
        ),
    }


def _summary_queued_task_age_aggregates(summary: str) -> dict[str, float]:
    labels = {
        "final queued task max age": "final_queued_task_max_age",
        "final queued task mean age": "final_queued_task_mean_age",
        "peak queued task max age": "peak_queued_task_max_age",
        "mean queued task mean age": "mean_queued_task_mean_age",
    }
    aggregates: dict[str, float] = {}
    for line in summary.splitlines():
        for label, field in labels.items():
            prefix = f"- {label}: "
            if line.startswith(prefix):
                aggregates[field] = float(line.removeprefix(prefix))

    assert set(aggregates) == set(labels.values())
    return aggregates


def _task_and_queue_totals_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> dict[str, int]:
    assert event_rows
    final = _top_level_metric_sequence_from_events(event_rows, ticks=ticks)[-1]
    return {
        "tasks_created_total": final[2],
        "tasks_completed_total": final[3],
        "queue_depth": final[0],
    }


def _queue_pressure_totals_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> dict[str, int]:
    pressure_sequence = _queue_pressure_metric_sequence_from_events(
        event_rows,
        ticks=ticks,
    )
    return {
        field: sum(row[index] for row in pressure_sequence)
        for index, field in enumerate(QUEUE_PRESSURE_METRIC_FIELDS)
        if field != "backlog_pressure_tick"
    }


def _queued_task_age_aggregates_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> dict[str, float]:
    age_sequence = _queued_task_age_metric_sequence_from_events(event_rows, ticks=ticks)
    final_max_age, final_mean_age = age_sequence[-1]
    return {
        "final_queued_task_max_age": float(final_max_age),
        "final_queued_task_mean_age": float(final_mean_age),
        "peak_queued_task_max_age": float(max(row[0] for row in age_sequence)),
        "mean_queued_task_mean_age": round(
            sum(float(row[1]) for row in age_sequence) / len(age_sequence),
            6,
        ),
    }


def _task_queue_pressure_and_age_aggregate_tuple_from_metrics(
    metric_rows: list[dict[str, str]],
) -> dict[str, dict[str, int] | dict[str, float]]:
    return {
        "task_queue_totals": _task_and_queue_totals_from_metrics(metric_rows),
        "queue_pressure_totals": _queue_pressure_totals_from_metrics(metric_rows),
        "queued_task_age_aggregates": _queued_task_age_aggregates_from_metrics(
            metric_rows
        ),
    }


def _summary_task_queue_pressure_and_age_aggregate_tuple(
    summary: str,
) -> dict[str, dict[str, int] | dict[str, float]]:
    return {
        "task_queue_totals": _summary_task_and_queue_totals(summary),
        "queue_pressure_totals": _summary_queue_pressure_totals(summary),
        "queued_task_age_aggregates": _summary_queued_task_age_aggregates(summary),
    }


def _task_queue_pressure_and_age_aggregate_tuple_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> dict[str, dict[str, int] | dict[str, float]]:
    return {
        "task_queue_totals": _task_and_queue_totals_from_events(
            event_rows,
            ticks=ticks,
        ),
        "queue_pressure_totals": _queue_pressure_totals_from_events(
            event_rows,
            ticks=ticks,
        ),
        "queued_task_age_aggregates": _queued_task_age_aggregates_from_events(
            event_rows,
            ticks=ticks,
        ),
    }


def _integrated_aggregate_bundle_from_metrics(
    metric_rows: list[dict[str, str]],
    *,
    actions: tuple[str, ...],
) -> dict[str, object]:
    return {
        "task_queue_pressure_and_age": (
            _task_queue_pressure_and_age_aggregate_tuple_from_metrics(metric_rows)
        ),
        "lobe_aggregates": {
            "totals": dict(
                sorted(Counter(row["baseline_lobe_label"] for row in metric_rows).items())
            ),
            "transitions": _lobe_transition_totals_from_adjacent_labels(metric_rows),
            "dwell_runs": _lobe_dwell_runs(metric_rows),
        },
        "role_action_totals": _role_action_totals_from_metrics(metric_rows, actions),
    }


def _integrated_aggregate_bundle_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
    roles: dict[str, str],
    actions: tuple[str, ...],
) -> dict[str, object]:
    lobe_rows = _lobe_metric_rows_from_events(event_rows, ticks=ticks)
    return {
        "task_queue_pressure_and_age": (
            _task_queue_pressure_and_age_aggregate_tuple_from_events(
                event_rows,
                ticks=ticks,
            )
        ),
        "lobe_aggregates": {
            "totals": dict(
                sorted(Counter(row["baseline_lobe_label"] for row in lobe_rows).items())
            ),
            "transitions": _lobe_transition_totals_from_adjacent_labels(lobe_rows),
            "dwell_runs": _lobe_dwell_runs(lobe_rows),
        },
        "role_action_totals": _role_action_totals_from_events(
            event_rows,
            manifest_roles=roles,
            actions=actions,
        ),
    }


def _summary_integrated_aggregate_bundle(
    summary: str,
    *,
    actions: tuple[str, ...],
) -> dict[str, object]:
    role_action_totals = _summary_role_action_totals(summary)

    return {
        "task_queue_pressure_and_age": (
            _summary_task_queue_pressure_and_age_aggregate_tuple(summary)
        ),
        "lobe_aggregates": {
            "totals": _summary_lobe_totals(summary),
            "transitions": _summary_lobe_transition_totals(summary),
            "dwell_runs": _summary_lobe_dwell_runs(summary),
        },
        "role_action_totals": {
            role: {
                action: role_action_totals[role][action]
                for action in actions
            }
            for role in BASELINE_ROLES
        },
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


def _lobe_metric_rows_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> list[dict[str, str]]:
    assert event_rows

    events_by_tick: dict[int, list[dict[str, str]]] = {
        tick: [] for tick in range(ticks)
    }
    for event in event_rows:
        events_by_tick[int(event["tick"])].append(event)

    assert sorted({int(event["tick"]) for event in event_rows}) == list(range(ticks))

    rows: list[dict[str, str]] = []
    queue_depth_start = 0
    previous_label = ""
    run_id = 0
    current_run_length = 0
    for tick in range(ticks):
        action_counts = Counter(event["action"] for event in events_by_tick[tick])
        completed_tick = sum(
            1
            for event in events_by_tick[tick]
            if event["event_type"] == "task_worked" and event["completed"] == "True"
        )
        queue_depth_end = (
            queue_depth_start + action_counts["create_task"] - completed_tick
        )
        queue_delta = queue_depth_end - queue_depth_start

        if (
            queue_depth_end > 0
            and queue_delta > 0
            and action_counts["create_task"] >= action_counts["work_task"]
        ):
            label = "backlog_growth"
        else:
            priority = ("work_task", "create_task", "message", "idle")
            dominant_action = max(
                priority,
                key=lambda action: (action_counts[action], -priority.index(action)),
            )
            label = {
                "work_task": "execution",
                "create_task": "task_generation",
                "message": "coordination",
                "idle": "low_activity",
            }[dominant_action]

        if label == previous_label:
            current_run_length += 1
        else:
            run_id += 1
            current_run_length = 1
        if not previous_label:
            transition = "start"
        elif previous_label == label:
            transition = "stable"
        else:
            transition = f"{previous_label}->{label}"

        rows.append(
            {
                "baseline_lobe_label": label,
                "baseline_lobe_previous_label": previous_label,
                "baseline_lobe_transition": transition,
                "baseline_lobe_transition_tick": str(
                    int(bool(previous_label) and previous_label != label)
                ),
                "baseline_lobe_run_id": str(run_id),
                "baseline_lobe_current_run_length": str(current_run_length),
            }
        )
        queue_depth_start = queue_depth_end
        previous_label = label

    return rows


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


def _top_level_metric_sequence(metric_rows: list[dict[str, str]]) -> list[tuple[int, ...]]:
    fields = (
        "queue_depth",
        "queue_delta_tick",
        "tasks_created_total",
        "tasks_completed_total",
        "tasks_completed_tick",
        "messages_sent_tick",
        "tasks_created_tick",
        "tasks_worked_tick",
        "idle_tick",
        "created_completed_balance_tick",
        "created_worked_balance_tick",
        "work_completion_gap_tick",
        "backlog_pressure_tick",
    )
    return [
        tuple(int(row[field]) for field in fields)
        for row in metric_rows
    ]


def _queue_pressure_metric_sequence(
    metric_rows: list[dict[str, str]],
) -> list[tuple[int, ...]]:
    return [
        tuple(int(row[field]) for field in QUEUE_PRESSURE_METRIC_FIELDS)
        for row in metric_rows
    ]


def _queued_task_age_metric_sequence(
    metric_rows: list[dict[str, str]],
) -> list[tuple[int, float]]:
    return [
        (
            int(row["queued_task_age_max_tick"]),
            float(row["queued_task_age_mean_tick"]),
        )
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
