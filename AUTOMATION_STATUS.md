# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-documented no-manifest reordered-action same-seed artifact reproducibility regression
- Changed: added a compact README-linked CLI regression for `configs/a0_no_manifest_reordered_actions.yaml` that verifies the documented seed-1 smoke command remains present, the enabled artifact set excludes disabled `manifest.yaml` provenance, two same-seed runs emit the same enabled artifact set, and `config.yaml`, `metrics.csv`, `events.csv`, and `summary.md` are byte-identical.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_no_manifest_reordered_actions" -q` passed with 2 tests and 387 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 389 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact A0/A1 README-linked smoke regression for the manifest-only reordered-action fixture that verifies schema/order provenance remains available when metrics, events, and summary outputs are disabled.
