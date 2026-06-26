# A4 Delayed-Coupling Follow-Up Decision, Seeds 100..129

Decision basis:

- `docs/results/a4_two_hive_holdout_seed100_129.md`
- `docs/results/a4_decision_note_seed100_129.md`
- `docs/a4_delayed_coupling_followup_null_preregistration.md`
- `docs/results/a4_delayed_coupling_null_seed100_129.md`
- latest external review at `../outputs/strategy-reviews/omegasim/latest-review.md`

The latest external review was marked `strategic_change_level: minor` and
`notify_ben: false`. Its recommendation to keep A4 bounded, use the existing
two-hive holdout and read-only analyzers, and avoid new mechanics remains
accepted. No recommendation is rejected, no strategic pivot is made, and no Ben
notification is required.

## Decision

The completion-fraction temporal-null residual warrants one more
analysis-only accounting control before any future three-hive target-null
preregistration.

Do not implement three-hive mechanics, new coupling modes, new lobe labels,
dashboards, external integrations, or broad residual-lobe sweeps from the
current A4 result. The delayed-coupling signal remains a synchronization
diagnostic inside the queue-flow/service research frame, not a mechanism claim.

## Evidence

The delayed-coupling temporal null separated the primary endpoints into two
groups.

Endpoints still explained conservatively by temporal/block-shift controls:

| endpoint | observed_minus_null_mean | outside_null_ci | seed_centered_positive_rate |
| --- | ---: | --- | ---: |
| load_backlog_corr_lag0 | 0.333787 | False | 0.700000 |
| load_backlog_corr_lag2 | 0.035677 | False | 0.633333 |
| queued_age_divergence_final | -0.570895 | False | 0.433333 |
| completion_fraction_divergence_final | -0.003026 | False | 0.400000 |

Endpoints that survive the circular-shift temporal null:

| endpoint | observed_minus_null_mean | outside_null_ci | seed_centered_positive_rate |
| --- | ---: | --- | ---: |
| completion_fraction_corr_lag0 | 0.719486 | True | 0.966667 |
| completion_fraction_corr_lag2 | 0.657053 | True | 0.900000 |

This pattern is scientifically interesting but narrow. The surviving endpoints
are completion-fraction correlations, not load-backlog correlations or
divergence endpoints. They therefore justify checking whether the residual is
still explained by service opportunity, work-event totals, queued age, transfer
timing, or action mix before designing any new simulator mechanics.

## Interpretation Boundary

The result supports this statement:

Delayed full-transfer coupling produced completion-fraction synchronization
stronger than the preregistered circular-shift temporal null over the existing
two-hive holdout artifacts.

The result does not support these stronger statements:

- delayed coupling demonstrates independent lobe grammar;
- two hives are sufficient for a meaningful target-randomization phase null;
- three-hive mechanics should be implemented immediately;
- completion-fraction synchronization is independent of queue-flow/service and
  action-budget accounting.

## Chosen Next Step

Draft and implement a read-only A4 accounting-control analyzer over the existing
seed `100..129` holdout artifacts.

The analyzer should keep the original run directories unchanged and should test
whether delayed-minus-none completion-fraction correlation residuals remain
after controlling for preregistered accounting fields already present in the
artifacts:

- per-hive work-event totals and work-event deltas;
- queued-task age summaries;
- transfer counts and delayed delivery timing;
- created-task and completed-task totals;
- action-mix totals or rates;
- final queue depth and load-normalized backlog.

The primary output should be a committed decision summary plus ignored run
tables reporting paired-seed residual effects, sign support, and whether the
completion-fraction residual remains outside the temporal-null/accounting-control
interpretation band.

If this accounting control explains the residual, close A4 as queue-flow/service
accounting plus a documented delayed synchronization diagnostic. If it does not
explain the residual, the next step should be a preregistered three-hive
target-null design document, still before any simulator mechanics are changed.
