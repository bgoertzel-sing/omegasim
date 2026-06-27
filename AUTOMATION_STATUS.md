# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

This run is scoped to Ben's explicitly requested **A5 anticipatory
predictive-control dynamics** thread. The requested A5 preregistration and the
minimal deterministic single-hive scaffold already exist, including matched
reactive, linear, nonlinear, oracle, and budget-matched timing-broken null
conditions.

The current A5 focus is the narrow follow-up question left by the completed
pilot and confirmatory evidence: why did bounded predictors improve forecast
skill while failing the preregistered full-accounting residual-structure
promotion gate?

The broader post-A5 roadmap still points to A6 as the next implementation
stage. This A5 run does not add real LLM calls, dashboards, Lean, Slack,
browser automation, Atomspace integrations, live task boards, broad three-hive
mechanics, or new simulator dynamics.

## Latest Changes

- Status: A5 forecast-skill/residual-gap diagnostic plan added, 2026-06-27.
- Changed: added
  `docs/a5_forecast_skill_residual_gap_diagnostic_plan.md`, a bounded
  read-only plan for explaining why forecast-skill gains in A5 did not survive
  residual accounting.
- Changed: the plan freezes candidate explanations, source artifacts,
  read-only checks, and fail-closed decision rules. It explicitly does not
  promote A5 or authorize new mechanics, multi-hive coupling, external
  integrations, dashboards, or a larger seed sweep.
- Changed: `README.md` now points readers from the A5 smoke/analyzer section to
  the new residual-gap diagnostic plan.
- Verification: `.venv-conda/bin/python -m pytest tests/test_run_harness.py
  -q -k 'a5 or automation_guard'` passed with `10 passed, 586 deselected`;
  `git diff --check` passed.
- Blockers: none.
- Recommended next step: write a concise read-only A5 residual-gap report over
  the existing seed `7..16` artifacts, choosing accounting-confirmed closure,
  analyzer refinement, or a separately preregistered future design.
