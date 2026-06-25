"""Deterministic OmegaHive-like baseline simulation."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import replace, dataclass
from typing import Any

import networkx as nx
import numpy as np

from ohdyn.config import (
    ATTENTION_CLASSES,
    ExogenousArrivalsConfig,
    OmegaConfig,
)


BASELINE_ROLES = (
    "coordinator",
    "researcher",
    "architect",
    "implementer",
    "reviewer",
)

BASELINE_LOBE_LABELS = (
    "backlog_growth",
    "execution",
    "task_generation",
    "coordination",
    "low_activity",
)

BASELINE_LOBE_TRANSITION_FIELDS = (
    "baseline_lobe_previous_label",
    "baseline_lobe_transition",
    "baseline_lobe_transition_tick",
    "baseline_lobe_run_id",
    "baseline_lobe_current_run_length",
)

BASELINE_EVENT_TYPES = (
    "agent_idle",
    "message_sent",
    "task_created",
    "task_worked",
)

ATTENTION_EVENT_TYPES = (
    "attention_capture_pressure",
)

EXOGENOUS_ARRIVAL_EVENT_TYPES = (
    "exogenous_task_arrived",
)

EVENT_FIELDS = (
    "tick",
    "event_type",
    "agent_id",
    "action",
    "target_id",
    "task_id",
    "work_units",
    "remaining_work",
    "completed",
    "task_class",
    "attention_selected_class",
    "attention_pressure_class",
    "attention_capture_pressure",
)

HIVE_EVENT_FIELDS = ("hive_id", *EVENT_FIELDS)

COUPLING_EVENT_FIELDS = (
    "tick",
    "source_hive_id",
    "target_hive_id",
    "task_id",
    "coupling_mode",
    "delay_ticks",
    "transfer_decision",
    "arrival_tick",
)

CROSS_HIVE_METRIC_FIELDS = (
    "tick",
    "hive_count",
    "coupling_mode",
    "transfer_attempts_tick",
    "transfers_completed_tick",
    "inbound_transfers_tick",
    "outbound_transfers_tick",
    "queued_age_mean_divergence_tick",
    "completion_fraction_min_tick",
    "completion_fraction_max_tick",
    "completion_fraction_divergence_tick",
    "aggregate_queue_depth",
    "aggregate_queue_delta_tick",
    "aggregate_created_tick",
    "aggregate_completed_tick",
    "aggregate_exogenous_arrivals_tick",
    "aggregate_inbound_transfers_tick",
    "aggregate_outbound_transfers_tick",
    "aggregate_explicit_drops_tick",
    "aggregate_queue_balance_residual_tick",
)

QUEUE_PRESSURE_METRIC_FIELDS = (
    "created_completed_balance_tick",
    "created_worked_balance_tick",
    "work_completion_gap_tick",
    "backlog_pressure_tick",
)

QUEUED_TASK_AGE_METRIC_FIELDS = (
    "queued_task_age_max_tick",
    "queued_task_age_mean_tick",
)

MULTI_HIVE_QUEUE_FLOW_METRIC_FIELDS = (
    "inbound_transfers_tick",
    "outbound_transfers_tick",
    "explicit_drops_tick",
    "queue_balance_residual_tick",
)

EXOGENOUS_ARRIVAL_METRIC_FIELDS = (
    "agent_tasks_created_tick",
    "agent_tasks_created_total",
    "exogenous_tasks_created_tick",
    "exogenous_tasks_created_total",
)

TASK_CLASS_VALUE_WEIGHTS = {
    "near_term_external": 4,
    "long_term_research": 3,
    "internal_improvement": 2,
    "housekeeping": 1,
}


def metrics_fieldnames(
    actions: tuple[str, ...],
    *,
    include_attention_policy: bool = False,
    include_exogenous_arrivals: bool = False,
) -> tuple[str, ...]:
    return (
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
        *BASELINE_LOBE_TRANSITION_FIELDS,
        "tasks_created_total",
        "tasks_completed_total",
        "tasks_completed_tick",
        "messages_sent_tick",
        "tasks_created_tick",
        *(EXOGENOUS_ARRIVAL_METRIC_FIELDS if include_exogenous_arrivals else ()),
        "tasks_worked_tick",
        *QUEUE_PRESSURE_METRIC_FIELDS,
        *QUEUED_TASK_AGE_METRIC_FIELDS,
        *(attention_policy_metric_fields() if include_attention_policy else ()),
        "idle_tick",
        *role_action_metric_fields(actions),
        "mean_agent_bias",
    )


def role_action_metric_fields(actions: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        f"role_{role}_{action}_tick"
        for role in BASELINE_ROLES
        for action in actions
    )


def attention_policy_metric_fields() -> tuple[str, ...]:
    return (
        *(
            field
            for class_name in ATTENTION_CLASSES
            for field in (
                f"attention_{class_name}_queued_tick",
                f"attention_{class_name}_completed_total",
                f"attention_{class_name}_worked_total",
                f"attention_{class_name}_queued_age_max_tick",
                f"attention_{class_name}_queued_age_mean_tick",
                f"attention_{class_name}_spent_share_tick",
                f"attention_{class_name}_target_share",
                f"attention_{class_name}_share_deviation_tick",
                f"attention_{class_name}_capture_pressure_tick",
            )
        ),
        "attention_capture_pressure_max_tick",
        "attention_value_weighted_completed_tick",
        "attention_value_weighted_completed_total",
        "attention_value_per_completed_task_tick",
        "attention_value_per_completed_task_total",
        "attention_value_per_work_event_tick",
        "attention_value_per_work_event_total",
    )


@dataclass(frozen=True)
class AgentState:
    agent_id: str
    role: str
    bias: float


@dataclass
class Task:
    task_id: str
    created_by: str
    created_tick: int
    remaining_work: int
    task_class: str = ""


@dataclass(frozen=True)
class SimulationResult:
    config: OmegaConfig
    seed: int
    bus_graph: nx.Graph
    agents: tuple[AgentState, ...]
    metrics: list[dict[str, Any]]
    events: list[dict[str, Any]]
    hive_results: tuple["SimulationResult", ...] = ()
    hive_metrics: list[dict[str, Any]] | None = None
    hive_events: list[dict[str, Any]] | None = None
    coupling_events: list[dict[str, Any]] | None = None
    cross_hive_metrics: list[dict[str, Any]] | None = None


@dataclass
class _HiveRuntime:
    hive_id: str
    transfer_probability: float
    config: OmegaConfig
    rng: np.random.Generator
    exogenous_rng: np.random.Generator | None
    bus_graph: nx.Graph
    agents: tuple[AgentState, ...]
    bus_metrics: dict[str, float]
    task_queue: deque[Task]
    events: list[dict[str, Any]]
    metrics: list[dict[str, Any]]
    task_counter: int = 0
    agent_tasks_created: int = 0
    exogenous_tasks_created: int = 0
    completed_tasks: int = 0
    attention_work_counts: Counter[str] | None = None
    attention_completed_counts: Counter[str] | None = None
    attention_value_weighted_completed_total: int = 0
    previous_lobe_label: str = ""
    baseline_lobe_run_id: int = 0
    baseline_lobe_current_run_length: int = 0
    queue_depth_start_tick: int = 0
    action_counts_tick: Counter[str] | None = None
    role_action_counts_tick: Counter[tuple[str, str]] | None = None
    attention_work_counts_tick: Counter[str] | None = None
    attention_completed_counts_tick: Counter[str] | None = None
    completed_this_tick: int = 0
    attention_value_weighted_completed_tick: int = 0
    exogenous_created_this_tick: int = 0
    inbound_transfers_tick: int = 0
    outbound_transfers_tick: int = 0
    transfer_attempts_tick: int = 0
    transfers_completed_tick: int = 0


def simulate(config: OmegaConfig, seed: int) -> SimulationResult:
    if config.hives:
        return _simulate_multi_hive(config, seed)
    return _simulate_single(config, seed)


def _simulate_single(config: OmegaConfig, seed: int) -> SimulationResult:
    rng = np.random.default_rng(seed)
    exogenous_rng = _exogenous_arrival_rng(config, seed)
    agents = _make_agents(config.model.agent_count, rng)
    bus_graph = _make_bus_graph(agents)
    bus_metrics = _bus_graph_metrics(bus_graph)
    task_queue: deque[Task] = deque()
    events: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    task_counter = 0
    agent_tasks_created = 0
    exogenous_tasks_created = 0
    completed_tasks = 0
    attention_work_counts: Counter[str] = Counter()
    attention_completed_counts: Counter[str] = Counter()
    attention_value_weighted_completed_total = 0
    previous_lobe_label = ""
    baseline_lobe_run_id = 0
    baseline_lobe_current_run_length = 0

    for tick in range(config.run.ticks):
        queue_depth_start = len(task_queue)
        action_counts: Counter[str] = Counter()
        role_action_counts: Counter[tuple[str, str]] = Counter()
        attention_work_counts_tick: Counter[str] = Counter()
        attention_completed_counts_tick: Counter[str] = Counter()
        completed_this_tick = 0
        attention_value_weighted_completed_tick = 0
        exogenous_created_this_tick = 0
        if _exogenous_arrivals_enabled(config):
            assert exogenous_rng is not None
            exogenous_created_this_tick = int(
                exogenous_rng.poisson(config.exogenous_arrivals.rate_per_tick)
            )
            for _ in range(exogenous_created_this_tick):
                task_counter += 1
                exogenous_tasks_created += 1
                work_units = int(exogenous_rng.integers(1, 4))
                task = Task(
                    task_id=f"task_{task_counter:05d}",
                    created_by="exogenous",
                    created_tick=tick,
                    remaining_work=work_units,
                    task_class=_choose_exogenous_task_class(config, exogenous_rng),
                )
                task_queue.append(task)
                events.append(
                    _event(
                        tick=tick,
                        event_type="exogenous_task_arrived",
                        agent_id="",
                        action="exogenous_arrival",
                        task_id=task.task_id,
                        work_units=work_units,
                        task_class=task.task_class,
                    )
                )
        for agent in agents:
            action = _choose_action(
                config.model.actions,
                bool(task_queue),
                agent,
                rng,
                task_creation_pressure=config.model.task_creation_pressure,
                work_service_capacity=config.model.work_service_capacity,
            )
            action_counts[action] += 1
            role_action_counts[(agent.role, action)] += 1

            if action == "message":
                target = _choose_target(agent, agents, rng)
                events.append(
                    _event(
                        tick=tick,
                        event_type="message_sent",
                        agent_id=agent.agent_id,
                        action=action,
                        target_id=target.agent_id,
                    )
                )
            elif action == "create_task":
                task_counter += 1
                agent_tasks_created += 1
                work_units = int(rng.integers(1, 4))
                task = Task(
                    task_id=f"task_{task_counter:05d}",
                    created_by=agent.agent_id,
                    created_tick=tick,
                    remaining_work=work_units,
                    task_class=_choose_task_class(config, rng),
                )
                task_queue.append(task)
                events.append(
                    _event(
                        tick=tick,
                        event_type="task_created",
                        agent_id=agent.agent_id,
                        action=action,
                        task_id=task.task_id,
                        work_units=work_units,
                    )
                )
            elif action == "work_task":
                selected_task_index: int | None = None
                desired_attention_class = (
                    _desired_attention_class(task_queue, config, attention_work_counts)
                    if config.attention_policy is not None
                    else ""
                )
                if config.attention_policy is not None:
                    if config.attention_policy.selection_strategy == "random_available":
                        selected_task_index = int(rng.integers(0, len(task_queue)))
                        desired_attention_class = task_queue[selected_task_index].task_class
                    capture_pressure_event = _attention_capture_pressure_event(
                        tick=tick,
                        agent=agent,
                        action=action,
                        task_queue=task_queue,
                        config=config,
                        selected_class=desired_attention_class,
                    )
                    if capture_pressure_event is not None:
                        events.append(capture_pressure_event)
                task = _pop_work_task(
                    task_queue,
                    config,
                    attention_work_counts,
                    desired_class=desired_attention_class,
                    selected_index=selected_task_index,
                )
                task.remaining_work -= 1
                if config.attention_policy is not None:
                    attention_work_counts[task.task_class] += 1
                    attention_work_counts_tick[task.task_class] += 1
                completed = task.remaining_work <= 0
                if completed:
                    completed_tasks += 1
                    completed_this_tick += 1
                    if config.attention_policy is not None:
                        attention_completed_counts[task.task_class] += 1
                        attention_completed_counts_tick[task.task_class] += 1
                        attention_value_weighted_completed_tick += TASK_CLASS_VALUE_WEIGHTS[
                            task.task_class
                        ]
                        attention_value_weighted_completed_total += TASK_CLASS_VALUE_WEIGHTS[
                            task.task_class
                        ]
                else:
                    task_queue.append(task)
                events.append(
                    _event(
                        tick=tick,
                        event_type="task_worked",
                        agent_id=agent.agent_id,
                        action=action,
                        task_id=task.task_id,
                        remaining_work=max(task.remaining_work, 0),
                        completed=completed,
                        task_class=task.task_class,
                    )
                )
            else:
                events.append(
                    _event(
                        tick=tick,
                        event_type="agent_idle",
                        agent_id=agent.agent_id,
                        action="idle",
                    )
                )

        queue_depth_end = len(task_queue)
        queue_delta = queue_depth_end - queue_depth_start
        queue_age_metrics = _queue_age_metrics(task_queue, tick)
        attention_metrics = _attention_policy_metrics(
            config=config,
            task_queue=task_queue,
            tick=tick,
            work_counts_tick=attention_work_counts_tick,
            work_counts=attention_work_counts,
            completed_counts=attention_completed_counts,
            value_weighted_completed_tick=attention_value_weighted_completed_tick,
            value_weighted_completed_total=attention_value_weighted_completed_total,
            completed_this_tick=completed_this_tick,
            completed_total=completed_tasks,
        )
        baseline_lobe_label = _baseline_lobe_label(
            action_counts=action_counts,
            queue_depth_start=queue_depth_start,
            queue_depth_end=queue_depth_end,
        )
        baseline_lobe_transition = _baseline_lobe_transition(
            previous_lobe_label,
            baseline_lobe_label,
        )
        if previous_lobe_label == baseline_lobe_label:
            baseline_lobe_current_run_length += 1
        else:
            baseline_lobe_run_id += 1
            baseline_lobe_current_run_length = 1
        metrics.append(
            {
                "tick": tick,
                "agent_count": len(agents),
                "bus_nodes": bus_graph.number_of_nodes(),
                "bus_edges": bus_graph.number_of_edges(),
                **bus_metrics,
                "queue_depth": queue_depth_end,
                "queue_delta_tick": queue_delta,
                "baseline_lobe_label": baseline_lobe_label,
                "baseline_lobe_previous_label": previous_lobe_label,
                "baseline_lobe_transition": baseline_lobe_transition,
                "baseline_lobe_transition_tick": int(
                    bool(previous_lobe_label) and previous_lobe_label != baseline_lobe_label
                ),
                "baseline_lobe_run_id": baseline_lobe_run_id,
                "baseline_lobe_current_run_length": baseline_lobe_current_run_length,
                "tasks_created_total": task_counter,
                "tasks_completed_total": completed_tasks,
                "tasks_completed_tick": completed_this_tick,
                "messages_sent_tick": action_counts["message"],
                "tasks_created_tick": action_counts["create_task"] + exogenous_created_this_tick,
                **_exogenous_arrival_metrics(
                    config=config,
                    agent_created_tick=action_counts["create_task"],
                    agent_created_total=agent_tasks_created,
                    exogenous_created_tick=exogenous_created_this_tick,
                    exogenous_created_total=exogenous_tasks_created,
                ),
                "tasks_worked_tick": action_counts["work_task"],
                "created_completed_balance_tick": (
                    action_counts["create_task"] + exogenous_created_this_tick - completed_this_tick
                ),
                "created_worked_balance_tick": (
                    action_counts["create_task"] + exogenous_created_this_tick - action_counts["work_task"]
                ),
                "work_completion_gap_tick": action_counts["work_task"] - completed_this_tick,
                "backlog_pressure_tick": queue_depth_end,
                **queue_age_metrics,
                **attention_metrics,
                "idle_tick": action_counts["idle"],
                **_role_action_metrics(config.model.actions, role_action_counts),
                "mean_agent_bias": round(float(np.mean([agent.bias for agent in agents])), 6),
            }
        )
        previous_lobe_label = baseline_lobe_label

    return SimulationResult(
        config=config,
        seed=seed,
        bus_graph=bus_graph,
        agents=agents,
        metrics=metrics,
        events=events,
    )


def _simulate_multi_hive(config: OmegaConfig, seed: int) -> SimulationResult:
    assert config.coupling is not None
    if config.coupling.mode == "none":
        return _simulate_multi_hive_none(config, seed)
    if config.coupling.mode == "direct":
        return _simulate_multi_hive_direct(config, seed)
    raise ValueError(
        "A4 multi-hive simulation currently supports coupling.mode 'none' and 'direct'."
    )


def _simulate_multi_hive_none(config: OmegaConfig, seed: int) -> SimulationResult:
    assert config.coupling is not None
    hive_results = []
    for hive in config.hives:
        hive_config = _hive_local_config(config, hive_index_seed_offset=hive.seed_offset)
        hive_results.append(_simulate_single(hive_config, seed + hive.seed_offset))

    hive_metrics = _hive_metrics(config, tuple(hive_results))
    hive_events = _hive_events(config, tuple(hive_results))
    coupling_events: list[dict[str, Any]] = []
    cross_hive_metrics = _cross_hive_metrics(config, tuple(hive_results))
    aggregate_metrics = _aggregate_hive_metrics(config, tuple(hive_results), cross_hive_metrics)
    aggregate_events = _aggregate_hive_events(hive_events)
    aggregate_graph = nx.disjoint_union_all([result.bus_graph for result in hive_results])
    aggregate_agents = tuple(agent for result in hive_results for agent in result.agents)

    return SimulationResult(
        config=config,
        seed=seed,
        bus_graph=aggregate_graph,
        agents=aggregate_agents,
        metrics=aggregate_metrics,
        events=aggregate_events,
        hive_results=tuple(hive_results),
        hive_metrics=hive_metrics,
        hive_events=hive_events,
        coupling_events=coupling_events,
        cross_hive_metrics=cross_hive_metrics,
    )


def _simulate_multi_hive_direct(config: OmegaConfig, seed: int) -> SimulationResult:
    assert config.coupling is not None
    coupling_rng = np.random.default_rng(seed + config.coupling.shuffle_seed_offset)
    runtimes = tuple(_make_hive_runtime(config, hive, seed) for hive in config.hives)
    coupling_events: list[dict[str, Any]] = []

    for tick in range(config.run.ticks):
        for runtime in runtimes:
            _begin_hive_tick(runtime)

        for source_index, runtime in enumerate(runtimes):
            _advance_hive_runtime_tick(
                runtime=runtime,
                runtimes=runtimes,
                source_index=source_index,
                tick=tick,
                coupling_rng=coupling_rng,
                coupling_events=coupling_events,
            )

        for runtime in runtimes:
            _finish_hive_tick(runtime, tick)

    hive_results = tuple(_runtime_result(runtime) for runtime in runtimes)
    hive_metrics = _hive_metrics(config, hive_results)
    hive_events = _hive_events(config, hive_results)
    cross_hive_metrics = _cross_hive_metrics(
        config,
        hive_results,
        coupling_events=coupling_events,
    )
    aggregate_metrics = _aggregate_hive_metrics(config, hive_results, cross_hive_metrics)
    aggregate_events = _aggregate_hive_events(hive_events)
    aggregate_graph = nx.disjoint_union_all([result.bus_graph for result in hive_results])
    aggregate_agents = tuple(agent for result in hive_results for agent in result.agents)

    return SimulationResult(
        config=config,
        seed=seed,
        bus_graph=aggregate_graph,
        agents=aggregate_agents,
        metrics=aggregate_metrics,
        events=aggregate_events,
        hive_results=hive_results,
        hive_metrics=hive_metrics,
        hive_events=hive_events,
        coupling_events=coupling_events,
        cross_hive_metrics=cross_hive_metrics,
    )


def _make_hive_runtime(config: OmegaConfig, hive: Any, seed: int) -> _HiveRuntime:
    assert config.coupling is not None
    hive_config = _hive_local_config(config, hive_index_seed_offset=hive.seed_offset)
    rng = np.random.default_rng(seed + hive.seed_offset)
    exogenous_rng = _exogenous_arrival_rng(hive_config, seed + hive.seed_offset)
    agents = _make_agents(hive_config.model.agent_count, rng)
    bus_graph = _make_bus_graph(agents)
    return _HiveRuntime(
        hive_id=hive.hive_id,
        transfer_probability=config.coupling.transfer_probability,
        config=hive_config,
        rng=rng,
        exogenous_rng=exogenous_rng,
        bus_graph=bus_graph,
        agents=agents,
        bus_metrics=_bus_graph_metrics(bus_graph),
        task_queue=deque(),
        events=[],
        metrics=[],
        attention_work_counts=Counter(),
        attention_completed_counts=Counter(),
    )


def _begin_hive_tick(runtime: _HiveRuntime) -> None:
    runtime.queue_depth_start_tick = len(runtime.task_queue)
    runtime.action_counts_tick = Counter()
    runtime.role_action_counts_tick = Counter()
    runtime.attention_work_counts_tick = Counter()
    runtime.attention_completed_counts_tick = Counter()
    runtime.completed_this_tick = 0
    runtime.attention_value_weighted_completed_tick = 0
    runtime.exogenous_created_this_tick = 0
    runtime.inbound_transfers_tick = 0
    runtime.outbound_transfers_tick = 0
    runtime.transfer_attempts_tick = 0
    runtime.transfers_completed_tick = 0


def _advance_hive_runtime_tick(
    *,
    runtime: _HiveRuntime,
    runtimes: tuple[_HiveRuntime, ...],
    source_index: int,
    tick: int,
    coupling_rng: np.random.Generator,
    coupling_events: list[dict[str, Any]],
) -> None:
    config = runtime.config
    if _exogenous_arrivals_enabled(config):
        assert runtime.exogenous_rng is not None
        runtime.exogenous_created_this_tick = int(
            runtime.exogenous_rng.poisson(config.exogenous_arrivals.rate_per_tick)
        )
        for _ in range(runtime.exogenous_created_this_tick):
            runtime.task_counter += 1
            runtime.exogenous_tasks_created += 1
            work_units = int(runtime.exogenous_rng.integers(1, 4))
            task = Task(
                task_id=f"task_{runtime.task_counter:05d}",
                created_by="exogenous",
                created_tick=tick,
                remaining_work=work_units,
                task_class=_choose_exogenous_task_class(config, runtime.exogenous_rng),
            )
            runtime.events.append(
                _event(
                    tick=tick,
                    event_type="exogenous_task_arrived",
                    agent_id="",
                    action="exogenous_arrival",
                    task_id=task.task_id,
                    work_units=work_units,
                    task_class=task.task_class,
                )
            )
            _route_emitted_task(
                task=task,
                runtime=runtime,
                runtimes=runtimes,
                source_index=source_index,
                tick=tick,
                coupling_rng=coupling_rng,
                coupling_events=coupling_events,
            )

    assert runtime.action_counts_tick is not None
    assert runtime.role_action_counts_tick is not None
    for agent in runtime.agents:
        action = _choose_action(
            config.model.actions,
            bool(runtime.task_queue),
            agent,
            runtime.rng,
            task_creation_pressure=config.model.task_creation_pressure,
            work_service_capacity=config.model.work_service_capacity,
        )
        runtime.action_counts_tick[action] += 1
        runtime.role_action_counts_tick[(agent.role, action)] += 1

        if action == "message":
            target = _choose_target(agent, runtime.agents, runtime.rng)
            runtime.events.append(
                _event(
                    tick=tick,
                    event_type="message_sent",
                    agent_id=agent.agent_id,
                    action=action,
                    target_id=target.agent_id,
                )
            )
        elif action == "create_task":
            runtime.task_counter += 1
            runtime.agent_tasks_created += 1
            work_units = int(runtime.rng.integers(1, 4))
            task = Task(
                task_id=f"task_{runtime.task_counter:05d}",
                created_by=agent.agent_id,
                created_tick=tick,
                remaining_work=work_units,
                task_class=_choose_task_class(config, runtime.rng),
            )
            runtime.events.append(
                _event(
                    tick=tick,
                    event_type="task_created",
                    agent_id=agent.agent_id,
                    action=action,
                    task_id=task.task_id,
                    work_units=work_units,
                )
            )
            _route_emitted_task(
                task=task,
                runtime=runtime,
                runtimes=runtimes,
                source_index=source_index,
                tick=tick,
                coupling_rng=coupling_rng,
                coupling_events=coupling_events,
            )
        elif action == "work_task":
            selected_task_index: int | None = None
            assert runtime.attention_work_counts is not None
            assert runtime.attention_work_counts_tick is not None
            assert runtime.attention_completed_counts is not None
            assert runtime.attention_completed_counts_tick is not None
            desired_attention_class = (
                _desired_attention_class(
                    runtime.task_queue,
                    config,
                    runtime.attention_work_counts,
                )
                if config.attention_policy is not None
                else ""
            )
            if config.attention_policy is not None:
                if config.attention_policy.selection_strategy == "random_available":
                    selected_task_index = int(runtime.rng.integers(0, len(runtime.task_queue)))
                    desired_attention_class = runtime.task_queue[
                        selected_task_index
                    ].task_class
                capture_pressure_event = _attention_capture_pressure_event(
                    tick=tick,
                    agent=agent,
                    action=action,
                    task_queue=runtime.task_queue,
                    config=config,
                    selected_class=desired_attention_class,
                )
                if capture_pressure_event is not None:
                    runtime.events.append(capture_pressure_event)
            task = _pop_work_task(
                runtime.task_queue,
                config,
                runtime.attention_work_counts,
                desired_class=desired_attention_class,
                selected_index=selected_task_index,
            )
            task.remaining_work -= 1
            if config.attention_policy is not None:
                runtime.attention_work_counts[task.task_class] += 1
                runtime.attention_work_counts_tick[task.task_class] += 1
            completed = task.remaining_work <= 0
            if completed:
                runtime.completed_tasks += 1
                runtime.completed_this_tick += 1
                if config.attention_policy is not None:
                    runtime.attention_completed_counts[task.task_class] += 1
                    runtime.attention_completed_counts_tick[task.task_class] += 1
                    runtime.attention_value_weighted_completed_tick += (
                        TASK_CLASS_VALUE_WEIGHTS[task.task_class]
                    )
                    runtime.attention_value_weighted_completed_total += (
                        TASK_CLASS_VALUE_WEIGHTS[task.task_class]
                    )
            else:
                runtime.task_queue.append(task)
            runtime.events.append(
                _event(
                    tick=tick,
                    event_type="task_worked",
                    agent_id=agent.agent_id,
                    action=action,
                    task_id=task.task_id,
                    remaining_work=max(task.remaining_work, 0),
                    completed=completed,
                    task_class=task.task_class,
                )
            )
        else:
            runtime.events.append(
                _event(
                    tick=tick,
                    event_type="agent_idle",
                    agent_id=agent.agent_id,
                    action="idle",
                )
            )


def _route_emitted_task(
    *,
    task: Task,
    runtime: _HiveRuntime,
    runtimes: tuple[_HiveRuntime, ...],
    source_index: int,
    tick: int,
    coupling_rng: np.random.Generator,
    coupling_events: list[dict[str, Any]],
) -> None:
    # The local runtime config intentionally strips coupling; the mode is direct
    # whenever this helper is used. The source tuple order defines the target.
    if len(runtimes) <= 1:
        runtime.task_queue.append(task)
        return

    target_index = (source_index + 1) % len(runtimes)
    target = runtimes[target_index]
    runtime.transfer_attempts_tick += 1
    transfer_decision = bool(coupling_rng.random() < runtime.transfer_probability)
    global_task_id = _qualified_task_id(runtime.hive_id, task.task_id)
    coupling_events.append(
        {
            "tick": tick,
            "source_hive_id": runtime.hive_id,
            "target_hive_id": target.hive_id,
            "task_id": global_task_id,
            "coupling_mode": "direct",
            "delay_ticks": 0,
            "transfer_decision": transfer_decision,
            "arrival_tick": tick if transfer_decision else "",
        }
    )
    if not transfer_decision:
        runtime.task_queue.append(task)
        return

    runtime.outbound_transfers_tick += 1
    runtime.transfers_completed_tick += 1
    target.inbound_transfers_tick += 1
    target.task_queue.append(replace(task, task_id=global_task_id))


def _finish_hive_tick(runtime: _HiveRuntime, tick: int) -> None:
    config = runtime.config
    assert runtime.action_counts_tick is not None
    assert runtime.role_action_counts_tick is not None
    assert runtime.attention_work_counts_tick is not None
    assert runtime.attention_completed_counts_tick is not None
    assert runtime.attention_work_counts is not None
    assert runtime.attention_completed_counts is not None
    queue_depth_end = len(runtime.task_queue)
    queue_delta = queue_depth_end - runtime.queue_depth_start_tick
    queue_age_metrics = _queue_age_metrics(runtime.task_queue, tick)
    attention_metrics = _attention_policy_metrics(
        config=config,
        task_queue=runtime.task_queue,
        tick=tick,
        work_counts_tick=runtime.attention_work_counts_tick,
        work_counts=runtime.attention_work_counts,
        completed_counts=runtime.attention_completed_counts,
        value_weighted_completed_tick=runtime.attention_value_weighted_completed_tick,
        value_weighted_completed_total=runtime.attention_value_weighted_completed_total,
        completed_this_tick=runtime.completed_this_tick,
        completed_total=runtime.completed_tasks,
    )
    baseline_lobe_label = _baseline_lobe_label(
        action_counts=runtime.action_counts_tick,
        queue_depth_start=runtime.queue_depth_start_tick,
        queue_depth_end=queue_depth_end,
    )
    baseline_lobe_transition = _baseline_lobe_transition(
        runtime.previous_lobe_label,
        baseline_lobe_label,
    )
    if runtime.previous_lobe_label == baseline_lobe_label:
        runtime.baseline_lobe_current_run_length += 1
    else:
        runtime.baseline_lobe_run_id += 1
        runtime.baseline_lobe_current_run_length = 1

    created_tick = (
        runtime.action_counts_tick["create_task"] + runtime.exogenous_created_this_tick
    )
    balance = (
        created_tick
        + runtime.inbound_transfers_tick
        - runtime.completed_this_tick
        - runtime.outbound_transfers_tick
    )
    runtime.metrics.append(
        {
            "tick": tick,
            "agent_count": len(runtime.agents),
            "bus_nodes": runtime.bus_graph.number_of_nodes(),
            "bus_edges": runtime.bus_graph.number_of_edges(),
            **runtime.bus_metrics,
            "queue_depth": queue_depth_end,
            "queue_delta_tick": queue_delta,
            "baseline_lobe_label": baseline_lobe_label,
            "baseline_lobe_previous_label": runtime.previous_lobe_label,
            "baseline_lobe_transition": baseline_lobe_transition,
            "baseline_lobe_transition_tick": int(
                bool(runtime.previous_lobe_label)
                and runtime.previous_lobe_label != baseline_lobe_label
            ),
            "baseline_lobe_run_id": runtime.baseline_lobe_run_id,
            "baseline_lobe_current_run_length": runtime.baseline_lobe_current_run_length,
            "tasks_created_total": runtime.task_counter,
            "tasks_completed_total": runtime.completed_tasks,
            "tasks_completed_tick": runtime.completed_this_tick,
            "messages_sent_tick": runtime.action_counts_tick["message"],
            "tasks_created_tick": created_tick,
            **_exogenous_arrival_metrics(
                config=config,
                agent_created_tick=runtime.action_counts_tick["create_task"],
                agent_created_total=runtime.agent_tasks_created,
                exogenous_created_tick=runtime.exogenous_created_this_tick,
                exogenous_created_total=runtime.exogenous_tasks_created,
            ),
            "tasks_worked_tick": runtime.action_counts_tick["work_task"],
            "created_completed_balance_tick": created_tick - runtime.completed_this_tick,
            "created_worked_balance_tick": (
                created_tick - runtime.action_counts_tick["work_task"]
            ),
            "work_completion_gap_tick": (
                runtime.action_counts_tick["work_task"] - runtime.completed_this_tick
            ),
            "backlog_pressure_tick": queue_depth_end,
            **queue_age_metrics,
            **attention_metrics,
            "idle_tick": runtime.action_counts_tick["idle"],
            **_role_action_metrics(config.model.actions, runtime.role_action_counts_tick),
            "mean_agent_bias": round(
                float(np.mean([agent.bias for agent in runtime.agents])),
                6,
            ),
            "inbound_transfers_tick": runtime.inbound_transfers_tick,
            "outbound_transfers_tick": runtime.outbound_transfers_tick,
            "explicit_drops_tick": 0,
            "queue_balance_residual_tick": queue_delta - balance,
        }
    )
    runtime.previous_lobe_label = baseline_lobe_label


def _runtime_result(runtime: _HiveRuntime) -> SimulationResult:
    return SimulationResult(
        config=runtime.config,
        seed=0,
        bus_graph=runtime.bus_graph,
        agents=runtime.agents,
        metrics=runtime.metrics,
        events=runtime.events,
    )


def _hive_local_config(config: OmegaConfig, *, hive_index_seed_offset: int) -> OmegaConfig:
    hive = next(hive for hive in config.hives if hive.seed_offset == hive_index_seed_offset)
    arrivals = config.exogenous_arrivals
    if arrivals is None and hive.exogenous_arrival_rate > 0.0:
        arrivals = ExogenousArrivalsConfig(
            enabled=True,
            rate_per_tick=hive.exogenous_arrival_rate,
            near_term_external=0.45,
            long_term_research=0.25,
            internal_improvement=0.20,
            housekeeping=0.10,
        )
    elif arrivals is not None:
        arrivals = replace(arrivals, rate_per_tick=hive.exogenous_arrival_rate)

    return replace(
        config,
        model=replace(config.model, work_service_capacity=hive.work_service_capacity),
        exogenous_arrivals=arrivals,
        hives=(),
        coupling=None,
    )


def _hive_metrics(
    config: OmegaConfig,
    hive_results: tuple[SimulationResult, ...],
) -> list[dict[str, Any]]:
    rows = []
    for hive, result in zip(config.hives, hive_results, strict=True):
        for row in result.metrics:
            rows.append({"hive_id": hive.hive_id, **row})
    return rows


def _hive_events(
    config: OmegaConfig,
    hive_results: tuple[SimulationResult, ...],
) -> list[dict[str, Any]]:
    rows = []
    for hive, result in zip(config.hives, hive_results, strict=True):
        for event in result.events:
            event_row = dict(event)
            if event_row.get("task_id"):
                event_row["task_id"] = _qualified_task_id(
                    hive.hive_id,
                    str(event_row["task_id"]),
                )
            rows.append({"hive_id": hive.hive_id, **event_row})
    return rows


def _qualified_task_id(hive_id: str, task_id: str) -> str:
    if ":" in task_id:
        return task_id
    return f"{hive_id}:{task_id}"


def _aggregate_hive_events(hive_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{field: row.get(field, "") for field in EVENT_FIELDS} for row in hive_events]


def _cross_hive_metrics(
    config: OmegaConfig,
    hive_results: tuple[SimulationResult, ...],
    *,
    coupling_events: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    assert config.coupling is not None
    rows = []
    for tick in range(config.run.ticks):
        tick_rows = [result.metrics[tick] for result in hive_results]
        tick_coupling_events = [
            event for event in (coupling_events or [])
            if int(event["tick"]) == tick
        ]
        queue_depths = [int(row["queue_depth"]) for row in tick_rows]
        queue_deltas = [int(row["queue_delta_tick"]) for row in tick_rows]
        created = [int(row["tasks_created_tick"]) for row in tick_rows]
        completed = [int(row["tasks_completed_tick"]) for row in tick_rows]
        exogenous = [int(row.get("exogenous_tasks_created_tick", 0)) for row in tick_rows]
        inbound = [int(row.get("inbound_transfers_tick", 0)) for row in tick_rows]
        outbound = [int(row.get("outbound_transfers_tick", 0)) for row in tick_rows]
        explicit_drops = [int(row.get("explicit_drops_tick", 0)) for row in tick_rows]
        age_means = [float(row["queued_task_age_mean_tick"]) for row in tick_rows]
        completion_fractions = [
            int(row["tasks_completed_total"]) / int(row["tasks_created_total"])
            if int(row["tasks_created_total"])
            else 0.0
            for row in tick_rows
        ]
        aggregate_delta = sum(queue_deltas)
        aggregate_balance = (
            sum(created)
            + sum(inbound)
            - sum(completed)
            - sum(outbound)
            - sum(explicit_drops)
        )
        rows.append(
            {
                "tick": tick,
                "hive_count": len(config.hives),
                "coupling_mode": config.coupling.mode,
                "transfer_attempts_tick": len(tick_coupling_events),
                "transfers_completed_tick": sum(
                    int(bool(event["transfer_decision"]))
                    for event in tick_coupling_events
                ),
                "inbound_transfers_tick": sum(inbound),
                "outbound_transfers_tick": sum(outbound),
                "queued_age_mean_divergence_tick": round(max(age_means) - min(age_means), 6),
                "completion_fraction_min_tick": round(min(completion_fractions), 6),
                "completion_fraction_max_tick": round(max(completion_fractions), 6),
                "completion_fraction_divergence_tick": round(
                    max(completion_fractions) - min(completion_fractions),
                    6,
                ),
                "aggregate_queue_depth": sum(queue_depths),
                "aggregate_queue_delta_tick": aggregate_delta,
                "aggregate_created_tick": sum(created),
                "aggregate_completed_tick": sum(completed),
                "aggregate_exogenous_arrivals_tick": sum(exogenous),
                "aggregate_inbound_transfers_tick": sum(inbound),
                "aggregate_outbound_transfers_tick": sum(outbound),
                "aggregate_explicit_drops_tick": sum(explicit_drops),
                "aggregate_queue_balance_residual_tick": aggregate_delta - aggregate_balance,
                **{
                    f"{hive.hive_id}_load_normalized_backlog_tick": round(
                        int(row["queue_depth"]) / int(row["tasks_created_total"]),
                        6,
                    )
                    if int(row["tasks_created_total"])
                    else 0.0
                    for hive, row in zip(config.hives, tick_rows, strict=True)
                },
            }
        )
    return rows


def _aggregate_hive_metrics(
    config: OmegaConfig,
    hive_results: tuple[SimulationResult, ...],
    cross_hive_metrics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    first_result = hive_results[0]
    for tick in range(config.run.ticks):
        tick_rows = [result.metrics[tick] for result in hive_results]
        cross_row = cross_hive_metrics[tick]
        aggregate_row = dict(first_result.metrics[tick])
        aggregate_row.update(
            {
                "agent_count": sum(int(row["agent_count"]) for row in tick_rows),
                "bus_nodes": sum(int(row["bus_nodes"]) for row in tick_rows),
                "bus_edges": sum(int(row["bus_edges"]) for row in tick_rows),
                "queue_depth": cross_row["aggregate_queue_depth"],
                "queue_delta_tick": cross_row["aggregate_queue_delta_tick"],
                "tasks_created_total": sum(
                    int(row["tasks_created_total"]) for row in tick_rows
                ),
                "tasks_completed_total": sum(
                    int(row["tasks_completed_total"]) for row in tick_rows
                ),
                "tasks_completed_tick": cross_row["aggregate_completed_tick"],
                "messages_sent_tick": sum(int(row["messages_sent_tick"]) for row in tick_rows),
                "tasks_created_tick": cross_row["aggregate_created_tick"],
                "tasks_worked_tick": sum(int(row["tasks_worked_tick"]) for row in tick_rows),
                "created_completed_balance_tick": (
                    cross_row["aggregate_created_tick"] - cross_row["aggregate_completed_tick"]
                ),
                "created_worked_balance_tick": (
                    cross_row["aggregate_created_tick"]
                    - sum(int(row["tasks_worked_tick"]) for row in tick_rows)
                ),
                "work_completion_gap_tick": (
                    sum(int(row["tasks_worked_tick"]) for row in tick_rows)
                    - cross_row["aggregate_completed_tick"]
                ),
                "backlog_pressure_tick": cross_row["aggregate_queue_depth"],
                "queued_task_age_max_tick": max(
                    int(row["queued_task_age_max_tick"]) for row in tick_rows
                ),
                "queued_task_age_mean_tick": round(
                    sum(float(row["queued_task_age_mean_tick"]) for row in tick_rows)
                    / len(tick_rows),
                    6,
                ),
                "idle_tick": sum(int(row["idle_tick"]) for row in tick_rows),
                "mean_agent_bias": round(
                    sum(float(row["mean_agent_bias"]) for row in tick_rows) / len(tick_rows),
                    6,
                ),
            }
        )
        for field in MULTI_HIVE_QUEUE_FLOW_METRIC_FIELDS:
            if any(field in row for row in tick_rows):
                if field == "queue_balance_residual_tick":
                    aggregate_row[field] = cross_row["aggregate_queue_balance_residual_tick"]
                elif field == "explicit_drops_tick":
                    aggregate_row[field] = cross_row["aggregate_explicit_drops_tick"]
                else:
                    aggregate_row[field] = cross_row[f"aggregate_{field}"]
        for field in EXOGENOUS_ARRIVAL_METRIC_FIELDS:
            if field in aggregate_row:
                aggregate_row[field] = sum(int(row.get(field, 0)) for row in tick_rows)
        for role in BASELINE_ROLES:
            for action in config.model.actions:
                field = f"role_{role}_{action}_tick"
                aggregate_row[field] = sum(int(row[field]) for row in tick_rows)
        rows.append(aggregate_row)
    return rows


def _make_agents(agent_count: int, rng: np.random.Generator) -> tuple[AgentState, ...]:
    agents = []
    for index in range(agent_count):
        role = BASELINE_ROLES[index % len(BASELINE_ROLES)]
        agents.append(
            AgentState(
                agent_id=f"agent_{index + 1:02d}",
                role=role,
                bias=round(float(rng.uniform(0.85, 1.15)), 6),
            )
        )
    return tuple(agents)


def _exogenous_arrival_rng(config: OmegaConfig, seed: int) -> np.random.Generator | None:
    if not _exogenous_arrivals_enabled(config):
        return None
    seed_sequence = np.random.SeedSequence([int(seed), 0xE906E, 0xA2])
    return np.random.default_rng(seed_sequence)


def _make_bus_graph(agents: tuple[AgentState, ...]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_node("bus", kind="bus")
    for agent in agents:
        graph.add_node(agent.agent_id, kind="agent", role=agent.role)
        graph.add_edge("bus", agent.agent_id, channel="omega_bus", weight=1.0)
    return graph


def _bus_graph_metrics(graph: nx.Graph) -> dict[str, float]:
    node_count = graph.number_of_nodes()
    if node_count <= 1:
        return {
            "bus_density": 0.0,
            "bus_mean_degree": 0.0,
            "bus_degree_centralization": 0.0,
        }

    degrees = [degree for _, degree in graph.degree()]
    max_degree = max(degrees)
    centralization_denominator = (node_count - 1) * (node_count - 2)
    if centralization_denominator == 0:
        degree_centralization = 0.0
    else:
        degree_centralization = sum(max_degree - degree for degree in degrees) / centralization_denominator

    return {
        "bus_density": round(float(nx.density(graph)), 6),
        "bus_mean_degree": round(float(np.mean(degrees)), 6),
        "bus_degree_centralization": round(float(degree_centralization), 6),
    }


def _role_action_metrics(
    actions: tuple[str, ...],
    role_action_counts: Counter[tuple[str, str]],
) -> dict[str, int]:
    return {
        field: role_action_counts[(role, action)]
        for role in BASELINE_ROLES
        for action in actions
        for field in (f"role_{role}_{action}_tick",)
    }


def _queue_age_metrics(task_queue: deque[Task], tick: int) -> dict[str, float | int]:
    if not task_queue:
        return {
            "queued_task_age_max_tick": 0,
            "queued_task_age_mean_tick": 0.0,
        }

    ages = [tick - task.created_tick for task in task_queue]
    return {
        "queued_task_age_max_tick": max(ages),
        "queued_task_age_mean_tick": round(float(np.mean(ages)), 6),
    }


def _choose_task_class(config: OmegaConfig, rng: np.random.Generator) -> str:
    if config.attention_policy is None:
        return ""
    shares = config.attention_policy.shares()
    probabilities = np.array([shares[class_name] for class_name in ATTENTION_CLASSES], dtype=float)
    return str(rng.choice(ATTENTION_CLASSES, p=probabilities))


def _exogenous_arrivals_enabled(config: OmegaConfig) -> bool:
    return (
        config.exogenous_arrivals is not None
        and config.exogenous_arrivals.enabled
    )


def _choose_exogenous_task_class(config: OmegaConfig, rng: np.random.Generator) -> str:
    assert config.exogenous_arrivals is not None
    shares = config.exogenous_arrivals.task_class_shares()
    probabilities = np.array([shares[class_name] for class_name in ATTENTION_CLASSES], dtype=float)
    return str(rng.choice(ATTENTION_CLASSES, p=probabilities))


def _exogenous_arrival_metrics(
    *,
    config: OmegaConfig,
    agent_created_tick: int,
    agent_created_total: int,
    exogenous_created_tick: int,
    exogenous_created_total: int,
) -> dict[str, int]:
    if not _exogenous_arrivals_enabled(config):
        return {}
    return {
        "agent_tasks_created_tick": agent_created_tick,
        "agent_tasks_created_total": agent_created_total,
        "exogenous_tasks_created_tick": exogenous_created_tick,
        "exogenous_tasks_created_total": exogenous_created_total,
    }


def _pop_work_task(
    task_queue: deque[Task],
    config: OmegaConfig,
    attention_work_counts: Counter[str],
    *,
    desired_class: str = "",
    selected_index: int | None = None,
) -> Task:
    if config.attention_policy is None:
        return task_queue.popleft()

    if selected_index is not None:
        task = task_queue[selected_index]
        del task_queue[selected_index]
        return task

    if not desired_class:
        desired_class = _desired_attention_class(task_queue, config, attention_work_counts)
    for index, task in enumerate(task_queue):
        if task.task_class == desired_class:
            del task_queue[index]
            return task
    return task_queue.popleft()


def _desired_attention_class(
    task_queue: deque[Task],
    config: OmegaConfig,
    attention_work_counts: Counter[str],
) -> str:
    assert config.attention_policy is not None
    available_classes = {task.task_class for task in task_queue}
    shares = config.attention_policy.shares()
    total_work = sum(attention_work_counts.values())

    def priority(class_name: str) -> tuple[float, int]:
        actual_share = attention_work_counts[class_name] / total_work if total_work else 0.0
        return actual_share - shares[class_name], ATTENTION_CLASSES.index(class_name)

    return min(
        (class_name for class_name in ATTENTION_CLASSES if class_name in available_classes),
        key=priority,
    )


def _attention_policy_metrics(
    *,
    config: OmegaConfig,
    task_queue: deque[Task],
    tick: int,
    work_counts_tick: Counter[str],
    work_counts: Counter[str],
    completed_counts: Counter[str],
    value_weighted_completed_tick: int,
    value_weighted_completed_total: int,
    completed_this_tick: int,
    completed_total: int,
) -> dict[str, int | float]:
    if config.attention_policy is None:
        return {}

    shares = config.attention_policy.shares()
    total_work_tick = sum(work_counts_tick.values())
    total_work = sum(work_counts.values())
    metrics: dict[str, int | float] = {}
    for class_name in ATTENTION_CLASSES:
        queued_tasks = [task for task in task_queue if task.task_class == class_name]
        ages = [tick - task.created_tick for task in queued_tasks]
        queued_share = len(queued_tasks) / len(task_queue) if task_queue else 0.0
        capture_pressure = max(queued_share - shares[class_name], 0.0)
        actual_share = work_counts_tick[class_name] / total_work_tick if total_work_tick else 0.0
        metrics.update(
            {
                f"attention_{class_name}_queued_tick": len(queued_tasks),
                f"attention_{class_name}_completed_total": completed_counts[class_name],
                f"attention_{class_name}_worked_total": work_counts[class_name],
                f"attention_{class_name}_queued_age_max_tick": max(ages, default=0),
                f"attention_{class_name}_queued_age_mean_tick": (
                    round(float(np.mean(ages)), 6) if ages else 0.0
                ),
                f"attention_{class_name}_spent_share_tick": round(float(actual_share), 6),
                f"attention_{class_name}_target_share": shares[class_name],
                f"attention_{class_name}_share_deviation_tick": round(
                    float(actual_share - shares[class_name]),
                    6,
                ),
                f"attention_{class_name}_capture_pressure_tick": round(
                    float(capture_pressure),
                    6,
                ),
            }
        )
    metrics["attention_capture_pressure_max_tick"] = max(
        (
            metrics[f"attention_{class_name}_capture_pressure_tick"]
            for class_name in ATTENTION_CLASSES
        ),
        default=0.0,
    )
    metrics["attention_value_weighted_completed_tick"] = value_weighted_completed_tick
    metrics["attention_value_weighted_completed_total"] = value_weighted_completed_total
    metrics["attention_value_per_completed_task_tick"] = (
        round(value_weighted_completed_tick / completed_this_tick, 6)
        if completed_this_tick
        else 0.0
    )
    metrics["attention_value_per_completed_task_total"] = (
        round(value_weighted_completed_total / completed_total, 6)
        if completed_total
        else 0.0
    )
    metrics["attention_value_per_work_event_tick"] = (
        round(value_weighted_completed_tick / total_work_tick, 6)
        if total_work_tick
        else 0.0
    )
    metrics["attention_value_per_work_event_total"] = (
        round(value_weighted_completed_total / total_work, 6)
        if total_work
        else 0.0
    )
    return metrics


def _attention_capture_pressure_event(
    *,
    tick: int,
    agent: AgentState,
    action: str,
    task_queue: deque[Task],
    config: OmegaConfig,
    selected_class: str,
) -> dict[str, Any] | None:
    assert config.attention_policy is not None
    if not task_queue:
        return None

    shares = config.attention_policy.shares()
    queue_counts = Counter(task.task_class for task in task_queue)
    candidates = []
    for class_name in ATTENTION_CLASSES:
        if class_name == selected_class or queue_counts[class_name] == 0:
            continue
        queued_share = queue_counts[class_name] / len(task_queue)
        capture_pressure = queued_share - shares[class_name]
        if capture_pressure > 0.0:
            candidates.append(
                (
                    -round(float(capture_pressure), 6),
                    ATTENTION_CLASSES.index(class_name),
                    class_name,
                    round(float(capture_pressure), 6),
                )
            )
    if not candidates:
        return None

    _, _, pressure_class, capture_pressure = sorted(candidates)[0]
    return _event(
        tick=tick,
        event_type="attention_capture_pressure",
        agent_id=agent.agent_id,
        action=action,
        task_class=selected_class,
        attention_selected_class=selected_class,
        attention_pressure_class=pressure_class,
        attention_capture_pressure=capture_pressure,
    )


def _baseline_lobe_label(
    *,
    action_counts: Counter[str],
    queue_depth_start: int,
    queue_depth_end: int,
) -> str:
    queue_delta = queue_depth_end - queue_depth_start
    if (
        queue_depth_end > 0
        and queue_delta > 0
        and action_counts["create_task"] >= action_counts["work_task"]
    ):
        return "backlog_growth"

    dominant_action = _dominant_action(action_counts)
    if dominant_action == "work_task":
        return "execution"
    if dominant_action == "create_task":
        return "task_generation"
    if dominant_action == "message":
        return "coordination"
    return "low_activity"


def _baseline_lobe_transition(previous_label: str, current_label: str) -> str:
    if not previous_label:
        return "start"
    if previous_label == current_label:
        return "stable"
    return f"{previous_label}->{current_label}"


def _dominant_action(action_counts: Counter[str]) -> str:
    priority = ("work_task", "create_task", "message", "idle")
    return max(priority, key=lambda action: (action_counts[action], -priority.index(action)))


def _choose_action(
    actions: tuple[str, ...],
    has_queued_tasks: bool,
    agent: AgentState,
    rng: np.random.Generator,
    *,
    task_creation_pressure: float = 1.0,
    work_service_capacity: float = 1.0,
) -> str:
    allowed_actions = list(actions)
    weights = {
        "idle": 0.18,
        "message": 0.34,
        "create_task": 0.22,
        "work_task": 0.26 if has_queued_tasks else 0.0,
    }
    if agent.role in {"implementer", "reviewer"} and has_queued_tasks:
        weights["work_task"] *= agent.bias
    weights["create_task"] *= task_creation_pressure
    weights["work_task"] *= work_service_capacity
    if agent.role == "researcher":
        weights["create_task"] *= agent.bias
    if agent.role == "coordinator":
        weights["message"] *= agent.bias

    probabilities = np.array([weights[action] for action in allowed_actions], dtype=float)
    if probabilities.sum() == 0.0:
        return "idle"
    probabilities = probabilities / probabilities.sum()
    return str(rng.choice(allowed_actions, p=probabilities))


def _choose_target(
    agent: AgentState,
    agents: tuple[AgentState, ...],
    rng: np.random.Generator,
) -> AgentState:
    candidates = [candidate for candidate in agents if candidate.agent_id != agent.agent_id]
    target_index = int(rng.integers(0, len(candidates)))
    return candidates[target_index]


def _event(
    *,
    tick: int,
    event_type: str,
    agent_id: str,
    action: str,
    target_id: str = "",
    task_id: str = "",
    work_units: int | str = "",
    remaining_work: int | str = "",
    completed: bool | str = "",
    task_class: str = "",
    attention_selected_class: str = "",
    attention_pressure_class: str = "",
    attention_capture_pressure: float | str = "",
) -> dict[str, Any]:
    return {
        "tick": tick,
        "event_type": event_type,
        "agent_id": agent_id,
        "action": action,
        "target_id": target_id,
        "task_id": task_id,
        "work_units": work_units,
        "remaining_work": remaining_work,
        "completed": completed,
        "task_class": task_class,
        "attention_selected_class": attention_selected_class,
        "attention_pressure_class": attention_pressure_class,
        "attention_capture_pressure": attention_capture_pressure,
    }
