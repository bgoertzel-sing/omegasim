# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI subprocess helper cleanup
- Changed: added `_run_documented_cli` in `tests/test_run_harness.py` and reused it across successful documented-CLI tests, including the newest manifest lobe fields regression, while leaving negative CLI subprocess tests explicit so their stderr/nonzero-return assertions stay local.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli or cli_config_only" -q` passed with 79 tests and 98 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 177 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused regression that `summary.md` lobe totals only report labels present in `manifest.yaml` `model.baseline_lobes.labels` for both full-output fixtures.
