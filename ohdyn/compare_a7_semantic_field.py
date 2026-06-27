"""Create deterministic A7 semantic-field comparison placeholders.

This scaffold enumerates the frozen A7 fixture stubs and writes config/manifest
placeholders only. It intentionally does not call the simulator or create
metrics/events, so A7 analysis must still fail closed until mechanics exist.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.a7_semantic_field_contract import (
    A7_CONDITIONS,
    A7_NULL_CONDITIONS,
    A7_POSITIVE_CONDITION,
)
from ohdyn.config import load_config


DEFAULT_A7_SMOKE_CONFIGS = (
    Path("configs/a7_logistic_semantic_coupling_smoke.yaml"),
    Path("configs/a7_semantic_off_baseline_smoke.yaml"),
    Path("configs/a7_amplitude_matched_linear_semantic_coupling_smoke.yaml"),
    Path("configs/a7_source_preserving_semantic_label_shuffle_smoke.yaml"),
    Path("configs/a7_semantic_field_phase_shuffle_smoke.yaml"),
    Path("configs/a7_prediction_budget_timing_broken_matched_count_null_smoke.yaml"),
)
DEFAULT_A7_SEMANTIC_FIELD_SEEDS = (1, 2)
DEFAULT_A7_SEMANTIC_FIELD_COMPARE_DIR = Path("runs/a7_semantic_field_compare")

A7_PLACEHOLDER_MANIFEST_FIELDS = (
    "condition",
    "seed",
    "config",
    "run_dir",
    "placeholder_status",
    "scientific_status",
)


def run_a7_semantic_field_placeholder_comparison(
    *,
    config_paths: tuple[str | Path, ...] = DEFAULT_A7_SMOKE_CONFIGS,
    seeds: tuple[int, ...] = DEFAULT_A7_SEMANTIC_FIELD_SEEDS,
    out_dir: str | Path = DEFAULT_A7_SEMANTIC_FIELD_COMPARE_DIR,
) -> list[dict[str, Any]]:
    """Write deterministic A7 comparison placeholders without simulation."""

    _validate_seeds(seeds)
    configs = _load_a7_configs(config_paths)
    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_configs = _write_generated_configs(configs, output_path / "configs")
    rows: list[dict[str, Any]] = []
    for condition in A7_CONDITIONS:
        config_path = generated_configs[condition]
        config = configs[condition]
        for seed in seeds:
            run_dir = output_path / f"{condition}_seed{seed}"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "config.yaml").write_text(
                yaml.safe_dump(config.to_dict(), sort_keys=True)
            )
            (run_dir / "manifest.yaml").write_text(
                yaml.safe_dump(
                    _placeholder_manifest(condition, config.to_dict(), seed),
                    sort_keys=True,
                )
            )
            (run_dir / "summary.md").write_text(
                _placeholder_run_summary(condition, seed)
            )
            rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "config": str(Path("configs") / config_path.name),
                    "run_dir": run_dir.name,
                    "placeholder_status": "config_manifest_only",
                    "scientific_status": "no_simulator_mechanics_no_a7_evidence",
                }
            )

    _write_csv(
        output_path / "a7_semantic_field_placeholder_manifest.csv",
        rows,
        A7_PLACEHOLDER_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(_summary(rows, seeds))
    return rows


def _validate_seeds(seeds: tuple[int, ...]) -> None:
    if not seeds:
        raise ValueError("At least one seed is required.")
    invalid = [
        seed
        for seed in seeds
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0
    ]
    if invalid:
        raise ValueError("Seeds must be non-negative integers.")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must not contain duplicates.")


def _load_a7_configs(
    config_paths: tuple[str | Path, ...],
) -> dict[str, Any]:
    configs: dict[str, Any] = {}
    for path in config_paths:
        cfg = load_config(path)
        if cfg.semantic_field is None:
            raise ValueError(f"{path} must enable semantic_field.")
        if cfg.logistic_appraisal is not None or cfg.predictive_control is not None:
            raise ValueError(f"{path} must not mix A7 with earlier mechanism sections.")
        if cfg.hives:
            raise ValueError(f"{path} must be a single-hive A7 config.")
        condition = cfg.semantic_field.condition
        if condition in configs:
            raise ValueError(f"Duplicate A7 condition config: {condition}")
        configs[condition] = cfg

    observed = tuple(configs)
    if observed != A7_CONDITIONS:
        raise ValueError(
            "A7 placeholder comparison requires configs in frozen condition order: "
            + ", ".join(A7_CONDITIONS)
        )
    return configs


def _write_generated_configs(
    configs: dict[str, Any],
    config_dir: Path,
) -> dict[str, Path]:
    config_dir.mkdir(parents=True, exist_ok=True)
    generated = {}
    for condition in A7_CONDITIONS:
        path = config_dir / f"{condition}.yaml"
        path.write_text(yaml.safe_dump(configs[condition].to_dict(), sort_keys=False))
        generated[condition] = path
    return generated


def _placeholder_manifest(
    condition: str,
    config: dict[str, Any],
    seed: int,
) -> dict[str, Any]:
    return {
        "experiment_id": config["run"]["experiment_id"],
        "seed": seed,
        "ticks": config["run"]["ticks"],
        "agent_count": config["model"]["agent_count"],
        "actions": config["model"]["actions"],
        "artifacts": ["config.yaml", "manifest.yaml", "summary.md"],
        "placeholder_status": "config_manifest_only",
        "scientific_status": "no_simulator_mechanics_no_a7_evidence",
        "a7_semantic_field": {
            "condition": condition,
            "positive_condition": A7_POSITIVE_CONDITION,
            "null_conditions": list(A7_NULL_CONDITIONS),
            "single_hive_only": True,
            "simulator_mechanics_touched": False,
        },
        "config": config,
    }


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        name
        for name in (
            "a7_semantic_field_placeholder_manifest.csv",
            "summary.md",
        )
        if (output_path / name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(
            f"Output path {output_path} already contains A7 placeholder artifacts: {names}"
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


def _placeholder_run_summary(condition: str, seed: int) -> str:
    return "\n".join(
        [
            "# A7 Semantic-Field Placeholder",
            "",
            f"- Condition: `{condition}`",
            f"- Seed: `{seed}`",
            "- Status: `config_manifest_only`",
            "",
            "No simulator mechanics were run and no A7 scientific evidence was produced.",
            "",
        ]
    )


def _summary(rows: list[dict[str, Any]], seeds: tuple[int, ...]) -> str:
    return "\n".join(
        [
            "# A7 Semantic-Field Placeholder Comparison",
            "",
            f"- Conditions: {len(A7_CONDITIONS)}",
            f"- Seeds: {', '.join(str(seed) for seed in seeds)}",
            f"- Placeholder run directories: {len(rows)}",
            "- Status: `config_manifest_only`",
            "",
            "This scaffold freezes the six-condition comparison envelope by writing",
            "normalized configs and manifests only. It intentionally does not run",
            "simulator mechanics, write metrics/events, or authorize semantic-field",
            "interpretation.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write A7 semantic-field comparison placeholders without simulation."
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_A7_SEMANTIC_FIELD_SEEDS),
        help="Deterministic seeds for placeholder manifests.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A7_SEMANTIC_FIELD_COMPARE_DIR),
        help="Output directory for A7 placeholder comparison artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a7_semantic_field_placeholder_comparison(
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
