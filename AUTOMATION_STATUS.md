# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison seed-set sensitivity on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 ran the default three-seed pressure comparison and inspected top-response stability against the two-seed regression fixture.
- Changed: no simulator code changes; generated ignored local artifacts under `runs/a2_attention_pressure_compare` and compared their `Top pressure-response explanation` against a fresh two-seed `/tmp` comparison.
- Verified: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 3 --out runs/a2_attention_pressure_compare` completed successfully; a fresh `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 --out /tmp/omegasim_pressure_two_seed.*` completed successfully. The three-seed run selected `policy=internal_improvement`, `observable=final queue depth`, `metric=normal_to_medium_slope`, `field=queue_depth_normal_to_medium_slope`, with condition means `normal=20.666667`, `medium_pressure=39.333333`, `high_pressure=45.666667`; the two-seed fixture selected `policy=baseline`, `observable=value-weighted completed work`, `metric=curvature`, `field=value_weighted_completed_pressure_curvature`, with condition means `normal=56.5`, `medium_pressure=45.0`, `high_pressure=57.5`.
- Blockers: none; the explained top pressure response is deterministic for each seed set but not stable between the two-seed fixture and the default three-seed run.
- Next step: add a deterministic seed-set sensitivity note or metric to the pressure comparison summary so top-response instability is visible without manual cross-run inspection.
