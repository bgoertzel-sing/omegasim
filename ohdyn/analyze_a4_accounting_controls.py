"""Read existing A4 holdout artifacts and residualize completion synchrony."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ohdyn.analyze_a4_delayed_null import (
    DEFAULT_A4_DELAYED_NULL_BLOCK_SIZES,
    _circular_shift,
    _completion_fraction_at_tick,
    _coupling_manifest_fields,
    _offsets_for,
)
from ohdyn.analyze_a4_holdout import (
    A4_HOLDOUT_COMPARISONS,
    A4_HOLDOUT_MODES,
    DEFAULT_A4_HOLDOUT_DIR,
    DEFAULT_A4_SEEDS,
    _effect_value,
    _float,
    _format_number,
    _int,
    _lagged_correlation,
    _mean,
    _median,
    _parse_seed_args,
    _quantile,
    _read_csv,
    _validate_source,
    _write_csv,
)


DEFAULT_A4_ACCOUNTING_CONTROL_OUT_DIR = Path("runs/a4_accounting_control_seed100_129")
DEFAULT_A4_ACCOUNTING_CONTROL_DOC = Path(
    "docs/results/a4_accounting_control_seed100_129.md"
)
A4_ACCOUNTING_CONTROL_GROUPS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("raw", (), "unresidualized completion-fraction trajectory"),
    ("clock_trend", ("tick", "tick_squared"), "tick and tick squared"),
    (
        "opportunity_load",
        (
            "queue_depth",
            "load_normalized_backlog",
            "queued_task_age_mean_tick",
            "queued_task_age_max_tick",
            "tasks_worked_tick",
            "tasks_created_tick",
            "messages_sent_tick",
            "idle_tick",
        ),
        "non-tautological queue, work-opportunity, age, and action-mix fields",
    ),
    (
        "transfer_timing",
        (
            "inbound_transfers_tick",
            "outbound_transfers_tick",
            "transfer_attempts_tick",
            "transfers_completed_tick",
            "delivered_inbound_transfers_tick",
            "pending_inbound_transfers_tick",
        ),
        "transfer counts, delivered arrivals, and pending delayed deliveries",
    ),
    (
        "combined_non_tautological",
        (
            "tick",
            "tick_squared",
            "queue_depth",
            "load_normalized_backlog",
            "queued_task_age_mean_tick",
            "queued_task_age_max_tick",
            "tasks_worked_tick",
            "tasks_created_tick",
            "messages_sent_tick",
            "idle_tick",
            "inbound_transfers_tick",
            "outbound_transfers_tick",
            "transfer_attempts_tick",
            "transfers_completed_tick",
            "delivered_inbound_transfers_tick",
            "pending_inbound_transfers_tick",
        ),
        "clock, load/opportunity, action-mix, and transfer-timing fields",
    ),
    (
        "identity_inclusive",
        (
            "tasks_created_total",
            "tasks_completed_total",
            "tasks_created_tick",
            "tasks_completed_tick",
        ),
        "completion numerator/denominator accounting sensitivity fields",
    ),
)
A4_ACCOUNTING_CONTROL_ENDPOINTS = (
    "completion_fraction_corr_lag0",
    "completion_fraction_corr_lag2",
)
A4_ACCOUNTING_CONTROL_ENDPOINT_FIELDS = (
    "mode",
    "seed",
    "control_group",
    "coupling_mode",
    "delay_ticks",
    "block_size",
    "offset",
    "tick_count",
    "completion_fraction_corr_lag0",
    "completion_fraction_corr_lag2",
)
A4_ACCOUNTING_CONTROL_EFFECT_FIELDS = (
    "comparison",
    "control_group",
    "endpoint",
    "paired_seed_count",
    "observed_mean_delta",
    "observed_median_delta",
    "observed_positive_delta_rate",
    "null_replicate_count",
    "null_mean_delta",
    "null_median_delta",
    "null_delta_ci_low",
    "null_delta_ci_high",
    "observed_minus_null_mean",
    "observed_outside_null_ci",
    "seed_observed_minus_seed_null_positive_rate",
)
A4_ACCOUNTING_CONTROL_MANIFEST_FIELDS = (
    "control_group",
    "covariates",
    "description",
    "mode",
    "seed",
    "delay_ticks",
    "block_size",
    "offsets",
    "transfer_decision_count",
    "arrival_delay_counts",
)
_OUTPUT_NAMES = (
    "a4_accounting_control_endpoints.csv",
    "a4_accounting_control_effects.csv",
    "a4_accounting_control_manifest.csv",
    "summary.md",
)


def run_a4_accounting_control_analysis(
    *,
    holdout_dir: str | Path = DEFAULT_A4_HOLDOUT_DIR,
    out_dir: str | Path = DEFAULT_A4_ACCOUNTING_CONTROL_OUT_DIR,
    doc_out: str | Path | None = DEFAULT_A4_ACCOUNTING_CONTROL_DOC,
    seeds: tuple[int, ...] = DEFAULT_A4_SEEDS,
    block_sizes: tuple[int, ...] = DEFAULT_A4_DELAYED_NULL_BLOCK_SIZES,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Residualize completion trajectories and rebuild temporal-shift nulls."""

    if not seeds:
        raise ValueError("At least one seed is required.")
    _validate_block_sizes(block_sizes)
    source_path = Path(holdout_dir)
    output_path = Path(out_dir)
    doc_path = Path(doc_out) if doc_out is not None else None
    _validate_source(source_path, seeds)
    _ensure_outputs_available(output_path, doc_path=doc_path, overwrite=overwrite)
    output_path.mkdir(parents=True, exist_ok=True)
    if doc_path is not None:
        doc_path.parent.mkdir(parents=True, exist_ok=True)

    observed_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    for mode in A4_HOLDOUT_MODES:
        for seed in seeds:
            run_path = source_path / f"{mode}_seed{seed}"
            observed_rows.extend(_observed_endpoint_rows(run_path, mode, seed))
            for block_size in block_sizes:
                rows, offsets, coupling_manifest = _null_endpoint_rows(
                    run_path, mode, seed, block_size
                )
                null_rows.extend(rows)
                for group_name, covariates, description in A4_ACCOUNTING_CONTROL_GROUPS:
                    manifest_rows.append(
                        {
                            "control_group": group_name,
                            "covariates": "|".join(covariates) if covariates else "none",
                            "description": description,
                            "mode": mode,
                            "seed": seed,
                            "delay_ticks": rows[0]["delay_ticks"] if rows else 0,
                            "block_size": block_size,
                            "offsets": "|".join(str(offset) for offset in offsets),
                            **coupling_manifest,
                        }
                    )

    effect_rows = _effect_rows(observed_rows, null_rows, seeds)
    _write_csv(
        output_path / "a4_accounting_control_endpoints.csv",
        A4_ACCOUNTING_CONTROL_ENDPOINT_FIELDS,
        [*observed_rows, *null_rows],
    )
    _write_csv(
        output_path / "a4_accounting_control_effects.csv",
        A4_ACCOUNTING_CONTROL_EFFECT_FIELDS,
        effect_rows,
    )
    _write_csv(
        output_path / "a4_accounting_control_manifest.csv",
        A4_ACCOUNTING_CONTROL_MANIFEST_FIELDS,
        manifest_rows,
    )
    summary = _summary(source_path, seeds, block_sizes, null_rows, effect_rows)
    (output_path / "summary.md").write_text(summary)
    if doc_path is not None:
        doc_path.write_text(summary)
    return {
        "out_dir": str(output_path),
        "doc_out": str(doc_path) if doc_path is not None else None,
        "seed_count": len(seeds),
        "observed_endpoint_rows": len(observed_rows),
        "null_endpoint_rows": len(null_rows),
        "effect_rows": len(effect_rows),
        "control_groups": tuple(group[0] for group in A4_ACCOUNTING_CONTROL_GROUPS),
        "block_sizes": block_sizes,
    }


def _validate_block_sizes(block_sizes: tuple[int, ...]) -> None:
    if not block_sizes:
        raise ValueError("At least one block size is required.")
    for block_size in block_sizes:
        if isinstance(block_size, bool) or not isinstance(block_size, int):
            raise ValueError("Block sizes must be integers.")
        if block_size <= 0:
            raise ValueError("Block sizes must be positive.")


def _ensure_outputs_available(
    output_path: Path,
    *,
    doc_path: Path | None,
    overwrite: bool,
) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [name for name in _OUTPUT_NAMES if (output_path / name).exists()]
    if doc_path is not None and doc_path.exists():
        collisions.append(str(doc_path))
    if collisions and not overwrite:
        raise FileExistsError(
            "Output path already contains A4 accounting-control artifacts: "
            f"{', '.join(collisions)}"
        )


def _observed_endpoint_rows(run_path: Path, mode: str, seed: int) -> list[dict[str, Any]]:
    config = yaml.safe_load((run_path / "config.yaml").read_text())
    delay_ticks = int(config.get("coupling", {}).get("delay_ticks", 0))
    trajectories = _residual_trajectories(run_path)
    rows = []
    for group_name, _covariates, _description in A4_ACCOUNTING_CONTROL_GROUPS:
        hive_a = trajectories[group_name]["hive_a"]
        hive_b = trajectories[group_name]["hive_b"]
        rows.append(
            _endpoint_row(
                mode=mode,
                seed=seed,
                control_group=group_name,
                coupling_mode=trajectories["coupling_mode"],
                delay_ticks=delay_ticks,
                block_size=0,
                offset=0,
                hive_a=hive_a,
                hive_b=hive_b,
            )
        )
    return rows


def _null_endpoint_rows(
    run_path: Path,
    mode: str,
    seed: int,
    block_size: int,
) -> tuple[list[dict[str, Any]], tuple[int, ...], dict[str, Any]]:
    config = yaml.safe_load((run_path / "config.yaml").read_text())
    delay_ticks = int(config.get("coupling", {}).get("delay_ticks", 0))
    trajectories = _residual_trajectories(run_path)
    coupling_rows = _read_csv(run_path / "coupling_events.csv")
    tick_count = len(trajectories["raw"]["hive_a"])
    offsets = _offsets_for(tick_count, block_size, delay_ticks)
    rows = []
    for group_name, _covariates, _description in A4_ACCOUNTING_CONTROL_GROUPS:
        hive_a = trajectories[group_name]["hive_a"]
        hive_b = trajectories[group_name]["hive_b"]
        for offset in offsets:
            rows.append(
                _endpoint_row(
                    mode=mode,
                    seed=seed,
                    control_group=group_name,
                    coupling_mode=trajectories["coupling_mode"],
                    delay_ticks=delay_ticks,
                    block_size=block_size,
                    offset=offset,
                    hive_a=hive_a,
                    hive_b=_circular_shift(hive_b, offset),
                )
            )
    return rows, offsets, _coupling_manifest_fields(coupling_rows)


def _endpoint_row(
    *,
    mode: str,
    seed: int,
    control_group: str,
    coupling_mode: str,
    delay_ticks: int,
    block_size: int,
    offset: int,
    hive_a: list[float],
    hive_b: list[float],
) -> dict[str, Any]:
    return {
        "mode": mode,
        "seed": seed,
        "control_group": control_group,
        "coupling_mode": coupling_mode,
        "delay_ticks": delay_ticks,
        "block_size": block_size,
        "offset": offset,
        "tick_count": len(hive_a),
        "completion_fraction_corr_lag0": _lagged_correlation(hive_a, hive_b, 0),
        "completion_fraction_corr_lag2": _lagged_correlation(hive_a, hive_b, 2),
    }


def _residual_trajectories(run_path: Path) -> dict[str, Any]:
    hive_rows = _read_csv(run_path / "hive_metrics.csv")
    cross_rows = _read_csv(run_path / "cross_hive_metrics.csv")
    coupling_rows = _read_csv(run_path / "coupling_events.csv")
    by_hive: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in hive_rows:
        by_hive[row["hive_id"]].append(row)
    transfer_features = _transfer_features(coupling_rows, len(cross_rows))
    result: dict[str, Any] = {"coupling_mode": cross_rows[0]["coupling_mode"]}
    for group_name, covariates, _description in A4_ACCOUNTING_CONTROL_GROUPS:
        result[group_name] = {}
        for hive_id in ("hive_a", "hive_b"):
            y = [_completion_fraction_at_tick(row) for row in by_hive[hive_id]]
            if not covariates:
                result[group_name][hive_id] = y
            else:
                x = [
                    [
                        _covariate_value(
                            covariate,
                            row=row,
                            cross_row=cross_rows[index],
                            transfer_features=transfer_features[hive_id][index],
                            tick=index,
                        )
                        for covariate in covariates
                    ]
                    for index, row in enumerate(by_hive[hive_id])
                ]
                result[group_name][hive_id] = _residualize(y, x)
    return result


def _transfer_features(
    coupling_rows: list[dict[str, str]],
    tick_count: int,
) -> dict[str, list[dict[str, int]]]:
    by_hive = {
        "hive_a": [
            {"delivered_inbound_transfers_tick": 0, "pending_inbound_transfers_tick": 0}
            for _tick in range(tick_count)
        ],
        "hive_b": [
            {"delivered_inbound_transfers_tick": 0, "pending_inbound_transfers_tick": 0}
            for _tick in range(tick_count)
        ],
    }
    accepted = [row for row in coupling_rows if row.get("transfer_decision") == "True"]
    for row in accepted:
        target = row["target_hive_id"]
        tick = _int(row["tick"])
        arrival_tick = _int(row["arrival_tick"])
        if target in by_hive and 0 <= arrival_tick < tick_count:
            by_hive[target][arrival_tick]["delivered_inbound_transfers_tick"] += 1
        if target in by_hive:
            for pending_tick in range(max(0, tick), min(arrival_tick, tick_count)):
                by_hive[target][pending_tick]["pending_inbound_transfers_tick"] += 1
    return by_hive


def _covariate_value(
    covariate: str,
    *,
    row: dict[str, str],
    cross_row: dict[str, str],
    transfer_features: dict[str, int],
    tick: int,
) -> float:
    if covariate == "tick":
        return float(tick)
    if covariate == "tick_squared":
        return float(tick * tick)
    if covariate == "load_normalized_backlog":
        created = _int(row["tasks_created_total"])
        return 0.0 if created == 0 else _int(row["queue_depth"]) / created
    if covariate in transfer_features:
        return float(transfer_features[covariate])
    if covariate in cross_row:
        return _float(cross_row[covariate])
    return _float(row[covariate])


def _residualize(y_values: list[float], x_values: list[list[float]]) -> list[float]:
    y = np.asarray(y_values, dtype=float)
    x = np.asarray(x_values, dtype=float)
    if x.ndim != 2 or x.shape[0] != y.shape[0]:
        raise ValueError("Covariate matrix must align with completion trajectory.")
    design = np.column_stack([np.ones(len(y)), x])
    fitted, *_unused = np.linalg.lstsq(design, y, rcond=None)
    residuals = y - design @ fitted
    return [round(float(value), 12) for value in residuals]


def _effect_rows(
    observed_rows: list[dict[str, Any]],
    null_rows: list[dict[str, Any]],
    seeds: tuple[int, ...],
) -> list[dict[str, Any]]:
    observed_index = {
        (row["mode"], int(row["seed"]), row["control_group"]): row
        for row in observed_rows
    }
    null_index = {
        (
            row["mode"],
            int(row["seed"]),
            row["control_group"],
            int(row["block_size"]),
            int(row["offset"]),
        ): row
        for row in null_rows
    }
    replicate_keys = sorted(
        {
            (int(row["seed"]), int(row["block_size"]), int(row["offset"]))
            for row in null_rows
        }
    )
    rows = []
    for comparison, high_mode, low_mode in A4_HOLDOUT_COMPARISONS:
        for group_name, _covariates, _description in A4_ACCOUNTING_CONTROL_GROUPS:
            for endpoint in A4_ACCOUNTING_CONTROL_ENDPOINTS:
                observed_seed_deltas = {}
                seed_null_deltas: dict[int, list[float]] = defaultdict(list)
                null_deltas = []
                for seed in seeds:
                    high = _effect_value(observed_index[(high_mode, seed, group_name)][endpoint])
                    low = _effect_value(observed_index[(low_mode, seed, group_name)][endpoint])
                    if high is not None and low is not None:
                        observed_seed_deltas[seed] = high - low
                for seed, block_size, offset in replicate_keys:
                    high_row = null_index.get(
                        (high_mode, seed, group_name, block_size, offset)
                    )
                    low_row = null_index.get(
                        (low_mode, seed, group_name, block_size, offset)
                    )
                    if high_row is None or low_row is None:
                        continue
                    high = _effect_value(high_row[endpoint])
                    low = _effect_value(low_row[endpoint])
                    if high is None or low is None:
                        continue
                    delta = high - low
                    null_deltas.append(delta)
                    seed_null_deltas[seed].append(delta)
                rows.append(
                    _summarize_effect(
                        comparison=comparison,
                        control_group=group_name,
                        endpoint=endpoint,
                        observed_seed_deltas=observed_seed_deltas,
                        null_deltas=null_deltas,
                        seed_null_deltas=seed_null_deltas,
                    )
                )
    return rows


def _summarize_effect(
    *,
    comparison: str,
    control_group: str,
    endpoint: str,
    observed_seed_deltas: dict[int, float],
    null_deltas: list[float],
    seed_null_deltas: dict[int, list[float]],
) -> dict[str, Any]:
    observed_deltas = [observed_seed_deltas[seed] for seed in sorted(observed_seed_deltas)]
    observed_mean = _mean(observed_deltas)
    null_mean = _mean(null_deltas)
    null_ci_low = _quantile(null_deltas, 0.025) if null_deltas else 0.0
    null_ci_high = _quantile(null_deltas, 0.975) if null_deltas else 0.0
    seed_centered = []
    for seed, observed_delta in sorted(observed_seed_deltas.items()):
        if seed_null_deltas[seed]:
            seed_centered.append(observed_delta - _mean(seed_null_deltas[seed]))
    return {
        "comparison": comparison,
        "control_group": control_group,
        "endpoint": endpoint,
        "paired_seed_count": len(observed_deltas),
        "observed_mean_delta": _format_number(observed_mean),
        "observed_median_delta": _format_number(_median(observed_deltas))
        if observed_deltas
        else "NA",
        "observed_positive_delta_rate": _format_number(
            sum(1 for delta in observed_deltas if delta > 0.0) / len(observed_deltas)
        )
        if observed_deltas
        else "NA",
        "null_replicate_count": len(null_deltas),
        "null_mean_delta": _format_number(null_mean),
        "null_median_delta": _format_number(_median(null_deltas)) if null_deltas else "NA",
        "null_delta_ci_low": _format_number(null_ci_low),
        "null_delta_ci_high": _format_number(null_ci_high),
        "observed_minus_null_mean": _format_number(observed_mean - null_mean),
        "observed_outside_null_ci": str(
            bool(null_deltas and (observed_mean < null_ci_low or observed_mean > null_ci_high))
        ),
        "seed_observed_minus_seed_null_positive_rate": _format_number(
            sum(1 for delta in seed_centered if delta > 0.0) / len(seed_centered)
        )
        if seed_centered
        else "NA",
    }


def _summary(
    source_path: Path,
    seeds: tuple[int, ...],
    block_sizes: tuple[int, ...],
    null_rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
) -> str:
    delayed_rows = [
        row for row in effect_rows if row["comparison"] == "delayed_minus_none"
    ]
    lines = [
        "# A4 Accounting-Control Completion Synchrony Analysis",
        "",
        f"- source: `{source_path}`",
        f"- seeds: {seeds[0]}..{seeds[-1]}",
        f"- block sizes: {', '.join(str(size) for size in block_sizes)}",
        f"- null endpoint rows: {len(null_rows)}",
        "- method: per-hive completion-fraction residualization followed by deterministic circular block shifts of hive_b relative to hive_a.",
        "- excluded offsets: 0 and each run's configured causal delay.",
        "- This analyzer is read-only and does not run or rewrite A4 holdout seeds.",
        "",
        "## Delayed Minus None Completion-Fraction Endpoints",
        "",
        "| control_group | endpoint | observed_mean_delta | null_mean_delta | null_ci | observed_minus_null_mean | outside_null_ci | seed_centered_positive_rate |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in delayed_rows:
        lines.append(
            "| {control_group} | {endpoint} | {observed_mean_delta} | {null_mean_delta} | [{null_delta_ci_low}, {null_delta_ci_high}] | {observed_minus_null_mean} | {observed_outside_null_ci} | {seed_observed_minus_seed_null_positive_rate} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Result Interpretation",
            "",
            _interpretation(delayed_rows),
        ]
    )
    lines.extend(
        [
            "",
            "## Control Groups",
            "",
        ]
    )
    for group_name, covariates, description in A4_ACCOUNTING_CONTROL_GROUPS:
        covariate_text = ", ".join(covariates) if covariates else "none"
        lines.append(f"- `{group_name}`: {description}. Covariates: {covariate_text}.")
    lines.extend(
        [
            "",
            "## Output Tables",
            "",
            "- `a4_accounting_control_endpoints.csv`: observed and circular-shift completion-correlation endpoint rows by control group.",
            "- `a4_accounting_control_effects.csv`: observed mode contrasts compared with residualized circular-shift null deltas.",
            "- `a4_accounting_control_manifest.csv`: covariate groups, block sizes, offsets, and transfer-delay summaries.",
            "",
            "## Interpretation Boundary",
            "",
            "- `identity_inclusive` is an accounting-decomposition sensitivity, not the primary causal control.",
            "- The two-hive shuffled condition remains a schema/source-opportunity control, not a phase-randomization null.",
            "- No simulator mechanics, configs, lobe labels, dashboards, real LLM calls, or external integrations are added by this analysis.",
            "",
        ]
    )
    return "\n".join(lines)


def _interpretation(delayed_rows: list[dict[str, Any]]) -> str:
    combined_rows = [
        row for row in delayed_rows if row["control_group"] == "combined_non_tautological"
    ]
    if combined_rows and all(row["observed_outside_null_ci"] == "False" for row in combined_rows):
        return (
            "The delayed-minus-none completion-fraction synchrony residual is no longer "
            "outside the residualized circular-shift null after the combined "
            "non-tautological accounting controls. Treat A4 as queue-flow/service "
            "and action-opportunity accounting plus a documented delayed "
            "synchronization diagnostic; do not implement three-hive mechanics from "
            "this result."
        )
    if combined_rows and any(row["observed_outside_null_ci"] == "True" for row in combined_rows):
        return (
            "At least one delayed-minus-none completion-fraction endpoint remains "
            "outside the residualized circular-shift null after the combined "
            "non-tautological accounting controls. The next step should be a "
            "preregistered three-hive target-null design document, not simulator "
            "mechanics."
        )
    return (
        "The combined non-tautological control rows are unavailable, so this analysis "
        "does not close the A4 accounting-control question."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run read-only A4 accounting controls on existing holdout artifacts."
    )
    parser.add_argument("--holdout-dir", default=str(DEFAULT_A4_HOLDOUT_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_A4_ACCOUNTING_CONTROL_OUT_DIR))
    parser.add_argument(
        "--doc-out",
        default=str(DEFAULT_A4_ACCOUNTING_CONTROL_DOC),
        help="Optional committed Markdown summary path. Use an empty value to skip.",
    )
    parser.add_argument(
        "--seeds",
        nargs="*",
        help="Seed list or inclusive ranges like 100..129. Defaults to 100..129.",
    )
    parser.add_argument(
        "--block-sizes",
        nargs="*",
        type=int,
        default=list(DEFAULT_A4_DELAYED_NULL_BLOCK_SIZES),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing accounting-control outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a4_accounting_control_analysis(
            holdout_dir=args.holdout_dir,
            out_dir=args.out_dir,
            doc_out=args.doc_out or None,
            seeds=_parse_seed_args(args.seeds),
            block_sizes=tuple(args.block_sizes),
            overwrite=args.overwrite,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
