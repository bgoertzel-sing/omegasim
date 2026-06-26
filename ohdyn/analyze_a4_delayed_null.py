"""Read existing A4 holdout artifacts and build temporal-shift null controls."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from ohdyn.analyze_a4_holdout import (
    A4_HOLDOUT_COMPARISONS,
    A4_HOLDOUT_MODES,
    DEFAULT_A4_HOLDOUT_DIR,
    DEFAULT_A4_SEEDS,
    _cross_endpoints,
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


DEFAULT_A4_DELAYED_NULL_OUT_DIR = Path("runs/a4_delayed_coupling_null_seed100_129")
DEFAULT_A4_DELAYED_NULL_DOC = Path("docs/results/a4_delayed_coupling_null_seed100_129.md")
DEFAULT_A4_DELAYED_NULL_BLOCK_SIZES = (5, 10, 20)
A4_DELAYED_NULL_ENDPOINTS = (
    "load_backlog_corr_lag0",
    "load_backlog_corr_lag2",
    "completion_fraction_corr_lag0",
    "completion_fraction_corr_lag2",
    "queued_age_divergence_final",
    "completion_fraction_divergence_final",
)
A4_DELAYED_NULL_ENDPOINT_FIELDS = (
    "mode",
    "seed",
    "coupling_mode",
    "delay_ticks",
    "block_size",
    "offset",
    "tick_count",
    "transfer_attempts_total",
    "transfers_completed_total",
    "load_backlog_corr_lag0",
    "load_backlog_corr_lag2",
    "completion_fraction_corr_lag0",
    "completion_fraction_corr_lag2",
    "queued_age_divergence_final",
    "completion_fraction_divergence_final",
)
A4_DELAYED_NULL_EFFECT_FIELDS = (
    "comparison",
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
A4_DELAYED_NULL_MANIFEST_FIELDS = (
    "mode",
    "seed",
    "delay_ticks",
    "block_size",
    "offsets",
    "transfer_decision_count",
    "arrival_delay_counts",
)
_OUTPUT_NAMES = (
    "a4_delayed_null_endpoints.csv",
    "a4_delayed_null_effects.csv",
    "a4_delayed_null_manifest.csv",
    "summary.md",
)


def run_a4_delayed_null_analysis(
    *,
    holdout_dir: str | Path = DEFAULT_A4_HOLDOUT_DIR,
    out_dir: str | Path = DEFAULT_A4_DELAYED_NULL_OUT_DIR,
    doc_out: str | Path | None = DEFAULT_A4_DELAYED_NULL_DOC,
    seeds: tuple[int, ...] = DEFAULT_A4_SEEDS,
    block_sizes: tuple[int, ...] = DEFAULT_A4_DELAYED_NULL_BLOCK_SIZES,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Construct deterministic circular-shift nulls from existing A4 artifacts."""

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

    observed_rows = _observed_cross_rows(source_path, seeds)
    null_rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    for mode in A4_HOLDOUT_MODES:
        for seed in seeds:
            run_path = source_path / f"{mode}_seed{seed}"
            for block_size in block_sizes:
                rows, offsets, coupling_manifest = _null_endpoint_rows(
                    run_path, mode, seed, block_size
                )
                null_rows.extend(rows)
                manifest_rows.append(
                    {
                        "mode": mode,
                        "seed": seed,
                        "delay_ticks": rows[0]["delay_ticks"] if rows else 0,
                        "block_size": block_size,
                        "offsets": "|".join(str(offset) for offset in offsets),
                        **coupling_manifest,
                    }
                )

    effect_rows = _null_effect_rows(observed_rows, null_rows, seeds)
    _write_csv(
        output_path / "a4_delayed_null_endpoints.csv",
        A4_DELAYED_NULL_ENDPOINT_FIELDS,
        null_rows,
    )
    _write_csv(
        output_path / "a4_delayed_null_effects.csv",
        A4_DELAYED_NULL_EFFECT_FIELDS,
        effect_rows,
    )
    _write_csv(
        output_path / "a4_delayed_null_manifest.csv",
        A4_DELAYED_NULL_MANIFEST_FIELDS,
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
        "null_endpoint_rows": len(null_rows),
        "null_effect_rows": len(effect_rows),
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
            f"Output path already contains A4 delayed-null artifacts: {', '.join(collisions)}"
        )


def _observed_cross_rows(source_path: Path, seeds: tuple[int, ...]) -> list[dict[str, Any]]:
    rows = []
    for mode in A4_HOLDOUT_MODES:
        for seed in seeds:
            rows.append(_cross_endpoints(source_path / f"{mode}_seed{seed}", mode, seed))
    return rows


def _null_endpoint_rows(
    run_path: Path,
    mode: str,
    seed: int,
    block_size: int,
) -> tuple[list[dict[str, Any]], tuple[int, ...], dict[str, Any]]:
    config = yaml.safe_load((run_path / "config.yaml").read_text())
    delay_ticks = int(config.get("coupling", {}).get("delay_ticks", 0))
    cross_rows = _read_csv(run_path / "cross_hive_metrics.csv")
    coupling_rows = _read_csv(run_path / "coupling_events.csv")
    hive_rows = _read_csv(run_path / "hive_metrics.csv")
    by_hive: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in hive_rows:
        by_hive[row["hive_id"]].append(row)
    hive_a_rows = by_hive["hive_a"]
    hive_b_rows = by_hive["hive_b"]
    tick_count = len(cross_rows)
    offsets = _offsets_for(tick_count, block_size, delay_ticks)
    rows = []
    for offset in offsets:
        shifted_hive_b_rows = _circular_shift(hive_b_rows, offset)
        shifted_hive_b_backlog = _circular_shift(
            [_float(row["hive_b_load_normalized_backlog_tick"]) for row in cross_rows],
            offset,
        )
        hive_a_backlog = [
            _float(row["hive_a_load_normalized_backlog_tick"]) for row in cross_rows
        ]
        hive_a_completion = [_completion_fraction_at_tick(row) for row in hive_a_rows]
        shifted_hive_b_completion = [
            _completion_fraction_at_tick(row) for row in shifted_hive_b_rows
        ]
        rows.append(
            {
                "mode": mode,
                "seed": seed,
                "coupling_mode": cross_rows[0]["coupling_mode"],
                "delay_ticks": delay_ticks,
                "block_size": block_size,
                "offset": offset,
                "tick_count": tick_count,
                "transfer_attempts_total": sum(
                    _int(row["transfer_attempts_tick"]) for row in cross_rows
                ),
                "transfers_completed_total": sum(
                    _int(row["transfers_completed_tick"]) for row in cross_rows
                ),
                "load_backlog_corr_lag0": _lagged_correlation(
                    hive_a_backlog, shifted_hive_b_backlog, 0
                ),
                "load_backlog_corr_lag2": _lagged_correlation(
                    hive_a_backlog, shifted_hive_b_backlog, 2
                ),
                "completion_fraction_corr_lag0": _lagged_correlation(
                    hive_a_completion, shifted_hive_b_completion, 0
                ),
                "completion_fraction_corr_lag2": _lagged_correlation(
                    hive_a_completion, shifted_hive_b_completion, 2
                ),
                "queued_age_divergence_final": _format_number(
                    abs(
                        _float(hive_a_rows[-1]["queued_task_age_mean_tick"])
                        - _float(shifted_hive_b_rows[-1]["queued_task_age_mean_tick"])
                    )
                ),
                "completion_fraction_divergence_final": _format_number(
                    abs(hive_a_completion[-1] - shifted_hive_b_completion[-1])
                ),
            }
        )
    return rows, offsets, _coupling_manifest_fields(coupling_rows)


def _coupling_manifest_fields(coupling_rows: list[dict[str, str]]) -> dict[str, Any]:
    accepted_rows = [row for row in coupling_rows if row.get("transfer_decision") == "True"]
    delay_counts: dict[int, int] = defaultdict(int)
    for row in accepted_rows:
        delay = _int(row.get("arrival_tick")) - _int(row.get("tick"))
        delay_counts[delay] += 1
    return {
        "transfer_decision_count": len(accepted_rows),
        "arrival_delay_counts": "|".join(
            f"{delay}:{count}" for delay, count in sorted(delay_counts.items())
        ),
    }


def _offsets_for(tick_count: int, block_size: int, delay_ticks: int) -> tuple[int, ...]:
    offsets = tuple(
        offset
        for offset in range(block_size, tick_count, block_size)
        if offset not in {0, delay_ticks}
    )
    if not offsets:
        raise ValueError(
            f"No legal circular-shift offsets for tick_count={tick_count}, "
            f"block_size={block_size}, delay_ticks={delay_ticks}."
        )
    return offsets


def _circular_shift(values: list[Any], offset: int) -> list[Any]:
    if not values:
        return []
    normalized = offset % len(values)
    if normalized == 0:
        return list(values)
    return list(values[normalized:]) + list(values[:normalized])


def _completion_fraction_at_tick(row: dict[str, str]) -> float:
    created = _int(row["tasks_created_total"])
    if created == 0:
        return 0.0
    return round(_int(row["tasks_completed_total"]) / created, 6)


def _null_effect_rows(
    observed_rows: list[dict[str, Any]],
    null_rows: list[dict[str, Any]],
    seeds: tuple[int, ...],
) -> list[dict[str, Any]]:
    observed_index = {(row["mode"], int(row["seed"])): row for row in observed_rows}
    null_index = {
        (row["mode"], int(row["seed"]), int(row["block_size"]), int(row["offset"])): row
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
        for endpoint in A4_DELAYED_NULL_ENDPOINTS:
            observed_seed_deltas = {}
            seed_null_deltas: dict[int, list[float]] = defaultdict(list)
            null_deltas = []
            for seed in seeds:
                high = _effect_value(observed_index[(high_mode, seed)][endpoint])
                low = _effect_value(observed_index[(low_mode, seed)][endpoint])
                if high is not None and low is not None:
                    observed_seed_deltas[seed] = high - low
            for seed, block_size, offset in replicate_keys:
                high_row = null_index.get((high_mode, seed, block_size, offset))
                low_row = null_index.get((low_mode, seed, block_size, offset))
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
                _summarize_null_effect(
                    comparison=comparison,
                    endpoint=endpoint,
                    observed_seed_deltas=observed_seed_deltas,
                    null_deltas=null_deltas,
                    seed_null_deltas=seed_null_deltas,
                )
            )
    return rows


def _summarize_null_effect(
    *,
    comparison: str,
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
        "# A4 Delayed-Coupling Temporal Null Analysis",
        "",
        f"- source: `{source_path}`",
        f"- seeds: {seeds[0]}..{seeds[-1]}",
        f"- block sizes: {', '.join(str(size) for size in block_sizes)}",
        f"- null endpoint rows: {len(null_rows)}",
        "- method: deterministic circular block shifts of hive_b relative to hive_a.",
        "- excluded offsets: 0 and each run's configured causal delay.",
        "- This analyzer is read-only and does not run or rewrite A4 holdout seeds.",
        "",
        "## Delayed Minus None Primary Endpoints",
        "",
        "| endpoint | observed_mean_delta | null_mean_delta | null_ci | observed_minus_null_mean | outside_null_ci | seed_centered_positive_rate |",
        "| --- | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in delayed_rows:
        lines.append(
            "| {endpoint} | {observed_mean_delta} | {null_mean_delta} | [{null_delta_ci_low}, {null_delta_ci_high}] | {observed_minus_null_mean} | {observed_outside_null_ci} | {seed_observed_minus_seed_null_positive_rate} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Output Tables",
            "",
            "- `a4_delayed_null_endpoints.csv`: per-mode, per-seed circular-shift endpoint replicates.",
            "- `a4_delayed_null_effects.csv`: observed mode contrasts compared with circular-shift null deltas.",
            "- `a4_delayed_null_manifest.csv`: deterministic block sizes and offsets used for each mode/seed.",
            "",
            "## Interpretation Boundary",
            "",
            "- The two-hive shuffled condition remains a schema/source-opportunity control, not a phase-randomization null.",
            "- Effects inside the null interval or with weak seed-centered sign support remain queue-flow/service diagnostics rather than mechanism claims.",
            "- No simulator mechanics, configs, lobe labels, dashboards, real LLM calls, or external integrations are added by this analysis.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build deterministic temporal-shift nulls from existing A4 holdout artifacts."
    )
    parser.add_argument("--holdout-dir", default=str(DEFAULT_A4_HOLDOUT_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_A4_DELAYED_NULL_OUT_DIR))
    parser.add_argument(
        "--doc-out",
        default=str(DEFAULT_A4_DELAYED_NULL_DOC),
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
        help="Overwrite existing delayed-null outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a4_delayed_null_analysis(
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
