# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

The current automation run is scoped to Ben's explicit A5 anticipatory
predictive-control request. The existing preregistration in
`docs/a5_anticipatory_predictive_control_preregistration.md` is the active gate
for this bounded pass. It already defines the deterministic single-hive setup,
reactive/linear/nonlinear/high-budget/oracle/timing-broken null conditions,
resource-bounded prediction hypothesis, matched accounting controls, residual
endpoints, and fail-closed decision rules requested for A5.

The historical A5 seed `7..16` closure records remain the current scientific
interpretation of the checked-in scaffold: prediction manipulations improve
forecast skill, but residual structure has not survived full accounting and
paired null checks. This run therefore only revalidates the preregistered
single-hive smoke/pilot path; it does not authorize broader seed sweeps, new
mechanics, downstream three-hive coupling, or lobe/attractor claims.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling.

## Latest Changes

- Confirmed that the A5 preregistration already exists and explicitly covers
  Ben's requested resource-bounded prediction hypothesis and fail-closed
  single-hive accounting controls.
- Re-ran the bounded paired A5 pilot comparison for seeds `5` and `6` in
  `/tmp/omegasim_a5_predictive_control_compare_20260627_current_request_2`.
  It generated 16 deterministic single-hive runs across the preregistered
  reactive, predictor, oracle, and timing-broken null conditions.
- Re-ran the read-only residual accounting analyzer in
  `/tmp/omegasim_a5_residual_accounting_20260627_current_request_2`.
  The result reproduced the fail-closed pattern: linear, nonlinear, and
  high-budget nonlinear predictors improved forecast skill versus reactive and
  budget-matched timing-broken nulls, but none passed both residual-structure
  null gates. Nonlinear and high-budget nonlinear also failed guardrails.
- Updated `README.md` so a future explicit A5 request points to the existing
  A5 preregistration as the active bounded gate without importing A6/A7
  mechanics or reopening broad seed sweeps.
- No simulator mechanics, dashboards, real integrations, seed sweeps, broad
  three-hive mechanics, or downstream multi-hive coupling were added.

## Verification

- `git status --short --branch` initially reported a clean worktree on
  `main...origin/main`.
- `.venv-conda/bin/python -m py_compile ohdyn/compare_predictive_control.py
  ohdyn/analyze_a5_residual_accounting.py ohdyn/automation_guard.py` passed.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed with `state: open`,
  `a5_preregistration_active: true`, `should_noop: false`, and
  `closed_reasons: []`.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6
  --out /tmp/omegasim_a5_predictive_control_compare_20260627_current_request_2`
  passed.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir
  /tmp/omegasim_a5_predictive_control_compare_20260627_current_request_2 --out
  /tmp/omegasim_a5_residual_accounting_20260627_current_request_2` passed and
  reported `Promotion decision: fail closed; no intermediate-budget condition
  satisfies all preregistered criteria.`
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting or automation_guard'` passed:
  `12 passed, 602 deselected`.
- `git diff --check` passed.

## Blockers

There is no code or local environment blocker. The scientific blocker is that
the current deterministic A5 scaffold again improves forecast skill without
surviving the preregistered full-accounting residual and null gates.

## Recommended Next Step

Draft a new A5.1 preregistration for direct prediction-spend/work-opportunity
competition before implementing any new prediction-resource mechanics.
