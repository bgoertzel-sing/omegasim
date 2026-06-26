# A4 Decision Note, Two-Hive Holdout Seeds 100..129

Run basis: `docs/results/a4_two_hive_holdout_seed100_129.md` and the regenerated
read-only analyzer outputs in `runs/a4_two_hive_holdout_seed100_129_analysis`.

External review basis: the latest review at
`../outputs/strategy-reviews/omegasim/latest-review.md` was marked
`strategic_change_level: minor` and `notify_ben: false`. Its recommendation to
run only the preregistered two-hive seed `100..129` bundle and read-only
analyzer was accepted. No strategic pivot was made, and no Ben notification is
required.

## Decision

Treat the first A4 holdout as a conservative queue-flow/service result, not as
evidence for an independent multi-hive lobe grammar.

The holdout supports three bounded conclusions:

1. Full-transfer coupling is robustly implemented and analyzable.
2. Two-hive direct and shuffled conditions are structurally identical for target
   assignment and therefore validate schema/conservation/source-opportunity
   behavior, not phase-randomization.
3. Delayed coupling shows bootstrap-supported cross-hive synchronization
   endpoints versus no coupling, but the same condition also changes service
   opportunity and queued-age fields enough that the result should be promoted
   only to a follow-up null-design question.

Do not add new simulator mechanics, three-hive coupling, dashboards, external
integrations, or new lobe architectures from this result alone.

## Evidence

The analyzer consumed 30 paired seeds, four modes, 240 per-hive endpoint rows,
and 120 cross-hive endpoint rows.

Transfer effects are stable and dominated by the configured full-transfer
coupling:

| comparison | transfers mean delta | bootstrap mean-delta CI | sign stability |
| --- | ---: | ---: | ---: |
| direct minus none | 865.333333 | [857.366667, 873.666667] | 1.000000 |
| delayed minus none | 865.900000 | [857.233333, 875.033333] | 1.000000 |
| shuffled minus none | 865.333333 | [856.866667, 873.933333] | 1.000000 |
| direct minus shuffled | 0.000000 | [0.000000, 0.000000] | 0.000000 |

The direct and shuffled rows are identical on every listed cross-hive endpoint.
In a two-hive system this is expected: each source hive has only one legal
non-source target, so shuffled target assignment cannot randomize phase
structure. The `direct minus shuffled` contrast is therefore a contract check,
not a scientific null.

Selected preregistered cross-hive endpoint effects:

| comparison | endpoint | mean delta | bootstrap mean-delta CI | positive delta rate | sign stability |
| --- | --- | ---: | ---: | ---: | ---: |
| direct minus none | load-backlog corr lag 0 | -0.654804 | [-0.817661, -0.488024] | 0.133333 | 1.000000 |
| direct minus none | load-backlog corr lag 2 | -0.474341 | [-0.643660, -0.306306] | 0.200000 | 1.000000 |
| direct minus none | completion-fraction corr lag 0 | -0.019374 | [-0.195802, 0.159425] | 0.433333 | 0.612000 |
| delayed minus none | load-backlog corr lag 0 | 0.325600 | [0.118204, 0.517629] | 0.700000 | 0.999000 |
| delayed minus none | completion-fraction corr lag 0 | 0.678330 | [0.494969, 0.857877] | 0.966667 | 1.000000 |
| delayed minus none | completion-fraction corr lag 2 | 0.619752 | [0.416347, 0.802583] | 0.900000 | 1.000000 |
| delayed minus none | queued-age divergence final | 0.518094 | [-0.168911, 1.204228] | 0.666667 | 0.935000 |
| delayed minus none | completion-fraction divergence final | -0.005065 | [-0.019377, 0.009767] | 0.500000 | 0.757000 |

The delayed correlation endpoints pass the paired-bootstrap uncertainty check
for this holdout. They do not yet pass the stronger mechanism decision rule,
because they are not separated from queue-flow/service accounting. In the same
delayed-minus-none comparison, hive-level work events decline with bootstrap
intervals excluding zero for both hives, and hive-level queued age rises:

| hive | endpoint | mean delta | bootstrap mean-delta CI | sign stability |
| --- | --- | ---: | ---: | ---: |
| hive_a | work events total | -8.066667 | [-10.433333, -6.000000] | 1.000000 |
| hive_b | work events total | -5.500000 | [-7.533333, -3.733333] | 1.000000 |
| hive_a | queued-task age mean final | 2.349097 | [1.167113, 3.535482] | 1.000000 |
| hive_b | queued-task age mean final | 1.175816 | [0.029264, 2.335281] | 0.979000 |

Those fields are exactly the preregistered explanatory variables that must be
ruled out before claiming a cross-hive coordination mechanism beyond
queue-flow/service dynamics.

## Interpretation

The first A4 holdout demonstrates that the two-hive artifact contract and
read-only paired-seed analyzer are stable enough to support scientific
comparison. It also produces a real delayed-coupling signal on preregistered
correlation endpoints.

The most defensible interpretation is narrower: delayed full-transfer coupling
changes queue-flow timing and work opportunity in a way that increases some
cross-hive service/load correlations versus no coupling. That is a queue-flow
and service result with an interesting delayed-synchronization diagnostic. It
is not yet evidence for a residual lobe grammar, strange-attractor dynamics, or
a general multi-hive phase-control mechanism.

## Gate Outcome

Close the seed `100..129` A4 decision gate with no simulator change.

The next scientific step should be a preregistered follow-up null design for the
delayed-coupling synchronization endpoints. That design should be written
before any new mechanics are implemented and should explicitly address:

- a meaningful phase or target null beyond the two-hive shuffled limitation;
- preservation of transfer volume, source opportunity, and delivery timing
  marginals where possible;
- paired-seed uncertainty and sign-stability requirements;
- queue-flow/service accounting fields that would explain away the effect;
- whether the follow-up needs three hives or can be done as an analysis-only
  temporal/block-shuffle null over existing two-hive artifacts.

Until that preregistration exists, keep A4 claims limited to analyzable
queue-flow/service effects and delayed-coupling synchronization diagnostics.
