"""Deterministic OmegaHive-like baseline simulation."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from typing import Any

import networkx as nx
import numpy as np

from ohdyn.config import ATTENTION_CLASSES, OmegaConfig


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
                f"attention_{class_name}_queued_age_max_tick",
                f"attention_{class_name}_queued_age_mean_tick",
                f"attention_{class_name}_spent_share_tick",
                f"attention_{class_name}_target_share",
                f"attention_{class_name}_share_deviation_tick",
            )
        ),
        "attention_value_weighted_completed_tick",
        "attention_value_weighted_completed_total",
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


def simulate(config: OmegaConfig, seed: int) -> SimulationResult:
    rng = np.random.default_rng(seed)
    agents = _make_agents(config.model.agent_count, rng)
    bus_graph = _make_bus_graph(agents)
    bus_metrics = _bus_graph_metrics(bus_graph)
    task_queue: deque[Task] = deque()
    events: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    task_counter = 0
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
        for agent in agents:
            action = _choose_action(
                config.model.actions,
                bool(task_queue),
                agent,
                rng,
                task_creation_pressure=config.model.task_creation_pressure,
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
                task = _pop_work_task(task_queue, config, attention_work_counts)
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
            completed_counts=attention_completed_counts,
            value_weighted_completed_tick=attention_value_weighted_completed_tick,
            value_weighted_completed_total=attention_value_weighted_completed_total,
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
                "tasks_created_tick": action_counts["create_task"],
                "tasks_worked_tick": action_counts["work_task"],
                "created_completed_balance_tick": action_counts["create_task"] - completed_this_tick,
                "created_worked_balance_tick": action_counts["create_task"] - action_counts["work_task"],
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


def _pop_work_task(
    task_queue: deque[Task],
    config: OmegaConfig,
    attention_work_counts: Counter[str],
) -> Task:
    if config.attention_policy is None:
        return task_queue.popleft()

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
    completed_counts: Counter[str],
    value_weighted_completed_tick: int,
    value_weighted_completed_total: int,
) -> dict[str, int | float]:
    if config.attention_policy is None:
        return {}

    shares = config.attention_policy.shares()
    total_work_tick = sum(work_counts_tick.values())
    metrics: dict[str, int | float] = {}
    for class_name in ATTENTION_CLASSES:
        queued_tasks = [task for task in task_queue if task.task_class == class_name]
        ages = [tick - task.created_tick for task in queued_tasks]
        actual_share = work_counts_tick[class_name] / total_work_tick if total_work_tick else 0.0
        metrics.update(
            {
                f"attention_{class_name}_queued_tick": len(queued_tasks),
                f"attention_{class_name}_completed_total": completed_counts[class_name],
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
            }
        )
    metrics["attention_value_weighted_completed_tick"] = value_weighted_completed_tick
    metrics["attention_value_weighted_completed_total"] = value_weighted_completed_total
    return metrics


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
    }
