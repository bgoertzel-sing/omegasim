# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI manifest-disabled regression
- Changed: added a documented CLI regression for `python -m ohdyn.run --config <no-manifest-config> --seed 17 --out ...` with `write_manifest: false` and metrics/events/summary enabled; it asserts the CLI exits cleanly, writes only `config.yaml`, `metrics.csv`, `events.csv`, and `summary.md`, preserves normalized output flags in `config.yaml`, omits `manifest.yaml`, and emits the expected 3 metric rows plus 45 event rows.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_respects_disabled_manifest_output -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 44 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a reproducibility regression proving same-seed CLI runs with `write_manifest: false` produce byte-identical `config.yaml`, `metrics.csv`, `events.csv`, and `summary.md` artifacts.
