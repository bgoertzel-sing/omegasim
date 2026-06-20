# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 role/action manifest provenance
- Changed: added `model.role_action_metrics.roles`, `model.role_action_metrics.actions`, and `model.role_action_metrics.fields` to `manifest.yaml`; introduced a shared `role_action_metric_fields()` helper; documented the new manifest field in `README.md`; added manifest schema coverage that verifies the declared role/action fields exist in `metrics.csv`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_manifest_records_role_action_metric_provenance -q` passed with 1 test; `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_manifest_and_config_match_documented_a0_provenance_schema -q` passed with 1 test; `.venv-conda/bin/python -m pytest -q` passed with 81 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out /tmp/omegasim-role-actions-20260620-a0/a0_seed1` wrote all five A0 artifacts and the expanded manifest.
- Blockers: none.
- Next step: add manifest provenance for queue pressure and queued-task-age metric fields so backlog dynamics are discoverable from `manifest.yaml`.
