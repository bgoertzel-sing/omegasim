# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

A5 is closed under its preregistered accounting evidence. The seed `7..16`
closure records in `docs/results/a5_eight_condition_closure_update_seed7_16.md`
and `docs/results/a5_closure_note_seed7_16.md` are the current A5
interpretation: prediction manipulations improved forecast skill, but residual
structure did not survive full accounting and paired null checks. Do not reopen
A5 for additional seeds, mechanics, or residual/lobe/attractor claims without a
new preregistration.

A7 is the active gated direction accepted by Ben on 2026-06-27. It is a
single-hive semantic-field design gate for source-accounted semantic/artifact
fields and logistic inter-agent dependence. Existing A7 artifacts are
schema/mechanics smoke evidence only: they do not support semantic dynamics,
lobe structure, attractors, synchrony, or downstream multi-hive coupling.

The latest urgent external strategic review in
`../outputs/strategy-reviews/omegasim/latest-review.md` reported
`strategic_change_level: major` and `notify_ben: true`. The direction shift is
to stop the A5 re-open loop, record A5 as closed/accounting-explained, restore
A7 as the active gated smoke, and notify Ben that the status/README drift was
corrected.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Do not make attractor, lobe, synchrony, or
semantic-dynamics claims from A7 smoke artifacts.

## Latest Changes

- Implemented the first read-only A7 residual/null analyzer over the existing
  six preregistered A7 conditions. `ohdyn.analyze_a7_semantic_field` now writes
  deterministic residual metric rows and paired positive-vs-null contrast rows
  in addition to the prior completeness, manifest, and smoke-report artifacts.
- The new A7 residual/null gate remains conservative: seed-1 smoke artifacts
  with complete schema/source reconstruction still fail closed as
  `fail_closed_insufficient_horizon`, with no semantic-dynamics, attractor,
  lobe, synchrony, or promotion claim.
- Reconciled `AUTOMATION_STATUS.md` and `README.md` with the closed A5
  evidence and the accepted A7 roadmap. The stale A5-active wording has been
  replaced with A5-closed/A7-active wording.
- Ran the current stale A5 paired-seed pilot command and residual-accounting
  analyzer before the urgent review completed. The result still fails closed:
  all intermediate prediction budgets improved forecast skill, but none
  satisfied the preregistered residual and guardrail promotion criteria.
- Requested and incorporated an urgent GPT-5.5-Pro strategy review because this
  run observed source-of-truth drift between A5-active status wording and
  A5-closed/A7-accepted roadmap/results. The review requires Ben notification.
- No simulator mechanics, dashboards, real integrations, seed sweeps, broad
  three-hive mechanics, or downstream multi-hive coupling were added.

## Verification

- `git status --short --branch` initially reported a clean worktree on
  `main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed with `state: open`,
  `should_noop: false`, and `closed_reasons: []`.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6
  --out /tmp/omegasim_a5_predictive_control_compare_20260627_current` passed.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir
  /tmp/omegasim_a5_predictive_control_compare_20260627_current --out
  /tmp/omegasim_a5_residual_accounting_20260627_current` passed. The analyzer
  reported `Promotion decision: fail closed; no intermediate-budget condition
  satisfies all preregistered criteria.`
- `../outputs/strategy-review.py --project omegasim --repo "$PWD" --root ..
  --trigger "urgent in-run confusion or novelty" --urgent` passed and wrote a
  major/notify-Ben review.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py
  ohdyn/analyze_a7_semantic_field.py ohdyn/a7_semantic_field_contract.py`
  passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a7 or automation_guard'` passed: `18 passed, 596 deselected`.
- Generated deterministic seed-1 A7 smoke artifacts for all six preregistered
  conditions under `/tmp/omegasim_a7_seed1_smoke_20260627_residual` and ran
  `.venv-conda/bin/python -m ohdyn.analyze_a7_semantic_field --compare-dir
  /tmp/omegasim_a7_seed1_smoke_20260627_residual --out
  /tmp/omegasim_a7_seed1_analysis_20260627_residual`. The analyzer passed and
  reported `Status: fail_closed_insufficient_horizon`, source reconstruction
  pass rows `6`, field variation pass rows `6`, prediction/work-budget
  competition pass rows `6`, residual row status `insufficient_horizon=36`,
  and null-contrast gate status `insufficient_horizon=30`.
- `git diff --check` passed.

## Blockers

Ben should be notified that the urgent review marked the status/roadmap drift
as a major strategic correction: A5 is closed/accounting-explained and A7 is
the active gated smoke. There is no code or local environment blocker.

## Recommended Next Step

Preregister the smallest A7 long-horizon residual/null validation gate before
running any longer A7 paired seeds, including minimum horizon, promotion/closure
criteria, productivity safeguard, null completeness requirements, and
cross-seed direction agreement rules.
