# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 reordered action-order schema alignment regression
- Changed: added `configs/a0_reordered_actions.yaml` as a full-output fixture with the same baseline actions in YAML-defined non-default order, plus load and run regressions proving normalized `config.yaml`, manifest `actions`, manifest metrics schema, manifest role/action schema, and emitted `metrics.csv` headers stay aligned to that YAML order.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "reordered_action or reordered_actions" -q` passed with 2 tests and 272 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 274 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: document the reordered action-order fixture in `README.md` with its smoke command and the schema-alignment invariant it protects.
