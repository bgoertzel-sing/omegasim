# A3 closure gate, seeds 70..99

This gate closes the current single-hive A2/A3 research loop using existing
artifacts only. It records the decision boundary for future automation runs so
that baseline infrastructure and residual-lobe experiments are not duplicated.

No simulations were rerun for this gate. No simulator mechanics, dashboards,
LLM calls, Lean, Slack, browser automation, Atomspace integration, or multi-hive
coupling were added.

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: minor`
- `notify_ben: false`
- Accepted: close the A3 cycle with queue-flow/service endpoints as the primary
  interpretation, keep lagged synchronization descriptive, and stop new A2/A3
  sweeps unless a concrete artifact bug is found.
- Deferred: a temporal-shift or block-shuffle null for lagged synchronization
  remains scientifically sensible, but is not required for closure because the
  lagged effects are not promoted to mechanism claims.
- Rejected: no recommendation was rejected.

## Gate decision

A0/A1 baseline infrastructure is complete and should not be reimplemented:
deterministic YAML-loaded runs, 15 static OmegaHive-like agents, one task
queue, one NetworkX bus graph, metrics/events output, `summary.md`,
reproducibility tests, role/action metrics, lobe labels, and lobe-transition
summaries are already covered.

A2 residual lobe grammar is closed under the current single-hive simulator and
label scheme. The current evidence supports load pressure, service capacity,
completion fraction, and work-opportunity accounting. It does not support an
independent emergent lobe grammar after exogenous-arrival, queue-blind, null,
and paired-seed controls.

A3 queue-flow/service accounting is frozen as the primary interpretation for
the current artifact set. Queue inflow/outflow, completion fraction,
load-normalized backlog, queued-task age, and work-event opportunity should be
the primary endpoints for any future preregistered multi-hive phase.

Lagged service/completion and service/load-change correlations remain
exploratory diagnostics. Best-lag selection is descriptive and should not be
used for mechanism claims unless a future preregistration fixes lag direction
or adds an explicit temporal-shift or block-shuffle null.

## Stop conditions

Do not run new broad A2 residual-lobe sweeps, add new queue/action-derived lobe
labels, or start multi-hive coupling mechanics in this closed A3 loop.

The only acceptable reasons to reopen A2/A3 analysis are:

- a concrete artifact bug that changes the recorded results;
- a narrowly scoped analysis-only validation that uses existing artifacts and
  does not promote lagged synchronization to a mechanism claim;
- a separate preregistered next phase with primary queue-flow/service endpoints.

## Future preregistration boundary

If OmegaSim later proceeds to multi-hive Moltbook coupling, write a new
preregistration before simulator changes. Primary endpoints should include
queue inflow/outflow, completion fraction, load-normalized backlog, queued-task
age, work-event opportunity, and preregistered cross-hive service/load phase
relations. Controls should include no coupling, shuffled or delayed coupling,
fixed exogenous-load controls, paired-seed comparisons, sign stability, and
confidence-interval thresholds before promoting any diagnostic to a claim.
