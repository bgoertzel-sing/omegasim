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
`notify_ben: false`). This run followed that recommendation and did not add real
LLM calls, dashboards, Lean, Slack, browser automation, Atomspace integrations,
or downstream multi-hive coupling.

## Latest Changes

- Status: A6 analysis-gate residual timeseries audit added, 2026-06-27.
- Changed: `ohdyn.analyze_a6_logistic_appraisal` now writes
  `a6_logistic_appraisal_residual_timeseries.csv` alongside the existing
  endpoint, paired control-delta, residual preflight, control-summary, and
  consistency-check artifacts. The new CSV exposes per-tick raw, fitted, and
  residual values for each latent/artifact outcome using the same clock, queue,
  task, prediction-budget, and action-opportunity controls as the residual
  preflight.
- Changed: residual fitting now shares one helper for fitted and residual values,
  and the analyzer summary reports the residual-timeseries row count while
  explicitly warning that these rows are audit data, not recurrence evidence.
- Result: Running the analyzer on the existing canonical A6 smoke comparison
  `runs/a6_logistic_appraisal_compare` produced 1,792 residual-timeseries rows
  for the two-seed four-condition smoke grid. The status remains read-only
  control/residual preflight; residualization is still underdetermined at smoke
  scale and is not promotion evidence.
- Verification: `.venv-conda/bin/python -m py_compile
  ohdyn/analyze_a6_logistic_appraisal.py tests/test_run_harness.py` passed;
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q -k
  'a6_read_only_analysis or a6_smoke_comparison_helper'` passed with `4 passed,
  592 deselected`; `.venv-conda/bin/python -m pytest tests/test_run_harness.py
  -q -k 'a6'` passed with `10 passed, 586 deselected`;
  `.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal --compare-dir
  runs/a6_logistic_appraisal_compare --out
  runs/a6_logistic_appraisal_analysis_residual_timeseries_v1` passed and wrote
  1,792 residual-timeseries data rows.
- Blockers: none.
- Recommended next step: add a narrow A6 residual-timeseries contrast summary
  that aggregates per-tick residual sign changes, lag-1 residual
  autocorrelation, and residual variance deltas by paired seed and contrast
  without broadening seeds or making promotion claims.
