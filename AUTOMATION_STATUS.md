# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Ben explicitly requested reopening the next scientific stage as A5
anticipatory predictive-control dynamics, overriding the earlier A5/A6/A7
closed/no-op posture for this bounded run.

The active A5 target is single-hive only: deterministic predictive/adaptive
controllers allocate attention or service priority from forecasts of future
task pressure while keeping task-arrival totals, service capacity, action
opportunity, and work budget matched. Prediction budget is a manipulated scarce
resource axis, not a free analytic overlay.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Treat any strange-attractor/lobe-like language
as secondary and fail-closed unless residual structure survives the
preregistered accounting controls and timing-broken nulls.

## Latest Changes

- Kept the existing A5 preregistration as the active design document and
  tightened it to name the current scaffold conditions explicitly:
  `reactive`, `linear`, `nonlinear`, `nonlinear_high_budget`, `oracle`,
  `shuffled`, `nonlinear_shuffled`, and
  `nonlinear_high_budget_shuffled`.
- Added an explicit high-budget nonlinear A5 comparison condition and a
  budget-matched high-budget timing-broken null to
  `ohdyn.compare_predictive_control`.
- Added simulator support for `nonlinear_high_budget` as a deterministic
  longer-memory nonlinear forecast, separate from the existing medium-budget
  nonlinear extrapolator.
- Updated the A5 residual accounting analyzer so required conditions,
  intermediate-condition promotion checks, timing-broken null mappings, and
  oracle contrasts include the high-budget nonlinear pair.
- Updated A5 tests, README text, the residual/accounting diagnostic design, and
  the confirmatory addendum to freeze the eight-condition pilot scaffold and
  its concrete budget-matched null requirements.

## Verification

- `.venv-conda/bin/python -m py_compile ohdyn/config.py ohdyn/sim.py
  ohdyn/compare_predictive_control.py ohdyn/analyze_a5_residual_accounting.py`
  passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting'` passed:
  `3 passed, 608 deselected`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed:
  `611 passed in 295.43s`.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out <temp>/smoke`
  passed.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6
  --out <temp>/compare` passed and generated 16 runs across 8 matched
  conditions.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting
  --compare-dir <temp>/compare --out <temp>/analysis` passed. The tiny
  paired-seed pilot still failed closed: no intermediate-budget condition
  satisfied all preregistered residual-structure and guardrail criteria under
  full accounting.

## Blockers

None for the bounded A5 scaffold. Scientifically, the current smoke/pilot
output remains analyzer-development evidence only and does not support an
attractor-like claim.

## Recommended Next Step

Run the preregistered eight-condition A5 confirmatory paired-seed set and
residual analyzer with no further mechanics changes.
