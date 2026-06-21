# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI agent identity/role-cycle parity regression
- Changed: added `test_documented_cli_manifest_agent_identity_and_roles_match_baseline_across_full_output_fixtures` and `_assert_manifest_agent_identity_and_roles_match_baseline` in `tests/test_run_harness.py` to verify documented full-output CLI runs keep manifest `model.agent_ids`, `model.roles`, and role/action role provenance aligned with the 15-agent OmegaHive baseline identity/role cycle for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`. Simulator behavior and output schemas were unchanged.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "agent_identity_and_roles_match_baseline" -q` passed with 2 tests and 145 deselected; `.venv-conda/bin/python -m pytest -q` passed with 147 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that documented full-output runs keep manifest bus node/edge counts aligned with `summary.md` and the first `metrics.csv` row across both full-output fixtures.
