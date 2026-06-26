# A5 Residual Accounting Analyzer Audit

## Scope

This bounded audit checked `ohdyn.analyze_a5_residual_accounting` against
`docs/a5_residual_accounting_diagnostic_design.md` before any broader A5 seed
sweep. It did not add simulator mechanics, multi-hive coupling, external
services, dashboards, or new lobe architectures.

The latest external strategic review recommended no repository-changing work
unless a concrete artifact bug or new preregistered design existed. The
repository status file identifies Ben's A5 preregistration as the active
reopened design, so this run kept the review's scientifically sensible
constraint by making an analyzer-only audit rather than extending seeds or
adding mechanics.

## Analyzer Changes

- Added missing lag-2 residual-state autocorrelation.
- Added nearest-return-time mean and nearest-return-time entropy as scalar
  summaries of the preregistered return-time histogram requirement.
- Added an explicit `summary.md` promotion-rule audit for intermediate
  predictors against reactive, shuffled, oracle, and guardrail criteria.
- Added `oracle_minus_linear` residual-accounting effects so both intermediate
  conditions have oracle comparison rows.

## Verification

```bash
.venv-conda/bin/python -m py_compile ohdyn/analyze_a5_residual_accounting.py
.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_a5_predictive_control_smoke_records_forecast_metrics tests/test_run_harness.py::test_a5_predictive_control_comparison_runs_matched_conditions tests/test_run_harness.py::test_a5_residual_accounting_analyzes_existing_comparison -q
.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6 --out runs/a5_predictive_control_audit_seed5_6_20260626
.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir runs/a5_predictive_control_audit_seed5_6_20260626 --out runs/a5_residual_accounting_audit_seed5_6_20260626
```

The focused pytest slice passed with `3 passed`. The fresh analyzer CLI wrote
`600` metric rows and `360` effect rows. Its promotion audit failed closed:
linear and nonlinear improved forecast skill versus reactive and shuffled, but
neither satisfied the full-accounting residual-structure criteria, and neither
passed zero-tolerance guardrails versus reactive.

## Decision

Do not promote A5 from this two-seed pilot. The analyzer now maps the current
pilot to the preregistered decision rule more explicitly, and the bounded result
remains pipeline evidence rather than evidence for residual structured
predictive dynamics.
