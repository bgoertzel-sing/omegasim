# Analytic Delayed Map Refinement/Null Gate Preregistration

Date: 2026-06-30.

Status: preregistered next gate only. This document authorizes the next small
standalone analytic-map refinement and null-scaffold implementation. It does
not authorize a larger grid, simulator mechanics, A5/A7 reruns, dashboards,
external integrations, multi-hive coupling, or strange-attractor promotion
language.

## Background

The completed analytic delayed-map smoke and four-condition grid preflight are
diagnostic background only. They showed bounded trajectories and nonzero
recurrence-surrogate deltas in a standalone mathematical sandbox, but the local
paired-divergence summaries remained negative. Those observations are not
evidence for lobe-like, semantic-dynamics, or strange-attractor-like behavior.

The next gate should sharpen the sandbox before any larger parameter search by
making the delayed state and null comparisons explicit enough to detect
trivial recurrence, contraction, saturation, or delay leakage.

## Question

Can the standalone analytic delayed resource-bounded prediction map produce
bounded, nontrivial residual dynamics that differ from no-delay, linearized,
and delay-shuffled nulls under matched seed, noise, initial state, and
dimensionless controls?

This is a mechanism-screening question only. Passing this gate would justify a
small pre-registered phase-diagram design, not a simulator claim.

## Frozen Scope

The next implementation may add only:

- explicit lifted delayed-state diagnostics for the existing analytic map;
- a read-only paired null runner over the existing map function;
- exactly four preregistered conditions: active delayed nonlinear, no-delay,
  linearized response, and delay-shuffled history;
- one fixed smoke seed and one fixed tick count from config;
- summary-level diagnostics and manifest artifacts.

The next implementation must not:

- call `ohdyn.run` or any A5/A6/A7 comparison/analyzer helper;
- write per-tick OmegaSim simulator artifacts;
- add real LLM, Lean, Slack, browser, Atomspace, dashboard, or external
  integration code;
- add downstream multi-hive coupling;
- broaden seeds or sweep a larger grid;
- describe any result as lobe-like, semantic-dynamic, chaotic, or
  strange-attractor-like.

## Conditions

All conditions must share seed, tick count, initial state, perturbation size,
noise path, `rho`, `delta`, `mu`, `kappa`, and `nu` unless the condition name
requires the specific controlled change.

- `active_delayed_nonlinear`: existing bounded nonlinear delayed map.
- `no_delay`: set effective delay to zero while preserving other controls.
- `linearized_response`: replace bounded nonlinear response with a local
  linear response around the configured initial-state center.
- `delay_shuffled_history`: preserve the delayed-state marginal sequence while
  destroying temporal alignment using a deterministic seed-derived
  permutation.

## Primary Diagnostics

The next gate should emit one row per condition with:

- boundedness status and state range;
- saturation fraction near the lower or upper clipping boundary;
- lifted-history state range or norm summary;
- recurrence rate, phase-shuffled or state-shuffled recurrence surrogate rate,
  and recurrence-surrogate delta;
- finite-time local divergence under matched noise;
- active-vs-null recurrence and divergence deltas.

The active condition is only a candidate for later phase-diagram work if it is
bounded, nontrivially unsaturated, and differs from all three nulls in the
same diagnostic direction. Negative or mixed results close this gate
conservatively.

## Verification

The next implementation must include focused deterministic tests proving:

- repeated runs with the same config produce byte-stable rows;
- exactly the four preregistered conditions are emitted;
- no per-tick simulator metrics/events artifacts are written;
- summary and manifest text retain the diagnostic-only/no-promotion boundary.

Acceptable smoke verification for the next implementation:

```bash
.venv-conda/bin/python -m pytest tests/test_run_harness.py -k analytic_delayed_map_null -q
.venv-conda/bin/python -m py_compile ohdyn/analytic_delayed_map.py tests/test_run_harness.py
git diff --check
```

## Interpretation Boundary

This gate is a prospective mathematical sandbox control. It can reject trivial
delay/null explanations or close fail-closed. It cannot establish OmegaHive
semantic dynamics, lobe dynamics, causal collective intelligence, or
strange-attractor behavior.
