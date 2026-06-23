# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 deterministic task creation pressure sensitivity fixtures for attention-policy comparison experiments on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 task creation pressure sensitivity fixtures
- Changed: added `model.task_creation_pressure` config loading with default `1.0` and deterministic scaling of the existing `create_task` action weight; added high-pressure A2 baseline, research-heavy, and internal-improvement fixtures at pressure `1.8`; documented the high-pressure comparison command in `README.md`; added regression coverage for fixture loading, higher same-seed task creation/backlog pressure, and reproducible high-pressure comparison artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "high_pressure or loads_a0_smoke_config or manifest_and_config_match_documented_a0_provenance_schema" -q` passed with 7 tests and 429 deselected; `.venv-conda/bin/python -m ruff check ohdyn/config.py ohdyn/sim.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 436 tests; `tmpdir=$(mktemp -d); .venv-conda/bin/python -m ohdyn.compare_attention --baseline-config configs/a2_attention_high_pressure.yaml --variant-config configs/a2_attention_research_heavy_high_pressure.yaml --internal-improvement-config configs/a2_attention_internal_improvement_high_pressure.yaml --seeds 1 2 3 --out "$tmpdir/a2_attention_high_pressure_compare" && sed -n '1,90p' "$tmpdir/a2_attention_high_pressure_compare/summary.md"` passed and showed deterministic high-pressure policy means plus phase-space regime distribution deltas.
- Blockers: none.
- Next step: add an aggregate comparison helper that runs normal-pressure and high-pressure policy sets together and reports fixed-policy pressure deltas in phase-space regime distributions.
