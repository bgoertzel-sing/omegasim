# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 output path file safety regression
- Changed: added a CLI regression proving an output path that already exists as a file exits nonzero, reports a clean argparse error, avoids tracebacks, and preserves the existing file contents.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_cli_output_path_file_does_not_overwrite_or_traceback -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 36 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a smoke test that the documented `python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out ...` command writes all five A0/A1 artifacts with the expected manifest artifact list.
