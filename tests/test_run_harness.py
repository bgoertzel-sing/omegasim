from __future__ import annotations

from collections import Counter, deque
from pathlib import Path
import csv
import subprocess
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


def test_metrics_and_events_headers_match_documented_a0_schema(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))

    role_action_headers = [
        f"role_{role}_{action}_tick"
        for role in BASELINE_ROLES
        for action in ("idle", "message", "create_task", "work_task")
    ]
    assert metrics_header == [
        "tick",
        "agent_count",
        "bus_nodes",
        "bus_edges",
        "bus_density",
        "bus_mean_degree",
        "bus_degree_centralization",
        "queue_depth",
        "queue_delta_tick",
        "baseline_lobe_label",
        "baseline_lobe_previous_label",
        "baseline_lobe_transition",
        "baseline_lobe_transition_tick",
        "baseline_lobe_run_id",
        "baseline_lobe_current_run_length",
        "tasks_created_total",
        "tasks_completed_total",
        "tasks_completed_tick",
        "messages_sent_tick",
        "tasks_created_tick",
        "tasks_worked_tick",
        "created_completed_balance_tick",
        "created_worked_balance_tick",
        "work_completion_gap_tick",
        "backlog_pressure_tick",
        "queued_task_age_max_tick",
        "queued_task_age_mean_tick",
        "idle_tick",
        *role_action_headers,
        "mean_agent_bias",
    ]
    assert events_header == [
        "tick",
        "event_type",
        "agent_id",
        "action",
        "target_id",
        "task_id",
        "work_units",
        "remaining_work",
        "completed",
    ]


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

    events_by_tick: dict[int, list[dict[str, str]]] = {}
    for event in event_rows:
        events_by_tick.setdefault(int(event["tick"]), []).append(event)

    task_queue: deque[dict[str, int | str]] = deque()
    expected_peak_age = 0
    expected_mean_age_sum = 0.0
    for row in metrics_rows:
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
        expected_peak_age = max(expected_peak_age, expected_max_age)
        expected_mean_age_sum += expected_mean_age

        assert int(row["queued_task_age_max_tick"]) == expected_max_age
        assert float(row["queued_task_age_mean_tick"]) == expected_mean_age

    final = metrics_rows[-1]
    expected_mean_of_means = round(expected_mean_age_sum / len(metrics_rows), 6)
    summary = (out_dir / "summary.md").read_text()
    assert f"- final queued task max age: {final['queued_task_age_max_tick']}" in summary
    assert f"- final queued task mean age: {final['queued_task_age_mean_tick']}" in summary
    assert f"- peak queued task max age: {expected_peak_age}" in summary
    assert f"- mean queued task mean age: {expected_mean_of_means}" in summary


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
    expected_artifacts = [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

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

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert sorted(path.name for path in out_dir.iterdir()) == sorted(expected_artifacts)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == expected_artifacts
    assert manifest["seed"] == 1
    assert manifest["experiment_id"] == "a0_smoke"


def test_documented_cli_smoke_writes_expected_metrics_and_events_rows(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

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

    assert completed.returncode == 0
    assert completed.stderr == ""

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

    assert completed.returncode == 0
    assert completed.stderr == ""

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    for heading in [
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
    artifacts = [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    for out_dir in [first, second]:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ohdyn.run",
                "--config",
                str(CONFIG),
                "--seed",
                "17",
                "--out",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert completed.returncode == 0
        assert completed.stderr == ""
        assert sorted(path.name for path in out_dir.iterdir()) == sorted(artifacts)

    for artifact in artifacts:
        assert (first / artifact).read_bytes() == (second / artifact).read_bytes()


def test_documented_cli_refuses_to_overwrite_complete_run_directory(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed17"
    artifacts = [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]
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
    before = {artifact: (out_dir / artifact).read_bytes() for artifact in artifacts}

    second = subprocess.run(command, capture_output=True, text=True, check=False)
    after = {artifact: (out_dir / artifact).read_bytes() for artifact in artifacts}

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert "already contains run artifacts" in second.stderr
    assert "Traceback" not in second.stderr
    assert sorted(path.name for path in out_dir.iterdir()) == sorted(artifacts)
    assert after == before


def test_documented_cli_respects_disabled_optional_outputs(tmp_path: Path) -> None:
    config_path = tmp_path / "minimal_cli_outputs.yaml"
    out_dir = tmp_path / "minimal_cli_outputs"
    expected_artifacts = [
        "config.yaml",
        "manifest.yaml",
    ]
    config_path.write_text(
        """
run:
  experiment_id: minimal_cli_outputs
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

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
            "--seed",
            "17",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert sorted(path.name for path in out_dir.iterdir()) == expected_artifacts

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == expected_artifacts
    assert manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["seed"] == 17
    assert manifest["experiment_id"] == "minimal_cli_outputs"
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_documented_cli_respects_disabled_manifest_output(tmp_path: Path) -> None:
    config_path = tmp_path / "no_manifest_cli_outputs.yaml"
    out_dir = tmp_path / "no_manifest_cli_outputs"
    expected_artifacts = [
        "config.yaml",
        "events.csv",
        "metrics.csv",
        "summary.md",
    ]
    config_path.write_text(
        """
run:
  experiment_id: no_manifest_cli_outputs
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_manifest: false
  write_metrics: true
  write_events: true
  write_summary: true
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
            "17",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert sorted(path.name for path in out_dir.iterdir()) == expected_artifacts

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert not (out_dir / "manifest.yaml").exists()
    with (out_dir / "metrics.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 3
    with (out_dir / "events.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 45
    assert "# no_manifest_cli_outputs" in (out_dir / "summary.md").read_text()


def test_documented_cli_same_seed_without_manifest_reproduces_byte_identical_artifacts(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "no_manifest_repro.yaml"
    first = tmp_path / "no_manifest_repro_first"
    second = tmp_path / "no_manifest_repro_second"
    artifacts = [
        "config.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]
    config_path.write_text(
        """
run:
  experiment_id: no_manifest_repro
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_manifest: false
  write_metrics: true
  write_events: true
  write_summary: true
"""
    )

    for out_dir in [first, second]:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ohdyn.run",
                "--config",
                str(config_path),
                "--seed",
                "17",
                "--out",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert completed.returncode == 0
        assert completed.stderr == ""
        assert sorted(path.name for path in out_dir.iterdir()) == sorted(artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    for artifact in artifacts:
        assert (first / artifact).read_bytes() == (second / artifact).read_bytes()


def test_documented_cli_without_manifest_refuses_partial_output_directory(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "no_manifest_partial_collision.yaml"
    out_dir = tmp_path / "no_manifest_partial_collision"
    config_path.write_text(
        """
run:
  experiment_id: no_manifest_partial_collision
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_manifest: false
  write_metrics: true
  write_events: true
  write_summary: true
"""
    )
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
            str(config_path),
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
    assert sorted(path.name for path in out_dir.iterdir()) == sorted(sentinels)
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "summary.md").exists()
    assert not (out_dir / "manifest.yaml").exists()


def test_documented_cli_different_seeds_change_events_but_preserve_schema(tmp_path: Path) -> None:
    first = tmp_path / "a0_seed17"
    second = tmp_path / "a0_seed18"

    for seed, out_dir in [(17, first), (18, second)]:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ohdyn.run",
                "--config",
                str(CONFIG),
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
    before = {artifact: (out_dir / artifact).read_bytes() for artifact in artifacts}

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        run_experiment(CONFIG, seed=17, out_dir=out_dir)

    after = {artifact: (out_dir / artifact).read_bytes() for artifact in artifacts}
    assert sorted(path.name for path in out_dir.iterdir()) == sorted(artifacts)
    assert after == before


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

    assert sorted(path.name for path in out_dir.iterdir()) == sorted(sentinels)
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
    assert sorted(path.name for path in out_dir.iterdir()) == ["metrics.csv"]
    assert not (out_dir / "config.yaml").exists()
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_run_experiment_ignores_disabled_output_collisions_but_blocks_enabled_artifacts(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "disabled_optional_collisions.yaml"
    success_dir = tmp_path / "disabled_optional_collisions_success"
    blocked_dir = tmp_path / "disabled_optional_collisions_blocked"
    config_path.write_text(
        """
run:
  experiment_id: disabled_optional_collisions
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
    disabled_sentinels = {
        "metrics.csv": "sentinel disabled metrics\n",
        "events.csv": "sentinel disabled events\n",
        "summary.md": "sentinel disabled summary\n",
    }
    success_dir.mkdir()
    for artifact, content in disabled_sentinels.items():
        (success_dir / artifact).write_text(content)

    run_experiment(config_path, seed=17, out_dir=success_dir)

    assert (success_dir / "config.yaml").is_file()
    assert (success_dir / "manifest.yaml").is_file()
    for artifact, content in disabled_sentinels.items():
        assert (success_dir / artifact).read_text() == content
    manifest = yaml.safe_load((success_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == ["config.yaml", "manifest.yaml"]

    blocked_dir.mkdir()
    for artifact, content in disabled_sentinels.items():
        (blocked_dir / artifact).write_text(content)
    (blocked_dir / "manifest.yaml").write_text("sentinel enabled manifest\n")

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        run_experiment(config_path, seed=17, out_dir=blocked_dir)

    assert (blocked_dir / "manifest.yaml").read_text() == "sentinel enabled manifest\n"
    assert sorted(path.name for path in blocked_dir.iterdir()) == sorted(
        [*disabled_sentinels, "manifest.yaml"]
    )
    assert not (blocked_dir / "config.yaml").exists()
    for artifact, content in disabled_sentinels.items():
        assert (blocked_dir / artifact).read_text() == content


def test_run_experiment_config_artifact_collision_blocks_when_all_optional_outputs_disabled(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config_only_collision.yaml"
    out_dir = tmp_path / "config_only_collision"
    config_path.write_text(
        """
run:
  experiment_id: config_only_collision
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_manifest: false
  write_metrics: false
  write_events: false
  write_summary: false
"""
    )
    disabled_sentinels = {
        "metrics.csv": "sentinel disabled metrics\n",
        "events.csv": "sentinel disabled events\n",
        "summary.md": "sentinel disabled summary\n",
        "manifest.yaml": "sentinel disabled manifest\n",
    }
    out_dir.mkdir()
    (out_dir / "config.yaml").write_text("sentinel mandatory config\n")
    for artifact, content in disabled_sentinels.items():
        (out_dir / artifact).write_text(content)

    with pytest.raises(FileExistsError, match="already contains run artifacts: config.yaml"):
        run_experiment(config_path, seed=17, out_dir=out_dir)

    assert (out_dir / "config.yaml").read_text() == "sentinel mandatory config\n"
    assert sorted(path.name for path in out_dir.iterdir()) == sorted(
        ["config.yaml", *disabled_sentinels]
    )
    for artifact, content in disabled_sentinels.items():
        assert (out_dir / artifact).read_text() == content


def test_run_experiment_config_only_outputs_succeed_and_are_byte_stable(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config_only.yaml"
    first = tmp_path / "config_only_first"
    second = tmp_path / "config_only_second"
    config_path.write_text(
        """
run:
  experiment_id: config_only
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_manifest: false
  write_metrics: false
  write_events: false
  write_summary: false
"""
    )

    first_result = run_experiment(config_path, seed=17, out_dir=first)
    second_result = run_experiment(config_path, seed=17, out_dir=second)

    assert sorted(path.name for path in first.iterdir()) == ["config.yaml"]
    assert sorted(path.name for path in second.iterdir()) == ["config.yaml"]
    assert (first / "config.yaml").read_bytes() == (second / "config.yaml").read_bytes()
    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == second_result.seed == 17
    assert len(first_result.metrics) == len(second_result.metrics) == 3
    assert len(first_result.events) == len(second_result.events) == 45


def test_run_experiment_config_only_rerun_refuses_to_overwrite_existing_config(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config_only_rerun.yaml"
    out_dir = tmp_path / "config_only_rerun"
    config_path.write_text(
        """
run:
  experiment_id: config_only_rerun
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_manifest: false
  write_metrics: false
  write_events: false
  write_summary: false
"""
    )

    run_experiment(config_path, seed=17, out_dir=out_dir)
    before = (out_dir / "config.yaml").read_bytes()

    with pytest.raises(FileExistsError, match="already contains run artifacts: config.yaml"):
        run_experiment(config_path, seed=17, out_dir=out_dir)

    assert sorted(path.name for path in out_dir.iterdir()) == ["config.yaml"]
    assert (out_dir / "config.yaml").read_bytes() == before


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
    config_path = tmp_path / "disabled_optional_cli_collisions.yaml"
    success_dir = tmp_path / "disabled_optional_cli_collisions_success"
    blocked_dir = tmp_path / "disabled_optional_cli_collisions_blocked"
    config_path.write_text(
        """
run:
  experiment_id: disabled_optional_cli_collisions
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
        str(config_path),
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
    assert manifest["artifacts"] == ["config.yaml", "manifest.yaml"]

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
    assert sorted(path.name for path in blocked_dir.iterdir()) == sorted(
        [*disabled_sentinels, "manifest.yaml"]
    )
    assert not (blocked_dir / "config.yaml").exists()
    for artifact, content in disabled_sentinels.items():
        assert (blocked_dir / artifact).read_text() == content


def test_cli_config_artifact_collision_blocks_when_all_optional_outputs_disabled(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config_only_cli_collision.yaml"
    out_dir = tmp_path / "config_only_cli_collision"
    config_path.write_text(
        """
run:
  experiment_id: config_only_cli_collision
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_manifest: false
  write_metrics: false
  write_events: false
  write_summary: false
"""
    )
    disabled_sentinels = {
        "metrics.csv": "sentinel disabled metrics\n",
        "events.csv": "sentinel disabled events\n",
        "summary.md": "sentinel disabled summary\n",
        "manifest.yaml": "sentinel disabled manifest\n",
    }
    out_dir.mkdir()
    (out_dir / "config.yaml").write_text("sentinel mandatory config\n")
    for artifact, content in disabled_sentinels.items():
        (out_dir / artifact).write_text(content)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
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
    assert (out_dir / "config.yaml").read_text() == "sentinel mandatory config\n"
    assert sorted(path.name for path in out_dir.iterdir()) == sorted(
        ["config.yaml", *disabled_sentinels]
    )
    for artifact, content in disabled_sentinels.items():
        assert (out_dir / artifact).read_text() == content


def test_cli_config_only_outputs_succeed_and_are_byte_stable(tmp_path: Path) -> None:
    config_path = tmp_path / "config_only_cli.yaml"
    first = tmp_path / "config_only_cli_first"
    second = tmp_path / "config_only_cli_second"
    config_path.write_text(
        """
run:
  experiment_id: config_only_cli
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_manifest: false
  write_metrics: false
  write_events: false
  write_summary: false
"""
    )

    for out_dir in [first, second]:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ohdyn.run",
                "--config",
                str(config_path),
                "--seed",
                "17",
                "--out",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert completed.returncode == 0
        assert completed.stderr == ""
        assert sorted(path.name for path in out_dir.iterdir()) == ["config.yaml"]

    assert (first / "config.yaml").read_bytes() == (second / "config.yaml").read_bytes()
    normalized_config = yaml.safe_load((first / "config.yaml").read_text())
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_cli_config_only_rerun_refuses_to_overwrite_existing_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config_only_cli_rerun.yaml"
    out_dir = tmp_path / "config_only_cli_rerun"
    config_path.write_text(
        """
run:
  experiment_id: config_only_cli_rerun
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_manifest: false
  write_metrics: false
  write_events: false
  write_summary: false
"""
    )
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(config_path),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = (out_dir / "config.yaml").read_bytes()

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
    assert sorted(path.name for path in out_dir.iterdir()) == ["config.yaml"]
    assert (out_dir / "config.yaml").read_bytes() == before


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
