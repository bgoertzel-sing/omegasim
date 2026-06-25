"""A4 smoke-contract preflight analyzer."""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from ohdyn.run import run_experiment
from ohdyn.sim import COUPLING_EVENT_FIELDS, CROSS_HIVE_METRIC_FIELDS, HIVE_EVENT_FIELDS


A4_SMOKE_MODES: tuple[str, ...] = ("none", "direct", "delayed", "shuffled")
A4_SMOKE_CONFIGS: dict[str, Path] = {
    "none": Path("configs/a4_two_hive_none_smoke.yaml"),
    "direct": Path("configs/a4_two_hive_direct_smoke.yaml"),
    "delayed": Path("configs/a4_two_hive_delayed_smoke.yaml"),
    "shuffled": Path("configs/a4_two_hive_shuffled_smoke.yaml"),
}
A4_SMOKE_ARTIFACTS: tuple[str, ...] = (
    "config.yaml",
    "manifest.yaml",
    "metrics.csv",
    "events.csv",
    "summary.md",
    "hive_metrics.csv",
    "cross_hive_metrics.csv",
    "hive_events.csv",
    "coupling_events.csv",
)
A4_PREFLIGHT_DEFAULT_OUT = Path("docs/results/a4_smoke_contract_preflight.md")


def run_a4_smoke_contract_preflight(
    *,
    out: str | Path = A4_PREFLIGHT_DEFAULT_OUT,
    work_dir: str | Path | None = None,
    seed: int = 31,
) -> dict[str, Any]:
    """Run A4 smoke fixtures and write a deterministic readiness report."""

    if seed < 0:
        raise ValueError("seed must be non-negative.")
    out_path = Path(out)
    if out_path.exists():
        raise FileExistsError(f"Output report already exists: {out_path}")

    if work_dir is None:
        with tempfile.TemporaryDirectory(prefix="omegasim_a4_preflight_") as tmp:
            return _run_preflight(out_path=out_path, work_path=Path(tmp), seed=seed)

    work_path = Path(work_dir)
    if work_path.exists():
        raise FileExistsError(f"Work directory already exists: {work_path}")
    work_path.mkdir(parents=True)
    try:
        return _run_preflight(out_path=out_path, work_path=work_path, seed=seed)
    except Exception:
        shutil.rmtree(work_path, ignore_errors=True)
        raise


def _run_preflight(*, out_path: Path, work_path: Path, seed: int) -> dict[str, Any]:
    first_dirs: dict[str, Path] = {}
    second_dirs: dict[str, Path] = {}
    mode_results = []

    for mode in A4_SMOKE_MODES:
        first = work_path / f"{mode}_first"
        second = work_path / f"{mode}_second"
        run_experiment(A4_SMOKE_CONFIGS[mode], seed, first)
        run_experiment(A4_SMOKE_CONFIGS[mode], seed, second)
        first_dirs[mode] = first
        second_dirs[mode] = second
        mode_results.append(_analyze_mode(mode, first, second))

    shuffled = next(result for result in mode_results if result["mode"] == "shuffled")
    direct = next(result for result in mode_results if result["mode"] == "direct")
    shuffled["checks"]["paired direct source-attempt marginals"] = (
        shuffled["source_attempts"] == direct["source_attempts"]
        and shuffled["transfer_attempts"] == direct["transfer_attempts"]
    )
    shuffled["notes"].append(
        "Two-hive shuffled is a schema/conservation control; target choice degenerates to the only non-source hive."
    )

    all_checks = [
        passed
        for result in mode_results
        for passed in result["checks"].values()
    ]
    report = _format_report(seed=seed, mode_results=mode_results)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)
    return {
        "out": str(out_path),
        "seed": seed,
        "passed": all(all_checks),
        "mode_results": mode_results,
    }


def _analyze_mode(mode: str, first: Path, second: Path) -> dict[str, Any]:
    manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    config = yaml.safe_load((first / "config.yaml").read_text())
    hive_rows = _read_csv(first / "hive_metrics.csv")
    cross_rows = _read_csv(first / "cross_hive_metrics.csv")
    hive_events = _read_csv(first / "hive_events.csv")
    coupling_events = _read_csv(first / "coupling_events.csv")
    metrics_rows = _read_csv(first / "metrics.csv")

    checks: dict[str, bool] = {
        "artifact set present": all((first / artifact).exists() for artifact in A4_SMOKE_ARTIFACTS),
        "same-seed artifacts byte-identical": _artifact_bytes_equal(first, second),
        "manifest/config provenance": _provenance_valid(mode, manifest, config),
        "CSV schemas stable": _schemas_valid(cross_rows, hive_events, coupling_events),
        "per-hive queue conservation": _per_hive_conservation_holds(hive_rows),
        "aggregate transfer conservation": _aggregate_conservation_holds(
            mode,
            cross_rows,
            coupling_events,
        ),
        "mode semantics": _mode_semantics_hold(mode, coupling_events),
        "endpoint table computable": _endpoints_computable(hive_rows, cross_rows, metrics_rows),
    }
    endpoints = _endpoint_summary(hive_rows, cross_rows)
    return {
        "mode": mode,
        "checks": checks,
        "transfer_attempts": len(coupling_events),
        "source_attempts": dict(Counter(row["source_hive_id"] for row in coupling_events)),
        "endpoint_summary": endpoints,
        "notes": [],
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _artifact_bytes_equal(first: Path, second: Path) -> bool:
    return all(
        (first / artifact).read_bytes() == (second / artifact).read_bytes()
        for artifact in A4_SMOKE_ARTIFACTS
    )


def _provenance_valid(mode: str, manifest: dict[str, Any], config: dict[str, Any]) -> bool:
    return (
        manifest.get("hive_count") == 2
        and manifest.get("hive_ids") == ["hive_a", "hive_b"]
        and manifest.get("coupling_mode") == mode
        and manifest.get("model", {}).get("multi_hive", {}).get("coupling_mode") == mode
        and config.get("coupling", {}).get("mode") == mode
        and [hive.get("hive_id") for hive in config.get("hives", [])] == ["hive_a", "hive_b"]
    )


def _schemas_valid(
    cross_rows: list[dict[str, str]],
    hive_events: list[dict[str, str]],
    coupling_events: list[dict[str, str]],
) -> bool:
    cross_header = tuple(cross_rows[0].keys()) if cross_rows else ()
    hive_event_header = tuple(hive_events[0].keys()) if hive_events else ()
    coupling_header = tuple(coupling_events[0].keys()) if coupling_events else tuple(COUPLING_EVENT_FIELDS)
    return (
        all(field in cross_header for field in CROSS_HIVE_METRIC_FIELDS)
        and all(field in hive_event_header for field in HIVE_EVENT_FIELDS)
        and coupling_header == tuple(COUPLING_EVENT_FIELDS)
    )


def _per_hive_conservation_holds(hive_rows: list[dict[str, str]]) -> bool:
    for row in hive_rows:
        created = _int(row["tasks_created_tick"])
        inbound = _int(row["inbound_transfers_tick"])
        completed = _int(row["tasks_completed_tick"])
        outbound = _int(row["outbound_transfers_tick"])
        drops = _int(row["explicit_drops_tick"])
        delta = _int(row["queue_delta_tick"])
        residual = _int(row["queue_balance_residual_tick"])
        if residual != 0 or delta != created + inbound - completed - outbound - drops:
            return False
    return True


def _aggregate_conservation_holds(
    mode: str,
    cross_rows: list[dict[str, str]],
    coupling_events: list[dict[str, str]],
) -> bool:
    for row in cross_rows:
        if _int(row["aggregate_queue_balance_residual_tick"]) != 0:
            return False
    total_inbound = sum(_int(row["aggregate_inbound_transfers_tick"]) for row in cross_rows)
    total_outbound = sum(_int(row["aggregate_outbound_transfers_tick"]) for row in cross_rows)
    if mode in {"none", "direct", "shuffled"}:
        return total_inbound == total_outbound == len(coupling_events)
    if mode == "delayed":
        delivered = sum(
            1
            for event in coupling_events
            if int(event["arrival_tick"]) < len(cross_rows)
        )
        return total_outbound == len(coupling_events) and total_inbound == delivered
    return True


def _mode_semantics_hold(mode: str, coupling_events: list[dict[str, str]]) -> bool:
    if mode == "none":
        return coupling_events == []
    if not coupling_events:
        return False
    if {row["coupling_mode"] for row in coupling_events} != {mode}:
        return False
    if {row["transfer_decision"] for row in coupling_events} != {"True"}:
        return False
    if any(row["source_hive_id"] == row["target_hive_id"] for row in coupling_events):
        return False
    if mode in {"direct", "shuffled"}:
        return all(row["delay_ticks"] == "0" and row["arrival_tick"] == row["tick"] for row in coupling_events)
    if mode == "delayed":
        return all(
            int(row["delay_ticks"]) > 0
            and int(row["arrival_tick"]) == int(row["tick"]) + int(row["delay_ticks"])
            for row in coupling_events
        )
    return False


def _endpoints_computable(
    hive_rows: list[dict[str, str]],
    cross_rows: list[dict[str, str]],
    metrics_rows: list[dict[str, str]],
) -> bool:
    required_hive_fields = {
        "hive_id",
        "tasks_created_total",
        "tasks_completed_total",
        "queue_depth",
        "queued_task_age_mean_tick",
        "queued_task_age_max_tick",
        "tasks_worked_tick",
        "messages_sent_tick",
        "tasks_created_tick",
        "idle_tick",
        "inbound_transfers_tick",
        "outbound_transfers_tick",
    }
    required_cross_fields = {
        "queued_age_mean_divergence_tick",
        "completion_fraction_divergence_tick",
        "hive_a_load_normalized_backlog_tick",
        "hive_b_load_normalized_backlog_tick",
    }
    return (
        bool(hive_rows)
        and bool(cross_rows)
        and bool(metrics_rows)
        and required_hive_fields.issubset(hive_rows[0])
        and required_cross_fields.issubset(cross_rows[0])
    )


def _endpoint_summary(
    hive_rows: list[dict[str, str]],
    cross_rows: list[dict[str, str]],
) -> dict[str, Any]:
    by_hive: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in hive_rows:
        by_hive[row["hive_id"]].append(row)
    per_hive = {}
    for hive_id, rows in sorted(by_hive.items()):
        last = rows[-1]
        created = int(last["tasks_created_total"])
        completed = int(last["tasks_completed_total"])
        per_hive[hive_id] = {
            "created": created,
            "completed": completed,
            "completion_fraction": _safe_ratio(completed, created),
            "load_normalized_backlog": _safe_ratio(int(last["queue_depth"]), created),
            "queued_age_mean_final": float(last["queued_task_age_mean_tick"]),
            "queued_age_max_final": int(last["queued_task_age_max_tick"]),
            "work_events": sum(int(row["tasks_worked_tick"]) for row in rows),
            "inbound_transfers": sum(_int(row["inbound_transfers_tick"]) for row in rows),
            "outbound_transfers": sum(_int(row["outbound_transfers_tick"]) for row in rows),
        }
    return {
        "per_hive": per_hive,
        "load_backlog_correlation": _correlation(
            [float(row["hive_a_load_normalized_backlog_tick"]) for row in cross_rows],
            [float(row["hive_b_load_normalized_backlog_tick"]) for row in cross_rows],
        ),
        "queued_age_divergence_final": float(cross_rows[-1]["queued_age_mean_divergence_tick"]),
        "completion_fraction_divergence_final": float(
            cross_rows[-1]["completion_fraction_divergence_tick"]
        ),
    }


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _int(value: str) -> int:
    if value == "":
        return 0
    return int(value)


def _correlation(left: list[float], right: list[float]) -> str:
    if len(left) < 2 or len(right) < 2:
        return "NA"
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    left_ss = sum((value - left_mean) ** 2 for value in left)
    right_ss = sum((value - right_mean) ** 2 for value in right)
    if left_ss == 0.0 or right_ss == 0.0:
        return "NA"
    covariance = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right, strict=True))
    return f"{covariance / math.sqrt(left_ss * right_ss):.6f}"


def _format_report(*, seed: int, mode_results: list[dict[str, Any]]) -> str:
    lines = [
        "# A4 Smoke Contract Preflight",
        "",
        f"- smoke seed: {seed}",
        "- scientific holdout seeds run: none",
        "- scope: read-only smoke artifact contract, schema, conservation, and endpoint-computability checks",
        "",
        "## Readiness checks",
        "",
        "| mode | artifact set | reproducible | provenance | schemas | per-hive conservation | aggregate conservation | mode semantics | endpoints |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in mode_results:
        checks = result["checks"]
        lines.append(
            "| {mode} | {artifact} | {repro} | {prov} | {schemas} | {hive} | {agg} | {sem} | {endpoints} |".format(
                mode=result["mode"],
                artifact=_mark(checks["artifact set present"]),
                repro=_mark(checks["same-seed artifacts byte-identical"]),
                prov=_mark(checks["manifest/config provenance"]),
                schemas=_mark(checks["CSV schemas stable"]),
                hive=_mark(checks["per-hive queue conservation"]),
                agg=_mark(checks["aggregate transfer conservation"]),
                sem=_mark(checks["mode semantics"]),
                endpoints=_mark(checks["endpoint table computable"]),
            )
        )
    lines.extend(
        [
            "",
            "## Smoke endpoint dry run",
            "",
            "| mode | hive | created | completed | completion_fraction | load_normalized_backlog | final_mean_age | work_events | inbound | outbound |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for result in mode_results:
        for hive_id, row in result["endpoint_summary"]["per_hive"].items():
            lines.append(
                "| {mode} | {hive} | {created} | {completed} | {completion_fraction:.6f} | {load_normalized_backlog:.6f} | {age:.6f} | {work_events} | {inbound} | {outbound} |".format(
                    mode=result["mode"],
                    hive=hive_id,
                    created=row["created"],
                    completed=row["completed"],
                    completion_fraction=row["completion_fraction"],
                    load_normalized_backlog=row["load_normalized_backlog"],
                    age=row["queued_age_mean_final"],
                    work_events=row["work_events"],
                    inbound=row["inbound_transfers"],
                    outbound=row["outbound_transfers"],
                )
            )
    lines.extend(
        [
            "",
            "## Cross-hive computability",
            "",
            "| mode | load_backlog_correlation | final_queued_age_divergence | final_completion_fraction_divergence | transfer_attempts |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for result in mode_results:
        summary = result["endpoint_summary"]
        lines.append(
            "| {mode} | {corr} | {age:.6f} | {completion:.6f} | {attempts} |".format(
                mode=result["mode"],
                corr=summary["load_backlog_correlation"],
                age=summary["queued_age_divergence_final"],
                completion=summary["completion_fraction_divergence_final"],
                attempts=result["transfer_attempts"],
            )
        )
    lines.extend(
        [
            "",
            "## Shuffled control limitation",
            "",
            f"- paired direct source-attempt marginals: {_mark(next(result for result in mode_results if result['mode'] == 'shuffled')['checks'].get('paired direct source-attempt marginals', False))}",
            "- Two-hive shuffled has only one legal target per source hive, so target assignment is structurally equivalent to the only non-source hive and is not a meaningful phase-structure null.",
            "",
            "## Interpretation boundary",
            "",
            "- PASS means the smoke artifact contract is analyzable; it is not evidence for A4 scientific effects.",
            "- A4 holdout seeds remain blocked until this preflight report is reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def _mark(value: bool) -> str:
    return "PASS" if value else "FAIL"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the A4 smoke-contract preflight analyzer.")
    parser.add_argument("--out", default=str(A4_PREFLIGHT_DEFAULT_OUT), help="Markdown report path.")
    parser.add_argument("--work-dir", default=None, help="Optional directory for generated smoke artifacts.")
    parser.add_argument("--seed", type=int, default=31, help="Deterministic smoke seed.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a4_smoke_contract_preflight(out=args.out, work_dir=args.work_dir, seed=args.seed)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
