# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

This run audited the current A6 analyzer against the existing seed `1..2` smoke
artifacts, following the external GPT-5.5-Pro strategy review recommendation.
The review direction was incorporated because it was scientifically sensible:
the analyzer code had outrun the tracked interpretation, and the next bounded
step was to publish the actual control-delta/residual gate rather than add
seeds or mechanisms.

A5 remains closed conservatively by the seed `7..16` forecast-skill/residual-gap
evidence: bounded predictors improved forecast skill under matched deterministic
demand streams, but the promotion-relevant residual structure did not survive
load, service-capacity, action-opportunity, work-budget, and budget-matched
timing-broken null controls. Do not add new A5 mechanics, broad seed sweeps, or
downstream three-hive delayed anticipatory coupling without a fresh
preregistration.

The current post-A5 focus remains the accepted A6.1 source-accounting direction.
A6 is still smoke/analyzer-only, not promoted. The canonical
`runs/a6_logistic_appraisal_compare` artifacts are adequate for the A6
endpoint/control-delta/residual smoke gate, but they predate the A6.1
artifact-update source fields and must not be used for A6.1 source-accounting
interpretation.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling.

## Latest Changes

- Status: A6 analyzer/read-only gate reconciliation completed, 2026-06-27.
- External review: `../outputs/strategy-reviews/omegasim/latest-review.md`
  reported `strategic_change_level: minor`, `notify_ben: false`, and
  recommended auditing the expanded A6 analyzer before adding seeds or
  mechanisms. No Ben notification is required.
- Guard: `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: open`, `should_noop: false`, `strategic_change_level: minor`, and
  `notify_ben: false`.
- Analyzer run: `.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal
  --compare-dir runs/a6_logistic_appraisal_compare --out
  runs/a6_logistic_appraisal_analysis_gate_seed1_2` completed without rerunning
  simulations.
- Outputs: the analyzer emitted endpoint, manifest, control-delta,
  control-summary, residual-preflight, residual-timeseries,
  residual-contrast-summary, residual-contrast-rollup,
  comparison-consistency, effects-consistency, artifact-provenance, and
  source-accounting CSVs plus `summary.md`.
- Row counts: endpoints `8`, manifest `7`, control deltas `6`, control summary
  `42`, residual preflight `112`, residual timeseries `1792`, residual contrast
  summary `84`, residual contrast rollup `42`, comparison consistency `4`,
  effects consistency `3`, artifact provenance `80`, source accounting `80`.
- Result: `docs/results/a6_analysis_gate_seed1_2.md` was updated to publish the
  actual current gate result. Logistic minus linear artifact utility remains
  tiny (`0.001707` mean), sign-disagrees by seed, has higher mean queue depth
  (`+1.5`), and lower mean completion fraction (`-0.018187`). All residual
  rows remain `underdetermined_smoke_scale`; this is not recurrence or
  promotion evidence.
- Source-accounting caveat: all `80` source-accounting rows from
  `runs/a6_logistic_appraisal_compare` are `missing_required_fields` because
  those canonical smoke artifacts predate the A6.1 source-field schema. The
  separate tracked source-accounting audit over fresh source-schema artifacts,
  `docs/results/a6_1_source_accounting_audit_seed1_2.md`, remains the relevant
  source-accounting result.
- Verification: `.venv-conda/bin/python -m py_compile
  ohdyn/analyze_a6_logistic_appraisal.py ohdyn/automation_guard.py` passed;
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q -k
  'a6_read_only_analysis or automation_guard'` passed (`12 passed, 587
  deselected`).
- Blockers: none.
- Recommended next step: preregister the smallest A6.1 pilot/null design using
  source-field-complete artifacts, source-preserving nulls, and
  backlog-adjusted productivity controls, without broadening seeds or changing
  interpretation in the same run.
