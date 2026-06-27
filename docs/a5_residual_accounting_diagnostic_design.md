# A5 Residual/Accounting Diagnostic Design

## Purpose

This note defines the minimum read-only diagnostic needed before any broader A5
predictive-control seed sweep. It uses existing A5 run artifacts and does not
add simulator mechanics, multi-hive coupling, external services, dashboards, or
new lobe architectures.

The diagnostic should answer one conservative question: after matching demand
streams and controlling for load, action opportunity, work budget, task volume,
and service capacity, does prediction budget leave residual high-level
trajectory structure beyond reactive and shuffled controls?

## Required Inputs

The analyzer should read an existing `ohdyn.compare_predictive_control` output
directory containing:

- `predictive_control_comparison_metrics.csv`
- `predictive_control_effects.csv`
- one per-condition/per-seed run directory with `metrics.csv`, `events.csv`,
  `manifest.yaml`, and `summary.md`

It should fail closed if any run is missing required A5 fields, if seeds are not
paired across all conditions, or if the condition set lacks `reactive`,
`linear`, `nonlinear`, `nonlinear_high_budget`, `oracle`, `shuffled`,
`nonlinear_shuffled`, and `nonlinear_high_budget_shuffled`.

## Primary Variables

Use the existing per-tick metric fields:

- Forecast variables: `a5_*_future_demand_share_tick`,
  `a5_*_forecast_share_tick`, `a5_*_forecast_error_tick`,
  `a5_forecast_abs_error_tick`, `a5_forecast_skill_tick`,
  and `a5_forecast_skill_per_budget_tick`.
- Allocation variables: `a5_*_work_share_tick`,
  `a5_*_allocation_future_residual_tick`,
  `a5_work_forecast_alignment_tick`, and
  `a5_work_future_demand_alignment_tick`.
- Accounting controls: `queue_depth`, `tasks_created_total`,
  `tasks_completed_total`, `queued_task_age_mean_tick`,
  `attention_capture_pressure_max_tick`, per-role/per-action counters, and
  per-class attention completion/work-event counters when present.
- Existing trajectory labels: baseline lobe labels and transition/dwell
  summaries may be reported as descriptive guardrails only, not as primary A5
  evidence.

## Residual Endpoints

The first analyzer should compute paired-seed condition means and deltas for:

- residual forecast-error trajectories after subtracting per-tick demand-share
  means;
- residual allocation-to-future-demand error after controlling for current
  backlog mix and total queue depth;
- residual high-level state vectors built from forecast error, allocation
  residuals, completion fraction, queue depth, queued age, capture pressure,
  and action/work opportunity counters;
- recurrence summaries for those residual state vectors, including nearest
  return distance, return-time histogram, and lag-1/lag-2 autocorrelation;
- compressibility/predictability summaries for the residual state sequence,
  using deterministic low-capacity predictors only.

Throughput, completion fraction, queue depth, and queued age are guardrails.
They can veto a claim if they degrade badly, but they do not by themselves
support structured-dynamics evidence.

## Accounting Controls

At minimum, report each endpoint in four forms:

1. Raw paired-seed condition delta.
2. Clock/demand controlled: residualized by tick and hidden demand shares.
3. Load/opportunity controlled: additionally residualized by queue depth,
   queued age, task creation/completion totals, and role/action work
   opportunity counters.
4. Full non-tautological accounting controlled: additionally residualized by
   capture pressure and per-class work-event/completion counters, excluding any
   target variable from its own control set.

The primary interpretation should come from the full non-tautological
accounting-controlled endpoint. If raw effects vanish under accounting controls,
close the pilot as another accounting result.

## Nulls

Use deterministic surrogate nulls that preserve the relevant marginals:

- paired condition-label permutation within seed;
- circular shift of residual trajectories within seed;
- shuffled predictor conditions as timing-breaking experimental nulls;
- label-count-preserving lobe transition null only for descriptive lobe
  summaries.

The two important contrasts are intermediate predictor minus reactive and
intermediate predictor minus its budget-matched shuffled/phase-randomized null:
`linear` versus `shuffled`, `nonlinear` versus `nonlinear_shuffled`, and
`nonlinear_high_budget` versus `nonlinear_high_budget_shuffled`. Oracle is a
positive-control ceiling, not the desired winner.

## Decision Rule

Promote A5 beyond smoke only if the same intermediate-budget condition satisfies
all of the following under paired seeds:

- forecast skill improves over reactive and the budget-matched shuffled null;
- residual structure increases over reactive and shuffled after full accounting
  controls;
- residual structure remains nontrivial relative to oracle rather than simply
  becoming perfectly smoothed;
- guardrails pass the prospective confirmatory tolerances in
  `docs/a5_confirmatory_addendum.md`: completion fraction may not drop by more
  than `0.01`, final queue depth may not rise by more than `1.0` task, final
  queued mean age may not rise by more than `0.5` tick, no attention class may
  lose more than one completed task, and peak capture pressure may not rise by
  more than `0.05`.

If these conditions do not hold, record A5 as unsupported or accounting
explained. Do not add multi-hive coupling or richer simulator mechanics to
rescue a failed single-hive diagnostic.

## Output Contract

A future read-only analyzer should write:

- `a5_residual_accounting_metrics.csv`: one row per condition/seed/control
  level/endpoint.
- `a5_residual_accounting_effects.csv`: paired deltas, null intervals, and
  sign-stability summaries.
- `summary.md`: conservative interpretation, guardrail failures, and whether
  any promotion rule is satisfied.

The analyzer must be deterministic by seed and must not modify the source run
artifacts it reads.
