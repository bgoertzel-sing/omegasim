# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 summary/manifest schema provenance count parity regression
- Changed: added `test_summary_schema_provenance_counts_match_manifest_across_full_output_fixtures` in `tests/test_run_harness.py` to verify `summary.md` artifact schema provenance counts match the corresponding `manifest.yaml` schema field counts for both full-output fixtures. Simulator behavior and output schemas were unchanged.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "summary_schema_provenance_counts_match_manifest or summary_records_artifact_schema_provenance" -q` passed with 3 tests and 124 deselected; `.venv-conda/bin/python -m pytest -q` passed with 127 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that full-output documented runs keep `summary.md` artifact schema provenance counts aligned with `manifest.yaml`.
