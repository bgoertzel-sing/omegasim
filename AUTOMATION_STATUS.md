# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response machine-readable artifacts on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added a machine-readable selected-pressure-response artifact.
- Changed: no simulator behavior changes; `ohdyn.compare_pressure` now writes top-level `pressure_response_selection.csv` beside `pressure_comparison_metrics.csv`, including the full seed set's selected top response and each proper prefix's selected response with condition means, slopes, curvature, high-minus-normal delta, stability, and instability-cause fields. README and tests document and verify the new artifact.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure'` passed with 48 selected tests; `.venv-conda/bin/python -m pytest` passed with 454 tests.
- Blockers: none.
- Next step: add the first deterministic A2 override-rule event and metric fields for attention-share capture pressure, keeping them disabled unless `attention_policy` is configured.
