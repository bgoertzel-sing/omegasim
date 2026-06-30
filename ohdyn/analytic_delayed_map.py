"""Analytic delayed resource-bounded prediction map.

This module is a small mathematical sandbox. It does not call the OmegaSim
agent simulator and does not create A5/A7 promotion evidence.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import numpy as np
import yaml


DEFAULT_CONFIG = Path("configs/analytic_delayed_map_smoke.yaml")
DEFAULT_OUT_DIR = Path("runs/analytic_delayed_map_smoke_seed1")
MAP_STATUS = "analytic_delayed_resource_bounded_map_smoke"
SCIENTIFIC_STATUS = "diagnostic_sandbox_only_no_attractor_or_lobe_claim"
METRIC_FIELDS = (
    "tick",
    "seed",
    "rho",
    "delta",
    "mu",
    "kappa",
    "nu",
    "delay_ticks",
    "prediction_state",
    "resource_state",
    "memory_state",
    "delayed_prediction_state",
    "delayed_resource_state",
    "delayed_memory_state",
    "prediction_spend",
    "lost_work_fraction",
    "drift_norm",
    "noise_norm",
)
DIAGNOSTIC_FIELDS = (
    "seed",
    "ticks",
    "rho",
    "delta",
    "mu",
    "kappa",
    "nu",
    "delay_ticks",
    "state_min",
    "state_max",
    "state_range",
    "boundedness_status",
    "recurrence_radius",
    "recurrence_rate",
    "surrogate_recurrence_rate",
    "recurrence_surrogate_delta",
    "finite_time_local_divergence",
    "paired_final_separation",
    "diagnostic_status",
)


def run_analytic_delayed_map(
    *,
    config_path: str | Path = DEFAULT_CONFIG,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> dict[str, Any]:
    """Run one deterministic analytic map smoke and write artifacts."""

    config = _load_config(config_path)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    metrics, diagnostics = simulate_and_diagnose(config)
    (output_path / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=True))
    _write_csv(output_path / "metrics.csv", metrics, METRIC_FIELDS)
    _write_csv(output_path / "diagnostics.csv", [diagnostics], DIAGNOSTIC_FIELDS)
    (output_path / "manifest.yaml").write_text(
        yaml.safe_dump(_manifest(config, len(metrics)), sort_keys=True)
    )
    (output_path / "summary.md").write_text(_summary(diagnostics))
    return diagnostics


def simulate_and_diagnose(config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    run_config = config["run"]
    map_config = config["analytic_delayed_map"]
    seed = int(run_config["seed"])
    ticks = int(run_config["ticks"])
    controls = _controls(map_config)
    delay_ticks = _delay_ticks(map_config, controls["delta"])
    initial_state = np.array(map_config.get("initial_state", [0.42, 0.55, 0.35]), dtype=float)
    noise = _noise_path(seed, ticks, controls["nu"])

    states, metrics = _simulate_path(initial_state, ticks, controls, delay_ticks, noise, seed)
    paired_initial = np.clip(
        initial_state + float(map_config.get("perturbation_epsilon", 1e-5)),
        0.0,
        1.0,
    )
    paired_states, _ = _simulate_path(paired_initial, ticks, controls, delay_ticks, noise, seed)
    diagnostics = _diagnostics(states, paired_states, seed, ticks, controls, delay_ticks, map_config)
    return metrics, diagnostics


def _simulate_path(
    initial_state: np.ndarray,
    ticks: int,
    controls: dict[str, float],
    delay_ticks: int,
    noise: np.ndarray,
    seed: int,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    state = np.clip(initial_state.astype(float), 0.0, 1.0)
    history: list[np.ndarray] = []
    states: list[np.ndarray] = []
    rows: list[dict[str, Any]] = []
    relaxation_weight = 1.0 / (1.0 + max(controls["delta"], 0.0) + 1.0)
    memory_update = 1.0 / (1.0 + max(controls["mu"], 1e-9))
    memory_persistence = 1.0 - memory_update

    for tick in range(ticks):
        delayed = history[-delay_ticks] if delay_ticks > 0 and len(history) >= delay_ticks else state
        nonlinear_drive = math.tanh(
            controls["rho"] * (delayed[0] - 0.5)
            + controls["kappa"] * (delayed[2] - delayed[1])
        )
        demand_wave = math.sin((tick + seed) / 7.0)
        prediction_target = _sigmoid(
            nonlinear_drive
            + 0.35 * (state[2] - 0.5)
            - 0.25 * state[1]
            + 0.10 * demand_wave
            + noise[tick, 0]
        )
        prediction_spend = min(0.65, max(0.0, prediction_target))
        lost_work_fraction = min(0.60, 0.35 * prediction_spend)
        resource_target = _sigmoid(
            0.70
            + 0.25 * demand_wave
            - lost_work_fraction
            - 0.30 * state[0]
            + controls["kappa"] * (delayed[1] - 0.5)
            + noise[tick, 1]
        )
        memory_target = np.clip(
            0.55 * state[0] + 0.25 * delayed[0] + 0.20 * (1.0 - state[1]) + noise[tick, 2],
            0.0,
            1.0,
        )
        next_state = np.array(
            [
                (1.0 - relaxation_weight) * state[0] + relaxation_weight * prediction_target,
                (1.0 - relaxation_weight) * state[1] + relaxation_weight * resource_target,
                memory_persistence * state[2] + memory_update * memory_target,
            ],
            dtype=float,
        )
        next_state = np.clip(next_state, 0.0, 1.0)
        drift_norm = float(np.linalg.norm(next_state - state))
        noise_norm = float(np.linalg.norm(noise[tick]))
        rows.append(
            {
                "tick": tick,
                "seed": seed,
                **{key: round(value, 6) for key, value in controls.items()},
                "delay_ticks": delay_ticks,
                "prediction_state": round(float(next_state[0]), 6),
                "resource_state": round(float(next_state[1]), 6),
                "memory_state": round(float(next_state[2]), 6),
                "delayed_prediction_state": round(float(delayed[0]), 6),
                "delayed_resource_state": round(float(delayed[1]), 6),
                "delayed_memory_state": round(float(delayed[2]), 6),
                "prediction_spend": round(float(prediction_spend), 6),
                "lost_work_fraction": round(float(lost_work_fraction), 6),
                "drift_norm": round(drift_norm, 6),
                "noise_norm": round(noise_norm, 6),
            }
        )
        history.append(state.copy())
        state = next_state
        states.append(state.copy())
    return np.vstack(states), rows


def _diagnostics(
    states: np.ndarray,
    paired_states: np.ndarray,
    seed: int,
    ticks: int,
    controls: dict[str, float],
    delay_ticks: int,
    map_config: dict[str, Any],
) -> dict[str, Any]:
    state_min = float(states.min())
    state_max = float(states.max())
    state_range = state_max - state_min
    bounded = bool(np.all(np.isfinite(states)) and state_min >= 0.0 and state_max <= 1.0)
    nontrivial = state_range >= float(map_config.get("nontrivial_range_min", 0.01))
    recurrence_radius, recurrence_rate = _recurrence_rate(states)
    surrogate_rate = _surrogate_recurrence_rate(states, seed, recurrence_radius)
    initial_sep = float(np.linalg.norm(paired_states[0] - states[0]))
    final_sep = float(np.linalg.norm(paired_states[-1] - states[-1]))
    divergence = math.log(max(final_sep, 1e-12) / max(initial_sep, 1e-12)) / max(ticks - 1, 1)
    return {
        "seed": seed,
        "ticks": ticks,
        **{key: round(value, 6) for key, value in controls.items()},
        "delay_ticks": delay_ticks,
        "state_min": round(state_min, 6),
        "state_max": round(state_max, 6),
        "state_range": round(state_range, 6),
        "boundedness_status": "pass" if bounded and nontrivial else "fail_closed",
        "recurrence_radius": round(float(recurrence_radius), 6),
        "recurrence_rate": round(float(recurrence_rate), 6),
        "surrogate_recurrence_rate": round(float(surrogate_rate), 6),
        "recurrence_surrogate_delta": round(float(recurrence_rate - surrogate_rate), 6),
        "finite_time_local_divergence": round(float(divergence), 6),
        "paired_final_separation": round(final_sep, 9),
        "diagnostic_status": MAP_STATUS,
    }


def _recurrence_rate(states: np.ndarray) -> tuple[float, float]:
    distances = _pairwise_distances(states)
    nonzero = distances[distances > 0.0]
    if len(nonzero) == 0:
        return 0.0, 0.0
    radius = float(np.quantile(nonzero, 0.10))
    return radius, float(np.mean(nonzero <= radius))


def _surrogate_recurrence_rate(states: np.ndarray, seed: int, radius: float) -> float:
    shuffled = states.copy()
    rng = np.random.default_rng(np.random.SeedSequence([seed, 0xA11A]))
    for column in range(shuffled.shape[1]):
        shuffled[:, column] = shuffled[rng.permutation(shuffled.shape[0]), column]
    distances = _pairwise_distances(shuffled)
    nonzero = distances[distances > 0.0]
    if len(nonzero) == 0:
        return 0.0
    return float(np.mean(nonzero <= radius))


def _pairwise_distances(states: np.ndarray) -> np.ndarray:
    deltas = states[:, None, :] - states[None, :, :]
    return np.linalg.norm(deltas, axis=2)


def _controls(map_config: dict[str, Any]) -> dict[str, float]:
    return {
        "rho": float(map_config["rho"]),
        "delta": float(map_config["delta"]),
        "mu": float(map_config["mu"]),
        "kappa": float(map_config["kappa"]),
        "nu": float(map_config["nu"]),
    }


def _delay_ticks(map_config: dict[str, Any], delta: float) -> int:
    if "delay_ticks" in map_config:
        return int(map_config["delay_ticks"])
    relaxation_ticks = int(map_config.get("relaxation_time_ticks", 8))
    return max(0, int(round(delta * relaxation_ticks)))


def _noise_path(seed: int, ticks: int, nu: float) -> np.ndarray:
    rng = np.random.default_rng(np.random.SeedSequence([seed, 0xA17A]))
    return rng.normal(loc=0.0, scale=max(nu, 0.0), size=(ticks, 3))


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def _load_config(config_path: str | Path) -> dict[str, Any]:
    config = yaml.safe_load(Path(config_path).read_text())
    if not isinstance(config, dict) or "run" not in config or "analytic_delayed_map" not in config:
        raise ValueError(f"{config_path} must define run and analytic_delayed_map sections.")
    return config


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    if (output_path / "metrics.csv").exists() or (output_path / "diagnostics.csv").exists():
        raise FileExistsError(
            f"Output path {output_path} already contains analytic delayed-map artifacts."
        )


def _manifest(config: dict[str, Any], metrics_rows: int) -> dict[str, Any]:
    return {
        "experiment_id": config["run"]["experiment_id"],
        "seed": int(config["run"]["seed"]),
        "ticks": int(config["run"]["ticks"]),
        "status": MAP_STATUS,
        "scientific_status": SCIENTIFIC_STATUS,
        "dimensionless_controls": ["rho", "delta", "mu", "kappa", "nu"],
        "metrics_rows": metrics_rows,
        "artifacts": [
            "config.yaml",
            "manifest.yaml",
            "metrics.csv",
            "diagnostics.csv",
            "summary.md",
        ],
        "config": config,
    }


def _summary(diagnostics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Analytic Delayed Resource-Bounded Map Smoke",
            "",
            f"- Status: `{MAP_STATUS}`",
            f"- Scientific status: `{SCIENTIFIC_STATUS}`",
            f"- Seed: `{diagnostics['seed']}`",
            f"- Ticks: `{diagnostics['ticks']}`",
            f"- Controls: rho={diagnostics['rho']}, delta={diagnostics['delta']}, "
            f"mu={diagnostics['mu']}, kappa={diagnostics['kappa']}, nu={diagnostics['nu']}",
            f"- Boundedness: `{diagnostics['boundedness_status']}`",
            f"- Recurrence delta vs shuffled surrogate: `{diagnostics['recurrence_surrogate_delta']}`",
            f"- Finite-time local divergence: `{diagnostics['finite_time_local_divergence']}`",
            "",
            "This is a standalone analytic sandbox. It does not run simulator mechanics,",
            "perform a parameter sweep, or support lobe-like or strange-attractor-like claims.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the analytic delayed resource-bounded prediction map smoke."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Analytic map config.")
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="Output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_analytic_delayed_map(config_path=args.config, out_dir=args.out)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
