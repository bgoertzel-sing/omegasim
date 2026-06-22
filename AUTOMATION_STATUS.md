# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 manifest-only reordered action-order fixture coverage
- Changed: added `configs/a0_manifest_only_reordered_actions.yaml`; added `MANIFEST_ONLY_REORDERED_ACTIONS` and `MANIFEST_ONLY_FIXTURES` test coverage; extended manifest-only schema-provenance checks across default and reordered manifest-only fixtures; added an explicit assertion that manifest-only reordered runs preserve YAML action order in `manifest.yaml`, manifest metrics schema, and role/action schema while metrics/events/summary are disabled; documented the new fixture in `README.md`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_only and reordered_actions" -q` passed with 2 tests and 358 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_only or reordered_actions or output_flag" -q` passed with 29 tests and 331 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 360 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a config-only reordered-action fixture so normalized `config.yaml` order preservation is covered when all optional artifacts are disabled.
