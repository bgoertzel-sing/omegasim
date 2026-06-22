# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 config-only reordered-action CLI coverage
- Changed: added documented CLI coverage proving `configs/a0_config_only_reordered_actions.yaml` writes only byte-stable `config.yaml` across same-seed runs while preserving YAML action order; added CLI coverage proving stale disabled `manifest.yaml`, `metrics.csv`, `events.csv`, and `summary.md` sentinels are preserved for that fixture; generalized the config-only normalized-config assertion helper with defaults for reordered action fixtures.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "config_only and reordered_actions" -q` passed with 4 tests and 361 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 365 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add API byte-stability and rerun collision coverage for the config-only reordered-action fixture.
