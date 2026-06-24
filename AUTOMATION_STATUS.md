# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure/attention experiments are testing whether the extreme-pressure endpoint yields a stable pressure-response interpretation across seed prefixes. The current priority is to separate robust queue-depth pressure effects from still-seed-sensitive value-yield and class-capture-pressure signals before adding new model mechanisms.

## Latest Run

- Status: ok, 2026-06-24 ran the documented extreme-pressure comparison across seeds `1 2 3 4 5` and analyzed the resulting pressure-response rankings.
- Changed: generated local ignored artifacts under `runs/a2_attention_extreme_pressure_compare_seed1_5_20260624/` and `runs/a2_attention_extreme_pressure_analysis_seed1_5_20260624/`. No code, configs, tests, simulator mechanisms, A0/A1 scheduling, task policy shares, output schemas, real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace integrations, or multi-hive coupling were changed.
- Strategic review: `../outputs/strategy-reviews/omegasim/latest-review.md` was not present, so no GPT-5.5-Pro recommendation was available to incorporate or defer. No `notify_ben: true` or `strategic_change_level: major` review header was available.
- Experiment run: `.venv-conda/bin/python -m ohdyn.compare_pressure --medium-pressure-baseline-config configs/a2_attention_high_pressure.yaml --medium-pressure-variant-config configs/a2_attention_research_heavy_high_pressure.yaml --medium-pressure-internal-improvement-config configs/a2_attention_internal_improvement_high_pressure.yaml --high-pressure-baseline-config configs/a2_attention_extreme_pressure.yaml --high-pressure-variant-config configs/a2_attention_research_heavy_extreme_pressure.yaml --high-pressure-internal-improvement-config configs/a2_attention_internal_improvement_extreme_pressure.yaml --seeds 1 2 3 4 5 --out runs/a2_attention_extreme_pressure_compare_seed1_5_20260624` completed successfully.
- Analysis run: `.venv-conda/bin/python -m ohdyn.analyze_pressure --pressure-dir runs/a2_attention_extreme_pressure_compare_seed1_5_20260624 --out runs/a2_attention_extreme_pressure_analysis_seed1_5_20260624 --limit 10` completed successfully.
- Result: the full five-seed extreme-pressure run keeps the strongest pressure response on baseline final queue depth medium-to-high slope (`40.5`), with condition means `18.4 -> 42.6 -> 58.8`, normal-to-medium slope `30.25`, curvature `10.25`, and high-minus-normal delta `40.4`. The last prefix `1,2,3,4` still selects a different queue-depth response, internal-improvement final queue depth normal-to-medium slope, so the global top response is stable for prefixes `1,2` and `1,2,3` but not for all prefixes. The top value-yield divergence is baseline medium-to-high slope: completion-normalized yield improves (`0.09805`) while effort-normalized yield degrades (`-0.648355`); it is stable for prefixes `1,2,3` and `1,2,3,4` but not for all prefixes. The strongest class-specific capture-pressure response shifted from peak internal-improvement capture pressure in smaller prefixes to internal-improvement policy final long-term-research capture-pressure curvature (`0.295168`) in the full run, with only the last prefix matching the full selection.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure_comparison or pressure_summary or pressure_analysis or value_yield"` passed with `57 passed, 452 deselected in 43.35s`.
- Blockers: none.
- Next step: run the same extreme-pressure comparison and analysis across seeds `1 2 3 4 5 6 7` to check whether the last-prefix queue-depth disagreement and class-capture-pressure prefix shift resolve.
