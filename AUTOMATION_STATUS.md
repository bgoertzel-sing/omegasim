# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 environment recovery and A0 guardrail update
- Changed: fixed package discovery for editable installs, ignored the local `.venv-conda`, tightened A0/A1 config validation to require 15 agents and real YAML booleans, and made the manifest list only artifacts actually written.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 7 tests; `.venv-conda/bin/python -c "import pytest, yaml"` succeeded.
- Blockers: none for local OmegaSim execution.
- Next step: resume the OmegaSim research automation on top of the now-working Python 3.11 environment.
