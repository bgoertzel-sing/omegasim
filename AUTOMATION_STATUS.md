# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 output fixture artifact expectation consolidation
- Changed: added shared expected artifact lists plus `_expected_artifacts()` in `tests/test_run_harness.py`, then replaced repeated config-only, manifest-only, no-manifest, default-output, and smoke expected artifact literals in output-flag tests/helpers. Simulator behavior and output schemas were unchanged.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "artifact_indexes_match_directory_contents or omitted_outputs or manifest_only or no_manifest or config_only or required_a0_artifacts" -q` passed with 46 tests and 73 deselected; `.venv-conda/bin/python -m pytest -q` passed with 119 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact regression that the lobe transition field list in `manifest.yaml` exactly matches the lobe transition columns emitted in `metrics.csv` for every output fixture that writes both artifacts.
