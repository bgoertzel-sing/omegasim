# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-documented manifest-only reordered-action same-seed manifest provenance regression
- Changed: added a compact README-linked CLI regression for `configs/a0_manifest_only_reordered_actions.yaml` that verifies the documented seed-1 smoke command remains present, only `config.yaml` and `manifest.yaml` are emitted, disabled metrics/events/summary artifacts stay absent, two same-seed runs are byte-identical for enabled artifacts, and manifest schema/order provenance remains complete for YAML-defined action order.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_manifest_only_reordered_actions" -q` passed with 1 test and 389 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 390 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact A0/A1 README-linked smoke regression for the config-only reordered-action fixture that verifies the documented seed-1 command writes only normalized config provenance while preserving YAML action order.
