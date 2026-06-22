# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-documented first-milestone smoke full-schema provenance regression
- Changed: added a compact README-linked CLI regression for `configs/a0_smoke.yaml` that verifies the first-milestone command emits the full A0 artifact set, runs the 100-tick/15-agent baseline, records 1500 per-agent events, and preserves manifest/metrics/events/summary schema provenance and output flags.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_a0_smoke" -q` passed with 1 test and 395 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 396 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact README-linked same-seed reproducibility regression for `configs/a0_smoke.yaml` that byte-compares the full first-milestone artifact set for the 100-tick baseline.
