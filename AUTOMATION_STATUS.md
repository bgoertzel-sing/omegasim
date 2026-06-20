# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI no-manifest partial-output overwrite refusal regression
- Changed: added a documented CLI regression for `write_manifest: false` runs where the output directory already contains a subset of the enabled artifacts; the test seeds `config.yaml` and `events.csv`, proves the CLI refuses the run without a traceback, confirms `manifest.yaml` is not part of the collision set, and verifies no missing artifacts are written.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_without_manifest_refuses_partial_output_directory -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 46 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add explicit CLI invalid-seed validation coverage so non-reproducible seed inputs fail before writing any artifacts.
