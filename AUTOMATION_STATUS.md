# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-documented no-manifest default-action same-seed emitted-schema provenance regression
- Changed: added a compact README-linked CLI regression for `configs/a0_no_manifest.yaml` that verifies the documented seed-1 command remains present, only normalized config/metrics/events/summary are emitted, manifest provenance stays absent, baseline action order is preserved across metrics and role/action schemas, summary schema provenance remains populated from emitted artifacts, and two same-seed runs are byte-identical for enabled artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_no_manifest_same_seed" -q` passed with 1 test and 393 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 394 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact README-linked CLI regression for the default-output fixture that verifies omitted output flags normalize to all artifacts enabled while preserving baseline action order and schema provenance.
