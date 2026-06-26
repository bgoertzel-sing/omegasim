# A4 Accounting-Control Completion Synchrony Analysis

- source: `runs/a4_two_hive_holdout_seed100_129`
- seeds: 100..129
- block sizes: 5, 10, 20
- null endpoint rows: 23040
- method: per-hive completion-fraction residualization followed by deterministic circular block shifts of hive_b relative to hive_a.
- excluded offsets: 0 and each run's configured causal delay.
- This analyzer is read-only and does not run or rewrite A4 holdout seeds.

## Delayed Minus None Completion-Fraction Endpoints

| control_group | endpoint | observed_mean_delta | null_mean_delta | null_ci | observed_minus_null_mean | outside_null_ci | seed_centered_positive_rate |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| raw | completion_fraction_corr_lag0 | 0.678330 | -0.041156 | [-0.460525, 0.437689] | 0.719486 | True | 0.966667 |
| raw | completion_fraction_corr_lag2 | 0.619752 | -0.037302 | [-0.475034, 0.506519] | 0.657053 | True | 0.900000 |
| clock_trend | completion_fraction_corr_lag0 | 0.606222 | -0.032910 | [-0.328565, 0.307020] | 0.639132 | True | 0.933333 |
| clock_trend | completion_fraction_corr_lag2 | 0.495297 | -0.029243 | [-0.345686, 0.382412] | 0.524541 | True | 1.000000 |
| opportunity_load | completion_fraction_corr_lag0 | 0.188740 | -0.010393 | [-0.376651, 0.316421] | 0.199133 | False | 0.733333 |
| opportunity_load | completion_fraction_corr_lag2 | 0.155380 | -0.005927 | [-0.364815, 0.335079] | 0.161307 | False | 0.700000 |
| transfer_timing | completion_fraction_corr_lag0 | 0.661023 | -0.038278 | [-0.457912, 0.452531] | 0.699301 | True | 0.900000 |
| transfer_timing | completion_fraction_corr_lag2 | 0.536277 | -0.034849 | [-0.499479, 0.492520] | 0.571126 | True | 0.833333 |
| combined_non_tautological | completion_fraction_corr_lag0 | 0.156653 | -0.008884 | [-0.335280, 0.312277] | 0.165537 | False | 0.700000 |
| combined_non_tautological | completion_fraction_corr_lag2 | 0.140351 | -0.002389 | [-0.362347, 0.311764] | 0.142740 | False | 0.666667 |
| identity_inclusive | completion_fraction_corr_lag0 | 0.641788 | -0.044218 | [-0.471335, 0.439133] | 0.686006 | True | 0.933333 |
| identity_inclusive | completion_fraction_corr_lag2 | 0.584480 | -0.037514 | [-0.473717, 0.467680] | 0.621994 | True | 0.933333 |

## Result Interpretation

The delayed-minus-none completion-fraction synchrony residual is no longer outside the residualized circular-shift null after the combined non-tautological accounting controls. Treat A4 as queue-flow/service and action-opportunity accounting plus a documented delayed synchronization diagnostic; do not implement three-hive mechanics from this result.

## Control Groups

- `raw`: unresidualized completion-fraction trajectory. Covariates: none.
- `clock_trend`: tick and tick squared. Covariates: tick, tick_squared.
- `opportunity_load`: non-tautological queue, work-opportunity, age, and action-mix fields. Covariates: queue_depth, load_normalized_backlog, queued_task_age_mean_tick, queued_task_age_max_tick, tasks_worked_tick, tasks_created_tick, messages_sent_tick, idle_tick.
- `transfer_timing`: transfer counts, delivered arrivals, and pending delayed deliveries. Covariates: inbound_transfers_tick, outbound_transfers_tick, transfer_attempts_tick, transfers_completed_tick, delivered_inbound_transfers_tick, pending_inbound_transfers_tick.
- `combined_non_tautological`: clock, load/opportunity, action-mix, and transfer-timing fields. Covariates: tick, tick_squared, queue_depth, load_normalized_backlog, queued_task_age_mean_tick, queued_task_age_max_tick, tasks_worked_tick, tasks_created_tick, messages_sent_tick, idle_tick, inbound_transfers_tick, outbound_transfers_tick, transfer_attempts_tick, transfers_completed_tick, delivered_inbound_transfers_tick, pending_inbound_transfers_tick.
- `identity_inclusive`: completion numerator/denominator accounting sensitivity fields. Covariates: tasks_created_total, tasks_completed_total, tasks_created_tick, tasks_completed_tick.

## Output Tables

- `a4_accounting_control_endpoints.csv`: observed and circular-shift completion-correlation endpoint rows by control group.
- `a4_accounting_control_effects.csv`: observed mode contrasts compared with residualized circular-shift null deltas.
- `a4_accounting_control_manifest.csv`: covariate groups, block sizes, offsets, and transfer-delay summaries.

## Interpretation Boundary

- `identity_inclusive` is an accounting-decomposition sensitivity, not the primary causal control.
- The two-hive shuffled condition remains a schema/source-opportunity control, not a phase-randomization null.
- No simulator mechanics, configs, lobe labels, dashboards, real LLM calls, or external integrations are added by this analysis.
