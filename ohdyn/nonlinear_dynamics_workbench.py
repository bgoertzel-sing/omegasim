"""Standalone nonlinear-dynamics diagnostic workbench.

This module is a smoke-scale diagnostic gate. It does not call the OmegaSim
agent simulator and does not create promotion evidence for prior runs.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ohdyn.analytic_delayed_map import (
    _delay_ticks,
    _pairwise_distances,
    _recurrence_rate,
    _sigmoid,
)


DEFAULT_CONFIG = Path("configs/nonlinear_dynamics_workbench.yaml")
DEFAULT_OUT_DIR = Path("runs/nonlinear_dynamics_workbench_seed1")
WORKBENCH_STATUS = "nonlinear_dynamics_workbench_smoke"
WORKBENCH_SCIENTIFIC_STATUS = "diagnostic_workbench_only_no_promotion_claim"
WORKBENCH_PANEL = (
    "low_gain_no_delay",
    "low_gain_delay",
    "active_reference",
    "high_gain_delay",
)
WORKBENCH_NULL_FAMILIES = (
    "no_delay_control",
    "linearized_response_control",
    "delay_shuffled_history_control",
    "state_shuffled_recurrence_surrogate",
    "phase_shuffled_recurrence_surrogate",
)
WORKBENCH_LABELS = (
    "fail_closed_unbounded_or_nonfinite",
    "fail_closed_trivial_saturation",
    "fail_closed_contracting_fixed_or_transient",
    "fail_closed_null_equivalent_recurrence",
    "fail_closed_noise_or_finite_horizon_irregularity",
    "candidate_noncontractive_bounded_diagnostic_only",
)
WORKBENCH_FIELDS = (
    "panel_id",
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
    "saturation_fraction",
    "lifted_history_min",
    "lifted_history_max",
    "lifted_history_range",
    "lifted_history_norm_mean",
    "recurrence_radius",
    "recurrence_rate",
    "state_shuffled_recurrence_rate",
    "state_shuffled_recurrence_delta",
    "phase_shuffled_recurrence_rate",
    "phase_shuffled_recurrence_delta",
    "no_delay_recurrence_delta",
    "linearized_response_recurrence_delta",
    "delay_shuffled_history_recurrence_delta",
    "finite_time_local_divergence",
    "paired_final_separation",
    "renormalized_lyapunov_estimate",
    "local_spectral_radius",
    "regime_label",
    "diagnostic_status",
)


def run_nonlinear_dynamics_workbench(
    *,
    config_path: str | Path = DEFAULT_CONFIG,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> list[dict[str, Any]]:
    """Run the preregistered four-row nonlinear-dynamics workbench."""

    config = _load_config(config_path)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    rows = _run_rows(config)
    _write_csv(output_path / "workbench_summary.csv", rows, WORKBENCH_FIELDS)
    (output_path / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=True))
    (output_path / "manifest.yaml").write_text(
        yaml.safe_dump(_manifest(config, rows), sort_keys=True)
    )
    (output_path / "summary.md").write_text(_summary(rows))
    return rows


def _run_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    run_config = config["run"]
    workbench_config = config["nonlinear_dynamics_workbench"]
    seed = int(run_config["seed"])
    ticks = int(run_config["ticks"])
    base_initial_state = np.array(
        workbench_config.get("initial_state", [0.42, 0.55, 0.35]),
        dtype=float,
    )
    perturbation_epsilon = float(workbench_config.get("perturbation_epsilon", 1e-5))
    panel_rows: list[dict[str, Any]] = []
    for panel in workbench_config["panel"]:
        controls = _controls(panel)
        delay_ticks = _delay_ticks(workbench_config, controls["delta"])
        noise = _noise_path(seed, ticks, controls["nu"])
        states, lifted = _simulate_condition(
            condition_id="active_delayed_nonlinear",
            initial_state=base_initial_state,
            ticks=ticks,
            controls=controls,
            delay_ticks=delay_ticks,
            noise=noise,
            seed=seed,
            active_delayed_sequence=None,
        )
        paired_states, _ = _simulate_condition(
            condition_id="active_delayed_nonlinear",
            initial_state=np.clip(base_initial_state + perturbation_epsilon, 0.0, 1.0),
            ticks=ticks,
            controls=controls,
            delay_ticks=delay_ticks,
            noise=noise,
            seed=seed,
            active_delayed_sequence=None,
        )
        null_recurrence = _null_recurrence_rates(
            initial_state=base_initial_state,
            ticks=ticks,
            controls=controls,
            delay_ticks=delay_ticks,
            noise=noise,
            seed=seed,
            active_delayed_sequence=lifted,
        )
        row = _diagnostic_row(
            panel_id=str(panel["panel_id"]),
            states=states,
            lifted=lifted,
            paired_states=paired_states,
            null_recurrence=null_recurrence,
            seed=seed,
            ticks=ticks,
            controls=controls,
            delay_ticks=delay_ticks,
            perturbation_epsilon=perturbation_epsilon,
            initial_state=base_initial_state,
            workbench_config=workbench_config,
        )
        panel_rows.append(row)
    return panel_rows


def _null_recurrence_rates(
    *,
    initial_state: np.ndarray,
    ticks: int,
    controls: dict[str, float],
    delay_ticks: int,
    noise: np.ndarray,
    seed: int,
    active_delayed_sequence: np.ndarray,
) -> dict[str, float]:
    rates: dict[str, float] = {}
    for condition_id, key in (
        ("no_delay", "no_delay"),
        ("linearized_response", "linearized_response"),
        ("delay_shuffled_history", "delay_shuffled_history"),
    ):
        states, _ = _simulate_condition(
            condition_id=condition_id,
            initial_state=initial_state,
            ticks=ticks,
            controls=controls,
            delay_ticks=delay_ticks,
            noise=noise,
            seed=seed,
            active_delayed_sequence=active_delayed_sequence,
        )
        _, rate = _recurrence_rate(states)
        rates[key] = float(rate)
    return rates


def _simulate_condition(
    *,
    condition_id: str,
    initial_state: np.ndarray,
    ticks: int,
    controls: dict[str, float],
    delay_ticks: int,
    noise: np.ndarray,
    seed: int,
    active_delayed_sequence: np.ndarray | None,
) -> tuple[np.ndarray, np.ndarray]:
    state = np.clip(initial_state.astype(float), 0.0, 1.0)
    history: list[np.ndarray] = []
    states: list[np.ndarray] = []
    lifted: list[np.ndarray] = []
    effective_delay = 0 if condition_id == "no_delay" else delay_ticks
    relaxation_weight = 1.0 / (1.0 + max(controls["delta"], 0.0) + 1.0)
    memory_update = 1.0 / (1.0 + max(controls["mu"], 1e-9))
    memory_persistence = 1.0 - memory_update
    center_state = np.clip(initial_state.astype(float), 0.0, 1.0)
    center_drive = _drive(center_state, controls)
    center_response = math.tanh(center_drive)
    center_slope = 1.0 - center_response * center_response
    shuffled_delayed = None
    if condition_id == "delay_shuffled_history":
        if active_delayed_sequence is None:
            raise ValueError("delay_shuffled_history requires an active delayed sequence.")
        rng = np.random.default_rng(np.random.SeedSequence([seed, 0xD7A1]))
        shuffled_delayed = active_delayed_sequence[rng.permutation(len(active_delayed_sequence))]

    for tick in range(ticks):
        if shuffled_delayed is not None:
            delayed = shuffled_delayed[tick]
        elif effective_delay > 0 and len(history) >= effective_delay:
            delayed = history[-effective_delay]
        else:
            delayed = state
        next_state = _step(
            state=state,
            delayed=delayed,
            tick=tick,
            seed=seed,
            controls=controls,
            noise_tick=noise[tick],
            relaxation_weight=relaxation_weight,
            memory_persistence=memory_persistence,
            memory_update=memory_update,
            condition_id=condition_id,
            center_drive=center_drive,
            center_response=center_response,
            center_slope=center_slope,
        )
        lifted.append(delayed.copy())
        history.append(state.copy())
        state = next_state
        states.append(state.copy())
    return np.vstack(states), np.vstack(lifted)


def _step(
    *,
    state: np.ndarray,
    delayed: np.ndarray,
    tick: int,
    seed: int,
    controls: dict[str, float],
    noise_tick: np.ndarray,
    relaxation_weight: float,
    memory_persistence: float,
    memory_update: float,
    condition_id: str,
    center_drive: float,
    center_response: float,
    center_slope: float,
) -> np.ndarray:
    drive = _drive(delayed, controls)
    if condition_id == "linearized_response":
        nonlinear_drive = center_response + center_slope * (drive - center_drive)
    else:
        nonlinear_drive = math.tanh(drive)
    demand_wave = math.sin((tick + seed) / 7.0)
    prediction_target = _sigmoid(
        nonlinear_drive
        + 0.35 * (state[2] - 0.5)
        - 0.25 * state[1]
        + 0.10 * demand_wave
        + noise_tick[0]
    )
    prediction_spend = min(0.65, max(0.0, prediction_target))
    lost_work_fraction = min(0.60, 0.35 * prediction_spend)
    resource_target = _sigmoid(
        0.70
        + 0.25 * demand_wave
        - lost_work_fraction
        - 0.30 * state[0]
        + controls["kappa"] * (delayed[1] - 0.5)
        + noise_tick[1]
    )
    memory_target = np.clip(
        0.55 * state[0] + 0.25 * delayed[0] + 0.20 * (1.0 - state[1]) + noise_tick[2],
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
    return np.clip(next_state, 0.0, 1.0)


def _diagnostic_row(
    *,
    panel_id: str,
    states: np.ndarray,
    lifted: np.ndarray,
    paired_states: np.ndarray,
    null_recurrence: dict[str, float],
    seed: int,
    ticks: int,
    controls: dict[str, float],
    delay_ticks: int,
    perturbation_epsilon: float,
    initial_state: np.ndarray,
    workbench_config: dict[str, Any],
) -> dict[str, Any]:
    state_min = float(states.min())
    state_max = float(states.max())
    state_range = state_max - state_min
    finite = bool(np.all(np.isfinite(states)))
    bounded = bool(finite and state_min >= 0.0 and state_max <= 1.0)
    nontrivial = state_range >= float(workbench_config.get("nontrivial_range_min", 0.01))
    saturation_epsilon = float(workbench_config.get("saturation_epsilon", 0.02))
    saturation_fraction = float(
        np.mean((states <= saturation_epsilon) | (states >= 1.0 - saturation_epsilon))
    )
    recurrence_radius, recurrence_rate = _recurrence_rate(states)
    state_shuffle_rate = _state_shuffled_recurrence_rate(states, seed, panel_id, recurrence_radius)
    phase_shuffle_rate = _phase_shuffled_recurrence_rate(states, seed, panel_id, recurrence_radius)
    initial_sep = float(np.linalg.norm(paired_states[0] - states[0]))
    final_sep = float(np.linalg.norm(paired_states[-1] - states[-1]))
    divergence = math.log(max(final_sep, 1e-12) / max(initial_sep, 1e-12)) / max(ticks - 1, 1)
    lyapunov = _renormalized_lyapunov_estimate(
        initial_state=initial_state,
        ticks=ticks,
        controls=controls,
        delay_ticks=delay_ticks,
        seed=seed,
        nu=controls["nu"],
        epsilon=perturbation_epsilon,
        interval=int(workbench_config.get("renormalization_interval", 8)),
    )
    spectral_radius = _local_spectral_radius(
        initial_state=initial_state,
        controls=controls,
        seed=seed,
        epsilon=max(perturbation_epsilon, 1e-6),
    )
    lifted_norms = np.linalg.norm(lifted, axis=1)
    no_delay_delta = recurrence_rate - null_recurrence["no_delay"]
    linear_delta = recurrence_rate - null_recurrence["linearized_response"]
    delay_shuffle_delta = recurrence_rate - null_recurrence["delay_shuffled_history"]
    state_shuffle_delta = recurrence_rate - state_shuffle_rate
    phase_shuffle_delta = recurrence_rate - phase_shuffle_rate
    regime_label = _regime_label(
        bounded=bounded and nontrivial,
        finite=finite,
        saturation_fraction=saturation_fraction,
        finite_time_divergence=divergence,
        lyapunov=lyapunov,
        spectral_radius=spectral_radius,
        recurrence_deltas=[
            no_delay_delta,
            linear_delta,
            delay_shuffle_delta,
            state_shuffle_delta,
            phase_shuffle_delta,
        ],
        saturation_max=float(workbench_config.get("saturation_fraction_max", 0.05)),
    )
    return {
        "panel_id": panel_id,
        "seed": seed,
        "ticks": ticks,
        **{key: round(value, 6) for key, value in controls.items()},
        "delay_ticks": delay_ticks,
        "state_min": round(state_min, 6),
        "state_max": round(state_max, 6),
        "state_range": round(state_range, 6),
        "boundedness_status": "pass" if bounded and nontrivial else "fail_closed",
        "saturation_fraction": round(saturation_fraction, 6),
        "lifted_history_min": round(float(lifted.min()), 6),
        "lifted_history_max": round(float(lifted.max()), 6),
        "lifted_history_range": round(float(lifted.max() - lifted.min()), 6),
        "lifted_history_norm_mean": round(float(np.mean(lifted_norms)), 6),
        "recurrence_radius": round(float(recurrence_radius), 6),
        "recurrence_rate": round(float(recurrence_rate), 6),
        "state_shuffled_recurrence_rate": round(float(state_shuffle_rate), 6),
        "state_shuffled_recurrence_delta": round(float(state_shuffle_delta), 6),
        "phase_shuffled_recurrence_rate": round(float(phase_shuffle_rate), 6),
        "phase_shuffled_recurrence_delta": round(float(phase_shuffle_delta), 6),
        "no_delay_recurrence_delta": round(float(no_delay_delta), 6),
        "linearized_response_recurrence_delta": round(float(linear_delta), 6),
        "delay_shuffled_history_recurrence_delta": round(float(delay_shuffle_delta), 6),
        "finite_time_local_divergence": round(float(divergence), 6),
        "paired_final_separation": round(final_sep, 9),
        "renormalized_lyapunov_estimate": round(float(lyapunov), 6),
        "local_spectral_radius": round(float(spectral_radius), 6),
        "regime_label": regime_label,
        "diagnostic_status": WORKBENCH_STATUS,
    }


def _renormalized_lyapunov_estimate(
    *,
    initial_state: np.ndarray,
    ticks: int,
    controls: dict[str, float],
    delay_ticks: int,
    seed: int,
    nu: float,
    epsilon: float,
    interval: int,
) -> float:
    noise = _noise_path(seed, ticks, nu)
    base_state = np.clip(initial_state.astype(float), 0.0, 1.0)
    paired_state = np.clip(base_state + epsilon, 0.0, 1.0)
    base_history: list[np.ndarray] = []
    paired_history: list[np.ndarray] = []
    logs: list[float] = []
    interval = max(1, interval)
    relaxation_weight = 1.0 / (1.0 + max(controls["delta"], 0.0) + 1.0)
    memory_update = 1.0 / (1.0 + max(controls["mu"], 1e-9))
    memory_persistence = 1.0 - memory_update
    center_drive = _drive(base_state, controls)
    center_response = math.tanh(center_drive)
    center_slope = 1.0 - center_response * center_response
    for tick in range(ticks):
        base_delayed = (
            base_history[-delay_ticks]
            if delay_ticks > 0 and len(base_history) >= delay_ticks
            else base_state
        )
        paired_delayed = (
            paired_history[-delay_ticks]
            if delay_ticks > 0 and len(paired_history) >= delay_ticks
            else paired_state
        )
        next_base = _step(
            state=base_state,
            delayed=base_delayed,
            tick=tick,
            seed=seed,
            controls=controls,
            noise_tick=noise[tick],
            relaxation_weight=relaxation_weight,
            memory_persistence=memory_persistence,
            memory_update=memory_update,
            condition_id="active_delayed_nonlinear",
            center_drive=center_drive,
            center_response=center_response,
            center_slope=center_slope,
        )
        next_paired = _step(
            state=paired_state,
            delayed=paired_delayed,
            tick=tick,
            seed=seed,
            controls=controls,
            noise_tick=noise[tick],
            relaxation_weight=relaxation_weight,
            memory_persistence=memory_persistence,
            memory_update=memory_update,
            condition_id="active_delayed_nonlinear",
            center_drive=center_drive,
            center_response=center_response,
            center_slope=center_slope,
        )
        base_history.append(base_state.copy())
        paired_history.append(paired_state.copy())
        base_state = next_base
        paired_state = next_paired
        if (tick + 1) % interval == 0:
            delta = paired_state - base_state
            separation = float(np.linalg.norm(delta))
            logs.append(math.log(max(separation, 1e-12) / max(epsilon, 1e-12)))
            if separation > 0.0:
                paired_state = np.clip(base_state + (epsilon / separation) * delta, 0.0, 1.0)
            else:
                paired_state = np.clip(base_state + epsilon, 0.0, 1.0)
    if not logs:
        return 0.0
    return float(sum(logs) / (len(logs) * interval))


def _local_spectral_radius(
    *,
    initial_state: np.ndarray,
    controls: dict[str, float],
    seed: int,
    epsilon: float,
) -> float:
    relaxation_weight = 1.0 / (1.0 + max(controls["delta"], 0.0) + 1.0)
    memory_update = 1.0 / (1.0 + max(controls["mu"], 1e-9))
    memory_persistence = 1.0 - memory_update
    noise_tick = np.zeros(3, dtype=float)
    center_drive = _drive(initial_state, controls)
    center_response = math.tanh(center_drive)
    center_slope = 1.0 - center_response * center_response

    def evaluate(state: np.ndarray) -> np.ndarray:
        return _step(
            state=state,
            delayed=state,
            tick=0,
            seed=seed,
            controls=controls,
            noise_tick=noise_tick,
            relaxation_weight=relaxation_weight,
            memory_persistence=memory_persistence,
            memory_update=memory_update,
            condition_id="active_delayed_nonlinear",
            center_drive=center_drive,
            center_response=center_response,
            center_slope=center_slope,
        )

    columns: list[np.ndarray] = []
    for index in range(len(initial_state)):
        delta = np.zeros_like(initial_state)
        delta[index] = epsilon
        plus = evaluate(np.clip(initial_state + delta, 0.0, 1.0))
        minus = evaluate(np.clip(initial_state - delta, 0.0, 1.0))
        columns.append((plus - minus) / (2.0 * epsilon))
    jacobian = np.column_stack(columns)
    eigenvalues = np.linalg.eigvals(jacobian)
    return float(np.max(np.abs(eigenvalues)))


def _state_shuffled_recurrence_rate(
    states: np.ndarray,
    seed: int,
    panel_id: str,
    radius: float,
) -> float:
    if radius <= 0.0:
        return 0.0
    salt = sum(ord(char) for char in panel_id)
    shuffled = states.copy()
    rng = np.random.default_rng(np.random.SeedSequence([seed, 0xA11A, salt]))
    for column in range(shuffled.shape[1]):
        shuffled[:, column] = shuffled[rng.permutation(shuffled.shape[0]), column]
    return _recurrence_at_radius(shuffled, radius)


def _phase_shuffled_recurrence_rate(
    states: np.ndarray,
    seed: int,
    panel_id: str,
    radius: float,
) -> float:
    if radius <= 0.0:
        return 0.0
    salt = sum(ord(char) for char in panel_id)
    rng = np.random.default_rng(np.random.SeedSequence([seed, 0xF4A5, salt]))
    shuffled = np.empty_like(states)
    for column in range(states.shape[1]):
        centered = states[:, column] - float(np.mean(states[:, column]))
        spectrum = np.fft.rfft(centered)
        if len(spectrum) > 2:
            phases = rng.uniform(0.0, 2.0 * math.pi, size=len(spectrum) - 2)
            spectrum[1:-1] *= np.exp(1j * phases)
        shuffled[:, column] = np.fft.irfft(spectrum, n=len(centered)) + float(
            np.mean(states[:, column])
        )
    return _recurrence_at_radius(shuffled, radius)


def _recurrence_at_radius(states: np.ndarray, radius: float) -> float:
    distances = _pairwise_distances(states)
    nonzero = distances[distances > 0.0]
    if len(nonzero) == 0:
        return 0.0
    return float(np.mean(nonzero <= radius))


def _regime_label(
    *,
    bounded: bool,
    finite: bool,
    saturation_fraction: float,
    finite_time_divergence: float,
    lyapunov: float,
    spectral_radius: float,
    recurrence_deltas: list[float],
    saturation_max: float,
) -> str:
    if not finite or not bounded:
        return "fail_closed_unbounded_or_nonfinite"
    if saturation_fraction > saturation_max:
        return "fail_closed_trivial_saturation"
    same_direction = all(delta > 0.0 for delta in recurrence_deltas) or all(
        delta < 0.0 for delta in recurrence_deltas
    )
    if lyapunov > 0.0 and spectral_radius > 1.0 and same_direction:
        return "candidate_noncontractive_bounded_diagnostic_only"
    if spectral_radius <= 1.0 and lyapunov <= 0.0 and finite_time_divergence <= 0.0:
        return "fail_closed_contracting_fixed_or_transient"
    if not same_direction:
        return "fail_closed_null_equivalent_recurrence"
    return "fail_closed_noise_or_finite_horizon_irregularity"


def _drive(delayed: np.ndarray, controls: dict[str, float]) -> float:
    return float(
        controls["rho"] * (delayed[0] - 0.5)
        + controls["kappa"] * (delayed[2] - delayed[1])
    )


def _controls(panel: dict[str, Any]) -> dict[str, float]:
    return {
        "rho": float(panel["rho"]),
        "delta": float(panel["delta"]),
        "mu": float(panel["mu"]),
        "kappa": float(panel["kappa"]),
        "nu": float(panel["nu"]),
    }


def _noise_path(seed: int, ticks: int, nu: float) -> np.ndarray:
    rng = np.random.default_rng(np.random.SeedSequence([seed, 0xBEE5]))
    return rng.normal(loc=0.0, scale=max(nu, 0.0), size=(ticks, 3))


def _load_config(config_path: str | Path) -> dict[str, Any]:
    config = yaml.safe_load(Path(config_path).read_text())
    if (
        not isinstance(config, dict)
        or "run" not in config
        or "nonlinear_dynamics_workbench" not in config
    ):
        raise ValueError(f"{config_path} must define run and nonlinear_dynamics_workbench.")
    workbench_config = config["nonlinear_dynamics_workbench"]
    panel = workbench_config.get("panel", [])
    panel_ids = tuple(row.get("panel_id") for row in panel if isinstance(row, dict))
    if panel_ids != WORKBENCH_PANEL:
        raise ValueError(f"{config_path} must define exactly the preregistered workbench panel.")
    nulls = tuple(workbench_config.get("null_families", []))
    if nulls != WORKBENCH_NULL_FAMILIES:
        raise ValueError(f"{config_path} must define exactly the preregistered null families.")
    labels = tuple(workbench_config.get("regime_labels", []))
    if labels != WORKBENCH_LABELS:
        raise ValueError(f"{config_path} must define exactly the preregistered regime labels.")
    return config


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    if (output_path / "workbench_summary.csv").exists():
        raise FileExistsError(
            f"Output path {output_path} already contains nonlinear workbench artifacts."
        )


def _manifest(config: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "experiment_id": config["run"]["experiment_id"],
        "seed": int(config["run"]["seed"]),
        "ticks": int(config["run"]["ticks"]),
        "status": WORKBENCH_STATUS,
        "scientific_status": WORKBENCH_SCIENTIFIC_STATUS,
        "preregistration": "docs/nonlinear_dynamics_workbench_preregistration.md",
        "panel": list(WORKBENCH_PANEL),
        "rows": len(rows),
        "dimensionless_axes": ["rho", "delta", "mu", "kappa", "nu"],
        "null_families": list(WORKBENCH_NULL_FAMILIES),
        "regime_labels": list(WORKBENCH_LABELS),
        "diagnostic_only_boundary": (
            "candidate rows are diagnostic only and do not authorize attractor, "
            "lobe, semantic-dynamics, simulator-mechanics, or promotion claims"
        ),
        "locks": [
            "seed",
            "ticks",
            "initial_state",
            "perturbation_epsilon",
            "noise_path",
            "clipping_bounds",
            "panel",
        ],
        "artifacts": [
            "config.yaml",
            "manifest.yaml",
            "workbench_summary.csv",
            "summary.md",
        ],
        "no_simulator_artifacts": ["metrics.csv", "events.csv"],
    }


def _summary(rows: list[dict[str, Any]]) -> str:
    label_counts = {label: 0 for label in WORKBENCH_LABELS}
    for row in rows:
        label_counts[str(row["regime_label"])] += 1
    label_lines = [f"- `{label}`: `{count}`" for label, count in label_counts.items()]
    return "\n".join(
        [
            "# Nonlinear-Dynamics Workbench",
            "",
            f"- Status: `{WORKBENCH_STATUS}`",
            f"- Scientific status: `{WORKBENCH_SCIENTIFIC_STATUS}`",
            f"- Panel rows: `{len(rows)}`",
            "",
            "## Regime Labels",
            "",
            *label_lines,
            "",
            "This standalone workbench writes summary diagnostics and manifest",
            "artifacts only. It does not write per-tick simulator metrics or events,",
            "and it does not support attractor, lobe, semantic-dynamics, causal",
            "collective-intelligence, or promotion claims.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the preregistered nonlinear-dynamics workbench."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Workbench config.")
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="Output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_nonlinear_dynamics_workbench(config_path=args.config, out_dir=args.out)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
