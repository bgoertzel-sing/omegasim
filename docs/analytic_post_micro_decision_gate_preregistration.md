# Analytic Post-Micro Decision Gate Preregistration

Date: 2026-07-01.

Status: preregistered decision gate only. This document authorizes one bounded
read-only synthesis over the completed standalone analytic delayed-map null
gate and analytic micro-society gate. It does not authorize new simulator
mechanics, A5/A6/A7 reruns, dashboards, external integrations, multi-hive
coupling, broader sweeps, or attractor/lobe/semantic-dynamics promotion
language.

## Background

Two standalone analytic mechanism screens have now closed conservatively.

The analytic delayed-map null gate emitted exactly the preregistered
`active_delayed_nonlinear`, `no_delay`, `linearized_response`, and
`delay_shuffled_history` conditions. The active seed-1 condition was bounded
and unsaturated, but active-vs-null recurrence and local-divergence deltas were
mixed and finite-time local divergence remained negative.

The analytic micro-society map gate emitted exactly the preregistered
`active_delayed_micro_society`, `no_delay`, `linearized_response`, and
`delay_shuffled_history` conditions over artifact readiness, prediction spend,
prediction error, and fatigue/adaptive threshold state. The active seed-1
condition was also bounded and unsaturated, but active-vs-null diagnostics were
mixed/null-equivalent and finite-time local divergence remained negative.

The current evidence therefore does not justify a phase diagram, OmegaSim
simulator mechanics, or promotion language. It does justify one explicit
decision gate before any further analytic-map implementation.

## Question

Given two conservative standalone analytic closures, should the next bounded
OmegaSim research step be:

- stop analytic-map churn and await a new scientific axis;
- build a small nonlinear-dynamics workbench for null, contraction, clipping,
  bifurcation, and Lyapunov-style diagnostics before returning to OmegaSim
  mechanisms;
- define one more mechanism-rich standalone map because a specific missing
  causal mechanism is scientifically compelling enough to preregister.

This gate is a decision gate, not a result-bearing experiment.

## Evidence To Review

The decision note must review only existing checked-in documentation and
existing smoke artifacts from:

- `docs/analytic_delayed_map_refinement_null_gate_preregistration.md`;
- `docs/analytic_micro_society_map_preregistration.md`;
- `docs/results/analytic_micro_society_map_gate_seed1_20260701.md`;
- current README and `AUTOMATION_STATUS.md` analytic-map sections;
- the latest external strategy review when present.

It may inspect checked-in configs and source code for auditability, but it must
not run new simulator experiments, broaden seeds, tune parameters, add
mechanics, or create dashboards.

## Decision Criteria

Choose `stop_analytic_churn` if both completed analytic gates are bounded but
contractive or null-equivalent, and no single missing mechanism is strong enough
to justify another standalone preregistration.

Choose `nonlinear_dynamics_workbench` if the main uncertainty is diagnostic:
recurrence could be caused by clipping, contraction, finite horizon, weak
surrogates, or local stability measurement rather than by the mechanism itself.
The future workbench would need its own preregistration before implementation.

Choose `one_more_mechanism_map` only if the note names exactly one missing
causal mechanism, explains why it is not covered by the delayed-map or
micro-society screens, and freezes the scope tightly enough for a later
standalone preregistration.

## Output Contract

The next implementation may add one decision note under `docs/results/` and
update `AUTOMATION_STATUS.md`. It may update README only to point to the
decision posture.

The decision note must state:

- selected option;
- evidence reviewed;
- reason the other two options were not selected;
- explicit non-authorization of simulator mechanics, A5/A7 reruns, dashboards,
  external integrations, broad sweeps, multi-hive coupling, and promotion
  language;
- exactly one next step.

## Verification

Acceptable verification for the future decision-note run:

```bash
.venv-conda/bin/python -m ohdyn.automation_guard
git diff --check
```

No result-bearing analytic runner, simulator runner, or analyzer is required
for this decision gate.
