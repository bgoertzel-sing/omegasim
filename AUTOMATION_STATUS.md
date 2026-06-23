# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 deterministic phase-space regime labeling for attention-policy comparison experiments on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 comparison phase-space regime labels
- Changed: extended `ohdyn.compare_attention` aggregate `summary.md` with a deterministic `## Phase-space regimes` section that labels each policy from the signs of mean queue-depth, queued-age, and value-throughput step deltas; documented the label convention in `README.md`; added regression coverage for the new section and baseline label visibility.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "a2_attention_comparison_runner_writes_aggregate_summary or a2_attention_comparison_runner_is_reproducible" -q` passed with 2 tests and 429 deselected; `.venv-conda/bin/python -m ruff check ohdyn/compare_attention.py tests/test_run_harness.py` passed; `tmpdir=$(mktemp -d); .venv-conda/bin/python -m ohdyn.compare_attention --seeds 1 2 3 --out "$tmpdir/a2_compare" && sed -n '1,90p' "$tmpdir/a2_compare/summary.md"` passed and showed the new phase-space regime section; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 431 tests.
- Blockers: none.
- Next step: add deterministic per-policy phase-space regime counts from per-run step-delta sign sequences.
