# A5 Confirmatory Addendum

## Scope

This addendum freezes the next A5 single-hive confirmatory rules before any
larger paired-seed run. It incorporates the 2026-06-26 external strategic
review recommendation to avoid a broader seed sweep until guardrail tolerances
and budget-matched timing-broken nulls are prospective.

The seed `5,6` A5 comparison remains pilot/analyzer-development data. It must
not be treated as the decisive confirmatory set.

## Budget-Matched Nulls

Each predictive-budget condition must have its own timing-broken null with the
same prediction budget and the same matched demand, action, service, and work
opportunity settings:

- `linear` budget `0.35` is compared to `shuffled` budget `0.35`.
- `nonlinear` budget `0.65` is compared to `nonlinear_shuffled` budget `0.65`.
- Any future high-budget condition must add its own budget-matched shuffled or
  phase-randomized null before it is run.

The older nonlinear-minus-`shuffled` contrast is retained only as pilot context;
it is not a confirmatory promotion contrast because the budgets differ.

## Guardrail Policy

The pilot guardrail remains strict zero tolerance. For a fresh confirmatory
seed set, use these practical equivalence tolerances prospectively:

- completion fraction: no worse than reactive by more than `0.01`;
- final queue depth: no worse than reactive by more than `1.0` task;
- final queued-task mean age: no worse than reactive by more than `0.5` tick;
- per-class starvation: no attention class may lose more than one completed
  task versus reactive when reactive completes at least one task in that class;
- volatility: peak capture pressure may not exceed reactive by more than `0.05`.

These tolerances are guardrails only. They can veto promotion, but satisfying
them is not evidence for residual structured dynamics.

## Frozen Promotion Contrasts

Primary residual-structure interpretation remains the full-accounting
`residual_state_predictability_r2` endpoint from
`ohdyn.analyze_a5_residual_accounting`.

A5 can be promoted beyond single-hive smoke only if the same intermediate
predictor satisfies all of the following on fresh paired seeds:

- forecast skill improves versus reactive;
- forecast skill improves versus its budget-matched timing-broken null;
- full-accounting residual-state predictability increases versus reactive
  outside the paired label-permutation interval;
- full-accounting residual-state predictability increases versus the
  budget-matched timing-broken null outside the paired label-permutation
  interval;
- residual structure remains nontrivial relative to oracle;
- the practical guardrails above pass.

Return-distance, return-time, lobe-transition, and dwell summaries remain
secondary diagnostics unless a later preregistration explicitly promotes them.
