"""Configuration loading for OmegaSim runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ohdyn.a7_2_delayed_prediction_contract import (
    A7_2_CONDITIONS,
    A7_2_SMOKE_PARAMETERS,
)
from ohdyn.a7_semantic_field_contract import A7_CONDITIONS


ATTENTION_CLASSES = (
    "near_term_external",
    "long_term_research",
    "internal_improvement",
    "housekeeping",
)

ATTENTION_SELECTION_STRATEGIES = (
    "quota_balance",
    "random_available",
)

COUPLING_MODES = (
    "none",
    "direct",
    "delayed",
    "shuffled",
)

PREDICTIVE_CONTROL_CONDITIONS = (
    "reactive",
    "linear",
    "nonlinear",
    "nonlinear_high_budget",
    "oracle",
    "shuffled",
    "nonlinear_shuffled",
    "nonlinear_high_budget_shuffled",
    "spend_only_replay",
)

LOGISTIC_APPRAISAL_CONDITIONS = (
    "logistic",
    "linear",
    "threshold_shuffled",
    "phase_shuffled",
)

SEMANTIC_FIELD_CONDITIONS = A7_CONDITIONS
A7_2_DELAYED_PREDICTION_CONDITIONS = A7_2_CONDITIONS

A6_ACTIONS = (
    "synthesize",
    "review",
    "formalize",
    "maintain",
    "predict",
    "communicate",
    "pause",
)


@dataclass(frozen=True)
class RunConfig:
    experiment_id: str
    ticks: int


@dataclass(frozen=True)
class ModelConfig:
    agent_count: int
    actions: tuple[str, ...] = ("idle", "message", "create_task", "work_task")
    task_creation_pressure: float = 1.0
    work_service_capacity: float = 1.0


@dataclass(frozen=True)
class OutputsConfig:
    write_manifest: bool = True
    write_metrics: bool = True
    write_events: bool = True
    write_summary: bool = True


@dataclass(frozen=True)
class AttentionPolicyConfig:
    near_term_external: float
    long_term_research: float
    internal_improvement: float
    housekeeping: float
    selection_strategy: str = "quota_balance"

    def shares(self) -> dict[str, float]:
        return {
            class_name: float(getattr(self, class_name))
            for class_name in ATTENTION_CLASSES
        }


@dataclass(frozen=True)
class ExogenousArrivalsConfig:
    enabled: bool = False
    rate_per_tick: float = 0.0
    near_term_external: float = 0.0
    long_term_research: float = 0.0
    internal_improvement: float = 0.0
    housekeeping: float = 0.0

    def task_class_shares(self) -> dict[str, float]:
        return {
            class_name: float(getattr(self, class_name))
            for class_name in ATTENTION_CLASSES
        }


@dataclass(frozen=True)
class PredictiveControlConfig:
    condition: str
    prediction_budget: float
    lead_ticks: int = 2
    signal_period: int = 12
    signal_amplitude: float = 0.25
    memory_window: int = 3
    phase_shift_ticks: int = 3
    charge_prediction_to_work: bool = False
    prediction_cost_scale: float = 1.0
    max_prediction_work_fraction_per_tick: float | None = None


@dataclass(frozen=True)
class LogisticAppraisalConfig:
    condition: str
    appraisal_gain: float
    sigmoid_slope: float
    prediction_budget: float
    action_temperature: float = 1.0
    handoff_threshold: float = 0.55
    overload_threshold: float = 0.82
    adaptive_threshold_rate: float = 0.03
    phase_shift_ticks: int = 2
    threshold_shuffle_probability: float = 0.35
    appraisal_noise: float = 0.04
    artifact_noise: float = 0.03


@dataclass(frozen=True)
class SemanticFieldConfig:
    condition: str
    prediction_budget_per_tick: float
    lead_ticks: int = 2
    semantic_decay: float = 0.9
    logistic_beta: float = 4.0
    linear_gain: float = 1.0
    threshold_adaptation_rate: float = 0.03
    semantic_noise: float = 0.02
    phase_shift_ticks: int = 3


@dataclass(frozen=True)
class A7_2DelayedPredictionConfig:
    condition: str
    forecast_delay_ticks: int
    artifact_delay_ticks: int
    prediction_cost_work_fraction: float
    max_prediction_work_fraction_per_tick: float
    fatigue_decay: float
    fatigue_increment_predict: float
    fatigue_increment_work: float
    fatigue_increment_review: float
    fatigue_increment_synthesize: float
    threshold_learning_rate_error: float
    threshold_recovery_rate: float
    threshold_min: float
    threshold_max: float
    utility_slope_predict: float
    utility_slope_work: float
    utility_slope_review: float
    utility_slope_synthesize: float
    artifact_clip_min: float
    artifact_clip_max: float
    artifact_decay: float
    same_tick_feedback_allowed: bool = False
    spend_only_replay_preserves_prediction_work_deductions: bool = False
    artifact_off_preserves_queue_accounting_controls: bool = False


@dataclass(frozen=True)
class HiveConfig:
    hive_id: str
    seed_offset: int
    exogenous_arrival_rate: float = 0.0
    work_service_capacity: float = 1.0


@dataclass(frozen=True)
class CouplingConfig:
    mode: str = "none"
    transfer_probability: float = 0.0
    delay_ticks: int = 0
    shuffle_seed_offset: int = 2000


@dataclass(frozen=True)
class OmegaConfig:
    run: RunConfig
    model: ModelConfig
    outputs: OutputsConfig = field(default_factory=OutputsConfig)
    attention_policy: AttentionPolicyConfig | None = None
    exogenous_arrivals: ExogenousArrivalsConfig | None = None
    predictive_control: PredictiveControlConfig | None = None
    logistic_appraisal: LogisticAppraisalConfig | None = None
    semantic_field: SemanticFieldConfig | None = None
    a7_2_delayed_prediction: A7_2DelayedPredictionConfig | None = None
    hives: tuple[HiveConfig, ...] = ()
    coupling: CouplingConfig | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["model"]["actions"] = list(self.model.actions)
        if self.attention_policy is None:
            data.pop("attention_policy")
        if self.exogenous_arrivals is None:
            data.pop("exogenous_arrivals")
        else:
            arrivals = data["exogenous_arrivals"]
            arrivals["task_class_shares"] = {
                class_name: arrivals.pop(class_name)
                for class_name in ATTENTION_CLASSES
            }
        if self.predictive_control is None:
            data.pop("predictive_control")
        else:
            if not self.predictive_control.charge_prediction_to_work:
                data["predictive_control"].pop("charge_prediction_to_work")
            if self.predictive_control.prediction_cost_scale == 1.0:
                data["predictive_control"].pop("prediction_cost_scale")
            if self.predictive_control.max_prediction_work_fraction_per_tick is None:
                data["predictive_control"].pop("max_prediction_work_fraction_per_tick")
        if self.logistic_appraisal is None:
            data.pop("logistic_appraisal")
        if self.semantic_field is None:
            data.pop("semantic_field")
        if self.a7_2_delayed_prediction is None:
            data.pop("a7_2_delayed_prediction")
        if not self.hives:
            data.pop("hives")
            data.pop("coupling")
        return data


def load_config(path: str | Path) -> OmegaConfig:
    config_path = Path(path)
    try:
        raw = yaml.safe_load(config_path.read_text()) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Config {config_path} contains invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"Config {config_path} must contain a YAML mapping.")

    run = _expect_mapping(raw.get("run"), "run")
    model = _expect_mapping(raw.get("model"), "model")
    outputs = raw.get("outputs", {})
    if outputs is None:
        outputs = {}
    outputs = _expect_mapping(outputs, "outputs")
    attention_policy = _optional_attention_policy(raw.get("attention_policy"))
    exogenous_arrivals = _optional_exogenous_arrivals(raw.get("exogenous_arrivals"))
    predictive_control = _optional_predictive_control(raw.get("predictive_control"))
    logistic_appraisal = _optional_logistic_appraisal(raw.get("logistic_appraisal"))
    semantic_field = _optional_semantic_field(raw.get("semantic_field"))
    a7_2_delayed_prediction = _optional_a7_2_delayed_prediction(
        raw.get("a7_2_delayed_prediction")
    )
    hives = _optional_hives(raw.get("hives"))
    coupling = _optional_coupling(raw.get("coupling"), hives)

    actions = tuple(str(action) for action in model.get("actions", ()))
    cfg = OmegaConfig(
        run=RunConfig(
            experiment_id=_nonempty_str(run.get("experiment_id"), "run.experiment_id"),
            ticks=_positive_int(run.get("ticks"), "run.ticks"),
        ),
        model=ModelConfig(
            agent_count=_exact_int(model.get("agent_count"), "model.agent_count", expected=15),
            actions=actions,
            task_creation_pressure=_nonnegative_float(
                model.get("task_creation_pressure", 1.0),
                "model.task_creation_pressure",
            ),
            work_service_capacity=_nonnegative_float(
                model.get("work_service_capacity", 1.0),
                "model.work_service_capacity",
            ),
        ),
        outputs=OutputsConfig(
            write_manifest=_bool(outputs.get("write_manifest", True), "outputs.write_manifest"),
            write_metrics=_bool(outputs.get("write_metrics", True), "outputs.write_metrics"),
            write_events=_bool(outputs.get("write_events", True), "outputs.write_events"),
            write_summary=_bool(outputs.get("write_summary", True), "outputs.write_summary"),
        ),
        attention_policy=attention_policy,
        exogenous_arrivals=exogenous_arrivals,
        predictive_control=predictive_control,
        logistic_appraisal=logistic_appraisal,
        semantic_field=semantic_field,
        a7_2_delayed_prediction=a7_2_delayed_prediction,
        hives=hives,
        coupling=coupling,
    )
    _validate_actions(
        cfg.model.actions,
        allow_a6=(
            cfg.logistic_appraisal is not None
            or cfg.semantic_field is not None
            or cfg.a7_2_delayed_prediction is not None
        ),
    )
    _validate_predictive_control_scope(cfg)
    _validate_logistic_appraisal_scope(cfg)
    _validate_semantic_field_scope(cfg)
    _validate_a7_2_delayed_prediction_scope(cfg)
    _validate_hive_seed_streams(cfg.hives, cfg.coupling)
    return cfg


def _expect_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Config section {name!r} must be a mapping.")
    return value


def _nonempty_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Config value {name!r} must be a non-empty string.")
    return value


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"Config value {name!r} must be a positive integer.")
    return value


def _nonnegative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Config value {name!r} must be a non-negative integer.")
    return value


def _exact_int(value: Any, name: str, expected: int) -> int:
    parsed = _positive_int(value, name)
    if parsed != expected:
        raise ValueError(f"Config value {name!r} must be exactly {expected} for the A0/A1 baseline.")
    return parsed


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"Config value {name!r} must be a boolean.")
    return value


def _optional_attention_policy(value: Any) -> AttentionPolicyConfig | None:
    if value is None:
        return None
    policy = _expect_mapping(value, "attention_policy")
    supported_keys = set(ATTENTION_CLASSES) | {"selection_strategy"}
    unknown = set(policy) - supported_keys
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"attention_policy contains unsupported classes: {names}")
    missing = set(ATTENTION_CLASSES) - set(policy)
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"attention_policy is missing required classes: {names}")

    shares = {
        class_name: _share(policy[class_name], f"attention_policy.{class_name}")
        for class_name in ATTENTION_CLASSES
    }
    total = sum(shares.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError("attention_policy values must sum to 1.0.")
    selection_strategy = _attention_selection_strategy(
        policy.get("selection_strategy", "quota_balance"),
        "attention_policy.selection_strategy",
    )
    return AttentionPolicyConfig(**shares, selection_strategy=selection_strategy)


def _optional_exogenous_arrivals(value: Any) -> ExogenousArrivalsConfig | None:
    if value is None:
        return None
    arrivals = _expect_mapping(value, "exogenous_arrivals")
    supported_keys = {"enabled", "rate_per_tick", "task_class_shares"}
    unknown = set(arrivals) - supported_keys
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"exogenous_arrivals contains unsupported keys: {names}")

    enabled = _bool(arrivals.get("enabled", False), "exogenous_arrivals.enabled")
    rate_per_tick = _nonnegative_float(
        arrivals.get("rate_per_tick", 0.0),
        "exogenous_arrivals.rate_per_tick",
    )
    raw_shares = arrivals.get("task_class_shares")
    if raw_shares is None:
        if enabled:
            raise ValueError(
                "exogenous_arrivals.task_class_shares is required when exogenous arrivals are enabled."
            )
        shares = {class_name: 0.0 for class_name in ATTENTION_CLASSES}
    else:
        share_mapping = _expect_mapping(raw_shares, "exogenous_arrivals.task_class_shares")
        unknown_shares = set(share_mapping) - set(ATTENTION_CLASSES)
        if unknown_shares:
            names = ", ".join(sorted(unknown_shares))
            raise ValueError(
                f"exogenous_arrivals.task_class_shares contains unsupported classes: {names}"
            )
        missing = set(ATTENTION_CLASSES) - set(share_mapping)
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(
                f"exogenous_arrivals.task_class_shares is missing required classes: {names}"
            )
        shares = {
            class_name: _share(
                share_mapping[class_name],
                f"exogenous_arrivals.task_class_shares.{class_name}",
            )
            for class_name in ATTENTION_CLASSES
        }
        total = sum(shares.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError("exogenous_arrivals.task_class_shares values must sum to 1.0.")

    return ExogenousArrivalsConfig(
        enabled=enabled,
        rate_per_tick=rate_per_tick,
        **shares,
    )


def _optional_predictive_control(value: Any) -> PredictiveControlConfig | None:
    if value is None:
        return None
    control = _expect_mapping(value, "predictive_control")
    supported_keys = {
        "condition",
        "prediction_budget",
        "lead_ticks",
        "signal_period",
        "signal_amplitude",
        "memory_window",
        "phase_shift_ticks",
        "charge_prediction_to_work",
        "prediction_cost_scale",
        "max_prediction_work_fraction_per_tick",
    }
    unknown = set(control) - supported_keys
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"predictive_control contains unsupported keys: {names}")

    condition = _predictive_control_condition(
        control.get("condition"),
        "predictive_control.condition",
    )
    return PredictiveControlConfig(
        condition=condition,
        prediction_budget=_nonnegative_float(
            control.get("prediction_budget", 0.0),
            "predictive_control.prediction_budget",
        ),
        lead_ticks=_nonnegative_int(
            control.get("lead_ticks", 2),
            "predictive_control.lead_ticks",
        ),
        signal_period=_positive_int(
            control.get("signal_period", 12),
            "predictive_control.signal_period",
        ),
        signal_amplitude=_probability(
            control.get("signal_amplitude", 0.25),
            "predictive_control.signal_amplitude",
        ),
        memory_window=_positive_int(
            control.get("memory_window", 3),
            "predictive_control.memory_window",
        ),
        phase_shift_ticks=_nonnegative_int(
            control.get("phase_shift_ticks", 3),
            "predictive_control.phase_shift_ticks",
        ),
        charge_prediction_to_work=_bool(
            control.get("charge_prediction_to_work", False),
            "predictive_control.charge_prediction_to_work",
        ),
        prediction_cost_scale=_nonnegative_float(
            control.get("prediction_cost_scale", 1.0),
            "predictive_control.prediction_cost_scale",
        ),
        max_prediction_work_fraction_per_tick=_optional_probability(
            control.get("max_prediction_work_fraction_per_tick"),
            "predictive_control.max_prediction_work_fraction_per_tick",
        ),
    )


def _optional_logistic_appraisal(value: Any) -> LogisticAppraisalConfig | None:
    if value is None:
        return None
    appraisal = _expect_mapping(value, "logistic_appraisal")
    supported_keys = {
        "condition",
        "appraisal_gain",
        "sigmoid_slope",
        "prediction_budget",
        "action_temperature",
        "handoff_threshold",
        "overload_threshold",
        "adaptive_threshold_rate",
        "phase_shift_ticks",
        "threshold_shuffle_probability",
        "appraisal_noise",
        "artifact_noise",
    }
    unknown = set(appraisal) - supported_keys
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"logistic_appraisal contains unsupported keys: {names}")

    return LogisticAppraisalConfig(
        condition=_logistic_appraisal_condition(
            appraisal.get("condition"),
            "logistic_appraisal.condition",
        ),
        appraisal_gain=_nonnegative_float(
            appraisal.get("appraisal_gain", 1.0),
            "logistic_appraisal.appraisal_gain",
        ),
        sigmoid_slope=_positive_float(
            appraisal.get("sigmoid_slope", 6.0),
            "logistic_appraisal.sigmoid_slope",
        ),
        prediction_budget=_nonnegative_float(
            appraisal.get("prediction_budget", 0.25),
            "logistic_appraisal.prediction_budget",
        ),
        action_temperature=_positive_float(
            appraisal.get("action_temperature", 1.0),
            "logistic_appraisal.action_temperature",
        ),
        handoff_threshold=_probability(
            appraisal.get("handoff_threshold", 0.55),
            "logistic_appraisal.handoff_threshold",
        ),
        overload_threshold=_probability(
            appraisal.get("overload_threshold", 0.82),
            "logistic_appraisal.overload_threshold",
        ),
        adaptive_threshold_rate=_probability(
            appraisal.get("adaptive_threshold_rate", 0.03),
            "logistic_appraisal.adaptive_threshold_rate",
        ),
        phase_shift_ticks=_nonnegative_int(
            appraisal.get("phase_shift_ticks", 2),
            "logistic_appraisal.phase_shift_ticks",
        ),
        threshold_shuffle_probability=_probability(
            appraisal.get("threshold_shuffle_probability", 0.35),
            "logistic_appraisal.threshold_shuffle_probability",
        ),
        appraisal_noise=_probability(
            appraisal.get("appraisal_noise", 0.04),
            "logistic_appraisal.appraisal_noise",
        ),
        artifact_noise=_probability(
            appraisal.get("artifact_noise", 0.03),
            "logistic_appraisal.artifact_noise",
        ),
    )


def _optional_semantic_field(value: Any) -> SemanticFieldConfig | None:
    if value is None:
        return None
    semantic_field = _expect_mapping(value, "semantic_field")
    supported_keys = {
        "condition",
        "prediction_budget_per_tick",
        "lead_ticks",
        "semantic_decay",
        "logistic_beta",
        "linear_gain",
        "threshold_adaptation_rate",
        "semantic_noise",
        "phase_shift_ticks",
    }
    unknown = set(semantic_field) - supported_keys
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"semantic_field contains unsupported keys: {names}")

    return SemanticFieldConfig(
        condition=_semantic_field_condition(
            semantic_field.get("condition"),
            "semantic_field.condition",
        ),
        prediction_budget_per_tick=_nonnegative_float(
            semantic_field.get("prediction_budget_per_tick", 0.25),
            "semantic_field.prediction_budget_per_tick",
        ),
        lead_ticks=_nonnegative_int(
            semantic_field.get("lead_ticks", 2),
            "semantic_field.lead_ticks",
        ),
        semantic_decay=_probability(
            semantic_field.get("semantic_decay", 0.9),
            "semantic_field.semantic_decay",
        ),
        logistic_beta=_positive_float(
            semantic_field.get("logistic_beta", 4.0),
            "semantic_field.logistic_beta",
        ),
        linear_gain=_nonnegative_float(
            semantic_field.get("linear_gain", 1.0),
            "semantic_field.linear_gain",
        ),
        threshold_adaptation_rate=_probability(
            semantic_field.get("threshold_adaptation_rate", 0.03),
            "semantic_field.threshold_adaptation_rate",
        ),
        semantic_noise=_probability(
            semantic_field.get("semantic_noise", 0.02),
            "semantic_field.semantic_noise",
        ),
        phase_shift_ticks=_nonnegative_int(
            semantic_field.get("phase_shift_ticks", 3),
            "semantic_field.phase_shift_ticks",
        ),
    )


def _optional_a7_2_delayed_prediction(
    value: Any,
) -> A7_2DelayedPredictionConfig | None:
    if value is None:
        return None
    section = _expect_mapping(value, "a7_2_delayed_prediction")
    supported_keys = {
        "condition",
        "forecast_delay_ticks",
        "artifact_delay_ticks",
        "prediction_cost_work_fraction",
        "max_prediction_work_fraction_per_tick",
        "fatigue_decay",
        "fatigue_increment_predict",
        "fatigue_increment_work",
        "fatigue_increment_review",
        "fatigue_increment_synthesize",
        "threshold_learning_rate_error",
        "threshold_recovery_rate",
        "threshold_min",
        "threshold_max",
        "utility_slope_predict",
        "utility_slope_work",
        "utility_slope_review",
        "utility_slope_synthesize",
        "artifact_clip_min",
        "artifact_clip_max",
        "artifact_decay",
        "same_tick_feedback_allowed",
        "spend_only_replay_preserves_prediction_work_deductions",
        "artifact_off_preserves_queue_accounting_controls",
    }
    unknown = set(section) - supported_keys
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"a7_2_delayed_prediction contains unsupported keys: {names}")

    condition = _a7_2_delayed_prediction_condition(
        section.get("condition"),
        "a7_2_delayed_prediction.condition",
    )
    cfg = A7_2DelayedPredictionConfig(
        condition=condition,
        forecast_delay_ticks=_nonnegative_int(
            section.get("forecast_delay_ticks"),
            "a7_2_delayed_prediction.forecast_delay_ticks",
        ),
        artifact_delay_ticks=_nonnegative_int(
            section.get("artifact_delay_ticks"),
            "a7_2_delayed_prediction.artifact_delay_ticks",
        ),
        prediction_cost_work_fraction=_probability(
            section.get("prediction_cost_work_fraction"),
            "a7_2_delayed_prediction.prediction_cost_work_fraction",
        ),
        max_prediction_work_fraction_per_tick=_probability(
            section.get("max_prediction_work_fraction_per_tick"),
            "a7_2_delayed_prediction.max_prediction_work_fraction_per_tick",
        ),
        fatigue_decay=_probability(
            section.get("fatigue_decay"),
            "a7_2_delayed_prediction.fatigue_decay",
        ),
        fatigue_increment_predict=_probability(
            section.get("fatigue_increment_predict"),
            "a7_2_delayed_prediction.fatigue_increment_predict",
        ),
        fatigue_increment_work=_probability(
            section.get("fatigue_increment_work"),
            "a7_2_delayed_prediction.fatigue_increment_work",
        ),
        fatigue_increment_review=_probability(
            section.get("fatigue_increment_review"),
            "a7_2_delayed_prediction.fatigue_increment_review",
        ),
        fatigue_increment_synthesize=_probability(
            section.get("fatigue_increment_synthesize"),
            "a7_2_delayed_prediction.fatigue_increment_synthesize",
        ),
        threshold_learning_rate_error=_probability(
            section.get("threshold_learning_rate_error"),
            "a7_2_delayed_prediction.threshold_learning_rate_error",
        ),
        threshold_recovery_rate=_probability(
            section.get("threshold_recovery_rate"),
            "a7_2_delayed_prediction.threshold_recovery_rate",
        ),
        threshold_min=_float(
            section.get("threshold_min"),
            "a7_2_delayed_prediction.threshold_min",
        ),
        threshold_max=_float(
            section.get("threshold_max"),
            "a7_2_delayed_prediction.threshold_max",
        ),
        utility_slope_predict=_positive_float(
            section.get("utility_slope_predict"),
            "a7_2_delayed_prediction.utility_slope_predict",
        ),
        utility_slope_work=_positive_float(
            section.get("utility_slope_work"),
            "a7_2_delayed_prediction.utility_slope_work",
        ),
        utility_slope_review=_positive_float(
            section.get("utility_slope_review"),
            "a7_2_delayed_prediction.utility_slope_review",
        ),
        utility_slope_synthesize=_positive_float(
            section.get("utility_slope_synthesize"),
            "a7_2_delayed_prediction.utility_slope_synthesize",
        ),
        artifact_clip_min=_probability(
            section.get("artifact_clip_min"),
            "a7_2_delayed_prediction.artifact_clip_min",
        ),
        artifact_clip_max=_probability(
            section.get("artifact_clip_max"),
            "a7_2_delayed_prediction.artifact_clip_max",
        ),
        artifact_decay=_probability(
            section.get("artifact_decay"),
            "a7_2_delayed_prediction.artifact_decay",
        ),
        same_tick_feedback_allowed=_bool(
            section.get("same_tick_feedback_allowed", False),
            "a7_2_delayed_prediction.same_tick_feedback_allowed",
        ),
        spend_only_replay_preserves_prediction_work_deductions=_bool(
            section.get("spend_only_replay_preserves_prediction_work_deductions", False),
            (
                "a7_2_delayed_prediction."
                "spend_only_replay_preserves_prediction_work_deductions"
            ),
        ),
        artifact_off_preserves_queue_accounting_controls=_bool(
            section.get("artifact_off_preserves_queue_accounting_controls", False),
            "a7_2_delayed_prediction.artifact_off_preserves_queue_accounting_controls",
        ),
    )
    _validate_a7_2_preregistered_values(cfg)
    return cfg


def _optional_hives(value: Any) -> tuple[HiveConfig, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("Config section 'hives' must be a list.")
    if not value:
        raise ValueError("Config section 'hives' must contain at least one hive.")

    hives = []
    seen_ids: set[str] = set()
    seen_offsets: set[int] = set()
    for index, raw_hive in enumerate(value):
        section = f"hives[{index}]"
        hive = _expect_mapping(raw_hive, section)
        supported_keys = {
            "hive_id",
            "seed_offset",
            "exogenous_arrival_rate",
            "work_service_capacity",
        }
        unknown = set(hive) - supported_keys
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"{section} contains unsupported keys: {names}")

        hive_id = _nonempty_str(hive.get("hive_id"), f"{section}.hive_id")
        if hive_id in seen_ids:
            raise ValueError(f"hives contains duplicate hive_id: {hive_id}")
        seen_ids.add(hive_id)

        seed_offset = _nonnegative_int(hive.get("seed_offset"), f"{section}.seed_offset")
        if seed_offset in seen_offsets:
            raise ValueError(f"hives contains duplicate seed_offset: {seed_offset}")
        seen_offsets.add(seed_offset)

        hives.append(
            HiveConfig(
                hive_id=hive_id,
                seed_offset=seed_offset,
                exogenous_arrival_rate=_nonnegative_float(
                    hive.get("exogenous_arrival_rate", 0.0),
                    f"{section}.exogenous_arrival_rate",
                ),
                work_service_capacity=_nonnegative_float(
                    hive.get("work_service_capacity", 1.0),
                    f"{section}.work_service_capacity",
                ),
            )
        )
    return tuple(hives)


def _optional_coupling(value: Any, hives: tuple[HiveConfig, ...]) -> CouplingConfig | None:
    if not hives:
        if value is not None:
            raise ValueError("Config section 'coupling' requires opt-in 'hives'.")
        return None

    coupling = {} if value is None else _expect_mapping(value, "coupling")
    supported_keys = {"mode", "transfer_probability", "delay_ticks", "shuffle_seed_offset"}
    unknown = set(coupling) - supported_keys
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"coupling contains unsupported keys: {names}")

    cfg = CouplingConfig(
        mode=_coupling_mode(coupling.get("mode", "none"), "coupling.mode"),
        transfer_probability=_probability(
            coupling.get("transfer_probability", 0.0),
            "coupling.transfer_probability",
        ),
        delay_ticks=_nonnegative_int(coupling.get("delay_ticks", 0), "coupling.delay_ticks"),
        shuffle_seed_offset=_nonnegative_int(
            coupling.get("shuffle_seed_offset", 2000),
            "coupling.shuffle_seed_offset",
        ),
    )
    _validate_coupling(cfg)
    return cfg


def _share(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Config value {name!r} must be a number.")
    parsed = float(value)
    if parsed < 0.0:
        raise ValueError(f"Config value {name!r} must be non-negative.")
    return parsed


def _nonnegative_float(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Config value {name!r} must be a number.")
    parsed = float(value)
    if parsed < 0.0:
        raise ValueError(f"Config value {name!r} must be non-negative.")
    return parsed


def _float(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Config value {name!r} must be a number.")
    return float(value)


def _positive_float(value: Any, name: str) -> float:
    parsed = _nonnegative_float(value, name)
    if parsed <= 0.0:
        raise ValueError(f"Config value {name!r} must be positive.")
    return parsed


def _probability(value: Any, name: str) -> float:
    parsed = _nonnegative_float(value, name)
    if parsed > 1.0:
        raise ValueError(f"Config value {name!r} must be between 0.0 and 1.0.")
    return parsed


def _optional_probability(value: Any, name: str) -> float | None:
    if value is None:
        return None
    return _probability(value, name)


def _attention_selection_strategy(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Config value {name!r} must be a string.")
    if value not in ATTENTION_SELECTION_STRATEGIES:
        names = ", ".join(ATTENTION_SELECTION_STRATEGIES)
        raise ValueError(f"Config value {name!r} must be one of: {names}.")
    return value


def _coupling_mode(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Config value {name!r} must be a string.")
    if value not in COUPLING_MODES:
        names = ", ".join(COUPLING_MODES)
        raise ValueError(f"Config value {name!r} must be one of: {names}.")
    return value


def _predictive_control_condition(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Config value {name!r} must be a string.")
    if value not in PREDICTIVE_CONTROL_CONDITIONS:
        names = ", ".join(PREDICTIVE_CONTROL_CONDITIONS)
        raise ValueError(f"Config value {name!r} must be one of: {names}.")
    return value


def _logistic_appraisal_condition(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Config value {name!r} must be a string.")
    if value not in LOGISTIC_APPRAISAL_CONDITIONS:
        names = ", ".join(LOGISTIC_APPRAISAL_CONDITIONS)
        raise ValueError(f"Config value {name!r} must be one of: {names}.")
    return value


def _semantic_field_condition(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Config value {name!r} must be a string.")
    if value not in SEMANTIC_FIELD_CONDITIONS:
        names = ", ".join(SEMANTIC_FIELD_CONDITIONS)
        raise ValueError(f"Config value {name!r} must be one of: {names}.")
    return value


def _a7_2_delayed_prediction_condition(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Config value {name!r} must be a string.")
    if value not in A7_2_DELAYED_PREDICTION_CONDITIONS:
        names = ", ".join(A7_2_DELAYED_PREDICTION_CONDITIONS)
        raise ValueError(f"Config value {name!r} must be one of: {names}.")
    return value


def _validate_a7_2_preregistered_values(
    config: A7_2DelayedPredictionConfig,
) -> None:
    actual = {
        "forecast_delay_ticks": config.forecast_delay_ticks,
        "artifact_delay_ticks": config.artifact_delay_ticks,
        "prediction_cost_work_fraction": config.prediction_cost_work_fraction,
        "max_prediction_work_fraction_per_tick": config.max_prediction_work_fraction_per_tick,
        "fatigue_decay": config.fatigue_decay,
        "fatigue_increment_predict": config.fatigue_increment_predict,
        "fatigue_increment_work": config.fatigue_increment_work,
        "fatigue_increment_review": config.fatigue_increment_review,
        "fatigue_increment_synthesize": config.fatigue_increment_synthesize,
        "threshold_learning_rate_error": config.threshold_learning_rate_error,
        "threshold_recovery_rate": config.threshold_recovery_rate,
        "threshold_min": config.threshold_min,
        "threshold_max": config.threshold_max,
        "utility_slope_predict": config.utility_slope_predict,
        "utility_slope_work": config.utility_slope_work,
        "utility_slope_review": config.utility_slope_review,
        "utility_slope_synthesize": config.utility_slope_synthesize,
        "artifact_clip_min": config.artifact_clip_min,
        "artifact_clip_max": config.artifact_clip_max,
        "artifact_decay": config.artifact_decay,
    }
    frozen = {
        key: value
        for key, value in A7_2_SMOKE_PARAMETERS.items()
        if key != "horizon_ticks"
    }
    for key, expected in frozen.items():
        if actual[key] != expected:
            raise ValueError(
                f"a7_2_delayed_prediction.{key} must remain preregistered at {expected}."
            )
    if config.threshold_min >= config.threshold_max:
        raise ValueError("a7_2_delayed_prediction threshold_min must be < threshold_max.")
    if config.artifact_clip_min >= config.artifact_clip_max:
        raise ValueError(
            "a7_2_delayed_prediction artifact_clip_min must be < artifact_clip_max."
        )
    if (
        config.condition == "same_tick_logistic_prediction"
        and not config.same_tick_feedback_allowed
    ):
        raise ValueError(
            "same_tick_logistic_prediction must explicitly allow same-tick feedback."
        )
    if (
        config.condition != "same_tick_logistic_prediction"
        and config.same_tick_feedback_allowed
    ):
        raise ValueError(
            "A7.2 same-tick feedback is allowed only for same_tick_logistic_prediction."
        )
    if (
        config.condition == "spend_only_replay"
        and not config.spend_only_replay_preserves_prediction_work_deductions
    ):
        raise ValueError(
            "spend_only_replay must preserve prediction-work deductions."
        )
    if (
        config.condition != "spend_only_replay"
        and config.spend_only_replay_preserves_prediction_work_deductions
    ):
        raise ValueError(
            "Only spend_only_replay may set "
            "spend_only_replay_preserves_prediction_work_deductions."
        )
    if (
        config.condition == "artifact_off_source_ledger_null"
        and not config.artifact_off_preserves_queue_accounting_controls
    ):
        raise ValueError(
            "artifact_off_source_ledger_null must preserve queue/accounting controls."
        )
    if (
        config.condition != "artifact_off_source_ledger_null"
        and config.artifact_off_preserves_queue_accounting_controls
    ):
        raise ValueError(
            "Only artifact_off_source_ledger_null may set "
            "artifact_off_preserves_queue_accounting_controls."
        )


def _validate_coupling(coupling: CouplingConfig) -> None:
    if coupling.mode == "none":
        if coupling.transfer_probability != 0.0:
            raise ValueError("coupling.mode 'none' requires transfer_probability 0.0.")
        if coupling.delay_ticks != 0:
            raise ValueError("coupling.mode 'none' requires delay_ticks 0.")
    elif coupling.mode == "direct":
        if coupling.delay_ticks != 0:
            raise ValueError("coupling.mode 'direct' requires delay_ticks 0.")
    elif coupling.mode == "delayed" and coupling.delay_ticks <= 0:
        raise ValueError("coupling.mode 'delayed' requires delay_ticks > 0.")


def _validate_predictive_control_scope(config: OmegaConfig) -> None:
    if config.predictive_control is None:
        return
    if config.attention_policy is None:
        raise ValueError("predictive_control requires an attention_policy section.")
    if config.hives:
        raise ValueError("predictive_control is currently preregistered for single-hive A5 runs only.")


def _validate_logistic_appraisal_scope(config: OmegaConfig) -> None:
    if config.logistic_appraisal is None:
        return
    if config.hives:
        raise ValueError("logistic_appraisal is currently preregistered for single-hive A6 runs only.")
    if config.predictive_control is not None:
        raise ValueError("logistic_appraisal must not be combined with A5 predictive_control.")


def _validate_semantic_field_scope(config: OmegaConfig) -> None:
    if config.semantic_field is None:
        return
    if config.hives:
        raise ValueError("semantic_field is currently preregistered for single-hive A7 runs only.")
    if config.predictive_control is not None:
        raise ValueError("semantic_field must not be combined with A5 predictive_control.")
    if config.logistic_appraisal is not None:
        raise ValueError("semantic_field must not be combined with A6 logistic_appraisal.")


def _validate_a7_2_delayed_prediction_scope(config: OmegaConfig) -> None:
    if config.a7_2_delayed_prediction is None:
        return
    if config.run.ticks != A7_2_SMOKE_PARAMETERS["horizon_ticks"]:
        raise ValueError("A7.2 smoke configs must use the preregistered 48-tick horizon.")
    if config.hives:
        raise ValueError(
            "a7_2_delayed_prediction is currently preregistered for single-hive A7.2 runs only."
        )
    if config.predictive_control is not None:
        raise ValueError("a7_2_delayed_prediction must not be combined with A5 predictive_control.")
    if config.logistic_appraisal is not None:
        raise ValueError(
            "a7_2_delayed_prediction must not be combined with A6 logistic_appraisal."
        )
    if config.semantic_field is not None:
        raise ValueError("a7_2_delayed_prediction must not be combined with A7 semantic_field.")


def _validate_hive_seed_streams(
    hives: tuple[HiveConfig, ...],
    coupling: CouplingConfig | None,
) -> None:
    if not hives or coupling is None:
        return
    hive_offsets = {hive.seed_offset for hive in hives}
    if coupling.shuffle_seed_offset in hive_offsets:
        raise ValueError(
            "coupling.shuffle_seed_offset must be distinct from hive seed_offset values."
        )


def _validate_actions(actions: tuple[str, ...], *, allow_a6: bool = False) -> None:
    required = {"idle", "message", "create_task", "work_task"}
    allowed = required | (set(A6_ACTIONS) if allow_a6 else set())
    configured = set(actions)
    missing = required - configured
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"model.actions is missing required baseline actions: {names}")
    unknown = configured - allowed
    if unknown:
        names = ", ".join(sorted(unknown))
        scope = "A6" if allow_a6 else "baseline"
        raise ValueError(f"model.actions contains unsupported {scope} actions: {names}")
    if len(configured) != len(actions):
        raise ValueError("model.actions must not contain duplicates.")
