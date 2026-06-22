# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 reordered action-order full-output fixture coverage
- Changed: added a shared `FULL_OUTPUT_FIXTURES` test tuple containing `configs/a0_smoke.yaml`, `configs/a0_default_outputs.yaml`, and `configs/a0_reordered_actions.yaml`; updated full-output manifest, summary, CLI, reproducibility, event replay, lobe, queue, and role/action parametrizations to cover non-default action order; adjusted role/action assertions to derive action order from manifests and made the different-seed lobe run-state assertion label-aware for short fixtures.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "full_output_fixtures or reordered_action or reordered_actions" -q` passed with 230 tests and 120 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 350 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a no-manifest reordered-action fixture so metrics and summary schema/order checks also cover non-default action order when `manifest.yaml` is disabled.
