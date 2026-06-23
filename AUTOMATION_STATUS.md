# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 attention-share pressure-response seed-prefix stability inspection on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added deterministic pressure-response stability-agreement summaries and ran the requested larger seed-set inspection.
- Changed: no simulator, scheduling, run harness, or CSV header behavior changes; `ohdyn.compare_pressure` summary output now includes `Pressure-response stability agreement`, comparing global top-response prefix stability with per-class capture-pressure prefix stability for every proper seed prefix. README documents the section, and the pressure-summary regression checks the new section/table.
- Larger seed inspection: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 3 4 5 --out runs/a2_attention_pressure_compare_seed1_5` completed. For seeds `1,2,3,4,5`, the global top response is `internal_improvement` final queue depth normal-to-medium slope and stabilizes starting at prefix `1,2,3`; the per-class top response is `research_heavy` peak long-term-research capture-pressure curvature and is stable for all prefixes. The stability-agreement table reports `all prefixes stable together: false` and `last prefix stable together: true`.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_summary'` passed with 9 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 457 tests.
- Blockers: none.
- Next step: add an aggregate pressure-response stability CSV so global/class prefix agreement can be consumed without parsing `summary.md`.
