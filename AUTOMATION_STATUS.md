# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 summary schema provenance
- Changed: added an `Artifact schema provenance` section to `summary.md` reporting metrics/event field counts, event type count, lobe/queue/role-action schema counts, the CSV schema helper sources, and explicit manifest/schema mirroring; documented the summary provenance section in `README.md`; added tests that compare the summary counts to emitted CSV headers and manifest schema fields.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_summary_records_artifact_schema_provenance tests/test_run_harness.py::test_manifest_records_full_metrics_schema_provenance tests/test_run_harness.py::test_manifest_records_event_schema_provenance tests/test_run_harness.py::test_documented_cli_smoke_writes_core_a0_summary_sections -q` passed with 4 tests; `.venv-conda/bin/python -m pytest -q` passed with 85 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out /tmp/omegasim-summary-schema-20260620-a0/a0_seed1` wrote all five A0 artifacts and `summary.md` reported 49 metrics fields, 9 event fields, and 20 role/action fields.
- Blockers: none.
- Next step: add a compact written-artifact/output-flag section to `summary.md` so human run review can confirm enabled outputs without opening `manifest.yaml`.
