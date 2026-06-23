# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response convergence inspection on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added pressure-stability convergence inspection derived from the existing pressure stability agreement rows.
- Changed: no simulator, scheduling, baseline run harness, or A0/A1 schema behavior changes; `ohdyn.compare_pressure` now writes top-level `pressure_stability_convergence.csv` with one row summarizing how many proper seed prefixes stabilize the global pressure-response ranking, the class-specific capture-pressure ranking, matching stability state, and both rankings together. The top-level `summary.md` now includes a `Pressure-stability convergence inspection` section, collision checks protect the new artifact, README documents it, and regression tests cover header/order, row contents, CLI layout, reproducibility, and overwrite refusal.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 3 4 5 --out runs/a2_attention_pressure_compare_convergence_seed1_5` completed and wrote `pressure_stability_convergence.csv`. For full seeds `1,2,3,4,5`, class-specific stability is present for all 4 proper prefixes, global stability first appears at prefix `1,2,3`, and the last prefix `1,2,3,4` is both globally and class-stable.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_stability or pressure_response_selection or pressure_summary_compares_global or documented_pressure_cli'` passed with 9 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 461 tests.
- Blockers: none.
- Next step: add a small comparison note that contrasts the convergence prefix for pressure-response stability against the pressure-response interpretation section's selected top response.
