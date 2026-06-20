# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 summary output review
- Changed: added a `Run artifacts and outputs` section to `summary.md` listing the exact written artifacts and enabled/disabled optional output flags; documented the section in `README.md`; added tests for all-output and no-manifest summary runs.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_summary_records_written_artifacts_and_output_flags tests/test_run_harness.py::test_summary_records_disabled_manifest_output_flag tests/test_run_harness.py::test_summary_records_artifact_schema_provenance -q` passed with 3 tests; `.venv-conda/bin/python -m pytest -q` passed with 87 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out /tmp/omegasim-summary-outputs-20260620-a0/a0_seed1` wrote all five A0 artifacts and `summary.md` reported the output flags as enabled.
- Blockers: none.
- Next step: add a regression assertion that `summary.md` written-artifact listings match `manifest.yaml` artifacts whenever both summary and manifest outputs are enabled.
