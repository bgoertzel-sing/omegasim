# Attention Allocation Policy Sketch

The A0/A1 baseline accumulates backlog because agents create more work than
they complete. This is a useful null model: almost every human research process
also produces more plausible tasks than it can execute. The next OmegaSim policy
experiments should treat backlog pressure as an attention-allocation problem,
not merely as a queue-depth problem.

## Task Categories

The main task-management agent should classify tasks into broad attention
classes:

- `near_term_external`: high-priority external/user-facing tasks.
- `long_term_research`: slower research and strategic development tasks.
- `internal_improvement`: self-analysis, policy improvement, and capability
  development tasks.
- `housekeeping`: maintenance, artifact hygiene, cleanup, and administrative
  tasks.

## Attention Parameters

Introduce system parameters:

```yaml
attention_policy:
  near_term_external: 0.45
  long_term_research: 0.25
  internal_improvement: 0.20
  housekeeping: 0.10
```

The four values should sum to `1.0` and represent the intended resource share
allocated to each task class. Early experiments can implement these shares as
soft scheduling quotas over agent actions or task-selection opportunities.

## Override Rule

The policy should resist being fully captured by short-term urgency. If a
perceived excessive short-term urgency condition would require overriding the
reserved shares for research, internal improvement, or housekeeping, the
simulated system should model an explicit human-permission gate.

The opposite exception is also useful: if a class has too few available tasks,
unused attention can be redistributed, but this should be recorded as a policy
event rather than silently hidden.

## Metrics To Add

Candidate metrics for A2 attention-policy experiments:

- Per-class queued task count.
- Per-class completed task count.
- Per-class oldest queued task age.
- Per-class mean queued task age.
- Per-class attention share actually spent.
- Deviation between target and actual attention share.
- Override requests, approvals, denials, and reasons.
- Value-weighted completed work, not only raw completed work.

## Research Hypothesis

A hive that can generate tasks but lacks attention governance becomes a backlog
engine. Minimal quota-based attention allocation should reduce stale-task age
and improve value-weighted throughput without requiring global synchronization
or constant human intervention.
