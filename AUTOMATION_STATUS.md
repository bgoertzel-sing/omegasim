# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 attention-policy comparison experiments on top of the stable deterministic A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 research-heavy attention comparison fixture
- Changed: added `configs/a2_attention_research_heavy.yaml` with higher reserved share for `long_term_research`, documented the comparison smoke command in `README.md`, and added focused tests that load the new fixture and compare same-seed outcomes against `configs/a2_attention_smoke.yaml` for research completions, near-term completions, value-weighted throughput, stale-task age, and summary output.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "a2_attention" -q` passed with 5 tests and 421 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 426 tests.
- Blockers: none.
- Next step: add a small deterministic A2 comparison CLI/script that runs both attention fixtures across a short seed set and writes an aggregate summary of value-weighted throughput and stale-task age.
