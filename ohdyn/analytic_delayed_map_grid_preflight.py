"""Read-only grid preflight for the analytic delayed map."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.analytic_delayed_map import (
    MAP_STATUS,
    SCIENTIFIC_STATUS,
    simulate_and_diagnose,
)


DEFAULT_CONFIG = Path("configs/analytic_delayed_map_grid_preflight.yaml")
DEFAULT_OUT_DIR = Path("runs/analytic_delayed_map_grid_preflight_seed1")
GRID_PREFLIGHT_STATUS = "analytic_delayed_map_grid_preflight_read_only"
GRID_PREFLIGHT_FIELDS = (
    "condition_id",
    "seed",
    "ticks",
    "rho",
    "delta",
    "delay_ticks",
    "boundedness_status",
    "recurrence_surrogate_delta",
    "finite_time_local_divergence",
    "local_lifted_spectral_radius",
    "contraction_status",
    "diagnostic_status",
)


def run_analytic_delayed_map_grid_preflight(
    *,
    config_path: str | Path = DEFAULT_CONFIG,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> list[dict[str, Any]]:
    """Run a tiny rho x delay diagnostic grid without writing per-tick metrics."""

    config = _load_config(config_path)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    rows = [_preflight_row(config, condition) for condition in _conditions(config)]
    _write_csv(output_path / "grid_preflight.csv", rows, GRID_PREFLIGHT_FIELDS)
    (output_path / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=True))
    (output_path / "manifest.yaml").write_text(
        yaml.safe_dump(_manifest(config, len(rows)), sort_keys=True)
    )
    (output_path / "summary.md").write_text(_summary(rows))
    return rows


def _conditions(config: dict[str, Any]) -> list[dict[str, float]]:
    grid = config["grid_preflight"]
    rho_values = [float(value) for value in grid["rho_values"]]
    delta_values = [float(value) for value in grid["delta_values"]]
    return [
        {"rho": rho, "delta": delta}
        for rho in rho_values
        for delta in delta_values
    ]


def _preflight_row(
    config: dict[str, Any],
    condition: dict[str, float],
) -> dict[str, Any]:
    condition_config = yaml.safe_load(yaml.safe_dump(config))
    map_config = condition_config["analytic_delayed_map"]
    map_config["rho"] = condition["rho"]
    map_config["delta"] = condition["delta"]
    _, diagnostics = simulate_and_diagnose(condition_config)
    return {
        "condition_id": f"rho_{condition['rho']:g}_delta_{condition['delta']:g}",
        "seed": diagnostics["seed"],
        "ticks": diagnostics["ticks"],
        "rho": diagnostics["rho"],
        "delta": diagnostics["delta"],
        "delay_ticks": diagnostics["delay_ticks"],
        "boundedness_status": diagnostics["boundedness_status"],
        "recurrence_surrogate_delta": diagnostics["recurrence_surrogate_delta"],
        "finite_time_local_divergence": diagnostics["finite_time_local_divergence"],
        "local_lifted_spectral_radius": diagnostics["local_lifted_spectral_radius"],
        "contraction_status": diagnostics["contraction_status"],
        "diagnostic_status": MAP_STATUS,
    }


def _load_config(config_path: str | Path) -> dict[str, Any]:
    config = yaml.safe_load(Path(config_path).read_text())
    if (
        not isinstance(config, dict)
        or "run" not in config
        or "analytic_delayed_map" not in config
        or "grid_preflight" not in config
    ):
        raise ValueError(
            f"{config_path} must define run, analytic_delayed_map, and grid_preflight sections."
        )
    grid = config["grid_preflight"]
    if len(grid.get("rho_values", [])) != 2 or len(grid.get("delta_values", [])) != 2:
        raise ValueError(f"{config_path} must define exactly two rho and two delta values.")
    return config


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    if (output_path / "grid_preflight.csv").exists():
        raise FileExistsError(
            f"Output path {output_path} already contains analytic grid preflight artifacts."
        )


def _manifest(config: dict[str, Any], rows: int) -> dict[str, Any]:
    return {
        "experiment_id": config["run"]["experiment_id"],
        "seed": int(config["run"]["seed"]),
        "ticks": int(config["run"]["ticks"]),
        "status": GRID_PREFLIGHT_STATUS,
        "scientific_status": SCIENTIFIC_STATUS,
        "source_map_status": MAP_STATUS,
        "dimensionless_controls": ["rho", "delta", "mu", "kappa", "nu"],
        "grid_axes": {
            "rho": [float(value) for value in config["grid_preflight"]["rho_values"]],
            "delta": [float(value) for value in config["grid_preflight"]["delta_values"]],
        },
        "rows": rows,
        "artifacts": [
            "config.yaml",
            "manifest.yaml",
            "grid_preflight.csv",
            "summary.md",
        ],
    }


def _summary(rows: list[dict[str, Any]]) -> str:
    bounded = sum(1 for row in rows if row["boundedness_status"] == "pass")
    recurrence_values = [
        float(row["recurrence_surrogate_delta"])
        for row in rows
    ]
    divergence_values = [
        float(row["finite_time_local_divergence"])
        for row in rows
    ]
    spectral_values = [
        float(row["local_lifted_spectral_radius"])
        for row in rows
    ]
    contraction_rows = sum(1 for row in rows if row["contraction_status"] == "local_contracting")
    return "\n".join(
        [
            "# Analytic Delayed Map Grid Preflight",
            "",
            f"- Status: `{GRID_PREFLIGHT_STATUS}`",
            f"- Scientific status: `{SCIENTIFIC_STATUS}`",
            f"- Conditions: `{len(rows)}`",
            f"- Boundedness pass rows: `{bounded}/{len(rows)}`",
            f"- Recurrence-surrogate delta range: `{min(recurrence_values):.6f}` to `{max(recurrence_values):.6f}`",
            f"- Finite-time local-divergence range: `{min(divergence_values):.6f}` to `{max(divergence_values):.6f}`",
            f"- Local lifted spectral-radius range: `{min(spectral_values):.6f}` to `{max(spectral_values):.6f}`",
            f"- Local contraction rows: `{contraction_rows}/{len(rows)}`",
            "",
            "This read-only preflight reports grid-level diagnostics only. It does not",
            "write per-tick simulator artifacts or support lobe-like, semantic-dynamics,",
            "or strange-attractor-like claims.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the read-only analytic delayed-map rho x delay preflight."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Grid preflight config.")
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="Output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_analytic_delayed_map_grid_preflight(config_path=args.config, out_dir=args.out)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
