"""Automation state guard for bounded OmegaSim research loops."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_STATUS_PATH = Path("AUTOMATION_STATUS.md")
DEFAULT_REVIEW_PATH = Path("../outputs/strategy-reviews/omegasim/latest-review.md")
DEFAULT_A5_PREREGISTRATION_PATH = Path(
    "docs/a5_anticipatory_predictive_control_preregistration.md"
)


def read_automation_state(
    status_path: str | Path = DEFAULT_STATUS_PATH,
    review_path: str | Path = DEFAULT_REVIEW_PATH,
    a5_preregistration_path: str | Path = DEFAULT_A5_PREREGISTRATION_PATH,
) -> dict[str, Any]:
    """Return the current automation state from local status/review artifacts."""

    status = _read_optional_text(Path(status_path))
    review = _read_optional_text(Path(review_path))
    review_header = _parse_review_header(review)
    a5_preregistration_active = Path(a5_preregistration_path).is_file()
    closed_reasons = _closed_reasons(status=status, review=review)
    if a5_preregistration_active and not _status_closes_active_a5(status):
        closed_reasons = []
    state = "closed_awaiting_preregistration" if closed_reasons else "open"

    status_next_action = _status_next_action(status)
    recommended_next_action = (
        status_next_action
        if closed_reasons and status_next_action
        else review_header.get("recommended_next_action", "")
    )

    return {
        "state": state,
        "should_noop": bool(closed_reasons),
        "closed_reasons": closed_reasons,
        "a5_preregistration_active": a5_preregistration_active,
        "strategic_change_level": review_header.get("strategic_change_level", ""),
        "notify_ben": _parse_bool(review_header.get("notify_ben", "")),
        "recommended_next_action": recommended_next_action,
        "review_recommended_next_action": review_header.get(
            "recommended_next_action", ""
        ),
    }


def _read_optional_text(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError:
        return ""


def _parse_review_header(review: str) -> dict[str, str]:
    header: dict[str, str] = {}
    for line in review.splitlines():
        if not line.strip():
            continue
        if line.startswith("#"):
            break
        if ":" not in line:
            break
        key, value = line.split(":", 1)
        header[key.strip()] = value.strip()
    return header


def _parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def _closed_reasons(*, status: str, review: str) -> list[str]:
    reasons = []
    normalized_status = _normalize(status)
    normalized_review = _normalize(review)

    if "next step: leave omegasim closed" in normalized_status:
        reasons.append("automation_status_next_step_closed")
    if "closed at the current a4 boundary" in normalized_status:
        reasons.append("automation_status_a4_closed")
    if (
        "state: closed_awaiting_preregistration" in normalized_status
        and "should_noop: true" in normalized_status
    ):
        reasons.append("automation_status_noop_guard")
    if "recommended next step: remain in no-op/awaiting-preregistration state" in normalized_status:
        reasons.append("automation_status_next_step_noop")
    if "do not reopen a5" in normalized_status:
        reasons.append("automation_status_a5_closed")
    if "explicit no-op/awaiting-preregistration state" in normalized_review:
        reasons.append("strategy_review_noop_awaiting_preregistration")
    if "do not run new simulations or analyzers now" in normalized_review:
        reasons.append("strategy_review_stop_new_work")

    return reasons


def _status_closes_active_a5(status: str) -> bool:
    normalized_status = _normalize(status)
    return (
        "current a5" in normalized_status
        and "closed" in normalized_status
        and (
            "recommended next step: remain in no-op/awaiting-preregistration state"
            in normalized_status
            or "do not reopen a5" in normalized_status
        )
    )


def _status_next_action(status: str) -> str:
    for line in status.splitlines():
        stripped = line.strip()
        normalized = stripped.lower()
        for prefix in (
            "- recommended next step:",
            "recommended next step:",
            "- next step:",
            "next step:",
        ):
            if normalized.startswith(prefix):
                return stripped.split(":", 1)[1].strip()
    return ""


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report whether OmegaSim automation should no-op."
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS_PATH),
        help="Path to AUTOMATION_STATUS.md.",
    )
    parser.add_argument(
        "--review",
        default=str(DEFAULT_REVIEW_PATH),
        help="Path to the latest external strategy review.",
    )
    parser.add_argument(
        "--a5-preregistration",
        default=str(DEFAULT_A5_PREREGISTRATION_PATH),
        help="Path to an explicit A5 preregistration that reopens the loop.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    state = read_automation_state(args.status, args.review, args.a5_preregistration)
    print(json.dumps(state, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
