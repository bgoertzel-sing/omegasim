# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

A6/A6.1 remain conservatively closed as evidence, and A6.2 is now the active
read-only residual-recurrence analyzer gate from the accepted provisional
roadmap. This run implemented the smallest A6.2 analyzer path over the existing
A6.1 source-preserving null comparison artifacts.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Do not broaden seeds, add new A6 mechanisms, or
promote attractor/lobe-like claims from the seed `1..2` smoke artifacts.

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: minor`
- `notify_ben: false`
- Accepted: publish the actual A6 analyzer gate status before new simulations
  or mechanisms.
- Applied to the current roadmap by adding the A6.2 read-only gate report.
- Rejected/deferred: no scientifically sensible GPT-5.5-Pro recommendation was
  rejected.

## Latest Changes

- Added `ohdyn/analyze_a6_2_residual_recurrence.py`.
- Added focused tests for A6.2 missing required source fields and
  smoke-horizon `insufficient_horizon` handling.
- Ran the analyzer read-only against `runs/a6_1_pilot_null_compare`.
- Added `docs/results/a6_2_residual_recurrence_gate_seed1_2.md`.
- Documented the A6.2 analyzer command in `README.md`.

## Verification

- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a6_2_residual_recurrence_gate or automation_guard'` passed: `9 passed,
  593 deselected`.
- `.venv-conda/bin/python -m py_compile
  ohdyn/analyze_a6_2_residual_recurrence.py tests/test_run_harness.py` passed.
- `git diff --check` passed.
- `.venv-conda/bin/python -m ohdyn.analyze_a6_2_residual_recurrence
  --compare-dir runs/a6_1_pilot_null_compare
  --out runs/a6_2_residual_recurrence_analysis_seed1_2` passed.

Analyzer output summary:

- run artifacts read: 12
- conditions observed: 6
- seeds observed: 2
- required field status: `complete=12`
- recurrence rows: 156, all `insufficient_horizon`
- paired delta rows: 130, all `insufficient_horizon`
- simulations rerun: no

## Blockers

None for the bounded A6.2 analyzer gate. Scientifically, the existing 16-tick
smoke artifacts are too short for residual-recurrence interpretation, and the
analyzer correctly fails closed as `insufficient_horizon`.

## Recommended Next Step

Preregister a narrow longer-horizon A6.2 validation design using the same
source-preserving null controls and no new mechanisms, or explicitly close the
single-hive residual-recurrence route; do not run longer horizons before that
design gate is written.
