# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Ben explicitly requested returning from the prior A4/A5 closure boundary to the
next scientific stage: A5 anticipatory predictive-control dynamics. This run
treats that request as the active source of truth. The prior A2/A3/A4 lessons
remain binding: do not interpret load, service-capacity, action-opportunity,
task-volume, or accounting artifacts as independent strange-attractor evidence.

The active A5 artifact is
`docs/a5_anticipatory_predictive_control_preregistration.md`. It now defines a
deterministic single-hive setup, matched demand/service/action/work controls,
reactive, linear, nonlinear, oracle, and budget-matched timing-broken null
conditions, and Ben's resource-bounded prediction hypothesis: prediction effort
is a scarce managed resource, perfect prediction may smooth away interesting
dynamics, and intermediate prediction budgets may create structured forecast
errors whose high-level collective states are cheaper to predict than detailed
task trajectories.

The smallest A5 smoke scaffold already exists and remains single-hive only:
`configs/a5_predictive_linear_smoke.yaml`,
`ohdyn.compare_predictive_control`, and `ohdyn.analyze_a5_residual_accounting`.
No real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace
integrations, live task boards, or three-hive mechanics are in scope for this
stage. Three-hive delayed anticipatory coupling remains downstream after
single-hive evidence, target/phase nulls, and resource-bounded cross-hive
prediction are preregistered.

## Latest Changes

- Status: A5 preregistration refresh and bounded smoke/pilot completed,
  2026-06-27.
- Changed: Tightened the A5 preregistration to spell out the deterministic
  single-hive setup, matched accounting controls, prediction-budget accounting,
  budget-matched shuffled or phase-randomized null semantics, lead-lag primary
  endpoint, and the intermediate-budget residual-dynamics question.
- Result: The existing smallest A5 scaffold ran end to end. The paired-seed
  smoke comparison improved forecast skill for linear and nonlinear predictors
  versus reactive and budget-matched shuffled/null controls, but residual
  accounting failed closed: no intermediate-budget condition satisfied all
  preregistered residual-structure and guardrail criteria.
- Verification: `.venv-conda/bin/python -m py_compile ohdyn/sim.py
  ohdyn/config.py ohdyn/compare_predictive_control.py
  ohdyn/analyze_a5_residual_accounting.py tests/test_run_harness.py` passed;
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q -k 'a5 or
  automation_guard'` passed with `10 passed, 586 deselected`;
  `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  runs/a5_predictive_linear_prereg_refresh_seed5` passed;
  `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6
  --out runs/a5_predictive_control_prereg_refresh_compare` passed;
  `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir
  runs/a5_predictive_control_prereg_refresh_compare --out
  runs/a5_residual_accounting_prereg_refresh` passed; `.venv-conda/bin/python
  -m ohdyn.automation_guard` returned `state: open` and `should_noop: false`;
  `git diff --check` passed.
- Blockers: none.
- Recommended next step: draft a narrow follow-up A5 diagnostic plan for why forecast-skill gains did not survive residual accounting.
