# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI summary artifact/output flag parity regression
- Changed: added `test_documented_cli_summary_artifacts_and_output_flags_match_manifest_across_full_output_fixtures` and `_assert_summary_output_flags_match_config` in `tests/test_run_harness.py` to verify documented full-output CLI runs keep `summary.md` written-artifact lists aligned with `manifest.yaml` artifacts and normalized `config.yaml`/manifest output flags for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`. Simulator behavior and output schemas were unchanged.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli_summary_artifacts_and_output_flags_match_manifest_across_full_output_fixtures or documented_cli_summary_schema_provenance_counts_match_manifest" -q` passed with 4 tests and 127 deselected; `.venv-conda/bin/python -m pytest -q` passed with 131 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that full-output documented runs keep `summary.md` role/action aggregate totals aligned with the emitted `metrics.csv` role/action columns across both full-output fixtures.
