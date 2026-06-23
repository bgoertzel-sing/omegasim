# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 attention-share capture-pressure telemetry on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added deterministic A2 capture-pressure metrics and events.
- Changed: no scheduling behavior changes; attention-policy runs now emit per-class `attention_<class>_capture_pressure_tick` metrics, `attention_capture_pressure_max_tick`, and `attention_capture_pressure` events when quota balancing works one class while another available queued class is above its target share. A0/A1 manifests keep the baseline event vocabulary; attention manifests append the attention event vocabulary. README and tests document and verify the new telemetry.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/sim.py ohdyn/io.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_manifest_records_event_schema_provenance tests/test_run_harness.py::test_documented_cli_events_per_tick_action_counts_match_metrics_top_level_action_totals_across_full_output_fixtures tests/test_run_harness.py::test_a2_attention_run_records_policy_metrics_and_summary` passed with 5 selected tests; `.venv-conda/bin/python -m pytest` passed with 454 tests.
- Blockers: none.
- Next step: add capture-pressure trajectories and summary aggregates to the deterministic A2 attention comparison output.
