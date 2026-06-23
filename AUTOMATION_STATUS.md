# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 deterministic phase-space derivative summaries for attention-policy comparison experiments on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 comparison phase-space step-delta summaries
- Changed: extended `ohdyn.compare_attention` so `comparison_metrics.csv` records deterministic pipe-delimited first differences for queue depth, queued-task mean age, and value-weighted completed work; added per-policy derivative summary means/min/max plus baseline-delta comparisons for those step deltas; documented the derivative columns in `README.md`; added regression coverage that reconstructs step deltas from trajectory columns and checks summary visibility.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "a2_attention_comparison_runner_writes_aggregate_summary or a2_attention_comparison_runner_is_reproducible" -q` passed with 2 tests and 429 deselected; `.venv-conda/bin/python -m ruff check ohdyn/compare_attention.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed; `tmpdir=$(mktemp -d); .venv-conda/bin/python -m ohdyn.compare_attention --seeds 1 2 3 --out "$tmpdir/a2_compare" && sed -n '1,3p' "$tmpdir/a2_compare/comparison_metrics.csv" && sed -n '1,80p' "$tmpdir/a2_compare/summary.md"` passed and showed the new step-delta columns plus aggregate derivative means/min/max; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 431 tests.
- Blockers: none.
- Next step: add a deterministic A2 phase-space regime label in the comparison summary using queue-depth, stale-age, and value-throughput step-delta signs.
