# A5 Forecast-Skill/Residual-Gap Diagnostic Plan

## Purpose

The A5 pilot and confirmatory runs showed a narrow positive result: bounded
predictors improved forecast skill under matched deterministic demand streams.
They did not show promotion-worthy residual collective structure after the
full accounting controls and budget-matched timing-broken nulls.

This note defines a bounded read-only follow-up for that gap. It does not
reopen A5 for broader simulation, multi-hive coupling, richer lobe mechanics,
external integrations, dashboards, or a larger seed sweep.

## Source Evidence

Use only existing A5 artifacts unless a separate preregistration authorizes new
runs:

- `docs/a5_anticipatory_predictive_control_preregistration.md`
- `docs/a5_residual_accounting_diagnostic_design.md`
- `docs/a5_confirmatory_addendum.md`
- `docs/results/a5_predictive_control_pilot_seed5_6.md`
- `docs/results/a5_confirmatory_seed7_16.md`
- `docs/results/a5_closure_note_seed7_16.md`

The diagnostic question is why forecast skill improved while the primary
full-accounting residual-state predictability contrasts did not survive the
paired label-permutation interval.

## Candidate Explanations

Treat these as mutually nonexclusive audit hypotheses, not as promotion claims:

1. The predictors forecast the hidden demand stream, but attention/work
   allocation cannot convert that forecast into distinct collective state
   trajectories under the fixed work budget.
2. The full-accounting controls correctly absorb the apparent structure because
   the residuals are explained by backlog, task flow, action opportunity,
   capture pressure, or per-class work/completion accounting.
3. The residual-state predictability endpoint is too coarse or too tightly
   coupled to queue accounting to detect a real but narrow anticipatory signal.
4. The budget-matched shuffled nulls preserve enough marginal forecast shape
   that timing advantage is small once paired seeds and accounting controls are
   applied.
5. Oracle smoothing reduces residual dynamics, but intermediate predictors do
   not create a distinct partially predictable residual regime in this scaffold.

## Read-Only Checks

Run the checks on already generated A5 comparison and residual-accounting
artifacts where available:

- map forecast-skill gains to allocation-future-demand alignment by condition,
  seed, and attention class;
- compare each predictor to its budget-matched shuffled null on lead-lag
  allocation fields before and after full accounting controls;
- break the full-accounting residual-state vector into its component fields and
  identify which controls remove the raw signal;
- audit whether completion fraction, queue depth, queued age, capture pressure,
  or class work/completion counters explain most predictor/null differences;
- compare oracle-minus-intermediate contrasts to determine whether high-quality
  prediction smooths residual variance rather than increasing structured
  recurrence;
- verify that any secondary return-distance or autocorrelation hints are not
  driven by a single seed, guardrail degradation, or budget mismatch.

The preferred output is one concise table per check with condition, seed,
contrast, control level, endpoint, mean delta, sign agreement, and whether the
effect is outside the existing paired label-permutation interval.

## Decision Rules

This diagnostic cannot promote A5. It can only choose one of three outcomes:

- accounting-confirmed closure: forecast gains remain explainable by matched
  demand/accounting fields, so A5 stays closed;
- analyzer refinement needed: a specific endpoint or control mapping bug is
  found, with a minimal testable fix identified before rerunning the read-only
  analyzer;
- new preregistration needed: a scientifically different A5 design is required,
  with prediction spend competing directly against work, coordination, cleanup,
  or research opportunity before any new mechanics are implemented.

Fail closed if the audit only finds secondary lobe-like or return-map hints
that do not survive budget-matched nulls, paired seeds, and the existing
accounting controls.

## Recommended Next Artifact

The next bounded artifact should be a small read-only diagnostic report over
the existing seed `7..16` A5 artifacts. It should explain which of the candidate
explanations above best accounts for the forecast-skill/residual-structure gap
and should recommend either continued A5 closure or one explicitly scoped
future preregistration.
