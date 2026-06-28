"""Deterministic OmegaHive-like baseline simulation."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import replace, dataclass
from typing import Any

import networkx as nx
import numpy as np

from ohdyn.a7_semantic_field_contract import (
    A7_CONTROL_FIELDS,
    A7_EVENT_FIELDS,
    A7_FIELD_VALUES,
    A7_METRIC_FIELDS,
    A7_RNG_STREAMS,
    A7_SOURCE_COMPONENTS,
)
from ohdyn.a7_2_delayed_prediction_contract import (
    A7_2_ACTIONS,
    A7_2_EVENT_FIELDS,
    a7_2_required_metric_fields,
)
from ohdyn.config import (
    A6_ACTIONS,
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

A5_EVENT_TYPES = (
    "a5_prediction_spent",
)

ATTENTION_EVENT_TYPES = (
    "attention_capture_pressure",
)

EXOGENOUS_ARRIVAL_EVENT_TYPES = (
    "exogenous_task_arrived",
)

A6_EVENT_TYPES = (
    "a6_appraisal_update",
    "a6_artifact_update",
    "a6_handoff_attempted",
    "a6_handoff_succeeded",
    "a6_handoff_failed",
    "a6_prediction_spent",
    "a6_threshold_adapted",
)

A6_ARTIFACT_UPDATE_SOURCE_FIELDS = (
    "a6_artifact_update_source",
    "a6_artifact_field",
    "a6_artifact_delta_total",
    "a6_artifact_delta_ambient",
    "a6_artifact_delta_handoff_attempt",
    "a6_artifact_delta_handoff_success",
    "a6_artifact_delta_handoff_failure",
    "a6_artifact_delta_prediction_expenditure",
    "a6_artifact_delta_prediction_error",
    "a6_artifact_delta_queue_work_accounting",
    "a6_artifact_delta_noise",
    "a6_artifact_delta_unclipped",
    "a6_artifact_delta_clip_residual",
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
    "a5_prediction_spend_charged",
    "a5_prediction_work_budget_remaining",
    *A6_ARTIFACT_UPDATE_SOURCE_FIELDS,
    *tuple(field for field in A7_EVENT_FIELDS if field not in {"tick", "agent_id", "event_type"}),
    *tuple(field for field in A7_2_EVENT_FIELDS if field not in {"tick", "agent_id", "event_type"}),
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
    include_predictive_control: bool = False,
    include_logistic_appraisal: bool = False,
    include_semantic_field: bool = False,
    include_a7_2_delayed_prediction: bool = False,
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
        *(predictive_control_metric_fields() if include_predictive_control else ()),
        *(logistic_appraisal_metric_fields() if include_logistic_appraisal else ()),
        *(semantic_field_metric_fields() if include_semantic_field else ()),
        *(
            a7_2_delayed_prediction_metric_fields()
            if include_a7_2_delayed_prediction
            else ()
        ),
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


def predictive_control_metric_fields() -> tuple[str, ...]:
    return (
        "a5_predictive_condition",
        "a5_prediction_budget",
        "a5_prediction_budget_spent_tick",
        "a5_prediction_cost_scale",
        "a5_max_prediction_work_fraction_per_tick",
        "a5_prediction_charged_to_work",
        "a5_prediction_work_charge_target_tick",
        "a5_prediction_work_charged_tick",
        "a5_work_opportunity_before_prediction_tick",
        "a5_work_budget_remaining_tick",
        "a5_prediction_lead_ticks",
        *(
            field
            for class_name in ATTENTION_CLASSES
            for field in (
                f"a5_{class_name}_demand_share_tick",
                f"a5_{class_name}_future_demand_share_tick",
                f"a5_{class_name}_forecast_share_tick",
                f"a5_{class_name}_forecast_error_tick",
                f"a5_{class_name}_work_share_tick",
                f"a5_{class_name}_allocation_future_residual_tick",
            )
        ),
        "a5_forecast_abs_error_tick",
        "a5_forecast_skill_tick",
        "a5_forecast_skill_per_budget_tick",
        "a5_work_forecast_alignment_tick",
        "a5_work_future_demand_alignment_tick",
    )


A6_ARTIFACT_FIELDS = (
    "artifact_novelty",
    "artifact_coherence",
    "artifact_actionability",
    "artifact_provenance_debt",
    "artifact_risk",
    "artifact_contradiction",
    "artifact_readiness",
    "artifact_implementation_maturity",
    "artifact_communication_maturity",
)

_A6_ARTIFACT_DELTA_SOURCE_FIELDS = (
    "ambient_artifact_drift",
    "handoff_attempt_effect",
    "handoff_success_effect",
    "handoff_failure_effect",
    "prediction_expenditure_effect",
    "prediction_error_effect",
    "queue_work_accounting_effect",
    "noise_effect",
)

A6_LATENT_FIELDS = (
    "activation",
    "focus",
    "fatigue",
    "novelty_appetite",
    "risk_sensitivity",
    "handoff_threshold",
    "prediction_error",
)


def logistic_appraisal_metric_fields() -> tuple[str, ...]:
    return (
        "a6_condition",
        "a6_appraisal_gain",
        "a6_sigmoid_slope",
        "a6_prediction_budget",
        "a6_prediction_budget_available_tick",
        "a6_prediction_budget_spent_tick",
        "a6_prediction_actions_tick",
        "a6_prediction_error_mean_tick",
        "a6_latent_activation_mean_tick",
        "a6_latent_focus_mean_tick",
        "a6_latent_fatigue_mean_tick",
        "a6_latent_prediction_error_mean_tick",
        "a6_artifact_novelty_tick",
        "a6_artifact_coherence_tick",
        "a6_artifact_actionability_tick",
        "a6_artifact_provenance_debt_tick",
        "a6_artifact_risk_tick",
        "a6_artifact_contradiction_tick",
        "a6_artifact_readiness_tick",
        "a6_artifact_implementation_maturity_tick",
        "a6_artifact_communication_maturity_tick",
        "a6_handoff_attempts_tick",
        "a6_handoff_successes_tick",
        "a6_handoff_failures_tick",
        "a6_queue_depth_tick",
        "a6_work_actions_tick",
        "a6_action_opportunity_tick",
        "a6_service_capacity_tick",
    )


def semantic_field_metric_fields() -> tuple[str, ...]:
    return (
        "a7_condition",
        "a7_prediction_budget_per_tick",
        "a7_lead_ticks",
        "a7_semantic_decay",
        "a7_logistic_beta",
        "a7_linear_gain",
        "a7_threshold_adaptation_rate",
        "a7_semantic_noise",
        *A7_METRIC_FIELDS,
        *A7_CONTROL_FIELDS,
        "a7_threshold_mean_tick",
        "a7_fatigue_mean_tick",
        "a7_near_threshold_occupancy_tick",
    )


def a7_2_delayed_prediction_metric_fields() -> tuple[str, ...]:
    baseline_metric_fields = set(metrics_fieldnames((), include_a7_2_delayed_prediction=False))
    return tuple(
        field for field in a7_2_required_metric_fields() if field not in baseline_metric_fields
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


@dataclass
class _A6TickState:
    prediction_budget_spent: float = 0.0
    prediction_actions: int = 0
    handoff_attempts: int = 0
    handoff_successes: int = 0
    handoff_failures: int = 0


@dataclass
class _A7TickState:
    prediction_budget_spent: float = 0.0
    prediction_error_sum: float = 0.0
    prediction_actions: int = 0
    work_actions: int = 0
    handoff_attempts: int = 0
    handoff_successes: int = 0
    handoff_failures: int = 0
    near_threshold_count: int = 0


@dataclass
class _A7_2TickState:
    prediction_spend: float = 0.0
    lost_work_opportunity: float = 0.0
    selected_actions: Counter[str] | None = None
    utilities: dict[str, float] | None = None
    source_ledger_forecast_error: float = 0.0
    source_ledger_artifact: float = 0.0
    source_ledger_queue_accounting: float = 0.0


@dataclass(frozen=True)
class _PendingTransfer:
    arrival_tick: int
    source_hive_id: str
    target_hive_id: str
    task: Task


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
    a6_appraisal_rng = _a6_stream_rng(config, seed, "appraisal_noise_stream")
    a6_artifact_rng = _a6_stream_rng(config, seed, "artifact_update_stream")
    a6_prediction_rng = _a6_stream_rng(config, seed, "prediction_noise_stream")
    a6_shuffle_rng = _a6_stream_rng(config, seed, "control_shuffle_stream")
    a6_latent = _initial_a6_latent(agents, config, a6_appraisal_rng)
    a6_artifact = _initial_a6_artifact(config)
    a7_action_rng = _a7_stream_rng(config, seed, "baseline_action_stream")
    a7_update_rng = _a7_stream_rng(config, seed, "semantic_update_stream")
    a7_prediction_rng = _a7_stream_rng(config, seed, "prediction_noise_stream")
    a7_shuffle_rng = _a7_stream_rng(config, seed, "semantic_control_shuffle_stream")
    a7_agent_state = _initial_a7_agent_state(agents, config, a7_update_rng)
    a7_field = _initial_a7_field(config)
    a7_2_action_rng = _a7_2_stream_rng(config, seed, "action")
    a7_2_prediction_rng = _a7_2_stream_rng(config, seed, "prediction")
    a7_2_shuffle_rng = _a7_2_stream_rng(config, seed, "shuffle")
    a7_2_agent_state = _initial_a7_2_agent_state(agents, config)
    a7_2_artifact = _initial_a7_2_artifact(config)
    a7_2_forecast_updates: deque[dict[str, float | int]] = deque()
    a7_2_artifact_updates: deque[dict[str, float | int]] = deque()
    a5_prediction_charge_bank = 0.0

    for tick in range(config.run.ticks):
        queue_depth_start = len(task_queue)
        action_counts: Counter[str] = Counter()
        role_action_counts: Counter[tuple[str, str]] = Counter()
        attention_work_counts_tick: Counter[str] = Counter()
        attention_completed_counts_tick: Counter[str] = Counter()
        completed_this_tick = 0
        attention_value_weighted_completed_tick = 0
        exogenous_created_this_tick = 0
        a5_prediction_work_charged_tick = 0
        a5_prediction_work_charge_target_tick = _a5_prediction_work_charge_target(
            config,
            len(agents),
        )
        if _a5_prediction_charges_work(config):
            a5_prediction_charge_bank += a5_prediction_work_charge_target_tick
        a6_tick = _A6TickState()
        a7_tick = _A7TickState()
        a7_2_tick = _A7_2TickState(selected_actions=Counter(), utilities={})
        if config.a7_2_delayed_prediction is not None:
            _advance_a7_2_delayed_state(
                config=config,
                artifact=a7_2_artifact,
                forecast_updates=a7_2_forecast_updates,
                artifact_updates=a7_2_artifact_updates,
                tick=tick,
                events=events,
                tick_state=a7_2_tick,
            )
        if config.logistic_appraisal is not None:
            _advance_a6_background_state(
                config=config,
                latent=a6_latent,
                artifact=a6_artifact,
                tick=tick,
                appraisal_rng=a6_appraisal_rng,
                artifact_rng=a6_artifact_rng,
                shuffle_rng=a6_shuffle_rng,
                events=events,
            )
        if config.semantic_field is not None:
            _advance_a7_background_state(
                config=config,
                field=a7_field,
                tick=tick,
                update_rng=a7_update_rng,
                shuffle_rng=a7_shuffle_rng,
                queue_depth=queue_depth_start,
                events=events,
            )
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
                    task_class=_choose_exogenous_task_class(
                        config,
                        exogenous_rng,
                        tick,
                    ),
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
            if config.a7_2_delayed_prediction is not None:
                assert a7_2_action_rng is not None
                action = _choose_a7_2_action(
                    config=config,
                    has_queued_tasks=bool(task_queue),
                    agent=agent,
                    rng=a7_2_action_rng,
                    agent_state=a7_2_agent_state[agent.agent_id],
                    artifact=a7_2_artifact,
                    queue_depth=queue_depth_start,
                    tick=tick,
                    tick_state=a7_2_tick,
                )
            elif config.semantic_field is not None:
                assert a7_action_rng is not None
                action = _choose_semantic_field_action(
                    config=config,
                    has_queued_tasks=bool(task_queue),
                    agent=agent,
                    rng=a7_action_rng,
                    agent_state=a7_agent_state[agent.agent_id],
                    field=a7_field,
                    tick=tick,
                )
            elif config.logistic_appraisal is None:
                action = _choose_action(
                    config.model.actions,
                    bool(task_queue),
                    agent,
                    rng,
                    task_creation_pressure=config.model.task_creation_pressure,
                    work_service_capacity=config.model.work_service_capacity,
                )
            else:
                action = _choose_logistic_appraisal_action(
                    config=config,
                    has_queued_tasks=bool(task_queue),
                    agent=agent,
                    rng=rng,
                    latent=a6_latent[agent.agent_id],
                    artifact=a6_artifact,
                    tick=tick,
                )
            charged_prediction_spend = (
                action == "work_task"
                and _a5_prediction_charges_work(config)
                and a5_prediction_charge_bank >= 1.0
            )
            if charged_prediction_spend:
                a5_prediction_charge_bank -= 1.0
                a5_prediction_work_charged_tick += 1
                action = "idle"
            action_counts[action] += 1
            role_action_counts[(agent.role, action)] += 1

            if charged_prediction_spend:
                events.append(
                    _event(
                        tick=tick,
                        event_type="a5_prediction_spent",
                        agent_id=agent.agent_id,
                        action=action,
                        a5_prediction_spend_charged=1,
                        a5_prediction_work_budget_remaining=max(
                            len(agents) - a5_prediction_work_charged_tick,
                            0,
                        ),
                    )
                )
                continue

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
                    task_class=_choose_task_class(config, rng, tick),
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
                    _desired_work_task_class(
                        task_queue,
                        config,
                        attention_work_counts,
                        tick,
                    )
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
                if config.a7_2_delayed_prediction is not None:
                    _apply_a7_2_work_action(
                        config=config,
                        tick=tick,
                        agent=agent,
                        agent_state=a7_2_agent_state[agent.agent_id],
                        artifact=a7_2_artifact,
                        tick_state=a7_2_tick,
                        events=events,
                    )
            elif action in A6_ACTIONS:
                if config.a7_2_delayed_prediction is not None:
                    _apply_a7_2_action(
                        config=config,
                        tick=tick,
                        agent=agent,
                        action=action,
                        agent_state=a7_2_agent_state[agent.agent_id],
                        artifact=a7_2_artifact,
                        forecast_updates=a7_2_forecast_updates,
                        artifact_updates=a7_2_artifact_updates,
                        prediction_rng=a7_2_prediction_rng,
                        shuffle_rng=a7_2_shuffle_rng,
                        tick_state=a7_2_tick,
                        events=events,
                    )
                elif config.semantic_field is not None:
                    _apply_semantic_field_action(
                        config=config,
                        tick=tick,
                        agent=agent,
                        action=action,
                        agent_state=a7_agent_state[agent.agent_id],
                        field=a7_field,
                        prediction_rng=a7_prediction_rng,
                        a7_tick=a7_tick,
                        events=events,
                    )
                else:
                    _apply_logistic_appraisal_action(
                        config=config,
                        tick=tick,
                        agent=agent,
                        action=action,
                        latent=a6_latent[agent.agent_id],
                        artifact=a6_artifact,
                        prediction_rng=a6_prediction_rng,
                        a6_tick=a6_tick,
                        events=events,
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
        predictive_metrics = _predictive_control_metrics(
            config=config,
            tick=tick,
            work_counts_tick=attention_work_counts_tick,
            action_opportunity=len(agents),
            prediction_work_charge_target_tick=a5_prediction_work_charge_target_tick,
            prediction_work_charged_tick=a5_prediction_work_charged_tick,
        )
        a6_metrics = _logistic_appraisal_metrics(
            config=config,
            latent=a6_latent,
            artifact=a6_artifact,
            a6_tick=a6_tick,
            queue_depth=queue_depth_end,
            work_actions=action_counts["work_task"],
            action_opportunity=len(agents),
        )
        a7_metrics = _semantic_field_metrics(
            config=config,
            agent_state=a7_agent_state,
            field=a7_field,
            a7_tick=a7_tick,
            queue_depth=queue_depth_end,
            queue_delta=queue_delta,
            tasks_created_total=task_counter,
            tasks_completed_total=completed_tasks,
            action_opportunity=len(agents),
        )
        a7_2_metrics = _a7_2_delayed_prediction_metrics(
            config=config,
            agent_state=a7_2_agent_state,
            artifact=a7_2_artifact,
            tick_state=a7_2_tick,
            forecast_queue_length=len(a7_2_forecast_updates),
            artifact_queue_length=len(a7_2_artifact_updates),
            tick=tick,
            queue_depth=queue_depth_end,
            queue_age_metrics=queue_age_metrics,
            completed_this_tick=completed_this_tick,
            completed_total=completed_tasks,
            task_arrivals=action_counts["create_task"] + exogenous_created_this_tick,
            action_opportunity=len(agents),
            work_actions=action_counts["work_task"],
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
                **predictive_metrics,
                **a6_metrics,
                **a7_metrics,
                **a7_2_metrics,
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
    if config.coupling.mode in {"direct", "delayed", "shuffled"}:
        return _simulate_multi_hive_coupled(config, seed)
    raise ValueError(
        "A4 multi-hive simulation currently supports coupling.mode 'none', "
        "'direct', 'delayed', and 'shuffled'."
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


def _simulate_multi_hive_coupled(config: OmegaConfig, seed: int) -> SimulationResult:
    assert config.coupling is not None
    coupling_rng = np.random.default_rng(seed + config.coupling.shuffle_seed_offset)
    runtimes = tuple(_make_hive_runtime(config, hive, seed) for hive in config.hives)
    coupling_events: list[dict[str, Any]] = []
    pending_transfers: list[_PendingTransfer] = []

    for tick in range(config.run.ticks):
        for runtime in runtimes:
            _begin_hive_tick(runtime)
        _deliver_pending_transfers(
            pending_transfers=pending_transfers,
            runtimes=runtimes,
            tick=tick,
        )

        for source_index, runtime in enumerate(runtimes):
            _advance_hive_runtime_tick(
                runtime=runtime,
                runtimes=runtimes,
                source_index=source_index,
                tick=tick,
                coupling_rng=coupling_rng,
                coupling_events=coupling_events,
                pending_transfers=pending_transfers,
                coupling_mode=config.coupling.mode,
                delay_ticks=config.coupling.delay_ticks,
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
    pending_transfers: list[_PendingTransfer],
    coupling_mode: str,
    delay_ticks: int,
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
                task_class=_choose_exogenous_task_class(
                    config,
                    runtime.exogenous_rng,
                    tick,
                ),
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
                pending_transfers=pending_transfers,
                coupling_mode=coupling_mode,
                delay_ticks=delay_ticks,
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
                task_class=_choose_task_class(config, runtime.rng, tick),
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
                pending_transfers=pending_transfers,
                coupling_mode=coupling_mode,
                delay_ticks=delay_ticks,
            )
        elif action == "work_task":
            selected_task_index: int | None = None
            assert runtime.attention_work_counts is not None
            assert runtime.attention_work_counts_tick is not None
            assert runtime.attention_completed_counts is not None
            assert runtime.attention_completed_counts_tick is not None
            desired_attention_class = (
                _desired_work_task_class(
                    runtime.task_queue,
                    config,
                    runtime.attention_work_counts,
                    tick,
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
    pending_transfers: list[_PendingTransfer],
    coupling_mode: str,
    delay_ticks: int,
) -> None:
    # The local runtime config intentionally strips coupling; the shared parent
    # config controls the active mode through runtime transfer settings.
    if len(runtimes) <= 1:
        runtime.task_queue.append(task)
        return

    target_index = _coupling_target_index(
        runtimes=runtimes,
        source_index=source_index,
        coupling_mode=coupling_mode,
        coupling_rng=coupling_rng,
    )
    target = runtimes[target_index]
    runtime.transfer_attempts_tick += 1
    transfer_decision = bool(coupling_rng.random() < runtime.transfer_probability)
    global_task_id = _qualified_task_id(runtime.hive_id, task.task_id)
    arrival_tick = tick + delay_ticks
    coupling_events.append(
        {
            "tick": tick,
            "source_hive_id": runtime.hive_id,
            "target_hive_id": target.hive_id,
            "task_id": global_task_id,
            "coupling_mode": coupling_mode,
            "delay_ticks": delay_ticks,
            "transfer_decision": transfer_decision,
            "arrival_tick": arrival_tick if transfer_decision else "",
        }
    )
    if not transfer_decision:
        runtime.task_queue.append(task)
        return

    runtime.outbound_transfers_tick += 1
    runtime.transfers_completed_tick += 1
    transferred_task = replace(task, task_id=global_task_id)
    if delay_ticks == 0:
        target.inbound_transfers_tick += 1
        target.task_queue.append(transferred_task)
        return

    pending_transfers.append(
        _PendingTransfer(
            arrival_tick=arrival_tick,
            source_hive_id=runtime.hive_id,
            target_hive_id=target.hive_id,
            task=transferred_task,
        )
    )


def _coupling_target_index(
    *,
    runtimes: tuple[_HiveRuntime, ...],
    source_index: int,
    coupling_mode: str,
    coupling_rng: np.random.Generator,
) -> int:
    if coupling_mode != "shuffled":
        return (source_index + 1) % len(runtimes)

    eligible_targets = [
        index for index in range(len(runtimes))
        if index != source_index
    ]
    return int(coupling_rng.choice(eligible_targets))


def _deliver_pending_transfers(
    *,
    pending_transfers: list[_PendingTransfer],
    runtimes: tuple[_HiveRuntime, ...],
    tick: int,
) -> None:
    if not pending_transfers:
        return

    runtime_by_id = {runtime.hive_id: runtime for runtime in runtimes}
    arrivals = sorted(
        (transfer for transfer in pending_transfers if transfer.arrival_tick == tick),
        key=lambda transfer: (
            transfer.arrival_tick,
            transfer.source_hive_id,
            transfer.target_hive_id,
            transfer.task.task_id,
        ),
    )
    if not arrivals:
        return

    remaining = [
        transfer for transfer in pending_transfers if transfer.arrival_tick != tick
    ]
    pending_transfers[:] = remaining
    for transfer in arrivals:
        target = runtime_by_id[transfer.target_hive_id]
        target.inbound_transfers_tick += 1
        target.task_queue.append(transfer.task)


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
    predictive_metrics = _predictive_control_metrics(
        config=config,
        tick=tick,
        work_counts_tick=runtime.attention_work_counts_tick,
        action_opportunity=config.model.agent_count,
        prediction_work_charge_target_tick=0.0,
        prediction_work_charged_tick=0,
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
            **predictive_metrics,
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


def _choose_task_class(config: OmegaConfig, rng: np.random.Generator, tick: int) -> str:
    if config.attention_policy is None:
        return ""
    shares = _a5_demand_shares(config, tick)
    probabilities = np.array([shares[class_name] for class_name in ATTENTION_CLASSES], dtype=float)
    return str(rng.choice(ATTENTION_CLASSES, p=probabilities))


def _exogenous_arrivals_enabled(config: OmegaConfig) -> bool:
    return (
        config.exogenous_arrivals is not None
        and config.exogenous_arrivals.enabled
    )


def _choose_exogenous_task_class(
    config: OmegaConfig,
    rng: np.random.Generator,
    tick: int,
) -> str:
    assert config.exogenous_arrivals is not None
    if config.predictive_control is not None and config.attention_policy is not None:
        shares = _a5_demand_shares(config, tick)
    else:
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


def _desired_work_task_class(
    task_queue: deque[Task],
    config: OmegaConfig,
    attention_work_counts: Counter[str],
    tick: int,
) -> str:
    if config.predictive_control is not None:
        return _desired_predictive_attention_class(
            task_queue,
            config,
            attention_work_counts,
            tick,
        )
    return _desired_attention_class(task_queue, config, attention_work_counts)


def _desired_predictive_attention_class(
    task_queue: deque[Task],
    config: OmegaConfig,
    attention_work_counts: Counter[str],
    tick: int,
) -> str:
    assert config.attention_policy is not None
    available_classes = {task.task_class for task in task_queue}
    if not available_classes:
        return ""

    forecast = _a5_forecast_shares(config, tick)
    total_work = sum(attention_work_counts.values())

    def priority(class_name: str) -> tuple[float, int]:
        actual_share = attention_work_counts[class_name] / total_work if total_work else 0.0
        return forecast[class_name] - actual_share, -ATTENTION_CLASSES.index(class_name)

    return max(
        (class_name for class_name in ATTENTION_CLASSES if class_name in available_classes),
        key=priority,
    )


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


def _a5_prediction_charges_work(config: OmegaConfig) -> bool:
    return (
        config.predictive_control is not None
        and config.predictive_control.charge_prediction_to_work
        and config.predictive_control.prediction_budget > 0.0
    )


def _a5_prediction_work_charge_target(config: OmegaConfig, action_opportunity: int) -> float:
    if not _a5_prediction_charges_work(config):
        return 0.0
    assert config.predictive_control is not None
    control = config.predictive_control
    target = max(
        control.prediction_budget * control.prediction_cost_scale * action_opportunity,
        0.0,
    )
    if control.max_prediction_work_fraction_per_tick is not None:
        target = min(
            target,
            action_opportunity * control.max_prediction_work_fraction_per_tick,
        )
    return target


def _a5_demand_shares(config: OmegaConfig, tick: int) -> dict[str, float]:
    assert config.attention_policy is not None
    if config.predictive_control is None:
        return config.attention_policy.shares()

    control = config.predictive_control
    base_shares = config.attention_policy.shares()
    raw: dict[str, float] = {}
    for index, class_name in enumerate(ATTENTION_CLASSES):
        phase = 2.0 * np.pi * ((tick / control.signal_period) + (index / len(ATTENTION_CLASSES)))
        raw[class_name] = max(
            base_shares[class_name] * (1.0 + control.signal_amplitude * float(np.sin(phase))),
            1e-9,
        )
    return _normalize_shares(raw)


def _a5_forecast_shares(config: OmegaConfig, tick: int) -> dict[str, float]:
    assert config.predictive_control is not None
    control = config.predictive_control
    lead_tick = tick + control.lead_ticks

    if control.condition == "oracle":
        return _a5_demand_shares(config, lead_tick)
    if control.condition in {
        "shuffled",
        "nonlinear_shuffled",
        "nonlinear_high_budget_shuffled",
        "spend_only_replay",
    }:
        return _a5_demand_shares(config, tick + control.phase_shift_ticks)
    if control.condition == "reactive":
        return _a5_demand_shares(config, tick)
    if control.condition == "linear":
        return _a5_linear_forecast_shares(config, tick)
    if control.condition == "nonlinear":
        return _a5_nonlinear_forecast_shares(config, tick)
    if control.condition == "nonlinear_high_budget":
        return _a5_high_budget_nonlinear_forecast_shares(config, tick)
    raise ValueError(f"Unsupported predictive_control.condition: {control.condition}")


def _a5_linear_forecast_shares(config: OmegaConfig, tick: int) -> dict[str, float]:
    assert config.predictive_control is not None
    current = _a5_demand_shares(config, tick)
    previous = _a5_demand_shares(config, max(0, tick - 1))
    raw = {
        class_name: current[class_name]
        + config.predictive_control.lead_ticks * (current[class_name] - previous[class_name])
        for class_name in ATTENTION_CLASSES
    }
    return _normalize_shares(raw)


def _a5_nonlinear_forecast_shares(config: OmegaConfig, tick: int) -> dict[str, float]:
    assert config.predictive_control is not None
    current = _a5_demand_shares(config, tick)
    previous = _a5_demand_shares(config, max(0, tick - 1))
    previous_2 = _a5_demand_shares(config, max(0, tick - 2))
    lead = config.predictive_control.lead_ticks
    raw = {}
    for class_name in ATTENTION_CLASSES:
        velocity = current[class_name] - previous[class_name]
        curvature = current[class_name] - 2.0 * previous[class_name] + previous_2[class_name]
        raw[class_name] = current[class_name] + lead * velocity + 0.5 * (lead**2) * curvature
    return _normalize_shares(raw)


def _a5_high_budget_nonlinear_forecast_shares(
    config: OmegaConfig,
    tick: int,
) -> dict[str, float]:
    assert config.predictive_control is not None
    current = _a5_demand_shares(config, tick)
    previous = _a5_demand_shares(config, max(0, tick - 1))
    previous_2 = _a5_demand_shares(config, max(0, tick - 2))
    previous_3 = _a5_demand_shares(config, max(0, tick - 3))
    lead = config.predictive_control.lead_ticks
    raw = {}
    for class_name in ATTENTION_CLASSES:
        velocity = current[class_name] - previous[class_name]
        curvature = current[class_name] - 2.0 * previous[class_name] + previous_2[class_name]
        jerk = (
            current[class_name]
            - 3.0 * previous[class_name]
            + 3.0 * previous_2[class_name]
            - previous_3[class_name]
        )
        raw[class_name] = (
            current[class_name]
            + lead * velocity
            + 0.5 * (lead**2) * curvature
            + (lead**3 / 6.0) * jerk
        )
    return _normalize_shares(raw)


def _normalize_shares(raw: dict[str, float]) -> dict[str, float]:
    clipped = {
        class_name: max(float(raw[class_name]), 1e-9)
        for class_name in ATTENTION_CLASSES
    }
    total = sum(clipped.values())
    return {
        class_name: clipped[class_name] / total
        for class_name in ATTENTION_CLASSES
    }


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


def _predictive_control_metrics(
    *,
    config: OmegaConfig,
    tick: int,
    work_counts_tick: Counter[str],
    action_opportunity: int,
    prediction_work_charge_target_tick: float,
    prediction_work_charged_tick: int,
) -> dict[str, int | float | str]:
    if config.predictive_control is None:
        return {}

    control = config.predictive_control
    demand = _a5_demand_shares(config, tick)
    future_demand = _a5_demand_shares(config, tick + control.lead_ticks)
    forecast = _a5_forecast_shares(config, tick)
    total_work_tick = sum(work_counts_tick.values())
    work_shares = {
        class_name: (
            work_counts_tick[class_name] / total_work_tick
            if total_work_tick
            else 0.0
        )
        for class_name in ATTENTION_CLASSES
    }
    forecast_abs_error = 0.5 * sum(
        abs(forecast[class_name] - future_demand[class_name])
        for class_name in ATTENTION_CLASSES
    )
    forecast_skill = max(0.0, 1.0 - forecast_abs_error)
    forecast_skill_per_budget = (
        forecast_skill / control.prediction_budget
        if control.prediction_budget > 0.0
        else 0.0
    )
    metrics: dict[str, int | float | str] = {
        "a5_predictive_condition": control.condition,
        "a5_prediction_budget": control.prediction_budget,
        "a5_prediction_budget_spent_tick": control.prediction_budget,
        "a5_prediction_cost_scale": control.prediction_cost_scale,
        "a5_max_prediction_work_fraction_per_tick": (
            ""
            if control.max_prediction_work_fraction_per_tick is None
            else control.max_prediction_work_fraction_per_tick
        ),
        "a5_prediction_charged_to_work": str(control.charge_prediction_to_work).lower(),
        "a5_prediction_work_charge_target_tick": round(
            float(prediction_work_charge_target_tick),
            6,
        ),
        "a5_prediction_work_charged_tick": prediction_work_charged_tick,
        "a5_work_opportunity_before_prediction_tick": action_opportunity,
        "a5_work_budget_remaining_tick": max(
            action_opportunity - prediction_work_charged_tick,
            0,
        ),
        "a5_prediction_lead_ticks": control.lead_ticks,
    }
    for class_name in ATTENTION_CLASSES:
        metrics.update(
            {
                f"a5_{class_name}_demand_share_tick": round(demand[class_name], 6),
                f"a5_{class_name}_future_demand_share_tick": round(
                    future_demand[class_name],
                    6,
                ),
                f"a5_{class_name}_forecast_share_tick": round(forecast[class_name], 6),
                f"a5_{class_name}_forecast_error_tick": round(
                    forecast[class_name] - future_demand[class_name],
                    6,
                ),
                f"a5_{class_name}_work_share_tick": round(work_shares[class_name], 6),
                f"a5_{class_name}_allocation_future_residual_tick": round(
                    work_shares[class_name] - future_demand[class_name],
                    6,
                ),
            }
        )
    metrics.update(
        {
            "a5_forecast_abs_error_tick": round(float(forecast_abs_error), 6),
            "a5_forecast_skill_tick": round(float(forecast_skill), 6),
            "a5_forecast_skill_per_budget_tick": round(
                float(forecast_skill_per_budget),
                6,
            ),
            "a5_work_forecast_alignment_tick": round(
                sum(
                    work_shares[class_name] * forecast[class_name]
                    for class_name in ATTENTION_CLASSES
                ),
                6,
            ),
            "a5_work_future_demand_alignment_tick": round(
                sum(
                    work_shares[class_name] * future_demand[class_name]
                    for class_name in ATTENTION_CLASSES
                ),
                6,
            ),
        }
    )
    return metrics


def _a6_stream_rng(
    config: OmegaConfig,
    seed: int,
    stream_name: str,
) -> np.random.Generator | None:
    if config.logistic_appraisal is None:
        return None
    stream_offsets = {
        "baseline_action_stream": 0xA600,
        "appraisal_noise_stream": 0xA601,
        "artifact_update_stream": 0xA602,
        "prediction_noise_stream": 0xA603,
        "control_shuffle_stream": 0xA604,
    }
    return np.random.default_rng(np.random.SeedSequence([seed, stream_offsets[stream_name]]))


def _initial_a6_latent(
    agents: tuple[AgentState, ...],
    config: OmegaConfig,
    rng: np.random.Generator | None,
) -> dict[str, dict[str, float]]:
    if config.logistic_appraisal is None:
        return {}
    assert rng is not None
    latent = {}
    for agent in agents:
        latent[agent.agent_id] = {
            "activation": round(float(rng.uniform(0.36, 0.54)), 6),
            "focus": round(float(rng.uniform(0.42, 0.62)), 6),
            "fatigue": round(float(rng.uniform(0.08, 0.22)), 6),
            "novelty_appetite": round(float(rng.uniform(0.46, 0.72)), 6),
            "risk_sensitivity": round(float(rng.uniform(0.34, 0.62)), 6),
            "handoff_threshold": config.logistic_appraisal.handoff_threshold,
            "prediction_error": 0.0,
        }
    return latent


def _initial_a6_artifact(config: OmegaConfig) -> dict[str, float]:
    if config.logistic_appraisal is None:
        return {}
    return {
        "artifact_novelty": 0.48,
        "artifact_coherence": 0.36,
        "artifact_actionability": 0.34,
        "artifact_provenance_debt": 0.28,
        "artifact_risk": 0.24,
        "artifact_contradiction": 0.30,
        "artifact_readiness": 0.38,
        "artifact_implementation_maturity": 0.28,
        "artifact_communication_maturity": 0.22,
    }


def _advance_a6_background_state(
    *,
    config: OmegaConfig,
    latent: dict[str, dict[str, float]],
    artifact: dict[str, float],
    tick: int,
    appraisal_rng: np.random.Generator | None,
    artifact_rng: np.random.Generator | None,
    shuffle_rng: np.random.Generator | None,
    events: list[dict[str, Any]],
) -> None:
    assert config.logistic_appraisal is not None
    assert appraisal_rng is not None
    assert artifact_rng is not None
    assert shuffle_rng is not None
    appraisal = config.logistic_appraisal
    phase_tick = tick
    if appraisal.condition == "phase_shuffled":
        phase_tick += appraisal.phase_shift_ticks
    phase = np.sin((phase_tick + 1) / 3.0)
    novelty_ambient = 0.018 * phase
    novelty_noise = float(artifact_rng.normal(0.0, appraisal.artifact_noise))
    _apply_a6_artifact_delta(
        artifact=artifact,
        field="artifact_novelty",
        tick=tick,
        source="ambient_artifact_drift",
        agent_id="",
        action="artifact_update",
        events=events,
        ambient_artifact_drift=novelty_ambient,
        noise_effect=novelty_noise,
    )
    _apply_a6_artifact_delta(
        artifact=artifact,
        field="artifact_contradiction",
        tick=tick,
        source="ambient_artifact_drift",
        agent_id="",
        action="artifact_update",
        events=events,
        ambient_artifact_drift=0.012
        * max(0.0, artifact["artifact_novelty"] - artifact["artifact_coherence"]),
    )
    _update_a6_readiness(
        artifact,
        tick=tick,
        source="ambient_artifact_drift",
        agent_id="",
        action="artifact_update",
        events=events,
    )

    for agent_id, state in latent.items():
        noise = float(appraisal_rng.normal(0.0, appraisal.appraisal_noise))
        state["activation"] = _clamp01(
            state["activation"]
            + 0.03 * (artifact["artifact_novelty"] - state["activation"])
            + noise
        )
        state["focus"] = _clamp01(
            state["focus"]
            + 0.025 * (artifact["artifact_readiness"] - state["focus"])
            - 0.015 * state["fatigue"]
        )
        state["fatigue"] = _clamp01(state["fatigue"] * 0.97 + 0.01 * state["activation"])
        target_threshold = appraisal.handoff_threshold
        if appraisal.condition == "threshold_shuffled" and (
            shuffle_rng.random() < appraisal.threshold_shuffle_probability
        ):
            target_threshold = float(shuffle_rng.uniform(0.38, 0.78))
        old_threshold = state["handoff_threshold"]
        state["handoff_threshold"] = _clamp01(
            old_threshold
            + appraisal.adaptive_threshold_rate * (target_threshold - old_threshold)
            + 0.01 * (state["fatigue"] - 0.3)
        )
        events.append(
            _event(
                tick=tick,
                event_type="a6_appraisal_update",
                agent_id=agent_id,
                action="appraisal_update",
            )
        )
        if round(old_threshold, 6) != round(state["handoff_threshold"], 6):
            events.append(
                _event(
                    tick=tick,
                    event_type="a6_threshold_adapted",
                    agent_id=agent_id,
                    action="threshold_adapted",
                )
            )


def _choose_logistic_appraisal_action(
    *,
    config: OmegaConfig,
    has_queued_tasks: bool,
    agent: AgentState,
    rng: np.random.Generator,
    latent: dict[str, float],
    artifact: dict[str, float],
    tick: int,
) -> str:
    assert config.logistic_appraisal is not None
    appraisal = config.logistic_appraisal
    utilities: dict[str, float] = {}
    for action in config.model.actions:
        if action == "work_task" and not has_queued_tasks:
            utilities[action] = -1.0e9
            continue
        signal = _a6_action_signal(action, latent, artifact)
        if appraisal.condition == "phase_shuffled":
            signal = _clamp01(signal + 0.08 * np.sin((tick + appraisal.phase_shift_ticks) / 2.0))
        gate = _a6_appraisal_gate(
            signal=signal,
            threshold=latent["handoff_threshold"],
            condition=appraisal.condition,
            slope=appraisal.sigmoid_slope,
        )
        utilities[action] = (
            _a6_action_base(action, has_queued_tasks)
            + appraisal.appraisal_gain * gate
            + _a6_role_bias(agent.role, action)
            - _a6_fatigue_cost(action, latent["fatigue"])
            - _a6_risk_cost(action, latent, artifact)
            - _a6_prediction_cost(action, appraisal.prediction_budget)
        )
    probabilities = _softmax_probabilities(
        [utilities[action] for action in config.model.actions],
        temperature=appraisal.action_temperature,
    )
    return str(rng.choice(list(config.model.actions), p=probabilities))


def _a6_appraisal_gate(
    *,
    signal: float,
    threshold: float,
    condition: str,
    slope: float,
) -> float:
    if condition == "linear":
        return _clamp01(0.5 + signal - threshold)
    return _sigmoid(slope * (signal - threshold))


def _a6_action_signal(
    action: str,
    latent: dict[str, float],
    artifact: dict[str, float],
) -> float:
    signals = {
        "idle": 0.18 + latent["fatigue"],
        "pause": 0.25 + latent["fatigue"],
        "message": artifact["artifact_communication_maturity"],
        "create_task": 0.5 * artifact["artifact_novelty"] + 0.5 * latent["novelty_appetite"],
        "work_task": artifact["artifact_implementation_maturity"],
        "synthesize": 0.6 * artifact["artifact_novelty"] + 0.4 * latent["focus"],
        "review": artifact["artifact_readiness"],
        "formalize": 0.5 * artifact["artifact_coherence"] + 0.5 * artifact["artifact_actionability"],
        "maintain": max(
            artifact["artifact_provenance_debt"],
            artifact["artifact_contradiction"],
            artifact["artifact_risk"],
            latent["fatigue"],
        ),
        "predict": abs(latent["prediction_error"]) + 0.35 * artifact["artifact_novelty"],
        "communicate": artifact["artifact_communication_maturity"],
    }
    return _clamp01(signals.get(action, 0.0))


def _a6_action_base(action: str, has_queued_tasks: bool) -> float:
    base = {
        "idle": -0.2,
        "pause": -0.25,
        "message": 0.1,
        "create_task": 0.05,
        "work_task": 0.18 if has_queued_tasks else -2.0,
        "synthesize": 0.15,
        "review": 0.1,
        "formalize": 0.05,
        "maintain": 0.0,
        "predict": -0.05,
        "communicate": -0.05,
    }
    return base.get(action, -1.0)


def _a6_role_bias(role: str, action: str) -> float:
    role_bias = {
        ("researcher", "create_task"): 0.18,
        ("researcher", "synthesize"): 0.16,
        ("architect", "synthesize"): 0.18,
        ("architect", "formalize"): 0.14,
        ("implementer", "work_task"): 0.2,
        ("implementer", "formalize"): 0.16,
        ("reviewer", "review"): 0.22,
        ("reviewer", "maintain"): 0.12,
        ("coordinator", "message"): 0.18,
        ("coordinator", "communicate"): 0.2,
        ("coordinator", "predict"): 0.1,
    }
    return role_bias.get((role, action), 0.0)


def _a6_fatigue_cost(action: str, fatigue: float) -> float:
    if action in {"idle", "pause", "maintain"}:
        return 0.0
    return 0.45 * fatigue


def _a6_risk_cost(
    action: str,
    latent: dict[str, float],
    artifact: dict[str, float],
) -> float:
    if action in {"communicate", "formalize", "work_task"}:
        return latent["risk_sensitivity"] * artifact["artifact_risk"]
    return 0.0


def _a6_prediction_cost(action: str, prediction_budget: float) -> float:
    return 0.25 * prediction_budget if action == "predict" else 0.0


def _apply_logistic_appraisal_action(
    *,
    config: OmegaConfig,
    tick: int,
    agent: AgentState,
    action: str,
    latent: dict[str, float],
    artifact: dict[str, float],
    prediction_rng: np.random.Generator | None,
    a6_tick: _A6TickState,
    events: list[dict[str, Any]],
) -> None:
    assert config.logistic_appraisal is not None
    assert prediction_rng is not None
    appraisal = config.logistic_appraisal
    if action == "pause":
        latent["fatigue"] = _clamp01(latent["fatigue"] - 0.04)
        events.append(_event(tick=tick, event_type="agent_idle", agent_id=agent.agent_id, action=action))
        return

    if action == "predict":
        spent = appraisal.prediction_budget / max(config.model.agent_count, 1)
        a6_tick.prediction_budget_spent += spent
        a6_tick.prediction_actions += 1
        prediction_error = float(prediction_rng.normal(0.0, 0.18))
        latent["prediction_error"] = _clamp(prediction_error, -1.0, 1.0)
        latent["fatigue"] = _clamp01(latent["fatigue"] + 0.025 + spent)
        events.append(
            _event(
                tick=tick,
                event_type="a6_prediction_spent",
                agent_id=agent.agent_id,
                action=action,
                work_units=round(float(spent), 6),
            )
        )
        return

    if action in {"synthesize", "review", "formalize", "maintain", "communicate"}:
        a6_tick.handoff_attempts += 1
        events.append(
            _event(
                tick=tick,
                event_type="a6_handoff_attempted",
                agent_id=agent.agent_id,
                action=action,
            )
        )
        success = _a6_handoff_success(action, latent, artifact, appraisal.overload_threshold)
        if success:
            a6_tick.handoff_successes += 1
            _a6_apply_successful_handoff(
                action,
                latent,
                artifact,
                tick=tick,
                agent_id=agent.agent_id,
                events=events,
            )
            event_type = "a6_handoff_succeeded"
        else:
            a6_tick.handoff_failures += 1
            _apply_a6_artifact_delta(
                artifact=artifact,
                field="artifact_contradiction",
                tick=tick,
                source="handoff_failure_effect",
                agent_id=agent.agent_id,
                action=action,
                events=events,
                handoff_failure_effect=0.025,
            )
            _apply_a6_artifact_delta(
                artifact=artifact,
                field="artifact_provenance_debt",
                tick=tick,
                source="handoff_failure_effect",
                agent_id=agent.agent_id,
                action=action,
                events=events,
                handoff_failure_effect=0.02,
            )
            latent["fatigue"] = _clamp01(latent["fatigue"] + 0.02)
            latent["prediction_error"] = _clamp(latent["prediction_error"] + 0.05, -1.0, 1.0)
            event_type = "a6_handoff_failed"
        _update_a6_readiness(
            artifact,
            tick=tick,
            source="handoff_success_effect" if success else "handoff_failure_effect",
            agent_id=agent.agent_id,
            action=action,
            events=events,
        )
        events.append(
            _event(
                tick=tick,
                event_type=event_type,
                agent_id=agent.agent_id,
                action=action,
            )
        )
        return

    events.append(_event(tick=tick, event_type="agent_idle", agent_id=agent.agent_id, action=action))


def _a6_handoff_success(
    action: str,
    latent: dict[str, float],
    artifact: dict[str, float],
    overload_threshold: float,
) -> bool:
    threshold = latent["handoff_threshold"]
    fatigue_ok = latent["fatigue"] < overload_threshold
    gates = {
        "synthesize": artifact["artifact_novelty"] >= threshold and fatigue_ok,
        "review": artifact["artifact_readiness"] >= threshold and fatigue_ok,
        "formalize": (
            artifact["artifact_coherence"] >= threshold
            and artifact["artifact_actionability"] >= threshold
            and artifact["artifact_provenance_debt"] <= overload_threshold
            and fatigue_ok
        ),
        "communicate": (
            artifact["artifact_communication_maturity"] >= threshold
            and artifact["artifact_risk"] <= overload_threshold
            and fatigue_ok
        ),
        "maintain": (
            max(
                artifact["artifact_provenance_debt"],
                artifact["artifact_contradiction"],
                artifact["artifact_risk"],
                latent["fatigue"],
            )
            >= threshold
        ),
    }
    return bool(gates.get(action, False))


def _a6_apply_successful_handoff(
    action: str,
    latent: dict[str, float],
    artifact: dict[str, float],
    *,
    tick: int,
    agent_id: str,
    events: list[dict[str, Any]],
) -> None:
    if action == "synthesize":
        field_deltas = {
            "artifact_coherence": 0.08,
            "artifact_actionability": 0.04,
            "artifact_novelty": -0.03,
        }
    elif action == "review":
        field_deltas = {
            "artifact_risk": -0.05,
            "artifact_contradiction": -0.06,
            "artifact_provenance_debt": -0.04,
        }
    elif action == "formalize":
        field_deltas = {
            "artifact_implementation_maturity": 0.08,
            "artifact_provenance_debt": -0.03,
        }
    elif action == "communicate":
        field_deltas = {
            "artifact_communication_maturity": 0.09,
            "artifact_risk": 0.01,
        }
    elif action == "maintain":
        field_deltas = {
            "artifact_provenance_debt": -0.06,
            "artifact_contradiction": -0.04,
            "artifact_risk": -0.03,
        }
        latent["fatigue"] = _clamp01(latent["fatigue"] - 0.05)
    else:
        field_deltas = {}
    for field, delta in field_deltas.items():
        _apply_a6_artifact_delta(
            artifact=artifact,
            field=field,
            tick=tick,
            source="handoff_success_effect",
            agent_id=agent_id,
            action=action,
            events=events,
            handoff_success_effect=delta,
        )
    latent["fatigue"] = _clamp01(latent["fatigue"] + 0.015)
    latent["prediction_error"] = _clamp(latent["prediction_error"] * 0.85, -1.0, 1.0)


def _apply_a6_artifact_delta(
    *,
    artifact: dict[str, float],
    field: str,
    tick: int,
    source: str,
    agent_id: str,
    action: str,
    events: list[dict[str, Any]],
    ambient_artifact_drift: float = 0.0,
    handoff_attempt_effect: float = 0.0,
    handoff_success_effect: float = 0.0,
    handoff_failure_effect: float = 0.0,
    prediction_expenditure_effect: float = 0.0,
    prediction_error_effect: float = 0.0,
    queue_work_accounting_effect: float = 0.0,
    noise_effect: float = 0.0,
) -> None:
    deltas = {
        "ambient_artifact_drift": round(float(ambient_artifact_drift), 6),
        "handoff_attempt_effect": round(float(handoff_attempt_effect), 6),
        "handoff_success_effect": round(float(handoff_success_effect), 6),
        "handoff_failure_effect": round(float(handoff_failure_effect), 6),
        "prediction_expenditure_effect": round(float(prediction_expenditure_effect), 6),
        "prediction_error_effect": round(float(prediction_error_effect), 6),
        "queue_work_accounting_effect": round(float(queue_work_accounting_effect), 6),
        "noise_effect": round(float(noise_effect), 6),
    }
    unclipped_delta = round(float(sum(deltas.values())), 6)
    before = artifact[field]
    after = _clamp01(before + unclipped_delta)
    total_delta = round(float(after - before), 6)
    clip_residual = round(float(total_delta - unclipped_delta), 6)
    artifact[field] = after
    events.append(
        _event(
            tick=tick,
            event_type="a6_artifact_update",
            agent_id=agent_id,
            action=action,
            a6_artifact_update_source=source,
            a6_artifact_field=field,
            a6_artifact_delta_total=total_delta,
            a6_artifact_delta_ambient=deltas["ambient_artifact_drift"],
            a6_artifact_delta_handoff_attempt=deltas["handoff_attempt_effect"],
            a6_artifact_delta_handoff_success=deltas["handoff_success_effect"],
            a6_artifact_delta_handoff_failure=deltas["handoff_failure_effect"],
            a6_artifact_delta_prediction_expenditure=deltas[
                "prediction_expenditure_effect"
            ],
            a6_artifact_delta_prediction_error=deltas["prediction_error_effect"],
            a6_artifact_delta_queue_work_accounting=deltas[
                "queue_work_accounting_effect"
            ],
            a6_artifact_delta_noise=deltas["noise_effect"],
            a6_artifact_delta_unclipped=unclipped_delta,
            a6_artifact_delta_clip_residual=clip_residual,
        )
    )


def _update_a6_readiness(
    artifact: dict[str, float],
    *,
    tick: int | None = None,
    source: str = "",
    agent_id: str = "",
    action: str = "",
    events: list[dict[str, Any]] | None = None,
) -> None:
    readiness = (
        0.25 * artifact["artifact_novelty"]
        + 0.30 * artifact["artifact_coherence"]
        + 0.25 * artifact["artifact_actionability"]
        - 0.12 * artifact["artifact_provenance_debt"]
        - 0.08 * artifact["artifact_risk"]
    )
    delta = _clamp01(readiness) - artifact["artifact_readiness"]
    if events is None or tick is None or round(float(delta), 6) == 0.0:
        artifact["artifact_readiness"] = _clamp01(readiness)
        return
    source_deltas = {source: delta} if source in _A6_ARTIFACT_DELTA_SOURCE_FIELDS else {}
    _apply_a6_artifact_delta(
        artifact=artifact,
        field="artifact_readiness",
        tick=tick,
        source=source,
        agent_id=agent_id,
        action=action,
        events=events,
        **source_deltas,
    )


def _logistic_appraisal_metrics(
    *,
    config: OmegaConfig,
    latent: dict[str, dict[str, float]],
    artifact: dict[str, float],
    a6_tick: _A6TickState,
    queue_depth: int,
    work_actions: int,
    action_opportunity: int,
) -> dict[str, int | float | str]:
    if config.logistic_appraisal is None:
        return {}
    appraisal = config.logistic_appraisal
    return {
        "a6_condition": appraisal.condition,
        "a6_appraisal_gain": appraisal.appraisal_gain,
        "a6_sigmoid_slope": appraisal.sigmoid_slope,
        "a6_prediction_budget": appraisal.prediction_budget,
        "a6_prediction_budget_available_tick": round(
            float(max(appraisal.prediction_budget - a6_tick.prediction_budget_spent, 0.0)),
            6,
        ),
        "a6_prediction_budget_spent_tick": round(float(a6_tick.prediction_budget_spent), 6),
        "a6_prediction_actions_tick": a6_tick.prediction_actions,
        "a6_prediction_error_mean_tick": _a6_latent_mean(latent, "prediction_error"),
        "a6_latent_activation_mean_tick": _a6_latent_mean(latent, "activation"),
        "a6_latent_focus_mean_tick": _a6_latent_mean(latent, "focus"),
        "a6_latent_fatigue_mean_tick": _a6_latent_mean(latent, "fatigue"),
        "a6_latent_prediction_error_mean_tick": _a6_latent_mean(latent, "prediction_error"),
        "a6_artifact_novelty_tick": round(float(artifact["artifact_novelty"]), 6),
        "a6_artifact_coherence_tick": round(float(artifact["artifact_coherence"]), 6),
        "a6_artifact_actionability_tick": round(float(artifact["artifact_actionability"]), 6),
        "a6_artifact_provenance_debt_tick": round(float(artifact["artifact_provenance_debt"]), 6),
        "a6_artifact_risk_tick": round(float(artifact["artifact_risk"]), 6),
        "a6_artifact_contradiction_tick": round(float(artifact["artifact_contradiction"]), 6),
        "a6_artifact_readiness_tick": round(float(artifact["artifact_readiness"]), 6),
        "a6_artifact_implementation_maturity_tick": round(
            float(artifact["artifact_implementation_maturity"]),
            6,
        ),
        "a6_artifact_communication_maturity_tick": round(
            float(artifact["artifact_communication_maturity"]),
            6,
        ),
        "a6_handoff_attempts_tick": a6_tick.handoff_attempts,
        "a6_handoff_successes_tick": a6_tick.handoff_successes,
        "a6_handoff_failures_tick": a6_tick.handoff_failures,
        "a6_queue_depth_tick": queue_depth,
        "a6_work_actions_tick": work_actions,
        "a6_action_opportunity_tick": action_opportunity,
        "a6_service_capacity_tick": config.model.work_service_capacity,
    }


def _a6_latent_mean(latent: dict[str, dict[str, float]], field: str) -> float:
    if not latent:
        return 0.0
    return round(float(np.mean([state[field] for state in latent.values()])), 6)


def _a7_stream_rng(
    config: OmegaConfig,
    seed: int,
    stream_name: str,
) -> np.random.Generator | None:
    if config.semantic_field is None:
        return None
    stream_offsets = {
        "baseline_action_stream": 0xA700,
        "semantic_update_stream": 0xA701,
        "prediction_noise_stream": 0xA702,
        "semantic_control_shuffle_stream": 0xA703,
    }
    if stream_name not in A7_RNG_STREAMS:
        raise ValueError(f"Unknown A7 RNG stream: {stream_name}")
    return np.random.default_rng(np.random.SeedSequence([seed, stream_offsets[stream_name]]))


def _initial_a7_field(config: OmegaConfig) -> dict[str, float]:
    if config.semantic_field is None:
        return {}
    return {
        "semantic_novelty": 0.46,
        "semantic_coherence": 0.42,
        "semantic_contradiction": 0.26,
        "semantic_risk": 0.24,
        "artifact_readiness": 0.34,
        "trust_weighted_salience": 0.38,
        "prediction_budget_spent": 0.0,
        "prediction_error": 0.0,
    }


def _initial_a7_agent_state(
    agents: tuple[AgentState, ...],
    config: OmegaConfig,
    rng: np.random.Generator | None,
) -> dict[str, dict[str, float]]:
    if config.semantic_field is None:
        return {}
    assert rng is not None
    return {
        agent.agent_id: {
            "threshold": round(float(rng.uniform(0.44, 0.58)), 6),
            "fatigue": round(float(rng.uniform(0.08, 0.2)), 6),
            "prediction_error": 0.0,
        }
        for agent in agents
    }


def _advance_a7_background_state(
    *,
    config: OmegaConfig,
    field: dict[str, float],
    tick: int,
    update_rng: np.random.Generator | None,
    shuffle_rng: np.random.Generator | None,
    queue_depth: int,
    events: list[dict[str, Any]],
) -> None:
    assert config.semantic_field is not None
    assert update_rng is not None
    assert shuffle_rng is not None
    semantic = config.semantic_field
    phase_tick = tick + (
        semantic.phase_shift_ticks
        if semantic.condition == "semantic_field_phase_shuffle"
        else 0
    )
    phase = float(np.sin((phase_tick + 1) / 3.0))
    queue_pressure = min(queue_depth / 12.0, 1.0)
    for field_name in A7_FIELD_VALUES:
        ambient_decay = round(
            float((semantic.semantic_decay - 1.0) * field[field_name]),
            6,
        )
        if semantic.condition == "semantic_off_baseline":
            semantic_noise = 0.0
            queue_work_accounting = 0.0
        else:
            semantic_noise = round(
                float(update_rng.normal(0.0, semantic.semantic_noise)),
                6,
            )
            queue_work_accounting = round(
                float(_a7_queue_delta(field_name, queue_pressure, phase)),
                6,
            )
        if semantic.condition == "source_preserving_semantic_label_shuffle":
            field_name = str(shuffle_rng.choice(list(A7_FIELD_VALUES)))
        _apply_a7_field_delta(
            field=field,
            field_name=field_name,
            tick=tick,
            agent_id="",
            action="semantic_background",
            events=events,
            condition=semantic.condition,
            ambient_decay=ambient_decay,
            queue_work_accounting=queue_work_accounting,
            semantic_noise=semantic_noise,
        )


def _a7_queue_delta(field_name: str, queue_pressure: float, phase: float) -> float:
    weights = {
        "semantic_novelty": 0.016 * phase,
        "semantic_coherence": 0.010 * (1.0 - queue_pressure),
        "semantic_contradiction": 0.018 * queue_pressure,
        "semantic_risk": 0.014 * queue_pressure,
        "artifact_readiness": 0.010 * (0.5 - queue_pressure),
        "trust_weighted_salience": 0.012 * (1.0 - abs(phase)),
    }
    return weights.get(field_name, 0.0)


def _choose_semantic_field_action(
    *,
    config: OmegaConfig,
    has_queued_tasks: bool,
    agent: AgentState,
    rng: np.random.Generator,
    agent_state: dict[str, float],
    field: dict[str, float],
    tick: int,
) -> str:
    assert config.semantic_field is not None
    semantic = config.semantic_field
    utilities: dict[str, float] = {}
    for action in config.model.actions:
        if action == "work_task" and not has_queued_tasks:
            utilities[action] = -1.0e9
            continue
        signal = _a7_action_signal(action, field)
        if semantic.condition == "semantic_field_phase_shuffle":
            signal = _clamp01(signal + 0.05 * np.sin((tick + semantic.phase_shift_ticks) / 2.0))
        if semantic.condition == "amplitude_matched_linear_semantic_coupling":
            gate = _clamp01(0.5 + semantic.linear_gain * (signal - agent_state["threshold"]))
        else:
            gate = _sigmoid(semantic.logistic_beta * (signal - agent_state["threshold"]))
        if semantic.condition == "semantic_off_baseline":
            gate = 0.0
        utilities[action] = (
            _a6_action_base(action, has_queued_tasks)
            + gate
            + _a6_role_bias(agent.role, action)
            - _a7_fatigue_cost(action, agent_state["fatigue"])
            - _a7_prediction_cost(action, semantic.prediction_budget_per_tick)
        )
    probabilities = _softmax_probabilities(
        [utilities[action] for action in config.model.actions],
        temperature=1.0,
    )
    return str(rng.choice(list(config.model.actions), p=probabilities))


def _a7_action_signal(action: str, field: dict[str, float]) -> float:
    signals = {
        "idle": 0.18,
        "pause": 0.25 + field["semantic_risk"],
        "message": field["trust_weighted_salience"],
        "create_task": field["semantic_novelty"],
        "work_task": field["artifact_readiness"],
        "synthesize": 0.65 * field["semantic_novelty"] + 0.35 * field["semantic_coherence"],
        "review": 0.5 * field["semantic_contradiction"] + 0.5 * field["semantic_risk"],
        "formalize": 0.55 * field["semantic_coherence"] + 0.45 * field["artifact_readiness"],
        "maintain": max(field["semantic_contradiction"], field["semantic_risk"]),
        "predict": abs(field["prediction_error"]) + 0.35 * field["semantic_novelty"],
        "communicate": field["trust_weighted_salience"],
    }
    return _clamp01(signals.get(action, 0.0))


def _a7_fatigue_cost(action: str, fatigue: float) -> float:
    if action in {"idle", "pause"}:
        return 0.0
    return 0.35 * fatigue


def _a7_prediction_cost(action: str, prediction_budget_per_tick: float) -> float:
    return 0.2 * prediction_budget_per_tick if action == "predict" else 0.0


def _apply_semantic_field_action(
    *,
    config: OmegaConfig,
    tick: int,
    agent: AgentState,
    action: str,
    agent_state: dict[str, float],
    field: dict[str, float],
    prediction_rng: np.random.Generator | None,
    a7_tick: _A7TickState,
    events: list[dict[str, Any]],
) -> None:
    assert config.semantic_field is not None
    assert prediction_rng is not None
    semantic = config.semantic_field
    signal = _a7_action_signal(action, field)
    if abs(signal - agent_state["threshold"]) <= 0.08:
        a7_tick.near_threshold_count += 1
    if action == "pause":
        agent_state["fatigue"] = _clamp01(agent_state["fatigue"] - 0.04)
        events.append(_event(tick=tick, event_type="agent_idle", agent_id=agent.agent_id, action=action))
        return
    if action == "predict":
        spent = semantic.prediction_budget_per_tick / max(config.model.agent_count, 1)
        error_mean = 0.0
        if semantic.condition == "prediction_budget_timing_broken_matched_count_null":
            error_mean = 0.08
        prediction_error = _clamp(float(prediction_rng.normal(error_mean, 0.16)), -1.0, 1.0)
        agent_state["prediction_error"] = prediction_error
        agent_state["fatigue"] = _clamp01(agent_state["fatigue"] + 0.02 + spent)
        a7_tick.prediction_budget_spent += spent
        a7_tick.prediction_error_sum += abs(prediction_error)
        a7_tick.prediction_actions += 1
        _apply_a7_field_delta(
            field=field,
            field_name="prediction_budget_spent",
            tick=tick,
            agent_id=agent.agent_id,
            action=action,
            events=events,
            condition=semantic.condition,
            prediction_expenditure=spent,
        )
        _apply_a7_field_delta(
            field=field,
            field_name="prediction_error",
            tick=tick,
            agent_id=agent.agent_id,
            action=action,
            events=events,
            condition=semantic.condition,
            prediction_error=prediction_error,
        )
        return
    if action == "work_task":
        a7_tick.work_actions += 1
        agent_state["fatigue"] = _clamp01(agent_state["fatigue"] + 0.012)
        return
    if action in {"synthesize", "review", "formalize", "maintain", "communicate"}:
        a7_tick.handoff_attempts += 1
        success = signal >= agent_state["threshold"] and agent_state["fatigue"] < 0.82
        if success:
            a7_tick.handoff_successes += 1
            deltas = _a7_success_deltas(action)
        else:
            a7_tick.handoff_failures += 1
            deltas = {
                "semantic_contradiction": 0.025,
                "semantic_risk": 0.018,
                "artifact_readiness": -0.012,
            }
        for field_name, delta in deltas.items():
            _apply_a7_field_delta(
                field=field,
                field_name=field_name,
                tick=tick,
                agent_id=agent.agent_id,
                action=action,
                events=events,
                condition=semantic.condition,
                artifact_handoff=delta,
                peer_contribution=0.004 if success else 0.0,
            )
        agent_state["fatigue"] = _clamp01(agent_state["fatigue"] + (0.014 if success else 0.022))
    agent_state["threshold"] = _clamp01(
        agent_state["threshold"]
        + semantic.threshold_adaptation_rate * abs(agent_state["prediction_error"])
        - (0.01 if action in {"idle", "pause"} else 0.0)
    )


def _a7_success_deltas(action: str) -> dict[str, float]:
    if action == "synthesize":
        return {
            "semantic_coherence": 0.045,
            "artifact_readiness": 0.025,
            "semantic_novelty": -0.018,
        }
    if action == "review":
        return {
            "semantic_contradiction": -0.038,
            "semantic_risk": -0.025,
            "trust_weighted_salience": 0.018,
        }
    if action == "formalize":
        return {
            "artifact_readiness": 0.052,
            "semantic_coherence": 0.024,
        }
    if action == "communicate":
        return {
            "trust_weighted_salience": 0.05,
            "semantic_risk": 0.006,
        }
    if action == "maintain":
        return {
            "semantic_contradiction": -0.032,
            "semantic_risk": -0.024,
        }
    return {}


def _apply_a7_field_delta(
    *,
    field: dict[str, float],
    field_name: str,
    tick: int,
    agent_id: str,
    action: str,
    events: list[dict[str, Any]],
    condition: str = "",
    ambient_decay: float = 0.0,
    self_contribution: float = 0.0,
    peer_contribution: float = 0.0,
    artifact_handoff: float = 0.0,
    prediction_expenditure: float = 0.0,
    prediction_error: float = 0.0,
    queue_work_accounting: float = 0.0,
    semantic_noise: float = 0.0,
) -> None:
    deltas = {
        "ambient_decay": round(float(ambient_decay), 6),
        "self_contribution": round(float(self_contribution), 6),
        "peer_contribution": round(float(peer_contribution), 6),
        "artifact_handoff": round(float(artifact_handoff), 6),
        "prediction_expenditure": round(float(prediction_expenditure), 6),
        "prediction_error": round(float(prediction_error), 6),
        "queue_work_accounting": round(float(queue_work_accounting), 6),
        "semantic_noise": round(float(semantic_noise), 6),
    }
    before = field[field_name]
    unclipped_delta = round(float(sum(deltas.values())), 6)
    after = _clamp01(before + unclipped_delta)
    total_delta = round(float(after - before), 6)
    clip_residual = round(float(total_delta - unclipped_delta), 6)
    field[field_name] = after
    source_fields = {
        f"a7_delta_{source}": deltas.get(source, clip_residual)
        for source in A7_SOURCE_COMPONENTS
    }
    source_fields["a7_delta_clip_residual"] = clip_residual
    events.append(
        _event(
            tick=tick,
            event_type="a7_semantic_field_update",
            agent_id=agent_id,
            action=action,
            a7_condition=condition,
            a7_semantic_field=field_name,
            a7_delta_total=total_delta,
            **source_fields,
        )
    )


def _semantic_field_metrics(
    *,
    config: OmegaConfig,
    agent_state: dict[str, dict[str, float]],
    field: dict[str, float],
    a7_tick: _A7TickState,
    queue_depth: int,
    queue_delta: int,
    tasks_created_total: int,
    tasks_completed_total: int,
    action_opportunity: int,
) -> dict[str, int | float | str]:
    if config.semantic_field is None:
        return {}
    semantic = config.semantic_field
    prediction_error_mean = (
        a7_tick.prediction_error_sum / a7_tick.prediction_actions
        if a7_tick.prediction_actions
        else abs(field["prediction_error"])
    )
    metrics: dict[str, int | float | str] = {
        "a7_condition": semantic.condition,
        "a7_prediction_budget_per_tick": semantic.prediction_budget_per_tick,
        "a7_lead_ticks": semantic.lead_ticks,
        "a7_semantic_decay": semantic.semantic_decay,
        "a7_logistic_beta": semantic.logistic_beta,
        "a7_linear_gain": semantic.linear_gain,
        "a7_threshold_adaptation_rate": semantic.threshold_adaptation_rate,
        "a7_semantic_noise": semantic.semantic_noise,
        "a7_service_capacity_tick": config.model.work_service_capacity,
        "a7_action_opportunity_tick": action_opportunity,
        "a7_work_budget_tick": round(
            float(max(action_opportunity - a7_tick.prediction_actions, 0)),
            6,
        ),
        "a7_work_actions_tick": a7_tick.work_actions,
        "a7_prediction_actions_tick": a7_tick.prediction_actions,
        "a7_handoff_attempts_tick": a7_tick.handoff_attempts,
        "a7_handoff_successes_tick": a7_tick.handoff_successes,
        "a7_handoff_failures_tick": a7_tick.handoff_failures,
        "a7_threshold_mean_tick": _a7_agent_mean(agent_state, "threshold"),
        "a7_fatigue_mean_tick": _a7_agent_mean(agent_state, "fatigue"),
        "a7_near_threshold_occupancy_tick": round(
            float(a7_tick.near_threshold_count / max(action_opportunity, 1)),
            6,
        ),
    }
    control_values = {
        "queue_depth": queue_depth,
        "queue_delta_tick": queue_delta,
        "tasks_created_total": tasks_created_total,
        "tasks_completed_total": tasks_completed_total,
    }
    metrics.update(control_values)
    for field_name in A7_FIELD_VALUES:
        metrics[f"a7_{field_name}_tick"] = round(float(field[field_name]), 6)
        metrics[f"a7_{field_name}_mean_tick"] = round(float(field[field_name]), 6)
    metrics["a7_prediction_budget_spent_tick"] = round(
        float(a7_tick.prediction_budget_spent),
        6,
    )
    metrics["a7_prediction_budget_spent_mean_tick"] = round(
        float(a7_tick.prediction_budget_spent / max(action_opportunity, 1)),
        6,
    )
    metrics["a7_prediction_error_tick"] = round(float(field["prediction_error"]), 6)
    metrics["a7_prediction_error_mean_tick"] = round(float(prediction_error_mean), 6)
    return metrics


def _a7_agent_mean(agent_state: dict[str, dict[str, float]], field: str) -> float:
    if not agent_state:
        return 0.0
    return round(float(np.mean([state[field] for state in agent_state.values()])), 6)


def _a7_2_stream_rng(
    config: OmegaConfig,
    seed: int,
    stream_name: str,
) -> np.random.Generator | None:
    if config.a7_2_delayed_prediction is None:
        return None
    stream_offsets = {
        "action": 0xA720,
        "prediction": 0xA721,
        "shuffle": 0xA722,
    }
    return np.random.default_rng(np.random.SeedSequence([seed, stream_offsets[stream_name]]))


def _initial_a7_2_agent_state(
    agents: tuple[AgentState, ...],
    config: OmegaConfig,
) -> dict[str, dict[str, float]]:
    if config.a7_2_delayed_prediction is None:
        return {}
    return {
        agent.agent_id: {
            "fatigue": 0.10,
            "adaptive_prediction_threshold": 0.15,
            "adaptive_work_threshold": 0.05,
            "adaptive_review_threshold": 0.10,
            "adaptive_synthesis_threshold": 0.12,
        }
        for agent in agents
    }


def _initial_a7_2_artifact(config: OmegaConfig) -> dict[str, float]:
    if config.a7_2_delayed_prediction is None:
        return {}
    return {
        "forecast_error_lag1": 0.25,
        "forecast_uncertainty_lag1": 0.20,
        "artifact_readiness": 0.30,
        "artifact_coherence": 0.35,
        "artifact_contradiction": 0.25,
        "artifact_risk": 0.22,
        "artifact_revision_pressure": 0.17,
    }


def _advance_a7_2_delayed_state(
    *,
    config: OmegaConfig,
    artifact: dict[str, float],
    forecast_updates: deque[dict[str, float | int]],
    artifact_updates: deque[dict[str, float | int]],
    tick: int,
    events: list[dict[str, Any]],
    tick_state: _A7_2TickState,
) -> None:
    assert config.a7_2_delayed_prediction is not None
    cfg = config.a7_2_delayed_prediction
    visible_forecast_error = 0.0
    visible_uncertainty = 0.0
    while forecast_updates and int(forecast_updates[0]["visible_tick"]) <= tick:
        update = forecast_updates.popleft()
        visible_forecast_error += float(update["forecast_error_delta"])
        visible_uncertainty += float(update["forecast_uncertainty_delta"])
    if visible_forecast_error or visible_uncertainty:
        artifact["forecast_error_lag1"] = _a7_2_clip(
            config,
            artifact["forecast_error_lag1"] + visible_forecast_error,
        )
        artifact["forecast_uncertainty_lag1"] = _a7_2_clip(
            config,
            artifact["forecast_uncertainty_lag1"] + visible_uncertainty,
        )
        tick_state.source_ledger_forecast_error += visible_forecast_error
    source = {
        "readiness": 0.0,
        "coherence": 0.0,
        "contradiction": 0.0,
        "risk": 0.0,
    }
    while artifact_updates and int(artifact_updates[0]["visible_tick"]) <= tick:
        update = artifact_updates.popleft()
        for key in source:
            source[key] += float(update.get(key, 0.0))
    if any(source.values()) or config.a7_2_delayed_prediction.condition != "zero_budget_reactive":
        if cfg.condition == "artifact_off_source_ledger_null":
            source = {key: 0.0 for key in source}
        before = dict(artifact)
        artifact["artifact_readiness"] = _a7_2_clip(
            config,
            (1.0 - cfg.artifact_decay) * artifact["artifact_readiness"]
            + source["readiness"]
            - max(source["contradiction"], 0.0) * 0.25,
        )
        artifact["artifact_coherence"] = _a7_2_clip(
            config,
            (1.0 - cfg.artifact_decay) * artifact["artifact_coherence"] + source["coherence"]
        )
        artifact["artifact_contradiction"] = _a7_2_clip(
            config,
            (1.0 - cfg.artifact_decay) * artifact["artifact_contradiction"]
            + source["contradiction"]
            + max(visible_forecast_error, 0.0) * 0.2,
        )
        artifact["artifact_risk"] = _a7_2_clip(
            config,
            (1.0 - cfg.artifact_decay) * artifact["artifact_risk"] + source["risk"]
        )
        artifact["artifact_revision_pressure"] = _a7_2_clip(
            config,
            artifact["artifact_contradiction"]
            + artifact["artifact_risk"]
            - artifact["artifact_readiness"],
        )
        deltas = {
            "source_ledger_artifact_readiness_delta": artifact["artifact_readiness"]
            - before["artifact_readiness"],
            "source_ledger_artifact_coherence_delta": artifact["artifact_coherence"]
            - before["artifact_coherence"],
            "source_ledger_artifact_contradiction_delta": artifact["artifact_contradiction"]
            - before["artifact_contradiction"],
            "source_ledger_artifact_risk_delta": artifact["artifact_risk"] - before["artifact_risk"],
        }
        tick_state.source_ledger_artifact += sum(abs(value) for value in deltas.values())
        events.append(
            _event(
                tick=tick,
                event_type="a7_2_delayed_artifact_update",
                agent_id="",
                action="delayed_update",
                a7_2_condition=cfg.condition,
                selected_action="delayed_update",
                source_ledger_forecast_error=round(visible_forecast_error, 6),
                source_ledger_artifact=round(tick_state.source_ledger_artifact, 6),
                source_ledger_queue_accounting=0.0,
                **{key: round(float(value), 6) for key, value in deltas.items()},
            )
        )


def _choose_a7_2_action(
    *,
    config: OmegaConfig,
    has_queued_tasks: bool,
    agent: AgentState,
    rng: np.random.Generator,
    agent_state: dict[str, float],
    artifact: dict[str, float],
    queue_depth: int,
    tick: int,
    tick_state: _A7_2TickState,
) -> str:
    assert config.a7_2_delayed_prediction is not None
    cfg = config.a7_2_delayed_prediction
    utilities = _a7_2_utilities(config, agent_state, artifact, queue_depth, tick)
    if not has_queued_tasks:
        utilities["work"] = 0.0
    if cfg.condition == "zero_budget_reactive":
        utilities["predict"] = 0.0
        utilities["review"] *= 0.25
        utilities["synthesize"] *= 0.25
    if cfg.condition == "high_budget_oracle_smoothing":
        utilities["predict"] *= 1.5
    if cfg.condition == "threshold_shuffled":
        utilities = {
            action: utilities[action]
            for action in ("work", "predict", "synthesize", "review")
        }
    if cfg.condition == "source_preserving_artifact_label_shuffle":
        utilities["review"], utilities["synthesize"] = utilities["synthesize"], utilities["review"]
    total = sum(max(value, 0.0) for value in utilities.values())
    if total <= 0.0:
        selected = "work" if has_queued_tasks else "synthesize"
    else:
        probabilities = [max(utilities[action], 0.0) / total for action in A7_2_ACTIONS]
        selected = str(rng.choice(list(A7_2_ACTIONS), p=probabilities))
    assert tick_state.selected_actions is not None
    assert tick_state.utilities is not None
    tick_state.selected_actions[selected] += 1
    for action, utility in utilities.items():
        tick_state.utilities[action] = tick_state.utilities.get(action, 0.0) + utility
    if selected == "work":
        return "work_task"
    return selected


def _a7_2_utilities(
    config: OmegaConfig,
    agent_state: dict[str, float],
    artifact: dict[str, float],
    queue_depth: int,
    tick: int,
) -> dict[str, float]:
    assert config.a7_2_delayed_prediction is not None
    cfg = config.a7_2_delayed_prediction
    forecast_error = artifact["forecast_error_lag1"]
    uncertainty = artifact["forecast_uncertainty_lag1"]
    revision_pressure = artifact["artifact_revision_pressure"]
    readiness = artifact["artifact_readiness"]
    coherence = artifact["artifact_coherence"]
    contradiction = artifact["artifact_contradiction"]
    risk = artifact["artifact_risk"]
    if cfg.condition == "same_tick_logistic_prediction":
        forecast_error = _a7_2_clip(config, forecast_error + 0.02 * np.sin(tick + 1))
    if cfg.condition == "phase_shuffled_lag_input":
        forecast_error = _a7_2_clip(config, forecast_error + 0.05 * np.sin((tick + 5) / 2.0))
    backlog_pressure = min(queue_depth / 12.0, 1.0)
    fatigue = agent_state["fatigue"]
    if cfg.condition == "amplitude_matched_linear_delayed_prediction":
        gate = lambda value: _clamp01(0.5 + 0.5 * value)
    else:
        gate = _sigmoid
    return {
        "predict": cfg.utility_slope_predict
        * gate(
            forecast_error
            + uncertainty
            + revision_pressure
            - agent_state["adaptive_prediction_threshold"]
            - fatigue
        ),
        "work": cfg.utility_slope_work
        * gate(backlog_pressure + readiness - agent_state["adaptive_work_threshold"] - fatigue),
        "review": cfg.utility_slope_review
        * gate(contradiction + risk - agent_state["adaptive_review_threshold"] - fatigue),
        "synthesize": cfg.utility_slope_synthesize
        * gate(
            readiness
            + coherence
            - contradiction
            - agent_state["adaptive_synthesis_threshold"]
            - fatigue
        ),
    }


def _apply_a7_2_action(
    *,
    config: OmegaConfig,
    tick: int,
    agent: AgentState,
    action: str,
    agent_state: dict[str, float],
    artifact: dict[str, float],
    forecast_updates: deque[dict[str, float | int]],
    artifact_updates: deque[dict[str, float | int]],
    prediction_rng: np.random.Generator | None,
    shuffle_rng: np.random.Generator | None,
    tick_state: _A7_2TickState,
    events: list[dict[str, Any]],
) -> None:
    assert config.a7_2_delayed_prediction is not None
    assert prediction_rng is not None
    cfg = config.a7_2_delayed_prediction
    if action == "predict":
        spend = 1.0 / max(config.model.agent_count, 1)
        work_cost = min(
            cfg.prediction_cost_work_fraction * spend,
            cfg.max_prediction_work_fraction_per_tick,
        )
        tick_state.prediction_spend += spend
        tick_state.lost_work_opportunity += work_cost
        if cfg.condition == "spend_only_replay":
            forecast_delta = 0.0
            uncertainty_delta = 0.0
        else:
            forecast_delta = -abs(float(prediction_rng.normal(0.035, 0.01)))
            uncertainty_delta = -abs(float(prediction_rng.normal(0.018, 0.006)))
        forecast_updates.append(
            {
                "visible_tick": tick + cfg.forecast_delay_ticks,
                "forecast_error_delta": forecast_delta,
                "forecast_uncertainty_delta": uncertainty_delta,
            }
        )
        agent_state["fatigue"] = _a7_2_clip(
            config,
            agent_state["fatigue"] + cfg.fatigue_increment_predict,
        )
        _adapt_a7_2_thresholds(config, agent_state, "adaptive_prediction_threshold")
        events.append(
            _event(
                tick=tick,
                event_type="a7_2_action_selected",
                agent_id=agent.agent_id,
                action=action,
                a7_2_condition=cfg.condition,
                selected_action=action,
                forecast_update_created_tick=tick,
                forecast_update_visible_tick=tick + cfg.forecast_delay_ticks,
                prediction_work_cost=round(work_cost, 6),
                source_ledger_forecast_error=round(forecast_delta, 6),
            )
        )
        return
    if action in {"review", "synthesize"}:
        _apply_a7_2_artifact_action(
            config=config,
            tick=tick,
            agent=agent,
            action=action,
            agent_state=agent_state,
            artifact=artifact,
            artifact_updates=artifact_updates,
            shuffle_rng=shuffle_rng,
            tick_state=tick_state,
            events=events,
        )


def _apply_a7_2_work_action(
    *,
    config: OmegaConfig,
    tick: int,
    agent: AgentState,
    agent_state: dict[str, float],
    artifact: dict[str, float],
    tick_state: _A7_2TickState,
    events: list[dict[str, Any]],
) -> None:
    assert config.a7_2_delayed_prediction is not None
    cfg = config.a7_2_delayed_prediction
    agent_state["fatigue"] = _a7_2_clip(config, agent_state["fatigue"] + cfg.fatigue_increment_work)
    _adapt_a7_2_thresholds(config, agent_state, "adaptive_work_threshold")
    tick_state.source_ledger_queue_accounting += 1.0
    events.append(
        _event(
            tick=tick,
            event_type="a7_2_action_selected",
            agent_id=agent.agent_id,
            action="work",
            a7_2_condition=cfg.condition,
            selected_action="work",
            source_ledger_queue_accounting=1.0,
        )
    )


def _apply_a7_2_artifact_action(
    *,
    config: OmegaConfig,
    tick: int,
    agent: AgentState,
    action: str,
    agent_state: dict[str, float],
    artifact: dict[str, float],
    artifact_updates: deque[dict[str, float | int]],
    shuffle_rng: np.random.Generator | None,
    tick_state: _A7_2TickState,
    events: list[dict[str, Any]],
) -> None:
    assert config.a7_2_delayed_prediction is not None
    cfg = config.a7_2_delayed_prediction
    if action == "review":
        update = {
            "readiness": 0.012,
            "coherence": 0.006,
            "contradiction": 0.025,
            "risk": -0.012,
        }
        fatigue_increment = cfg.fatigue_increment_review
        threshold = "adaptive_review_threshold"
    else:
        update = {
            "readiness": 0.030,
            "coherence": 0.026,
            "contradiction": -0.020,
            "risk": -0.008,
        }
        fatigue_increment = cfg.fatigue_increment_synthesize
        threshold = "adaptive_synthesis_threshold"
    if cfg.condition == "source_preserving_artifact_label_shuffle" and shuffle_rng is not None:
        values = list(update.values())
        shuffled_keys = list(update)
        shuffle_rng.shuffle(shuffled_keys)
        update = dict(zip(shuffled_keys, values))
    if cfg.condition == "artifact_off_source_ledger_null":
        update = {key: 0.0 for key in update}
    artifact_updates.append(
        {
            "visible_tick": tick + cfg.artifact_delay_ticks,
            **update,
        }
    )
    agent_state["fatigue"] = _a7_2_clip(config, agent_state["fatigue"] + fatigue_increment)
    _adapt_a7_2_thresholds(config, agent_state, threshold)
    tick_state.source_ledger_artifact += sum(abs(value) for value in update.values())
    events.append(
        _event(
            tick=tick,
            event_type="a7_2_action_selected",
            agent_id=agent.agent_id,
            action=action,
            a7_2_condition=cfg.condition,
            selected_action=action,
            artifact_update_created_tick=tick,
            artifact_update_visible_tick=tick + cfg.artifact_delay_ticks,
            source_ledger_artifact=round(sum(abs(value) for value in update.values()), 6),
            source_ledger_artifact_readiness_delta=round(update["readiness"], 6),
            source_ledger_artifact_coherence_delta=round(update["coherence"], 6),
            source_ledger_artifact_contradiction_delta=round(update["contradiction"], 6),
            source_ledger_artifact_risk_delta=round(update["risk"], 6),
        )
    )


def _adapt_a7_2_thresholds(
    config: OmegaConfig,
    agent_state: dict[str, float],
    active_threshold: str,
) -> None:
    assert config.a7_2_delayed_prediction is not None
    cfg = config.a7_2_delayed_prediction
    for key in (
        "adaptive_prediction_threshold",
        "adaptive_work_threshold",
        "adaptive_review_threshold",
        "adaptive_synthesis_threshold",
    ):
        delta = cfg.threshold_learning_rate_error if key == active_threshold else -cfg.threshold_recovery_rate
        agent_state[key] = _clamp(
            agent_state[key] + delta,
            cfg.threshold_min,
            cfg.threshold_max,
        )
    agent_state["fatigue"] = _a7_2_clip(
        config,
        agent_state["fatigue"] * (1.0 - cfg.fatigue_decay),
    )


def _a7_2_delayed_prediction_metrics(
    *,
    config: OmegaConfig,
    agent_state: dict[str, dict[str, float]],
    artifact: dict[str, float],
    tick_state: _A7_2TickState,
    forecast_queue_length: int,
    artifact_queue_length: int,
    tick: int,
    queue_depth: int,
    queue_age_metrics: dict[str, float],
    completed_this_tick: int,
    completed_total: int,
    task_arrivals: int,
    action_opportunity: int,
    work_actions: int,
) -> dict[str, int | float | str]:
    if config.a7_2_delayed_prediction is None:
        return {}
    cfg = config.a7_2_delayed_prediction
    selected_actions = tick_state.selected_actions or Counter()
    utilities = tick_state.utilities or {}
    remaining_work_budget = max(action_opportunity - tick_state.lost_work_opportunity, 0.0)
    completion_fraction = completed_this_tick / max(action_opportunity, 1)
    selected_action = selected_actions.most_common(1)[0][0] if selected_actions else ""
    metrics: dict[str, int | float | str] = {
        "a7_2_forecast_error_lag1": round(artifact["forecast_error_lag1"], 6),
        "a7_2_forecast_uncertainty_lag1": round(artifact["forecast_uncertainty_lag1"], 6),
        "a7_2_prediction_spend": round(tick_state.prediction_spend, 6),
        "a7_2_lost_work_opportunity_from_prediction": round(
            tick_state.lost_work_opportunity,
            6,
        ),
        "a7_2_fatigue": _a7_agent_mean(agent_state, "fatigue"),
        "a7_2_adaptive_prediction_threshold": _a7_agent_mean(
            agent_state,
            "adaptive_prediction_threshold",
        ),
        "a7_2_adaptive_work_threshold": _a7_agent_mean(
            agent_state,
            "adaptive_work_threshold",
        ),
        "a7_2_adaptive_review_threshold": _a7_agent_mean(
            agent_state,
            "adaptive_review_threshold",
        ),
        "a7_2_adaptive_synthesis_threshold": _a7_agent_mean(
            agent_state,
            "adaptive_synthesis_threshold",
        ),
        "a7_2_artifact_readiness": round(artifact["artifact_readiness"], 6),
        "a7_2_artifact_coherence": round(artifact["artifact_coherence"], 6),
        "a7_2_artifact_contradiction": round(artifact["artifact_contradiction"], 6),
        "a7_2_artifact_risk": round(artifact["artifact_risk"], 6),
        "a7_2_artifact_revision_pressure": round(
            artifact["artifact_revision_pressure"],
            6,
        ),
        "a7_2_selected_action": selected_action,
        "a7_2_predict_utility": round(utilities.get("predict", 0.0) / max(action_opportunity, 1), 6),
        "a7_2_work_utility": round(utilities.get("work", 0.0) / max(action_opportunity, 1), 6),
        "a7_2_review_utility": round(utilities.get("review", 0.0) / max(action_opportunity, 1), 6),
        "a7_2_synthesize_utility": round(
            utilities.get("synthesize", 0.0) / max(action_opportunity, 1),
            6,
        ),
        "a7_2_delayed_forecast_update_queue": forecast_queue_length,
        "a7_2_delayed_artifact_update_queue": artifact_queue_length,
        "a7_2_source_ledger_forecast_error": round(tick_state.source_ledger_forecast_error, 6),
        "a7_2_source_ledger_artifact": round(tick_state.source_ledger_artifact, 6),
        "a7_2_source_ledger_queue_accounting": round(
            tick_state.source_ledger_queue_accounting,
            6,
        ),
        "tick": tick,
        "demand_phase": round(float(np.sin((tick + 1) / 3.0)), 6),
        "task_arrivals": task_arrivals,
        "service_capacity": config.model.work_service_capacity,
        "action_opportunity": action_opportunity,
        "work_budget": action_opportunity,
        "prediction_spend": round(tick_state.prediction_spend, 6),
        "remaining_work_budget": round(remaining_work_budget, 6),
        "backlog": queue_depth,
        "queued_age": queue_age_metrics.get("queued_task_age_mean_tick", 0.0),
        "completion_fraction": round(completion_fraction, 6),
        "starvation": int(queue_depth > 0 and work_actions == 0),
        "prediction_spend_volatility": 0.0,
        "work_budget_volatility": round(
            float(tick_state.lost_work_opportunity / max(action_opportunity, 1)),
            6,
        ),
        "source_ledger_queue_accounting": round(tick_state.source_ledger_queue_accounting, 6),
    }
    return metrics


def _a7_2_clip(config: OmegaConfig, value: float) -> float:
    assert config.a7_2_delayed_prediction is not None
    cfg = config.a7_2_delayed_prediction
    return _clamp(value, cfg.artifact_clip_min, cfg.artifact_clip_max)


def _softmax_probabilities(values: list[float], *, temperature: float) -> np.ndarray:
    scaled = np.array(values, dtype=float) / temperature
    shifted = scaled - np.max(scaled)
    exp = np.exp(shifted)
    return exp / exp.sum()


def _sigmoid(value: float) -> float:
    return float(1.0 / (1.0 + np.exp(-value)))


def _clamp01(value: float) -> float:
    return _clamp(value, 0.0, 1.0)


def _clamp(value: float, low: float, high: float) -> float:
    return round(float(min(high, max(low, value))), 6)


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
    a5_prediction_spend_charged: int | str = "",
    a5_prediction_work_budget_remaining: int | str = "",
    a6_artifact_update_source: str = "",
    a6_artifact_field: str = "",
    a6_artifact_delta_total: float | str = "",
    a6_artifact_delta_ambient: float | str = "",
    a6_artifact_delta_handoff_attempt: float | str = "",
    a6_artifact_delta_handoff_success: float | str = "",
    a6_artifact_delta_handoff_failure: float | str = "",
    a6_artifact_delta_prediction_expenditure: float | str = "",
    a6_artifact_delta_prediction_error: float | str = "",
    a6_artifact_delta_queue_work_accounting: float | str = "",
    a6_artifact_delta_noise: float | str = "",
    a6_artifact_delta_unclipped: float | str = "",
    a6_artifact_delta_clip_residual: float | str = "",
    a7_condition: str = "",
    a7_semantic_field: str = "",
    a7_delta_total: float | str = "",
    a7_delta_ambient_decay: float | str = "",
    a7_delta_self_contribution: float | str = "",
    a7_delta_peer_contribution: float | str = "",
    a7_delta_artifact_handoff: float | str = "",
    a7_delta_prediction_expenditure: float | str = "",
    a7_delta_prediction_error: float | str = "",
    a7_delta_queue_work_accounting: float | str = "",
    a7_delta_semantic_noise: float | str = "",
    a7_delta_clip_residual: float | str = "",
    a7_2_condition: str = "",
    selected_action: str = "",
    forecast_update_created_tick: int | str = "",
    forecast_update_visible_tick: int | str = "",
    artifact_update_created_tick: int | str = "",
    artifact_update_visible_tick: int | str = "",
    prediction_work_cost: float | str = "",
    source_ledger_forecast_error: float | str = "",
    source_ledger_artifact: float | str = "",
    source_ledger_queue_accounting: float | str = "",
    source_ledger_artifact_readiness_delta: float | str = "",
    source_ledger_artifact_coherence_delta: float | str = "",
    source_ledger_artifact_contradiction_delta: float | str = "",
    source_ledger_artifact_risk_delta: float | str = "",
    source_ledger_clip_residual: float | str = "",
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
        "a5_prediction_spend_charged": a5_prediction_spend_charged,
        "a5_prediction_work_budget_remaining": a5_prediction_work_budget_remaining,
        "a6_artifact_update_source": a6_artifact_update_source,
        "a6_artifact_field": a6_artifact_field,
        "a6_artifact_delta_total": a6_artifact_delta_total,
        "a6_artifact_delta_ambient": a6_artifact_delta_ambient,
        "a6_artifact_delta_handoff_attempt": a6_artifact_delta_handoff_attempt,
        "a6_artifact_delta_handoff_success": a6_artifact_delta_handoff_success,
        "a6_artifact_delta_handoff_failure": a6_artifact_delta_handoff_failure,
        "a6_artifact_delta_prediction_expenditure": a6_artifact_delta_prediction_expenditure,
        "a6_artifact_delta_prediction_error": a6_artifact_delta_prediction_error,
        "a6_artifact_delta_queue_work_accounting": a6_artifact_delta_queue_work_accounting,
        "a6_artifact_delta_noise": a6_artifact_delta_noise,
        "a6_artifact_delta_unclipped": a6_artifact_delta_unclipped,
        "a6_artifact_delta_clip_residual": a6_artifact_delta_clip_residual,
        "a7_condition": a7_condition,
        "a7_semantic_field": a7_semantic_field,
        "a7_delta_total": a7_delta_total,
        "a7_delta_ambient_decay": a7_delta_ambient_decay,
        "a7_delta_self_contribution": a7_delta_self_contribution,
        "a7_delta_peer_contribution": a7_delta_peer_contribution,
        "a7_delta_artifact_handoff": a7_delta_artifact_handoff,
        "a7_delta_prediction_expenditure": a7_delta_prediction_expenditure,
        "a7_delta_prediction_error": a7_delta_prediction_error,
        "a7_delta_queue_work_accounting": a7_delta_queue_work_accounting,
        "a7_delta_semantic_noise": a7_delta_semantic_noise,
        "a7_delta_clip_residual": a7_delta_clip_residual,
        "a7_2_condition": a7_2_condition,
        "selected_action": selected_action,
        "forecast_update_created_tick": forecast_update_created_tick,
        "forecast_update_visible_tick": forecast_update_visible_tick,
        "artifact_update_created_tick": artifact_update_created_tick,
        "artifact_update_visible_tick": artifact_update_visible_tick,
        "prediction_work_cost": prediction_work_cost,
        "source_ledger_forecast_error": source_ledger_forecast_error,
        "source_ledger_artifact": source_ledger_artifact,
        "source_ledger_queue_accounting": source_ledger_queue_accounting,
        "source_ledger_artifact_readiness_delta": source_ledger_artifact_readiness_delta,
        "source_ledger_artifact_coherence_delta": source_ledger_artifact_coherence_delta,
        "source_ledger_artifact_contradiction_delta": source_ledger_artifact_contradiction_delta,
        "source_ledger_artifact_risk_delta": source_ledger_artifact_risk_delta,
        "source_ledger_clip_residual": source_ledger_clip_residual,
    }
