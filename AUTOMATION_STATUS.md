# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 config-only reordered action-order fixture coverage
- Changed: added `configs/a0_config_only_reordered_actions.yaml`; registered `CONFIG_ONLY_REORDERED_ACTIONS` in output fixture artifact expectations; added loader coverage and an API run assertion that config-only reordered runs write only `config.yaml` while preserving YAML action order in normalized config; documented the new fixture in `README.md`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "config_only and reordered_actions" -q` passed with 2 tests and 361 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "config_only or reordered_actions or output_flag" -q` passed with 28 tests and 335 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 363 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add documented CLI byte-stability and disabled-artifact sentinel coverage for the config-only reordered-action fixture.
