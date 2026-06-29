# A7.3 Long-Horizon Residual/Recurrence Validation Preregistration

Status: preregistered next gate; no result-bearing analyzer has been enabled
yet.

This file freezes the first longer-horizon A7.3 validation gate after the
deterministic smoke, read-only preflight, lag-source tightening, and residual
skeleton gates. It does not reopen A5, A7.2, or the three-hive ring, and it
does not authorize parameter sweeps, dashboards, integrations, real LLM calls,
Lean, Slack, browser automation, Atomspace, or downstream multi-hive coupling.

## Scope

The gate remains one hive only. It may reuse the existing A7.3 deterministic
mechanism and the nine frozen conditions:

- `full_delayed_logistic`
- `low_gain_contraction`
- `no_delay_same_tick_blocked`
- `amplitude_matched_linear`
- `artifact_off`
- `cost_free_prediction`
- `spend_only_replay`
- `phase_shuffled_lag`
- `threshold_shuffled`

The fixed validation run is paired seeds `1,2` at `256` ticks per
condition/seed. The existing `64`-tick smoke remains artifact-validity only and
must not be reinterpreted as recurrence evidence.

## Required Inputs

The validation analyzer must be read-only over existing run artifacts. It may
not rerun simulations, tune parameters, infer missing ledgers, or repair
artifacts. It requires an eligible A7.3 preflight manifest for the same compare
directory before computing any residual, recurrence, surrogate, or divergence
row.

Every run must include complete metrics, events, lifted-state, and
source-ledger artifacts. The source ledger must reconstruct delayed peer
activity from prior metrics rows, prove no same-tick leakage for delayed
conditions, preserve no-delay control semantics, and expose phase-shuffled and
threshold-shuffled provenance.

## Residual Targets And Controls

Primary target fields:

- `artifact_readiness`
- `artifact_coherence`
- `contradiction_risk`
- `prediction_error`
- `prediction_uncertainty`
- `fatigue`
- `memory_pressure`
- `work_backlog`

Residual controls:

- `demand_phase`
- `task_arrivals`
- `service_capacity`
- `action_opportunity`
- `work_budget`
- `work_backlog`
- `queued_age`
- `completion_fraction`
- `prediction_spend`
- `lost_work_opportunity_from_prediction`
- `memory_pressure`

The analyzer must treat queue depth, throughput, action counts, spend, and
synchrony-like timing as controls or manipulation checks, not promotion
endpoints.

## Frozen Analysis Parameters

- Seeds: `1,2`
- Horizon: `256` ticks
- Minimum rows for recurrence: `128`
- Train/holdout split: first `60%` train, final `40%` holdout
- Embedding lags: `1,3,6,12`
- Recurrence radius: per-target residual distance quantile `0.10`
- Surrogate repetitions: `32`
- Local divergence neighbors: `8`

These values are intentionally small but longer than the smoke horizon. Any
larger seed set, longer horizon, or parameter grid requires a new
preregistration before results are inspected.

## Primary Endpoints

- Source-ledger delay reconstruction status
- Bounded lifted-state status
- Productivity guardrail status
- Held-out residual forecast improvement over naive controls
- Delay-embedding recurrence rate
- Phase-shuffle surrogate recurrence contrast
- Threshold-shuffle surrogate recurrence contrast
- Linear-control forecastability contrast
- Finite-time local-divergence contrast against low-gain baseline

## Promotion Rule

Promotion is all-or-nothing and fail-closed. The full delayed logistic
condition must pass preflight, boundedness, productivity, and source-ledger
gates for both seeds, then beat every preregistered null on the same target
family without relying on backlog, demand phase, service capacity, prediction
spend, or action-opportunity accounting.

The required null victories are:

- full mechanism beats `low_gain_contraction`
- full mechanism beats `no_delay_same_tick_blocked`
- full mechanism beats `amplitude_matched_linear`
- full mechanism beats `artifact_off`
- full mechanism beats `cost_free_prediction`
- full mechanism beats `spend_only_replay`
- full mechanism beats `phase_shuffled_lag`
- full mechanism beats `threshold_shuffled`

Finite-time local divergence must exceed the low-gain contraction baseline in
the same paired-seed analysis. Failure of any source, guardrail, null,
surrogate, or divergence gate blocks promotion. A blocked gate may motivate a
new preregistration, but it is not evidence for lobe-like, semantic-dynamics,
or strange-attractor-like claims.

## Next Implementation Step

Implement a separate long-horizon comparison helper or controlled extension of
the A7.3 smoke helper that produces only the fixed `256`-tick paired-seed
artifacts described here. Then add a read-only analyzer that consumes those
artifacts plus an eligible preflight manifest and emits fail-closed
residual/recurrence/surrogate/divergence rows.
