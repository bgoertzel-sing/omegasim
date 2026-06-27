# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

This run reconciled Ben's A5 anticipatory predictive-control request against
the current repository state. The requested concise A5 preregistration and
minimal deterministic single-hive scaffold already exist:
`docs/a5_anticipatory_predictive_control_preregistration.md`,
`configs/a5_predictive_linear_smoke.yaml`, `ohdyn.compare_predictive_control`,
and `ohdyn.analyze_a5_residual_accounting`.

A5 remains scientifically closed after the seed `7..16` residual-gap result and
post-closure reopening gate. The frozen interpretation is narrow: bounded
predictors improved forecast skill under matched demand streams, but the effect
did not survive full accounting controls and budget-matched timing-broken nulls.
No new A5 preregistration rules, simulator mechanics, analyzers, configs,
dashboards, external integrations, broad seed runs, or multi-hive coupling were
added.

The later A6.2 validation remains the current post-A5 state: the fixed 96-tick
paired-seed validation passed schema/computation checks but closed
conservatively because logistic did not beat linear and both source-preserving
nulls on the same target with paired cross-seed agreement.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Do not broaden seeds, reinterpret A5/A6 as
attractor evidence, or add anticipatory-prediction mechanics unless a later
accepted preregistration explicitly supersedes the current closures.

## Latest Changes

- Updated this status file to record that the repeated A5 prompt is already
  satisfied by tracked A5 preregistration/scaffold artifacts and should not be
  duplicated.
- Rechecked the A5 preregistration, deterministic smoke config, predictive
  comparison helper, read-only residual-accounting analyzer, post-closure gate,
  and seed `7..16` residual-gap report.
- Preserved the completed A6.2 validation result and did not change simulator
  code, configs, tests, analyzers, result documents, dashboards, integrations,
  seed scope, or multi-hive mechanics.

## Verification

- `.venv-conda/bin/python -m py_compile ohdyn/compare_predictive_control.py
  ohdyn/analyze_a5_residual_accounting.py ohdyn/automation_guard.py
  ohdyn/sim.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting or automation_guard'`
  passed: `10 passed, 593 deselected`.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_reconcile_smoke_20260627_1600` passed.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed and reported
  `state=open`, `should_noop=false`, `strategic_change_level=minor`, and
  `notify_ben=false`; the open state is driven by the later A6 thread, not by
  missing A5 preregistration/scaffold work.

## Blockers

None for this reconciliation run. Scientifically, A5 should remain closed
unless Ben accepts a new preregistration that explicitly supersedes the
post-closure reopening gate.

## Recommended Next Step

Create a short A6.2 closure addendum that freezes the conservative
interpretation and explicitly blocks further single-hive A6 seed broadening or
mechanism work unless Ben accepts a new preregistered direction.
