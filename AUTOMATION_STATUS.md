# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A0 manifest provenance update
- Changed: added deterministic run provenance to `manifest.yaml`, including git commit, Python version, and package versions for the declared runtime dependencies.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 8 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` produced `manifest.yaml`, `metrics.csv`, `events.csv`, `summary.md`, and the saved config.
- Blockers: none for local OmegaSim execution; sandbox policy rejected an attempted pre-smoke `rm -rf runs/a0_seed1`, so the smoke command was run without destructive cleanup.
- Next step: add A1 per-tick NetworkX graph summary metrics for bus density and centralization.
