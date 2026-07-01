"""Standalone null gate for the analytic delayed resource-bounded map."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ohdyn.analytic_delayed_map import (
    SCIENTIFIC_STATUS,
    _controls,
    _delay_ticks,
    _noise_path,
    _pairwise_distances,
    _recurrence_rate,
    _sigmoid,
)


DEFAULT_CONFIG = Path("configs/analytic_delayed_map_null_gate.yaml")
DEFAULT_OUT_DIR = Path("runs/analytic_delayed_map_null_gate_seed1")
NULL_GATE_STATUS = "analytic_delayed_map_refinement_null_gate"
NULL_GATE_SCIENTIFIC_STATUS = "diagnostic_null_gate_only_no_promotion_claim"
NULL_GATE_CONDITIONS = (
    "active_delayed_nonlinear",
    "no_delay",
    "linearized_response",
    "delay_shuffled_history",
)
NULL_GATE_FIELDS = (
    "condition_id",
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
    "surrogate_recurrence_rate",
    "recurrence_surrogate_delta",
    "finite_time_local_divergence",
    "paired_final_separation",
    "active_vs_null_recurrence_delta",
    "active_vs_null_divergence_delta",
    "condition_status",
    "diagnostic_status",
)


def run_analytic_delayed_map_null_gate(
    *,
    config_path: str | Path = DEFAULT_CONFIG,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> list[dict[str, Any]]:
    """Run the four preregistered analytic delayed-map null conditions."""

    config = _load_config(config_path)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    rows = _run_rows(config)
    _write_csv(output_path / "null_gate_summary.csv", rows, NULL_GATE_FIELDS)
    (output_path / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=True))
    (output_path / "manifest.yaml").write_text(
        yaml.safe_dump(_manifest(config, rows), sort_keys=True)
    )
    (output_path / "summary.md").write_text(_summary(rows))
    return rows


def _run_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    run_config = config["run"]
    map_config = config["analytic_delayed_map"]
    seed = int(run_config["seed"])
    ticks = int(run_config["ticks"])
    controls = _controls(map_config)
    delay_ticks = _delay_ticks(map_config, controls["delta"])
    initial_state = np.array(map_config.get("initial_state", [0.42, 0.55, 0.35]), dtype=float)
    perturbation_epsilon = float(map_config.get("perturbation_epsilon", 1e-5))
    noise = _noise_path(seed, ticks, controls["nu"])

    _, active_lifted = _simulate_condition(
        condition_id="active_delayed_nonlinear",
        initial_state=initial_state,
        ticks=ticks,
        controls=controls,
        delay_ticks=delay_ticks,
        noise=noise,
        seed=seed,
        active_delayed_sequence=None,
    )
    _, active_paired = _condition_diagnostics(
        condition_id="active_delayed_nonlinear",
        initial_state=initial_state,
        perturbation_epsilon=perturbation_epsilon,
        ticks=ticks,
        controls=controls,
        delay_ticks=delay_ticks,
        noise=noise,
        seed=seed,
        map_config=map_config,
        active_delayed_sequence=None,
    )
    active_delayed_sequence = active_lifted.copy()

    condition_rows: list[dict[str, Any]] = []
    for condition_id in NULL_GATE_CONDITIONS:
        if condition_id == "active_delayed_nonlinear":
            row = active_paired
        else:
            _, row = _condition_diagnostics(
                condition_id=condition_id,
                initial_state=initial_state,
                perturbation_epsilon=perturbation_epsilon,
                ticks=ticks,
                controls=controls,
                delay_ticks=delay_ticks,
                noise=noise,
                seed=seed,
                map_config=map_config,
                active_delayed_sequence=active_delayed_sequence,
            )
        condition_rows.append(row)

    active_row = condition_rows[0]
    for row in condition_rows:
        row["active_vs_null_recurrence_delta"] = round(
            float(active_row["recurrence_surrogate_delta"])
            - float(row["recurrence_surrogate_delta"]),
            6,
        )
        row["active_vs_null_divergence_delta"] = round(
            float(active_row["finite_time_local_divergence"])
            - float(row["finite_time_local_divergence"]),
            6,
        )
    for row in condition_rows:
        row["condition_status"] = _condition_status(condition_rows, row)
    return condition_rows


def _condition_diagnostics(
    *,
    condition_id: str,
    initial_state: np.ndarray,
    perturbation_epsilon: float,
    ticks: int,
    controls: dict[str, float],
    delay_ticks: int,
    noise: np.ndarray,
    seed: int,
    map_config: dict[str, Any],
    active_delayed_sequence: np.ndarray | None,
) -> tuple[np.ndarray, dict[str, Any]]:
    states, lifted = _simulate_condition(
        condition_id=condition_id,
        initial_state=initial_state,
        ticks=ticks,
        controls=controls,
        delay_ticks=delay_ticks,
        noise=noise,
        seed=seed,
        active_delayed_sequence=active_delayed_sequence,
    )
    paired_initial = np.clip(initial_state + perturbation_epsilon, 0.0, 1.0)
    paired_states, _ = _simulate_condition(
        condition_id=condition_id,
        initial_state=paired_initial,
        ticks=ticks,
        controls=controls,
        delay_ticks=delay_ticks,
        noise=noise,
        seed=seed,
        active_delayed_sequence=active_delayed_sequence,
    )
    return states, _diagnostic_row(
        condition_id=condition_id,
        states=states,
        lifted=lifted,
        paired_states=paired_states,
        seed=seed,
        ticks=ticks,
        controls=controls,
        delay_ticks=0 if condition_id == "no_delay" else delay_ticks,
        map_config=map_config,
    )


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
        rng = np.random.default_rng(np.random.SeedSequence([seed, 0xD31A]))
        shuffled_delayed = active_delayed_sequence[rng.permutation(len(active_delayed_sequence))]

    for tick in range(ticks):
        if shuffled_delayed is not None:
            delayed = shuffled_delayed[tick]
        elif effective_delay > 0 and len(history) >= effective_delay:
            delayed = history[-effective_delay]
        else:
            delayed = state

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
        lifted.append(delayed.copy())
        history.append(state.copy())
        state = next_state
        states.append(state.copy())
    return np.vstack(states), np.vstack(lifted)


def _drive(delayed: np.ndarray, controls: dict[str, float]) -> float:
    return float(
        controls["rho"] * (delayed[0] - 0.5)
        + controls["kappa"] * (delayed[2] - delayed[1])
    )


def _diagnostic_row(
    *,
    condition_id: str,
    states: np.ndarray,
    lifted: np.ndarray,
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
    saturation_epsilon = float(map_config.get("saturation_epsilon", 0.02))
    saturation_fraction = float(
        np.mean((states <= saturation_epsilon) | (states >= 1.0 - saturation_epsilon))
    )
    recurrence_radius, recurrence_rate = _recurrence_rate(states)
    surrogate_rate = _state_shuffled_recurrence_rate(states, seed, condition_id, recurrence_radius)
    initial_sep = float(np.linalg.norm(paired_states[0] - states[0]))
    final_sep = float(np.linalg.norm(paired_states[-1] - states[-1]))
    divergence = math.log(max(final_sep, 1e-12) / max(initial_sep, 1e-12)) / max(ticks - 1, 1)
    lifted_norms = np.linalg.norm(lifted, axis=1)
    return {
        "condition_id": condition_id,
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
        "surrogate_recurrence_rate": round(float(surrogate_rate), 6),
        "recurrence_surrogate_delta": round(float(recurrence_rate - surrogate_rate), 6),
        "finite_time_local_divergence": round(float(divergence), 6),
        "paired_final_separation": round(final_sep, 9),
        "active_vs_null_recurrence_delta": 0.0,
        "active_vs_null_divergence_delta": 0.0,
        "condition_status": "pending",
        "diagnostic_status": NULL_GATE_STATUS,
    }


def _state_shuffled_recurrence_rate(
    states: np.ndarray,
    seed: int,
    condition_id: str,
    radius: float,
) -> float:
    if radius <= 0.0:
        return 0.0
    condition_salt = sum(ord(char) for char in condition_id)
    shuffled = states.copy()
    rng = np.random.default_rng(np.random.SeedSequence([seed, 0xA11A, condition_salt]))
    for column in range(shuffled.shape[1]):
        shuffled[:, column] = shuffled[rng.permutation(shuffled.shape[0]), column]
    distances = _pairwise_distances(shuffled)
    nonzero = distances[distances > 0.0]
    if len(nonzero) == 0:
        return 0.0
    return float(np.mean(nonzero <= radius))


def _condition_status(rows: list[dict[str, Any]], row: dict[str, Any]) -> str:
    if row["condition_id"] != "active_delayed_nonlinear":
        return "null_summary"
    active = rows[0]
    nulls = rows[1:]
    if active["boundedness_status"] != "pass":
        return "fail_closed_active_unbounded_or_trivial"
    if float(active["saturation_fraction"]) > 0.05:
        return "fail_closed_active_saturated"
    recurrence_deltas = [float(null["active_vs_null_recurrence_delta"]) for null in nulls]
    divergence_deltas = [float(null["active_vs_null_divergence_delta"]) for null in nulls]
    recurrence_direction = all(delta > 0.0 for delta in recurrence_deltas) or all(
        delta < 0.0 for delta in recurrence_deltas
    )
    divergence_direction = all(delta > 0.0 for delta in divergence_deltas) or all(
        delta < 0.0 for delta in divergence_deltas
    )
    if recurrence_direction and divergence_direction:
        return "candidate_for_preregistered_phase_diagram"
    return "fail_closed_mixed_or_null_equivalent"


def _load_config(config_path: str | Path) -> dict[str, Any]:
    config = yaml.safe_load(Path(config_path).read_text())
    if (
        not isinstance(config, dict)
        or "run" not in config
        or "analytic_delayed_map" not in config
        or "null_gate" not in config
    ):
        raise ValueError(
            f"{config_path} must define run, analytic_delayed_map, and null_gate sections."
        )
    conditions = tuple(config["null_gate"].get("conditions", []))
    if conditions != NULL_GATE_CONDITIONS:
        raise ValueError(
            f"{config_path} must define exactly the preregistered null-gate conditions."
        )
    return config


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    if (output_path / "null_gate_summary.csv").exists():
        raise FileExistsError(
            f"Output path {output_path} already contains analytic null-gate artifacts."
        )


def _manifest(config: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "experiment_id": config["run"]["experiment_id"],
        "seed": int(config["run"]["seed"]),
        "ticks": int(config["run"]["ticks"]),
        "status": NULL_GATE_STATUS,
        "scientific_status": NULL_GATE_SCIENTIFIC_STATUS,
        "source_scientific_status": SCIENTIFIC_STATUS,
        "preregistration": "docs/analytic_delayed_map_refinement_null_gate_preregistration.md",
        "conditions": list(NULL_GATE_CONDITIONS),
        "dimensionless_controls": ["rho", "delta", "mu", "kappa", "nu"],
        "locks": [
            "seed",
            "ticks",
            "initial_state",
            "perturbation_epsilon",
            "noise_path",
            "rho",
            "delta",
            "mu",
            "kappa",
            "nu",
        ],
        "rows": len(rows),
        "artifacts": [
            "config.yaml",
            "manifest.yaml",
            "null_gate_summary.csv",
            "summary.md",
        ],
        "no_simulator_artifacts": ["metrics.csv", "events.csv"],
    }


def _summary(rows: list[dict[str, Any]]) -> str:
    active = rows[0]
    return "\n".join(
        [
            "# Analytic Delayed Map Null Gate",
            "",
            f"- Status: `{NULL_GATE_STATUS}`",
            f"- Scientific status: `{NULL_GATE_SCIENTIFIC_STATUS}`",
            f"- Conditions: `{len(rows)}`",
            f"- Active boundedness: `{active['boundedness_status']}`",
            f"- Active saturation fraction: `{active['saturation_fraction']}`",
            f"- Active recurrence-surrogate delta: `{active['recurrence_surrogate_delta']}`",
            f"- Active finite-time local divergence: `{active['finite_time_local_divergence']}`",
            f"- Gate status: `{active['condition_status']}`",
            "",
            "This is a standalone analytic null gate. It writes summary diagnostics",
            "and manifest artifacts only; it does not write per-tick simulator metrics",
            "or events, and it does not support lobe-like, semantic-dynamics, chaotic,",
            "or strange-attractor-like claims.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the four-condition analytic delayed-map null gate."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Null-gate config.")
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="Output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_analytic_delayed_map_null_gate(config_path=args.config, out_dir=args.out)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
