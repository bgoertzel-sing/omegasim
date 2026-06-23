# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 documented-CLI same-seed reproducibility helper reuse
- Changed: added a CLI-only `_run_documented_cli_pair` helper and refactored the documented CLI same-seed byte-identical artifact tests for default outputs, full-output fixtures, smoke, and no-manifest runs to share setup while preserving their fixture-specific assertions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli_omitted_outputs_same_seed_reproduces_byte_identical_artifacts or documented_cli_full_output_fixture_same_seed_reproduces_byte_identical_enabled_artifacts or documented_cli_same_seed_reproduces_byte_identical_a0_artifacts or documented_cli_same_seed_without_manifest_reproduces_byte_identical_artifacts" -q` passed with 5 tests and 416 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: review documented-CLI different-seed pair tests for one narrow CLI-only helper reuse that reduces duplicate two-run setup without changing schema or seed-variation assertions.
