# Three-Hive Ring Closure Note, Seeds 1-2

Date: 2026-06-28.

This note freezes the interpretation of the completed post-A7.2 three-hive
ring mechanics smoke and read-only residual/null analyzer. It adds no new
mechanics, no new seeds, no parameter tuning, no dashboards, no integrations,
and no promotion language.

## Scope

The fixed gate used the preregistered three-hive ring conditions and paired
seeds `1,2`:

```bash
.venv-conda/bin/python -m ohdyn.compare_three_hive_ring_mechanics --seeds 1 2 --out runs/three_hive_ring_mechanics_smoke_seed1_2
.venv-conda/bin/python -m ohdyn.analyze_three_hive_ring_residual_null --compare-dir runs/three_hive_ring_mechanics_smoke_seed1_2 --out runs/three_hive_ring_residual_null_analysis_seed1_2
```

The mechanics helper emits deterministic metrics, events, and source-ledger
rows for the frozen thirteen-condition grid. The analyzer is read-only: it
consumes existing artifacts, checks schema and source-ledger completeness,
computes residual preflight metrics, compares `delayed_logistic_ring` against
all preregistered nulls, and applies productivity guardrails.

## Verified Result

A bounded reproduction in `/tmp` on 2026-06-28 produced the same fail-closed
result:

```text
runs inspected: 26
overall status: fail_closed_productivity_guardrails
schema/metrics/events/source-ledger pass rows: 26
source-ledger pass rows: 26
residual rows computed: 156
null-contrast gate rows:
  eligible_for_guardrail_and_cross_seed_review: 37
  fail_closed_no_residual_autocorrelation_advantage: 67
  fail_closed_no_residual_predictability_advantage: 16
productivity guardrail rows:
  fail_closed_completion_fraction: 2
```

Both paired seeds failed the preregistered completion-fraction productivity
guardrail for the positive condition. The analyzer also found many null
contrasts where the positive condition did not beat preregistered controls on
residual autocorrelation or residual predictability.

## Interpretation Boundary

This is a fail-closed three-hive ring smoke result. It supports only the
harness-level claim that the fixed schema, mechanics artifacts, and
source-ledger reconstruction can be generated and audited at smoke scale.

It does not support lobe-like, strange-attractor-like, semantic-dynamics,
synchrony, phase-grammar, or causal collective-structure claims. Better
transfer activity, queue effects, raw action counts, or individual eligible
contrast rows should not be interpreted as evidence while productivity
guardrails and all-null contrasts fail.

The current three-hive gate should not be reopened by broad seed sweeps,
parameter sweeps, post-result tuning, additional hives, dashboards,
integrations, or promotion language. Any next scientific direction should be
opened by a fresh preregistration rather than by rescuing this negative smoke.
