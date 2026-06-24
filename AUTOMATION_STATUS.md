# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure/attention experiments are now testing whether the extreme-pressure endpoint changes the pressure-response interpretation across seed prefixes. The current priority is to distinguish stable queue-depth pressure effects from seed-sensitive value-yield divergence signals before adding new model mechanisms.

## Latest Run

- Status: ok, 2026-06-24 ran the documented extreme-pressure comparison across seeds `1 2 3` and analyzed the resulting pressure-response rankings.
- Changed: generated local ignored artifacts under `runs/a2_attention_extreme_pressure_compare_seed1_3_20260624/` and `runs/a2_attention_extreme_pressure_analysis_seed1_3_20260624/`. No code, configs, tests, simulator mechanisms, A0/A1 scheduling, task policy shares, output schemas, real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace integrations, or multi-hive coupling were changed.
- Strategic review: `../outputs/strategy-reviews/omegasim/latest-review.md` was not present, so no GPT-5.5-Pro recommendation was available to incorporate or defer. No `notify_ben: true` or `strategic_change_level: major` review header was available.
- Experiment run: `.venv-conda/bin/python -m ohdyn.compare_pressure --medium-pressure-baseline-config configs/a2_attention_high_pressure.yaml --medium-pressure-variant-config configs/a2_attention_research_heavy_high_pressure.yaml --medium-pressure-internal-improvement-config configs/a2_attention_internal_improvement_high_pressure.yaml --high-pressure-baseline-config configs/a2_attention_extreme_pressure.yaml --high-pressure-variant-config configs/a2_attention_research_heavy_extreme_pressure.yaml --high-pressure-internal-improvement-config configs/a2_attention_internal_improvement_extreme_pressure.yaml --seeds 1 2 3 --out runs/a2_attention_extreme_pressure_compare_seed1_3_20260624` completed successfully.
- Analysis run: `.venv-conda/bin/python -m ohdyn.analyze_pressure --pressure-dir runs/a2_attention_extreme_pressure_compare_seed1_3_20260624 --out runs/a2_attention_extreme_pressure_analysis_seed1_3_20260624 --limit 10` completed successfully.
- Result: the full three-seed extreme-pressure run changed the one-seed interpretation. The strongest pressure response is now baseline final queue depth medium-to-high slope (`45.0`), with condition means `21.333333 -> 44.666667 -> 62.666667`; baseline value-weighted completed-work curvature fell to rank 8 (`-24.583332`). The last seed prefix `1,2` agrees with the full-seed top global response, but all-prefix stability is still false because seed `1` alone selected baseline value-weighted completed-work curvature. The strongest class-specific capture-pressure response is stable across all prefixes: internal-improvement policy, peak internal-improvement capture-pressure curvature (`-0.401804`). The top value-yield divergence is baseline medium-to-high slope: completion-normalized yield improves (`0.23065`) while effort-normalized yield degrades (`-0.74289`), but that divergence is not prefix-stable.
- Verified: `.venv-conda/bin/python -m pytest` passed with `509 passed in 444.34s`.
- Blockers: none.
- Next step: run the same extreme-pressure comparison and analysis across seeds `1 2 3 4 5` to check whether baseline queue-depth slope remains the top response and whether value-yield divergence stabilizes.
