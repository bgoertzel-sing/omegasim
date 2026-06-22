# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 manifest-only reordered-action CLI rerun collision coverage
- Changed: added documented CLI rerun coverage proving `configs/a0_manifest_only_reordered_actions.yaml` refuses to overwrite existing enabled `config.yaml` and `manifest.yaml` artifacts, omits disabled `metrics.csv`/`events.csv`/`summary.md` from the collision message, avoids tracebacks, preserves the first run byte-for-byte, and keeps normalized reordered-action manifest provenance intact.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_only_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts" -q` passed with 1 test and 370 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 371 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add run API rerun collision coverage for the manifest-only reordered-action fixture, matching the documented CLI behavior and preserving reordered-action manifest provenance.
