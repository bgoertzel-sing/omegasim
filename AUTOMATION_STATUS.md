# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 final documented-CLI same-seed helper reuse
- Changed: refactored the remaining documented CLI same-seed lobe label, lobe transition, lobe run-state, and role/action metric sequence reproducibility tests to use `_run_documented_cli_pair`, preserving artifact checks and existing sequence assertions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "lobe_label_sequence_reproduces_across_same_seed or lobe_transition_sequence_reproduces_across_same_seed or lobe_run_state_sequence_reproduces_across_same_seed or role_action_metric_sequence_reproduces_across_same_seed" -q` passed with 12 tests and 409 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: begin one executable A2 attention-allocation experiment increment while preserving the stable A0/A1 deterministic baseline.
