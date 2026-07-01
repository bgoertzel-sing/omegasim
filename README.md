# OmegaSim

OmegaSim is a lightweight Python simulator for OmegaHive1 and Moltbook-style multi-hive dynamics.

The first implementation is intentionally abstract and numeric. It should not call real LLMs, Lean, Slack, browsers, Atomspace, or live task boards. Early versions represent those systems as queues, graph edges, semantic fields, role policies, and events.

## Initial Mission

Explore whether OmegaHive-like agent societies display structured lobe dynamics, and whether multiple hives coupled through a Moltbook-style shared layer display useful phase-differentiated lobe grammars rather than global synchronization.

## First Milestone

Implement Phase A0/A1 from the experiment plan:

```bash
python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1
```

The first run harness should produce:

```text
config.yaml
manifest.yaml
metrics.csv
events.csv
summary.md
```

## A5 Anticipatory Predictive-Control Smoke

A5 has an explicit bounded single-hive anticipatory predictive-control gate in
`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.
That concise preregistration is the current reference for the explicitly
requested A5 single-hive smoke/scaffold stage. It permits only the existing
deterministic scaffold and read-only residual diagnostics needed for a bounded
smoke/pilot. The prior seed `5,6` smoke result is recorded in
`docs/results/a5_single_hive_reopened_smoke_seed5_6.md`; it remains an
interpretation boundary, not a reason to broaden mechanics. Forecast skill
improved, but residual/null promotion failed. The older detailed design record
remains in
`docs/a5_anticipatory_predictive_control_preregistration.md`. The prior seed
`7..16`, A5.1a accounting closure, and reopened A5 seed `5,6` result all
constrain interpretation: do not make residual-structure, lobe-like, or
strange-attractor-like claims from A5-family artifacts.

The older renewed 2026-06-30 A5 automation directive is no longer the active
scientific line. Ben subsequently selected the analytic delayed-map pivot, not
A5.2. The concise A5 preregistration and scaffold remain negative background
and accounting guardrails only; they do not authorize broad A5 tuning, A5.2
implementation, A7-family mechanics, dashboards, external integrations, or
downstream multi-hive coupling.

The scaffold remains intentionally single-hive and deterministic. It keeps the
existing action set and artifact contract, adds a hidden periodic demand-share
signal over the four attention classes, and lets an opt-in predictive
controller shift work-task class priority from forecasted future pressure. Do
not broaden A5 to new mechanics, wider seed sweeps, dashboards, integrations,
or multi-hive coupling without another preregistration.
The paired A5 comparison now also writes
`predictive_control_accounting_locks.csv` so the matched task stream, demand
stream, service capacity, action opportunity, pre-prediction work opportunity,
and budget-matched null prediction-spend checks are visible before residual
interpretation.
It also writes `predictive_control_design_manifest.yaml`, which records the
fixed A5 condition grid, prediction-budget axis, preregistration pointer,
budget-matched null pairings, oracle-positive-control role, and fail-closed
residual promotion gate for replay/audit. This is an accounting artifact only;
it does not broaden A5 mechanics. The manifest now also records the
lead/signal/phase parameters and the deterministic phase-shifted timing-broken
null controls, making the shuffled/phase-randomized null surface auditable
before residual interpretation. It also maps each preregistered endpoint family
to the concrete comparison or residual-accounting artifacts, fields, endpoint
values, control levels, and null contrasts that would have to support it. The
manifest also makes the resource-bounded prediction axis explicit: reactive is
the zero-budget baseline, intermediate budgets are candidates only after
budget-matched null and accounting checks, and oracle is a smoothing positive
control rather than target dynamics evidence. It also records a
scarce-resource accounting subcontract: inter-agent or inter-role prediction is
the managed resource, useful anticipation must be judged per unit prediction
budget, and charged prediction spend must be represented as explicit transfer
from work opportunity rather than hidden extra capacity. The manifest now
includes a cheap-high-level-regularities contract: any structured residual
pattern is useful only if it gives bounded agents cheaper predictability or
compression than the raw pressure stream after full accounting and matched
surrogate nulls. The manifest also includes a fail-closed decision checklist
that requires every promotion criterion to pass for the same
intermediate-budget condition before any residual-structure or
strange-attractor-like language can be considered. It also includes a
comparison-readiness contract that separates directly auditable comparison
facts from residual-structure claims that remain gated on the read-only
residual-accounting analyzer. It also includes a downstream-extension boundary
that keeps three-hive delayed anticipatory coupling, resource-bounded
cross-hive prediction, and target/phase-shuffled transfer nulls out of scope
until separately preregistered after single-hive A5 evidence passes the
fail-closed accounting and residual gates.
It also records surrogate-null requirements that make the budget-matched null
pairings, preservation targets, timing/target-alignment breaks, future null
families, and matched-surrogate invalidation rule explicit before residual
interpretation.

Broader A5 seed sweeps, new A5 predictor knobs, A5 rescue diagnostics, and A5.2
implementation remain closed. Ben's 2026-06-28 decision opened the A7.2 delayed
artifact-mediated endogenous-prediction direction, now historical:
`docs/a5_family_exit_and_a7_2_decision_preregistration.md`. Ben's 2026-06-29
follow-up opened A7.3 one-hive dimensionless delayed dynamics as later
historical context. The active line is now the analytic delayed-map pivot
described below.

The A5.2 design gate remains preregistered, but not implemented, in
`docs/a5_2_endogenous_delayed_prediction_spend_preregistration.md`. It is not
the current next step.

The current bounded read-only follow-up is preregistered in
`docs/a5_resource_bounded_residual_compression_preregistration.md`. It
authorizes only a residual-compression diagnostic report over existing
A5-family artifacts. It does not authorize new simulator mechanics, new runs,
broader seeds, A7.2 mechanics, or multi-hive coupling.

## Analytic Delayed Resource-Bounded Map

Ben's 2026-06-30 direction selects a minimal analytic delayed-map pivot before
adding more simulator mechanics. The first checked-in sandbox is standalone: it
does not call the OmegaSim agent simulator, A5 helpers, A7 helpers, dashboards,
external integrations, or multi-hive coupling. It exposes the Hyperseed axes
`rho`, `delta`, `mu`, `kappa`, and `nu`, emits deterministic trajectories from
a fixed seed, and writes boundedness, recurrence-vs-shuffled-surrogate, and
paired local-divergence diagnostics.

```bash
python -m ohdyn.analytic_delayed_map \
  --config configs/analytic_delayed_map_smoke.yaml \
  --out runs/analytic_delayed_map_smoke_seed1
```

The smoke fixture is diagnostic only. Passing boundedness or recurrence wiring
does not support lobe-like, semantic-dynamics, or strange-attractor-like
claims.

The bounded grid preflight runs the existing analytic map in memory over the
fixed low/high `rho` x no-delay/delay set and writes only summary diagnostics:

```bash
python -m ohdyn.analytic_delayed_map_grid_preflight \
  --config configs/analytic_delayed_map_grid_preflight.yaml \
  --out runs/analytic_delayed_map_grid_preflight_seed1
```

This preflight reports boundedness, recurrence-surrogate deltas, and paired
local-divergence summaries only. It does not write per-tick simulator metrics
or support attractor, lobe, or semantic-dynamics claims.

The next analytic-map refinement/null gate is preregistered, but not yet
implemented, in
`docs/analytic_delayed_map_refinement_null_gate_preregistration.md`. It freezes
a four-condition standalone sandbox check over active delayed nonlinear,
no-delay, linearized-response, and delay-shuffled-history conditions before any
larger grid. It does not authorize simulator mechanics, A5/A7 reruns,
dashboards, external integrations, broader seeds, multi-hive coupling, or
promotion language.

The checked-in null gate runs those four preregistered conditions and writes
only summary diagnostics plus manifest artifacts:

```bash
python -m ohdyn.analytic_delayed_map_null_gate \
  --config configs/analytic_delayed_map_null_gate.yaml \
  --out runs/analytic_delayed_map_null_gate_seed1
```

It does not write per-tick simulator `metrics.csv` or `events.csv` artifacts.
The seed-1 smoke is diagnostic only; bounded unsaturated active dynamics with
mixed null deltas close the gate conservatively rather than supporting
attractor, lobe, or semantic-dynamics claims.

Because that null gate closed conservatively, the next active analytic-map
design gate is preregistered in
`docs/analytic_micro_society_map_preregistration.md`. It allows only a future
standalone four-state analytic micro-society mechanism screen over artifact
readiness, prediction spend/error, and fatigue/adaptive threshold state. It
does not authorize simulator mechanics, A5/A7 reruns, dashboards, external
integrations, multi-hive coupling, broader sweeps, or promotion language.

The completed A5 follow-up gate is recorded in
`docs/a5_1_prediction_spend_competition_preregistration.md`. A5.1 stayed
single-hive and deterministic, but asked the narrower resource-bounded question
that the first A5 scaffold did not test directly: prediction spend must compete
with work opportunity, with spend-matched timing-broken nulls and full
accounting controls before any residual-structure or strange-attractor-like
language is allowed.

The bounded A5.1a subgate was cost calibration, not seed broadening. It added
explicit prediction-cost scale/cap knobs plus a spend-only replay null that
deducts the same work opportunities at the same ticks while removing useful
forecast timing. It closed fail-closed in
`docs/results/a5_1a_cost_calibration_closure_note_seed5_6.md`.

The checked-in A5.1a scaffold adds `prediction_cost_scale`,
`max_prediction_work_fraction_per_tick`, and generated spend-only replay-null
conditions when the predictive-control comparison helper is run from a
charged-to-work base config:

```bash
python -m ohdyn.compare_predictive_control --base-config configs/a5_1_prediction_spend_linear_smoke.yaml --seeds 5 6 --out runs/a5_1a_cost_calibration_compare_seed5_6
python -m ohdyn.analyze_a5_residual_accounting --compare-dir runs/a5_1a_cost_calibration_compare_seed5_6 --out runs/a5_1a_cost_calibration_residual_accounting_seed5_6
```

The checked-in low-budget linear smoke fixture is:

```bash
python -m ohdyn.run --config configs/a5_predictive_linear_smoke.yaml --seed 5 --out runs/a5_predictive_linear_seed5
```

The checked-in A5.1 prediction-spend smoke fixture enables direct charging of
prediction spend against work opportunity:

```bash
python -m ohdyn.run --config configs/a5_1_prediction_spend_linear_smoke.yaml --seed 5 --out runs/a5_1_prediction_spend_linear_seed5
python -m ohdyn.compare_predictive_control --base-config configs/a5_1_prediction_spend_linear_smoke.yaml --seeds 5 6 --out runs/a5_1_prediction_spend_compare_seed5_6
python -m ohdyn.analyze_a5_residual_accounting --compare-dir runs/a5_1_prediction_spend_compare_seed5_6 --out runs/a5_1_prediction_spend_residual_accounting_seed5_6
```

## A6 Logistic-Appraisal Smoke

A6 was the post-A5 preregistered smoke-scaffold direction, recorded in
`docs/omegasim_provisional_experiment_roadmap.md` and
`docs/a6_logistic_appraisal_attractor_preregistration.md`. The bounded A6.1
source-accounting and pilot/null gates are recorded in
`docs/a6_1_schema_control_addendum.md` and
`docs/a6_1_pilot_null_preregistration.md`. A6 is single-hive only and remains
abstract/numeric: no real LLM calls, Lean, Slack, browser, Atomspace,
dashboard, or downstream multi-hive integration.

The four checked-in smoke fixtures are:

```bash
python -m ohdyn.run --config configs/a6_logistic_appraisal_smoke.yaml --seed 1 --out runs/a6_logistic_appraisal_seed1
python -m ohdyn.run --config configs/a6_linear_appraisal_smoke.yaml --seed 1 --out runs/a6_linear_appraisal_seed1
python -m ohdyn.run --config configs/a6_threshold_shuffled_smoke.yaml --seed 1 --out runs/a6_threshold_shuffled_seed1
python -m ohdyn.run --config configs/a6_phase_shuffled_smoke.yaml --seed 1 --out runs/a6_phase_shuffled_seed1
```

The bounded paired-seed smoke comparison runs only those four fixtures and
writes aggregate artifacts for schema/analyzer exercise, not scientific
promotion:

```bash
python -m ohdyn.compare_a6_logistic_appraisal --seeds 1 2 --out runs/a6_logistic_appraisal_compare
python -m ohdyn.analyze_a6_logistic_appraisal --compare-dir runs/a6_logistic_appraisal_compare --out runs/a6_logistic_appraisal_analysis
```

The comparison directory contains one normal run artifact directory per
condition/seed, `a6_logistic_appraisal_comparison_metrics.csv`,
`a6_logistic_appraisal_effects.csv`, and `summary.md`. The analyzer consumes
those existing artifacts without rerunning simulations, including the A6.1
`a6_logistic_appraisal_source_accounting.csv` schema/control audit when source
fields are present in the run artifacts.

The A6.2 residual-recurrence gate is a read-only analyzer over the existing
A6.1 source-preserving null comparison. It checks source/control field
completeness and emits recurrence/delta status rows; smoke-horizon rows are
expected to fail closed as `insufficient_horizon` rather than support recurrence
claims:

```bash
python -m ohdyn.analyze_a6_2_residual_recurrence \
  --compare-dir runs/a6_1_pilot_null_compare \
  --out runs/a6_2_residual_recurrence_analysis_seed1_2
```

The accepted A6.2 design gate is documented in
`docs/a6_2_long_horizon_validation_preregistration.md`, and the completed
96-tick seed `1..2` result is recorded in
`docs/results/a6_2_long_horizon_validation_seed1_2.md`. The validation used the
same single-hive A6 mechanics and source-preserving null controls and closed
conservatively: source schema and recurrence computation passed, but logistic
did not beat linear and both source-preserving nulls on the same target with
paired cross-seed agreement. It does not authorize broader seeds, new
mechanisms, downstream multi-hive coupling, or promotion language.

The A6.2 closure addendum is recorded in
`docs/results/a6_2_closure_addendum_seed1_2.md`. Ben accepted proceeding to A7
on 2026-06-27. The A7 semantic-field preregistration is documented in
`docs/a7_semantic_field_preregistration.md`; it treats A7 as a new design gate
for source-accounted semantic/artifact fields and logistic inter-agent
dependence, not as a continuation-by-seed-broadening of A6.2.

The A7 implementation contract is frozen in
`ohdyn/a7_semantic_field_contract.py` and `docs/a7_implementation_gate.md`.
The checked-in A7 smoke fixture stubs are config-schema fixtures only; they
load the six preregistered conditions and do not authorize simulator mechanics
or scientific comparisons yet:

```text
configs/a7_logistic_semantic_coupling_smoke.yaml
configs/a7_semantic_off_baseline_smoke.yaml
configs/a7_amplitude_matched_linear_semantic_coupling_smoke.yaml
configs/a7_source_preserving_semantic_label_shuffle_smoke.yaml
configs/a7_semantic_field_phase_shuffle_smoke.yaml
configs/a7_prediction_budget_timing_broken_matched_count_null_smoke.yaml
```

The placeholder comparison scaffold enumerates those six fixtures and paired
seeds, writing normalized generated configs and config/manifest-only run
placeholders. It intentionally does not call the simulator, write metrics or
events, or create A7 scientific evidence:

```bash
python -m ohdyn.compare_a7_semantic_field --seeds 1 2 --out runs/a7_semantic_field_compare
```

The first longer-horizon A7 validation gate is preregistered in
`docs/a7_long_horizon_residual_null_validation_preregistration.md`. It freezes
a bounded 96-tick, seed `1..2`, six-condition residual/null validation over the
existing A7 mechanics and read-only analyzer. It does not authorize new A7
mechanics, broader seeds, parameter sweeps, downstream multi-hive coupling, or
semantic-dynamics promotion language.

The fixed comparison and analysis commands are:

```bash
python -m ohdyn.compare_a7_long_horizon --seeds 1 2 --out runs/a7_long_horizon_compare_seed1_2
python -m ohdyn.analyze_a7_semantic_field --compare-dir runs/a7_long_horizon_compare_seed1_2 --out runs/a7_long_horizon_residual_null_analysis_seed1_2
```

## A7.3 One-Hive Dimensionless Delayed Dynamics Smoke

A7.3 is the fresh one-hive delayed nonlinear dynamics line opened by Ben's
2026-06-29 proceed instruction and preregistered in
`docs/a7_3_one_hive_dimensionless_delayed_dynamics_preregistration.md`. It does
not reopen A5, A7.2, or the three-hive ring as result-bearing lines.

The checked-in A7.3 smoke fixture and helper emit deterministic metrics,
events, source-ledger, and lifted-state rows for the frozen nine-condition,
paired-seed grid. This is an artifact-validity smoke only; it does not compute
promotion endpoints or support strange-attractor-like, lobe-like, or semantic
dynamics claims.

```bash
python -m ohdyn.compare_a7_3_dimensionless_delayed --seeds 1 2 --out runs/a7_3_dimensionless_smoke_seed1_2
python -m ohdyn.analyze_a7_3_preflight --compare-dir runs/a7_3_dimensionless_smoke_seed1_2 --out runs/a7_3_preflight_seed1_2
python -m ohdyn.analyze_a7_3_residual_skeleton --compare-dir runs/a7_3_dimensionless_smoke_seed1_2 --preflight-dir runs/a7_3_preflight_seed1_2 --out runs/a7_3_residual_skeleton_seed1_2
```

The A7.3 preflight analyzer is read-only. It checks condition/seed coverage,
schema completeness, lifted-state availability, source-ledger delay integrity,
boundedness, and productivity guardrails. It does not rerun simulations,
compute promotion endpoints, or create A7.3 scientific evidence.

The A7.3 residual skeleton is also read-only and requires an eligible preflight
manifest. At the fixed 64-tick smoke horizon it records only residual/null
analyzer wiring and remains fail-closed; it does not compute promotion
endpoints or support A7.3 scientific claims.

The next A7.3 gate is preregistered in
`docs/a7_3_long_horizon_residual_recurrence_preregistration.md`. It freezes a
one-hive, fixed `256`-tick, seed `1,2` validation plan with residual targets,
source-ledger prerequisites, recurrence/surrogate/divergence endpoints, all
eight null contrasts, and fail-closed promotion criteria. The checked-in
validation helper emits the fixed 256-tick artifact/preflight input set only;
it does not enable result-bearing recurrence analysis.

```bash
python -m ohdyn.compare_a7_3_dimensionless_delayed --validation --out runs/a7_3_dimensionless_validation_seed1_2
python -m ohdyn.analyze_a7_3_preflight --compare-dir runs/a7_3_dimensionless_validation_seed1_2 --out runs/a7_3_validation_preflight_seed1_2
python -m ohdyn.analyze_a7_3_residual_recurrence --compare-dir runs/a7_3_dimensionless_validation_seed1_2 --preflight-dir runs/a7_3_validation_preflight_seed1_2 --out runs/a7_3_residual_recurrence_validation_seed1_2
```

The A7.3 residual/recurrence analyzer is read-only over the fixed validation
artifacts and requires an eligible preflight manifest. It emits residual,
recurrence, surrogate, local-divergence, null-contrast, gate, manifest, and
summary artifacts. The 2026-06-29 bounded smoke verification stayed
fail-closed: preflight, coverage, and row-count gates passed, but all
preregistered null/divergence promotion gates failed. This does not support
A7.3 promotion, lobe-like, semantic-dynamics, or strange-attractor-like claims.

## Three-Hive Ring Schema And Mechanics Smoke

The post-A7.2 three-hive ring gate is frozen in
`docs/three_hive_ring_preregistration.md`,
`ohdyn/three_hive_ring_contract.py`, and
`configs/three_hive_ring_contract_validation.yaml`. The current checked-in
smoke helper is artifact-only: it loads the frozen contract fixture and emits
per-condition/per-seed config, manifest, metric-schema, event-schema, and
source-ledger-schema artifacts. It does not call the simulator, write
metrics/events, or create three-hive scientific evidence.

```bash
python -m ohdyn.compare_three_hive_ring --seeds 1 2 --out runs/three_hive_ring_schema_smoke_seed1_2
```

The checked-in read-only preflight analyzer inspects those schema/source-ledger
artifacts and fails closed until real simulator metrics/events exist:

```bash
python -m ohdyn.analyze_three_hive_ring_preflight --compare-dir runs/three_hive_ring_schema_smoke_seed1_2 --out runs/three_hive_ring_preflight_seed1_2
```

At the artifact-only stage the expected status is
`fail_closed_no_metrics_events`; this is a schema/source-ledger preflight, not
three-hive scientific evidence.

The bounded mechanics smoke emits deterministic metrics, events, and
source-ledger rows for the same frozen thirteen-condition, paired-seed grid:

```bash
python -m ohdyn.compare_three_hive_ring_mechanics --seeds 1 2 --out runs/three_hive_ring_mechanics_smoke_seed1_2
python -m ohdyn.analyze_three_hive_ring_preflight --compare-dir runs/three_hive_ring_mechanics_smoke_seed1_2 --out runs/three_hive_ring_mechanics_preflight_seed1_2
```

For those mechanics artifacts the preflight status is
`eligible_for_mechanics_gate`, meaning schemas and metrics/events are present.
It is still not a residual/null analyzer and does not create promotion
evidence.

The bounded read-only residual/null analyzer consumes existing mechanics
artifacts, checks source-ledger reconstruction, computes residual preflight
metrics, compares the positive condition against all preregistered nulls, and
applies productivity guardrails:

```bash
python -m ohdyn.analyze_three_hive_ring_residual_null --compare-dir runs/three_hive_ring_mechanics_smoke_seed1_2 --out runs/three_hive_ring_residual_null_analysis_seed1_2
```

The fixed seed `1,2` mechanics smoke closes fail-closed under this analyzer.
Schema/source-ledger reconstruction passes, but productivity guardrails and
null contrasts block promotion. This is not three-hive scientific evidence and
does not support lobe-like, strange-attractor-like, synchrony,
semantic-dynamics, or causal collective-structure claims.

A bounded paired-seed pilot comparison derives matched single-hive configs for
reactive, low-budget linear, medium-budget nonlinear, high-budget nonlinear,
oracle, and budget-matched timing-broken null predictors from the smoke
fixture:

```bash
python -m ohdyn.compare_predictive_control --seeds 5 6 --out runs/a5_predictive_control_compare
```

The comparison directory contains one generated config per condition under
`configs/`, normal run artifact directories for each condition/seed,
`predictive_control_comparison_metrics.csv`, `predictive_control_effects.csv`,
and an aggregate `summary.md`.

For A5 configs, `metrics.csv`, `manifest.yaml`, and `summary.md` add forecast
budget, demand-share, forecast-share, forecast-error, forecast-skill, and
work-allocation alignment fields. Task-arrival totals, service capacity, action
opportunity, and work budget remain governed by the existing baseline knobs so
pilot comparisons can stay matched across preregistered predictor conditions.

Before any broader A5 seed sweep, use
`docs/a5_residual_accounting_diagnostic_design.md` as the minimum read-only
diagnostic design for residual structure, accounting controls, surrogate nulls,
and promotion/closure rules.
`docs/a5_confirmatory_addendum.md` freezes prospective confirmatory guardrail
tolerances and budget-matched timing-broken null requirements for any fresh
larger paired-seed run.
`docs/a5_forecast_skill_residual_gap_diagnostic_plan.md` defines the bounded
read-only follow-up for why the checked-in forecast-skill gains did not survive
full residual accounting.
`docs/a5_post_closure_reopening_gate.md` freezes the conservative A5
interpretation after the seed `7..16` closure and requires a new
preregistration before any future anticipatory-prediction mechanics, broader
seeds, or multi-hive coupling.

The matching read-only analyzer consumes an existing comparison directory
without rerunning simulations:

```bash
python -m ohdyn.analyze_a5_residual_accounting --compare-dir runs/a5_predictive_control_compare --out runs/a5_residual_accounting
```

## Current A0/A1 Baseline

The baseline runner loads one YAML config, creates 15 static OmegaHive-like agents, connects them through one NetworkX bus graph, advances one in-memory task queue for the configured tick count, and writes deterministic artifacts for the supplied seed. The only supported baseline actions are `idle`, `message`, `create_task`, and `work_task`.

The 15 agents cycle through five roles, with three agents per role:

- `coordinator`
- `researcher`
- `architect`
- `implementer`
- `reviewer`

Baseline lobe labels are derived from per-tick queue movement and dominant action counts:

- `backlog_growth`
- `execution`
- `task_generation`
- `coordination`
- `low_activity`

## A2 Attention Allocation Smoke

The first opt-in A2 fixture keeps the A0/A1 agent population, bus graph, actions, and artifact contract, but adds a four-class `attention_policy` section:

```bash
python -m ohdyn.run --config configs/a2_attention_smoke.yaml --seed 1 --out runs/a2_attention_seed1
```

Attention-policy runs assign created tasks to `near_term_external`, `long_term_research`, `internal_improvement`, and `housekeeping`; work selection favors queued classes that are under their target share. `metrics.csv`, `manifest.yaml`, and `summary.md` add per-class queue, completion, queued-age, attention-share, share-deviation, and value-weighted completed-work fields only for configs that enable `attention_policy`.

Attention-policy configs may set `attention_policy.selection_strategy`. The
default `quota_balance` preserves the original soft quota scheduler. The
`random_available` strategy is a preregistered scheduler-mechanism ablation: it
keeps the same task creation process and target shares, but each work action
selects uniformly from the queued tasks available under the run's deterministic
seed. Baseline-share random-available fixtures are checked in at normal, high,
and extreme task-creation pressure:

```bash
python -m ohdyn.run --config configs/a2_attention_random_available.yaml --seed 1 --out runs/a2_attention_random_available_seed1
python -m ohdyn.run --config configs/a2_attention_random_available_high_pressure.yaml --seed 1 --out runs/a2_attention_random_available_high_pressure_seed1
python -m ohdyn.run --config configs/a2_attention_random_available_extreme_pressure.yaml --seed 1 --out runs/a2_attention_random_available_extreme_pressure_seed1
```

Attention-policy metrics also include value-yield fields derived from existing completion counters: `attention_value_per_completed_task_tick` and `attention_value_per_completed_task_total`. These distinguish pressure responses caused by completing more tasks from responses caused by shifting the completed task-class mix toward higher-value classes. To separate that completed-task mix signal from task-work effort, A2 runs also emit per-class cumulative work-event totals plus effort-normalized value fields: `attention_value_per_work_event_tick` and `attention_value_per_work_event_total`.

Attention-policy runs also record deterministic capture-pressure telemetry. Per-class `attention_<class>_capture_pressure_tick` fields report how far each class's queued-task share exceeds its target share at the end of a tick, and `attention_capture_pressure_max_tick` reports the largest per-class pressure. When the selected work class differs from another available class above target share, `events.csv` emits an `attention_capture_pressure` event with the selected class, pressure class, and pressure value. These fields are present only for configs that enable `attention_policy`; A0/A1 configs keep the baseline metrics shape.

A contrasting research-heavy A2 fixture uses the same deterministic baseline with more reserved share for long-term research:

```bash
python -m ohdyn.run --config configs/a2_attention_research_heavy.yaml --seed 1 --out runs/a2_attention_research_heavy_seed1
```

The focused comparison test runs `configs/a2_attention_smoke.yaml` and `configs/a2_attention_research_heavy.yaml` with the same seed and verifies that the research-heavy policy shifts completed work toward `long_term_research` while changing value-weighted throughput and stale-task age.

A contrasting internal-improvement-heavy A2 fixture reserves more share for self-analysis, policy improvement, and capability development:

```bash
python -m ohdyn.run --config configs/a2_attention_internal_improvement.yaml --seed 1 --out runs/a2_attention_internal_improvement_seed1
```

A small deterministic comparison runner executes the smoke, research-heavy, and internal-improvement-heavy A2 fixtures across a short seed set and writes per-run artifacts plus aggregate comparison outputs:

```bash
python -m ohdyn.compare_attention --seeds 1 2 3 --out runs/a2_attention_compare
```

The comparison directory contains `comparison_metrics.csv`, an aggregate `summary.md`, and one normal run artifact directory per policy/seed. The aggregate CSV uses stable run subdirectory names so same-seed comparisons are byte-reproducible across output parent directories. It records value-weighted throughput, queue depth, stale-task age, per-class completed work totals, pipe-delimited per-run trajectory columns for queue depth, queued-task mean age, value-weighted completed work, and each attention class's completed-work totals. It also records pipe-delimited first-difference columns for queue depth, queued-task mean age, and value-weighted completed work so policy summaries can report phase-space step deltas.

The aggregate comparison `summary.md` derives deterministic phase-space regime labels from the signs of each policy's mean queue-depth, queued-age, and value-throughput step deltas, for example `queue_growth+stale_age_rising+value_throughput_rising`. It also counts each per-run step-level regime label from the same delta sign sequence, reports per-policy regime counts and rates, reports each variant policy's regime count/rate distribution deltas versus the baseline policy, and summarizes per-policy regime dwell runs plus turning-point counts. `comparison_metrics.csv` carries the per-run dwell run encoding, longest dwell label/length, turning-point encoding, and turning-point count for downstream trajectory analysis.

Attention comparison rows also carry capture-pressure trajectories from the A2 run metrics. `comparison_metrics.csv` records final, mean-over-ticks, peak, full max-capture-pressure trajectory, first differences, and per-class capture-pressure trajectories. The aggregate comparison `summary.md` reports per-policy capture-pressure final/mean/peak means, capture-pressure step-delta aggregates, and variant deltas versus the baseline policy.

A2 configs may also set `model.task_creation_pressure`, a deterministic scalar applied to the baseline `create_task` action weight. The default is `1.0`, preserving A0/A1 behavior. The checked-in high-pressure fixtures use `1.8` to compare the same policy shares under stronger backlog creation pressure:

The checked-in medium-pressure fixtures use `1.4` to provide a reproducible midpoint between the normal and high-pressure conditions:

```bash
python -m ohdyn.compare_attention \
  --baseline-config configs/a2_attention_medium_pressure.yaml \
  --variant-config configs/a2_attention_research_heavy_medium_pressure.yaml \
  --internal-improvement-config configs/a2_attention_internal_improvement_medium_pressure.yaml \
  --seeds 1 2 3 \
  --out runs/a2_attention_medium_pressure_compare
```

```bash
python -m ohdyn.compare_attention \
  --baseline-config configs/a2_attention_high_pressure.yaml \
  --variant-config configs/a2_attention_research_heavy_high_pressure.yaml \
  --internal-improvement-config configs/a2_attention_internal_improvement_high_pressure.yaml \
  --seeds 1 2 3 \
  --out runs/a2_attention_high_pressure_compare
```

The pressure comparison helper runs the normal, medium, and high-pressure policy sets together, preserving the per-condition comparison artifacts while adding fixed-policy high-minus-normal pressure deltas and pressure-curve slope/curvature metrics:

```bash
python -m ohdyn.compare_pressure --seeds 1 2 3 --out runs/a2_attention_pressure_compare
```

The output directory contains `normal_pressure/`, `medium_pressure/`, `high_pressure/`, `pressure_comparison_metrics.csv`, `pressure_response_selection.csv`, `pressure_stability_agreement.csv`, `pressure_stability_convergence.csv`, `pressure_trajectory_structure.csv`, and a top-level `summary.md`. The three pressure-condition subdirectories are ordinary `ohdyn.compare_attention` outputs with their own `comparison_metrics.csv`, aggregate `summary.md`, and per-policy/per-seed run artifact directories.

For an extreme-pressure extension, keep the normal-pressure fixtures at `1.0`,
reuse the checked-in high-pressure fixtures as the middle endpoint at `1.8`,
and use the extreme-pressure fixtures as the high endpoint at `2.2`:

```bash
python -m ohdyn.compare_pressure \
  --medium-pressure-baseline-config configs/a2_attention_high_pressure.yaml \
  --medium-pressure-variant-config configs/a2_attention_research_heavy_high_pressure.yaml \
  --medium-pressure-internal-improvement-config configs/a2_attention_internal_improvement_high_pressure.yaml \
  --high-pressure-baseline-config configs/a2_attention_extreme_pressure.yaml \
  --high-pressure-variant-config configs/a2_attention_research_heavy_extreme_pressure.yaml \
  --high-pressure-internal-improvement-config configs/a2_attention_internal_improvement_extreme_pressure.yaml \
  --seeds 1 2 3 \
  --out runs/a2_attention_extreme_pressure_compare
```

Pressure-curve slopes are computed from the actual `model.task_creation_pressure`
values loaded from the three condition config sets, so custom pressure endpoints
remain numerically meaningful as long as the normal, medium, and high condition
pressures are strictly increasing and each policy config within a condition uses
the same pressure value.

## Demand vs Service-Capacity Preregistration

A2 configs may also set `model.work_service_capacity`, a deterministic scalar
applied to the baseline `work_task` action weight. The default is `1.0`,
preserving earlier A0/A1 and A2 behavior. This knob is intended for the next
mechanism-discriminating ablation: keep baseline attention shares and
`quota_balance`, cross creation pressure (`1.0`, `1.8`, `2.2`) with service
capacity (`0.7`, `1.0`, `1.3`), and treat raw queue depth as load accounting
rather than the primary emergent-dynamics endpoint.

The checked-in endpoint fixtures are:

```bash
python -m ohdyn.run --config configs/a2_attention_low_service_capacity.yaml --seed 1 --out runs/a2_attention_low_service_capacity_seed1
python -m ohdyn.run --config configs/a2_attention_high_service_capacity.yaml --seed 1 --out runs/a2_attention_high_service_capacity_seed1
python -m ohdyn.run --config configs/a2_attention_low_service_capacity_high_pressure.yaml --seed 1 --out runs/a2_attention_low_service_capacity_high_pressure_seed1
python -m ohdyn.run --config configs/a2_attention_high_service_capacity_high_pressure.yaml --seed 1 --out runs/a2_attention_high_service_capacity_high_pressure_seed1
python -m ohdyn.run --config configs/a2_attention_low_service_capacity_extreme_pressure.yaml --seed 1 --out runs/a2_attention_low_service_capacity_extreme_pressure_seed1
python -m ohdyn.run --config configs/a2_attention_high_service_capacity_extreme_pressure.yaml --seed 1 --out runs/a2_attention_high_service_capacity_extreme_pressure_seed1
```

Use the existing baseline-share configs as the middle service-capacity row:
`configs/a2_attention_smoke.yaml`, `configs/a2_attention_high_pressure.yaml`,
and `configs/a2_attention_extreme_pressure.yaml`. Primary outcomes for this
ablation are load-normalized backlog, queued age, value per work event, capture
pressure, and lobe transition/dwell summaries.

The checked-in service-capacity comparison helper runs that 3x3 grid directly:

```bash
python -m ohdyn.compare_service_capacity \
  --seeds 1 2 3 \
  --out runs/a2_service_capacity_compare
```

The output directory contains one normal run artifact directory for each
pressure/service/seed cell, `service_capacity_comparison_metrics.csv`,
`service_capacity_effects.csv`, and a top-level `summary.md`. The aggregate CSV
has one row per pressure/service cell and reports task creation/completion
totals, completion fraction, created-completed balance, queue depth normalized
by created tasks and by created-completed balance, queued-age summaries, value
per work event, capture pressure, and baseline lobe transition/dwell summaries.
The effect CSV reports high-minus-low service-capacity deltas at fixed pressure
and extreme-minus-normal pressure deltas at fixed service capacity for the
load-normalized backlog, age, value-efficiency, capture-pressure, and
lobe-transition/dwell fields. The helper validates that pressure increases
across the three pressure rows, service capacity increases across the three
service columns, every pressure row uses the same service-capacity axis, and
every config uses baseline attention shares with the `quota_balance` scheduler.

The service-capacity trajectory analyzer reads an existing comparison directory
without rerunning the grid and computes transition-entropy plus dwell
distribution summaries from each run's baseline lobe labels:

```bash
python -m ohdyn.analyze_service_capacity_trajectory \
  --service-capacity-dir runs/a2_service_capacity_compare \
  --out runs/a2_service_capacity_trajectory_analysis
```

The output directory contains `service_capacity_trajectory_metrics.csv`,
`service_capacity_trajectory_effects.csv`, and `summary.md`. The metrics CSV
joins each pressure/service cell's load-normalized backlog and final queued age
to transition count, transition entropy, normalized transition entropy, dwell
run count, mean and max dwell length, backlog-growth dwell share, dominant lobe
counts, transition-pair counts, and dwell-length histograms. The effect CSV
reports high-minus-low service-capacity deltas at fixed pressure and
extreme-minus-normal pressure deltas at fixed service capacity for
load-normalized backlog, queued age, transition entropy, dwell lengths, and
backlog-growth dwell share. Use this analysis to distinguish load accounting
from pressure-induced regime locking before adding another experiment.

The queue-blind lobe analyzer reads the same existing comparison directory and
relabels each tick from action counts only: `tasks_worked_tick`,
`tasks_created_tick`, `messages_sent_tick`, and `idle_tick`. It excludes
`queue_depth`, `queue_delta_tick`, and the queue-derived `baseline_lobe_label`,
then reports transition entropy, dwell summaries, task-generation share, and
execution share:

```bash
python -m ohdyn.analyze_queue_blind_lobes \
  --service-capacity-dir runs/a2_service_capacity_compare \
  --out runs/a2_queue_blind_lobes
```

Use this as an analysis-only robustness check for whether pressure structure
survives outside the default queue-derived lobe labeler; do not promote it to a
replacement lobe architecture without a preregistered follow-up.

The A2 exogenous-arrival decoupling experiment was preregistered in
`docs/a2_exogenous_arrival_decoupling_preregistration.md` and has now been
completed by the seed `70..99` decision synthesis below. It decoupled task
arrivals from agent `create_task` action pressure by adding opt-in exogenous
arrivals while holding `model.task_creation_pressure` fixed. Its purpose was to
decide whether the remaining pressure-induced trajectory locking signal was
load accounting, action-budget coupling, or a residual lobe-dynamics effect.

The completed calibration step selected opt-in exogenous arrival rates against
existing coupled-pressure created-task totals using load/accounting fields only:

```bash
python -m ohdyn.calibrate_exogenous_arrivals \
  --candidate-rates 0.0 0.5 1.0 1.5 2.0 2.5 3.0 \
  --seeds 1 2 3 \
  --out runs/a2_exogenous_arrival_calibration
```

The calibration output contains per-target and per-candidate run artifacts,
`exogenous_arrival_calibration.csv`, and `summary.md`. The report intentionally
does not use lobe, entropy, or value outcomes to choose rates; those outcomes
belong to the later frozen-rate holdout.

The provisional frozen exogenous-arrival fixtures selected by the seed `1..3`
calibration are checked in as low/medium/high rates `1.0`, `2.0`, and `3.0`:

```bash
python -m ohdyn.run --config configs/a2_exogenous_arrivals_low.yaml --seed 1 --out runs/a2_exogenous_arrivals_low_seed1
python -m ohdyn.run --config configs/a2_exogenous_arrivals_medium.yaml --seed 1 --out runs/a2_exogenous_arrivals_medium_seed1
python -m ohdyn.run --config configs/a2_exogenous_arrivals_high.yaml --seed 1 --out runs/a2_exogenous_arrivals_high_seed1
```

The bounded comparison scaffold runs the endogenous control plus the three
frozen exogenous-arrival fixtures while holding `model.task_creation_pressure:
1.0`, baseline attention shares, `quota_balance`, and baseline service capacity:

```bash
python -m ohdyn.compare_exogenous_arrivals \
  --seeds 1 2 3 \
  --out runs/a2_exogenous_arrival_compare
```

The output directory contains one normal run artifact directory per
condition/seed, `exogenous_arrival_comparison_metrics.csv`,
`exogenous_arrival_effects.csv`, and `summary.md`. The aggregate metrics report
agent-created tasks separately from exogenous arrivals, total created/completed
tasks, action counts, load-normalized backlog, queued age, value per work
event, capture pressure, baseline lobe entropy/dwell fields, and queue-blind
action-only lobe summaries using `agent_tasks_created_tick` when present. The
effect CSV reports each exogenous condition minus the endogenous control. Treat
this helper as the frozen-rate holdout scaffold; do not interpret tiny smoke
seed outputs as lobe-dynamics evidence.

The seed `70..99` exogenous-arrival decision synthesis freezes the current A2
interpretation:

```text
docs/results/a2_exogenous_arrival_decision_synthesis_seed70_99.md
```

The high exogenous-arrival holdout raises total created tasks while holding
agent `task_creation_pressure` fixed, and it supports robust load/accounting
effects plus action-budget-mediated trajectory effects. It does not support an
independent residual lobe-grammar claim under the current simulator and label
scheme. Do not extend A2 with broad residual-lobe sweeps or new simulator
mechanisms unless a concrete artifact bug is found. Any next-stage experiment
should be preregistered around queue-flow balance, service capacity,
load-normalized backlog, queued-task age, action/work-opportunity accounting,
and, only after explicit preregistration, service/queue-flow synchronization
endpoints.

The next-stage queue-flow/service-capacity preregistration is:

```text
docs/a3_queue_flow_service_preregistration.md
```

It keeps A2 frozen as a load/action-accounting dominated result and restricts
new work to deterministic queue-flow, service-capacity, load-normalized
backlog, queued-age, completion-fraction, action/work-opportunity accounting,
and explicitly preregistered synchronization endpoints.

The first A3 analysis-only artifact reader consumes existing A2
service-capacity and exogenous-arrival comparison directories and writes
queue-flow/service metrics, effect deltas, and a summary without rerunning
simulations:

```bash
python -m ohdyn.analyze_queue_flow_service \
  --service-capacity-dir runs/a2_service_capacity_holdout_seed70_99_20260624 \
  --exogenous-arrival-dir runs/a2_exogenous_arrival_holdout_seed70_99_20260625_v2 \
  --out runs/a3_queue_flow_service_analysis_seed70_99_20260625
```

The output directory contains `queue_flow_service_metrics.csv`,
`queue_flow_service_effects.csv`, and `summary.md`. The metrics CSV reports
load-normalized backlog, completion fraction, queued age, action/work-event
accounting, per-run service-opportunity/completion correlation, and
created-completed-flow/queue-delta correlation for each reused condition. The
effect CSV reports high-minus-low service-capacity, extreme-minus-normal demand
pressure, and exogenous-minus-endogenous demand deltas. These A3 fields are
primary queue-flow/service endpoints; baseline and queue-blind lobe summaries
remain secondary diagnostics only.

The lagged synchronization reader is the preregistered A3 analysis-only check
that separates primary lagged service/queue-flow endpoints from the same-tick
flow-balance identity diagnostic:

```bash
python -m ohdyn.analyze_lagged_service_sync \
  --service-capacity-dir runs/a2_service_capacity_holdout_seed70_99_20260624 \
  --exogenous-arrival-dir runs/a2_exogenous_arrival_holdout_seed70_99_20260625_v2 \
  --out runs/a3_lagged_service_sync_seed70_99_20260625
```

The output directory contains `lagged_service_sync_metrics.csv`,
`lagged_service_sync_effects.csv`, and `summary.md`. The primary endpoints are
lagged service/completion and service/load-change correlations at lag `-1` or
`+1`; the same-tick created-completed balance versus queue-delta correlation is
retained only as an artifact identity diagnostic and is excluded from the
primary synchronization interpretation. The effect CSV also reports paired
seed-count, seed-median delta, deterministic bootstrap median CI, and raw
paired-seed sign stability for both lagged endpoints. Those uncertainty fields
are required guardrails: best-lag effects remain descriptive unless they show
strong seed-level support or are replaced by a preregistered causal lag
direction.

The A3 queue-flow/service synthesis freezes the seed `70..99` interpretation:

```text
docs/results/a3_queue_flow_service_synthesis_seed70_99.md
```

It combines the queue-flow/service and lagged synchronization artifacts,
classifies the claims as load accounting, service-capacity response,
work-opportunity accounting, modest synchronization diagnostics, and unsupported
residual lobe grammar, and records seed-level uncertainty caveats for the
lagged endpoints. Any later multi-hive preregistration should use
queue-flow/service synchronization endpoints as primary and keep lobe labels
secondary unless a genuinely non-queue, non-action-derived observable is added.

The next-stage multi-hive study plan is preregistered here:

```text
docs/a4_multihive_queue_flow_service_preregistration.md
```

External review has approved only the bounded A4 smoke-contract implementation,
not A4 holdout runs. The checked-in A4 smoke fixtures keep multi-hive behavior
opt-in through YAML. Absence of `hives` preserves the single-hive A0/A1 path.
The inert two-hive control plus direct, delayed, and shuffled transfer smokes
can be run with:

```bash
python -m ohdyn.run --config configs/a4_two_hive_none_smoke.yaml --seed 1 --out runs/a4_two_hive_none_seed1
python -m ohdyn.run --config configs/a4_two_hive_direct_smoke.yaml --seed 1 --out runs/a4_two_hive_direct_seed1
python -m ohdyn.run --config configs/a4_two_hive_delayed_smoke.yaml --seed 1 --out runs/a4_two_hive_delayed_seed1
python -m ohdyn.run --config configs/a4_two_hive_shuffled_smoke.yaml --seed 1 --out runs/a4_two_hive_shuffled_seed1
```

The direct smoke records deterministic coupling decisions in
`coupling_events.csv`; the delayed smoke preserves task provenance but delivers
accepted transfers exactly two ticks after the decision tick. The shuffled
smoke uses the coupling RNG stream for target assignment while preserving the
same deterministic source-hive opportunity counts and transfer-attempt counts
as the paired direct two-hive smoke. Because this first smoke has only two
hives, target assignment is structurally equivalent to the only non-source
hive; treat it as a schema and conservation control, not as a phase-structure
null. Coupled fixtures emit per-hive transfer accounting fields in
`hive_metrics.csv` and check aggregate transfer conservation through
`cross_hive_metrics.csv`. A4 analysis scripts and scientific holdout seeds
remain deferred until the smoke contract is stable.

The A4 smoke-contract preflight analyzer runs the four two-hive smoke fixtures
with a bounded smoke seed, validates artifact presence, same-seed
reproducibility, manifest/config provenance, stable CSV schemas, per-hive
queue-flow conservation, aggregate transfer conservation including delayed
pending deliveries, mode-specific coupling semantics, and dry-run endpoint
computability. It emits a readiness report without running A4 holdout seeds:

```bash
python -m ohdyn.analyze_a4_smoke_contract \
  --out docs/results/a4_smoke_contract_preflight.md
```

The current committed report is:

```text
docs/results/a4_smoke_contract_preflight.md
```

It passes all four smoke modes and preserves the two-hive shuffled limitation:
the shuffled fixture is a schema/conservation control, not a meaningful
phase-structure null.

The exact seed `100..129` A4 holdout command/config bundle has been drafted for
review without running holdout seeds:

```text
docs/results/a4_holdout_command_bundle_seed100_129.md
```

The bundle introduces reviewed-only holdout configs for `none`, `direct`,
`delayed`, and `shuffled`, all using the same two-hive contract with 100 ticks.
It keeps `transfer_probability: 1.0` for the first coupled holdout to avoid the
current probabilistic-transfer RNG-stream confound and continues to treat
two-hive shuffled as a schema/conservation control rather than a meaningful
phase-structure null.

The read-only A4 holdout analyzer consumes an existing paired-seed output root
and emits endpoint/effect tables without running any holdout seeds:

```bash
python -m ohdyn.analyze_a4_holdout \
  --holdout-dir runs/a4_two_hive_holdout_seed100_129 \
  --out-dir runs/a4_two_hive_holdout_seed100_129_analysis \
  --seeds 100..129
```

The analyzer writes `a4_holdout_hive_endpoints.csv`,
`a4_holdout_cross_hive_endpoints.csv`, `a4_holdout_effects.csv`, and
`summary.md`. The effect table covers `direct-minus-none`,
`delayed-minus-none`, `shuffled-minus-none`, and `direct-minus-shuffled`; the
last contrast keeps the documented two-hive shuffled caveat.

The preregistered A4 delayed-coupling temporal null analyzer reads the same
existing holdout artifacts and constructs deterministic circular block shifts
of one hive trajectory relative to the other. It does not run simulations or
rewrite holdout artifacts:

```bash
python -m ohdyn.analyze_a4_delayed_null \
  --holdout-dir runs/a4_two_hive_holdout_seed100_129 \
  --out-dir runs/a4_delayed_coupling_null_seed100_129 \
  --doc-out docs/results/a4_delayed_coupling_null_seed100_129.md \
  --seeds 100..129
```

The analyzer writes `a4_delayed_null_endpoints.csv`,
`a4_delayed_null_effects.csv`, `a4_delayed_null_manifest.csv`, and
`summary.md`. The default circular-shift block sizes are `5`, `10`, and `20`
ticks; offsets exclude `0` and the configured causal delay. Treat surviving
null-centered delayed endpoints as follow-up synchronization diagnostics only,
not as independent lobe-grammar or multi-hive phase-control evidence.

The read-only A4 accounting-control analyzer tests that delayed completion
synchrony diagnostic without new simulator runs. It residualizes per-hive
completion-fraction trajectories by preregistered clock, opportunity/load,
transfer-timing, combined non-tautological, and identity-inclusive covariate
groups, then recomputes the same circular-shift temporal null:

```bash
python -m ohdyn.analyze_a4_accounting_controls \
  --holdout-dir runs/a4_two_hive_holdout_seed100_129 \
  --out-dir runs/a4_accounting_control_seed100_129 \
  --doc-out docs/results/a4_accounting_control_seed100_129.md \
  --seeds 100..129
```

The analyzer writes `a4_accounting_control_endpoints.csv`,
`a4_accounting_control_effects.csv`, `a4_accounting_control_manifest.csv`, and
`summary.md`. The committed seed `100..129` summary closes the delayed
completion-fraction residual conservatively: the raw and clock-only endpoints
survive the temporal null, but the opportunity/load and combined
non-tautological controls move both lag endpoints inside the residualized null,
so A4 should remain a queue-flow/service and action-opportunity accounting
result plus a documented delayed synchronization diagnostic.

`pressure_comparison_metrics.csv` has one row per fixed policy and records high-pressure minus normal-pressure deltas:

- `policy`, the fixed policy being compared across pressure conditions.
- `normal_total_steps`, `medium_pressure_total_steps`, and `high_pressure_total_steps`, the number of phase-space first-difference steps available for the policy in each condition.
- `regime_rate_deltas`, pipe-delimited `regime:delta` entries for high-minus-normal step-regime rates.
- `regime_count_deltas`, pipe-delimited `regime:delta` entries for high-minus-normal step-regime counts.
- `value_weighted_completed_mean_delta`, mean final value-weighted completed-work delta across seeds.
- `value_per_completed_task_mean_delta`, mean final value yield per completed task delta across seeds.
- `value_per_work_event_mean_delta`, mean final value yield per task-work event delta across seeds.
- `tasks_completed_mean_delta`, mean final completed-task delta across seeds.
- `queue_depth_mean_delta`, mean final queue-depth delta across seeds.
- `queued_task_age_mean_final_delta`, mean final queued-task mean-age delta across seeds.
- `queued_task_age_mean_over_ticks_delta`, mean over-ticks queued-task mean-age delta across seeds.
- `queued_task_age_max_peak_delta`, mean peak queued-task max-age delta across seeds.
- `attention_capture_pressure_max_final_delta`, mean final max capture-pressure delta across seeds.
- `attention_capture_pressure_mean_over_ticks_delta`, mean over-ticks max capture-pressure delta across seeds.
- `attention_capture_pressure_peak_delta`, mean peak max capture-pressure delta across seeds.
- Per-class capture-pressure final, mean-over-ticks, and peak high-minus-normal deltas for each attention class.
- Per-policy normal-to-medium slope, medium-to-high slope, and high-interval-minus-low-interval curvature fields for value-weighted completed work, completed tasks, final queue depth, final queued-task mean age, peak queued-task max age, final max capture pressure, mean max capture pressure, and peak max capture pressure.
- Per-policy normal-to-medium slope, medium-to-high slope, and high-interval-minus-low-interval curvature fields for value yield per completed task and value yield per task-work event.
- Per-class capture-pressure normal-to-medium slope, medium-to-high slope, and high-interval-minus-low-interval curvature fields for final, mean-over-ticks, and peak capture pressure.

The pressure comparison `summary.md` reports the normal, medium, and high-pressure config paths, seed set, policy-row count, a `Fixed-policy pressure deltas` section, a `Most pressure-sensitive curve metric` section, a `Pressure-curve response ranking` section, a `Top pressure-response explanation` section, a `Pressure-response interpretation` section, a `Value throughput vs effort interpretation` section, a `Pressure-condition source metric comparison` section, a `Per-class capture-pressure prefix comparison` section, a `Pressure-response stability agreement` section, a `Pressure-stability convergence inspection` section, a `Seed-set sensitivity` section, and a `Fixed-policy pressure curves` section. The sensitivity section identifies the policy/observable pair with the largest absolute slope or curvature response from the existing pressure-curve fields, including capture-pressure observables. The ranking section sorts every policy/observable pressure-curve response by absolute magnitude, the explanation section reports the top-ranked response's condition means, slopes, curvature, and high-minus-normal delta, the interpretation section turns the leading full-seed response into a compact deterministic reading and notes whether the last checked prefix selects the same response, the value-throughput section contrasts raw value-weighted throughput against value per completed task and value per task-work event for each fixed policy, the source-metric comparison section reports the normal/medium/high per-seed values and aggregate range for the source metric behind the selected top pressure response, and the curves section reports the same slope and curvature fields emitted in `pressure_comparison_metrics.csv`.

The pressure comparison summary also includes a `Pressure-condition trajectory structure` section. It reuses the per-run phase-space dwell and turning fields from each normal, medium, and high-pressure comparison artifact to report fixed-policy turning-point means, longest-dwell means, high-minus-normal trajectory-structure deltas, and longest-dwell label counts across pressure conditions.

`pressure_trajectory_structure.csv` is the machine-readable companion for the `Pressure-condition trajectory structure` summary section. It has one row per fixed policy and records normal, medium-pressure, and high-pressure turning-point means, longest-dwell-step means, high-minus-normal deltas for both trajectory-structure observables, and pipe-delimited longest-dwell label counts for each pressure condition.

For downstream analysis, treat `policy` as the stable join key between `pressure_comparison_metrics.csv` and `pressure_trajectory_structure.csv`. Use `pressure_comparison_metrics.csv` for pressure-response magnitudes, slopes, curvature, queue depth, throughput, stale-task age, and capture-pressure observables; use `pressure_trajectory_structure.csv` for the matching fixed policy's phase-space turning-point and longest-dwell summaries. Both files are deterministic for the configured seed set, so a reproducible analysis can load the two CSVs directly after the documented `python -m ohdyn.compare_pressure ...` run without parsing `summary.md`.

The checked-in pressure analysis helper reads that CSV pair and emits a compact deterministic pressure-response ranking annotated with each policy's trajectory-structure deltas:

```bash
python -m ohdyn.analyze_pressure \
  --pressure-dir runs/a2_attention_pressure_compare \
  --out runs/a2_attention_pressure_analysis \
  --limit 10 \
  --bootstrap-resamples 200 \
  --bootstrap-seed 1
```

The output directory contains `trajectory_pressure_ranking.csv`, `value_yield_divergence_ranking.csv`, `value_yield_divergence_stability.csv`, `pressure_bootstrap_rank_stability.csv`, `interpretation.csv`, and `summary.md`. The trajectory ranking uses `pressure_comparison_metrics.csv` for pressure-response slopes/curvature and `pressure_trajectory_structure.csv` for same-policy turning-point and longest-dwell high-minus-normal deltas, joined by `policy`. The value-yield divergence ranking uses `pressure_comparison_metrics.csv` only and ranks fixed policies by the absolute gap between pressure effects on value per completed task and value per task-work event, across high-minus-normal deltas, pressure slopes, and pressure curvature.

The analysis helper also writes `interpretation.csv`, a one-row machine-readable companion for downstream tools that need the selected top divergence, prefix-stability verdict, and top trajectory-pressure response without parsing `summary.md`.

The analysis summary includes a deterministic interpretation of the top value-yield divergence row. It reports the selected policy and pressure metric, then distinguishes true opposite-sign completion-vs-effort tradeoffs from same-direction yield shifts whose main signal is a magnitude gap between completion-normalized and effort-normalized yield.

`value_yield_divergence_stability.csv` is a seed-prefix stability companion for the top divergence interpretation. It reads the per-seed `comparison_metrics.csv` files under `normal_pressure/`, `medium_pressure/`, and `high_pressure/`, recomputes pressure rows for each proper seed prefix, and records whether each prefix selects the same top divergence policy and pressure metric as the full seed set. The analysis summary's `Value-yield divergence prefix stability` section reports the full seed set, last prefix, last-prefix stability, all-prefix stability, instability causes, and one row per proper seed prefix.

`pressure_bootstrap_rank_stability.csv` is a deterministic seed-level bootstrap companion. It resamples the per-seed pressure comparison rows with replacement using `--bootstrap-seed`, recomputes pressure rows for each resample, and reports top-selection probabilities plus sign-stability probabilities for three scopes: the global pressure-response ranking, class-specific capture-pressure ranking, and value-yield divergence ranking. This complements ordered-prefix stability because it does not depend on the original seed order.

The analysis helper validates its input artifacts before writing outputs. `pressure_comparison_metrics.csv` must contain the full pressure-comparison schema, `pressure_trajectory_structure.csv` must contain the full trajectory-structure schema, and the two files must have the same policy set with no blank or duplicate policy keys. The pressure directory must also contain the three per-condition comparison artifacts used for prefix and bootstrap stability: `normal_pressure/comparison_metrics.csv`, `medium_pressure/comparison_metrics.csv`, and `high_pressure/comparison_metrics.csv`. `--limit` and `--bootstrap-resamples` must be positive integers, and `--bootstrap-seed` must be an integer. The output directory is append-safe: `ohdyn.analyze_pressure` refuses to run if `trajectory_pressure_ranking.csv`, `value_yield_divergence_ranking.csv`, `value_yield_divergence_stability.csv`, `pressure_bootstrap_rank_stability.csv`, `interpretation.csv`, or `summary.md` already exists. Missing inputs, malformed schemas, policy mismatches, invalid limits, and output collisions fail before creating partial analysis artifacts or modifying preexisting analysis files.

The pressure comparison summary also includes a `Per-class capture-pressure interpretation` section. It filters the same deterministic pressure-response ranking down to individual attention-class capture-pressure observables, reports the strongest overall class-specific response, and then reports the strongest class-specific response for each fixed policy with condition means, slopes, curvature, and high-minus-normal delta.

`Per-class capture-pressure prefix comparison` applies the same seed-prefix stability check to the class-specific pressure-response ranking only. It reports the full seed set's strongest class-specific capture-pressure response, the last proper prefix's strongest class-specific response, whether the class top response is stable for the last prefix and across all prefixes, prefix instability causes, and one table row for every proper seed prefix.

`Pressure-response stability agreement` compares global top-response prefix stability with class-specific capture-pressure prefix stability. It reports whether the last prefix and all proper prefixes stabilize together, then emits one row per prefix with the global stability flag, class-specific stability flag, combined agreement flag, and both instability-cause fields.

`pressure_response_selection.csv` is a companion machine-readable artifact for the top response selected by the same deterministic ranking used in `summary.md`. It has one `full` row for the configured full seed set and one `prefix` row for each proper seed prefix. It also has one `class_full` row and one `class_prefix` row for each proper seed prefix, filtered to individual attention-class capture-pressure observables. Each row records the selected policy, observable, metric, source field, signed and absolute response value, condition means, pressure slopes, curvature, high-minus-normal delta, and whether that prefix selected the same top response as the matching full-seed selection. It also records the selected source metric's normal, medium, and high-pressure mean/min/max plus pipe-delimited per-seed values, matching the `Pressure-condition source metric comparison` summary section without requiring Markdown parsing.

`pressure_stability_agreement.csv` is the machine-readable companion for the `Pressure-response stability agreement` summary section. It has one row per proper seed prefix and records the full seed set, prefix seed set, global stability flag, class-specific stability flag, combined agreement flag, both instability-cause fields, and the selected global/class policy, observable, metric, and source field for that prefix.

`pressure_stability_convergence.csv` is a one-row inspection artifact derived from the stability agreement rows. It records the full seed set, number of proper prefixes inspected, how many prefixes stabilize the global top response, how many stabilize the class-specific capture-pressure top response, how many prefixes have matching stability state, how many stabilize both rankings, the first prefix for each convergence condition, and the last prefix's global/class/stable-together/both-stable state. The summary's convergence inspection also contrasts the first globally stable prefix against the full-seed top response selected in `Pressure-response interpretation`.

`Pressure-response interpretation` restates the full seed set's largest absolute pressure response as one sentence with the selected policy, observable, slope-or-curvature metric, normal/medium/high condition means, both pressure slopes, curvature, and high-minus-normal delta. When at least two seeds are configured, the section also compares the last proper prefix against the full seed set. Stable prefixes report that the leading explanation is stable for the checked prefix; unstable prefixes report the changed dimensions through `instability causes`, the prefix seed set, the prefix-selected policy/observable/metric, and that prefix response's same curve values.

`Seed-set sensitivity` is a deterministic prefix check over the already-generated per-seed comparison rows. For a run with `--seeds 1 2 3`, `full_seeds` is `1,2,3` and `prefix_seeds` is `1,2`; the summary recomputes pressure rows for the prefix subset and compares its top-ranked pressure response with the full seed set's top response. The section also reports a prefix table for every proper prefix of the configured seed set, such as `1` and `1,2`, so the top pressure-response ordering can be inspected as seeds accumulate. `top response stable across prefix: true` means the same policy, observable, and slope-or-curvature metric won under both seed sets. `top response stable across all prefixes: true` means every proper prefix selected the same top response as the full seed set. `false` means the current top response depends on the seed set, so the pressure-response ranking should be treated as seed-set-sensitive rather than as a stable ordering.

When a prefix ranking is unstable, `prefix instability causes` reports which top-response dimensions changed relative to the full seed set: `policy`, `observable`, `metric`, or a comma-separated combination. `metric` means the winning pressure-curve measure changed between a slope and curvature field, or between the normal-to-medium and medium-to-high slope fields. Stable prefix rows report `none`.

## Output Schema

Every run writes `config.yaml`, a normalized copy of the loaded config. Optional artifact flags in the config control the remaining outputs.

The `outputs` section may disable any optional artifact:

```yaml
outputs:
  write_manifest: false
  write_metrics: false
  write_events: false
  write_summary: false
```

With all optional outputs disabled, the run still simulates normally and writes only `config.yaml`. Output directories are append-safe: a run refuses to start when any artifact it would write already exists. Disabled artifacts are ignored for collision checks and are preserved byte-for-byte, so stale or sentinel `manifest.yaml`, `metrics.csv`, `events.csv`, or `summary.md` files do not block a config-only run. The mandatory `config.yaml` always participates in collision checks and blocks reruns into the same directory.

The checked-in config-only fixture can be exercised with:

```bash
python -m ohdyn.run --config configs/a0_config_only.yaml --seed 1 --out runs/a0_config_only_seed1
```

The checked-in default-output fixture omits the optional `outputs` section and therefore normalizes to all artifacts enabled:

```bash
python -m ohdyn.run --config configs/a0_default_outputs.yaml --seed 1 --out runs/a0_default_outputs_seed1
```

The checked-in config-only reordered-actions fixture writes only normalized config provenance while preserving YAML action order:

```bash
python -m ohdyn.run --config configs/a0_config_only_reordered_actions.yaml --seed 1 --out runs/a0_config_only_reordered_actions_seed1
```

The checked-in manifest-only fixture disables metrics, events, and summary output while preserving manifest provenance:

```bash
python -m ohdyn.run --config configs/a0_manifest_only.yaml --seed 1 --out runs/a0_manifest_only_seed1
```

The checked-in manifest-only reordered-actions fixture preserves manifest schema/order provenance without writing metrics, events, or summary output:

```bash
python -m ohdyn.run --config configs/a0_manifest_only_reordered_actions.yaml --seed 1 --out runs/a0_manifest_only_reordered_actions_seed1
```

The checked-in no-manifest fixture writes metrics, events, and summary output without manifest provenance:

```bash
python -m ohdyn.run --config configs/a0_no_manifest.yaml --seed 1 --out runs/a0_no_manifest_seed1
```

The checked-in no-manifest reordered-actions fixture combines disabled manifest output with non-default action order:

```bash
python -m ohdyn.run --config configs/a0_no_manifest_reordered_actions.yaml --seed 1 --out runs/a0_no_manifest_reordered_actions_seed1
```

This fixture is the current smoke path for replaying lobe state without manifest provenance: use the normalized `config.yaml` for ticks/actions and `events.csv` for per-tick action/task lifecycle replay, then compare reconstructed lobe labels, transitions, dwell runs, queue aggregates, and role/action totals against `metrics.csv` and `summary.md`.

The checked-in reordered-actions fixture keeps the same baseline action vocabulary but uses YAML-defined non-default action order:

```bash
python -m ohdyn.run --config configs/a0_reordered_actions.yaml --seed 1 --out runs/a0_reordered_actions_seed1
```

This fixture protects the schema-alignment invariant that normalized `config.yaml`, manifest `actions`, manifest metrics schema, manifest role/action schema, and emitted `metrics.csv` headers all preserve the action order from the loaded YAML config.

`manifest.yaml` records run provenance and model shape:

- `experiment_id`, `seed`, `ticks`, `agent_count`, and configured `actions`
- `outputs`, the artifact flags used by the run
- `artifacts`, the exact files written for the run
- `environment.git_commit`, `environment.python_version`, and package versions
- `model.agent_ids`, `model.roles`, `model.bus_nodes`, and `model.bus_edges`
- `model.baseline_lobes.labels`, the baseline lobe vocabulary used in `metrics.csv`
- `model.baseline_lobes.transition_fields`, the lobe transition/run-state metric fields
- `model.queue_dynamics_metrics.pressure_fields`, the queue pressure balance metric fields
- `model.queue_dynamics_metrics.queued_task_age_fields`, the queued-task-age metric fields
- `model.events.types`, the supported baseline event type vocabulary
- `model.events.fields`, the event schema fields emitted in `events.csv`
- `model.metrics.fields`, the complete metrics schema field order emitted in `metrics.csv`
- `model.role_action_metrics.fields`, the role/action metric fields emitted in `metrics.csv`
- `config`, the normalized run config

`metrics.csv` has one row per tick. The current fields include:

- Tick and static graph state: `tick`, `agent_count`, `bus_nodes`, `bus_edges`, `bus_density`, `bus_mean_degree`, `bus_degree_centralization`
- Queue and task totals: `queue_depth`, `queue_delta_tick`, `tasks_created_total`, `tasks_completed_total`, `tasks_completed_tick`
- Per-tick action counts: `messages_sent_tick`, `tasks_created_tick`, `tasks_worked_tick`, `idle_tick`
- Queue pressure balances: `created_completed_balance_tick`, `created_worked_balance_tick`, `work_completion_gap_tick`, `backlog_pressure_tick`
- Queue age metrics: `queued_task_age_max_tick`, `queued_task_age_mean_tick`
- Lobe state: `baseline_lobe_label`, `baseline_lobe_previous_label`, `baseline_lobe_transition`, `baseline_lobe_transition_tick`, `baseline_lobe_run_id`, `baseline_lobe_current_run_length`
- Role/action counts named `role_<role>_<action>_tick`
- Agent population summary: `mean_agent_bias`

`events.csv` has one row per agent action per tick. The current fields are `tick`, `event_type`, `agent_id`, `action`, `target_id`, `task_id`, `work_units`, `remaining_work`, and `completed`. Event types are `agent_idle`, `message_sent`, `task_created`, and `task_worked`.

`summary.md` is a human-readable run summary with bus node/edge counts, static bus metrics, event, task, queue pressure, queue age, written-artifact/output-flag, artifact schema provenance, lobe total, lobe transition, lobe dwell-run, and role/action aggregate sections. The written-artifact/output-flag section reports the exact artifacts written for the run and whether each optional output class was enabled. The schema provenance section reports the emitted metrics/event field counts, lobe/queue/role-action schema counts, and the helper names that define the CSV schemas mirrored in `manifest.yaml`.

## Early Guardrails

- Every run must be reproducible by seed.
- Save the full config and run manifest in the output directory.
- Do not implement dashboards before the metrics schema is stable.
- Do not add real LLM calls in early experiments.
- Every experiment must produce a `summary.md`.
- Every sweep must save per-run metrics and an aggregate summary.

## Planned Stack

- Python
- Mesa
- NetworkX
- NumPy/SciPy
- pandas or polars
- pydantic/PyYAML
- pytest
- Plotly/Jupyter later
- UMAP/HDBSCAN/ruptures/PySINDy later
