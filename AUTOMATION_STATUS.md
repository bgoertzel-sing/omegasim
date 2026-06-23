# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 deterministic attention-policy comparison experiments on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 internal-improvement attention fixture and three-policy comparison
- Changed: added `configs/a2_attention_internal_improvement.yaml` with a 0.55 internal-improvement share; extended `ohdyn.compare_attention` so the default deterministic comparison now runs smoke baseline, research-heavy, and internal-improvement-heavy policies across the seed set; added per-class completed-work totals for near-term external, long-term research, internal improvement, and housekeeping to `comparison_metrics.csv`; updated aggregate `summary.md` deltas to compare each non-baseline policy against baseline; documented the new fixture and three-policy comparison in `README.md`; added regression coverage for loading the new fixture, three-policy aggregate artifact shape, research-heavy shift, and internal-improvement shift.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "a2_attention" -q` passed with 10 tests and 421 deselected; `.venv-conda/bin/python -m ruff check ohdyn/compare_attention.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 431 tests; `tmpdir=$(mktemp -d); .venv-conda/bin/python -m ohdyn.compare_attention --seeds 1 2 3 --out "$tmpdir/a2_compare" && find "$tmpdir/a2_compare" -maxdepth 2 -type f | sort` passed and produced comparison plus baseline, research-heavy, and internal-improvement per-run artifacts; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add deterministic A2 phase-space summary outputs for attention-policy comparisons, starting with aggregate queue-depth, stale-age, value-throughput, and per-class completion trajectory columns that can support later attractor analysis.
