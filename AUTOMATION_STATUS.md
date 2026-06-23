# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response reproducibility hardening on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added the downstream-friendly smoke assertion that `pressure_response_selection.csv` source-metric condition fields stay byte-reproducible across two documented pressure CLI runs.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, comparison code, or artifact layout changes; `tests/test_run_harness.py` now runs `python -m ohdyn.compare_pressure --seeds 1 2 3` twice through the documented CLI helper, compares `pressure_response_selection.csv` bytes, and explicitly asserts the selected `source_field` plus normal/medium/high source-metric means for the full selection row.
- Smoke run: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_response_selection or source_metric_selection_fields or documented_pressure_cli_reproduces_top_level_artifacts'` passed with 3 tests.
- Verified: `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 463 tests.
- Blockers: none.
- Next step: add a compact A2 phase-space dwell/turning-point summary to the attention comparison outputs so pressure-response interpretation includes trajectory structure, not only final-condition deltas.
