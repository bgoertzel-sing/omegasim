# Analytic Post-Micro Decision Gate

Date: 2026-07-01.

Status: read-only decision synthesis. This note does not report a new
result-bearing experiment and does not support lobe-like, semantic-dynamics,
chaotic, or strange-attractor-like claims.

## Selected Option

`nonlinear_dynamics_workbench`.

The next scientific step should be a separately preregistered, standalone
nonlinear-dynamics workbench for null strength, contraction, clipping,
finite-horizon recurrence, bifurcation, and Lyapunov-style diagnostics before
returning to OmegaSim mechanism design.

## Evidence Reviewed

- `AUTOMATION_STATUS.md`: current source of truth says A5/A7-family work is
  historical or closed and the active gate is read-only post-micro synthesis.
- `README.md`: documents the analytic delayed-map null gate, the analytic
  micro-society gate, and the post-micro decision gate boundaries.
- `docs/analytic_delayed_map_refinement_null_gate_preregistration.md`: froze
  the four-condition delayed-map null gate and required bounded, unsaturated,
  active-vs-null separation before phase-diagram work.
- `docs/analytic_micro_society_map_preregistration.md`: froze the
  four-condition micro-society mechanism screen and required the same
  fail-closed active-vs-null separation.
- `docs/results/analytic_micro_society_map_gate_seed1_20260701.md`: records
  that the micro-society active condition was bounded and unsaturated but had
  mixed or null-equivalent deltas and negative finite-time local divergence.
- `../outputs/strategy-reviews/omegasim/latest-review.md`: recommended the
  analytic null gate as the next step. That recommendation was sensible and
  already completed before this decision note; the later micro-society gate
  also closed conservatively.

## Rationale

Both completed standalone analytic gates produced bounded, unsaturated active
conditions, but neither produced robust same-direction separation from the
preregistered nulls. Both also retained negative finite-time local divergence.
That pattern makes the main uncertainty diagnostic rather than mechanistic:
recurrence-like summaries may be explained by contraction, clipping,
finite-horizon effects, or insufficient null/surrogate pressure.

The workbench option directly targets that uncertainty without adding another
OmegaSim mechanism or tuning the existing maps after inspection. It also
matches the external review's contingency advice: if analytic gates remain
contractive or null-equivalent, stop simulator churn and build a
nonlinear-dynamics diagnostic workbench before returning to OmegaSim.

## Options Not Selected

`stop_analytic_churn` was not selected because the failures are informative:
they point to diagnostic weaknesses that can be isolated in a small
mathematical workbench without broadening OmegaSim mechanics.

`one_more_mechanism_map` was not selected because no single missing causal
mechanism is strong enough after the delayed-map and micro-society closures.
The already tested micro-society gate covered the most obvious next mechanism
set: artifact readiness, prediction spend/error, and fatigue/adaptive
threshold state.

## Boundary

This decision does not authorize simulator mechanics, A5/A7 reruns, dashboards,
external integrations, broad sweeps, downstream multi-hive coupling, or
promotion language. It also does not authorize implementing the workbench yet.

## Exactly One Next Step

Preregister the standalone nonlinear-dynamics workbench, including its fixed
diagnostics, null families, output contract, verification commands, and
fail-closed interpretation rules, before any workbench implementation.
