"""Run the preregistered A7 96-tick residual/null validation comparison."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from ohdyn.compare_a7_semantic_field import (
    DEFAULT_A7_LONG_HORIZON_COMPARE_DIR,
    DEFAULT_A7_LONG_HORIZON_SEEDS,
    run_a7_semantic_field_comparison,
)


def run_a7_long_horizon_comparison(
    *,
    seeds: tuple[int, ...] = DEFAULT_A7_LONG_HORIZON_SEEDS,
    out_dir: str | Path = DEFAULT_A7_LONG_HORIZON_COMPARE_DIR,
) -> list[dict[str, object]]:
    return run_a7_semantic_field_comparison(seeds=seeds, out_dir=out_dir)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the fixed 96-tick A7 residual/null validation comparison."
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_A7_LONG_HORIZON_SEEDS),
        help="Fixed deterministic paired seeds; preregistered value is 1 2.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A7_LONG_HORIZON_COMPARE_DIR),
        help="Output directory for A7 long-horizon comparison artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a7_long_horizon_comparison(
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
