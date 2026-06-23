# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 deterministic baseline-relative phase-space regime distribution summaries for attention-policy comparison experiments on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 comparison phase-space regime distribution deltas
- Changed: extended `ohdyn.compare_attention` aggregate `summary.md` with a deterministic `## Phase-space regime distribution deltas vs baseline` section that compares each variant policy's per-step phase-space regime count/rate distribution against the baseline; documented the baseline-relative regime delta output in `README.md`; added regression coverage for the new section and representative deterministic deltas.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "a2_attention_comparison_runner_writes_aggregate_summary or a2_attention_comparison_runner_is_reproducible" -q` passed with 2 tests and 429 deselected; `.venv-conda/bin/python -m ruff check ohdyn/compare_attention.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 431 tests; `tmpdir=$(mktemp -d); .venv-conda/bin/python -m ohdyn.compare_attention --seeds 1 2 3 --out "$tmpdir/a2_compare" && sed -n '25,80p' "$tmpdir/a2_compare/summary.md"` passed and showed deterministic baseline-relative regime count/rate deltas.
- Blockers: none.
- Next step: add deterministic attention-policy sensitivity fixtures for task creation pressure so phase-space regime distributions can be compared across both policy shares and backlog pressure.
