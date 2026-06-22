# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 config-only reordered-action CLI rerun collision coverage
- Changed: added documented CLI rerun coverage proving `configs/a0_config_only_reordered_actions.yaml` refuses to overwrite the existing enabled `config.yaml` artifact without disabled sentinels, reports only `config.yaml` in the collision message, avoids tracebacks, preserves the first run byte-for-byte, and keeps normalized reordered-action provenance intact.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "config_only_reordered_actions_rerun_refuses_to_overwrite_existing_config" -q` passed with 2 tests and 368 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 370 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add documented CLI rerun collision coverage for the manifest-only reordered-action fixture, matching the existing enabled-artifact collision behavior while preserving disabled metrics/events/summary omission.
