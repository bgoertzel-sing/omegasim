"""Read pressure comparison artifacts and rank trajectory-vs-pressure responses."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_attention import COMPARISON_FIELDS
from ohdyn.compare_pressure import (
    PRESSURE_COMPARISON_FIELDS,
    PRESSURE_CURVE_METRICS,
    PRESSURE_CURVE_OBSERVABLES,
    PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
    _format_seed_set,
    _pressure_rows,
    _rows_for_seeds,
)


TRAJECTORY_PRESSURE_RANKING_FIELDS = (
    "rank",
    "policy",
    "response_observable",
    "response_metric",
    "response_field",
    "response_value",
    "response_abs_value",
    "turning_points_high_minus_normal_delta",
    "turning_points_abs_delta",
    "longest_dwell_steps_high_minus_normal_delta",
    "longest_dwell_steps_abs_delta",
    "trajectory_abs_delta_total",
)
VALUE_YIELD_DIVERGENCE_RANKING_FIELDS = (
    "rank",
    "policy",
    "metric",
    "value_per_completed_task_field",
    "value_per_work_event_field",
    "value_per_completed_task_response",
    "value_per_work_event_response",
    "divergence",
    "abs_divergence",
)
VALUE_YIELD_DIVERGENCE_STABILITY_FIELDS = (
    "full_seeds",
    "prefix_seeds",
    "stable_with_full",
    "instability_causes",
    "policy",
    "metric",
    "value_per_completed_task_field",
    "value_per_work_event_field",
    "value_per_completed_task_response",
    "value_per_work_event_response",
    "divergence",
    "abs_divergence",
    "full_policy",
    "full_metric",
)
INTERPRETATION_FIELDS = (
    "top_divergence_policy",
    "top_divergence_metric",
    "top_divergence_value_per_completed_task_response",
    "top_divergence_value_per_work_event_response",
    "top_divergence",
    "top_divergence_abs",
    "top_divergence_stable_last_prefix",
    "top_divergence_stable_all_prefixes",
    "top_divergence_full_seeds",
    "top_divergence_last_prefix_seeds",
    "top_divergence_last_prefix_instability_causes",
    "top_trajectory_policy",
    "top_trajectory_response_observable",
    "top_trajectory_response_metric",
    "top_trajectory_response_field",
    "top_trajectory_response_value",
    "top_trajectory_response_abs_value",
    "top_trajectory_abs_delta_total",
)
ANALYSIS_ARTIFACTS = (
    "trajectory_pressure_ranking.csv",
    "value_yield_divergence_ranking.csv",
    "value_yield_divergence_stability.csv",
    "interpretation.csv",
    "summary.md",
)


def run_analysis(
    *,
    pressure_dir: str | Path,
    out_dir: str | Path,
    limit: int = 10,
) -> list[dict[str, Any]]:
    _validate_limit(limit)
    pressure_path = Path(pressure_dir)
    output_path = Path(out_dir)
    _ensure_analysis_outputs_available(output_path)

    pressure_rows = _read_csv(
        pressure_path / "pressure_comparison_metrics.csv",
        required_fields=PRESSURE_COMPARISON_FIELDS,
    )
    trajectory_rows = _read_csv(
        pressure_path / "pressure_trajectory_structure.csv",
        required_fields=PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
    )
    trajectory_rows_ranked = _trajectory_pressure_rows(
        pressure_rows=pressure_rows,
        trajectory_rows=trajectory_rows,
        limit=limit,
    )
    value_yield_rows = _value_yield_divergence_rows(
        pressure_rows=pressure_rows,
        limit=limit,
    )
    divergence_stability_rows = _value_yield_divergence_stability_rows(
        pressure_dir=pressure_path,
        pressure_rows=pressure_rows,
    )
    interpretation_row = _interpretation_row(
        trajectory_rows=trajectory_rows_ranked,
        value_yield_rows=value_yield_rows,
        divergence_stability_rows=divergence_stability_rows,
    )

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "trajectory_pressure_ranking.csv",
        rows=trajectory_rows_ranked,
        fieldnames=TRAJECTORY_PRESSURE_RANKING_FIELDS,
    )
    _write_csv(
        output_path / "value_yield_divergence_ranking.csv",
        rows=value_yield_rows,
        fieldnames=VALUE_YIELD_DIVERGENCE_RANKING_FIELDS,
    )
    _write_csv(
        output_path / "value_yield_divergence_stability.csv",
        rows=divergence_stability_rows,
        fieldnames=VALUE_YIELD_DIVERGENCE_STABILITY_FIELDS,
    )
    _write_csv(
        output_path / "interpretation.csv",
        rows=[interpretation_row],
        fieldnames=INTERPRETATION_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(
            pressure_dir=pressure_path,
            trajectory_rows=trajectory_rows_ranked,
            value_yield_rows=value_yield_rows,
            divergence_stability_rows=divergence_stability_rows,
            pressure_row_count=len(pressure_rows),
            trajectory_row_count=len(trajectory_rows),
            limit=limit,
        )
    )
    return trajectory_rows_ranked


def _interpretation_row(
    *,
    trajectory_rows: list[dict[str, Any]],
    value_yield_rows: list[dict[str, Any]],
    divergence_stability_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    top_divergence = value_yield_rows[0] if value_yield_rows else {}
    top_trajectory = trajectory_rows[0] if trajectory_rows else {}
    last_prefix = divergence_stability_rows[-1] if divergence_stability_rows else {}
    all_prefixes_stable = (
        bool(divergence_stability_rows)
        and all(row["stable_with_full"] == "true" for row in divergence_stability_rows)
    )

    return {
        "top_divergence_policy": top_divergence.get("policy", ""),
        "top_divergence_metric": top_divergence.get("metric", ""),
        "top_divergence_value_per_completed_task_response": top_divergence.get(
            "value_per_completed_task_response",
            "",
        ),
        "top_divergence_value_per_work_event_response": top_divergence.get(
            "value_per_work_event_response",
            "",
        ),
        "top_divergence": top_divergence.get("divergence", ""),
        "top_divergence_abs": top_divergence.get("abs_divergence", ""),
        "top_divergence_stable_last_prefix": last_prefix.get("stable_with_full", ""),
        "top_divergence_stable_all_prefixes": (
            str(all_prefixes_stable).lower() if divergence_stability_rows else ""
        ),
        "top_divergence_full_seeds": last_prefix.get("full_seeds", ""),
        "top_divergence_last_prefix_seeds": last_prefix.get("prefix_seeds", ""),
        "top_divergence_last_prefix_instability_causes": last_prefix.get(
            "instability_causes",
            "",
        ),
        "top_trajectory_policy": top_trajectory.get("policy", ""),
        "top_trajectory_response_observable": top_trajectory.get(
            "response_observable",
            "",
        ),
        "top_trajectory_response_metric": top_trajectory.get("response_metric", ""),
        "top_trajectory_response_field": top_trajectory.get("response_field", ""),
        "top_trajectory_response_value": top_trajectory.get("response_value", ""),
        "top_trajectory_response_abs_value": top_trajectory.get(
            "response_abs_value",
            "",
        ),
        "top_trajectory_abs_delta_total": top_trajectory.get(
            "trajectory_abs_delta_total",
            "",
        ),
    }


def _validate_limit(limit: int) -> None:
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        raise ValueError("limit must be a positive integer.")


def _ensure_analysis_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [name for name in ANALYSIS_ARTIFACTS if (output_path / name).exists()]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains analysis artifacts: {names}")


def _read_csv(
    path: Path,
    *,
    required_fields: tuple[str, ...],
) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Required pressure analysis input is missing: {path}")
    with path.open() as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = [field for field in required_fields if field not in fieldnames]
        if missing:
            names = ", ".join(missing)
            raise ValueError(f"{path.name} is missing required fields: {names}")
        return list(reader)


def _trajectory_pressure_rows(
    *,
    pressure_rows: list[dict[str, str]],
    trajectory_rows: list[dict[str, str]],
    limit: int,
) -> list[dict[str, Any]]:
    pressure_by_policy = _rows_by_policy(pressure_rows, "pressure_comparison_metrics.csv")
    trajectory_by_policy = _rows_by_policy(trajectory_rows, "pressure_trajectory_structure.csv")
    pressure_policies = set(pressure_by_policy)
    trajectory_policies = set(trajectory_by_policy)
    missing = sorted(pressure_policies - trajectory_policies)
    extra = sorted(trajectory_policies - pressure_policies)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing policies in trajectory: {', '.join(missing)}")
        if extra:
            details.append(f"extra policies in trajectory: {', '.join(extra)}")
        raise ValueError(
            "Policy mismatch between pressure_comparison_metrics.csv and "
            f"pressure_trajectory_structure.csv: {'; '.join(details)}"
        )

    candidates: list[dict[str, Any]] = []
    for pressure_row in pressure_by_policy.values():
        policy = pressure_row["policy"]
        trajectory_row = trajectory_by_policy[policy]
        turning_delta = _float_field(
            trajectory_row,
            "turning_points_high_minus_normal_delta",
        )
        dwell_delta = _float_field(
            trajectory_row,
            "longest_dwell_steps_high_minus_normal_delta",
        )
        trajectory_total = round(abs(turning_delta) + abs(dwell_delta), 6)
        for observable_prefix, observable_label, _source_field in PRESSURE_CURVE_OBSERVABLES:
            for metric_suffix, metric_label in PRESSURE_CURVE_METRICS:
                field = f"{observable_prefix}_{metric_suffix}"
                value = _float_field(pressure_row, field)
                candidates.append(
                    {
                        "policy": policy,
                        "response_observable": observable_label,
                        "response_metric": metric_label,
                        "response_field": field,
                        "response_value": round(value, 6),
                        "response_abs_value": round(abs(value), 6),
                        "turning_points_high_minus_normal_delta": round(turning_delta, 6),
                        "turning_points_abs_delta": round(abs(turning_delta), 6),
                        "longest_dwell_steps_high_minus_normal_delta": round(dwell_delta, 6),
                        "longest_dwell_steps_abs_delta": round(abs(dwell_delta), 6),
                        "trajectory_abs_delta_total": trajectory_total,
                    }
                )

    candidates.sort(
        key=lambda row: (
            -float(row["response_abs_value"]),
            -float(row["trajectory_abs_delta_total"]),
            str(row["policy"]),
            str(row["response_observable"]),
            str(row["response_metric"]),
        )
    )
    return [
        {"rank": rank, **row}
        for rank, row in enumerate(candidates[:limit], start=1)
    ]


def _value_yield_divergence_stability_rows(
    *,
    pressure_dir: Path,
    pressure_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    normal_rows = _read_csv(
        pressure_dir / "normal_pressure" / "comparison_metrics.csv",
        required_fields=COMPARISON_FIELDS,
    )
    medium_pressure_rows = _read_csv(
        pressure_dir / "medium_pressure" / "comparison_metrics.csv",
        required_fields=COMPARISON_FIELDS,
    )
    high_pressure_rows = _read_csv(
        pressure_dir / "high_pressure" / "comparison_metrics.csv",
        required_fields=COMPARISON_FIELDS,
    )
    seeds = _comparison_seeds(normal_rows)
    if len(seeds) < 2:
        return []

    full_top = _value_yield_divergence_rows(pressure_rows=pressure_rows, limit=1)[0]
    rows: list[dict[str, Any]] = []
    for prefix_length in range(1, len(seeds)):
        prefix_seeds = seeds[:prefix_length]
        prefix_seed_set = set(prefix_seeds)
        prefix_pressure_rows = _pressure_rows(
            _rows_for_seeds(normal_rows, prefix_seed_set),
            _rows_for_seeds(medium_pressure_rows, prefix_seed_set),
            _rows_for_seeds(high_pressure_rows, prefix_seed_set),
        )
        prefix_top = _value_yield_divergence_rows(
            pressure_rows=prefix_pressure_rows,
            limit=1,
        )[0]
        stable_with_full = _same_value_yield_divergence(full_top, prefix_top)
        rows.append(
            {
                "full_seeds": _format_seed_set(seeds),
                "prefix_seeds": _format_seed_set(prefix_seeds),
                "stable_with_full": str(stable_with_full).lower(),
                "instability_causes": _value_yield_divergence_instability_causes(
                    full_top,
                    prefix_top,
                ),
                "policy": prefix_top["policy"],
                "metric": prefix_top["metric"],
                "value_per_completed_task_field": prefix_top[
                    "value_per_completed_task_field"
                ],
                "value_per_work_event_field": prefix_top[
                    "value_per_work_event_field"
                ],
                "value_per_completed_task_response": prefix_top[
                    "value_per_completed_task_response"
                ],
                "value_per_work_event_response": prefix_top[
                    "value_per_work_event_response"
                ],
                "divergence": prefix_top["divergence"],
                "abs_divergence": prefix_top["abs_divergence"],
                "full_policy": full_top["policy"],
                "full_metric": full_top["metric"],
            }
        )
    return rows


def _comparison_seeds(rows: list[dict[str, str]]) -> tuple[int, ...]:
    seeds: list[int] = []
    for row in rows:
        seed = int(row["seed"])
        if seed not in seeds:
            seeds.append(seed)
    return tuple(seeds)


def _same_value_yield_divergence(
    first: dict[str, Any],
    second: dict[str, Any],
) -> bool:
    return (first["policy"], first["metric"]) == (second["policy"], second["metric"])


def _value_yield_divergence_instability_causes(
    full_top: dict[str, Any],
    prefix_top: dict[str, Any],
) -> str:
    changed = []
    if full_top["policy"] != prefix_top["policy"]:
        changed.append("policy")
    if full_top["metric"] != prefix_top["metric"]:
        changed.append("metric")
    if not changed:
        return "none"
    return ",".join(changed)


def _value_yield_divergence_rows(
    *,
    pressure_rows: list[dict[str, str]],
    limit: int,
) -> list[dict[str, Any]]:
    _rows_by_policy(pressure_rows, "pressure_comparison_metrics.csv")
    candidates: list[dict[str, Any]] = []
    metric_fields = (
        (
            "high_minus_normal_delta",
            "value_per_completed_task_mean_delta",
            "value_per_work_event_mean_delta",
        ),
        (
            "normal_to_medium_slope",
            "value_per_completed_task_normal_to_medium_slope",
            "value_per_work_event_normal_to_medium_slope",
        ),
        (
            "medium_to_high_slope",
            "value_per_completed_task_medium_to_high_slope",
            "value_per_work_event_medium_to_high_slope",
        ),
        (
            "curvature",
            "value_per_completed_task_pressure_curvature",
            "value_per_work_event_pressure_curvature",
        ),
    )

    for pressure_row in pressure_rows:
        policy = pressure_row["policy"]
        for metric, completed_field, work_field in metric_fields:
            completed_response = _float_field(pressure_row, completed_field)
            work_response = _float_field(pressure_row, work_field)
            divergence = completed_response - work_response
            candidates.append(
                {
                    "policy": policy,
                    "metric": metric,
                    "value_per_completed_task_field": completed_field,
                    "value_per_work_event_field": work_field,
                    "value_per_completed_task_response": round(completed_response, 6),
                    "value_per_work_event_response": round(work_response, 6),
                    "divergence": round(divergence, 6),
                    "abs_divergence": round(abs(divergence), 6),
                }
            )

    candidates.sort(
        key=lambda row: (
            -float(row["abs_divergence"]),
            str(row["policy"]),
            str(row["metric"]),
        )
    )
    return [
        {"rank": rank, **row}
        for rank, row in enumerate(candidates[:limit], start=1)
    ]


def _rows_by_policy(
    rows: list[dict[str, str]],
    artifact_name: str,
) -> dict[str, dict[str, str]]:
    by_policy: dict[str, dict[str, str]] = {}
    for row in rows:
        policy = row.get("policy", "")
        if not policy:
            raise ValueError(f"{artifact_name} contains a row without policy.")
        if policy in by_policy:
            raise ValueError(f"{artifact_name} contains duplicate policy: {policy}")
        by_policy[policy] = row
    return by_policy


def _float_field(row: dict[str, str], field: str) -> float:
    try:
        return float(row[field])
    except KeyError as exc:
        raise ValueError(f"CSV row is missing required field: {field}") from exc


def _write_csv(
    path: Path,
    *,
    rows: list[dict[str, Any]],
    fieldnames: tuple[str, ...],
) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    *,
    pressure_dir: Path,
    trajectory_rows: list[dict[str, Any]],
    value_yield_rows: list[dict[str, Any]],
    divergence_stability_rows: list[dict[str, Any]],
    pressure_row_count: int,
    trajectory_row_count: int,
    limit: int,
) -> str:
    lines = [
        "# Trajectory-vs-pressure ranking",
        "",
        f"- pressure_dir: {pressure_dir}",
        f"- pressure rows: {pressure_row_count}",
        f"- trajectory rows: {trajectory_row_count}",
        f"- limit: {limit}",
        "",
        "## Ranking",
    ]
    if not trajectory_rows:
        lines.append("- none: no rows available")
    else:
        lines.extend(
            [
                "| rank | policy | response_observable | response_metric | response_value | trajectory_abs_delta_total |",
                "| ---: | --- | --- | --- | ---: | ---: |",
                *[
                    "| "
                    f"{row['rank']} | {row['policy']} | {row['response_observable']} | "
                    f"{row['response_metric']} | {row['response_value']} | "
                    f"{row['trajectory_abs_delta_total']} |"
                    for row in trajectory_rows
                ],
            ]
        )
    lines.extend(["", "## Value-yield divergence ranking"])
    if not value_yield_rows:
        lines.append("- none: no rows available")
    else:
        lines.extend(
            [
                "| rank | policy | metric | value_per_completed_task_response | value_per_work_event_response | divergence |",
                "| ---: | --- | --- | ---: | ---: | ---: |",
                *[
                    "| "
                    f"{row['rank']} | {row['policy']} | {row['metric']} | "
                    f"{row['value_per_completed_task_response']} | "
                    f"{row['value_per_work_event_response']} | {row['divergence']} |"
                    for row in value_yield_rows
                ],
            ]
        )
        lines.extend(
            [
                "",
                "## Top value-yield divergence interpretation",
                _value_yield_divergence_interpretation(value_yield_rows[0]),
            ]
        )
    lines.extend(["", "## Value-yield divergence prefix stability"])
    if not divergence_stability_rows:
        lines.append("- unavailable: at least two seeds are required for prefix stability.")
    else:
        last_prefix = divergence_stability_rows[-1]
        all_stable = all(
            row["stable_with_full"] == "true"
            for row in divergence_stability_rows
        )
        lines.extend(
            [
                f"- full_seeds: {last_prefix['full_seeds']}",
                f"- last_prefix: {last_prefix['prefix_seeds']}",
                (
                    "- top divergence stable across last prefix: "
                    f"{last_prefix['stable_with_full']}"
                ),
                f"- top divergence stable across all prefixes: {str(all_stable).lower()}",
                f"- last prefix instability causes: {last_prefix['instability_causes']}",
                "| prefix_seeds | top_divergence | stable_with_full | instability_causes |",
                "| --- | --- | --- | --- |",
                *[
                    "| "
                    f"{row['prefix_seeds']} | policy={row['policy']}, "
                    f"metric={row['metric']}, divergence={row['divergence']} | "
                    f"{row['stable_with_full']} | {row['instability_causes']} |"
                    for row in divergence_stability_rows
                ],
            ]
        )
    return "\n".join(lines) + "\n"


def _value_yield_divergence_interpretation(row: dict[str, Any]) -> str:
    completed_response = float(row["value_per_completed_task_response"])
    work_response = float(row["value_per_work_event_response"])
    completed_direction = _yield_direction(completed_response)
    work_direction = _yield_direction(work_response)
    pressure_tradeoff = _yield_divergence_interpretation(
        completed_response,
        work_response,
    )

    return (
        "- top divergence: "
        f"{row['policy']} {row['metric']} changes completion-normalized yield "
        f"by {completed_response:.6f} ({completed_direction}) and effort-normalized "
        f"yield by {work_response:.6f} ({work_direction}); {pressure_tradeoff}."
    )


def _yield_divergence_interpretation(
    completed_response: float,
    work_response: float,
) -> str:
    completed_sign = _sign(completed_response)
    work_sign = _sign(work_response)

    if completed_sign == work_sign == 1:
        stronger = _stronger_yield_axis(completed_response, work_response)
        return (
            "pressure improves both yield normalizations, with a larger "
            f"{stronger} response; this is a same-direction divergence, not a "
            "completion-vs-effort tradeoff"
        )
    if completed_sign == work_sign == -1:
        stronger = _stronger_yield_axis(completed_response, work_response)
        return (
            "pressure degrades both yield normalizations, with a larger "
            f"{stronger} response; this is a same-direction divergence, not a "
            "completion-vs-effort tradeoff"
        )
    if completed_sign == 1 and work_sign == -1:
        return (
            "pressure improves completion-normalized yield while degrading "
            "effort-normalized yield"
        )
    if completed_sign == -1 and work_sign == 1:
        return (
            "pressure degrades completion-normalized yield while improving "
            "effort-normalized yield"
        )
    if completed_sign == 0 and work_sign == 0:
        return "pressure leaves both yield normalizations unchanged"
    if completed_sign == 0:
        return (
            "pressure leaves completion-normalized yield unchanged while "
            f"{_yield_direction(work_response)} effort-normalized yield"
        )
    return (
        f"pressure {_yield_direction(completed_response)} completion-normalized "
        "yield while leaving effort-normalized yield unchanged"
    )


def _stronger_yield_axis(completed_response: float, work_response: float) -> str:
    completed_abs = abs(completed_response)
    work_abs = abs(work_response)
    if completed_abs > work_abs:
        return "completion-normalized"
    if work_abs > completed_abs:
        return "effort-normalized"
    return "equal-magnitude"


def _sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


def _yield_direction(value: float) -> str:
    if value > 0.0:
        return "improves"
    if value < 0.0:
        return "degrades"
    return "unchanged"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rank joined A2 pressure-response and trajectory-structure artifacts."
    )
    parser.add_argument(
        "--pressure-dir",
        required=True,
        help="Directory containing pressure_comparison_metrics.csv and pressure_trajectory_structure.csv.",
    )
    parser.add_argument("--out", required=True, help="Output directory for analysis artifacts.")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of ranked rows to write.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_analysis(
            pressure_dir=args.pressure_dir,
            out_dir=args.out,
            limit=args.limit,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
