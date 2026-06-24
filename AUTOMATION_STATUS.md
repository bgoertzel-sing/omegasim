# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response analysis hardening on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 added deterministic seed-prefix stability reporting for `ohdyn.analyze_pressure`'s value-yield divergence interpretation.
- Changed: `ohdyn.analyze_pressure` now writes `value_yield_divergence_stability.csv` and a `Value-yield divergence prefix stability` summary section. The helper reads the existing per-seed pressure-condition `comparison_metrics.csv` files, recomputes prefix pressure rows, and records whether each prefix selects the same top divergence policy/metric as the full seed set. Tests and README were updated for the new artifact contract. Generated ignored run artifacts in `runs/a2_attention_pressure_analysis_stability_20260624`. No real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace integrations, multi-hive coupling, A0/A1 scheduling, simulator output schema, or agent population changes.
- Strategic review: `../outputs/strategy-reviews/omegasim/latest-review.md` was not present, so no GPT-5.5-Pro recommendation was available to incorporate or defer.
- Smoke run: `.venv-conda/bin/python -m ohdyn.analyze_pressure --pressure-dir runs/a2_attention_pressure_compare_full_20260624 --out runs/a2_attention_pressure_analysis_stability_20260624 --limit 10` completed successfully against the existing three-seed pressure comparison.
- Result: the full three-seed top value-yield divergence remains `baseline` / `curvature` with completed-task response `0.024544`, work-event response `0.727770`, and divergence `-0.703226`. The new stability section reports last-prefix stability for seeds `1,2` as `true`, all-prefix stability as `false`, and single-seed prefix instability caused by `policy` because seed `1` selects `internal_improvement` / `curvature`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis'` passed with `29 passed, 465 deselected`; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis or pressure_comparison'` passed with `34 passed, 460 deselected`; `.venv-conda/bin/python -m ruff check ohdyn/analyze_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with `494 passed`.
- Blockers: none.
- Next step: run one four- or five-seed pressure comparison plus analysis to see whether the value-yield divergence top policy/metric remains stable after adding more seeds.
