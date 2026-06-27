# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

A5 remains scientifically closed after the seed `7..16` residual-gap result and
post-closure reopening gate. The frozen interpretation is narrow: bounded
predictors improved forecast skill under matched demand streams, but the effect
did not survive full accounting controls and budget-matched timing-broken nulls.

A6/A6.1/A6.2 are also closed conservatively. The fixed 96-tick A6.2
paired-seed validation passed schema/computation checks but logistic did not
beat linear and both source-preserving nulls on the same target with paired
cross-seed agreement. The closure addendum is
`docs/results/a6_2_closure_addendum_seed1_2.md`.

Ben accepted proceeding to A7 on 2026-06-27. The current focus is the A7
semantic-field preregistration/design gate in
`docs/a7_semantic_field_preregistration.md`: add a source-accounted
semantic/artifact activation field and test logistic inter-agent dependence
under limited prediction/attention resources, with strict nulls and accounting
controls.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Do not broaden A5/A6/A6.2 seeds, reinterpret
A5/A6 as attractor evidence, or add simulator mechanics before the A7
implementation gate freezes state variables, update equations, source
accounting, null semantics, schemas, and tests.

## Latest Changes

- Added `docs/results/a6_2_closure_addendum_seed1_2.md` to freeze the A6.2
  conservative interpretation before moving on.
- Added `docs/a7_semantic_field_preregistration.md` as the accepted A7 design
  target.
- Updated `docs/omegasim_provisional_experiment_roadmap.md`, `README.md`, and
  this status file so automation treats A7 as the next preregistered direction
  rather than reopening A6.2.
- Updated `ohdyn.automation_guard` so a Markdown `Recommended Next Step`
  section in this file overrides stale strategy-review next-action text.
- No simulator code, configs, analyzers, dashboards, integrations, seed scope,
  or multi-hive mechanics were changed.

## Verification

- Documentation-only update.
- `git diff --check` passed.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard'` passed: `8 passed, 596 deselected`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed with
  `state=open`, `should_noop=false`, and recommended next action set to the A7
  implementation gate.

## Blockers

None. Scientifically, A5 and A6.2 remain closed unless Ben accepts a later
preregistration that explicitly supersedes those closures.

## Recommended Next Step

Create the A7 implementation gate: freeze the semantic/artifact state vector,
logistic and linear action-utility equations, prediction-budget accounting,
source-preserving null semantics, schema additions, deterministic tests, and
read-only analyzer skeleton before changing simulator mechanics or running a
tiny paired smoke.
