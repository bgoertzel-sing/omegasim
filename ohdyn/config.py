"""Configuration loading for OmegaSim runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RunConfig:
    experiment_id: str
    ticks: int


@dataclass(frozen=True)
class ModelConfig:
    agent_count: int
    actions: tuple[str, ...] = ("idle", "message", "create_task", "work_task")


@dataclass(frozen=True)
class OutputsConfig:
    write_manifest: bool = True
    write_metrics: bool = True
    write_events: bool = True
    write_summary: bool = True


@dataclass(frozen=True)
class OmegaConfig:
    run: RunConfig
    model: ModelConfig
    outputs: OutputsConfig = field(default_factory=OutputsConfig)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["model"]["actions"] = list(self.model.actions)
        return data


def load_config(path: str | Path) -> OmegaConfig:
    config_path = Path(path)
    raw = yaml.safe_load(config_path.read_text()) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Config {config_path} must contain a YAML mapping.")

    run = _expect_mapping(raw.get("run"), "run")
    model = _expect_mapping(raw.get("model"), "model")
    outputs = raw.get("outputs", {})
    if outputs is None:
        outputs = {}
    outputs = _expect_mapping(outputs, "outputs")

    actions = tuple(str(action) for action in model.get("actions", ()))
    cfg = OmegaConfig(
        run=RunConfig(
            experiment_id=_nonempty_str(run.get("experiment_id"), "run.experiment_id"),
            ticks=_positive_int(run.get("ticks"), "run.ticks"),
        ),
        model=ModelConfig(
            agent_count=_min_int(model.get("agent_count"), "model.agent_count", minimum=2),
            actions=actions,
        ),
        outputs=OutputsConfig(
            write_manifest=bool(outputs.get("write_manifest", True)),
            write_metrics=bool(outputs.get("write_metrics", True)),
            write_events=bool(outputs.get("write_events", True)),
            write_summary=bool(outputs.get("write_summary", True)),
        ),
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


def _min_int(value: Any, name: str, minimum: int) -> int:
    parsed = _positive_int(value, name)
    if parsed < minimum:
        raise ValueError(f"Config value {name!r} must be at least {minimum}.")
    return parsed


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
