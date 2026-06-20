# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 event schema manifest provenance
- Changed: added `BASELINE_EVENT_TYPES` and `EVENT_FIELDS` constants; added `model.events.types` and `model.events.fields` to `manifest.yaml`; documented the new manifest event provenance in `README.md`; added manifest schema coverage that verifies declared event fields and event type vocabulary match `events.csv`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_manifest_records_event_schema_provenance tests/test_run_harness.py::test_manifest_and_config_match_documented_a0_provenance_schema -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 83 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out /tmp/omegasim-event-schema-20260620-a0/a0_seed1` wrote all five A0 artifacts and `manifest.yaml` includes `model.events.fields` and `model.events.types`.
- Blockers: none.
- Next step: add manifest provenance for full `metrics.csv` field order so metrics consumers can validate the complete A0 schema from `manifest.yaml`.
