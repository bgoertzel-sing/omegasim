# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 attention-allocation smoke experiments on top of the stable deterministic A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 attention-policy smoke fixture and opt-in metrics
- Changed: added strict `attention_policy` YAML loading for the four documented attention classes, an `a2_attention_smoke` fixture, deterministic task-class assignment and under-served-class work selection, opt-in per-class queue/completion/age/share/deviation/value-weighted metrics, manifest/summary provenance for attention runs, README smoke documentation, and focused reproducibility tests while preserving A0/A1 schemas for configs without `attention_policy`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "a2_attention" -q` passed with 3 tests and 421 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 424 tests.
- Blockers: none.
- Next step: add an A2 comparison fixture with a contrasting attention policy and a focused test or script that compares value-weighted throughput and stale-task age against `configs/a2_attention_smoke.yaml`.
