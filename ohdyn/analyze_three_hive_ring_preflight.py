"""Read-only three-hive ring schema/source-ledger preflight analyzer."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_three_hive_ring import DEFAULT_THREE_HIVE_RING_SCHEMA_SMOKE_DIR
from ohdyn.three_hive_ring_contract import (
    THREE_HIVE_RING_CONDITIONS,
    THREE_HIVE_RING_PREFLIGHT_COMPLETENESS_FIELDS,
    THREE_HIVE_RING_PREFLIGHT_MANIFEST_FIELDS,
    THREE_HIVE_RING_SMOKE_PARAMETERS,
    THREE_HIVE_RING_SOURCE_LEDGER_FIELDS,
    three_hive_ring_required_event_fields,
    three_hive_ring_required_metric_fields,
)


DEFAULT_THREE_HIVE_RING_PREFLIGHT_DIR = Path(
    "runs/three_hive_ring_preflight_seed1_2"
)
THREE_HIVE_RING_PREFLIGHT_STATUS_NO_METRICS_EVENTS = (
    "fail_closed_no_metrics_events"
)
THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SOURCE_LEDGER = (
    "fail_closed_missing_source_ledger"
)
THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SCHEMA = "fail_closed_missing_schema"
THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_COVERAGE = (
    "fail_closed_missing_condition_seed_coverage"
)
THREE_HIVE_RING_PREFLIGHT_STATUS_ELIGIBLE = "eligible_for_mechanics_gate"


def run_three_hive_ring_preflight_analysis(
    compare_dir: str | Path = DEFAULT_THREE_HIVE_RING_SCHEMA_SMOKE_DIR,
    out_dir: str | Path = DEFAULT_THREE_HIVE_RING_PREFLIGHT_DIR,
) -> dict[str, Any]:
    """Inspect existing three-hive ring artifacts without running simulations."""

    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs = _read_runs(compare_path)
    completeness_rows = [_completeness_row(run) for run in runs]
    status = _overall_status(completeness_rows)
    manifest_row = _manifest_row(compare_path, output_path, completeness_rows, status)

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "three_hive_ring_preflight_completeness.csv",
        completeness_rows,
        THREE_HIVE_RING_PREFLIGHT_COMPLETENESS_FIELDS,
    )
    _write_csv(
        output_path / "three_hive_ring_preflight_manifest.csv",
        [manifest_row],
        THREE_HIVE_RING_PREFLIGHT_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(compare_path, completeness_rows, manifest_row)
    )
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "run_count": len(runs),
        "status": status,
    }


def _read_runs(compare_path: Path) -> list[dict[str, Any]]:
    if not compare_path.exists():
        raise FileNotFoundError(
            f"Three-hive ring comparison directory does not exist: {compare_path}"
        )
    runs: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        manifest_path = run_dir / "manifest.yaml"
        manifest = _read_manifest(manifest_path)
        condition = str(manifest.get("condition") or _condition_from_name(run_dir.name))
        seed = int(manifest.get("seed", _seed_from_name(run_dir.name)))
        runs.append(
            {
                "condition": condition,
                "seed": seed,
                "run_dir": run_dir,
                "config_path": run_dir / "config.yaml",
                "manifest_path": manifest_path,
                "metrics_schema_path": run_dir / "metrics_schema.csv",
                "events_schema_path": run_dir / "events_schema.csv",
                "source_ledger_schema_path": run_dir / "source_ledger_schema.csv",
                "metrics_path": run_dir / "metrics.csv",
                "events_path": run_dir / "events.csv",
            }
        )
    return runs


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def _condition_from_name(name: str) -> str:
    for condition in THREE_HIVE_RING_CONDITIONS:
        if name.startswith(condition):
            return condition
    return name.rsplit("_seed", 1)[0]


def _seed_from_name(name: str) -> int:
    if "_seed" not in name:
        return 0
    suffix = name.rsplit("_seed", 1)[1]
    digits = "".join(char for char in suffix if char.isdigit())
    return int(digits) if digits else 0


def _completeness_row(run: dict[str, Any]) -> dict[str, str | int]:
    required_paths = (
        Path(run["config_path"]),
        Path(run["manifest_path"]),
        Path(run["metrics_schema_path"]),
        Path(run["events_schema_path"]),
        Path(run["source_ledger_schema_path"]),
    )
    missing_required_artifacts = [
        path.name for path in required_paths if not path.exists()
    ]
    metric_fields = _schema_fields(Path(run["metrics_schema_path"]))
    event_fields = _schema_fields(Path(run["events_schema_path"]))
    source_ledger_fields = _schema_fields(Path(run["source_ledger_schema_path"]))
    missing_metric_fields = _missing_fields(
        metric_fields, three_hive_ring_required_metric_fields()
    )
    missing_event_fields = _missing_fields(
        event_fields, three_hive_ring_required_event_fields()
    )
    missing_source_ledger_fields = _missing_fields(
        source_ledger_fields, THREE_HIVE_RING_SOURCE_LEDGER_FIELDS
    )
    metrics_path = Path(run["metrics_path"])
    events_path = Path(run["events_path"])
    metrics_events_status = (
        "present" if metrics_path.exists() and events_path.exists() else "absent"
    )
    status = _row_status(
        missing_required_artifacts,
        missing_metric_fields,
        missing_event_fields,
        missing_source_ledger_fields,
        metrics_events_status,
    )
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "run_dir": str(run["run_dir"]),
        "config_path": str(run["config_path"]),
        "manifest_path": str(run["manifest_path"]),
        "metrics_schema_path": str(run["metrics_schema_path"]),
        "events_schema_path": str(run["events_schema_path"]),
        "source_ledger_schema_path": str(run["source_ledger_schema_path"]),
        "metrics_path": str(metrics_path),
        "events_path": str(events_path),
        "required_artifact_status": (
            "pass" if not missing_required_artifacts else "missing:"
            + "|".join(missing_required_artifacts)
        ),
        "metric_schema_status": "pass" if not missing_metric_fields else "missing_fields",
        "event_schema_status": "pass" if not missing_event_fields else "missing_fields",
        "source_ledger_schema_status": (
            "pass" if not missing_source_ledger_fields else "missing_fields"
        ),
        "missing_metric_schema_fields": "|".join(missing_metric_fields),
        "missing_event_schema_fields": "|".join(missing_event_fields),
        "missing_source_ledger_fields": "|".join(missing_source_ledger_fields),
        "metrics_events_status": metrics_events_status,
        "status": status,
        "interpretation": _row_interpretation(status),
    }


def _schema_fields(path: Path) -> frozenset[str]:
    if not path.exists():
        return frozenset()
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return frozenset(row.get("field_name", "") for row in reader)


def _missing_fields(observed: frozenset[str], required: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(field for field in required if field not in observed)


def _row_status(
    missing_required_artifacts: list[str],
    missing_metric_fields: tuple[str, ...],
    missing_event_fields: tuple[str, ...],
    missing_source_ledger_fields: tuple[str, ...],
    metrics_events_status: str,
) -> str:
    if missing_source_ledger_fields or "source_ledger_schema.csv" in missing_required_artifacts:
        return THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SOURCE_LEDGER
    if missing_required_artifacts or missing_metric_fields or missing_event_fields:
        return THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SCHEMA
    if metrics_events_status != "present":
        return THREE_HIVE_RING_PREFLIGHT_STATUS_NO_METRICS_EVENTS
    return THREE_HIVE_RING_PREFLIGHT_STATUS_ELIGIBLE


def _row_interpretation(status: str) -> str:
    if status == THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SOURCE_LEDGER:
        return "source-ledger schema is incomplete; no three-hive interpretation is allowed"
    if status == THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SCHEMA:
        return "schema artifacts are incomplete; no three-hive interpretation is allowed"
    if status == THREE_HIVE_RING_PREFLIGHT_STATUS_NO_METRICS_EVENTS:
        return "schema/source-ledger artifacts pass, but simulator metrics/events are absent"
    return "schema/source-ledger and metrics/events are present; mechanics gate review is still required"


def _overall_status(rows: list[dict[str, str | int]]) -> str:
    if _missing_condition_seed_pairs(rows):
        return THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_COVERAGE
    statuses = {str(row["status"]) for row in rows}
    if THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SOURCE_LEDGER in statuses:
        return THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SOURCE_LEDGER
    if THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SCHEMA in statuses:
        return THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SCHEMA
    if THREE_HIVE_RING_PREFLIGHT_STATUS_NO_METRICS_EVENTS in statuses:
        return THREE_HIVE_RING_PREFLIGHT_STATUS_NO_METRICS_EVENTS
    if statuses == {THREE_HIVE_RING_PREFLIGHT_STATUS_ELIGIBLE}:
        return THREE_HIVE_RING_PREFLIGHT_STATUS_ELIGIBLE
    return THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SCHEMA


def _manifest_row(
    compare_path: Path,
    output_path: Path,
    rows: list[dict[str, str | int]],
    status: str,
) -> dict[str, str | int]:
    expected_seeds = tuple(THREE_HIVE_RING_SMOKE_PARAMETERS["seeds"])
    observed_conditions = sorted({str(row["condition"]) for row in rows})
    observed_seeds = sorted({int(row["seed"]) for row in rows})
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "expected_condition_count": len(THREE_HIVE_RING_CONDITIONS),
        "observed_condition_count": len(observed_conditions),
        "expected_seed_count": len(expected_seeds),
        "observed_seed_count": len(observed_seeds),
        "expected_run_count": len(THREE_HIVE_RING_CONDITIONS) * len(expected_seeds),
        "observed_run_count": len(rows),
        "missing_condition_seed_pairs": "|".join(_missing_condition_seed_pairs(rows)),
        "schema_pass_count": sum(
            1
            for row in rows
            if str(row["status"])
            in {
                THREE_HIVE_RING_PREFLIGHT_STATUS_NO_METRICS_EVENTS,
                THREE_HIVE_RING_PREFLIGHT_STATUS_ELIGIBLE,
            }
        ),
        "metrics_events_present_count": sum(
            1 for row in rows if row["metrics_events_status"] == "present"
        ),
        "status": status,
    }


def _missing_condition_seed_pairs(rows: list[dict[str, str | int]]) -> tuple[str, ...]:
    observed = {(str(row["condition"]), int(row["seed"])) for row in rows}
    expected = {
        (condition, int(seed))
        for condition in THREE_HIVE_RING_CONDITIONS
        for seed in THREE_HIVE_RING_SMOKE_PARAMETERS["seeds"]
    }
    return tuple(
        f"{condition}:seed{seed}"
        for condition, seed in sorted(expected - observed)
    )


def _summary(
    compare_path: Path,
    completeness_rows: list[dict[str, str | int]],
    manifest_row: dict[str, str | int],
) -> str:
    return "\n".join(
        [
            "# Three-Hive Ring Preflight",
            "",
            f"- Compare dir: `{compare_path}`",
            f"- Runs inspected: {len(completeness_rows)}",
            f"- Schema-pass rows: {manifest_row['schema_pass_count']}",
            f"- Metrics/events-present rows: {manifest_row['metrics_events_present_count']}",
            f"- Status: `{manifest_row['status']}`",
            "",
            "This analyzer is read-only. It checks condition/seed coverage,",
            "schema completeness, and source-ledger schema availability.",
            "It does not run the simulator. It does not fabricate metrics/events, compute promotion",
            "endpoints, or create three-hive scientific evidence.",
            "",
        ]
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


def _ensure_output_paths_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    if (output_path / "three_hive_ring_preflight_manifest.csv").exists():
        raise FileExistsError(
            f"Output path {output_path} already contains three-hive ring preflight artifacts."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only preflight analyzer for three-hive ring artifacts."
    )
    parser.add_argument(
        "--compare-dir",
        default=str(DEFAULT_THREE_HIVE_RING_SCHEMA_SMOKE_DIR),
        help="Existing three-hive ring schema/source-ledger artifact directory.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_THREE_HIVE_RING_PREFLIGHT_DIR),
        help="Output directory for preflight analyzer artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_three_hive_ring_preflight_analysis(
            compare_dir=args.compare_dir,
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
