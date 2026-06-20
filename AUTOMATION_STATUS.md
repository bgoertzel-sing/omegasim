# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 queue dynamics manifest provenance
- Changed: added `QUEUE_PRESSURE_METRIC_FIELDS` and `QUEUED_TASK_AGE_METRIC_FIELDS` constants; added `model.queue_dynamics_metrics.pressure_fields` and `model.queue_dynamics_metrics.queued_task_age_fields` to `manifest.yaml`; documented the new manifest fields in `README.md`; added manifest schema coverage that verifies the declared queue dynamics fields exist in `metrics.csv`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_manifest_records_queue_dynamics_metric_provenance tests/test_run_harness.py::test_manifest_and_config_match_documented_a0_provenance_schema -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 82 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out /tmp/omegasim-queue-dynamics-20260620-a0/a0_seed1` wrote all five A0 artifacts and the expanded manifest.
- Blockers: none.
- Next step: add manifest provenance for event schema and event type vocabulary so `events.csv` consumers can discover supported baseline event records from `manifest.yaml`.
