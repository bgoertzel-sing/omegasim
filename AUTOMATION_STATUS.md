# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Source-of-truth status: Ben's 2026-06-30 automation prompt explicitly reopens
the bounded A5 single-hive anticipatory predictive-control stage. This
overrides the prior closed/no-op recommendation for this bounded
preregistration/scaffold stage only.

The active source of truth is
`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`. That
document defines the deterministic single-hive setup, predictor/null grid,
resource-bounded prediction hypothesis, accounting locks, endpoints,
guardrails, and fail-closed interpretation boundary. The existing
deterministic single-hive scaffold and read-only residual accounting are the
only authorized implementation surface for this pass.

Interpretation boundary: prior bounded A5 seed `5,6` smoke/analyzer results
improved forecast skill for intermediate predictors, but residual/null,
oracle-nontriviality, compression, and guardrail promotion criteria did not
pass. No residual-structure, strange-attractor-like, lobe-like,
phase-structure, semantic-dynamics, or causal collective-structure claim is
supported.

Out of scope for this reopened bounded stage: real LLM calls, dashboards,
Lean, Slack, browser automation, Atomspace integrations, live task boards,
broad A5 rescue tuning, new A5 predictor families, broad seed sweeps, A7-family
mechanics, analyzer rescue diagnostics, and downstream multi-hive coupling.

## Latest Changes

- 2026-06-30 01:05 PDT A5 status reconciliation: restored the bounded
  single-hive A5 preregistration/scaffold as the active stage for the current
  automation prompt while keeping broader mechanics out of scope.
- 2026-06-30 01:05 PDT preregistration checkpoint: added a dated note to the
  concise A5 preregistration recording that the current prompt overrides the
  prior closed/no-op recommendation only for this bounded stage.
- 2026-06-30 01:05 PDT guard reconciliation: narrowed
  `ohdyn.automation_guard` so an explicit current A5 override can reopen this
  stage even when a stale PAUSE-RECOVER review remains present.

## Verification

- 2026-06-30 01:05 PDT guard reconciliation:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported `state=open`,
  `should_noop=false`, `repo_write_allowed=true`, `notify_ben=true`, and the
  bounded A5 scaffold review next action.
- 2026-06-30 01:05 PDT focused tests:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  passed (`32 passed, 647 deselected`).
- 2026-06-30 01:05 PDT bounded A5 smoke/analyzer:
  `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6 --out /tmp/omegasim_a5_current_20260630_qOFQMt/compare`
  and
  `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir /tmp/omegasim_a5_current_20260630_qOFQMt/compare --out /tmp/omegasim_a5_current_20260630_qOFQMt/analysis`
  completed. The analyzer emitted 1280 residual metric rows and 720 effect
  rows. Promotion remained fail-closed for linear, nonlinear, and high-budget
  nonlinear predictors.
- 2026-06-30 01:05 PDT syntax and whitespace checks:
  `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py ohdyn/compare_predictive_control.py ohdyn/analyze_a5_residual_accounting.py tests/test_run_harness.py`
  passed, and `git diff --check` passed.

## Blockers

Scientific promotion remains blocked by prior fail-closed A5 evidence. Any
larger A5 holdout, new predictor family, A5 rescue diagnostic, A7-family work,
or three-hive delayed anticipatory coupling requires a separate future
preregistration or explicit Ben decision.

## Recommended Next Step

- Recommended next step: review the current bounded A5 seed `5,6`
  smoke/analyzer fail-closed output and decide whether a separately
  preregistered larger holdout is scientifically warranted.
