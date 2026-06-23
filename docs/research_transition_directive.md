# Research Transition Directive

OmegaSim infrastructure hardening should now be treated as a means, not the
main research product. Reproducibility, CLI parity, and artifact hygiene remain
important, but the automation should avoid spending too many more cycles on
narrow test refactors unless they directly unlock more informative experiments.

Near-term priority should shift toward executable A2 experiments that can show
interesting hive dynamics:

- attention allocation across external, long-term research, internal
  improvement, and housekeeping task classes;
- backlog growth, stale-task age, and value-weighted throughput under different
  attention policies;
- attractor and strange-attractor-like structure in task queues, agent roles,
  event trajectories, and attention allocation dynamics;
- sensitivity to seed, policy parameters, task creation pressure, and override
  rules;
- phase-space summaries that make the dynamics interpretable rather than only
  regression-testable.

Infrastructure work is still justified when it supports these experiments
directly, for example by adding metrics needed for attractor analysis or by
making experimental comparisons reproducible. Otherwise, the preferred next
move is to implement and run more informative simulations.
