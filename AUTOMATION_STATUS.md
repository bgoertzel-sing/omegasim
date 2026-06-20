# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI summary-section regression
- Changed: added a CLI smoke regression for the documented `python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out ...` command, asserting `summary.md` includes the core A0/A1 sections for event totals, lobe totals, lobe transitions, dwell runs, and role/action totals, with representative rows matching generated `metrics.csv` and `events.csv`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_smoke_writes_core_a0_summary_sections -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 39 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a documented CLI reproducibility regression that two runs with the same seed produce byte-identical A0/A1 artifacts.
