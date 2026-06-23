# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 attention-share pressure-response interpretation summaries on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added deterministic per-class capture-pressure interpretation to A2 pressure comparison summaries.
- Changed: no simulator, scheduling, or CSV schema behavior changes; `ohdyn.compare_pressure` now adds a `Per-class capture-pressure interpretation` summary section that reports the strongest overall attention-class capture-pressure response and the strongest class-specific response for each fixed policy using existing condition means, slopes, curvature, and high-minus-normal deltas. README and pressure-summary tests cover the new summary contract.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_summary'` passed with 7 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 455 tests.
- Blockers: none.
- Next step: add a compact comparison of per-class capture-pressure interpretations across normal, medium, and high pressure seed prefixes.
