# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 baseline lobe manifest provenance
- Changed: added `model.baseline_lobes.labels` and `model.baseline_lobes.transition_fields` to `manifest.yaml`, backed by simulator constants; documented the new manifest fields in `README.md`; added manifest schema coverage that verifies the declared lobe transition fields exist in `metrics.csv`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_manifest_records_baseline_lobe_metric_provenance -q` passed with 1 test; `.venv-conda/bin/python -m pytest -q` passed with 80 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add manifest provenance for role/action metric fields so role aggregate metrics are discoverable from `manifest.yaml`.
