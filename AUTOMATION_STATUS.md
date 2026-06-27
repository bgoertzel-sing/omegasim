# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Ben accepted proceeding to A7 on 2026-06-27, as recorded in
`docs/omegasim_provisional_experiment_roadmap.md`. A5 and A6/A6.1/A6.2 remain
closed under their preregistered decision rules and should not be broadened or
rescued by additional seed sweeps.

A7 is the current preregistered direction: a single-hive semantic-field design
gate for source-accounted semantic/artifact fields and logistic inter-agent
dependence. The current A7 gate is intentionally pre-mechanics. It freezes
field names, source ledgers, null conditions, utility/update-equation text,
schemas, fixture stubs, a placeholder comparison envelope, and a read-only
analyzer that fails closed until real A7 artifacts exist.

The external strategic review in
`../outputs/strategy-reviews/omegasim/latest-review.md` recommended verifying
the guard state and creating the A7 implementation contract before simulator
mechanics. That recommendation is incorporated. `notify_ben: false` and
`strategic_change_level: none`; no Ben notification is required from the review
header.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Do not make attractor, lobe, synchrony, or
semantic-dynamics claims from A7 placeholders.

## Latest Changes

- Updated `ohdyn.automation_guard` so the accepted A7 roadmap can reopen the
  loop when stale A5 closure/status wording would otherwise force a no-op.
  Temporary test status files do not read the repository roadmap unless a
  matching roadmap path is passed explicitly.
- Added a regression test for the exact transition: closed A5 status plus an
  accepted roadmap stating that Ben accepted A7 and that the roadmap replaces
  the closed A5 no-op posture.
- Reconfirmed the existing A7 implementation gate remains pre-mechanics:
  `ohdyn/a7_semantic_field_contract.py`,
  `docs/a7_implementation_gate.md`,
  `ohdyn/compare_a7_semantic_field.py`, and
  `ohdyn/analyze_a7_semantic_field.py`.
- No simulator mechanics, real integrations, dashboards, LLM calls, seed
  sweeps, or downstream multi-hive coupling were added.

## Verification

- `.venv-conda/bin/python -m ohdyn.automation_guard` passed with `state: open`,
  `should_noop: false`, and `closed_reasons: []`.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py
  ohdyn/a7_semantic_field_contract.py ohdyn/analyze_a7_semantic_field.py
  ohdyn/compare_a7_semantic_field.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a7 or automation_guard'` passed: `16 passed, 596 deselected`.
- `.venv-conda/bin/python -m ohdyn.compare_a7_semantic_field --seeds 1 2
  --out runs/a7_semantic_field_placeholder_smoke_20260627` passed and wrote
  12 config/manifest-only placeholder runs for six frozen A7 conditions.
- `.venv-conda/bin/python -m ohdyn.analyze_a7_semantic_field --compare-dir
  runs/a7_semantic_field_placeholder_smoke_20260627 --out
  runs/a7_semantic_field_analysis_smoke_20260627` passed with
  `status: fail_closed_missing_schema`, `run_count: 12`,
  `condition_count: 6`, and `seed_count: 2`.

## Blockers

None for this bounded guard/status repair. Scientifically, A7 still has no
simulator mechanics or positive evidence; the placeholder comparison and
fail-closed analyzer are schema/contract scaffolding only.

## Recommended Next Step

Implement the smallest opt-in A7 simulator mechanics behind `semantic_field`,
then run only a seed-1 schema smoke against the frozen six-condition gate.
