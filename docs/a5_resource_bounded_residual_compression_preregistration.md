# A5 Resource-Bounded Residual-Compression Diagnostic Preregistration

## Purpose

This document freezes one read-only A5 follow-up diagnostic before any new A5
simulator mechanics are considered. It addresses the current gap: A5-family
predictors repeatedly improved forecast skill, but no intermediate-budget
condition survived full-accounting residual/null promotion.

The diagnostic asks whether the existing A5 and A5.1a artifacts contain a
resource-bounded compression signal that is hidden by aggregate residual
predictability summaries, or whether the prior fail-closed interpretation is
confirmed. It cannot promote A5 by itself.

## Scope

Use only existing deterministic single-hive artifacts from already completed
A5-family runs, especially:

- reopened A5 seed `5,6` predictive-control comparison artifacts;
- A5.1 and A5.1a prediction-spend/cost-calibration comparison artifacts when
  available;
- existing residual-accounting analyzer outputs and result notes.

No new simulator runs, broad seed sweeps, new predictor knobs, new mechanics,
dashboards, real LLM calls, Lean, Slack, browser automation, Atomspace
integrations, live task-board integrations, A7.2 mechanics, or multi-hive
coupling are authorized by this preregistration.

## Hypothesis

If Ben's resource-bounded prediction hypothesis has residual support in the
existing A5-family artifacts, intermediate prediction budgets should compress
or predict the fully accounted residual state better than reactive,
oracle-smoothed, and budget-matched timing-broken null conditions after
conditioning on prediction spend and remaining work budget.

If the apparent compression advantage is explained by spend, backlog,
completion, queue age, work opportunity, class completions, or matched shuffled
nulls, then the A5-family result remains closed as an accounting/null result.

## Required Inputs

The diagnostic consumes existing `ohdyn.compare_predictive_control` and
`ohdyn.analyze_a5_residual_accounting` artifact directories. It should fail
closed if required files are absent rather than generating replacement runs.

Required files, when a comparison directory is analyzed:

- `predictive_control_comparison_metrics.csv`
- `predictive_control_effects.csv`
- per-condition/per-seed `metrics.csv`
- existing residual-accounting CSVs or summaries when available

The diagnostic may report missing artifact classes as coverage gaps, but it
must not infer promotion from incomplete artifacts.

## Residual State

Use the already recorded per-tick fields needed to build a residual state over:

- forecast absolute error and forecast skill per budget;
- lead-lag allocation/future-demand residuals;
- queue depth, queued mean age, task creation and completion totals;
- work opportunity, charged prediction work, remaining work budget, and
  prediction spend when present;
- attention class work/completion counters and capture pressure when present.

The primary residual representation is the full-accounting residual state from
the existing analyzer. The diagnostic may break that state into components, but
component-level hints are secondary.

## Compression Endpoints

Report deterministic low-capacity compression or predictability summaries for
the fully accounted residual state:

1. residual compression ratio by condition and seed;
2. delta versus reactive, oracle, and budget-matched timing-broken nulls;
3. compression gain per unit prediction spend;
4. compression gain after controlling for remaining work budget and charged
   prediction work;
5. sign agreement across paired seeds;
6. whether the contrast agrees with the existing residual predictability
   promotion audit.

Do not use high-capacity models, learned embeddings, stochastic search, or
post-hoc predictor tuning. The point is to audit whether a simple reproducible
compression signal exists, not to rescue A5 with a more expressive detector.

## Nulls And Controls

The primary nulls are the already generated budget-matched timing-broken
conditions:

- `linear` versus `shuffled`;
- `nonlinear` versus `nonlinear_shuffled`;
- `nonlinear_high_budget` versus `nonlinear_high_budget_shuffled`;
- A5.1a charged predictors versus their spend-only replay nulls when present.

Also report reactive and oracle contrasts. Oracle is a smoothing ceiling, not
the target winner. Full-accounting interpretation must control demand phase,
task arrivals, service/action opportunity, work budget, prediction spend,
remaining work budget, backlog, queued age, completion fraction, capture
pressure, and per-class work/completion counters when those fields exist.

## Decision Rule

This diagnostic has only three possible outcomes:

- `closure_confirmed`: no intermediate-budget condition beats reactive,
  oracle, and its budget-matched null on full-accounting residual compression
  while satisfying guardrails;
- `analyzer_bug_or_coverage_gap`: a specific missing field, control mapping
  error, or artifact coverage problem prevents interpretation and can be fixed
  without new simulator mechanics;
- `future_preregistration_needed`: an interpretable compression signal exists
  but requires a separate preregistered mechanism or confirmatory design before
  any scientific promotion.

Promotion language remains disallowed. In particular, do not claim
strange-attractor-like, lobe-like, semantic-dynamics, or collective phase
structure from this diagnostic alone.

## Output Contract

The follow-up artifact should be a concise report under `docs/results/` with:

- input artifact paths and coverage status;
- one table of compression endpoints by condition/seed/control level;
- one table of preregistered contrasts and pass/fail status;
- explicit handling of GPT-5.5-Pro recommendations;
- the conservative decision outcome above;
- exactly one next step.

The diagnostic must be deterministic and must not modify source run artifacts.
