# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response stability inspection on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 ran the full three-seed pressure comparison and pressure-analysis helper to check whether the new top value-yield divergence interpretation stays stable beyond the two-seed smoke.
- Changed: no source-code or schema changes. Generated ignored run artifacts in `runs/a2_attention_pressure_compare_full_20260624` and `runs/a2_attention_pressure_analysis_full_20260624`. No real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace integrations, multi-hive coupling, A0/A1 scheduling, simulator output schema, or agent population changes.
- Strategic review: `../outputs/strategy-reviews/omegasim/latest-review.md` was not present, so no GPT-5.5-Pro recommendation was available to incorporate or defer.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 3 --out runs/a2_attention_pressure_compare_full_20260624` and `.venv-conda/bin/python -m ohdyn.analyze_pressure --pressure-dir runs/a2_attention_pressure_compare_full_20260624 --out runs/a2_attention_pressure_analysis_full_20260624 --limit 10` both completed successfully.
- Result: the top value-yield divergence remained `baseline` / `curvature` and the interpretation remained "pressure improves completion-normalized yield without degrading effort-normalized yield." The magnitude changed from the two-seed smoke (`completed=0.307552`, `work_event=1.335545`) to the three-seed run (`completed=0.024544`, `work_event=0.727770`), so the qualitative reading is stable while the effect size is seed-sensitive. The broader global top pressure response is not seed-prefix stable (`policy,observable,metric` changed for prefixes), while the class-specific capture-pressure top response is stable across prefixes.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis or pressure_comparison'` passed with `33 passed, 460 deselected`.
- Blockers: none.
- Next step: add a deterministic seed-prefix stability section for `ohdyn.analyze_pressure`'s value-yield divergence ranking, so the analysis artifact reports whether the top divergence interpretation itself is stable rather than requiring manual comparison across runs.
