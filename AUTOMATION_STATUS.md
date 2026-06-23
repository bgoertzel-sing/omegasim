# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 attention-share capture-pressure comparison summaries on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added deterministic A2 capture-pressure trajectories and aggregates to the attention comparison output.
- Changed: no simulator or scheduling behavior changes; `ohdyn.compare_attention` now writes final, mean-over-ticks, peak, max-trajectory, first-difference, and per-class capture-pressure trajectory fields to `comparison_metrics.csv`, and `summary.md` reports capture-pressure final/mean/peak means, step-delta aggregates, and variant deltas versus baseline. README and the aggregate comparison test cover the new output.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_attention.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_a2_attention_comparison_runner_writes_aggregate_summary` passed; `.venv-conda/bin/python -m pytest` passed with 454 tests.
- Blockers: none.
- Next step: extend the pressure comparison helper to include capture-pressure pressure-response deltas and curve metrics.
