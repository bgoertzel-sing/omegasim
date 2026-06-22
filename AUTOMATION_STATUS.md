# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 reordered action-order fixture documentation
- Changed: documented `configs/a0_reordered_actions.yaml` in `README.md` with its smoke command and the schema-alignment invariant it protects: normalized `config.yaml`, manifest `actions`, manifest metrics schema, manifest role/action schema, and emitted `metrics.csv` headers must preserve the YAML-defined action order.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "reordered_action or reordered_actions" -q` passed with 2 tests and 272 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 274 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ruff check README.md` reported no Python files and all checks passed.
- Blockers: none.
- Next step: include `configs/a0_reordered_actions.yaml` in the full-output fixture parametrizations so documented CLI summary/provenance regressions also cover non-default action order.
