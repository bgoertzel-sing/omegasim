# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure/attention experiments are now extending beyond the initial 1.0/1.4/1.8 pressure curve. The current priority is to use the new extreme-pressure endpoint to test whether queue-depth and value-throughput curvature remain stable across seeds or were one-seed artifacts.

## Latest Run

- Status: ok, 2026-06-24 added an A2 extreme-pressure fixture set and made pressure-curve slope calculations use the actual configured task-creation pressures.
- Changed: added `configs/a2_attention_extreme_pressure.yaml`, `configs/a2_attention_research_heavy_extreme_pressure.yaml`, and `configs/a2_attention_internal_improvement_extreme_pressure.yaml` at `model.task_creation_pressure: 2.2`; updated `ohdyn.compare_pressure` to validate one shared pressure value per condition and strictly increasing normal/medium/high endpoints; threaded those endpoint values through pressure-row prefix/stability recalculations; documented the normal=1.0, medium=1.8, high=2.2 extreme-pressure comparison command in `README.md`; added regression coverage that custom pressure-axis slopes use the 2.2 endpoint rather than the default 1.8 denominator. No real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace integrations, multi-hive coupling, A0/A1 scheduling, task policy shares, simulator action vocabulary, or output schemas were changed.
- Strategic review: `../outputs/strategy-reviews/omegasim/latest-review.md` was not present, so no GPT-5.5-Pro recommendation was available to incorporate or defer. Older review/failure files may exist in that directory but were not treated as the current strategic source.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --medium-pressure-baseline-config configs/a2_attention_high_pressure.yaml --medium-pressure-variant-config configs/a2_attention_research_heavy_high_pressure.yaml --medium-pressure-internal-improvement-config configs/a2_attention_internal_improvement_high_pressure.yaml --high-pressure-baseline-config configs/a2_attention_extreme_pressure.yaml --high-pressure-variant-config configs/a2_attention_research_heavy_extreme_pressure.yaml --high-pressure-internal-improvement-config configs/a2_attention_internal_improvement_extreme_pressure.yaml --seeds 1 --out runs/a2_attention_extreme_pressure_smoke_20260624` completed successfully.
- Result: the one-seed extreme-pressure smoke ranked baseline value-weighted completed-work curvature as the strongest pressure response (`-58.75`), with internal-improvement final queue-depth medium-to-high slope and value-weighted curvature tied next (`55.0` absolute). This is a useful probe signal, not yet a stable interpretation, because only seed `1` was run.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'loads_a2_attention_pressure_fixtures or pressure_comparison_uses_custom_pressure_axis or pressure_comparison_curve_metrics_match_condition_means or pressure_comparison_runner_writes_fixed_policy_deltas'` passed with `12 passed, 497 deselected`; `.venv-conda/bin/python -m pytest` passed with `509 passed`.
- Blockers: none.
- Next step: run the documented extreme-pressure comparison across seeds `1 2 3`, then run `ohdyn.analyze_pressure` on that output to check whether the one-seed curvature/queue-depth signal is seed-stable.
