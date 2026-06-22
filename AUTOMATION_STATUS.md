# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 config-only reordered-action API coverage
- Changed: added `run_experiment` API coverage proving `configs/a0_config_only_reordered_actions.yaml` writes only byte-stable `config.yaml` across same-seed runs while preserving YAML action order; added API rerun collision coverage proving existing `config.yaml` blocks reruns for that fixture without treating disabled optional artifacts as collisions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "config_only_reordered_actions and run_experiment" -q` passed with 2 tests and 365 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 367 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add API stale-disabled-artifact preservation coverage for the config-only reordered-action fixture.
