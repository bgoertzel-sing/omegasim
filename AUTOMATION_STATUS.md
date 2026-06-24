# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response metric refinement on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 ran the full default-seed A2 value-yield pressure inspection and added deterministic effort-normalized value metrics.
- Changed: no real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace integrations, multi-hive coupling, A0/A1 scheduling, or agent population changes; A2 attention runs now emit per-class cumulative work-event totals plus `attention_value_per_work_event_tick` and `attention_value_per_work_event_total`; comparison and pressure artifacts now carry value-per-work-event totals, trajectories, step deltas, high-minus-normal deltas, and pressure-curve slopes/curvature; README and tests document/pin the new fields.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 3 --out runs/a2_attention_value_effort_full_seed_probe_20260624 && .venv-conda/bin/python -m ohdyn.analyze_pressure --pressure-dir runs/a2_attention_value_effort_full_seed_probe_20260624 --out runs/a2_attention_value_effort_full_seed_probe_20260624_analysis --limit 15` passed; value per work event appears in `summary.md` and the pressure-response ranking, below the queue-depth and value-throughput leaders. For seeds `1,2,3`, baseline `value_per_work_event_mean_delta=0.087794`, research-heavy `-0.036446`, and internal-improvement `-0.026027`, separating effort-normalized value from value per completed task.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'attention_run_records_policy_metrics or comparison_runner_writes_aggregate_summary or pressure_comparison_runner_writes_fixed_policy_deltas or trajectory_pressure'` passed with 5 selected tests; `.venv-conda/bin/python -m ruff check ohdyn tests` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 491 tests.
- Blockers: none.
- Next step: use the new value-per-work-event curves to add a compact A2 summary interpretation that contrasts value throughput, value per completed task, and value per work event for each fixed policy.
