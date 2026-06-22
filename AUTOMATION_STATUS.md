# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-documented config-only reordered-action same-seed normalized-config provenance regression
- Changed: added a compact README-linked CLI regression for `configs/a0_config_only_reordered_actions.yaml` that verifies the documented seed-1 smoke command remains present, only `config.yaml` is emitted, disabled manifest/metrics/events/summary artifacts stay absent, normalized config preserves YAML-defined action order, and two same-seed runs are byte-identical for enabled artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_config_only_reordered_actions" -q` passed with 1 test and 390 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 391 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact README-linked CLI regression for the config-only default-action fixture that verifies the documented seed-1 command writes only normalized config provenance with baseline action order.
