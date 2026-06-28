"""Run the preregistered A7.2 ten-condition smoke comparison."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.a7_2_delayed_prediction_contract import (
    A7_2_COMPARISON_MANIFEST_FIELDS,
    A7_2_CONDITIONS,
    A7_2_SMOKE_PARAMETERS,
)
from ohdyn.config import load_config
from ohdyn.run import run_experiment


DEFAULT_A7_2_SMOKE_CONFIGS = (
    Path("configs/a7_2_zero_budget_reactive_smoke.yaml"),
    Path("configs/a7_2_intermediate_endogenous_delayed_prediction_smoke.yaml"),
    Path("configs/a7_2_high_budget_oracle_smoothing_smoke.yaml"),
    Path("configs/a7_2_amplitude_matched_linear_delayed_prediction_smoke.yaml"),
    Path("configs/a7_2_same_tick_logistic_prediction_smoke.yaml"),
    Path("configs/a7_2_phase_shuffled_lag_input_smoke.yaml"),
    Path("configs/a7_2_threshold_shuffled_smoke.yaml"),
    Path("configs/a7_2_source_preserving_artifact_label_shuffle_smoke.yaml"),
    Path("configs/a7_2_spend_only_replay_smoke.yaml"),
    Path("configs/a7_2_artifact_off_source_ledger_null_smoke.yaml"),
)
DEFAULT_A7_2_SEEDS = (1, 2)
DEFAULT_A7_2_COMPARE_DIR = Path("runs/a7_2_delayed_prediction_compare_seed1_2")


def run_a7_2_delayed_prediction_comparison(
    *,
    config_paths: tuple[str | Path, ...] = DEFAULT_A7_2_SMOKE_CONFIGS,
    seeds: tuple[int, ...] = DEFAULT_A7_2_SEEDS,
    out_dir: str | Path = DEFAULT_A7_2_COMPARE_DIR,
) -> list[dict[str, Any]]:
    """Run only the fixed preregistered A7.2 tiny smoke grid."""

    if seeds != DEFAULT_A7_2_SEEDS:
        raise ValueError("A7.2 smoke comparison is fixed to paired seeds 1 and 2.")
    configs = _load_a7_2_configs(config_paths)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for condition in A7_2_CONDITIONS:
        config_path = Path(config_paths[A7_2_CONDITIONS.index(condition)])
        config = configs[condition]
        for seed in seeds:
            run_dir = output_path / f"{condition}_seed{seed}"
            run_experiment(config_path, seed=seed, out_dir=run_dir)
            rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "config": str(config_path),
                    "run_dir": run_dir.name,
                    "tick_count": config.run.ticks,
                    "metrics_rows": _csv_row_count(run_dir / "metrics.csv"),
                    "events_rows": _csv_row_count(run_dir / "events.csv"),
                    "scientific_status": (
                        "bounded_a7_2_smoke_artifacts_only_requires_read_only_analyzer"
                    ),
                }
            )

    _write_csv(
        output_path / "a7_2_delayed_prediction_comparison_manifest.csv",
        rows,
        A7_2_COMPARISON_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(_summary(rows, seeds))
    return rows


def _load_a7_2_configs(config_paths: tuple[str | Path, ...]) -> dict[str, Any]:
    configs: dict[str, Any] = {}
    for path in config_paths:
        cfg = load_config(path)
        if cfg.a7_2_delayed_prediction is None:
            raise ValueError(f"{path} must enable a7_2_delayed_prediction.")
        if cfg.semantic_field is not None or cfg.logistic_appraisal is not None:
            raise ValueError(f"{path} must not mix A7.2 with earlier mechanism sections.")
        if cfg.predictive_control is not None or cfg.hives:
            raise ValueError(f"{path} must be a single-hive A7.2 config.")
        if cfg.run.ticks != A7_2_SMOKE_PARAMETERS["horizon_ticks"]:
            raise ValueError(f"{path} must use the frozen 48-tick A7.2 smoke horizon.")
        condition = cfg.a7_2_delayed_prediction.condition
        if condition in configs:
            raise ValueError(f"Duplicate A7.2 condition config: {condition}")
        configs[condition] = cfg

    observed = tuple(configs)
    if observed != A7_2_CONDITIONS:
        raise ValueError(
            "A7.2 comparison requires configs in frozen condition order: "
            + ", ".join(A7_2_CONDITIONS)
        )
    return configs


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    if (output_path / "a7_2_delayed_prediction_comparison_manifest.csv").exists():
        raise FileExistsError(
            f"Output path {output_path} already contains A7.2 comparison artifacts."
        )


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: tuple[str, ...],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return sum(1 for _ in reader)


def _summary(rows: list[dict[str, Any]], seeds: tuple[int, ...]) -> str:
    return "\n".join(
        [
            "# A7.2 Delayed Prediction Smoke Comparison",
            "",
            f"- Conditions: {len(A7_2_CONDITIONS)}",
            f"- Seeds: {', '.join(str(seed) for seed in seeds)}",
            f"- Run directories: {len(rows)}",
            "- Horizon: 48 ticks",
            "- Status: `bounded_a7_2_smoke_artifacts_only_requires_read_only_analyzer`",
            "",
            "This helper runs only the preregistered single-hive A7.2 smoke grid.",
            "It does not authorize promotion language, parameter tuning, broad",
            "seed sweeps, dashboards, integrations, or downstream multi-hive coupling.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the fixed A7.2 delayed-prediction smoke comparison."
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_A7_2_SEEDS),
        help="Fixed deterministic paired seeds; preregistered value is 1 2.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A7_2_COMPARE_DIR),
        help="Output directory for A7.2 smoke comparison artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a7_2_delayed_prediction_comparison(
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
