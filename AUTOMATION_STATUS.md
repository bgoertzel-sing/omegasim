# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI run-field parity regression
- Changed: added `test_documented_cli_config_manifest_and_summary_run_fields_match_across_full_output_fixtures` and `_assert_config_manifest_and_summary_run_fields_match` in `tests/test_run_harness.py` to verify documented full-output CLI runs keep normalized `config.yaml` aligned with manifest top-level run fields and `summary.md` experiment id, seed, tick, and agent lines for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`. Simulator behavior and output schemas were unchanged.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "config_manifest_and_summary_run_fields_match" -q` passed with 2 tests and 143 deselected; `.venv-conda/bin/python -m pytest -q` passed with 145 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that documented full-output runs keep manifest `model.agent_ids` and `model.roles` aligned with the 15-agent OmegaHive baseline identity/role cycle across both full-output fixtures.
