"""Read-only A7.3 artifact/source-ledger preflight analyzer."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.a7_3_dimensionless_contract import (
    A7_3_ACTIONS,
    A7_3_CONDITIONS,
    A7_3_LIFTED_STATE_FIELDS,
    A7_3_PRODUCTIVITY_GUARDRAILS,
    A7_3_SMOKE_PARAMETERS,
    A7_3_SOURCE_LEDGER_CSV_FIELDS,
    A7_3_SOURCE_LEDGER_FIELDS,
    a7_3_required_event_fields,
    a7_3_required_metric_fields,
)
from ohdyn.compare_a7_3_dimensionless_delayed import DEFAULT_A7_3_SMOKE_DIR


DEFAULT_A7_3_PREFLIGHT_DIR = Path("runs/a7_3_preflight_seed1_2")
A7_3_PREFLIGHT_STATUS_ELIGIBLE = "eligible_for_read_only_residual_analysis"
A7_3_PREFLIGHT_STATUS_MISSING_COVERAGE = "fail_closed_missing_condition_seed_coverage"
A7_3_PREFLIGHT_STATUS_MISSING_SCHEMA = "fail_closed_missing_schema_or_artifacts"
A7_3_PREFLIGHT_STATUS_SOURCE_LEDGER = "fail_closed_source_ledger_integrity"
A7_3_PREFLIGHT_STATUS_GUARDRAILS = "fail_closed_boundedness_or_productivity"

A7_3_PREFLIGHT_COMPLETENESS_FIELDS = (
    "condition",
    "seed",
    "run_dir",
    "metric_row_count",
    "event_row_count",
    "source_ledger_row_count",
    "lifted_state_row_count",
    "required_artifact_status",
    "metric_schema_status",
    "event_schema_status",
    "source_ledger_schema_status",
    "lifted_state_schema_status",
    "missing_required_fields",
    "status",
    "interpretation",
)
A7_3_PREFLIGHT_SOURCE_LEDGER_FIELDS = (
    "condition",
    "seed",
    "delay_integrity_status",
    "peer_lag_status",
    "same_tick_block_status",
    "shuffle_status",
    "clip_residual_status",
    "status",
    "interpretation",
)
A7_3_PREFLIGHT_GUARDRAIL_FIELDS = (
    "condition",
    "seed",
    "boundedness_status",
    "completion_fraction_mean",
    "completion_fraction_status",
    "work_backlog_max",
    "work_backlog_status",
    "prediction_spend_fraction_max",
    "prediction_spend_fraction_status",
    "status",
    "interpretation",
)
A7_3_PREFLIGHT_MANIFEST_FIELDS = (
    "compare_dir",
    "out_dir",
    "expected_condition_count",
    "observed_condition_count",
    "expected_seed_count",
    "observed_seed_count",
    "expected_run_count",
    "observed_run_count",
    "missing_condition_seed_pairs",
    "completeness_pass_count",
    "source_ledger_pass_count",
    "guardrail_pass_count",
    "status",
)
_OUTPUT_NAMES = (
    "a7_3_preflight_completeness.csv",
    "a7_3_preflight_source_ledger.csv",
    "a7_3_preflight_guardrails.csv",
    "a7_3_preflight_manifest.csv",
    "summary.md",
)
_BOUNDED_0_1_FIELDS = (
    "agent_role_activity_predict",
    "agent_role_activity_work",
    "agent_role_activity_review",
    "agent_role_activity_synthesize",
    "agent_role_activity_rest",
    "delayed_agent_role_activity_predict",
    "delayed_agent_role_activity_work",
    "delayed_agent_role_activity_review",
    "delayed_agent_role_activity_synthesize",
    "delayed_agent_role_activity_rest",
    "peer_activity_lag_predict",
    "peer_activity_lag_work",
    "peer_activity_lag_review",
    "peer_activity_lag_synthesize",
    "peer_activity_lag_rest",
    "artifact_readiness",
    "artifact_coherence",
    "contradiction_risk",
    "prediction_error",
    "prediction_uncertainty",
    "fatigue",
    "memory_pressure",
)
_THRESHOLD_FIELDS = (
    "adaptive_threshold_predict",
    "adaptive_threshold_work",
    "adaptive_threshold_review",
    "adaptive_threshold_synthesize",
    "adaptive_threshold_rest",
)


def run_a7_3_preflight_analysis(
    compare_dir: str | Path = DEFAULT_A7_3_SMOKE_DIR,
    out_dir: str | Path = DEFAULT_A7_3_PREFLIGHT_DIR,
) -> dict[str, Any]:
    """Inspect existing A7.3 smoke artifacts without rerunning simulations."""

    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs = _read_runs(compare_path)
    completeness_rows = [_completeness_row(run) for run in runs]
    source_ledger_rows = [_source_ledger_row(run) for run in runs]
    guardrail_rows = [_guardrail_row(run) for run in runs]
    status = _overall_status(completeness_rows, source_ledger_rows, guardrail_rows)
    manifest_row = _manifest_row(
        compare_path,
        output_path,
        completeness_rows,
        source_ledger_rows,
        guardrail_rows,
        status,
    )

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "a7_3_preflight_completeness.csv",
        completeness_rows,
        A7_3_PREFLIGHT_COMPLETENESS_FIELDS,
    )
    _write_csv(
        output_path / "a7_3_preflight_source_ledger.csv",
        source_ledger_rows,
        A7_3_PREFLIGHT_SOURCE_LEDGER_FIELDS,
    )
    _write_csv(
        output_path / "a7_3_preflight_guardrails.csv",
        guardrail_rows,
        A7_3_PREFLIGHT_GUARDRAIL_FIELDS,
    )
    _write_csv(
        output_path / "a7_3_preflight_manifest.csv",
        [manifest_row],
        A7_3_PREFLIGHT_MANIFEST_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(compare_path, completeness_rows, source_ledger_rows, guardrail_rows, manifest_row)
    )
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "run_count": len(runs),
        "status": status,
    }


def _read_runs(compare_path: Path) -> list[dict[str, Any]]:
    if not compare_path.exists():
        raise FileNotFoundError(f"A7.3 smoke directory does not exist: {compare_path}")
    runs: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        manifest = _read_manifest(run_dir / "manifest.yaml")
        condition = str(manifest.get("condition") or _condition_from_name(run_dir.name))
        seed = int(manifest.get("seed", _seed_from_name(run_dir.name)))
        runs.append(
            {
                "condition": condition,
                "seed": seed,
                "run_dir": run_dir,
                "manifest": manifest,
                "metrics_path": run_dir / "metrics.csv",
                "events_path": run_dir / "events.csv",
                "source_ledger_path": run_dir / "source_ledger.csv",
                "lifted_state_path": run_dir / "lifted_state.csv",
                "metrics": _read_csv_rows(run_dir / "metrics.csv"),
                "events": _read_csv_rows(run_dir / "events.csv"),
                "source_ledger": _read_csv_rows(run_dir / "source_ledger.csv"),
                "lifted_state": _read_csv_rows(run_dir / "lifted_state.csv"),
            }
        )
    return runs


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def _condition_from_name(name: str) -> str:
    for condition in A7_3_CONDITIONS:
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
    metric_header, metric_rows = _csv_header_and_row_count(Path(run["metrics_path"]))
    event_header, event_rows = _csv_header_and_row_count(Path(run["events_path"]))
    source_header, source_rows = _csv_header_and_row_count(Path(run["source_ledger_path"]))
    lifted_header, lifted_rows = _csv_header_and_row_count(Path(run["lifted_state_path"]))
    missing_artifacts = [
        path.name
        for path in (
            Path(run["metrics_path"]),
            Path(run["events_path"]),
            Path(run["source_ledger_path"]),
            Path(run["lifted_state_path"]),
        )
        if not path.exists()
    ]
    missing = (
        *missing_fields(metric_header, ("condition", "seed", *a7_3_required_metric_fields())),
        *missing_fields(event_header, a7_3_required_event_fields()),
        *missing_fields(source_header, A7_3_SOURCE_LEDGER_CSV_FIELDS),
        *missing_fields(lifted_header, ("condition", "seed", *A7_3_LIFTED_STATE_FIELDS)),
    )
    expected_rows = _expected_rows_for_run(run)
    row_counts_ok = all(
        count == expected_rows for count in (metric_rows, event_rows, source_rows, lifted_rows)
    )
    status = "pass" if not missing_artifacts and not missing and row_counts_ok else "fail_closed"
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "run_dir": str(run["run_dir"]),
        "metric_row_count": metric_rows,
        "event_row_count": event_rows,
        "source_ledger_row_count": source_rows,
        "lifted_state_row_count": lifted_rows,
        "required_artifact_status": "pass" if not missing_artifacts else "missing:" + "|".join(missing_artifacts),
        "metric_schema_status": "pass" if not missing_fields(metric_header, a7_3_required_metric_fields()) else "missing_fields",
        "event_schema_status": "pass" if not missing_fields(event_header, a7_3_required_event_fields()) else "missing_fields",
        "source_ledger_schema_status": "pass" if not missing_fields(source_header, A7_3_SOURCE_LEDGER_CSV_FIELDS) else "missing_fields",
        "lifted_state_schema_status": "pass" if not missing_fields(lifted_header, ("condition", "seed", *A7_3_LIFTED_STATE_FIELDS)) else "missing_fields",
        "missing_required_fields": "|".join(missing),
        "status": status,
        "interpretation": (
            "A7.3 artifacts are complete for preflight review"
            if status == "pass"
            else "A7.3 artifacts are incomplete; no A7.3 interpretation is allowed"
        ),
    }


def _expected_rows_for_run(run: dict[str, Any]) -> int:
    manifest = run.get("manifest") or {}
    return int(manifest.get("ticks") or A7_3_SMOKE_PARAMETERS["horizon_ticks"])


def _source_ledger_row(run: dict[str, Any]) -> dict[str, str | int]:
    metrics = run["metrics"]
    events = run["events"]
    source_rows = run["source_ledger"]
    condition = str(run["condition"])
    delay_status = _delay_integrity_status(condition, source_rows, events)
    peer_status = _peer_lag_status(condition, metrics, source_rows)
    same_tick_status = _same_tick_block_status(condition, events)
    shuffle_status = _shuffle_status(condition, source_rows)
    clip_status = _clip_residual_status(metrics, source_rows)
    status = (
        "pass"
        if all(
            item == "pass"
            for item in (delay_status, peer_status, same_tick_status, shuffle_status, clip_status)
        )
        else "fail_closed"
    )
    return {
        "condition": condition,
        "seed": int(run["seed"]),
        "delay_integrity_status": delay_status,
        "peer_lag_status": peer_status,
        "same_tick_block_status": same_tick_status,
        "shuffle_status": shuffle_status,
        "clip_residual_status": clip_status,
        "status": status,
        "interpretation": (
            "source ledger delay and null-control provenance pass preflight"
            if status == "pass"
            else "source ledger delay/provenance failed; no A7.3 interpretation is allowed"
        ),
    }


def _guardrail_row(run: dict[str, Any]) -> dict[str, str | int | float]:
    metrics = run["metrics"]
    bounded_status = _boundedness_status(metrics)
    completion_values = [_float_cell(row.get("completion_fraction")) for row in metrics]
    backlog_values = [_float_cell(row.get("work_backlog")) for row in metrics]
    spend_fractions = [
        _float_cell(row.get("prediction_spend")) / max(_float_cell(row.get("work_budget")), 1e-9)
        for row in metrics
    ]
    completion_mean = sum(completion_values) / len(completion_values) if completion_values else 0.0
    backlog_max = max(backlog_values) if backlog_values else 0.0
    spend_fraction_max = max(spend_fractions) if spend_fractions else 0.0
    completion_status = (
        "pass"
        if completion_mean >= float(A7_3_PRODUCTIVITY_GUARDRAILS["completion_fraction_min"])
        else "fail"
    )
    backlog_status = (
        "pass"
        if backlog_max <= float(A7_3_PRODUCTIVITY_GUARDRAILS["work_backlog_max"])
        else "fail"
    )
    spend_status = (
        "pass"
        if spend_fraction_max <= float(A7_3_PRODUCTIVITY_GUARDRAILS["prediction_spend_fraction_max"])
        else "fail"
    )
    status = (
        "pass"
        if all(
            item == "pass"
            for item in (bounded_status, completion_status, backlog_status, spend_status)
        )
        else "fail_closed"
    )
    return {
        "condition": str(run["condition"]),
        "seed": int(run["seed"]),
        "boundedness_status": bounded_status,
        "completion_fraction_mean": _round(completion_mean),
        "completion_fraction_status": completion_status,
        "work_backlog_max": _round(backlog_max),
        "work_backlog_status": backlog_status,
        "prediction_spend_fraction_max": _round(spend_fraction_max),
        "prediction_spend_fraction_status": spend_status,
        "status": status,
        "interpretation": (
            "boundedness/productivity guardrails pass preflight"
            if status == "pass"
            else "boundedness/productivity guardrails failed; no A7.3 promotion analysis is allowed"
        ),
    }


def missing_fields(observed: frozenset[str], required: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(field for field in required if field not in observed)


def _csv_header_and_row_count(path: Path) -> tuple[frozenset[str], int]:
    if not path.exists():
        return frozenset(), 0
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return frozenset(reader.fieldnames or ()), sum(1 for _ in reader)


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _delay_integrity_status(
    condition: str,
    source_rows: list[dict[str, str]],
    events: list[dict[str, str]],
) -> str:
    if not source_rows or not events:
        return "missing_rows"
    expected = "control_no_delay" if condition == "no_delay_same_tick_blocked" else "pass"
    if any(row.get("source_ledger_delay_integrity") != expected for row in source_rows):
        return "fail_delay_ledger"
    for row in events:
        created = int(_float_cell(row.get("feedback_created_tick")))
        visible = int(_float_cell(row.get("feedback_visible_tick")))
        if condition == "no_delay_same_tick_blocked":
            if visible != created:
                return "fail_no_delay_control"
        elif visible <= created:
            return "fail_same_tick_leakage"
    return "pass"


def _same_tick_block_status(condition: str, events: list[dict[str, str]]) -> str:
    if not events:
        return "missing_events"
    if condition != "no_delay_same_tick_blocked":
        blocked_values = {row.get("same_tick_influence_blocked") for row in events}
        return "pass" if blocked_values == {"True"} else "fail"
    return "pass"


def _shuffle_status(condition: str, source_rows: list[dict[str, str]]) -> str:
    if not source_rows:
        return "missing_source_ledger"
    phase_expected = "applied" if condition == "phase_shuffled_lag" else "not_applicable"
    threshold_expected = "applied" if condition == "threshold_shuffled" else "not_applicable"
    for row in source_rows:
        if row.get("source_ledger_phase_shuffle") != phase_expected:
            return "fail_phase_shuffle"
        if row.get("source_ledger_threshold_shuffle") != threshold_expected:
            return "fail_threshold_shuffle"
    return "pass"


def _clip_residual_status(
    metrics: list[dict[str, str]],
    source_rows: list[dict[str, str]],
) -> str:
    rows = metrics if metrics else source_rows
    if not rows:
        return "missing_rows"
    for row in rows:
        if abs(_float_cell(row.get("source_ledger_clip_residual"))) > 1e-9:
            return "fail"
    return "pass"


def _range_status(rows: list[dict[str, str]], fields: tuple[str, ...]) -> str:
    if not rows:
        return "missing_rows"
    for row in rows:
        for field in fields:
            value = _float_cell(row.get(field))
            if value < 0.0 or value > 1.0:
                return "fail"
    return "pass"


def _peer_lag_status(
    condition: str,
    metrics: list[dict[str, str]],
    source_rows: list[dict[str, str]],
) -> str:
    if not metrics or not source_rows:
        return "missing_rows"
    if any(row.get("source_ledger_peer_activity_lag") != "pass" for row in source_rows):
        return "fail_peer_lag_ledger"
    fields = tuple(
        field
        for action in A7_3_ACTIONS
        for field in (
            f"delayed_agent_role_activity_{action}",
            f"peer_activity_lag_{action}",
        )
    )
    range_status = _range_status(metrics, fields)
    if range_status != "pass":
        return range_status
    if condition == "no_delay_same_tick_blocked":
        return _no_delay_lag_status(metrics)
    return _delayed_lag_reconstruction_status(condition, metrics)


def _no_delay_lag_status(metrics: list[dict[str, str]]) -> str:
    for row in metrics:
        for action in A7_3_ACTIONS:
            delayed = _float_cell(row.get(f"delayed_agent_role_activity_{action}"))
            peer = _float_cell(row.get(f"peer_activity_lag_{action}"))
            if abs(delayed) > 1e-9 or abs(peer) > 1e-9:
                return "fail_no_delay_lag"
    return "pass"


def _delayed_lag_reconstruction_status(
    condition: str,
    metrics: list[dict[str, str]],
) -> str:
    delay = int(A7_3_SMOKE_PARAMETERS["feedback_delay_ticks"])
    peer_differs_from_delayed = False
    for index, row in enumerate(metrics):
        for action in A7_3_ACTIONS:
            delayed = _float_cell(row.get(f"delayed_agent_role_activity_{action}"))
            peer = _float_cell(row.get(f"peer_activity_lag_{action}"))
            expected = (
                0.0
                if index < delay
                else _float_cell(metrics[index - delay].get(f"agent_role_activity_{action}"))
            )
            if abs(delayed - expected) > 1e-6:
                return "fail_delayed_role_reconstruction"
            if condition == "phase_shuffled_lag":
                if action != "rest" and abs(peer - delayed) > 1e-6:
                    peer_differs_from_delayed = True
            elif abs(peer - delayed) > 1e-6:
                return "fail_peer_lag_reconstruction"
    if condition == "phase_shuffled_lag" and not peer_differs_from_delayed:
        return "fail_phase_shuffle_not_reflected"
    return "pass"


def _boundedness_status(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "missing_metrics"
    for row in rows:
        for field in _BOUNDED_0_1_FIELDS:
            value = _float_cell(row.get(field))
            if value < 0.0 or value > 1.0:
                return f"fail:{field}"
        for field in _THRESHOLD_FIELDS:
            value = _float_cell(row.get(field))
            if value < -2.0 or value > 2.0:
                return f"fail:{field}"
        if _float_cell(row.get("work_backlog")) < 0.0:
            return "fail:work_backlog"
    return "pass"


def _overall_status(
    completeness_rows: list[dict[str, str | int]],
    source_ledger_rows: list[dict[str, str | int]],
    guardrail_rows: list[dict[str, str | int | float]],
) -> str:
    if _missing_condition_seed_pairs(completeness_rows):
        return A7_3_PREFLIGHT_STATUS_MISSING_COVERAGE
    if any(row["status"] != "pass" for row in completeness_rows):
        return A7_3_PREFLIGHT_STATUS_MISSING_SCHEMA
    if any(row["status"] != "pass" for row in source_ledger_rows):
        return A7_3_PREFLIGHT_STATUS_SOURCE_LEDGER
    if any(row["status"] != "pass" for row in guardrail_rows):
        return A7_3_PREFLIGHT_STATUS_GUARDRAILS
    return A7_3_PREFLIGHT_STATUS_ELIGIBLE


def _manifest_row(
    compare_path: Path,
    output_path: Path,
    completeness_rows: list[dict[str, str | int]],
    source_ledger_rows: list[dict[str, str | int]],
    guardrail_rows: list[dict[str, str | int | float]],
    status: str,
) -> dict[str, str | int]:
    expected_seeds = tuple(A7_3_SMOKE_PARAMETERS["seeds"])
    observed_conditions = sorted({str(row["condition"]) for row in completeness_rows})
    observed_seeds = sorted({int(row["seed"]) for row in completeness_rows})
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "expected_condition_count": len(A7_3_CONDITIONS),
        "observed_condition_count": len(observed_conditions),
        "expected_seed_count": len(expected_seeds),
        "observed_seed_count": len(observed_seeds),
        "expected_run_count": len(A7_3_CONDITIONS) * len(expected_seeds),
        "observed_run_count": len(completeness_rows),
        "missing_condition_seed_pairs": "|".join(_missing_condition_seed_pairs(completeness_rows)),
        "completeness_pass_count": sum(1 for row in completeness_rows if row["status"] == "pass"),
        "source_ledger_pass_count": sum(1 for row in source_ledger_rows if row["status"] == "pass"),
        "guardrail_pass_count": sum(1 for row in guardrail_rows if row["status"] == "pass"),
        "status": status,
    }


def _missing_condition_seed_pairs(rows: list[dict[str, str | int]]) -> tuple[str, ...]:
    observed = {(str(row["condition"]), int(row["seed"])) for row in rows}
    expected = {
        (condition, int(seed))
        for condition in A7_3_CONDITIONS
        for seed in A7_3_SMOKE_PARAMETERS["seeds"]
    }
    return tuple(
        f"{condition}:seed{seed}" for condition, seed in sorted(expected - observed)
    )


def _summary(
    compare_path: Path,
    completeness_rows: list[dict[str, str | int]],
    source_ledger_rows: list[dict[str, str | int]],
    guardrail_rows: list[dict[str, str | int | float]],
    manifest_row: dict[str, str | int],
) -> str:
    return "\n".join(
        [
            "# A7.3 Preflight",
            "",
            f"- Compare dir: `{compare_path}`",
            f"- Runs inspected: {len(completeness_rows)}",
            f"- Completeness-pass rows: {manifest_row['completeness_pass_count']}",
            f"- Source-ledger-pass rows: {manifest_row['source_ledger_pass_count']}",
            f"- Guardrail-pass rows: {manifest_row['guardrail_pass_count']}",
            f"- Status: `{manifest_row['status']}`",
            "",
            "This analyzer is read-only. It checks condition/seed coverage,",
            "schema completeness, lifted-state availability, source-ledger delay integrity,",
            "boundedness, and productivity guardrails. It does not rerun simulations,",
            "compute promotion endpoints, run sweeps, or create A7.3 scientific evidence.",
            "",
        ]
    )


def _float_cell(value: str | None) -> float:
    if value in {None, ""}:
        return 0.0
    return float(value)


def _round(value: float) -> float:
    return round(value, 6)


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
    for name in _OUTPUT_NAMES:
        if (output_path / name).exists():
            raise FileExistsError(
                f"Output path {output_path} already contains A7.3 preflight artifacts."
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only preflight analyzer for A7.3 smoke artifacts."
    )
    parser.add_argument(
        "--compare-dir",
        default=str(DEFAULT_A7_3_SMOKE_DIR),
        help="Existing A7.3 smoke artifact directory.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A7_3_PREFLIGHT_DIR),
        help="Output directory for read-only A7.3 preflight artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_a7_3_preflight_analysis(
            compare_dir=args.compare_dir,
            out_dir=args.out,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    print(yaml.safe_dump(result, sort_keys=True), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
