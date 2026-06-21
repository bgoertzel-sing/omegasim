# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI lobe run-state sequence reproducibility regression
- Changed: added a documented-CLI same-seed duplicate-run regression across the full-output fixtures proving the ordered `baseline_lobe_run_id`/`baseline_lobe_current_run_length` sequence in `metrics.csv` is reproducible; added `_lobe_run_state_sequence` in `tests/test_run_harness.py`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "lobe_run_state_sequence_reproduces" -q` passed with 2 tests and 189 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 191 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that the `baseline_lobe_label` sequence is identical across same-seed duplicate runs for both full-output fixtures.
