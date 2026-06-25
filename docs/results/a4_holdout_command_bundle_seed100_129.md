# A4 Holdout Command Bundle, Seeds 100..129

This is a review bundle only. It drafts the exact A4 two-hive holdout configs,
seed set, and run commands after the smoke-contract preflight passed. It does
not run the seed `100..129` holdout and does not interpret A4 scientific
effects.

## Preconditions

- Review `docs/results/a4_smoke_contract_preflight.md` and confirm the A4 smoke
  artifact contract is sufficient for paired-seed comparisons.
- Keep `transfer_probability: 1.0` for the first holdout so direct, delayed,
  and shuffled avoid the current RNG-stream acceptance-decision confound noted
  in external review.
- Treat two-hive `shuffled` as a schema/conservation and source-opportunity
  marginal control only. With two hives, target assignment has only one legal
  non-source target and is not a meaningful phase-structure null.
- Do not add three-hive mechanics, new lobe labels, dashboards, external
  integrations, or real LLM calls for this holdout.

## Config Bundle

| mode | config | ticks | transfer_probability | delay_ticks |
| --- | --- | ---: | ---: | ---: |
| none | `configs/a4_two_hive_none_holdout.yaml` | 100 | 0.0 | 0 |
| direct | `configs/a4_two_hive_direct_holdout.yaml` | 100 | 1.0 | 0 |
| delayed | `configs/a4_two_hive_delayed_holdout.yaml` | 100 | 1.0 | 2 |
| shuffled | `configs/a4_two_hive_shuffled_holdout.yaml` | 100 | 1.0 | 0 |

All four configs use two hives, `hive_a` and `hive_b`, with hive seed offsets
`0` and `1000`, exogenous arrival rate `1.0`, service capacity `1.0`, and
coupling seed offset `2000`.

## Gate Command

Run this before any holdout execution. If the report path already exists, use a
new review path rather than overwriting committed evidence.

```bash
python -m ohdyn.analyze_a4_smoke_contract \
  --out docs/results/a4_smoke_contract_preflight_review.md
```

## Holdout Commands

The holdout output root should be append-safe and absent before execution:
`runs/a4_two_hive_holdout_seed100_129`.

```bash
for seed in $(seq 100 129); do
  python -m ohdyn.run \
    --config configs/a4_two_hive_none_holdout.yaml \
    --seed "$seed" \
    --out "runs/a4_two_hive_holdout_seed100_129/none_seed${seed}"

  python -m ohdyn.run \
    --config configs/a4_two_hive_direct_holdout.yaml \
    --seed "$seed" \
    --out "runs/a4_two_hive_holdout_seed100_129/direct_seed${seed}"

  python -m ohdyn.run \
    --config configs/a4_two_hive_delayed_holdout.yaml \
    --seed "$seed" \
    --out "runs/a4_two_hive_holdout_seed100_129/delayed_seed${seed}"

  python -m ohdyn.run \
    --config configs/a4_two_hive_shuffled_holdout.yaml \
    --seed "$seed" \
    --out "runs/a4_two_hive_holdout_seed100_129/shuffled_seed${seed}"
done
```

## Required Analysis Contract

Before interpreting results, add or run an analyzer that consumes the holdout
directories and emits paired-seed tables for:

- direct minus none;
- delayed minus none;
- shuffled minus none;
- direct minus shuffled, explicitly caveated as source-opportunity matched but
  not a real target-randomization null in two hives.

Primary fields must come from the preregistered A4 queue-flow/service endpoints:
per-hive inflow, outflow, created and completed tasks, completion fraction,
load-normalized backlog, queued-task age, work-event opportunity, action mix,
transfer counts and direction, fixed lag `0`, fixed lag `2` for delayed, and
cross-hive divergence/correlation fields with deterministic `NA` handling.

The read-only analyzer command is:

```bash
python -m ohdyn.analyze_a4_holdout \
  --holdout-dir runs/a4_two_hive_holdout_seed100_129 \
  --out-dir runs/a4_two_hive_holdout_seed100_129_analysis \
  --seeds 100..129
```

It writes:

- `a4_holdout_hive_endpoints.csv`;
- `a4_holdout_cross_hive_endpoints.csv`;
- `a4_holdout_effects.csv`;
- `summary.md`.

## Boundary

This bundle is ready for review, not execution. A4 holdout seeds remain blocked
until the preflight report and this command/config bundle are reviewed as
sufficient.
