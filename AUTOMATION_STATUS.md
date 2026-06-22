# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 full manifest/config provenance config-action derivation
- Changed: updated the full manifest/config provenance regression to derive baseline actions from normalized `config.yaml` through a shared helper instead of a hard-coded baseline list, preserving exact manifest, config, metrics, and role/action schema checks.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_and_config_match_documented_a0_provenance_schema" -q` passed with 1 test and 271 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 272 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a regression that full-output fixture manifest `actions`, normalized `config.yaml` model actions, metrics schema fields, and role/action schema fields all stay aligned when action order comes from the YAML config.
