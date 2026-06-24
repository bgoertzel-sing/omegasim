# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response metric refinement on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 ran the compact A2 pressure-response analysis sweep requested by the previous next step and added a deterministic value-yield metric.
- Changed: no real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace integrations, multi-hive coupling, A0/A1 scheduling, or agent population changes; A2 attention runs now emit `attention_value_per_completed_task_tick` and `attention_value_per_completed_task_total`; comparison and pressure artifacts now carry value-per-completed-task totals, trajectories, step deltas, high-minus-normal deltas, and pressure-curve slopes/curvature; README and tests document/pin the new fields.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 --out runs/a2_attention_value_yield_probe_20260624 && .venv-conda/bin/python -m ohdyn.analyze_pressure --pressure-dir runs/a2_attention_value_yield_probe_20260624 --out runs/a2_attention_value_yield_probe_20260624_analysis --limit 12` passed; the new value-yield observable appears in `summary.md` and the pressure-response ranking, below the existing value-throughput and queue-depth leaders for seeds 1,2.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'attention_run_records_policy_metrics or comparison_runner_writes_aggregate_summary or pressure_comparison_runner'` passed with 5 selected tests; `.venv-conda/bin/python -m ruff check ohdyn tests` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 491 tests.
- Blockers: none.
- Next step: inspect the new value-yield pressure curves across the full default seed set (`1 2 3`) and decide whether the next simulator metric should separate completed-task class mix from task-work effort.
