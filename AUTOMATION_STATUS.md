# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 deterministic attention-policy comparison experiments on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 deterministic attention comparison runner
- Changed: added `ohdyn.compare_attention`, a bounded CLI/module that runs the smoke and research-heavy A2 attention fixtures across a seed set, writes normal per-policy/seed run artifacts, and emits reproducible `comparison_metrics.csv` plus aggregate `summary.md` with value-weighted throughput, queue depth, stale-task age, long-term research completions, and near-term external completions. Documented `python -m ohdyn.compare_attention --seeds 1 2 3 --out runs/a2_attention_compare` in `README.md` and added regression tests for aggregate artifact shape, byte reproducibility across parent output directories, and research-heavy aggregate shift.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "a2_attention_comparison_runner" -q` passed with 3 tests and 426 deselected; `.venv-conda/bin/python -m ruff check ohdyn/compare_attention.py tests/test_run_harness.py` passed; `tmpdir=$(mktemp -d); .venv-conda/bin/python -m ohdyn.compare_attention --seeds 1 2 3 --out "$tmpdir/a2_compare" && find "$tmpdir/a2_compare" -maxdepth 2 -type f | sort` passed and produced comparison plus per-run artifacts; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 429 tests.
- Blockers: none.
- Next step: add one additional A2 attention-policy fixture that stresses internal-improvement share and compare it against the existing smoke and research-heavy policies with the deterministic comparison runner.
