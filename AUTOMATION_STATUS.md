# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 documented-CLI different-seed lobe helper reuse
- Changed: refactored the documented CLI different-seed lobe label, transition, run-state, and dwell-run summary tests to use the existing `_run_documented_cli_pair` helper while preserving their seed-variation and metrics/summary assertions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "lobe_label_sequence_changes_across_different_seeds or lobe_transition_sequence_changes_across_different_seeds or lobe_run_state_sequence_changes_across_different_seeds or lobe_dwell_run_summary_changes_across_different_seeds" -q` passed with 12 tests and 409 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: review documented-CLI different-seed event-replay tests for one narrow `_run_documented_cli_pair` helper reuse without changing replay or seed-variation assertions.
