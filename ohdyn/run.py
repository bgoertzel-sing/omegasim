"""Command line entry point for OmegaSim experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

from ohdyn.config import load_config
from ohdyn.io import write_outputs
from ohdyn.sim import SimulationResult, simulate


def run_experiment(config_path: str | Path, seed: int, out_dir: str | Path) -> SimulationResult:
    config = load_config(config_path)
    result = simulate(config, seed)
    write_outputs(result, out_dir)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an OmegaSim dynamics experiment.")
    parser.add_argument("--config", required=True, help="Path to a YAML run config.")
    parser.add_argument("--seed", required=True, type=int, help="Deterministic RNG seed.")
    parser.add_argument("--out", required=True, help="Output directory for run artifacts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_experiment(args.config, args.seed, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
