"""Configuration loading for OmegaSim runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


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
class OmegaConfig:
    run: RunConfig
    model: ModelConfig
    outputs: OutputsConfig = field(default_factory=OutputsConfig)
    attention_policy: AttentionPolicyConfig | None = None
    exogenous_arrivals: ExogenousArrivalsConfig | None = None

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
    )
    _validate_actions(cfg.model.actions)
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


def _attention_selection_strategy(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Config value {name!r} must be a string.")
    if value not in ATTENTION_SELECTION_STRATEGIES:
        names = ", ".join(ATTENTION_SELECTION_STRATEGIES)
        raise ValueError(f"Config value {name!r} must be one of: {names}.")
    return value


def _validate_actions(actions: tuple[str, ...]) -> None:
    required = {"idle", "message", "create_task", "work_task"}
    configured = set(actions)
    missing = required - configured
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"model.actions is missing required baseline actions: {names}")
    unknown = configured - required
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"model.actions contains unsupported baseline actions: {names}")
    if len(configured) != len(actions):
        raise ValueError("model.actions must not contain duplicates.")
