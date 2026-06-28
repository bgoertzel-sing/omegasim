"""Emit deterministic three-hive ring schema/source-ledger smoke artifacts.

This scaffold loads the frozen three-hive ring contract fixture and writes
config, manifest, and schema artifacts only. It intentionally does not call the
simulator, produce metrics/events, or create scientific evidence.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.config import load_config
from ohdyn.three_hive_ring_contract import (
    THREE_HIVE_RING_CONDITIONS,
    THREE_HIVE_RING_HIVES,
    THREE_HIVE_RING_SCHEMA_SMOKE_MANIFEST_FIELDS,
    THREE_HIVE_RING_SMOKE_PARAMETERS,
    THREE_HIVE_RING_SOURCE_LEDGER_FIELDS,
    three_hive_ring_required_event_fields,
    three_hive_ring_required_metric_fields,
)


DEFAULT_THREE_HIVE_RING_CONTRACT_CONFIG = Path(
    "configs/three_hive_ring_contract_validation.yaml"
)
DEFAULT_THREE_HIVE_RING_SEEDS = tuple(THREE_HIVE_RING_SMOKE_PARAMETERS["seeds"])
DEFAULT_THREE_HIVE_RING_SCHEMA_SMOKE_DIR = Path(
    "runs/three_hive_ring_schema_smoke_seed1_2"
)
THREE_HIVE_RING_ARTIFACT_STATUS = "schema_source_ledger_only"
THREE_HIVE_RING_SCIENTIFIC_STATUS = (
    "no_simulator_mechanics_no_three_hive_ring_evidence"
)


def run_three_hive_ring_schema_smoke(
    *,
    config_path: str | Path = DEFAULT_THREE_HIVE_RING_CONTRACT_CONFIG,
    seeds: tuple[int, ...] = DEFAULT_THREE_HIVE_RING_SEEDS,
    out_dir: str | Path = DEFAULT_THREE_HIVE_RING_SCHEMA_SMOKE_DIR,
) -> list[dict[str, Any]]:
    """Write the fixed three-hive ring schema/source-ledger smoke artifact grid."""

    if seeds != DEFAULT_THREE_HIVE_RING_SEEDS:
        raise ValueError("Three-hive ring schema smoke is fixed to paired seeds 1 and 2.")
    config = load_config(config_path)
    if config.three_hive_ring is None:
        raise ValueError(f"{config_path} must enable three_hive_ring.")

    output_path = Path(out_dir)
    _ensure_outputs_available(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    metric_fields = three_hive_ring_required_metric_fields()
    event_fields = three_hive_ring_required_event_fields()
    source_ledger_fields = THREE_HIVE_RING_SOURCE_LEDGER_FIELDS
    rows: list[dict[str, Any]] = []

    for condition in THREE_HIVE_RING_CONDITIONS:
        for seed in seeds:
            run_dir = output_path / f"{condition}_seed{seed}"
            run_dir.mkdir(parents=True, exist_ok=True)
            config_dict = config.to_dict()
            (run_dir / "config.yaml").write_text(
                yaml.safe_dump(config_dict, sort_keys=True)
            )
            (run_dir / "manifest.yaml").write_text(
                yaml.safe_dump(
                    _manifest(
                        condition,
                        seed,
                        config_dict,
                        metric_fields,
                        event_fields,
                        source_ledger_fields,
                    ),
                    sort_keys=True,
                )
            )
            _write_schema(run_dir / "metrics_schema.csv", metric_fields)
            _write_schema(run_dir / "events_schema.csv", event_fields)
            _write_schema(run_dir / "source_ledger_schema.csv", source_ledger_fields)
            (run_dir / "summary.md").write_text(_run_summary(condition, seed))
            rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "config": str(Path(config_path)),
                    "run_dir": run_dir.name,
                    "tick_count": config.run.ticks,
                    "hive_count": len(config.three_hive_ring.hives),
                    "edge_count": len(config.three_hive_ring.edges),
                    "metric_schema_fields": len(metric_fields),
                    "event_schema_fields": len(event_fields),
                    "source_ledger_schema_fields": len(source_ledger_fields),
                    "artifact_status": THREE_HIVE_RING_ARTIFACT_STATUS,
                    "scientific_status": THREE_HIVE_RING_SCIENTIFIC_STATUS,
                }
            )

    _write_csv(
        output_path / "three_hive_ring_schema_smoke_manifest.csv",
        rows,
        THREE_HIVE_RING_SCHEMA_SMOKE_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(_summary(rows, seeds))
    return rows


def _manifest(
    condition: str,
    seed: int,
    config: dict[str, Any],
    metric_fields: tuple[str, ...],
    event_fields: tuple[str, ...],
    source_ledger_fields: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "experiment_id": config["run"]["experiment_id"],
        "condition": condition,
        "seed": seed,
        "ticks": config["run"]["ticks"],
        "hives": list(THREE_HIVE_RING_HIVES),
        "metric_schema_fields": list(metric_fields),
        "event_schema_fields": list(event_fields),
        "source_ledger_schema_fields": list(source_ledger_fields),
        "artifacts": [
            "config.yaml",
            "manifest.yaml",
            "metrics_schema.csv",
            "events_schema.csv",
            "source_ledger_schema.csv",
            "summary.md",
        ],
        "artifact_status": THREE_HIVE_RING_ARTIFACT_STATUS,
        "scientific_status": THREE_HIVE_RING_SCIENTIFIC_STATUS,
        "simulator_mechanics_touched": False,
        "config": config,
    }


def _write_schema(path: Path, fields: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("field_name",))
        writer.writeheader()
        writer.writerows({"field_name": field} for field in fields)


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: tuple[str, ...],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _ensure_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    if (output_path / "three_hive_ring_schema_smoke_manifest.csv").exists():
        raise FileExistsError(
            f"Output path {output_path} already contains three-hive ring schema smoke artifacts."
        )


def _run_summary(condition: str, seed: int) -> str:
    return "\n".join(
        [
            "# Three-Hive Ring Schema Smoke Artifact",
            "",
            f"- Condition: `{condition}`",
            f"- Seed: `{seed}`",
            f"- Status: `{THREE_HIVE_RING_ARTIFACT_STATUS}`",
            f"- Scientific status: `{THREE_HIVE_RING_SCIENTIFIC_STATUS}`",
            "",
            "This directory contains only frozen contract, schema, and source-ledger",
            "artifacts for later preflight. It contains no simulator metrics/events.",
            "",
        ]
    )


def _summary(rows: list[dict[str, Any]], seeds: tuple[int, ...]) -> str:
    return "\n".join(
        [
            "# Three-Hive Ring Schema Smoke",
            "",
            f"- Conditions: {len(THREE_HIVE_RING_CONDITIONS)}",
            f"- Seeds: {', '.join(str(seed) for seed in seeds)}",
            f"- Artifact directories: {len(rows)}",
            f"- Horizon: {THREE_HIVE_RING_SMOKE_PARAMETERS['horizon_ticks']} ticks",
            f"- Status: `{THREE_HIVE_RING_ARTIFACT_STATUS}`",
            f"- Scientific status: `{THREE_HIVE_RING_SCIENTIFIC_STATUS}`",
            "",
            "This helper loads the frozen contract fixture and emits schema/source-ledger artifacts only.",
            "It does not authorize analyzers, promotion",
            "claims, broad seed sweeps, dashboards, integrations, parameter sweeps,",
            "or hives beyond the frozen ring.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit fixed three-hive ring schema/source-ledger smoke artifacts."
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_THREE_HIVE_RING_CONTRACT_CONFIG),
        help="Frozen three-hive ring contract fixture.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(DEFAULT_THREE_HIVE_RING_SEEDS),
        help="Fixed deterministic paired seeds; preregistered value is 1 2.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_THREE_HIVE_RING_SCHEMA_SMOKE_DIR),
        help="Output directory for schema/source-ledger artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_three_hive_ring_schema_smoke(
            config_path=args.config,
            seeds=tuple(args.seeds),
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
