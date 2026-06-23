# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-sensitivity fixtures on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 medium-pressure fixture set
- Changed: added deterministic medium-pressure A2 fixtures at `task_creation_pressure: 1.4` for baseline, research-heavy, and internal-improvement policies; documented the medium-pressure comparison command; added regression coverage that loads all pressure fixtures and verifies the medium baseline run sits between normal and high pressure for task creation and queue depth.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure" -q` passed with 37 tests and 406 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 443 tests.
- Blockers: none.
- Next step: extend `ohdyn.compare_pressure` into a pressure-curve comparison helper that runs normal, medium, and high pressure conditions together and reports per-policy slope or curvature metrics.
