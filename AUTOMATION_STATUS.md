# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-documented first-milestone event replay regression
- Changed: added a compact README-linked CLI regression for `configs/a0_smoke.yaml` that runs the first-milestone command and reconstructs top-level queue/task metrics, queue pressure, queued-task age, role/action metric sequences, lobe labels/transitions/run state, and the integrated summary aggregate bundle from `events.csv`; it compares those replayed values against `metrics.csv` and `summary.md` while preserving manifest/config artifact provenance.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_a0_smoke_event_replay" -q` passed with 1 test and 398 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 399 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor the repeated event-replay/summary assertion bundle into one shared helper so future A1 regressions can cover new fixtures without growing `tests/test_run_harness.py` ad hoc.
