"""Read pressure comparison artifacts and rank trajectory-vs-pressure responses."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

from ohdyn.compare_pressure import (
    PRESSURE_CURVE_METRICS,
    PRESSURE_CURVE_OBSERVABLES,
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

    pressure_rows = _read_csv(pressure_path / "pressure_comparison_metrics.csv")
    trajectory_rows = _read_csv(pressure_path / "pressure_trajectory_structure.csv")
    rows = _trajectory_pressure_rows(
        pressure_rows=pressure_rows,
        trajectory_rows=trajectory_rows,
        limit=limit,
    )

    output_path.mkdir(parents=True, exist_ok=True)
    _write_ranking_csv(output_path / "trajectory_pressure_ranking.csv", rows)
    (output_path / "summary.md").write_text(
        _summary(
            pressure_dir=pressure_path,
            rows=rows,
            pressure_row_count=len(pressure_rows),
            trajectory_row_count=len(trajectory_rows),
            limit=limit,
        )
    )
    return rows


def _validate_limit(limit: int) -> None:
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        raise ValueError("limit must be a positive integer.")


def _ensure_analysis_outputs_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        artifact_name
        for artifact_name in ("trajectory_pressure_ranking.csv", "summary.md")
        if (output_path / artifact_name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains analysis artifacts: {names}")


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Required pressure analysis input is missing: {path}")
    with path.open() as handle:
        return list(csv.DictReader(handle))


def _trajectory_pressure_rows(
    *,
    pressure_rows: list[dict[str, str]],
    trajectory_rows: list[dict[str, str]],
    limit: int,
) -> list[dict[str, Any]]:
    trajectory_by_policy = _rows_by_policy(trajectory_rows, "pressure_trajectory_structure.csv")
    missing = [
        row["policy"]
        for row in pressure_rows
        if row["policy"] not in trajectory_by_policy
    ]
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"pressure_trajectory_structure.csv is missing policies: {names}")

    candidates: list[dict[str, Any]] = []
    for pressure_row in pressure_rows:
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


def _write_ranking_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(TRAJECTORY_PRESSURE_RANKING_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def _summary(
    *,
    pressure_dir: Path,
    rows: list[dict[str, Any]],
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
    if not rows:
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
                    for row in rows
                ],
            ]
        )
    return "\n".join(lines) + "\n"


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
