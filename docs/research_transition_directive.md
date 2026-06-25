# Research Transition Directive

OmegaSim infrastructure hardening should remain a means, not the main research
product. Reproducibility, CLI parity, artifact hygiene, and append-safe outputs
remain mandatory, but the A0/A1 baseline and A2 artifact scaffolds are stable
enough that new work should be justified by a sharper scientific question.

## Superseded A2 exploration directive

The earlier directive to continue broad A2 residual-lobe exploration is now
superseded by `docs/results/a2_exogenous_arrival_decision_synthesis_seed70_99.md`.
That synthesis freezes A2 as a negative/clarifying mechanism result:

- robust load/accounting effects are supported;
- action-budget-mediated trajectory effects are supported;
- the residual queue-blind entropy result is only a weak point estimate;
- independent emergent lobe grammar is not demonstrated by the current
  simulator and label scheme.

The external strategic review that triggered this shift was marked
`strategic_change_level: major` and `notify_ben: true`; Ben should be notified
that the A2 residual-lobe search is closed unless a concrete artifact bug is
found.

## Current research direction

Do not run more broad A2 seed sweeps or add simulator mechanisms to rescue the
residual-lobe hypothesis. Future work should either be analysis-only validation
of existing artifacts or a preregistered next stage with primary endpoints that
are less mechanically tied to the current lobe labels.

Preferred next-stage endpoints:

- queue-flow balance and load-normalized backlog;
- service-capacity and completion-fraction response;
- queued-task age and stale-work accumulation;
- action-budget and work-opportunity accounting;
- synchronization or desynchronization of service and queue-flow observables if
  a later multi-hive phase is explicitly preregistered.

New lobe observables should be introduced only if they are not derived directly
from queue depth, queue delta, or the same action counts being manipulated. A
stronger queue-blind trajectory null or first-order Markov-preserving null is a
reasonable analysis-only follow-up, but it is not a blocker for the frozen A2
conclusion.

Infrastructure work remains justified when it directly supports these endpoints
or protects reproducibility. Otherwise, the preferred next move is synthesis,
validation, or a narrowly preregistered experiment rather than another broad
exploratory simulator sweep.
