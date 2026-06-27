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
`docs/results/a6_artifact_provenance_audit_seed1_2.md`. Treat A6 as
smoke/analyzer-only, not promoted.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling.

## Latest Changes

- Status: A6 artifact provenance audit added, 2026-06-27.
- Changed: extended `ohdyn.analyze_a6_logistic_appraisal` with
  `a6_logistic_appraisal_artifact_provenance.csv`, a read-only audit that
  derives per-artifact-field tick deltas from `metrics.csv` and attributes them
  to same-tick A6 event/action sources from existing run artifacts.
- Changed: ran
  `.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal --compare-dir runs/a6_logistic_appraisal_compare --out runs/a6_artifact_provenance_audit`
  over the existing seed `1..2` smoke comparison artifacts and added
  `docs/results/a6_artifact_provenance_audit_seed1_2.md`.
- Result: the audit emitted 80 artifact-provenance rows. Across all conditions,
  alias flags were `57` `high_action_alias_risk`, `15` `no_change`, `6`
  `mixed_or_low_alias_risk_smoke`, and `2` `action_coupled_smoke`. Logistic
  artifact readiness and utility rows for both seeds were
  `high_action_alias_risk`, dominated by same-tick handoff-success attribution.
- Interpretation: A6 remains smoke/analyzer-only. The provenance audit
  strengthens the previous non-promotion conclusion because current artifact
  utility/readiness signals are too handoff/action-coupled to support attractor,
  lobe-grammar, synchrony, causality, recurrence, or nonlinear collective
  structure claims.
- External strategic review handling: latest review has
  `strategic_change_level: minor` and `notify_ben: false`; its completed A6 gate
  recommendation remains accepted. No GPT-5.5-Pro recommendation was rejected in
  this run.
- Verification: `.venv-conda/bin/python -m py_compile
  ohdyn/analyze_a6_logistic_appraisal.py tests/test_run_harness.py` passed;
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported `state: open`;
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q -k
  'a6_read_only_analysis or automation_guard'` passed with `11 passed, 586
  deselected`; `git diff --check` passed.
- Blockers: none.
- Recommended next step: write a minimal A6.1 schema/control addendum that preregisters how to separate ambient artifact drift, handoff success/failure effects, prediction expenditure, and queue/work accounting before any broader A6 seed run.
