# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-documented default-output omitted-flags full-schema provenance regression
- Changed: documented the `configs/a0_default_outputs.yaml` seed-1 CLI smoke command in README and added a compact README-linked CLI regression that verifies omitted output flags normalize to all artifacts enabled, baseline action order is preserved across manifest/metrics/role-action schemas, summary output-flag and schema provenance match the manifest, and two same-seed runs are byte-identical for all emitted artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_default_outputs" -q` passed with 1 test and 394 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 395 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact README-linked CLI regression for `configs/a0_smoke.yaml` that verifies the first-milestone command emits the full A0 artifact set and preserves manifest/summary schema provenance for the 100-tick baseline.
