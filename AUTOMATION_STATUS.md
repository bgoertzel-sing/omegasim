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

The current A6 analyzer gate, artifact provenance audit, and A6.1
source-accounting audit have now been run on seed `1..2` smoke artifacts and
recorded in `docs/results/a6_analysis_gate_seed1_2.md`,
`docs/results/a6_artifact_provenance_audit_seed1_2.md`, and
`docs/results/a6_1_source_accounting_audit_seed1_2.md`. The A6.1
schema/control addendum is preregistered in
`docs/a6_1_schema_control_addendum.md`; the minimal artifact-update source
schema exists for A6-enabled smoke runs and the read-only analyzer now audits
source completeness, reconstruction residuals, and source shares. Treat A6 as
smoke/analyzer-only, not promoted.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling.

## Latest Changes

- Status: A6.1 read-only source-accounting analyzer audit implemented and run,
  2026-06-27.
- Changed: `ohdyn.analyze_a6_logistic_appraisal` now writes
  `a6_logistic_appraisal_source_accounting.csv` with A6.1 required-field
  completeness, artifact-delta reconstruction status, per-source absolute
  delta shares, handoff-success/prediction/queue-work alias shares, and
  conservative schema/alias statuses.
- Changed: added a focused deterministic analyzer test for the new source
  accounting output and updated the existing read-only analyzer skeleton test.
- Result: a fresh bounded seed `1..2` smoke comparison and read-only analyzer
  run were written under ignored `runs/a6_1_source_schema_compare` and
  `runs/a6_1_source_schema_analysis_v2`. The tracked result note is
  `docs/results/a6_1_source_accounting_audit_seed1_2.md`.
- Result: source-accounting row counts were 80 rows; required-field status was
  `schema_pass` for all 80 rows; reconstruction status was `schema_pass` for
  all 80 rows; conservative source-accounting statuses were
  `high_handoff_alias_risk: 16` and `underdetermined_smoke_scale: 64`.
- Result: no dashboards, external integrations, real LLM calls, broader seeds,
  new configs, new scientific claims, or multi-hive/downstream coupling were
  added.
- Interpretation: A6 remains smoke/analyzer-only. The source schema is present
  and reconstructs, but the audit remains smoke-scale and handoff-success alias
  risk persists; this is not evidence for attractors, recurrence, lobe grammar,
  synchrony, or nonlinear collective structure.
- External strategic review handling: latest review has
  `strategic_change_level: minor` and `notify_ben: false`. Its A6 analyzer-gate
  recommendation was already completed by the current status; the follow-on
  GPT-5.5-Pro recommendation to add artifact-update provenance and source
  accounting is accepted and now implemented through the source schema,
  deterministic reconstruction test, and read-only source-accounting analyzer
  audit. No GPT-5.5-Pro recommendation was rejected in this run.
- Verification: `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: open`, `should_noop: false`, `strategic_change_level: minor`, and
  `notify_ben: false`; `.venv-conda/bin/python -m py_compile
  ohdyn/analyze_a6_logistic_appraisal.py tests/test_run_harness.py` passed;
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q -k 'a6 or
  automation_guard'` passed; `.venv-conda/bin/python -m
  ohdyn.compare_a6_logistic_appraisal --seeds 1 2 --out
  runs/a6_1_source_schema_compare` passed; `.venv-conda/bin/python -m
  ohdyn.analyze_a6_logistic_appraisal --compare-dir
  runs/a6_1_source_schema_compare --out runs/a6_1_source_schema_analysis_v2`
  passed; `git diff --check` passed.
- Blockers: none.
- Recommended next step: preregister the smallest A6.1 pilot/null design that
  tests source-preserving nulls and backlog-adjusted productivity after source
  accounting, without broadening seeds or changing interpretation in the same
  run.
