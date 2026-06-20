# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI optional-output regression
- Changed: added a documented CLI regression for `python -m ohdyn.run --config <minimal-output-config> --seed 17 --out ...` with metrics/events/summary disabled; it asserts the CLI writes only `config.yaml` and `manifest.yaml`, records the exact artifact list and output flags in `manifest.yaml`, and does not create disabled artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_respects_disabled_optional_outputs -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 43 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a CLI smoke regression for a documented run with `write_manifest: false` that writes only `config.yaml` plus enabled non-manifest artifacts and exits cleanly.
