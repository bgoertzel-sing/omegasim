# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Source-of-truth status: the current recurring automation prompt explicitly
selects A5 single-hive anticipatory predictive-control dynamics as the bounded
scientific stage. The active preregistration is
`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.

Current active task: preserve the concise A5 preregistration, keep the existing
deterministic single-hive scaffold as the only authorized smoke/pilot surface,
and avoid broad new mechanics. The earlier closed/no-op posture is overridden
only for this preregistration/status/scaffold-verification pass.

Current interpretation boundary: the repeated bounded seed `5,6` A5
smoke/analyzer results improved forecast skill for intermediate predictors,
but residual/null, oracle-nontriviality, compression, and guardrail promotion
criteria remained fail-closed. No residual-structure, strange-attractor-like,
lobe-like, semantic-dynamics, or phase-structure claim is supported.

Out of scope for this stage: real LLM calls, dashboards, Lean, Slack, browser
automation, Atomspace integrations, live task boards, A7-family mechanics,
broad A5 tuning, wider seed sweeps, and downstream three-hive coupling.

## Latest Changes

- 2026-06-30 00:05 PDT A5 bounded preregistration checkpoint: added a dated
  checkpoint to
  `docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`
  confirming that the recurring prompt still selects the bounded A5
  single-hive preregistration/scaffold stage and does not broaden mechanics.
- 2026-06-30 00:05 PDT A5 bounded status reconciliation: replaced the stale
  recovery/no-op top-level status with the current explicitly requested A5
  preregistration/scaffold boundary. The existing deterministic scaffold
  remains sufficient for smoke/pilot verification; no simulator mechanics,
  dashboards, external integrations, A7-family work, or multi-hive coupling
  were added.

## Verification

- 2026-06-30 00:05 PDT A5 bounded preregistration checkpoint:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  passed with `30 passed, 647 deselected`.
- 2026-06-30 00:05 PDT A5 bounded preregistration checkpoint:
  `.venv-conda/bin/python -m py_compile ohdyn/config.py ohdyn/sim.py
  ohdyn/io.py ohdyn/compare_predictive_control.py
  ohdyn/analyze_a5_residual_accounting.py ohdyn/automation_guard.py
  tests/test_run_harness.py` passed.
- 2026-06-30 00:05 PDT A5 bounded preregistration checkpoint:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `a5_preregistration_active=true`, `state=open`, `should_noop=false`,
  `repo_write_allowed=true`, `closed_reasons=[]`, `notify_ben=true`,
  `strategic_change_level=major`, and the current A5 next action.
- 2026-06-30 00:05 PDT A5 bounded preregistration checkpoint:
  `git diff --check` passed.

## Blockers

No environment blocker. Scientific promotion remains blocked by the existing
fail-closed A5 smoke/analyzer evidence: intermediate predictors have not passed
the preregistered residual/null, oracle-nontriviality, compression, and
guardrail criteria.

## Recommended Next Step

- Recommended next step: review the existing bounded A5 seed `5,6`
  smoke/analyzer result before authorizing any larger A5 holdout.
