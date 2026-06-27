"""Read-only A7 semantic-field analyzer skeleton.

The first A7 gate must fail closed until simulator artifacts expose the frozen
schema from ``ohdyn.a7_semantic_field_contract``. This module does not rerun
simulations or infer missing fields.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.a7_semantic_field_contract import (
    A7_ANALYZER_COMPLETENESS_FIELDS,
    A7_ANALYZER_MANIFEST_FIELDS,
    A7_CONDITIONS,
    A7_SOURCE_COMPONENTS,
    a7_required_event_fields,
    a7_required_metric_fields,
    missing_fields,
)


DEFAULT_A7_COMPARE_DIR = Path("runs/a7_semantic_field_compare")
DEFAULT_A7_OUT_DIR = Path("runs/a7_semantic_field_analysis")
_A7_OUTPUT_NAMES = (
    "a7_semantic_field_completeness.csv",
    "a7_semantic_field_manifest.csv",
    "summary.md",
)


def run_a7_semantic_field_analysis(
    compare_dir: str | Path = DEFAULT_A7_COMPARE_DIR,
    out_dir: str | Path = DEFAULT_A7_OUT_DIR,
) -> dict[str, Any]:
    """Inspect existing A7 artifacts and fail closed on absent schema."""

    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs = _read_runs(compare_path)
    completeness_rows = [_completeness_row(run) for run in runs]
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    status = _overall_status(completeness_rows, conditions)
    manifest_rows = [
        {
            "compare_dir": str(compare_path),
            "condition_count": len(conditions),
            "seed_count": len(seeds),
            "run_count": len(runs),
            "status": status,
        }
    ]

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "a7_semantic_field_completeness.csv",
        completeness_rows,
        A7_ANALYZER_COMPLETENESS_FIELDS,
    )
    _write_csv(
        output_path / "a7_semantic_field_manifest.csv",
        manifest_rows,
        A7_ANALYZER_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(compare_path, completeness_rows, manifest_rows[0])
    )
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "condition_count": len(conditions),
        "seed_count": len(seeds),
        "run_count": len(runs),
        "status": status,
    }


def _read_runs(compare_path: Path) -> list[dict[str, Any]]:
    if not compare_path.exists():
        raise FileNotFoundError(f"A7 comparison directory does not exist: {compare_path}")
    runs: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        manifest_path = run_dir / "manifest.yaml"
        if not manifest_path.exists():
            continue
        manifest = yaml.safe_load(manifest_path.read_text()) or {}
        config = manifest.get("config", {})
        semantic_field = config.get("semantic_field", {})
        condition = semantic_field.get("condition") or _condition_from_name(run_dir.name)
        seed = int(manifest.get("seed", _seed_from_name(run_dir.name)))
        runs.append(
            {
                "condition": condition,
                "seed": seed,
                "metrics_path": run_dir / "metrics.csv",
                "events_path": run_dir / "events.csv",
            }
        )
    return runs


def _condition_from_name(name: str) -> str:
    for condition in A7_CONDITIONS:
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
    metrics_path = Path(run["metrics_path"])
    events_path = Path(run["events_path"])
    metric_header, row_count = _csv_header_and_row_count(metrics_path)
    event_header, _ = _csv_header_and_row_count(events_path)
    missing = (
        *missing_fields(metric_header, a7_required_metric_fields()),
        *missing_fields(event_header, a7_required_event_fields()),
    )
    required_status = "pass" if not missing else "missing_fields"
    source_status = (
        _source_reconstruction_status(events_path) if not missing else "not_evaluable"
    )
    null_status = "not_evaluable"
    status = (
        "fail_closed"
        if missing or source_status != "pass"
        else "schema_present_analysis_not_implemented"
    )
    interpretation = (
        "A7 artifacts are absent or incomplete; no semantic-field interpretation is allowed."
        if missing
        else "A7 source ledger does not reconstruct field deltas; no semantic-field interpretation is allowed."
        if source_status != "pass"
        else "A7 schema is present; residual recurrence and null contrasts remain unimplemented."
    )
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "metrics_path": str(metrics_path),
        "events_path": str(events_path),
        "row_count": row_count,
        "required_field_status": required_status,
        "missing_required_fields": "|".join(missing),
        "source_reconstruction_status": source_status,
        "null_artifact_status": null_status,
        "status": status,
        "interpretation": interpretation,
    }


def _csv_header_and_row_count(path: Path) -> tuple[frozenset[str], int]:
    if not path.exists():
        return frozenset(), 0
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return frozenset(reader.fieldnames or ()), sum(1 for _ in reader)


def _source_reconstruction_status(path: Path) -> str:
    if not path.exists():
        return "missing_events"
    checked = 0
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("event_type") != "a7_semantic_field_update":
                continue
            checked += 1
            source_sum = sum(
                _float_cell(row.get(f"a7_delta_{source}", "0"))
                for source in A7_SOURCE_COMPONENTS
            )
            total = _float_cell(row.get("a7_delta_total", "0"))
            if round(source_sum, 6) != round(total, 6):
                return "fail"
    return "pass" if checked else "no_a7_update_events"


def _float_cell(value: str | None) -> float:
    if value in {None, ""}:
        return 0.0
    return float(value)


def _overall_status(rows: list[dict[str, str | int]], conditions: list[str]) -> str:
    if not rows:
        return "fail_closed_no_runs"
    missing_conditions = set(A7_CONDITIONS) - set(conditions)
    if missing_conditions:
        return "fail_closed_missing_conditions"
    if any(row["status"] == "fail_closed" for row in rows):
        return "fail_closed_missing_schema"
    return "schema_present_analysis_not_implemented"


def _ensure_output_paths_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [name for name in _A7_OUTPUT_NAMES if (output_path / name).exists()]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains artifacts: {names}")


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: tuple[str, ...],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    compare_path: Path,
    rows: list[dict[str, str | int]],
    manifest: dict[str, str | int],
) -> str:
    fail_closed = sum(1 for row in rows if row["status"] == "fail_closed")
    return "\n".join(
        [
            "# A7 Semantic-Field Analysis Skeleton",
            "",
            f"- Compare directory: `{compare_path}`",
            f"- Runs inspected: {manifest['run_count']}",
            f"- Status: `{manifest['status']}`",
            f"- Fail-closed rows: {fail_closed}",
            "",
            "This analyzer is read-only and intentionally refuses positive interpretation",
            "until A7 artifacts expose the frozen schema and all preregistered nulls.",
            "When required schema is missing, no semantic-field interpretation is allowed.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fail-closed read-only A7 semantic-field analyzer skeleton."
    )
    parser.add_argument("--compare-dir", default=str(DEFAULT_A7_COMPARE_DIR))
    parser.add_argument("--out", default=str(DEFAULT_A7_OUT_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    run_a7_semantic_field_analysis(args.compare_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
