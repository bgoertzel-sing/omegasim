# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 attention-share pressure-response comparison summaries on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 extended deterministic A2 pressure comparison outputs with per-class capture-pressure response deltas and curve metrics.
- Changed: no simulator or scheduling behavior changes; `ohdyn.compare_attention` now exposes per-attention-class capture-pressure final, mean-over-ticks, and peak aggregates, and `ohdyn.compare_pressure` carries their high-minus-normal deltas plus normal-to-medium slopes, medium-to-high slopes, and curvature fields into `pressure_comparison_metrics.csv`, pressure-response ranking/selection, and `summary.md`. README and pressure comparison tests cover the new artifact contract.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_attention.py ohdyn/compare_pressure.py tests/test_run_harness.py` passed; focused pressure comparison pytest selection passed with 6 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 454 tests.
- Blockers: none.
- Next step: add a compact per-class capture-pressure interpretation section to the pressure comparison summary.
