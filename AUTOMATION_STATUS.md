# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 deterministic phase-space summaries for attention-policy comparison experiments on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 comparison phase-space trajectory columns
- Changed: extended `ohdyn.compare_attention` so `comparison_metrics.csv` records deterministic pipe-delimited trajectories for queue depth, queued-task mean age, value-weighted completed work, and each attention class's completed-work totals; added aggregate summary fields that cross-check final trajectory means against final-state means; documented the trajectory columns in `README.md`; added regression coverage for trajectory column shape and final-value alignment.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "a2_attention_comparison_runner_writes_aggregate_summary or a2_attention_comparison_runner_is_reproducible" -q` passed with 2 tests and 429 deselected; `.venv-conda/bin/python -m ruff check ohdyn/compare_attention.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed; `tmpdir=$(mktemp -d); .venv-conda/bin/python -m ohdyn.compare_attention --seeds 1 2 3 --out "$tmpdir/a2_compare" && sed -n '1,3p' "$tmpdir/a2_compare/comparison_metrics.csv" && sed -n '1,80p' "$tmpdir/a2_compare/summary.md"` passed and showed the new trajectory columns plus aggregate trajectory-final means; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 431 tests.
- Blockers: none.
- Next step: add a deterministic A2 phase-space derivative summary that reports per-policy queue-depth, stale-age, and value-throughput step deltas from the new trajectory columns.
