"""Automation state guard for bounded OmegaSim research loops."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_STATUS_PATH = Path("AUTOMATION_STATUS.md")
DEFAULT_REVIEW_PATH = Path("../outputs/strategy-reviews/omegasim/latest-review.md")
DEFAULT_A5_PREREGISTRATION_PATH = Path(
    "docs/a5_single_hive_anticipatory_predictive_control_preregistration.md"
)
DEFAULT_ROADMAP_PATH = Path("docs/omegasim_provisional_experiment_roadmap.md")


def read_automation_state(
    status_path: str | Path = DEFAULT_STATUS_PATH,
    review_path: str | Path = DEFAULT_REVIEW_PATH,
    a5_preregistration_path: str | Path = DEFAULT_A5_PREREGISTRATION_PATH,
    roadmap_path: str | Path = DEFAULT_ROADMAP_PATH,
) -> dict[str, Any]:
    """Return the current automation state from local status/review artifacts."""

    status = _read_optional_text(Path(status_path))
    current_status = _current_status_scope(status)
    review = _read_optional_text(Path(review_path))
    roadmap = _read_scoped_roadmap_text(Path(status_path), Path(roadmap_path))
    review_header = _parse_review_header(review)
    a5_preregistration_active = Path(a5_preregistration_path).is_file()
    closed_reasons = _closed_reasons(status=current_status, review=review)
    status_opens_a7_3 = _status_opens_active_a7_3_dimensionless(current_status)
    review_opens_a7_3 = _review_recommends_active_a7_3(review_header)
    status_reopens_a5 = (
        a5_preregistration_active
        and _status_reopens_active_a5(current_status)
        and not _status_closes_active_a5(current_status)
    )
    active_a7_3 = status_opens_a7_3 or review_opens_a7_3
    closed_after_a7_2_three_hive = _status_closes_after_a7_2_three_hive(
        current_status
    )
    stale_a5_after_closed_branch = status_reopens_a5 and closed_after_a7_2_three_hive
    current_line_closed = closed_after_a7_2_three_hive and not active_a7_3
    if closed_reasons and active_a7_3:
        closed_reasons = []
    if (
        closed_reasons
        and _status_opens_active_a7_2_then_three_hive(current_status)
        and not current_line_closed
    ):
        closed_reasons = []
    if (
        a5_preregistration_active
        and not _status_closes_active_a5(current_status)
        and not current_line_closed
    ):
        closed_reasons = []
    if (
        status_reopens_a5
        and not current_line_closed
    ):
        closed_reasons = []
    roadmap_reopens_a7 = _roadmap_reopens_after_a5(roadmap) and not (
        _status_supersedes_roadmap(current_status)
    )
    if closed_reasons and roadmap_reopens_a7:
        closed_reasons = []
    state = "closed_awaiting_preregistration" if closed_reasons else "open"

    status_next_action = _status_next_action(current_status)
    if review_opens_a7_3 and not status_opens_a7_3 and (
        not status_reopens_a5 or stale_a5_after_closed_branch
    ):
        status_next_action = ""
    roadmap_next_action = _roadmap_next_action(roadmap) if roadmap_reopens_a7 else ""
    if roadmap_reopens_a7 and _is_noop_next_action(status_next_action):
        status_next_action = ""
    recommended_next_action = status_next_action or review_header.get(
        "recommended_next_action", ""
    ) or roadmap_next_action

    should_noop = bool(closed_reasons)

    return {
        "state": state,
        "should_noop": should_noop,
        "repo_write_allowed": not should_noop,
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


def _read_scoped_roadmap_text(status_path: Path, roadmap_path: Path) -> str:
    if roadmap_path == DEFAULT_ROADMAP_PATH and status_path != DEFAULT_STATUS_PATH:
        return ""
    return _read_optional_text(roadmap_path)


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


def _review_recommends_active_a7_3(review_header: dict[str, str]) -> bool:
    normalized_action = _normalize(review_header.get("recommended_next_action", ""))
    normalized_verdict = _normalize(review_header.get("verdict", ""))
    return (
        normalized_verdict == "go"
        and "a7.3" in normalized_action
        and (
            "implement" in normalized_action
            or "run" in normalized_action
            or "preregister" in normalized_action
        )
    )


def _current_status_scope(status: str) -> str:
    scoped_lines: list[str] = []
    saw_section = False
    included_section = False
    include_current = True
    for line in status.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            saw_section = True
            name = stripped.removeprefix("## ").strip().lower()
            include_current = name in {
                "current focus",
                "blockers",
                "recommended next step",
            }
            if include_current:
                included_section = True
                scoped_lines.append(line)
            continue
        if not saw_section or include_current:
            scoped_lines.append(line)

    if included_section:
        return "\n".join(scoped_lines).strip()
    return status


def _closed_reasons(*, status: str, review: str) -> list[str]:
    status_reasons = []
    normalized_status = _normalize(status)
    normalized_review = _normalize(review)

    if "next step: leave omegasim closed" in normalized_status:
        status_reasons.append("automation_status_next_step_closed")
    if "closed at the current a4 boundary" in normalized_status:
        status_reasons.append("automation_status_a4_closed")
    if (
        "state: closed_awaiting_preregistration" in normalized_status
        and "should_noop: true" in normalized_status
    ):
        status_reasons.append("automation_status_noop_guard")
    if "recommended next step: remain in no-op/awaiting-preregistration state" in normalized_status:
        status_reasons.append("automation_status_next_step_noop")
    if "do not reopen a5" in normalized_status:
        status_reasons.append("automation_status_a5_closed")
    if "stop a5 broadening after this fail-closed smoke" in normalized_status:
        status_reasons.append("automation_status_a5_broadening_stopped")
    if (
        not status_reasons
        and "the current a5 anticipatory predictive-control loop is closed"
        in normalized_status
    ):
        status_reasons.append("automation_status_a5_loop_closed")
    if (
        "recommended next step: design one preregistered resource-bounded residual diagnostic"
        in normalized_status
        and (
            "reopened a5 smoke" in normalized_status
            or "reopened a5 preregistration" in normalized_status
        )
        and "fail-closed" in normalized_status
    ):
        status_reasons.append("automation_status_a5_reopened_smoke_failed_closed")
    if _status_closes_after_a7_2_three_hive(status):
        status_reasons.append("automation_status_a7_2_three_hive_failed_closed")

    reasons = list(status_reasons)
    if not status_reasons:
        return reasons

    if "explicit no-op/awaiting-preregistration state" in normalized_review:
        reasons.append("strategy_review_noop_awaiting_preregistration")
    if "do not run new simulations or analyzers now" in normalized_review:
        reasons.append("strategy_review_stop_new_work")

    return reasons


def _status_closes_after_a7_2_three_hive(status: str) -> bool:
    normalized_status = _normalize(status)
    return (
        "a7.2" in normalized_status
        and "three-hive ring" in normalized_status
        and (
            "fail-closed" in normalized_status
            or "failed-closed" in normalized_status
            or "failed closed" in normalized_status
        )
        and (
            "pause further three-hive ring expansion" in normalized_status
            or "awaiting-preregistration" in normalized_status
            or "fresh preregistered decision note" in normalized_status
        )
        and (
            "one-hive dimensionless delayed-dynamics sweep" in normalized_status
            or "ben wants another scientific direction" in normalized_status
            or "ben should be notified" in normalized_status
        )
    )


def _status_closes_active_a5(status: str) -> bool:
    normalized_status = _normalize(status)
    return (
        (
            "current a5" in normalized_status
            or "current concise a5 gate" in normalized_status
            or "the current a5 anticipatory predictive-control loop" in normalized_status
            or "a5-family automation" in normalized_status
        )
        and "closed" in normalized_status
        and (
            "recommended next step: remain in no-op/awaiting-preregistration state"
            in normalized_status
            or "recommended next step: have ben decide whether a5 should stay closed"
            in normalized_status
            or "recommended next step: design one preregistered resource-bounded residual diagnostic"
            in normalized_status
            or "do not reopen a5" in normalized_status
            or "stop a5 broadening after this fail-closed smoke"
            in normalized_status
            or "not an active authorization for more a5-family automation"
            in normalized_status
        )
    )


def _status_reopens_active_a5(status: str) -> bool:
    normalized_status = _normalize(status)
    return (
        "current concise a5 gate" in normalized_status
        and "explicit single-hive a5 reopening" in normalized_status
        and "active preregistration summary" in normalized_status
    )


def _status_opens_active_a7_2_then_three_hive(status: str) -> bool:
    normalized_status = _normalize(status)
    return (
        "source-of-truth status" in normalized_status
        and "a7.2 delayed artifact-mediated endogenous prediction" in normalized_status
        and "active next omegasim gate" in normalized_status
        and "supersedes the previous a5-family decision-awaiting posture"
        in normalized_status
        and "after a7.2 closes" in normalized_status
        and "three-hive ring" in normalized_status
    )


def _status_opens_active_a7_3_dimensionless(status: str) -> bool:
    normalized_status = _normalize(status)
    return (
        "a7.3 one-hive dimensionless delayed dynamics" in normalized_status
        and "active next omegasim gate" in normalized_status
        and "supersedes the previous awaiting-preregistration posture"
        in normalized_status
        and "does not reopen a7.2" in normalized_status
    )


def _status_next_action(status: str) -> str:
    lines = status.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        normalized = stripped.lower()
        for prefix in (
            "- recommended next step:",
            "recommended next step:",
            "- next step:",
            "next step:",
        ):
            if normalized.startswith(prefix):
                action_parts = [stripped.split(":", 1)[1].strip()]
                for continuation in lines[index + 1 :]:
                    continuation_stripped = continuation.strip()
                    if not continuation_stripped:
                        break
                    if continuation_stripped.startswith("## "):
                        break
                    if continuation_stripped.startswith("- "):
                        break
                    if not continuation.startswith((" ", "\t")):
                        break
                    action_parts.append(continuation_stripped)
                return " ".join(action_parts)
    return _status_section_text(status, "Recommended Next Step")


def _roadmap_next_action(roadmap: str) -> str:
    return _status_section_text(roadmap, "Immediate Next Step")


def _roadmap_reopens_after_a5(roadmap: str) -> bool:
    normalized_roadmap = _normalize(roadmap)
    return (
        "accepted by ben" in normalized_roadmap
        and "ben accepted proceeding to a7" in normalized_roadmap
        and "replaces the closed a5 no-op posture" in normalized_roadmap
    )


def _status_supersedes_roadmap(status: str) -> bool:
    normalized_status = _normalize(status)
    return (
        "source of truth" in normalized_status
        or "source-of-truth" in normalized_status
        or (
            "a5.1a" in normalized_status
            and "closed" in normalized_status
            and "older a7 roadmap wording" in normalized_status
        )
        or (
            "current concise a5 gate" in normalized_status
            and "reopened a5 smoke" in normalized_status
            and "fail-closed" in normalized_status
        )
    )


def _is_noop_next_action(next_action: str) -> bool:
    normalized_next_action = _normalize(next_action)
    return (
        "remain in no-op/awaiting-preregistration state" in normalized_next_action
        or "explicit no-op/awaiting-preregistration state" in normalized_next_action
    )


def _status_section_text(status: str, title: str) -> str:
    in_section = False
    lines: list[str] = []
    target = f"## {title}".lower()

    for line in status.splitlines():
        stripped = line.strip()
        normalized = stripped.lower()
        if normalized == target:
            in_section = True
            continue
        if in_section and normalized.startswith("## "):
            break
        if in_section and stripped:
            lines.append(stripped.removeprefix("- ").strip())

    return " ".join(lines)


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
    parser.add_argument(
        "--roadmap",
        default=str(DEFAULT_ROADMAP_PATH),
        help="Path to the current provisional experiment roadmap.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    state = read_automation_state(
        args.status,
        args.review,
        args.a5_preregistration,
        args.roadmap,
    )
    print(json.dumps(state, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
