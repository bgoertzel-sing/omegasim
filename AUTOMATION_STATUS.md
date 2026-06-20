# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 metrics schema manifest provenance
- Changed: added `metrics_fieldnames(...)` as the explicit `metrics.csv` field-order source; made `metrics.csv` and `events.csv` write with declared fieldnames; added `model.metrics.fields` to `manifest.yaml`; documented the full metrics schema provenance in `README.md`; added tests that verify manifest-declared metrics fields exactly match the emitted CSV header.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_metrics_and_events_headers_match_documented_a0_schema tests/test_run_harness.py::test_manifest_and_config_match_documented_a0_provenance_schema tests/test_run_harness.py::test_manifest_records_full_metrics_schema_provenance -q` passed with 3 tests; `.venv-conda/bin/python -m pytest -q` passed with 84 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out /tmp/omegasim-metrics-schema-20260620-a0/a0_seed1` wrote all five A0 artifacts and `manifest.yaml` `model.metrics.fields` exactly matched the `metrics.csv` header.
- Blockers: none.
- Next step: add summary-level reporting for metrics schema size and artifact schema provenance so human run review can confirm emitted schemas without opening CSV files.
