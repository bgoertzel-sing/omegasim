# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI lobe-transition sequence reproducibility regression
- Changed: added a documented-CLI same-seed duplicate-run regression across the full-output fixtures proving the ordered non-`start`/`stable` `baseline_lobe_transition` sequence in `metrics.csv` is reproducible; added `_lobe_transition_sequence` in `tests/test_run_harness.py`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "lobe_transition_sequence_reproduces" -q` passed with 2 tests and 187 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 189 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that the lobe run-state sequence (`baseline_lobe_run_id`, `baseline_lobe_current_run_length`) is identical across same-seed duplicate runs for both full-output fixtures.
