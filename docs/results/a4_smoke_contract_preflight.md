# A4 Smoke Contract Preflight

- smoke seed: 31
- scientific holdout seeds run: none
- scope: read-only smoke artifact contract, schema, conservation, and endpoint-computability checks

## Readiness checks

| mode | artifact set | reproducible | provenance | schemas | per-hive conservation | aggregate conservation | mode semantics | endpoints |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| direct | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| delayed | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| shuffled | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

## Smoke endpoint dry run

| mode | hive | created | completed | completion_fraction | load_normalized_backlog | final_mean_age | work_events | inbound | outbound |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | hive_a | 31 | 8 | 0.258065 | 0.741935 | 2.434783 | 23 | 0 | 0 |
| none | hive_b | 34 | 12 | 0.352941 | 0.647059 | 1.363636 | 22 | 0 | 0 |
| direct | hive_a | 28 | 10 | 0.357143 | 0.642857 | 0.888889 | 20 | 28 | 28 |
| direct | hive_b | 28 | 5 | 0.178571 | 0.821429 | 2.521739 | 20 | 28 | 28 |
| delayed | hive_a | 29 | 9 | 0.310345 | 0.241379 | 2.714286 | 16 | 16 | 29 |
| delayed | hive_b | 30 | 7 | 0.233333 | 0.500000 | 3.066667 | 15 | 22 | 30 |
| shuffled | hive_a | 28 | 10 | 0.357143 | 0.642857 | 0.888889 | 20 | 28 | 28 |
| shuffled | hive_b | 28 | 5 | 0.178571 | 0.821429 | 2.521739 | 20 | 28 | 28 |

## Cross-hive computability

| mode | load_backlog_correlation | final_queued_age_divergence | final_completion_fraction_divergence | transfer_attempts |
| --- | ---: | ---: | ---: | ---: |
| none | -0.367518 | 1.071147 | 0.094877 | 0 |
| direct | -0.363644 | 1.632850 | 0.178571 | 56 |
| delayed | 0.903851 | 0.352381 | 0.077011 | 59 |
| shuffled | -0.363644 | 1.632850 | 0.178571 | 56 |

## Shuffled control limitation

- paired direct source-attempt marginals: PASS
- Two-hive shuffled has only one legal target per source hive, so target assignment is structurally equivalent to the only non-source hive and is not a meaningful phase-structure null.

## Interpretation boundary

- PASS means the smoke artifact contract is analyzable; it is not evidence for A4 scientific effects.
- A4 holdout seeds remain blocked until this preflight report is reviewed.
