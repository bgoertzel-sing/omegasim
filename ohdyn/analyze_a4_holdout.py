"""Read existing A4 holdout artifacts and emit paired-seed endpoint tables."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from ohdyn.sim import BASELINE_ROLES


DEFAULT_A4_HOLDOUT_DIR = Path("runs/a4_two_hive_holdout_seed100_129")
DEFAULT_A4_HOLDOUT_OUT_DIR = Path("runs/a4_two_hive_holdout_seed100_129_analysis")
DEFAULT_A4_SEEDS = tuple(range(100, 130))
DEFAULT_A4_BOOTSTRAP_REPS = 1000
DEFAULT_A4_BOOTSTRAP_SEED = 4404
A4_HOLDOUT_MODES = ("none", "direct", "delayed", "shuffled")
A4_HOLDOUT_COMPARISONS = (
    ("direct_minus_none", "direct", "none"),
    ("delayed_minus_none", "delayed", "none"),
    ("shuffled_minus_none", "shuffled", "none"),
    ("direct_minus_shuffled", "direct", "shuffled"),
)
A4_REQUIRED_ARTIFACTS = (
    "config.yaml",
    "manifest.yaml",
    "hive_metrics.csv",
    "cross_hive_metrics.csv",
    "coupling_events.csv",
)
A4_HIVE_ENDPOINT_FIELDS = (
    "mode",
    "seed",
    "hive_id",
    "tasks_created_total",
    "agent_tasks_created_total",
    "exogenous_tasks_created_total",
    "tasks_completed_total",
    "completion_fraction",
    "queue_depth_final",
    "load_normalized_backlog_final",
    "queued_task_age_mean_final",
    "queued_task_age_max_peak",
    "work_events_total",
    "inbound_transfers_total",
    "outbound_transfers_total",
    "idle_actions_total",
    "message_actions_total",
    "create_task_actions_total",
    "work_task_actions_total",
    "role_action_totals",
)
A4_CROSS_ENDPOINT_FIELDS = (
    "mode",
    "seed",
    "coupling_mode",
    "delay_ticks",
    "transfer_attempts_total",
    "transfers_completed_total",
    "aggregate_inbound_transfers_total",
    "aggregate_outbound_transfers_total",
    "queued_age_divergence_final",
    "queued_age_divergence_mean",
    "completion_fraction_divergence_final",
    "completion_fraction_divergence_mean",
    "load_backlog_corr_lag0",
    "load_backlog_corr_lag2",
    "completion_fraction_corr_lag0",
    "completion_fraction_corr_lag2",
    "hive_a_to_hive_b_transfers",
    "hive_b_to_hive_a_transfers",
)
A4_EFFECT_FIELDS = (
    "comparison",
    "endpoint_scope",
    "hive_id",
    "endpoint",
    "high_mode",
    "low_mode",
    "paired_seed_count",
    "high_mean",
    "low_mean",
    "mean_delta",
    "median_delta",
    "positive_delta_rate",
    "bootstrap_reps",
    "bootstrap_seed",
    "bootstrap_mean_delta_ci_low",
    "bootstrap_mean_delta_ci_high",
    "bootstrap_median_delta_ci_low",
    "bootstrap_median_delta_ci_high",
    "bootstrap_positive_delta_rate_ci_low",
    "bootstrap_positive_delta_rate_ci_high",
    "bootstrap_sign_stability",
)
HIVE_EFFECT_ENDPOINTS = tuple(
    field
    for field in A4_HIVE_ENDPOINT_FIELDS
    if field not in {"mode", "seed", "hive_id", "role_action_totals"}
)
CROSS_EFFECT_ENDPOINTS = tuple(
    field
    for field in A4_CROSS_ENDPOINT_FIELDS
    if field not in {"mode", "seed", "coupling_mode"}
)


def run_a4_holdout_analysis(
    *,
    holdout_dir: str | Path = DEFAULT_A4_HOLDOUT_DIR,
    out_dir: str | Path = DEFAULT_A4_HOLDOUT_OUT_DIR,
    seeds: tuple[int, ...] = DEFAULT_A4_SEEDS,
    bootstrap_reps: int = DEFAULT_A4_BOOTSTRAP_REPS,
    bootstrap_seed: int = DEFAULT_A4_BOOTSTRAP_SEED,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Analyze an existing A4 holdout directory without running simulations."""

    if not seeds:
        raise ValueError("At least one seed is required.")
    _validate_bootstrap_options(bootstrap_reps, bootstrap_seed)
    source_path = Path(holdout_dir)
    output_path = Path(out_dir)
    _validate_source(source_path, seeds)
    _ensure_outputs_available(output_path, overwrite=overwrite)
    output_path.mkdir(parents=True, exist_ok=True)

    hive_rows: list[dict[str, Any]] = []
    cross_rows: list[dict[str, Any]] = []
    for mode in A4_HOLDOUT_MODES:
        for seed in seeds:
            run_path = source_path / f"{mode}_seed{seed}"
            hive_rows.extend(_hive_endpoints(run_path, mode, seed))
            cross_rows.append(_cross_endpoints(run_path, mode, seed))

    effect_rows = _effect_rows(
        hive_rows,
        cross_rows,
        bootstrap_reps=bootstrap_reps,
        bootstrap_seed=bootstrap_seed,
    )
    _write_csv(output_path / "a4_holdout_hive_endpoints.csv", A4_HIVE_ENDPOINT_FIELDS, hive_rows)
    _write_csv(
        output_path / "a4_holdout_cross_hive_endpoints.csv",
        A4_CROSS_ENDPOINT_FIELDS,
        cross_rows,
    )
    _write_csv(output_path / "a4_holdout_effects.csv", A4_EFFECT_FIELDS, effect_rows)
    (output_path / "summary.md").write_text(
        _summary(source_path, seeds, hive_rows, cross_rows, effect_rows)
    )
    return {
        "out_dir": str(output_path),
        "seed_count": len(seeds),
        "run_count": len(A4_HOLDOUT_MODES) * len(seeds),
        "hive_endpoint_rows": len(hive_rows),
        "cross_endpoint_rows": len(cross_rows),
        "effect_rows": len(effect_rows),
        "bootstrap_reps": bootstrap_reps,
        "bootstrap_seed": bootstrap_seed,
    }


def _validate_bootstrap_options(bootstrap_reps: int, bootstrap_seed: int) -> None:
    if isinstance(bootstrap_reps, bool) or not isinstance(bootstrap_reps, int):
        raise ValueError("bootstrap_reps must be an integer.")
    if bootstrap_reps <= 0:
        raise ValueError("bootstrap_reps must be positive.")
    if isinstance(bootstrap_seed, bool) or not isinstance(bootstrap_seed, int):
        raise ValueError("bootstrap_seed must be an integer.")


def _validate_source(source_path: Path, seeds: tuple[int, ...]) -> None:
    if not source_path.is_dir():
        raise FileNotFoundError(f"A4 holdout directory does not exist: {source_path}")
    missing: list[str] = []
    for mode in A4_HOLDOUT_MODES:
        for seed in seeds:
            run_path = source_path / f"{mode}_seed{seed}"
            for artifact in A4_REQUIRED_ARTIFACTS:
                if not (run_path / artifact).is_file():
                    missing.append(str(run_path / artifact))
    if missing:
        sample = ", ".join(missing[:6])
        suffix = "" if len(missing) <= 6 else f", ... ({len(missing)} missing total)"
        raise FileNotFoundError(f"A4 holdout source is missing artifacts: {sample}{suffix}")


def _ensure_outputs_available(output_path: Path, *, overwrite: bool) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        name
        for name in (
            "a4_holdout_hive_endpoints.csv",
            "a4_holdout_cross_hive_endpoints.csv",
            "a4_holdout_effects.csv",
            "summary.md",
        )
        if (output_path / name).exists()
    ]
    if collisions and not overwrite:
        raise FileExistsError(
            f"Output path {output_path} already contains A4 analysis artifacts: "
            f"{', '.join(collisions)}"
        )


def _hive_endpoints(run_path: Path, mode: str, seed: int) -> list[dict[str, Any]]:
    hive_rows = _read_csv(run_path / "hive_metrics.csv")
    by_hive: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in hive_rows:
        by_hive[row["hive_id"]].append(row)
    endpoints = []
    for hive_id, rows in sorted(by_hive.items()):
        last = rows[-1]
        created = _int(last["tasks_created_total"])
        completed = _int(last["tasks_completed_total"])
        queue_depth = _int(last["queue_depth"])
        role_counts = _role_action_totals(rows)
        endpoints.append(
            {
                "mode": mode,
                "seed": seed,
                "hive_id": hive_id,
                "tasks_created_total": created,
                "agent_tasks_created_total": _int(last.get("agent_tasks_created_total", "")),
                "exogenous_tasks_created_total": _int(
                    last.get("exogenous_tasks_created_total", "")
                ),
                "tasks_completed_total": completed,
                "completion_fraction": _safe_ratio(completed, created),
                "queue_depth_final": queue_depth,
                "load_normalized_backlog_final": _safe_ratio(queue_depth, created),
                "queued_task_age_mean_final": _float(last["queued_task_age_mean_tick"]),
                "queued_task_age_max_peak": max(
                    _int(row["queued_task_age_max_tick"]) for row in rows
                ),
                "work_events_total": sum(_int(row["tasks_worked_tick"]) for row in rows),
                "inbound_transfers_total": sum(
                    _int(row["inbound_transfers_tick"]) for row in rows
                ),
                "outbound_transfers_total": sum(
                    _int(row["outbound_transfers_tick"]) for row in rows
                ),
                "idle_actions_total": sum(_int(row["idle_tick"]) for row in rows),
                "message_actions_total": sum(_int(row["messages_sent_tick"]) for row in rows),
                "create_task_actions_total": sum(
                    _int(row["tasks_created_tick"]) for row in rows
                ),
                "work_task_actions_total": sum(_int(row["tasks_worked_tick"]) for row in rows),
                "role_action_totals": "|".join(
                    f"{key}:{value}" for key, value in sorted(role_counts.items())
                ),
            }
        )
    return endpoints


def _cross_endpoints(run_path: Path, mode: str, seed: int) -> dict[str, Any]:
    manifest = yaml.safe_load((run_path / "manifest.yaml").read_text())
    config = yaml.safe_load((run_path / "config.yaml").read_text())
    hive_ids = manifest.get("hive_ids", [])
    if hive_ids != ["hive_a", "hive_b"]:
        raise ValueError(f"{run_path} must contain hive_a and hive_b in order.")
    cross_rows = _read_csv(run_path / "cross_hive_metrics.csv")
    coupling_rows = _read_csv(run_path / "coupling_events.csv")
    directions = Counter(
        (row["source_hive_id"], row["target_hive_id"])
        for row in coupling_rows
        if row.get("transfer_decision") == "True"
    )
    hive_metrics = _read_csv(run_path / "hive_metrics.csv")
    by_hive: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in hive_metrics:
        by_hive[row["hive_id"]].append(row)
    hive_a_completion = [
        _completion_fraction_at_tick(row) for row in by_hive["hive_a"]
    ]
    hive_b_completion = [
        _completion_fraction_at_tick(row) for row in by_hive["hive_b"]
    ]
    hive_a_backlog = [
        _float(row["hive_a_load_normalized_backlog_tick"]) for row in cross_rows
    ]
    hive_b_backlog = [
        _float(row["hive_b_load_normalized_backlog_tick"]) for row in cross_rows
    ]
    return {
        "mode": mode,
        "seed": seed,
        "coupling_mode": manifest["coupling_mode"],
        "delay_ticks": config.get("coupling", {}).get("delay_ticks", 0),
        "transfer_attempts_total": sum(_int(row["transfer_attempts_tick"]) for row in cross_rows),
        "transfers_completed_total": sum(
            _int(row["transfers_completed_tick"]) for row in cross_rows
        ),
        "aggregate_inbound_transfers_total": sum(
            _int(row["aggregate_inbound_transfers_tick"]) for row in cross_rows
        ),
        "aggregate_outbound_transfers_total": sum(
            _int(row["aggregate_outbound_transfers_tick"]) for row in cross_rows
        ),
        "queued_age_divergence_final": _float(cross_rows[-1]["queued_age_mean_divergence_tick"]),
        "queued_age_divergence_mean": _mean(
            _float(row["queued_age_mean_divergence_tick"]) for row in cross_rows
        ),
        "completion_fraction_divergence_final": _float(
            cross_rows[-1]["completion_fraction_divergence_tick"]
        ),
        "completion_fraction_divergence_mean": _mean(
            _float(row["completion_fraction_divergence_tick"]) for row in cross_rows
        ),
        "load_backlog_corr_lag0": _lagged_correlation(hive_a_backlog, hive_b_backlog, 0),
        "load_backlog_corr_lag2": _lagged_correlation(hive_a_backlog, hive_b_backlog, 2),
        "completion_fraction_corr_lag0": _lagged_correlation(
            hive_a_completion, hive_b_completion, 0
        ),
        "completion_fraction_corr_lag2": _lagged_correlation(
            hive_a_completion, hive_b_completion, 2
        ),
        "hive_a_to_hive_b_transfers": directions[("hive_a", "hive_b")],
        "hive_b_to_hive_a_transfers": directions[("hive_b", "hive_a")],
    }


def _effect_rows(
    hive_rows: list[dict[str, Any]],
    cross_rows: list[dict[str, Any]],
    *,
    bootstrap_reps: int,
    bootstrap_seed: int,
) -> list[dict[str, Any]]:
    rows = []
    hive_index = {
        (row["mode"], row["seed"], row["hive_id"]): row
        for row in hive_rows
    }
    cross_index = {(row["mode"], row["seed"]): row for row in cross_rows}
    seeds = sorted({int(row["seed"]) for row in cross_rows})
    hive_ids = sorted({str(row["hive_id"]) for row in hive_rows})
    for comparison, high_mode, low_mode in A4_HOLDOUT_COMPARISONS:
        for hive_id in hive_ids:
            for endpoint in HIVE_EFFECT_ENDPOINTS:
                pairs = [
                    (
                        _effect_value(hive_index[(high_mode, seed, hive_id)][endpoint]),
                        _effect_value(hive_index[(low_mode, seed, hive_id)][endpoint]),
                    )
                    for seed in seeds
                ]
                rows.append(
                    _summarize_effect(
                        comparison=comparison,
                        endpoint_scope="hive",
                        hive_id=hive_id,
                        endpoint=endpoint,
                        high_mode=high_mode,
                        low_mode=low_mode,
                        pairs=pairs,
                        bootstrap_reps=bootstrap_reps,
                        bootstrap_seed=bootstrap_seed,
                    )
                )
        for endpoint in CROSS_EFFECT_ENDPOINTS:
            pairs = [
                (
                    _effect_value(cross_index[(high_mode, seed)][endpoint]),
                    _effect_value(cross_index[(low_mode, seed)][endpoint]),
                )
                for seed in seeds
            ]
            rows.append(
                _summarize_effect(
                    comparison=comparison,
                    endpoint_scope="cross_hive",
                    hive_id="all",
                    endpoint=endpoint,
                    high_mode=high_mode,
                    low_mode=low_mode,
                    pairs=pairs,
                    bootstrap_reps=bootstrap_reps,
                    bootstrap_seed=bootstrap_seed,
                )
            )
    return rows


def _summarize_effect(
    *,
    comparison: str,
    endpoint_scope: str,
    hive_id: str,
    endpoint: str,
    high_mode: str,
    low_mode: str,
    pairs: list[tuple[float | None, float | None]],
    bootstrap_reps: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    valid_pairs = [(high, low) for high, low in pairs if high is not None and low is not None]
    if not valid_pairs:
        return {
            "comparison": comparison,
            "endpoint_scope": endpoint_scope,
            "hive_id": hive_id,
            "endpoint": endpoint,
            "high_mode": high_mode,
            "low_mode": low_mode,
            "paired_seed_count": 0,
            "high_mean": "NA",
            "low_mean": "NA",
            "mean_delta": "NA",
            "median_delta": "NA",
            "positive_delta_rate": "NA",
            "bootstrap_reps": bootstrap_reps,
            "bootstrap_seed": bootstrap_seed,
            "bootstrap_mean_delta_ci_low": "NA",
            "bootstrap_mean_delta_ci_high": "NA",
            "bootstrap_median_delta_ci_low": "NA",
            "bootstrap_median_delta_ci_high": "NA",
            "bootstrap_positive_delta_rate_ci_low": "NA",
            "bootstrap_positive_delta_rate_ci_high": "NA",
            "bootstrap_sign_stability": "NA",
        }
    highs = [high for high, _low in valid_pairs]
    lows = [low for _high, low in valid_pairs]
    deltas = [high - low for high, low in valid_pairs]
    bootstrap = _bootstrap_delta_stats(
        deltas,
        bootstrap_reps=bootstrap_reps,
        bootstrap_seed=_effect_bootstrap_seed(
            bootstrap_seed,
            comparison=comparison,
            endpoint_scope=endpoint_scope,
            hive_id=hive_id,
            endpoint=endpoint,
        ),
    )
    return {
        "comparison": comparison,
        "endpoint_scope": endpoint_scope,
        "hive_id": hive_id,
        "endpoint": endpoint,
        "high_mode": high_mode,
        "low_mode": low_mode,
        "paired_seed_count": len(valid_pairs),
        "high_mean": _format_number(_mean(highs)),
        "low_mean": _format_number(_mean(lows)),
        "mean_delta": _format_number(_mean(deltas)),
        "median_delta": _format_number(_median(deltas)),
        "positive_delta_rate": _format_number(
            sum(1 for delta in deltas if delta > 0.0) / len(deltas)
        ),
        "bootstrap_reps": bootstrap_reps,
        "bootstrap_seed": bootstrap_seed,
        "bootstrap_mean_delta_ci_low": _format_number(bootstrap["mean_ci_low"]),
        "bootstrap_mean_delta_ci_high": _format_number(bootstrap["mean_ci_high"]),
        "bootstrap_median_delta_ci_low": _format_number(bootstrap["median_ci_low"]),
        "bootstrap_median_delta_ci_high": _format_number(bootstrap["median_ci_high"]),
        "bootstrap_positive_delta_rate_ci_low": _format_number(
            bootstrap["positive_rate_ci_low"]
        ),
        "bootstrap_positive_delta_rate_ci_high": _format_number(
            bootstrap["positive_rate_ci_high"]
        ),
        "bootstrap_sign_stability": _format_number(bootstrap["sign_stability"]),
    }


def _effect_bootstrap_seed(
    bootstrap_seed: int,
    *,
    comparison: str,
    endpoint_scope: str,
    hive_id: str,
    endpoint: str,
) -> int:
    key = f"{bootstrap_seed}|{comparison}|{endpoint_scope}|{hive_id}|{endpoint}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _bootstrap_delta_stats(
    deltas: list[float],
    *,
    bootstrap_reps: int,
    bootstrap_seed: int,
) -> dict[str, float]:
    rng = random.Random(bootstrap_seed)
    mean_values: list[float] = []
    median_values: list[float] = []
    positive_rates: list[float] = []
    sample_size = len(deltas)
    for _ in range(bootstrap_reps):
        sample = [rng.choice(deltas) for _index in range(sample_size)]
        mean_values.append(_mean(sample))
        median_values.append(_median(sample))
        positive_rates.append(sum(1 for value in sample if value > 0.0) / sample_size)
    observed_mean = _mean(deltas)
    return {
        "mean_ci_low": _quantile(mean_values, 0.025),
        "mean_ci_high": _quantile(mean_values, 0.975),
        "median_ci_low": _quantile(median_values, 0.025),
        "median_ci_high": _quantile(median_values, 0.975),
        "positive_rate_ci_low": _quantile(positive_rates, 0.025),
        "positive_rate_ci_high": _quantile(positive_rates, 0.975),
        "sign_stability": _sign_stability(mean_values, observed_mean),
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows and path.name != "coupling_events.csv":
        raise ValueError(f"{path} contains no rows.")
    return rows


def _role_action_totals(rows: list[dict[str, str]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        actions = ("idle", "message", "create_task", "work_task")
        for role in BASELINE_ROLES:
            for action in actions:
                field = f"role_{role}_{action}_tick"
                if field in row:
                    counts[f"{role}_{action}"] += _int(row[field])
    return counts


def _completion_fraction_at_tick(row: dict[str, str]) -> float:
    return _safe_ratio(_int(row["tasks_completed_total"]), _int(row["tasks_created_total"]))


def _effect_value(value: Any) -> float | None:
    if value == "NA":
        return None
    return float(value)


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _int(value: Any) -> int:
    if value in ("", None):
        return 0
    return int(value)


def _float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    return float(value)


def _mean(values: Any) -> float:
    collected = list(values)
    if not collected:
        return 0.0
    return sum(collected) / len(collected)


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2.0


def _quantile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * quantile)
    return ordered[index]


def _sign_stability(values: list[float], observed_delta: float) -> float:
    if not values or observed_delta == 0.0:
        return 0.0
    if observed_delta > 0.0:
        stable = sum(1 for value in values if value > 0.0)
    else:
        stable = sum(1 for value in values if value < 0.0)
    return stable / len(values)


def _lagged_correlation(left: list[float], right: list[float], lag: int) -> str:
    if lag < 0:
        raise ValueError("lag must be non-negative.")
    if lag:
        if len(left) <= lag or len(right) <= lag:
            return "NA"
        left_values = left[:-lag]
        right_values = right[lag:]
    else:
        left_values = left
        right_values = right
    if len(left_values) < 2 or len(right_values) < 2:
        return "NA"
    left_mean = _mean(left_values)
    right_mean = _mean(right_values)
    left_ss = sum((value - left_mean) ** 2 for value in left_values)
    right_ss = sum((value - right_mean) ** 2 for value in right_values)
    if left_ss == 0.0 or right_ss == 0.0:
        return "NA"
    covariance = sum(
        (left_value - left_mean) * (right_value - right_mean)
        for left_value, right_value in zip(left_values, right_values)
    )
    return _format_number(covariance / math.sqrt(left_ss * right_ss))


def _format_number(value: float) -> str:
    return f"{value:.6f}"


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    source_path: Path,
    seeds: tuple[int, ...],
    hive_rows: list[dict[str, Any]],
    cross_rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
) -> str:
    transfer_rows = [
        row
        for row in effect_rows
        if row["endpoint_scope"] == "cross_hive"
        and row["endpoint"] == "transfer_attempts_total"
    ]
    lines = [
        "# A4 Holdout Paired-Seed Analysis",
        "",
        f"- source: `{source_path}`",
        f"- seeds: {seeds[0]}..{seeds[-1]}",
        f"- seed count: {len(seeds)}",
        f"- modes: {', '.join(A4_HOLDOUT_MODES)}",
        f"- hive endpoint rows: {len(hive_rows)}",
        f"- cross-hive endpoint rows: {len(cross_rows)}",
        "",
        "## Transfer Effects",
        "",
        "| comparison | paired_seed_count | mean_delta | mean_delta_ci | positive_delta_rate | sign_stability |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in transfer_rows:
        lines.append(
            "| {comparison} | {paired_seed_count} | {mean_delta} | [{bootstrap_mean_delta_ci_low}, {bootstrap_mean_delta_ci_high}] | {positive_delta_rate} | {bootstrap_sign_stability} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Output Tables",
            "",
            "- `a4_holdout_hive_endpoints.csv`: per-mode, per-seed, per-hive queue-flow/service/action endpoints.",
            "- `a4_holdout_cross_hive_endpoints.csv`: per-mode, per-seed transfer, divergence, and fixed-lag correlation endpoints.",
            "- `a4_holdout_effects.csv`: paired-seed high-minus-low effects for preregistered comparisons, including deterministic paired-bootstrap uncertainty fields.",
            "",
            "## Interpretation Boundary",
            "",
            "- This analyzer is read-only and does not run A4 holdout seeds.",
            "- `direct_minus_shuffled` is included as a source-opportunity matched contrast, but two-hive shuffled is not a meaningful target-randomization null.",
            "- Lobe diagnostics are intentionally not promoted to A4 mechanism evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_seed_args(seed_args: list[str] | None) -> tuple[int, ...]:
    if not seed_args:
        return DEFAULT_A4_SEEDS
    seeds: list[int] = []
    for seed_arg in seed_args:
        if ".." in seed_arg:
            start, end = seed_arg.split("..", maxsplit=1)
            seeds.extend(range(int(start), int(end) + 1))
        else:
            seeds.append(int(seed_arg))
    return tuple(dict.fromkeys(seeds))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze existing A4 holdout artifacts without running simulations."
    )
    parser.add_argument("--holdout-dir", default=str(DEFAULT_A4_HOLDOUT_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_A4_HOLDOUT_OUT_DIR))
    parser.add_argument(
        "--seeds",
        nargs="*",
        help="Seed list or inclusive ranges like 100..129. Defaults to 100..129.",
    )
    parser.add_argument(
        "--bootstrap-reps",
        type=int,
        default=DEFAULT_A4_BOOTSTRAP_REPS,
        help="Deterministic paired bootstrap resamples per endpoint.",
    )
    parser.add_argument(
        "--bootstrap-seed",
        type=int,
        default=DEFAULT_A4_BOOTSTRAP_SEED,
        help="Base seed for deterministic paired bootstrap resampling.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing A4 analyzer outputs in --out-dir.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_a4_holdout_analysis(
            holdout_dir=args.holdout_dir,
            out_dir=args.out_dir,
            seeds=_parse_seed_args(args.seeds),
            bootstrap_reps=args.bootstrap_reps,
            bootstrap_seed=args.bootstrap_seed,
            overwrite=args.overwrite,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
