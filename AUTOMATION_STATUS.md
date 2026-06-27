# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Ben accepted the provisional A6/A7/A8 roadmap on 2026-06-27 in
`docs/omegasim_provisional_experiment_roadmap.md`. That roadmap supersedes the
older A5 closure/no-op posture and is the active source of truth for the current
research loop.

The active stage is **A6: single-hive logistic-appraisal smoke and analysis
gate**. A0/A1 are complete and must not be duplicated. A2-A5 remain binding
negative/clarifying controls: do not interpret load, service capacity, action
opportunity, task volume, work budget, queue depth, or action-count accounting
as independent strange-attractor evidence.

External strategy review
`../outputs/strategy-reviews/omegasim/latest-review.md` recommends strengthening
the read-only A6 analyzer before any broader simulation or promotion claim. The
review did not require notifying Ben (`strategic_change_level: none`,
`notify_ben: false`). Current runs follow that recommendation and do not add
real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace
integrations, or downstream multi-hive coupling.

## Latest Changes

- Status: A6 analysis-gate residual contrast rollup added, 2026-06-27.
- Changed: `ohdyn.analyze_a6_logistic_appraisal` now writes
  `a6_logistic_appraisal_residual_contrast_rollup.csv` alongside the existing
  endpoint, paired control-delta, residual preflight, residual-timeseries,
  residual-contrast summary, control-summary, and consistency-check artifacts.
  The new CSV aggregates paired seed-level residual variance, lag-1 residual
  autocorrelation, and residual sign-change deltas by contrast/outcome and
  reports direction-agreement counts without rerunning simulations.
- Changed: analyzer summary and focused A6 tests now cover the new residual
  rollup artifact and explicitly label direction agreement as smoke-scale audit
  data, not recurrence or promotion evidence.
- Result: Running the analyzer on the existing canonical A6 smoke comparison
  `runs/a6_logistic_appraisal_compare` produced 42 residual-contrast rollup data
  rows, 84 residual-contrast summary data rows, and 1,792 residual-timeseries
  data rows for the two-seed four-condition smoke grid. All 42 rollup rows are
  `underdetermined_smoke_scale`; direction agreement is mixed across the two
  smoke seeds (`0.5` for most variance/autocorrelation/sign-change rollups).
  The scientific status remains read-only control/residual preflight and is not
  promotion evidence.
- Verification: `.venv-conda/bin/python -m py_compile
  ohdyn/analyze_a6_logistic_appraisal.py tests/test_run_harness.py` passed;
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q -k
  'a6_read_only_analysis or a6_smoke_comparison_helper'` passed with `4 passed,
  592 deselected`; `.venv-conda/bin/python -m pytest tests/test_run_harness.py
  -q -k 'a6'` passed with `10 passed, 586 deselected`;
  `.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal --compare-dir
  runs/a6_logistic_appraisal_compare --out
  runs/a6_logistic_appraisal_analysis_residual_rollup_v1` passed and wrote 42
  residual-contrast rollup data rows.
- Blockers: none.
- Recommended next step: add a preregistered same-tick logistic smoke control
  fixture and wire it into the existing A6 paired comparison/analyzer at the
  same two-seed smoke scale, preserving read-only analysis semantics and making
  no promotion claims.
