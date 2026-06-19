"""Deterministic OmegaHive-like baseline simulation."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from typing import Any

import networkx as nx
import numpy as np

from ohdyn.config import OmegaConfig


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
    previous_lobe_label = ""

    for tick in range(config.run.ticks):
        queue_depth_start = len(task_queue)
        action_counts: Counter[str] = Counter()
        role_action_counts: Counter[tuple[str, str]] = Counter()
        completed_this_tick = 0
        for agent in agents:
            action = _choose_action(config.model.actions, bool(task_queue), agent, rng)
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
                task = task_queue.popleft()
                task.remaining_work -= 1
                completed = task.remaining_work <= 0
                if completed:
                    completed_tasks += 1
                    completed_this_tick += 1
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
        baseline_lobe_label = _baseline_lobe_label(
            action_counts=action_counts,
            queue_depth_start=queue_depth_start,
            queue_depth_end=queue_depth_end,
        )
        baseline_lobe_transition = _baseline_lobe_transition(
            previous_lobe_label,
            baseline_lobe_label,
        )
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
                "tasks_created_total": task_counter,
                "tasks_completed_total": completed_tasks,
                "tasks_completed_tick": completed_this_tick,
                "messages_sent_tick": action_counts["message"],
                "tasks_created_tick": action_counts["create_task"],
                "tasks_worked_tick": action_counts["work_task"],
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
        f"role_{role}_{action}_tick": role_action_counts[(role, action)]
        for role in BASELINE_ROLES
        for action in actions
    }


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
