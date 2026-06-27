# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

The A5 anticipatory predictive-control diagnostic thread is closed
conservatively. The requested A5 preregistration, minimal deterministic
single-hive scaffold, matched reactive/linear/nonlinear/oracle/budget-matched
timing-broken null conditions, confirmatory residual-accounting analysis, and
read-only forecast-skill/residual-gap report now exist.

The current focus returns to the accepted post-A5 **A6 analysis gate**. Do not
broaden seeds or interpret logistic-appraisal results until the read-only A6
analyzer reports paired accounting, residual, and null-control deltas from the
existing smoke artifacts.

The current A6 analyzer gate and the follow-up artifact provenance audit have
now been run on the existing seed `1..2` smoke artifacts and recorded in
`docs/results/a6_analysis_gate_seed1_2.md` and
`docs/results/a6_artifact_provenance_audit_seed1_2.md`. The A6.1
schema/control addendum is preregistered in
`docs/a6_1_schema_control_addendum.md`, and the minimal artifact-update source
schema now exists for A6-enabled smoke runs. Treat A6 as smoke/analyzer-only,
not promoted.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling.

## Latest Changes

- Status: minimal A6.1 artifact-update source schema implemented, 2026-06-27.
- Changed: A6-enabled `events.csv` now includes source-separated artifact delta
  columns for ambient drift, handoff attempt/success/failure,
  prediction-expenditure/error, queue/work accounting, noise, unclipped delta,
  and clipping residual. A6-enabled `metrics.csv` now includes the addendum's
  prediction budget/action/error, queue depth, work action, action opportunity,
  and service-capacity accounting fields. The manifest records the artifact
  update source schema.
- Changed: added a deterministic A6 smoke reconstruction test asserting that
  each artifact-update row reconstructs from its source columns and clipping
  residual, and that per-field source totals reconstruct final artifact metrics
  from the initial artifact state.
- Result: no dashboards, external integrations, real LLM calls, broader seeds,
  new configs, new scientific claims, or multi-hive/downstream coupling were
  added.
- Interpretation: A6 remains smoke/analyzer-only. The schema now supports
  source-separated reconstruction for fresh A6 smoke runs, but the read-only
  analyzer still needs to audit source completeness/shares before any A6.1
  pilot or interpretation change.
- External strategic review handling: latest review has
  `strategic_change_level: minor` and `notify_ben: false`. Its A6 analyzer-gate
  recommendation was already completed by the current status; the follow-on
  GPT-5.5-Pro recommendation to add artifact-update provenance and source
  accounting is accepted and partially implemented as the minimal source schema
  and deterministic reconstruction test. No GPT-5.5-Pro recommendation was
  rejected in this run.
- Verification: `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: open`, `should_noop: false`, `strategic_change_level: minor`, and
  `notify_ben: false`; `.venv-conda/bin/python -m py_compile ohdyn/sim.py
  ohdyn/io.py ohdyn/analyze_a6_logistic_appraisal.py
  ohdyn/compare_a6_logistic_appraisal.py ohdyn/automation_guard.py` passed;
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q -k 'a6 or
  automation_guard'` passed; `git diff --check` passed.
- Blockers: none.
- Recommended next step: extend the read-only A6 analyzer with A6.1 source
  completeness, reconstruction-residual, and source-share audit outputs for
  freshly generated source-schema smoke artifacts, without broadening seeds or
  changing scientific interpretation.
