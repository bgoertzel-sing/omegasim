# A4 Delayed-Coupling Temporal Null Analysis

- source: `runs/a4_two_hive_holdout_seed100_129`
- seeds: 100..129
- block sizes: 5, 10, 20
- null endpoint rows: 3840
- method: deterministic circular block shifts of hive_b relative to hive_a.
- excluded offsets: 0 and each run's configured causal delay.
- This analyzer is read-only and does not run or rewrite A4 holdout seeds.

## Delayed Minus None Primary Endpoints

| endpoint | observed_mean_delta | null_mean_delta | null_ci | observed_minus_null_mean | outside_null_ci | seed_centered_positive_rate |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| load_backlog_corr_lag0 | 0.325600 | -0.008187 | [-0.604649, 0.513942] | 0.333787 | False | 0.700000 |
| load_backlog_corr_lag2 | 0.027716 | -0.007961 | [-0.622876, 0.513410] | 0.035677 | False | 0.633333 |
| completion_fraction_corr_lag0 | 0.678330 | -0.041156 | [-0.460525, 0.437689] | 0.719486 | True | 0.966667 |
| completion_fraction_corr_lag2 | 0.619752 | -0.037302 | [-0.475034, 0.506519] | 0.657053 | True | 0.900000 |
| queued_age_divergence_final | 0.518094 | 1.088989 | [-8.515245, 11.433051] | -0.570895 | False | 0.433333 |
| completion_fraction_divergence_final | -0.005065 | -0.002039 | [-0.099326, 0.113188] | -0.003026 | False | 0.400000 |

## Output Tables

- `a4_delayed_null_endpoints.csv`: per-mode, per-seed circular-shift endpoint replicates.
- `a4_delayed_null_effects.csv`: observed mode contrasts compared with circular-shift null deltas.
- `a4_delayed_null_manifest.csv`: deterministic block sizes and offsets used for each mode/seed.

## Interpretation Boundary

- The two-hive shuffled condition remains a schema/source-opportunity control, not a phase-randomization null.
- Effects inside the null interval or with weak seed-centered sign support remain queue-flow/service diagnostics rather than mechanism claims.
- No simulator mechanics, configs, lobe labels, dashboards, real LLM calls, or external integrations are added by this analysis.
