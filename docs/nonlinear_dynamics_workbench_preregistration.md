# Nonlinear-Dynamics Workbench Preregistration

Date: 2026-07-01.

Status: preregistered next implementation gate only. This document authorizes
one small standalone diagnostic workbench after the analytic delayed-map null
gate and analytic micro-society gate both closed conservatively. It does not
authorize OmegaSim simulator mechanics, A5/A6/A7 reruns, dashboards, external
integrations, multi-hive coupling, broad sweeps, or attractor/lobe/
semantic-dynamics promotion language.

## Background

The Hyperseed tuning formalization requires well-posedness, boundedness,
non-contraction checks, recurrence diagnostics, Lyapunov-style diagnostics,
surrogate/null controls, and explicit fail-closed interpretation before any
complex-attractor language is meaningful.

The completed analytic delayed-map null gate and analytic micro-society gate
were bounded and unsaturated at seed 1, but both were contractive or
mixed/null-equivalent against their preregistered controls. The post-micro
decision note therefore selected a nonlinear-dynamics workbench rather than
another mechanism map.

This next gate is diagnostic, not mechanistic. It should determine whether the
existing analytic-map evidence is limited by clipping, contraction, finite
horizon recurrence, weak nulls, or local-stability measurement choices before
OmegaSim mechanism design resumes.

## Question

Can a tiny standalone workbench distinguish contraction, clipping-driven
recurrence, finite-horizon recurrence, noise-driven irregularity, and candidate
non-contractive bounded regimes using deterministic summary diagnostics over
the existing dimensionless axes `rho`, `delta`, `mu`, `kappa`, and `nu`?

Passing this gate would justify a later separately preregistered phase-diagram
design. It would not establish OmegaHive semantic dynamics, lobe dynamics,
causal collective intelligence, chaos, or strange-attractor behavior.

## Frozen Scope

The next implementation may add exactly one standalone workbench runner and one
config. It may use the existing analytic map functions as mathematical objects
under test, but it must not call `ohdyn.run`, A5/A6/A7 helpers, dashboards, live
task systems, browser/Slack/Atomspace integrations, real LLMs, or any multi-hive
coupling.

The workbench must remain smoke-scale:

- one fixed seed;
- one fixed tick count;
- one fixed perturbation size;
- one fixed initial state;
- a tiny preregistered parameter panel rather than a broad sweep;
- summary-level artifacts only.

The parameter panel should include only these four rows unless a future
preregistration changes them:

| panel_id | rho | delta | mu | kappa | nu | purpose |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `low_gain_no_delay` | 0.4 | 0.0 | 3.0 | 0.05 | 0.0 | contraction/control baseline |
| `low_gain_delay` | 0.4 | 0.5 | 3.0 | 0.05 | 0.0 | delay-only baseline |
| `active_reference` | 1.35 | 0.5 | 3.0 | 0.2 | 0.01 | current analytic reference |
| `high_gain_delay` | 2.2 | 1.0 | 3.0 | 0.2 | 0.01 | non-contraction stress check |

These are diagnostic anchors only. They are not a phase diagram and must not be
expanded in the same implementation run.

## Required Diagnostics

Emit one summary row per panel entry with:

- boundedness status, state range, and finite-value checks;
- clipping/saturation fraction near the lower and upper bounds;
- lifted-history range and norm summary;
- recurrence rate, state-shuffled recurrence rate, phase-shuffled recurrence
  rate, and both deltas;
- finite-time local divergence with matched noise;
- finite-time Lyapunov-style estimate using periodic perturbation
  renormalization;
- local finite-difference Jacobian spectral radius at the configured initial
  state when applicable;
- a regime label chosen only from the frozen fail-closed labels below.

The finite-time Lyapunov-style estimate must use fixed noise and repeated
renormalization rather than only final paired separation. It is still a
diagnostic estimate, not proof of chaos.

## Required Nulls And Controls

For each panel entry, compute matched controls sufficient to detect trivial
sources of recurrence:

- no-delay control;
- linearized-response control;
- delay-shuffled-history control;
- state-shuffled recurrence surrogate;
- phase-shuffled recurrence surrogate.

All controls must preserve seed, tick count, initial state, perturbation size,
noise path, clipping bounds, and all dimensionless controls except the intended
null manipulation.

## Regime Labels

Each panel row must choose exactly one label:

- `fail_closed_unbounded_or_nonfinite`;
- `fail_closed_trivial_saturation`;
- `fail_closed_contracting_fixed_or_transient`;
- `fail_closed_null_equivalent_recurrence`;
- `fail_closed_noise_or_finite_horizon_irregularity`;
- `candidate_noncontractive_bounded_diagnostic_only`.

The candidate label is allowed only if the row is bounded, nontrivially
unsaturated, has positive Lyapunov-style estimate after renormalization, has
local spectral radius above one, and separates from all preregistered nulls in
the same recurrence direction. Even that candidate label is diagnostic only and
does not authorize promotion language.

## Output Contract

The runner must write only:

```text
config.yaml
manifest.yaml
workbench_summary.csv
summary.md
```

It must not write simulator `metrics.csv` or `events.csv` artifacts, launch a
dashboard, call broader analyzers, broaden seeds, or create per-tick simulator
state logs.

## Verification

The next implementation must include focused deterministic tests proving:

- repeated runs with the same config produce byte-stable summary rows;
- exactly the four preregistered panel entries are emitted;
- the manifest records the dimensionless axes, null families, and
  diagnostic-only/no-promotion boundary;
- no simulator `metrics.csv` or `events.csv` artifacts are written;
- changing the panel list fails closed.

Acceptable smoke verification for that future implementation:

```bash
.venv-conda/bin/python -m pytest tests/test_run_harness.py -k nonlinear_dynamics_workbench -q
.venv-conda/bin/python -m py_compile ohdyn/nonlinear_dynamics_workbench.py tests/test_run_harness.py
git diff --check
```

## Interpretation Boundary

This workbench exists to audit analytic-map diagnostics after two conservative
closures. It is not a rescue sweep and is not evidence that prior A5, A7, or
analytic-map runs contained hidden attractors. Any future positive workbench
result remains a diagnostic artifact until a later preregistered phase diagram
and stronger semantic/provenance gates exist.

## Exactly One Next Step

Implement only the preregistered standalone nonlinear-dynamics workbench smoke
runner and focused deterministic tests described above.
