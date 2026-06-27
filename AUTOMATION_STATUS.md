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

- Added a strict opt-in `semantic_field` config schema for A7 that imports the
  frozen A7 condition names from `ohdyn/a7_semantic_field_contract.py`,
  normalizes through `OmegaConfig.to_dict()`, permits the existing A6 action
  vocabulary for future semantic-field mechanics, and rejects unsupported
  fields, invalid probabilities, mixed A5/A6/A7 configs, and multi-hive A7
  configs.
- Added six A7 smoke fixture stubs under `configs/`, one for each frozen
  condition/null: `a7_logistic_semantic_coupling`,
  `semantic_off_baseline`, `amplitude_matched_linear_semantic_coupling`,
  `source_preserving_semantic_label_shuffle`, `semantic_field_phase_shuffle`,
  and `prediction_budget_timing_broken_matched_count_null`.
- Added focused tests that load the A7 fixture bundle, assert exact condition
  order against `A7_CONDITIONS`, verify normalized config output, and check the
  new fail-fast config validation paths.
- Added `ohdyn/a7_semantic_field_contract.py` to freeze the A7 semantic field
  values, prediction fields, source ledger components, control fields,
  preregistered conditions/nulls, utility/update-equation text, schema fields,
  and helper functions before simulator mechanics.
- Added `docs/a7_implementation_gate.md` to record the implementation contract:
  state vector, update equations, utility equations, source reconstruction
  ledger, null semantics, controls, and fail-closed analyzer requirements.
- Added read-only `ohdyn/analyze_a7_semantic_field.py`, which inspects existing
  comparison artifacts, writes deterministic completeness/manifest/summary
  outputs, and fails closed when A7 runs, null conditions, or required schema
  fields are absent.
- Added focused tests for the frozen A7 contract and analyzer fail-closed path.
- Added `ohdyn.compare_a7_semantic_field`, a deterministic A7 placeholder
  comparison scaffold that enumerates the six frozen fixture stubs and paired
  seeds, writes normalized generated configs plus config/manifest-only run
  placeholders, and deliberately does not run simulator mechanics or emit
  metrics/events.
- Added focused tests that verify the A7 placeholder scaffold writes only
  config/manifest/summary placeholders and that the read-only A7 analyzer still
  fails closed on those placeholders.
- Added `docs/results/a6_2_closure_addendum_seed1_2.md` to freeze the A6.2
  conservative interpretation before moving on.
- Added `docs/a7_semantic_field_preregistration.md` as the accepted A7 design
  target.
- Updated `docs/omegasim_provisional_experiment_roadmap.md`, `README.md`, and
  this status file so automation treats A7 as the next preregistered direction
  rather than reopening A6.2.
- Updated `ohdyn.automation_guard` so a Markdown `Recommended Next Step`
  section in this file overrides stale strategy-review next-action text.
- The earlier A7 contract/analyzer gate did not change simulator mechanics,
  dashboards, integrations, seed scope, or multi-hive mechanics.
- This run did not change simulator mechanics, dashboards, integrations, seed
  scope, or multi-hive mechanics. It added A7 placeholder comparison artifacts
  only.

## Verification

- Guard before this run: `.venv-conda/bin/python -m ohdyn.automation_guard`
  passed with `state=open`, `should_noop=false`, `strategic_change_level=none`,
  and `notify_ben=false`. Its recommended next action was the A7 config schema
  and smoke fixture stub gate completed here.
- External strategy review at
  `../outputs/strategy-reviews/omegasim/latest-review.md` recommended the
  earlier A7 implementation contract/gate. That gate was already complete, so
  this run followed the newer `AUTOMATION_STATUS.md` next step. No
  GPT-5.5-Pro recommendation was deferred or rejected.
- `.venv-conda/bin/python -m py_compile
  ohdyn/config.py ohdyn/a7_semantic_field_contract.py
  ohdyn/analyze_a7_semantic_field.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a7 or automation_guard'` passed: `13 passed, 596 deselected`.
- `git diff --check` passed.
- Guard before changes: `.venv-conda/bin/python -m ohdyn.automation_guard`
  passed with `state=open`, `should_noop=false`, `strategic_change_level=none`,
  and `notify_ben=false`.
- External strategy review at
  `../outputs/strategy-reviews/omegasim/latest-review.md` recommended the A7
  implementation contract/gate first; no GPT-5.5-Pro recommendation was
  deferred or rejected.
- `git diff --check` passed.
- `.venv-conda/bin/python -m py_compile
  ohdyn/a7_semantic_field_contract.py ohdyn/analyze_a7_semantic_field.py`
  passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a7 or automation_guard'` passed: `10 passed, 596 deselected`.
- Guard before this run: `.venv-conda/bin/python -m ohdyn.automation_guard`
  passed with `state=open`, `should_noop=false`, `strategic_change_level=none`,
  and `notify_ben=false`. Its recommended next action was the A7 placeholder
  comparison scaffold completed here.
- External strategy review at
  `../outputs/strategy-reviews/omegasim/latest-review.md` recommended the
  earlier A7 implementation contract/gate; that gate was already complete, so
  this run followed the newer `AUTOMATION_STATUS.md` next step. No
  GPT-5.5-Pro recommendation was deferred or rejected.
- `.venv-conda/bin/python -m py_compile
  ohdyn/compare_a7_semantic_field.py ohdyn/analyze_a7_semantic_field.py
  ohdyn/a7_semantic_field_contract.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a7 or automation_guard'` passed: `15 passed, 596 deselected`.
- `.venv-conda/bin/python -m ohdyn.compare_a7_semantic_field --seeds 1 2
  --out <temp>/compare` passed and wrote only generated configs plus
  config/manifest/summary placeholders.

## Blockers

None. Scientifically, A5 and A6.2 remain closed unless Ben accepts a later
preregistration that explicitly supersedes those closures.

## Recommended Next Step

Add the minimal opt-in A7 semantic-field simulator mechanics needed to emit the
frozen A7 metric/event schema for the six preregistered conditions, then run
only the tiny paired smoke grid as a schema/manipulation check with no
scientific promotion claim.
