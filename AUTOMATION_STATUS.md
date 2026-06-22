# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-documented manifest-only default-action same-seed manifest provenance regression
- Changed: added a compact README-linked CLI regression for `configs/a0_manifest_only.yaml` that verifies the documented seed-1 command remains present, only `config.yaml` and `manifest.yaml` are emitted, disabled metrics/events/summary artifacts stay absent, normalized config and manifest preserve baseline action order, manifest schema provenance remains populated without CSV/summary outputs, and two same-seed runs are byte-identical for enabled artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_manifest_only_same_seed" -q` passed with 1 test and 392 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 393 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact README-linked CLI regression for the no-manifest default-action fixture that verifies the documented seed-1 command writes normalized config, metrics, events, and summary without manifest provenance while preserving baseline action order.
