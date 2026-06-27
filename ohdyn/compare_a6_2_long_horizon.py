"""Run the preregistered A6.2 96-tick validation comparison."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from ohdyn.compare_a6_logistic_appraisal import (
    A6_2_LONG_HORIZON_CONFIGS,
    run_a6_logistic_appraisal_comparison,
)


DEFAULT_A6_2_LONG_HORIZON_SEEDS = (1, 2)
DEFAULT_A6_2_LONG_HORIZON_COMPARE_DIR = Path(
    "runs/a6_2_long_horizon_compare_seed1_2"
)


def run_a6_2_long_horizon_comparison(
    *,
    seeds: tuple[int, ...] = DEFAULT_A6_2_LONG_HORIZON_SEEDS,
    out_dir: str | Path = DEFAULT_A6_2_LONG_HORIZON_COMPARE_DIR,
) -> list[dict[str, object]]:
    if seeds != DEFAULT_A6_2_LONG_HORIZON_SEEDS:
        raise ValueError("A6.2 long-horizon validation is fixed to paired seeds 1 and 2.")
    return run_a6_logistic_appraisal_comparison(
        seeds=seeds,
        out_dir=out_dir,
        include_a6_1_nulls=True,
        config_specs=A6_2_LONG_HORIZON_CONFIGS,
        summary_title="A6.2 Long-Horizon Validation Comparison",
        scope_line=(
            "fixed 96-tick single-hive A6.2 validation configs plus the two "
            "source-preserving null artifacts; paired seeds 1 and 2 only"
        ),
        scientific_status=(
            "bounded validation artifact comparison; recurrence interpretation "
            "requires the read-only A6.2 analyzer"
        ),
        conservative_use=(
            "This helper is limited to the preregistered A6.2 long-horizon "
            "validation. Use these artifacts for the existing read-only "
            "residual-recurrence analyzer; do not broaden seeds, add mechanisms, "
            "or promote A6 from the comparison summary."
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the fixed 96-tick A6.2 long-horizon validation comparison."
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_A6_2_LONG_HORIZON_SEEDS),
        help="Fixed deterministic paired seeds; preregistered value is 1 2.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A6_2_LONG_HORIZON_COMPARE_DIR),
        help="Output directory for A6.2 long-horizon comparison artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a6_2_long_horizon_comparison(
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
