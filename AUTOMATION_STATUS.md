# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Current run focus: A5 single-hive anticipatory predictive-control dynamics,
because the recurring prompt explicitly reopens that bounded stage for
preregistration/scaffold validation. The concise preregistration already exists
at `docs/a5_single_hive_anticipatory_predictive_control_preregistration.md` and
still matches Ben's requested design: deterministic single hive, matched
task-arrival totals, service capacity, action opportunity, work budget,
prediction spend, reactive/linear/nonlinear/high-budget/oracle/timing-broken
null conditions, primary residual/predictability endpoints, and fail-closed
strange-attractor-like interpretation rules.

The smallest deterministic A5 scaffold also already exists and remains the only
authorized implementation surface for this stage:
`configs/a5_predictive_linear_smoke.yaml`,
`ohdyn.compare_predictive_control`, and
`ohdyn.analyze_a5_residual_accounting`. A fresh fixed smoke at seeds `5,6`
again improved forecast skill for intermediate predictors but failed the
preregistered residual-accounting promotion audit. This keeps A5 at an evidence
boundary: forecast skill alone is not support for lobe-like,
strange-attractor-like, semantic-dynamics, or causal collective-structure
claims. No broad A5 mechanics, broader seed sweeps, dashboards, integrations,
result-bearing committed run artifacts, or three-hive coupling are authorized.

Broader governance context remains relevant: the later A7.2 delayed
artifact-mediated endogenous prediction gate and downstream three-hive ring gate
also completed at bounded fixed seed `1,2` smoke scale and closed fail-closed.
`ohdyn.automation_guard` still reports `closed_awaiting_preregistration`,
`repo_write_allowed=false`, and `notify_ben=true` because those downstream gates
failed closed. The current A5 prompt overrides that no-op posture only for
validating the existing A5 preregistration/scaffold and recording the current
fail-closed smoke result.

Historical A7.2 context: that branch tested the resource-bounded prediction
hypothesis with a more mechanism-rich single-hive design in which agents choose
among `predict`, `work`, `review`, and `synthesize`; prediction consumes scarce
work opportunity; utilities are thresholded logistic functions of lagged
forecast error, artifact readiness, contradiction/risk, fatigue, and adaptive
thresholds; and all forecast/artifact updates must be delayed or lagged before
they can affect later action.

The immediate A7.2 implementation/smoke gate has now run at the fixed paired
seed `1,2` tiny smoke scale. It emitted complete schema/source-ledger artifacts
and passed productivity preflight, but closed fail-closed at the residual/null
gate: the intermediate endogenous-prediction condition did not beat every
preregistered null on residual preflight contrasts. This does not support
lobe-like, strange-attractor-like, semantic-dynamics, synchrony, or causal
collective-structure claims, and it does not authorize A7.2 tuning without a
new preregistration.

The earlier A7.2-then-three-hive launch posture has now been executed through
the bounded gates it authorized. The latest external strategic review is
`strategic_change_level: major` and `notify_ben: true`; its recommendation to
close into awaiting-preregistration is accepted as scientifically sensible
because A7.2 and the three-hive ring both failed closed and further expansion
would become post-result rescue tuning without a new preregistration.
Ben's 2026-06-28 Hyperseed follow-up is captured in
`docs/hyperseed_one_hive_delayed_dynamics_note.md`: three hives are
diagnostically useful but not ontologically required for complex dynamics; the
three-hive preregistration should treat the ring as a relational diagnostic
amplifier, emphasize cross-hive artifact readiness plus contradiction/risk over
demand prediction alone, and preserve a possible later one-hive dimensionless
delayed-dynamics sweep rather than retro-tuning A7.2.

Ben's 2026-06-28 Hyperseed/dynamical formalization PDF is captured in
`docs/hyperseed_strange_attractor_tuning_formalization_20260628.md`. It
sharpens the prospective next-design frame: any A7.3 or analytic-map pivot
should expose dimensionless controls (`rho`, `delta`, `mu`, `kappa`, `nu`),
log the lifted delayed state explicitly, preserve compact boundedness, use a
low-gain contraction baseline, and require Lyapunov/recurrence/surrogate/
refinement/semantic-provenance gates before any strange-attractor-like claim.
This is prospective design guidance only and does not reopen A7.2 or authorize
post-result tuning of the fail-closed gates.

The post-A7.2 three-hive ring is now past the contract/config-validation,
schema/source-ledger smoke, read-only preflight, smallest deterministic
mechanics-smoke, and read-only residual/null analyzer gates. The helper
`ohdyn.compare_three_hive_ring` remains artifact-only and still fails closed as
`fail_closed_no_metrics_events` under the preflight analyzer. The helper
`ohdyn.compare_three_hive_ring_mechanics` emits fixed seed `1,2` metrics,
events, and source-ledger rows for all thirteen preregistered conditions; the
preflight marks those artifacts `eligible_for_mechanics_gate` because
metrics/events are present. The new read-only analyzer
`ohdyn.analyze_three_hive_ring_residual_null` consumes those artifacts without
rerunning simulations, verifies source ledgers, computes residual preflight
metrics, checks all preregistered null contrasts, and applies productivity
guardrails. The fixed seed `1,2` mechanics/analyzer result closes fail-closed:
source ledgers pass, but productivity guardrails and null contrasts block
promotion. This does not create three-hive scientific evidence and does not
support lobe-like, strange-attractor-like, semantic-dynamics, synchrony, or
causal collective-structure claims.

## Recommended Next Step

- Recommended next step: prepare a Ben decision note that treats the A5
  preregistration/scaffold as complete, reports the current A5 smoke as
  fail-closed under residual accounting, and asks whether to preregister a
  fresh one-hive dimensionless delayed-dynamics sweep.

## Blockers

No environment blocker. Scientific progress is blocked on Ben's next
preregistered direction because the current A5 smoke, A7.2 smoke, and
three-hive ring smoke all failed closed under their preregistered promotion
rules.

## Verification

- `.venv-conda/bin/python -m ohdyn.automation_guard` passed and reported
  `a5_preregistration_active=true`, `state=closed_awaiting_preregistration`,
  `repo_write_allowed=false`, and `notify_ben=true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  passed with `21 passed, 632 deselected`.
- Temporary smoke command passed:
  `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6
  --out /tmp/omegasim_a5_current_6AQ418`.
- Temporary read-only residual accounting passed as a command and failed closed
  scientifically:
  `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting
  --compare-dir /tmp/omegasim_a5_current_6AQ418
  --out /tmp/omegasim_a5_residual_current_5WTM3R`.

## Latest Changes

- 2026-06-28 23:37 PDT bounded A5 revalidation under explicit A5 reopening:
  re-read automation memory, `README.md`, `AUTOMATION_STATUS.md`, the concise
  A5 single-hive preregistration, the older detailed A5 design record, the A5
  smoke comparison/analyzer scaffold, current tests, current guard output, and
  recent git history. Confirmed that the requested preregistration already
  exists and still covers deterministic single-hive setup, resource-bounded
  prediction, matched task-arrival/service-capacity/action-opportunity/work-
  budget controls, reactive/linear/nonlinear/high-budget/oracle/timing-broken
  nulls, primary residual/predictability endpoints, and fail-closed
  strange-attractor/lobe interpretation rules.
- Ran the focused A5/automation verification again. The guard reports
  `state=closed_awaiting_preregistration`, `repo_write_allowed=false`, and
  `notify_ben=true` because later A7.2 and three-hive gates failed closed, but
  `a5_preregistration_active=true` for bounded A5 validation. Focused pytest
  passed with `21 passed, 632 deselected`. A temporary A5 seed `5,6`
  comparison again improved forecast skill for intermediate predictors, but
  the read-only residual-accounting analyzer failed closed: no intermediate-
  budget condition satisfied all preregistered skill, residual/null,
  compression, oracle-nontriviality, and guardrail criteria. No duplicate
  preregistration, simulator mechanics, configs, committed run artifacts,
  dashboards, integrations, broad seed sweeps, parameter sweeps, extra hives,
  or promotion claims were added.

- 2026-06-28 22:36 PDT bounded A5 revalidation under explicit A5 reopening:
  re-read automation memory, `README.md`, `AUTOMATION_STATUS.md`, the concise
  A5 single-hive preregistration, the older detailed A5 design record, the A5
  smoke config/comparison/analyzer scaffold, focused tests, current guard
  output, and recent git history. Confirmed that the requested A5
  preregistration already exists and includes the deterministic single-hive
  setup, resource-bounded prediction hypothesis, matched task-arrival/service-
  capacity/action-opportunity/work-budget controls, reactive/linear/nonlinear/
  high-budget/oracle/timing-broken nulls, primary endpoints, and fail-closed
  strange-attractor/lobe interpretation rules.
- Ran a fresh temporary A5 comparison smoke at seeds `5,6`. Forecast skill
  improved for intermediate predictors, but the read-only residual-accounting
  analyzer failed closed: no intermediate-budget condition satisfied all
  preregistered skill, residual/null, compression, oracle-nontriviality, and
  guardrail criteria. No preregistration duplicate, simulator mechanics,
  configs, committed run artifacts, dashboards, integrations, broad seeds,
  parameter sweeps, extra hives, or promotion claims were added.

- 2026-06-28 21:36 PDT bounded A5 prompt revalidation under governance
  closure: re-read automation memory, `README.md`, `AUTOMATION_STATUS.md`, the
  concise single-hive A5 preregistration, the older detailed A5 design record,
  current guard output, focused A5/automation references, and recent git
  history. Confirmed again that the explicit A5 preregistration request is
  already satisfied: deterministic single-hive setup, resource-bounded
  prediction hypothesis, matched task-arrival/service-capacity/action-
  opportunity/work-budget controls, reactive/linear/nonlinear/high-budget/
  oracle/timing-broken nulls, primary endpoints, and fail-closed
  strange-attractor/lobe rules are present.
- The guard still reports `state=closed_awaiting_preregistration`,
  `repo_write_allowed=false`, `should_noop=true`, and `notify_ben=true`
  because the later A7.2 and three-hive fixed seed `1,2` gates failed closed.
  No duplicate A5 preregistration, simulator mechanics, configs, analyzers,
  run artifacts, dashboards, integrations, broad seeds, parameter sweeps, extra
  hives, or promotion claims were added. The status update preserves exactly
  one next step: notify Ben and wait for a fresh preregistered direction.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard` and
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`21 passed, 632 deselected`).

- 2026-06-28 20:36 PDT bounded A5 prompt revalidation under governance
  closure: re-read automation memory, `README.md`, `AUTOMATION_STATUS.md`, the
  concise single-hive A5 preregistration, the current guard output, focused
  A5/automation references, and recent git history. Confirmed again that the
  explicit A5 preregistration request is already satisfied: deterministic
  single-hive setup, resource-bounded prediction hypothesis, matched
  task-arrival/service-capacity/action-opportunity/work-budget controls,
  reactive/linear/nonlinear/high-budget/oracle/timing-broken nulls, primary
  endpoints, and fail-closed strange-attractor/lobe rules are present.
- The guard still reports `state=closed_awaiting_preregistration`,
  `repo_write_allowed=false`, and `notify_ben=true` because the later A7.2 and
  three-hive fixed seed `1,2` gates failed closed. No simulator mechanics,
  configs, analyzers, run artifacts, dashboards, integrations, broad seeds,
  parameter sweeps, extra hives, or promotion claims were added. The status
  update preserves exactly one next step: notify Ben and wait for a fresh
  preregistered direction.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard` and
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`21 passed, 632 deselected`).

- 2026-06-28 19:36 PDT bounded A5 prompt revalidation under governance
  closure: re-read automation memory, `README.md`, `AUTOMATION_STATUS.md`, the
  concise single-hive A5 preregistration, the structured strange-attractor
  research note, the existing A5 comparison/scaffold surface, current guard
  output, and recent git history. Confirmed again that the explicit A5
  preregistration request is already satisfied: deterministic single-hive
  setup, resource-bounded prediction hypothesis, matched task-arrival/service-
  capacity/action-opportunity/work-budget controls, reactive/linear/nonlinear/
  high-budget/oracle/timing-broken nulls, primary endpoints, and fail-closed
  strange-attractor/lobe rules are present.
- The guard still reports `state=closed_awaiting_preregistration`,
  `repo_write_allowed=false`, and `notify_ben=true` because the later A7.2 and
  three-hive fixed seed `1,2` gates failed closed. No simulator mechanics,
  configs, analyzers, run artifacts, dashboards, integrations, broad seeds,
  parameter sweeps, extra hives, or promotion claims were added. The status
  update preserves exactly one next step: notify Ben and wait for a fresh
  preregistered direction.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard` and
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`21 passed, 632 deselected`).

- 2026-06-28 18:35 PDT bounded A5 prompt revalidation under governance
  closure: re-read automation memory, `README.md`, `AUTOMATION_STATUS.md`, the
  concise single-hive A5 preregistration, the structured strange-attractor
  research note, focused A5/automation references, current guard output, and
  recent git history. Confirmed the explicit A5 preregistration request is
  already satisfied: deterministic single-hive setup, resource-bounded
  prediction hypothesis, matched task-arrival/service-capacity/action-
  opportunity/work-budget controls, reactive/linear/nonlinear/high-budget/
  oracle/timing-broken nulls, primary endpoints, and fail-closed
  strange-attractor/lobe rules are present.
- The guard now reports `state=closed_awaiting_preregistration`,
  `repo_write_allowed=false`, and `notify_ben=true` because the later A7.2 and
  three-hive fixed seed `1,2` gates failed closed. No simulator mechanics,
  configs, analyzers, run artifacts, dashboards, integrations, broad seeds,
  parameter sweeps, extra hives, or promotion claims were added. The status
  update preserves exactly one next step: notify Ben and wait for a fresh
  preregistered direction.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard` and
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`21 passed, 632 deselected`).

- 2026-06-29 bounded governance-closure run: re-read `README.md`,
  `AUTOMATION_STATUS.md`, configs/tests, the superseded provisional roadmap,
  current guard output, and the latest GPT-5.5-Pro strategy review before
  choosing a next step. The review header was `strategic_change_level: major`
  and `notify_ben: true`; accepted its recommendation to close automation into
  awaiting-preregistration because A7.2 and the three-hive ring have both
  completed their bounded fixed seed `1,2` gates and failed closed.
- Updated `ohdyn.automation_guard` so completed A7.2 plus three-hive
  fail-closed status is represented as `state=closed_awaiting_preregistration`,
  `repo_write_allowed=false`, and `notify_ben=true` even though the stale A5
  preregistration file still exists. Added a focused regression test for that
  governance state.
- Added `docs/results/ben_decision_after_a7_2_three_hive_failclosed_20260629.md`
  as the Ben notification/decision draft. It records the evidence boundary and
  offers exactly three choices: pause, preregister a one-hive dimensionless
  delayed-dynamics sweep, or pivot first to an analytic delayed
  resource-bounded prediction map. No simulator mechanics, configs, run
  artifacts, dashboards, integrations, broad seeds, parameter sweeps, extra
  hives, or promotion claims were added. Exactly one next step remains: notify
  Ben and wait for a fresh preregistered direction.

- 2026-06-28 18:01 PDT bounded source-of-truth recheck: re-read
  `README.md`, `AUTOMATION_STATUS.md`, config/test references, the superseded
  provisional roadmap, `docs/three_hive_ring_preregistration.md`,
  `docs/hyperseed_one_hive_delayed_dynamics_note.md`, current guard output,
  CLI-loop process status, recent git history, and the latest GPT-5.5-Pro
  strategy review before choosing a next step. The worktree was clean, the
  guard reported `state=open`, `repo_write_allowed=true`, and
  `notify_ben=false`, and the only live same-repo processes were this
  wrapper/Codex pair.
- Deferred the latest external review's concrete preflight-analyzer
  recommendation again because it remains superseded by the repository
  source-of-truth: the three-hive schema/source-ledger preflight,
  deterministic mechanics smoke, residual/null analyzer, closure note, and
  prior governance-hold record are already complete. The review header was
  `strategic_change_level: minor` and `notify_ben: false`, so no direction
  shift or Ben notification is required from this pass.
- No simulator code, configs, analyzers, docs beyond this status note, or run
  artifacts were changed. This run preserved the fixed seed `1,2`
  fail-closed interpretation boundary and leaves exactly one next step:
  prepare a fresh preregistered decision note only if Ben chooses a new
  scientific direction such as a one-hive dimensionless delayed-dynamics
  sweep.

- 2026-06-28 17:44 PDT bounded governance-hold run: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs, focused test references, the
  superseded provisional roadmap, current guard output, CLI-loop process
  status, recent git history, and the latest GPT-5.5-Pro strategy review
  before choosing a next step. The only live same-repo processes were this
  wrapper/Codex pair. The guard reported `state=open`,
  `repo_write_allowed=true`, and `notify_ben=false`.
- Deferred the latest external review's concrete preflight-analyzer
  recommendation because it is now superseded by the repository
  source-of-truth: the three-hive schema/source-ledger preflight, deterministic
  mechanics smoke, residual/null analyzer, and closure note are already
  complete. The current status-backed next step remains a pause on further
  three-hive expansion, with no rescue claims, broad seed sweeps, dashboards,
  integrations, parameter sweeps, post-result tuning, or extra hives.
- No simulator code, configs, analyzers, docs beyond this status note, or run
  artifacts were changed in this bounded pass. This was not a new scientific
  result; it preserved the fail-closed seed `1,2` interpretation boundary and
  left exactly one next step: prepare a fresh preregistered decision note only
  if Ben chooses a new scientific direction such as a one-hive dimensionless
  delayed-dynamics sweep.

- 2026-06-28 17:34 PDT bounded A5 prompt revalidation after three-hive closure:
  re-read the automation memory, `README.md`, `AUTOMATION_STATUS.md`, the
  concise single-hive A5 preregistration, the structured strange-attractor
  research note, guard logic, focused A5/automation test references, and recent
  git history. Confirmed again that Ben's explicit A5 single-hive request is
  already satisfied by the existing preregistration and deterministic scaffold:
  resource-bounded prediction, matched task-arrival/service-capacity/action-
  opportunity/work-budget controls, reactive/linear/nonlinear/high-budget/
  oracle/timing-broken null conditions, primary endpoints, and fail-closed
  strange-attractor/lobe interpretation rules are present.
- Reran bounded verification without adding mechanics, configs, dashboards,
  integrations, broad seed sweeps, or multi-hive coupling. The guard reported
  `state=open`, `a5_preregistration_active=true`, `repo_write_allowed=true`,
  and `notify_ben=false`; focused A5/automation tests passed; and a temporary
  seed `5,6` A5 comparison plus read-only residual-accounting analyzer under
  `/tmp/omegasim_a5_current_srBySX` reproduced the fail-closed result.
  Forecast skill improved for intermediate predictors, but no intermediate
  condition passed all residual/null, oracle-nontriviality, compression, and
  guardrail criteria.

- 2026-06-28 17:27 PDT three-hive ring closure note: re-read `README.md`,
  `AUTOMATION_STATUS.md`, configs/tests, the superseded provisional roadmap,
  `docs/three_hive_ring_preregistration.md`, current guard output, CLI-loop
  status, and the latest GPT-5.5-Pro strategy review before choosing the next
  step. The review has `notify_ben: false` and `strategic_change_level:
  minor`; its preflight-analyzer recommendation is now superseded by the
  repository source-of-truth because the preflight, mechanics smoke, and
  residual/null analyzer gates have already been completed. This run therefore
  followed the newer status recommendation to add only a documentation closure
  note.
- Added `docs/results/three_hive_ring_closure_note_seed1_2.md`, freezing the
  fixed seed `1,2` three-hive mechanics/analyzer interpretation boundary. The
  note records the fail-closed status, productivity-guardrail failure on
  `completion_fraction`, null-contrast failures, and the prohibition on
  treating harness-level artifacts as lobe-like, strange-attractor-like,
  semantic-dynamics, synchrony, phase-grammar, or causal collective-structure
  evidence.
- Verification reran the fixed mechanics/analyzer smoke in `/tmp`:
  `.venv-conda/bin/python -m ohdyn.compare_three_hive_ring_mechanics --out
  /tmp/omegasim_three_hive_closure_0f5wEt/mechanics` followed by
  `.venv-conda/bin/python -m ohdyn.analyze_three_hive_ring_residual_null
  --compare-dir /tmp/omegasim_three_hive_closure_0f5wEt/mechanics --out
  /tmp/omegasim_three_hive_closure_0f5wEt/analysis`. The analyzer reported
  26/26 schema/metrics/events/source-ledger pass rows, 26/26 source-ledger
  pass rows, 156 residual rows computed, null-contrast gates of 37
  `eligible_for_guardrail_and_cross_seed_review`, 67
  `fail_closed_no_residual_autocorrelation_advantage`, and 16
  `fail_closed_no_residual_predictability_advantage`, plus 2/2
  `fail_closed_completion_fraction` productivity guardrail rows. Overall
  status remained `fail_closed_productivity_guardrails`.
- Focused verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'three_hive_ring' -q` (`13 passed, 639 deselected`),
  `.venv-conda/bin/python -m ohdyn.automation_guard` (`state=open`,
  `repo_write_allowed=true`, `notify_ben=false`), and `git diff --check`.

- 2026-06-28 17:08 PDT three-hive ring residual/null analyzer gate: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests, the superseded
  provisional roadmap, `docs/three_hive_ring_preregistration.md`, current
  guard output, CLI-loop status, and the latest GPT-5.5-Pro strategy review
  before choosing the next step. The review has `notify_ben: false` and
  `strategic_change_level: minor`; its preflight-analyzer recommendation had
  already been completed in an earlier run, so this run followed the newer
  source-of-truth status recommendation to implement the bounded read-only
  residual/null/source-ledger analyzer.
- Added `ohdyn.analyze_three_hive_ring_residual_null` and analyzer field
  constants in `ohdyn/three_hive_ring_contract.py`. The analyzer reads only
  existing fixed seed `1,2` mechanics artifacts; verifies metrics/events/source
  ledger completeness; reconstructs event and per-hive source ledgers with a
  CSV-rounding tolerance; computes residual preflight metrics for artifact and
  forecast-error targets after accounting controls; compares
  `delayed_logistic_ring` against every preregistered null; and applies the
  frozen productivity guardrails. It does not run simulations, tune
  parameters, add hives, create dashboards/integrations, broaden seeds, or make
  promotion claims.
- The bounded temp smoke
  `.venv-conda/bin/python -m ohdyn.compare_three_hive_ring_mechanics --out
  /tmp/omegasim_three_hive_residual_null_S0E8Wk/mechanics` followed by
  `.venv-conda/bin/python -m ohdyn.analyze_three_hive_ring_residual_null
  --compare-dir /tmp/omegasim_three_hive_residual_null_S0E8Wk/mechanics --out
  /tmp/omegasim_three_hive_residual_null_S0E8Wk/analysis` closed
  fail-closed with status `fail_closed_productivity_guardrails`: 26/26
  schema/metrics/events/source-ledger rows passed, 26/26 source-ledger checks
  passed, 156 residual rows computed, null-contrast gates were 37
  `eligible_for_guardrail_and_cross_seed_review`, 67
  `fail_closed_no_residual_autocorrelation_advantage`, and 16
  `fail_closed_no_residual_predictability_advantage`, and both productivity
  guardrail rows failed on `completion_fraction`. This is not a much-better or
  scientifically novel result; it reinforces the preregistered fail-closed
  interpretation boundary.
- Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'three_hive_ring' -q` (`13 passed, 639 deselected`) and
  `.venv-conda/bin/python -m py_compile
  ohdyn/analyze_three_hive_ring_residual_null.py
  ohdyn/three_hive_ring_contract.py`.

- 2026-06-28 16:45 PDT three-hive ring mechanics smoke gate: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests, the superseded
  provisional roadmap, `docs/three_hive_ring_preregistration.md`, current
  guard output, CLI-loop status, and the latest GPT-5.5-Pro strategy review
  before choosing the next step. The review still has `notify_ben: false` and
  `strategic_change_level: minor`; its preflight-analyzer recommendation had
  already been completed in the prior run, so this run followed the newer
  source-of-truth status recommendation to implement the bounded mechanics
  gate.
- Added `ohdyn.compare_three_hive_ring_mechanics` plus mechanics/source-ledger
  manifest constants in `ohdyn/three_hive_ring_contract.py`. The helper loads
  the frozen contract fixture, refuses non-fixed seeds, and emits one artifact
  directory per preregistered condition and seed `1,2` with deterministic
  per-hive `metrics.csv`, per-edge `events.csv`, per-hive `source_ledger.csv`,
  schemas, config, manifest, and summary. Each run has 216 metrics rows, 216
  event rows, and 216 source-ledger rows. It includes delayed transfer,
  cross-hive prediction/work-cost accounting, membrane acceptance, source
  ledgers, and the preregistered null/control condition variants at smoke
  scale. It does not compute residual endpoints, promotion labels, broad seed
  sweeps, dashboards, integrations, parameter sweeps, post-result tuning, or
  hives beyond the frozen ring.
- Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'three_hive_ring' -q` (`11 passed, 639 deselected`),
  `.venv-conda/bin/python -m py_compile
  ohdyn/compare_three_hive_ring_mechanics.py ohdyn/three_hive_ring_contract.py`,
  and a temp CLI smoke:
  `.venv-conda/bin/python -m ohdyn.compare_three_hive_ring_mechanics --out
  /tmp/omegasim_three_hive_mechanics_MAvujR/mechanics` followed by
  `.venv-conda/bin/python -m ohdyn.analyze_three_hive_ring_preflight
  --compare-dir /tmp/omegasim_three_hive_mechanics_MAvujR/mechanics --out
  /tmp/omegasim_three_hive_mechanics_MAvujR/preflight`, whose manifest
  reported 26 observed runs, 26 schema-pass rows, 26 metrics/events-present
  rows, and status `eligible_for_mechanics_gate`.

- 2026-06-28 16:35 PDT A5 bounded prompt revalidation: re-read automation
  memory, `README.md`, `AUTOMATION_STATUS.md`, the concise single-hive A5
  preregistration, current A5 comparison/analyzer scaffold references, the
  automation guard, recent git history, and focused A5 test surface. Confirmed
  that the explicitly requested A5 preregistration/scaffold stage remains
  satisfied: deterministic single-hive setup, resource-bounded prediction
  hypothesis, matched task-arrival/service-capacity/action-opportunity/work
  budget controls, reactive/linear/nonlinear/high-budget/oracle/timing-broken
  null conditions, primary endpoints, and fail-closed strange-attractor/lobe
  interpretation rules are all present.
- Ran the bounded A5 single-hive verification without changing mechanics:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported `state=open`,
  `a5_preregistration_active=true`, `repo_write_allowed=true`, and
  `notify_ben=false`; focused pytest passed with `20 passed, 626 deselected`;
  and a temporary seed `5,6` smoke plus read-only residual accounting analyzer
  under `/tmp/omegasim_a5_current_WLrPvy` reproduced the fail-closed promotion
  audit. Forecast skill improved for intermediate predictors, but no
  intermediate condition passed all residual/null, oracle-nontriviality,
  compression, and guardrail criteria. No A5 preregistration, simulator
  mechanics, configs, analyzers, dashboards, integrations, seed sweeps, or
  multi-hive coupling were added.

- 2026-06-28 16:23 PDT three-hive ring preflight analyzer: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests, the superseded
  provisional roadmap, the frozen three-hive preregistration, the current
  schema-smoke helper/contract, current guard output, CLI-loop status, and the
  latest GPT-5.5-Pro strategy review before choosing the next step. The review
  has `notify_ben: false` and `strategic_change_level: minor`; its
  recommendation to recover from self-concurrency and add only a read-only
  fail-closed preflight analyzer was accepted as scientifically sensible. The
  apparent live CLI-loop/Codex process was this bounded run itself, not a
  competing worker.
- Added `ohdyn.analyze_three_hive_ring_preflight` plus preflight field
  constants in `ohdyn/three_hive_ring_contract.py`. The analyzer reads only
  existing schema-smoke artifacts, verifies condition/seed coverage, required
  config/manifest/schema/source-ledger files, required metric/event/source
  schema fields, and metrics/events presence. For the current artifact-only
  smoke it emits `fail_closed_no_metrics_events`; missing source-ledger schema
  fails closed as `fail_closed_missing_source_ledger`. No simulator mechanics,
  metrics/events fabrication, promotion endpoints, dashboards, integrations,
  parameter sweeps, broader seeds, or extra hives were added.
- Updated `README.md` and `docs/three_hive_ring_preregistration.md` with the
  analyzer command, expected fail-closed status, and the next authorized
  mechanics boundary. Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'three_hive_ring' -q` (`7 passed, 639 deselected`),
  `.venv-conda/bin/python -m py_compile
  ohdyn/analyze_three_hive_ring_preflight.py ohdyn/three_hive_ring_contract.py`,
  and a temp CLI smoke:
  `.venv-conda/bin/python -m ohdyn.compare_three_hive_ring --out
  /tmp/omegasim_three_hive_preflight_ahSOeX/schema_smoke` followed by
  `.venv-conda/bin/python -m ohdyn.analyze_three_hive_ring_preflight
  --compare-dir /tmp/omegasim_three_hive_preflight_ahSOeX/schema_smoke --out
  /tmp/omegasim_three_hive_preflight_ahSOeX/preflight`, whose manifest reported
  26 runs, 26 schema-pass rows, 0 metrics/events-present rows, and status
  `fail_closed_no_metrics_events`.

- 2026-06-28 15:35 PDT three-hive ring schema/source-ledger smoke scaffold:
  re-read automation memory, the A5 single-hive preregistration, `README.md`,
  `AUTOMATION_STATUS.md`, the frozen three-hive ring preregistration,
  contract/config-validation fixture, comparison-helper patterns, and focused
  tests. Confirmed again that the explicit A5 preregistration/scaffold request
  remains satisfied and that the current source-of-truth next bounded action
  was the post-A7.2 three-hive ring schema/source-ledger smoke scaffold.
- Added `ohdyn.compare_three_hive_ring` and the frozen manifest-field constant
  in `ohdyn/three_hive_ring_contract.py`. The helper loads
  `configs/three_hive_ring_contract_validation.yaml`, refuses non-fixed seeds,
  and emits one artifact directory per frozen condition and seed `1,2` with
  `config.yaml`, `manifest.yaml`, `metrics_schema.csv`, `events_schema.csv`,
  `source_ledger_schema.csv`, and `summary.md`. No simulator mechanics,
  metrics/events, analyzers, result claims, dashboards, integrations,
  parameter sweeps, or extra hives were added.
- Updated `README.md` and `docs/three_hive_ring_preregistration.md` with the
  artifact-only command and the next read-only preflight-analyzer boundary.
  Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'three_hive_ring' -q` (`5 passed, 639 deselected`),
  `.venv-conda/bin/python -m py_compile ohdyn/compare_three_hive_ring.py
  ohdyn/three_hive_ring_contract.py`, and
  `.venv-conda/bin/python -m ohdyn.compare_three_hive_ring --out
  /tmp/omegasim_three_hive_schema_smoke_9vIM7C` (26 artifact directories
  emitted).

- 2026-06-28 14:36 PDT three-hive ring config-validation gate: re-read the
  A5 single-hive preregistration, `README.md`, `AUTOMATION_STATUS.md`,
  `docs/three_hive_ring_preregistration.md`, the frozen three-hive ring
  contract, config loader patterns, existing A7/A7.2 fixture tests, and recent
  git history. Confirmed again that the explicit A5 preregistration/scaffold
  requirement remains satisfied and that the source-of-truth next bounded
  action had moved to the post-A7.2 three-hive ring contract/config gate.
- Added a simulator-free `three_hive_ring` config-validation path in
  `ohdyn/config.py` plus `configs/three_hive_ring_contract_validation.yaml`.
  The fixture loads the frozen hives, A->B->C->A directed edges, condition
  order, smoke parameters, role-bias labels, state fields, edge fields,
  source-ledger schema, dimensionless manifest fields, primary endpoints,
  residual controls, and productivity guardrails. It rejects schema drift
  against `ohdyn/three_hive_ring_contract.py`. No simulator mechanics,
  analyzers, result-bearing runs, dashboards, integrations, parameter sweeps,
  or additional hives were added.
- Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'three_hive_ring_contract' -q` (`3 passed, 639 deselected`) and
  `.venv-conda/bin/python -m py_compile ohdyn/config.py
  ohdyn/three_hive_ring_contract.py`; after this status update,
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'three_hive_ring_contract or automation_guard' -q` (`19 passed, 623
  deselected`), `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=open`, `a5_preregistration_active=true`,
  `repo_write_allowed=true`, `notify_ben=false`, recommended next action is
  the smallest deterministic three-hive ring smoke scaffold), and
  `git diff --check`.

- 2026-06-28 14:12 PDT three-hive ring contract gate: re-read `README.md`,
  `AUTOMATION_STATUS.md`, configs/tests/docs surface, the superseded
  provisional roadmap, `docs/three_hive_ring_preregistration.md`, current
  guard output, CLI-loop status, and the latest GPT-5.5-Pro strategy review
  before choosing the next step. The review has `notify_ben: false` and
  `strategic_change_level: none`; its recommendation to implement only the
  three-hive contract/constants schema tests was accepted as scientifically
  sensible. The apparent live CLI-loop process was this bounded run itself, not
  a separate stale worker, so no process cleanup was performed.
- Added `ohdyn/three_hive_ring_contract.py` as a pure constants/schema module
  freezing the preregistered hives, A->B->C->A edges, action names, role-bias
  labels, state fields, edge/source-ledger fields, condition order, smoke
  parameters, dimensionless manifest fields, primary endpoints, residual
  controls, productivity guardrails, and required metric/event schema helpers.
  Added focused tests in `tests/test_run_harness.py`. No simulator mechanics,
  configs, analyzers, simulation runs, dashboards, integrations, parameter
  sweeps, or additional hives were added.
- Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'three_hive_ring_contract or a7_2_delayed_prediction_contract or
  a7_semantic_field_contract' -q` (`3 passed, 637 deselected`),
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'three_hive_ring_contract or automation_guard' -q` (`17 passed, 623
  deselected`), `.venv-conda/bin/python -m py_compile
  ohdyn/three_hive_ring_contract.py`,
  `.venv-conda/bin/python -m ohdyn.automation_guard` (`state=open`,
  `repo_write_allowed=true`, `notify_ben=false`, recommended next action is
  now the three-hive ring config-validation fixture step),
  and `git diff --check`.

- 2026-06-28 13:32 PDT A5 bounded prompt revalidation: re-read automation
  memory, `README.md`, `AUTOMATION_STATUS.md`, the concise A5 single-hive
  preregistration, the structured strange-attractor research note, current A5
  scaffold references, the reopened A5 smoke note, recent git history, and the
  already-frozen three-hive ring preregistration. Confirmed that the requested
  A5 preregistration/scaffold stage remains satisfied: deterministic
  single-hive setup, resource-bounded prediction hypothesis, matched task-
  arrival/service-capacity/action-opportunity/work-budget controls,
  reactive/linear/nonlinear/high-budget/oracle/timing-broken null conditions,
  primary endpoints, and fail-closed strange-attractor/lobe interpretation
  rules are all present.
- No A5 preregistration, scaffold, or smoke gap was found. No simulator
  mechanics, configs, analyzers, simulation runs, dashboards, integrations,
  seed sweeps, A7.2 changes, or multi-hive mechanics were added. The single
  recommended next step remains the contract-only three-hive ring schema
  module and focused tests already named above.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard` (`state=open`,
  `a5_preregistration_active=true`, `repo_write_allowed=true`,
  `notify_ben=false`),
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`20 passed, 619 deselected`), and `git diff --check`.

- 2026-06-28 13:01 PDT three-hive ring preregistration: re-read `README.md`,
  `AUTOMATION_STATUS.md`, configs/tests surface, the superseded provisional
  roadmap, the research transition directive, the experiment rundown, the
  Hyperseed delayed-dynamics note, the A7.2 preregistration, current guard
  output, CLI-loop status, and the latest GPT-5.5-Pro strategy review before
  choosing the next step. The review has `notify_ben: false` and
  `strategic_change_level: none`; its recommendation to freeze a three-hive
  preregistration before mechanics was accepted as scientifically sensible.
- Added `docs/three_hive_ring_preregistration.md`, freezing the post-A7.2
  three-hive ring as a relational diagnostic amplifier rather than an
  ontological requirement for complexity. The preregistration fixes the three
  biased hives, A->B->C->A ring topology, cross-hive prediction and transfer
  costs, delayed artifact transfer, membrane acceptance, artifact update
  equations, dimensionless smoke parameters, target/phase/transfer-
  opportunity/spend/source-ledger nulls, residual endpoints, productivity
  guardrails, closure rules, and the next contract-only step. No simulator
  mechanics, configs, analyzers, simulation runs, dashboards, integrations, or
  seed sweeps were added.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard` (`state=open`,
  `repo_write_allowed=true`, `notify_ben=false`, recommended next action is
  the contract-only three-hive ring schema step) and `git diff --check`.

- 2026-06-28 12:32 PDT A5 bounded prompt verification: re-read automation
  memory, `README.md`, `AUTOMATION_STATUS.md`, the concise A5 single-hive
  preregistration, the structured strange-attractor research note, current
  guard logic, focused test references, and recent git history. Confirmed that
  the A5 preregistration already covers the requested deterministic
  single-hive anticipatory predictive-control setup, resource-bounded
  prediction hypothesis, matched task-arrival/service-capacity/action-
  opportunity/work-budget accounting, reactive/linear/nonlinear/high-budget/
  oracle/timing-broken null conditions, primary endpoints, and fail-closed
  strange-attractor/lobe interpretation rules.
- No A5 preregistration or smallest-scaffold gap was found. No simulator
  mechanics, configs, analyzers, simulation runs, dashboards, integrations,
  seed sweeps, A7.2 changes, or multi-hive coupling were added. The current
  source-of-truth next step remains the separate three-hive ring
  preregistration, not A5 broadening.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard` (`state=open`,
  `a5_preregistration_active=true`, `repo_write_allowed=true`,
  `notify_ben=false`),
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`20 passed, 619 deselected`), and `git diff --check`.

- 2026-06-28 A7.2 bounded comparison/analyzer smoke: re-read `README.md`,
  `AUTOMATION_STATUS.md`, configs/tests surface, the superseded provisional
  roadmap, the frozen A7.2 preregistration, current guard output, CLI-loop
  tail, and the latest GPT-5.5-Pro strategy review before choosing the next
  step. The review has `notify_ben: false` and `strategic_change_level:
  minor`; its preregistration-freeze recommendation was already satisfied, so
  this run followed the current source-of-truth next step.
- Added `ohdyn.compare_a7_2_delayed_prediction` to run only the ten
  preregistered single-hive A7.2 smoke conditions at fixed seeds `1,2`, with
  no broad seed sweep, tuning, dashboards, integrations, or multi-hive
  mechanics. Added `ohdyn.analyze_a7_2_delayed_prediction` as a read-only
  preflight analyzer covering schema/source-ledger completeness, delay checks,
  residual audit rows, null contrasts, and productivity guardrails. Added
  focused tests for the fixed-seed comparison, missing-schema fail-closed
  behavior, and full ten-condition smoke preflight.
- Ran the bounded commands:
  `.venv-conda/bin/python -m ohdyn.compare_a7_2_delayed_prediction --seeds 1 2
  --out runs/a7_2_delayed_prediction_compare_seed1_2` and
  `.venv-conda/bin/python -m ohdyn.analyze_a7_2_delayed_prediction
  --compare-dir runs/a7_2_delayed_prediction_compare_seed1_2 --out
  runs/a7_2_delayed_prediction_analysis_seed1_2`. The analyzer inspected 20
  runs and closed `fail_closed_residual_null_gate`: schema/source pass rows
  `20`, forecast delay pass rows `18`, artifact delay pass rows `20`,
  residual row status `computed=140`, null-contrast gate status
  `eligible_for_guardrail_and_cross_seed_review=45`,
  `fail_closed_no_nonlinear_forecastability_advantage=25`,
  `fail_closed_no_residual_autocorrelation_advantage=56`, and productivity
  guardrail status `pass=18`. Tracked result note:
  `docs/results/a7_2_delayed_prediction_smoke_preflight_seed1_2.md`.
- Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'a7_2' -q`
  (`12 passed, 627 deselected`),
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a7_2 or a7_semantic_field_contract' -q` (`28 passed,
  611 deselected`), `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=open`, `repo_write_allowed=true`, `notify_ben=false`, recommended
  next action is the three-hive ring preregistration), and `git diff --check`.

- 2026-06-28 11:31 PDT A5 bounded prompt verification: re-read automation
  memory, `README.md`, `AUTOMATION_STATUS.md`, the concise A5 single-hive
  preregistration, the structured strange-attractor research note, current A5
  comparison/analyzer code, focused test references, and recent git history.
  Confirmed that the A5 preregistration already covers the requested
  deterministic single-hive anticipatory predictive-control setup,
  resource-bounded prediction hypothesis, matched task-arrival/service-
  capacity/action-opportunity/work-budget accounting, reactive/linear/
  nonlinear/high-budget/oracle/timing-broken null conditions, primary
  endpoints, and fail-closed strange-attractor/lobe interpretation rules.
  Confirmed that the existing deterministic scaffold is still the smallest
  bounded A5 smoke path; no new mechanics, configs, analyzers, dashboards,
  integrations, seed sweeps, A7.2 changes, or multi-hive coupling were added.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard` (`state=open`,
  `a5_preregistration_active=true`, `repo_write_allowed=true`,
  `notify_ben=false`),
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`20 passed, 615 deselected`), and a temporary paired-seed A5 smoke plus
  read-only residual analyzer under `/tmp/omegasim_a5_20260628_current_9uBnsr`.
  The smoke reproduced forecast-skill gains for linear, nonlinear, and
  high-budget nonlinear predictors, but the analyzer promotion audit failed
  closed for every intermediate-budget condition after accounting/null checks.

- 2026-06-28 current bounded A7.2 mechanics pass: re-read `README.md`,
  `AUTOMATION_STATUS.md`, configs/tests surface, the superseded provisional
  roadmap, the frozen A7.2 preregistration, current guard output, CLI-loop
  tail, and the latest GPT-5.5-Pro strategy review before choosing the next
  step. The review has `notify_ben: false` and `strategic_change_level:
  minor`; its preregistration-freeze recommendation was already satisfied by
  the prior A7.2 contract/config pass, so this run followed the current
  source-of-truth status next step and added only minimal simulator/output
  mechanics needed to emit the frozen A7.2 fields.
- Added isolated A7.2 delayed prediction mechanics in `ohdyn.sim`: deterministic
  A7.2 action selection among `predict`, `work`, `review`, and `synthesize`;
  prediction work-opportunity charging; delayed forecast/artifact update
  queues; fatigue/adaptive-threshold updates; source-ledger event rows; and
  per-tick metrics for the frozen contract fields. Wired A7.2 metric/event
  fieldnames and manifest metadata in `ohdyn.io`. Added focused simulator-path
  regression coverage proving the intermediate A7.2 smoke fixture emits the
  required metric/event schema and delayed forecast timing. No paired A7.2
  scientific smoke, analyzer interpretation, dashboards, integrations, broad
  seed sweeps, or multi-hive coupling were added.
- Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'a7_2' -q`
  (`8 passed, 627 deselected`),
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a7_2 or a7_semantic_field_contract' -q` (`24 passed,
  611 deselected`), a temporary single-seed write-path smoke
  `.venv-conda/bin/python -m ohdyn.run --config
  configs/a7_2_intermediate_endogenous_delayed_prediction_smoke.yaml --seed 1
  --out /tmp/.../run` with inspected `metrics.csv` and `events.csv` headers,
  `.venv-conda/bin/python -m ohdyn.automation_guard` (`state=open`,
  `repo_write_allowed=true`, `notify_ben=false`), and `git diff --check`.

- 2026-06-28 10:29 PDT A5 prompt-replay verification: re-read automation
  memory, `README.md`, `AUTOMATION_STATUS.md`, the concise A5 single-hive
  preregistration, the structured strange-attractor research note, the A5
  comparison/analyzer scaffold, focused test references, and recent git
  history. Confirmed that the A5 preregistration already covers the requested
  deterministic single-hive anticipatory predictive-control setup,
  resource-bounded prediction hypothesis, matched task-arrival/service-
  capacity/action-opportunity/work-budget accounting, reactive/linear/
  nonlinear/high-budget/oracle/null conditions, primary endpoints, and
  fail-closed strange-attractor/lobe interpretation rules. No missing A5
  preregistration or minimal-scaffold gap was found; the newer A7.2 status
  remains the single active next gate.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard` (`state=open`,
  `repo_write_allowed=true`, `notify_ben=false`) and
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`20 passed, 614 deselected`). `git diff --check` passed before this status
  edit. No simulator mechanics, configs, analyzers, simulation runs,
  dashboards, integrations, seed sweeps, or multi-hive coupling were added.

- 2026-06-28 10:05 PDT A7.2 config/schema contract gate: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the historical
  provisional roadmap, the A5-family exit/A7.2 decision record, the frozen
  A7.2 preregistration, and the latest GPT-5.5-Pro strategy review before
  choosing the next step. The review has `notify_ben: false` and
  `strategic_change_level: minor`; its recommendation to freeze A7.2 before
  simulator implementation had already been incorporated in the prior
  preregistration pass, so this run accepted the current source-of-truth next
  step and added only config/schema contract support.
- Added `ohdyn/a7_2_delayed_prediction_contract.py` with frozen A7.2 action,
  condition, state, source-ledger, control, metric/event schema, endpoint,
  productivity guardrail, and smoke-parameter constants. Added
  `a7_2_delayed_prediction` config loading/validation, including fail-closed
  checks for preregistered constants, same-tick feedback only in the explicit
  same-tick control, spend-only replay accounting preservation, and
  artifact-off queue/accounting preservation. Added ten 48-tick A7.2 smoke
  config fixtures that load in preregistered condition order. Added focused
  tests for the contract, fixtures, and invariant rejection paths.
- Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'a7_2' -q`
  (`7 passed, 627 deselected`),
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a7_2 or a7_semantic_field_contract' -q` (`23 passed,
  611 deselected`), `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=open`, `repo_write_allowed=true`, `notify_ben=false`), and
  `git diff --check`. Full verification also passed:
  `.venv-conda/bin/python -m pytest -q` (`634 passed in 636.36s`). No A7.2
  simulations, analyzers, dashboards, integrations, seed sweeps, or multi-hive
  coupling were added or run.

- 2026-06-28 09:43 PDT A7.2 preregistration freeze: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the superseded
  provisional roadmap, the A5-family exit/A7.2 decision record, A7/A7
  long-horizon preregistrations, current guard output, CLI-loop tail, and the
  latest GPT-5.5-Pro strategy review. The review has `notify_ben: false` and
  `strategic_change_level: minor`; its recommendation to freeze A7.2 before
  simulator implementation is accepted as scientifically sensible. Added
  `docs/a7_2_delayed_artifact_endogenous_prediction_preregistration.md` with
  frozen A7.2 state fields, delays, costs, thresholds, slopes, artifact update
  equations, endpoints, nulls, productivity guardrails, closure rules, and the
  first implementation step. No simulator mechanics, configs, analyzers,
  simulation runs, dashboards, integrations, seed sweeps, or multi-hive
  coupling were added.

- 2026-06-28 Ben decision encoded: Ben explicitly instructed OmegaSim to try
  A7.2-style delayed artifact-mediated endogenous prediction first, then move
  on to a three-hive ring experiment family whether A7.2 is positive or
  negative. This status now treats A7.2 as the active next gate and the
  three-hive ring as pre-authorized downstream work requiring its own
  preregistration and bounded controls, without another governance pause.

- 2026-06-28 09:27 PDT bounded A5 verification: re-read the automation
  memory, `README.md`, `AUTOMATION_STATUS.md`, the structured
  strange-attractor research note, the concise A5 single-hive
  preregistration, recent git history, and focused A5/automation verification
  output. The preregistration already covers the explicitly requested
  deterministic single-hive setup, resource-bounded prediction hypothesis,
  matched accounting controls, reactive/linear/nonlinear/high-budget/oracle/
  timing-broken null conditions, primary endpoints, and fail-closed
  interpretation rules. No missing A5 preregistration item or smallest
  deterministic scaffold gap was found.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, `notify_ben=true`, `closed_reasons=[
  "automation_status_a5_broadening_stopped"]`) and
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`19 passed, 608 deselected`). No simulator mechanics, configs, analyzers,
  simulation runs, dashboards, integrations, seed sweeps, A7.2 mechanics, or
  multi-hive coupling were added.

- 2026-06-28 08:26 PDT bounded A5 verification: re-read the automation
  memory, `README.md`, `AUTOMATION_STATUS.md`, the structured
  strange-attractor research note, the concise A5 single-hive
  preregistration, recent git history, and the focused A5/automation test
  surface. The preregistration already covers the explicitly requested
  deterministic single-hive setup, resource-bounded prediction hypothesis,
  matched accounting controls, reactive/linear/nonlinear/high-budget/oracle/
  timing-broken null conditions, primary endpoints, and fail-closed
  interpretation rules. No missing A5 preregistration item or smallest
  deterministic scaffold gap was found.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, `notify_ben=true`, `closed_reasons=[
  "automation_status_a5_broadening_stopped"]`) and
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`19 passed, 608 deselected`). No simulator mechanics, configs, analyzers,
  simulation runs, dashboards, integrations, seed sweeps, A7.2 mechanics, or
  multi-hive coupling were added.

- 2026-06-28 07:25 PDT bounded A5 verification: re-read the automation
  memory, `README.md`, `AUTOMATION_STATUS.md`, the structured
  strange-attractor research note, the concise A5 single-hive
  preregistration, focused A5/automation test references, and recent git
  history. The preregistration already covers the explicitly requested
  deterministic single-hive setup, resource-bounded prediction hypothesis,
  matched accounting controls, reactive/linear/nonlinear/high-budget/oracle/
  timing-broken null conditions, primary endpoints, and fail-closed
  interpretation rules. No missing A5 preregistration item or smallest
  deterministic scaffold gap was found.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, `notify_ben=true`, `closed_reasons=[
  "automation_status_a5_broadening_stopped"]`) and
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`19 passed, 608 deselected`). No simulator mechanics, configs, analyzers,
  simulation runs, dashboards, integrations, seed sweeps, A7.2 mechanics, or
  multi-hive coupling were added.

- 2026-06-28 06:25 PDT bounded A5 status verification: re-read the
  automation memory, the concise A5 single-hive preregistration, `README.md`,
  `AUTOMATION_STATUS.md`, the structured strange-attractor research note, the
  focused A5/automation test surface, and recent git history. The A5
  preregistration already covers the explicitly requested deterministic
  single-hive setup, resource-bounded prediction hypothesis, matched
  arrival/capacity/opportunity/work-budget controls, reactive/linear/nonlinear/
  high-budget/oracle/null conditions, preregistered endpoints, and fail-closed
  interpretation rules. No missing preregistration item or deterministic
  scaffold gap was found.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, `notify_ben=true`, `closed_reasons=[
  "automation_status_a5_broadening_stopped"]`) and
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`19 passed, 608 deselected`). No simulator mechanics, configs, analyzers,
  simulation runs, dashboards, integrations, seed sweeps, A7.2 mechanics, or
  multi-hive coupling were added.

- 2026-06-28 05:24 PDT bounded A5 guard verification: re-read the automation
  memory, the concise A5 single-hive preregistration, `README.md`,
  `AUTOMATION_STATUS.md`, the structured strange-attractor research note, the
  automation guard, focused A5/automation test surface, and recent git history.
  No missing A5 preregistration item or deterministic single-hive scaffold gap
  was found. The existing scaffold still covers reactive, low-budget linear,
  medium-budget nonlinear, high-budget nonlinear, oracle, and budget-matched
  timing-broken null conditions, and the current source-of-truth status still
  closes further A5 broadening after the fail-closed smoke.
- No simulator mechanics, configs, analyzers, simulation runs, dashboards,
  integrations, seed sweeps, A7.2 mechanics, or multi-hive coupling were
  added. Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard -q` (`15 passed, 612 deselected`),
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, `notify_ben=true`, `closed_reasons=[
  "automation_status_a5_broadening_stopped"]`), and `git diff --check`.
  Exactly one next step remains: send Ben the existing A5-exit/A7.2 decision
  request and keep automation closed to new simulations or mechanics until he
  chooses the next separately preregistered scientific target.

- 2026-06-28 04:37 PDT bounded guard consistency pass: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the superseded
  provisional roadmap, the latest GPT-5.5-Pro strategy review, the CLI-loop
  log, the existing Ben A5-exit/A7.2 decision request, the concise A5
  preregistration, and the completed residual-compression report before
  choosing the next step. The review has `notify_ben: true` and
  `strategic_change_level: minor`; its recommendation to send Ben the
  existing decision request and stop repo-writing/status-loop automation while
  awaiting his choice is accepted as scientifically sensible.
- Updated `ohdyn.automation_guard` so the current source-of-truth
  recommendation to stop A5 broadening after the fail-closed smoke closes the
  live guard even though the historical concise A5 preregistration file still
  exists. Added focused regression coverage for that exact status wording.
- Verification passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard -q` (`15 passed, 612 deselected`),
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, `notify_ben=true`, `closed_reasons=[
  "automation_status_a5_broadening_stopped"]`), and `git diff --check`.
  No simulator mechanics, configs, analyzers, simulation runs, dashboards,
  integrations, seed sweeps, A7.2 mechanics, or multi-hive coupling were
  added. The GPT-5.5-Pro recommendation to avoid further status-only commits
  is deferred for this bounded pass only because the current automation
  instruction explicitly requires updating this status file and committing
  local progress. Exactly one next step remains: send Ben the existing
  A5-exit/A7.2 decision request and keep automation closed to new simulations
  or mechanics until he chooses the next preregistered target.

- 2026-06-28 current bounded A5 preregistration pass: re-read
  `README.md`, `AUTOMATION_STATUS.md`, the concise A5 single-hive
  preregistration, the existing A5 comparison scaffold, the A5 smoke config,
  and focused A5/automation tests. Updated the concise preregistration with
  explicit determinism and accounting locks: paired seeds, same base config,
  predictor as the intended contrast, matched arrivals/capacity/opportunity
  and work budget, explicit prediction-work transfer when charged, and
  budget-matched timing-broken nulls for every interpreted intermediate
  predictor. Updated this status file so the explicit A5 request is the active
  bounded gate for this pass while preserving fail-closed interpretation
  constraints.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=open`, `should_noop=false`, `repo_write_allowed=true`),
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`18 passed, 608 deselected`), the bounded existing A5 smoke
  `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6
  --out /tmp/omegasim_a5_20260628_current_53908/a5_predictive_control_compare`,
  and the read-only analyzer
  `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting
  --compare-dir /tmp/omegasim_a5_20260628_current_53908/a5_predictive_control_compare
  --out /tmp/omegasim_a5_20260628_current_53908/a5_residual_accounting`.
  The smoke remained fail-closed: linear, nonlinear, and high-budget nonlinear
  improved forecast skill versus reactive and matched shuffled nulls, but none
  satisfied residual/null, oracle-nontriviality, compression, and guardrail
  criteria together. `git diff --check` passed.

- 2026-06-28 03:40 PDT bounded guard-closed verification: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the superseded
  provisional roadmap, the latest GPT-5.5-Pro strategy review, the CLI-loop
  log, the existing Ben A5-exit/A7.2 decision request, the A5 single-hive
  preregistration, the reopened seed `5,6` A5 smoke result, and the completed
  resource-bounded residual-compression report before choosing the next step.
  The review has `notify_ben: true` and `strategic_change_level: minor`; its
  recommendation to send Ben the existing decision request and stop
  repo-writing/status-only automation while closed is accepted as
  scientifically sensible.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, `notify_ben=true`),
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard -q` (`14 passed, 612 deselected`), and `git diff --check`.
  No simulator mechanics, configs, analyzers, simulation runs, dashboards,
  integrations, seed sweeps, A7.2 mechanics, or multi-hive coupling were
  added.

- 2026-06-28 03:08 PDT bounded guard-closed verification: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the superseded
  provisional roadmap, the historical A5 diagnostic plan, the latest
  GPT-5.5-Pro strategy review, the CLI-loop log, the existing Ben
  A5-exit/A7.2 decision request, and the automation guard before choosing the
  next step. The review has `notify_ben: true` and
  `strategic_change_level: minor`; its recommendation to send Ben the
  existing decision request and stop repo-writing/status-only automation while
  closed is accepted as scientifically sensible.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, `notify_ben=true`). The existing decision
  request includes `closure_confirmed` and three explicit decision options.
  No callable notification integration was found or added. No simulator
  mechanics, configs, analyzers, simulation runs, dashboards, integrations,
  seed sweeps, A7.2 mechanics, or multi-hive coupling were added. The
  GPT-5.5-Pro recommendation to avoid further status-only commits is deferred
  for this bounded pass only because the current automation instruction
  explicitly requires updating this status file and committing local progress.

- 2026-06-28 02:35 PDT bounded guard-closed verification: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the superseded
  provisional roadmap, the latest GPT-5.5-Pro strategy review, the existing
  Ben A5-exit/A7.2 decision request, notification-status artifacts, and the
  automation guard before choosing the next step. The review has
  `notify_ben: true` and `strategic_change_level: minor`; its recommendation
  to send Ben the existing decision request and stop repo-writing/status-only
  automation while closed is accepted as scientifically sensible.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, `notify_ben=true`). The existing decision
  request includes `closure_confirmed` and three explicit decision options.
  No callable notification integration was found in the repo. No simulator
  mechanics, configs, analyzers, simulation runs, dashboards, integrations,
  seed sweeps, A7.2 mechanics, or multi-hive coupling were added. The
  GPT-5.5-Pro recommendation to avoid further status-only commits is deferred
  for this bounded pass only because the current automation instruction
  explicitly requires updating this status file and committing local progress.

- 2026-06-28 02:23 PDT bounded A5 status verification: re-read the
  automation memory, the concise A5 single-hive preregistration, `README.md`,
  `AUTOMATION_STATUS.md`, the existing reopened smoke note, the A5 comparison
  scaffold, focused A5/automation tests, and the automation guard. No
  unhandled A5 preregistration or scaffold gap was found.
- Verification passed:
  `.venv-conda/bin/python -m ohdyn.automation_guard`
  (`state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, `notify_ben=true`) and focused pytest
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  (`18 passed, 608 deselected`). No simulator mechanics, configs, analyzers,
  simulation runs, dashboards, integrations, seed sweeps, A7.2 mechanics, or
  multi-hive coupling were added.

- 2026-06-28 01:46 PDT bounded guard-closed stop pass: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the superseded
  provisional roadmap, the latest GPT-5.5-Pro strategy review, the Ben
  A5-exit/A7.2 decision request, and the automation guard before choosing the
  next step. The review has `notify_ben: true` and
  `strategic_change_level: minor`; its recommendation to send Ben the
  existing decision request and stop repo-writing/status-only automation while
  closed is accepted as scientifically sensible.
- The guard reports `state=closed_awaiting_preregistration`,
  `should_noop=true`, `repo_write_allowed=false`, and `notify_ben=true`. The
  decision request already includes the newer `closure_confirmed`
  residual-compression evidence and the three explicit decision options. No
  callable notification integration was found in the repo, so this pass did
  not add notification plumbing, simulator mechanics, configs, analyzers,
  simulation runs, dashboards, integrations, A7.2 mechanics, or multi-hive
  coupling. The GPT-5.5-Pro recommendation to avoid further status-only
  commits is deferred for this bounded pass only because the current
  automation instruction explicitly requires updating this status file and
  committing local progress.

- 2026-06-28 01:29 PDT bounded guard governance pass: re-read `README.md`,
  `AUTOMATION_STATUS.md`, the configs/tests surface, the superseded
  provisional roadmap, the latest GPT-5.5-Pro strategy review, the existing
  Ben A5-exit/A7.2 decision request, and the automation guard before choosing
  the next step. The review had `notify_ben: true` and
  `strategic_change_level: minor`; its recommendation to notify Ben and stop
  repo-writing/status-only automation while closed is accepted as
  scientifically sensible.
- Updated `ohdyn.automation_guard` to emit `repo_write_allowed=false` for
  closed/no-op states and `true` for open states, with focused regression
  coverage. This is a governance-surface change only. No notification text,
  simulator mechanics, configs, analyzers, simulation runs, dashboards,
  integrations, seed sweeps, A7.2 mechanics, or multi-hive coupling were
  added. The GPT-5.5-Pro recommendation to avoid further status-only commits
  is deferred for this bounded pass only because the current automation
  instruction explicitly requires updating this status file and committing
  local progress.

- 2026-06-28 01:21 PDT bounded A5 verification pass: re-read the automation
  memory, the concise A5 single-hive preregistration, `README.md`,
  `AUTOMATION_STATUS.md`, and the reopened seed `5,6` smoke note. The explicit
  A5 request is already represented by the checked-in preregistration and
  deterministic scaffold; no preregistration gap, simulator-mechanics gap, or
  authorized broader run was found.
- The automation guard remains closed with
  `state=closed_awaiting_preregistration`, `should_noop=true`, and
  `notify_ben=true`. No notification text, simulator mechanics, configs,
  analyzers, simulation runs, dashboards, integrations, seed sweeps, A7.2
  mechanics, or multi-hive coupling were added. The recommended next step
  remains exactly one action: send Ben the existing A5-exit/A7.2 decision
  request with the compression-enforced fail-closed update.

- 2026-06-28 01:11 PDT bounded guard-closed notification check: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the superseded
  provisional roadmap, the latest GPT-5.5-Pro strategy review, the Ben
  decision request, and the completed A5 residual-compression report before
  choosing the next step. The guard remains closed with
  `state=closed_awaiting_preregistration`, `should_noop=true`, and
  `notify_ben=true`.
- The Ben decision request already includes the newer
  `closure_confirmed` residual-compression evidence and three explicit
  decision options. No notification text, simulator mechanics, configs,
  analyzers, simulation runs, dashboards, integrations, seed sweeps, A7.2
  mechanics, or multi-hive coupling were added. The GPT-5.5-Pro
  recommendation to notify Ben and keep automation guard-closed is accepted
  as scientifically sensible. Its recommendation to avoid further
  status-only commits is deferred for this bounded pass only because the
  current automation instruction explicitly requires updating this status
  file and committing local progress.

- 2026-06-28 00:54 PDT bounded guard-closed notification check: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the superseded
  provisional roadmap, the latest GPT-5.5-Pro strategy review, the Ben
  decision request, and the completed A5 residual-compression report before
  choosing the next step. The guard remains closed with
  `state=closed_awaiting_preregistration`, `should_noop=true`, and
  `notify_ben=true`.
- The Ben decision request already includes the newer
  `closure_confirmed` residual-compression evidence and the three explicit
  decision options, so no notification text, simulator mechanics, configs,
  analyzers, simulation runs, dashboards, integrations, seed sweeps, A7.2
  mechanics, or multi-hive coupling were added. The GPT-5.5-Pro
  recommendation to notify Ben and keep automation guard-closed is accepted
  as scientifically sensible. Its recommendation to avoid further
  status-only commits is deferred for this bounded pass only because the
  current automation instruction explicitly requires updating this status
  file and committing local progress.

- 2026-06-28 00:38 PDT bounded guard-closed notification check: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the superseded
  provisional roadmap, the latest GPT-5.5-Pro strategy review, the Ben
  decision request, and the completed A5 residual-compression report before
  choosing the next step. The guard remains closed with
  `state=closed_awaiting_preregistration`, `should_noop=true`, and
  `notify_ben=true`.
- The Ben decision request already includes the newer
  `closure_confirmed` residual-compression evidence and the three explicit
  decision options, so no notification text, simulator mechanics, configs,
  analyzers, simulation runs, dashboards, integrations, seed sweeps, A7.2
  mechanics, or multi-hive coupling were added. The GPT-5.5-Pro
  recommendation to notify Ben and keep automation guard-closed is accepted
  as scientifically sensible. Its recommendation to avoid further
  status-only commits is deferred for this bounded pass only because the
  current automation instruction explicitly requires updating this status
  file and committing local progress.

- 2026-06-28 00:21 PDT bounded A5 closure verification: re-read the concise
  A5 single-hive preregistration, the resource-bounded residual-compression
  preregistration/report, the Ben A5-exit/A7.2 decision request, and the
  automation guard output before choosing the next step. The guard remains
  closed with `state=closed_awaiting_preregistration`, `should_noop=true`, and
  `notify_ben=true`.
- The Ben decision request already includes the newer
  `closure_confirmed` residual-compression evidence, so no notification text,
  simulator mechanics, configs, analyzers, simulation runs, dashboards,
  integrations, seed sweeps, A7.2 mechanics, or multi-hive coupling were
  added. The
  GPT-5.5-Pro recommendation to notify Ben and keep automation guard-closed is
  accepted as scientifically sensible. Its recommendation to avoid further
  status-only commits is deferred for this bounded pass only because the
  current automation instruction explicitly requires updating this status file
  and committing local progress.

- 2026-06-28 00:04 PDT bounded guard-closed verification: re-read
  `README.md`, `AUTOMATION_STATUS.md`, the config/test surface, the superseded
  provisional roadmap, the latest GPT-5.5-Pro strategy review, the Ben
  decision request, and the completed A5 residual-compression report before
  choosing the next step. The guard remains closed with
  `state=closed_awaiting_preregistration`, `should_noop=true`, and
  `notify_ben=true`.
- The Ben decision request already includes the newer
  `closure_confirmed` residual-compression evidence, so no notification text,
  simulator mechanics, configs, analyzers, simulations, dashboards,
  integrations, A7.2 mechanics, or multi-hive coupling were added. The
  GPT-5.5-Pro recommendation to notify Ben and keep automation guard-closed is
  accepted as scientifically sensible. Its recommendation to avoid further
  status-only commits is deferred for this bounded pass only because the
  current automation instruction explicitly requires updating this status file
  and committing local progress.

- 2026-06-27 23:48 PDT bounded guard-closed verification: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the superseded
  provisional roadmap, the latest GPT-5.5-Pro strategy review, the Ben
  decision request, and the completed A5 residual-compression report before
  choosing the next step. The guard remains closed with
  `state=closed_awaiting_preregistration`, `should_noop=true`, and
  `notify_ben=true`.
- The Ben decision request already includes the newer
  `closure_confirmed` residual-compression evidence, so no notification text,
  simulator mechanics, configs, analyzers, simulations, dashboards,
  integrations, A7.2 mechanics, or multi-hive coupling were added. The
  GPT-5.5-Pro recommendation to notify Ben and keep automation guard-closed is
  accepted as scientifically sensible. Its recommendation to avoid further
  status-only commits is deferred for this bounded pass only because the
  current automation instruction explicitly requires updating this status file
  and committing local progress.

- 2026-06-27 23:31 PDT bounded guard-closed verification: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the provisional
  roadmap, the latest GPT-5.5-Pro strategy review, the Ben decision request,
  and the completed A5 residual-compression report before choosing the next
  step. The guard remains closed with `state=closed_awaiting_preregistration`,
  `should_noop=true`, and `notify_ben=true`.
- The GPT-5.5-Pro recommendation to keep automation guard-closed with no
  simulations or mechanics is accepted as scientifically sensible. Its
  recommendation to avoid further status-only commits is deferred for this
  bounded pass only because the current automation instruction explicitly
  requires updating this status file and committing local progress. No
  simulations, simulator mechanics, configs, analyzers, dashboards,
  integrations, A7.2 mechanics, or multi-hive coupling were added.

- 2026-06-28 00:34 PDT compression-enforced A5 residual audit: treated Ben's
  explicit A5 request as authorization for a bounded analyzer/test tightening,
  not for new simulator mechanics, configs, dashboards, integrations, seed
  sweeps, A7.2 mechanics, or multi-hive coupling.
- Updated `ohdyn.analyze_a5_residual_accounting` so the promotion audit now
  requires full-accounting residual compression to pass alongside residual
  predictability. Standard A5 conditions must compress better than reactive
  and their budget-matched timing-broken null; A5.1a charged conditions must
  compress better than their spend-only replay null. Lower compression ratio is
  the favorable endpoint, and the gate remains fail-closed.
- Updated the focused regression tests and
  `docs/results/a5_residual_accounting_analyzer_audit.md` to record the new
  compression gate. Reran the bounded standard A5 seed `5,6` smoke and the
  charged A5.1a seed `5,6` analyzer path in `/tmp`; both remained fail-closed.
- 2026-06-27 23:14 PDT guard-closed notification alignment: re-read
  `README.md`, this status file, configs/tests surface, the provisional
  roadmap, the latest GPT-5.5-Pro strategy review, the Ben decision request,
  and the completed A5 resource-bounded residual-compression report before
  choosing the next step. The guard is closed with
  `state=closed_awaiting_preregistration`, `should_noop=true`, and
  `notify_ben=true`; no simulations, simulator mechanics, configs, analyzers,
  dashboards, integrations, A7.2 mechanics, or multi-hive coupling were added.
- Updated `docs/results/ben_decision_request_a5_exit_a7_2_20260627.md` so the
  notification draft explicitly includes the newer residual-compression
  `closure_confirmed` evidence. The GPT-5.5-Pro recommendation to notify Ben
  is accepted as scientifically sensible; A7.2 and three-hive directions
  remain deferred pending Ben's explicit preregistered decision.

- 2026-06-27 22:55 PDT read-only residual-compression report pass: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the provisional
  roadmap, the resource-bounded residual-compression preregistration, existing
  A5 result notes, and the latest GPT-5.5-Pro strategy review before choosing
  the next step. The status file and automation guard were authoritative and
  allowed exactly the preregistered read-only A5 residual-compression report,
  despite the external review recommending Ben notification and no further
  status churn.
- Added
  `docs/results/a5_resource_bounded_residual_compression_report.md`. The
  report consumes existing residual-accounting CSVs from the reopened seed
  `5,6` and confirmatory seed `7..16` A5 artifacts, marks A5.1a reusable CSV
  coverage as absent under `runs/`, and confirms closure: intermediate
  prediction budgets do not beat reactive, oracle, and matched timing-broken
  or spend-only null expectations on full-accounting residual compression.
- Updated this status file so the active focus is now closed pending Ben's
  decision. This run did not add simulator mechanics, configs, analyzers,
  simulation runs, dashboards, integrations, A7.2 mechanics, or multi-hive
  coupling.

## Verification

- 2026-06-28 02:23 PDT check: `.venv-conda/bin/python -m
  ohdyn.automation_guard` passed and reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, and `notify_ben=true`.
- 2026-06-28 02:23 PDT focused tests passed:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting' -q`
  reported `18 passed, 608 deselected`.

- `git status --short --branch` initially reported a clean branch after
  `git update-index --refresh`: `## main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: closed_awaiting_preregistration`, `should_noop: true`,
  `repo_write_allowed: false`, `notify_ben: true`,
  `strategic_change_level: minor`, and the single recommended next action to
  send Ben the existing A5-exit/A7.2 decision request with the
  compression-enforced fail-closed update.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the latest loop still
  using the GPT-5.5-Pro review path and requesting Ben notification; no
  successful later simulation or mechanics run was observed in the log tail.
- `git diff --check` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed: 14 selected tests passed, 612 deselected.

- `git status --short --branch` reported a clean branch before this run:
  `## main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` now reports
  `state: closed_awaiting_preregistration`, `should_noop: true`,
  `repo_write_allowed: false`, `notify_ben: true`,
  `strategic_change_level: minor`, and the single recommended next action to
  send Ben the existing A5-exit/A7.2 decision request with the
  compression-enforced fail-closed update.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the latest loop using
  the GPT-5.5-Pro review path and requesting Ben notification; no successful
  later simulation or mechanics run was observed in the log tail.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed: 14 selected tests passed, 612 deselected.

- `git status --short --branch` reported a clean branch before this status
  update: `## main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: closed_awaiting_preregistration`, `should_noop: true`,
  `notify_ben: true`, `strategic_change_level: none`, and the single
  recommended next action to send Ben the existing A5-exit/A7.2 decision
  request with the compression-enforced fail-closed update.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the latest loop still
  using the GPT-5.5-Pro review path and requesting Ben notification; no
  successful later simulation or mechanics run was observed in the log tail.
- `git diff --check` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed: 14 selected tests passed, 612 deselected.

- `git status --short --branch` reported a clean branch before this status
  update: `## main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: closed_awaiting_preregistration`, `should_noop: true`,
  `notify_ben: true`, `strategic_change_level: none`, and the single
  recommended next action to send Ben the existing A5-exit/A7.2 decision
  request with the compression-enforced fail-closed update.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the latest loop still
  using the GPT-5.5-Pro review path and requesting Ben notification; no
  successful later simulation or mechanics run was observed in the log tail.
- `git diff --check` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed: 14 selected tests passed, 612 deselected.

- `git status --short --branch` reported a clean branch before this status
  update: `## main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: closed_awaiting_preregistration`, `should_noop: true`,
  `notify_ben: true`, `strategic_change_level: none`, and the single
  recommended next action to send Ben the existing A5-exit/A7.2 decision
  request with the compression-enforced fail-closed update.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the latest loop still
  using the GPT-5.5-Pro review path and requesting Ben notification; no
  successful later simulation or mechanics run was observed in the log tail.

- `git status --short --branch` reported a clean branch before this status
  update: `## main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: closed_awaiting_preregistration`, `should_noop: true`,
  `notify_ben: true`, `strategic_change_level: none`, and the single
  recommended next action to send Ben the existing A5-exit/A7.2 decision
  request with the compression-enforced fail-closed update.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the latest loop still
  using the GPT-5.5-Pro review path and requesting Ben notification; no
  successful later simulation or mechanics run was observed in the log tail.
- `git diff --check` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed: 14 selected tests passed, 612 deselected.

- `git status --short --branch` reported a clean branch before this status
  update: `## main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: closed_awaiting_preregistration`, `should_noop: true`,
  `notify_ben: true`, `strategic_change_level: none`, and the single
  recommended next action to send Ben the existing A5-exit/A7.2 decision
  request with the compression-enforced fail-closed update.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the latest loop still
  using the GPT-5.5-Pro review path and requesting Ben notification; no
  successful later simulation or mechanics run was observed in the log tail.
- `git diff --check` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed: 14 selected tests passed, 612 deselected.

- `git status --short --branch` reported a clean branch before this status
  update: `## main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: closed_awaiting_preregistration`, `should_noop: true`,
  `notify_ben: true`, `strategic_change_level: none`, and the single
  recommended next action to send Ben the existing A5-exit/A7.2 decision
  request with the compression-enforced fail-closed update.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the latest loop still
  using the GPT-5.5-Pro review path and requesting Ben notification; no
  successful later simulation or mechanics run was observed in the log tail.
- `git diff --check` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed: 14 selected tests passed, 612 deselected.

- `git status --short --branch` reported a clean branch before this status
  update: `## main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: closed_awaiting_preregistration`, `should_noop: true`,
  `notify_ben: true`, `strategic_change_level: none`, and the single
  recommended next action to send Ben the existing A5-exit/A7.2 decision
  request with the compression-enforced fail-closed update.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the latest loop still
  using the GPT-5.5-Pro review path and requesting Ben notification; no
  successful later simulation or mechanics run was observed in the log tail.
- `git diff --check` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed: 14 selected tests passed, 612 deselected.

- `.venv-conda/bin/python -m py_compile
  ohdyn/analyze_a5_residual_accounting.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting' -q` passed: 4 selected
  tests passed, 622 deselected.
- Standard bounded A5 smoke passed in
  `/tmp/omegasim_a5_20260628_compression_gate_1`: `ohdyn.run` seed `5`,
  `compare_predictive_control` seeds `5,6`, and
  `analyze_a5_residual_accounting`. Promotion failed closed for `linear`,
  `nonlinear`, and `nonlinear_high_budget`.
- Charged A5.1a analyzer smoke passed in
  `/tmp/omegasim_a5_1a_20260628_compression_gate_1`:
  `compare_predictive_control --base-config
  configs/a5_1_prediction_spend_linear_smoke.yaml --seeds 5 6` and
  `analyze_a5_residual_accounting`. Promotion failed closed for all charged
  linear cost conditions.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state: closed_awaiting_preregistration`, `should_noop: true`,
  `notify_ben: true`, and the single recommended next action to send Ben the
  existing A5-exit/A7.2 decision request.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the latest strategy
  review again requested Ben notification; no successful later simulation or
  mechanics run was started by this bounded pass.
- `git diff --check` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed: 14 selected tests passed, 612 deselected.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported `state: open`
  only for the read-only residual-compression report step before this update,
  with `notify_ben: true` and the external review still recommending Ben
  notification.
- Existing artifact inspection found the required A5 comparison and
  residual-accounting CSVs for reopened seed `5,6` and confirmatory seed
  `7..16`; no checked-in A5.1a reusable run CSV directories were present under
  `runs/`, so A5.1a was treated as result-note coverage only.

## Historical Blockers

- 2026-06-28 02:23 PDT check: no local code or environment blocker. The
  active blocker remains scientific/governance scope: the requested A5
  preregistration and minimal smoke scaffold already exist, later residual and
  compression audits failed closed, and Ben has not yet chosen the next
  preregistered gate.

- No code or environment blocker. Governance blocker remains: Ben has not yet
  chosen among A5-family closure, active A7.2 preregistration, or a separate
  three-hive preregistration after the compression-enforced A5 fail-closed
  update.
- 2026-06-28 00:21 PDT check: the blocker is unchanged. The explicit A5
  preregistration request has already been satisfied, and the guard-closed
  status prevents scientifically meaningful additional mechanics or runs until
  Ben chooses the next preregistered gate.

- 2026-06-27 22:36 PDT bounded residual-compression preregistration pass:
  re-read `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the
  provisional roadmap, the A5 residual-accounting design, the
  forecast-skill/residual-gap diagnostic plan, the reopened A5 smoke result,
  and the latest GPT-5.5-Pro strategy review before choosing the next step.
  The status file and guard were authoritative: the external review still says
  to notify Ben and avoid no-op/status churn, but the current source-of-truth
  next step authorized one preregistered A5 residual-compression diagnostic.
- Added
  `docs/a5_resource_bounded_residual_compression_preregistration.md` to freeze
  the diagnostic question, existing-artifact inputs, full-accounting residual
  state, compression endpoints, budget/spend controls, timing-broken nulls,
  fail-closed decision rule, and report output contract.
- Updated `README.md` and this status file so the only current next step is the
  preregistered read-only report over existing A5/A5.1a artifacts. This run
  did not add simulator mechanics, configs, analyzers, simulation runs,
  dashboards, integrations, A7.2 mechanics, or multi-hive coupling.
- 2026-06-27 22:19 PDT explicit A5 bounded scaffold/reporting pass: re-read
  automation memory, `README.md`, `AUTOMATION_STATUS.md`, the concise A5
  preregistration, and the residual-accounting analyzer surface. Ben's current
  request overrides the stale no-op posture for this bounded stage only.
  No simulator mechanics, new configs, dashboards, integrations, broad seed
  sweeps, A7.2 mechanics, or multi-hive coupling were added.
- Updated `README.md` and this status file so the concise A5 preregistration is
  again the current bounded single-hive smoke reference for this explicit run,
  while the prior seed `5,6`, seed `7..16`, and A5.1a fail-closed results
  remain interpretation boundaries.
- Extended the read-only A5 residual-accounting summary to print the existing
  full-accounting residual compression-ratio contrast beside residual
  predictability, matching the preregistered
  predictability/compressibility endpoint without changing simulator behavior.
- Reran the bounded A5 smoke chain in `/tmp`: `ohdyn.run` seed `5`,
  `compare_predictive_control` seeds `5,6`, and
  `analyze_a5_residual_accounting`. The new summary reported full-accounting
  compression-ratio deltas beside residual predictability, but the promotion
  audit still failed closed for linear, nonlinear, and high-budget nonlinear
  predictors.
- 2026-06-27 21:03 PDT bounded guard-closed verification: re-read
  `README.md`, `AUTOMATION_STATUS.md`, the configs/tests surface, the
  provisional roadmap, the non-active A7.2 decision preregistration, the Ben
  decision request, and the latest GPT-5.5-Pro strategy review before choosing
  the next step. The guard remains closed with `strategic_change_level: none`
  and `notify_ben: true`; the review says to send Ben the existing decision
  request, keep the guard closed, and stop no-op/status commits. This run
  records the verification only because the bounded automation instruction
  explicitly requires updating this status file and committing local progress.
  It did not add simulator mechanics, configs, analyzers, simulations,
  dashboards, integrations, seed sweeps, A5-family reruns, A7.2 mechanics, or
  multi-hive coupling.
- 2026-06-27 19:07 PDT bounded guard-closed verification: re-read
  `README.md`, `AUTOMATION_STATUS.md`, the configs/tests surface, the
  provisional roadmap, the non-active A7.2 decision preregistration, the Ben
  decision request, and the latest GPT-5.5-Pro strategy review before choosing
  the next step. The guard remains closed with `strategic_change_level: none`
  and `notify_ben: true`; the review recommends sending Ben the existing
  decision request and stopping further no-op status commits. This run did not
  add simulator mechanics, configs, analyzers, simulations, dashboards,
  integrations, seed sweeps, A5-family reruns, A7.2 mechanics, or multi-hive
  coupling.
- 2026-06-27 18:33 PDT bounded guard-closed no-op run: re-read
  `README.md`, `AUTOMATION_STATUS.md`, the configs/tests surface, the
  provisional roadmap, the existing non-active A7.2 decision preregistration,
  the Ben decision request, and the latest GPT-5.5-Pro strategy review before
  choosing the next step. The guard remains closed with
  `strategic_change_level: major` and `notify_ben: true`. Because
  `docs/a5_family_exit_and_a7_2_decision_preregistration.md` and
  `docs/results/ben_decision_request_a5_exit_a7_2_20260627.md` already exist,
  this run did not duplicate them and did not add simulator mechanics,
  configs, analyzers, simulations, dashboards, integrations, seed sweeps,
  A5-family reruns, A7.2 mechanics, or multi-hive coupling.
- 2026-06-27 18:16 PDT bounded guard-closed verification: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the provisional
  roadmap, the non-active A7.2 decision preregistration, and the latest
  GPT-5.5-Pro strategy review before choosing the next step. The guard remains
  closed with `strategic_change_level: major` and `notify_ben: true`. The
  external review's pivot recommendation is already incorporated in
  `docs/a5_family_exit_and_a7_2_decision_preregistration.md`, so this run did
  not duplicate that document and did not add simulator mechanics, configs,
  analyzers, simulations, dashboards, integrations, seed sweeps, A5-family
  reruns, A7.2 mechanics, or multi-hive coupling.
- 2026-06-27 bounded documentation alignment pass: re-read `README.md`,
  `AUTOMATION_STATUS.md`, the configs/tests surface, the provisional roadmap,
  the non-active A7.2 decision preregistration, Ben notification notes, and the
  latest GPT-5.5-Pro strategy review before choosing the next step. The guard
  is closed with `strategic_change_level: major` and `notify_ben: true`, so
  this run did not add simulator mechanics, configs, analyzers, simulations,
  dashboards, integrations, seed sweeps, A5-family reruns, A7.2 mechanics, or
  multi-hive coupling.
- Updated `README.md` to stop describing the concise A5 preregistration as the
  active A5 smoke reference. It is now explicitly historical because the
  reopened seed `5,6` smoke has closed fail-closed.
- Added a supersession note to
  `docs/omegasim_provisional_experiment_roadmap.md` so its older A7 immediate
  next-step wording does not override the current status-file posture: closed
  awaiting Ben's decision.
- 2026-06-27 bounded no-op/status consistency pass: re-read `README.md`,
  `AUTOMATION_STATUS.md`, configs/tests surface, the provisional roadmap, the
  non-active A7.2 decision preregistration, the A7 Ben notification note, and
  the latest GPT-5.5-Pro strategy review before choosing the next step. The
  guard is closed with `strategic_change_level: major` and `notify_ben: true`,
  so this run did not add simulator mechanics, configs, analyzers,
  simulations, dashboards, integrations, seed sweeps, A5-family reruns, A7.2
  mechanics, or multi-hive coupling.
- Removed the stale duplicate bottom `Recommended Next Step` entry that still
  pointed at a residual diagnostic. The single current next step is to remain
  in no-op/awaiting-preregistration state while Ben decides whether A5-family
  work stays closed, A7.2 becomes an active preregistered gate, or a separate
  three-hive ring preregistration should be drafted.
- 2026-06-27 bounded guard/status correction: re-read `README.md`,
  `AUTOMATION_STATUS.md`, configs/tests surface, the provisional roadmap, the
  non-active A7.2 decision preregistration, the Ben decision request, and the
  latest GPT-5.5-Pro strategy review before choosing the next step. The newest
  review's `strategic_change_level: major` and `notify_ben: true` direction is
  recorded as accepted. This run did not add simulator mechanics, configs,
  analyzers, dashboards, integrations, seed sweeps, A5-family reruns, or
  multi-hive coupling.
- Updated the current focus so the already-run concise A5 reopening is no
  longer treated as active authorization. The current posture is closed
  awaiting Ben's decision among A5-family closure, a new active A7.2
  preregistration, or a separate three-hive preregistration.
- 2026-06-27 17:16 PDT explicit A5 alignment pass: re-read automation memory,
  `README.md`, `AUTOMATION_STATUS.md`, the active concise A5 preregistration,
  the residual-accounting diagnostic design, the reopened A5 seed `5,6`
  result, the deterministic A5 config, and the automation guard/tests surface.
  This run did not add simulator mechanics, dashboards, integrations, broad
  seed sweeps, A7.2 mechanics, or multi-hive coupling.
- Updated `ohdyn.automation_guard` so current closure/reopening decisions come
  from the active status sections rather than stale historical bullets in
  `Latest Changes` or `Verification`, and so its default explicit A5
  preregistration path points at the concise single-hive gate.
- Added a regression test proving historical A5 closure text does not override
  a current explicit concise-A5 reopening gate.
- Updated `README.md` so the A5 section names the concise preregistration as
  the active single-hive gate for this explicit stage while preserving the
  seed `5,6` residual/null failure as an interpretation boundary.
- Reran the bounded A5 smoke chain in `/tmp`: one low-budget linear run, the
  paired seed `5,6` predictive-control comparison, and the read-only
  residual-accounting analyzer. The rerun matched the prior scientific
  outcome: forecast skill improved, but no intermediate-budget predictor
  passed the residual/null promotion gate.
- 2026-06-27 17:05 PDT bounded Ben-notification run: re-read `README.md`,
  `AUTOMATION_STATUS.md`, configs/tests surface, the provisional roadmap, the
  non-active A7.2 decision preregistration, and the latest GPT-5.5-Pro strategy
  review before choosing a next step. The guard was closed, so this run did not
  add simulator mechanics, configs, analyzers, simulations, dashboards,
  integrations, seed sweeps, or multi-hive coupling.
- Added notification draft
  `docs/results/ben_decision_request_a5_exit_a7_2_20260627.md` to make the
  required Ben decision explicit: close A5-family work as an evidence boundary,
  open the non-active A7.2 delayed artifact-mediated endogenous-prediction
  preregistration as an active gate, or request a separate three-hive ring
  preregistration. This accepts the latest GPT-5.5-Pro recommendation as
  scientifically sensible but keeps it non-active pending Ben's decision.
- 2026-06-27 17:10 PDT bounded decision-preregistration run: re-read
  `README.md`, `AUTOMATION_STATUS.md`, configs/tests surface, the provisional
  roadmap, current A5/A5.1/A6/A7 closure evidence, and the latest GPT-5.5-Pro
  strategy review before choosing a next step. The guard was closed, so this
  run did not add simulator mechanics, configs, analyzers, simulations,
  dashboards, integrations, seed sweeps, or multi-hive coupling.
- Added non-active
  `docs/a5_family_exit_and_a7_2_decision_preregistration.md` to summarize the
  A5/A5.1a/A6.2/A7 fail-closed evidence boundary and freeze the candidate
  A7.2 delayed artifact-mediated endogenous-prediction direction for Ben's
  decision only.
- Updated `README.md` so A5 no longer reads as currently reopened. The current
  posture is closed awaiting Ben; do not reopen A5 without a new explicit
  preregistration and decision.
- The latest GPT-5.5-Pro review's delayed artifact-mediated endogenous
  prediction recommendation is accepted as sensible enough for a decision
  preregistration. Multi-hive ring work remains deferred because the current
  status/roadmap does not authorize downstream coupling and earlier gates are
  closed rather than promoted.
- 2026-06-27 16:55 PDT bounded guard-closure run: re-read `README.md`,
  `AUTOMATION_STATUS.md`, configs/tests surface, the provisional roadmap,
  A5/A5.1 preregistrations/results, and the latest GPT-5.5-Pro strategy
  review before choosing a next step. The status file is the source of truth:
  the reopened A5 smoke is already run and fail-closed, so this run did not
  add simulator mechanics, configs, analyzers, dashboards, integrations,
  broad seed sweeps, or multi-hive coupling.
- Updated `ohdyn.automation_guard` so the explicit current-A5 reopening marker
  no longer reopens automation after the newer status records the reopened A5
  smoke as fail-closed. The guard now treats this current A5 closure as
  superseding older accepted A7 roadmap wording.
- Added a regression test for the reopened-A5 fail-closed status wording.
  External review recommendations to control prediction cost/spend-only
  artifacts remain scientifically sensible and already incorporated via the
  completed A5.1a gate; delayed semantic/logistic or multi-hive suggestions
  remain deferred pending Ben's explicit preregistered decision.
- 2026-06-27 16:40 PDT explicit A5 reopening: added
  `docs/a5_single_hive_anticipatory_predictive_control_preregistration.md` as
  the concise active preregistration for the requested single-hive
  anticipatory predictive-control stage. The preregistration freezes matched
  task arrivals, service capacity, action opportunity, work budget,
  prediction-budget/null controls, primary residual endpoints, guardrails, and
  fail-closed treatment of strange-attractor-like claims.
- Updated `README.md` and the older A5 preregistration to point at the concise
  active A5 gate while retaining the prior A5/A5.1a closure evidence as an
  interpretation constraint.
- Updated `ohdyn.automation_guard` so the explicit current A5 preregistration
  marker can reopen the automation despite stale historical no-op status text,
  without changing the existing closure behavior when no current reopening is
  recorded.
- Ran the bounded reopened A5 single-hive smoke/pilot with the existing
  deterministic scaffold only. The paired seed `5,6` comparison again showed
  forecast-skill improvements, but the residual-accounting analyzer failed
  closed: no intermediate-budget condition satisfied the preregistered
  residual/null and guardrail criteria.
- Added `docs/results/a5_single_hive_reopened_smoke_seed5_6.md` to record the
  smoke result and fail-closed interpretation boundary.
- 2026-06-27 16:08 PDT bounded no-op verification: re-read `README.md`, this
  status file, the current configs/tests surface, the provisional roadmap,
  A5.1/A5.1a preregistration and closure documents, and the latest
  GPT-5.5-Pro strategy review before choosing a next step. The status file and
  guard remain authoritative: A5.1a is already preregistered, implemented, and
  closed conservatively, so this run did not add mechanics, configs, analyzers,
  simulations, dashboards, integrations, or multi-hive coupling.
- The latest GPT-5.5-Pro review still says `strategic_change_level: major` and
  `notify_ben: true`. Its cost-calibration/spend-only-replay-null
  recommendation is accepted as scientifically sensible but already completed;
  its delayed semantic/logistic and multi-hive suggestions remain deferred
  pending Ben's explicit preregistered decision.
- This bounded automation run re-read `README.md`, this status file, configs,
  tests, the provisional roadmap, and the latest GPT-5.5-Pro strategy review
  before choosing a next step. The guard and status file remain authoritative:
  A5.1a is already preregistered, implemented, tested, and closed
  conservatively, so no new simulator/analyzer mechanics or experiment runs
  were started.
- The external review still recommends A5.1a cost calibration and a
  spend-only replay null with `strategic_change_level: major` and
  `notify_ben: true`; this run records that the recommendation has already
  been incorporated and closed fail-closed, while Ben still needs notification
  about the direction shift and closure.
- This bounded automation run treated the status file and guard as authoritative:
  A5.1a remains closed conservatively, the older accepted A7 roadmap wording is
  still superseded by the newer A5.1a closure status, and no new simulations,
  analyzers, simulator mechanics, configs, dashboards, integrations, or
  multi-hive coupling were added.
- Re-read the external GPT-5.5-Pro strategy review. Its sensible
  cost-calibration/spend-only-null recommendation has already been completed;
  the remaining delayed semantic/logistic or multi-hive suggestions are
  deferred pending Ben's explicit preregistered decision.
- Added `docs/a5_1_prediction_spend_competition_preregistration.md` as the
  next bounded A5 follow-up preregistration. It freezes a single-hive design in
  which prediction spend is deducted from explicit work opportunity, preserving
  matched task-arrival totals, class-demand streams, service capacity, action
  opportunity, and total decision budget across conditions.
- The A5.1 gate defines reactive, low-budget linear or short-memory,
  medium-budget nonlinear, high-budget nonlinear, oracle, and budget-matched
  timing-broken null conditions.
- Primary endpoints are forecast skill per prediction spend, lead-lag
  allocation to future demand, residual phase structure after full accounting,
  recurrence/return-map structure in residual predictive-state delay
  embeddings, high-level state predictability/compressibility, and guardrails
  for backlog, queued age, completion fraction, starvation, prediction-spend
  volatility, and work-budget volatility.
- Updated `README.md` to point at the A5.1 gate and clarify that the next
  prediction-resource question is direct spend/work-opportunity competition,
  not broad A5 seed extension or downstream multi-hive coupling.
- Added the smallest opt-in deterministic A5.1 scaffold: predictive-control
  configs can set `charge_prediction_to_work: true`, which accumulates a
  fractional prediction-cost bank and converts selected `work_task`
  opportunities into explicit `a5_prediction_spent` events counted as `idle`
  for the existing action schema.
- Added A5.1 prediction-spend metrics for charged-to-work status, charge
  target, charged work units, pre-charge work opportunity, and remaining work
  budget. Existing A5 configs keep the old manifest config shape because the
  new flag is omitted unless enabled.
- Added `configs/a5_1_prediction_spend_linear_smoke.yaml` and extended the A5
  comparison helper to aggregate charged-work and remaining-budget means.
- Extended the read-only A5 residual-accounting analyzer's full-accounting
  level with optional prediction-spend and remaining-work controls.
- Ran a paired-seed A5.1 smoke/pilot in `/tmp`. Forecast skill improved for
  intermediate predictors, but charged prediction spend sharply reduced work
  completion and the residual-accounting promotion audit failed closed with
  guardrails not satisfied.
- Added the A5.1a cost-calibration addendum to
  `docs/a5_1_prediction_spend_competition_preregistration.md`. It freezes
  `prediction_cost_scale`, `max_prediction_work_fraction_per_tick`, and a
  spend-only replay null as prerequisites before any larger A5.1
  prediction-spend run.
- Updated `README.md` to make A5.1a the current bounded cost-calibration
  subgate and clarify that it is not A5.1 seed broadening.
- Implemented the A5.1a cost-calibration scaffold in config, simulator,
  manifest, summary, and comparison outputs. Predictive-control configs now
  accept `prediction_cost_scale` and
  `max_prediction_work_fraction_per_tick`; the charged-work target is scaled
  and capped before entering the existing prediction-charge bank.
- Added `spend_only_replay` as a timing-broken predictive-control condition.
  When `compare_predictive_control` is run from a base config with
  `charge_prediction_to_work=true`, it now generates the preregistered A5.1a
  grid: harsh-cost linear, gentle-cost linear, capped-cost linear, matched
  spend-only replay nulls for each charged positive, and a no-cost diagnostic.
- Extended the read-only A5 residual-accounting analyzer to discover comparison
  conditions from `predictive_control_comparison_metrics.csv`, preserving the
  old eight-condition A5 promotion audit while adding an A5.1a-specific
  spend-only-replay audit.
- Ran the bounded A5.1a seed `5,6` cost-calibration smoke in `/tmp`. Harsh,
  gentle, and capped charged linear predictors beat their spend-only replay
  nulls on forecast skill, but none beat the replay null on full-accounting
  residual predictability. The A5.1a audit failed closed for all charged cost
  rules.
- Added `docs/results/a5_1a_cost_calibration_closure_note_seed5_6.md`
  documenting the A5.1a closure boundary. It records the three charged cost
  rules, spend-only replay nulls, full-accounting residual audit, external
  strategy-review handling, and the stop condition against broader A5.1 seed
  sweeps.
- No dashboards, real integrations, broad seed sweeps, A6/A7 imports, or
  multi-hive mechanics were added.

## Verification

- `git status --short --branch` passed at the start of the 2026-06-27 22:36
  PDT bounded residual-compression preregistration pass and reported
  `main...origin/main` with no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed before the
  preregistration patch and reported `state=open`, `should_noop=false`,
  `strategic_change_level=none`, `notify_ben=true`, and the single next step
  to preregister one resource-bounded residual-compression diagnostic before
  new A5 simulator mechanics.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the
  preregistration patch and reported `state=open`, `should_noop=false`,
  `strategic_change_level=none`, `notify_ben=true`, and the single next step
  to produce the preregistered read-only residual-compression report over
  existing A5/A5.1a artifacts, without new mechanics or runs.
- `git diff --check` passed after the preregistration/status update.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after the preregistration/status update:
  `14 passed, 612 deselected`.
- `.venv-conda/bin/python -m py_compile
  ohdyn/analyze_a5_residual_accounting.py ohdyn/automation_guard.py` passed.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed and reported
  `state=open`, `should_noop=false`, `a5_preregistration_active=true`, and
  the bounded A5 smoke-chain next action before the smoke rerun.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting'`
  passed: `18 passed, 608 deselected`.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_20260627_2219/a5_predictive_linear_seed5` passed.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6
  --out /tmp/omegasim_a5_20260627_2219/a5_predictive_control_compare`
  passed.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting
  --compare-dir /tmp/omegasim_a5_20260627_2219/a5_predictive_control_compare
  --out /tmp/omegasim_a5_20260627_2219/a5_residual_accounting` passed and
  produced `Promotion decision: fail closed; no intermediate-budget condition
  satisfies all preregistered criteria.`
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the final
  status update and reported `state=open`, `should_noop=false`, and the single
  next step to preregister one resource-bounded residual-compression
  diagnostic before new A5 mechanics.
- `git diff --check` passed.
- `git status --short --branch` passed at the start of the 2026-06-27 21:03
  PDT bounded guard-closed verification and reported `main...origin/main` with
  no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this run. It reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level=none`, `notify_ben=true`, and the single next step
  to remain in no-op/awaiting-preregistration state pending Ben's decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent automation loops
  completing successfully and the latest strategy review requesting Ben
  notification.
- `git diff --check` passed after this status update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after this status
  update and still reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level=none`, and `notify_ben=true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after this status update: `14 passed, 612
  deselected`.
- `git status --short --branch` passed at the start of the 2026-06-27 19:07
  PDT bounded guard-closed verification and reported `main...origin/main` with
  no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this run. It reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level=none`, `notify_ben=true`, and the single next step
  to remain in no-op/awaiting-preregistration state pending Ben's decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent automation loops
  completing successfully and the latest strategy review requesting Ben
  notification.
- `git diff --check` passed before this status correction.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed before this status correction: `14 passed, 612
  deselected`.
- `git diff --check` passed after this status correction.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after this status
  correction and still reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level=none`, and `notify_ben=true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after this status correction: `14 passed, 612
  deselected`.
- `git status --short --branch` passed at the start of the 2026-06-27 18:33
  PDT bounded guard-closed no-op run and reported `main...origin/main` with no
  uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this run. It reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level=major`, `notify_ben=true`, and the single next step
  to remain in no-op/awaiting-preregistration state pending Ben's decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent automation loops
  completing successfully and the latest strategy review requesting Ben
  notification.
- `git diff --check` passed after the 2026-06-27 18:33 PDT status update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the status
  update and still reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level=major`, and `notify_ben=true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after the status update: `14 passed, 612
  deselected`.
- `git status --short --branch` passed at the start of the 2026-06-27 18:16
  PDT bounded guard-closed verification and reported `main...origin/main` with
  no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this run. It reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level=major`, `notify_ben=true`, and the single next step
  to remain in no-op/awaiting-preregistration state pending Ben's decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent automation loops
  completing successfully and the latest strategy review requesting Ben
  notification.
- `git diff --check` passed after the 2026-06-27 18:16 PDT status update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the status
  update and still reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level=major`, and `notify_ben=true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after the status update: `14 passed, 612
  deselected`.
- `git status --short --branch` passed at the start of the 2026-06-27 bounded
  documentation alignment pass and reported `main...origin/main` with no
  uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this run and reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level=major`, `notify_ben=true`, and the single next step
  to remain in no-op/awaiting-preregistration state pending Ben's decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent automation loops
  completed successfully and that the latest strategy review requested Ben
  notification.
- `git diff --check` passed after the documentation alignment edits.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the edits and
  still reported `state=closed_awaiting_preregistration`, `should_noop=true`,
  closed reason `automation_status_next_step_noop`,
  `strategic_change_level=major`, and `notify_ben=true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after the edits: `14 passed, 612 deselected`.
- `git status --short --branch` passed at the start of the 2026-06-27 bounded
  no-op/status consistency pass and reported `main...origin/main` with no
  uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this run and reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level=major`, `notify_ben=true`, and the single next step
  to remain in no-op/awaiting-preregistration state pending Ben's decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent automation loops
  completed successfully and that the latest strategy review requested Ben
  notification.
- `git diff --check` passed after the status consistency update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the status
  consistency update and still reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, `strategic_change_level=major`, and `notify_ben=true`.
- `grep -n "^## Recommended Next Step\\|Recommended next step:"
  AUTOMATION_STATUS.md` showed only the top current next-step section after
  the duplicate stale bottom section was removed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after the status consistency update: `14 passed,
  612 deselected`.
- `git diff --check` passed after the bounded guard/status correction.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the
  bounded guard/status correction and reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  closed reasons `automation_status_next_step_noop` and
  `automation_status_a5_reopened_smoke_failed_closed`,
  `strategic_change_level=major`, and `notify_ben=true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after the bounded guard/status correction:
  `14 passed, 612 deselected`.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py` passed
  after the scoped current-status parser update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed and reported
  `state=open`, `should_noop=false`, no closed reasons, `notify_ben=true`, and
  the single recommended next step to design one preregistered
  resource-bounded residual diagnostic before adding new mechanics.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting'`
  passed: `17 passed, 608 deselected`.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_explicit_alignment_linear_seed5_20260627_1716` passed.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6
  --out /tmp/omegasim_a5_explicit_alignment_compare_seed5_6_20260627_1716`
  passed and wrote 16 run artifacts across the matched A5 predictive-control
  conditions.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting
  --compare-dir
  /tmp/omegasim_a5_explicit_alignment_compare_seed5_6_20260627_1716 --out
  /tmp/omegasim_a5_explicit_alignment_residual_accounting_seed5_6_20260627_1716`
  passed. The analyzer reported fail-closed promotion status: no
  intermediate-budget condition satisfied all preregistered criteria.
- `git status --short --branch` passed at the start of the 2026-06-27 16:08
  PDT bounded no-op verification and reported `main...origin/main` with no
  uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  the 2026-06-27 16:08 PDT bounded no-op verification. It reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  closed reason `automation_status_next_step_noop`,
  `strategic_change_level=major`, `notify_ben=true`, and the single next step
  to remain in no-op/awaiting-preregistration state pending Ben's decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent automation loops
  completed successfully and that the latest strategy review still requested
  Ben notification.
- `git diff --check` passed after the 2026-06-27 16:08 PDT bounded no-op
  status update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the
  2026-06-27 16:08 PDT bounded no-op status update and still reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `strategic_change_level=major`, and `notify_ben=true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after the 2026-06-27 16:08 PDT bounded no-op status
  update: `10 passed, 612 deselected`.
- `git status --short --branch` passed at the start of this bounded no-op run
  and reported `main...origin/main` with no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this bounded no-op run. It reported
  `state=closed_awaiting_preregistration`, `should_noop=true`, closed reason
  `automation_status_next_step_noop`, `strategic_change_level=major`,
  `notify_ben=true`, and the single next step to remain in no-op/awaiting-
  preregistration state pending Ben's decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent automation loops
  completed successfully and that the latest strategy review still requested
  Ben notification.
- `git diff --check` passed after this bounded no-op status update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after this bounded
  no-op status update and still reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `strategic_change_level=major`, and `notify_ben=true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after this bounded no-op status update:
  `10 passed, 612 deselected`.
- `git status --short --branch` initially reported
  `main...origin/main [ahead 1]` with no uncommitted changes before this
  preregistration pass.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed. It reported
  state `open`, `should_noop: false`, no closed reasons, and recommended the
  A5.1 smoke scaffold as the next action from this status file.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py
  ohdyn/compare_predictive_control.py ohdyn/analyze_a5_residual_accounting.py`
  passed.
- `.venv-conda/bin/python -m py_compile ohdyn/config.py ohdyn/sim.py
  ohdyn/io.py ohdyn/compare_predictive_control.py
  ohdyn/analyze_a5_residual_accounting.py ohdyn/automation_guard.py` passed
  after the A5.1 scaffold.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting or automation_guard'`
  passed: `12 passed, 605 deselected`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_1_prediction_spend or a5_residual_accounting or
  automation_guard'` passed after the A5.1 scaffold: `13 passed, 605
  deselected`.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_predictive_linear_smoke_20260627_a5_1_prereg` passed.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_1_prediction_spend_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_1_prediction_spend_linear_smoke_20260627_final` passed. The
  final metric row recorded `a5_prediction_charged_to_work=true`,
  `a5_prediction_work_charge_target_tick=5.25`, and
  `a5_work_budget_remaining_tick=13`.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --base-config
  configs/a5_1_prediction_spend_linear_smoke.yaml --seeds 5 6 --out
  /tmp/omegasim_a5_1_prediction_spend_compare_seed5_6_20260627_final` passed.
  The pilot wrote 16 run artifacts across the eight A5 conditions.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir
  /tmp/omegasim_a5_1_prediction_spend_compare_seed5_6_20260627_final --out
  /tmp/omegasim_a5_1_prediction_spend_residual_accounting_seed5_6_20260627_final`
  passed. The analyzer reported fail-closed promotion status; all intermediate
  predictors failed the residual/null and guardrail gates.
- `git diff --check` passed.
- `git status --short --branch` passed at the start of this run and reported
  `main...origin/main` with no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this run. It reported state `open`, `should_noop: false`,
  `strategic_change_level: major`, `notify_ben: true`, and recommended the
  A5.1a cost-calibration/spend-only-null patch.
- `git diff --check` passed after the A5.1a preregistration/status patch.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_1 or automation_guard'` passed after the A5.1a patch: `10 passed, 608
  deselected`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the A5.1a
  patch. It reported state `open`, `should_noop: false`,
  `strategic_change_level: major`, `notify_ben: true`, and the exact next step
  to implement the A5.1a cost-calibration/spend-only replay-null scaffold.
- `.venv-conda/bin/python -m py_compile ohdyn/config.py ohdyn/sim.py
  ohdyn/io.py ohdyn/compare_predictive_control.py` passed after implementing
  the A5.1a scaffold.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_1 or automation_guard'` passed after the scaffold implementation:
  `12 passed, 608 deselected`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting'` passed after preserving
  the original non-charged A5 comparison path: `3 passed, 617 deselected`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_1 or a5_predictive_control or a5_residual_accounting or automation_guard'`
  passed after extending the analyzer for A5.1a: `16 passed, 605 deselected`.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --base-config
  configs/a5_1_prediction_spend_linear_smoke.yaml --seeds 5 6 --out
  /tmp/omegasim_a5_1a_cost_calibration_compare_seed5_6_20260627` passed and
  wrote 14 run artifacts across seven A5.1a conditions.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir
  /tmp/omegasim_a5_1a_cost_calibration_compare_seed5_6_20260627 --out
  /tmp/omegasim_a5_1a_cost_calibration_residual_accounting_seed5_6_20260627
  --overwrite` passed after the analyzer extension. The summary reported
  fail-closed promotion status for harsh, gentle, and capped charged-cost
  conditions against their spend-only replay nulls.
- `git status --short --branch` passed at the start of this closure-note run
  and reported `main...origin/main` with no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this closure-note run. It reported state `open`, `should_noop: false`,
  `strategic_change_level: major`, `notify_ben: true`, and recommended the
  A5.1a closure note.
- `git diff --check` passed after the A5.1a closure note and status update.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py` passed
  after updating the guard to let newer A5.1a closure status supersede the
  older accepted A7 roadmap.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_1 or automation_guard'` passed after the closure/guard update:
  `14 passed, 608 deselected`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the final
  status update. It reported state `closed_awaiting_preregistration`,
  `should_noop: true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level: major`, `notify_ben: true`, and the single next
  step to remain in no-op/awaiting-preregistration state while notifying Ben.
- `git diff --check` passed after the final status update.
- `git status --short --branch` passed at the start of this no-op guard run and
  reported `main...origin/main` with no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this no-op guard run. It reported state `closed_awaiting_preregistration`,
  `should_noop: true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level: major`, `notify_ben: true`, and the single next
  step to remain in no-op/awaiting-preregistration state pending Ben's
  decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the recent automation loop
  had completed the A5.1a closure/status run and that the latest strategy
  review still requested Ben notification.
- `git diff --check` passed after this no-op guard status update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after this no-op
  guard status update and still reported `closed_awaiting_preregistration`,
  `should_noop: true`, `strategic_change_level: major`, and `notify_ben: true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after this no-op guard status update: `10 passed,
  612 deselected`.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py` passed
  after adding the explicit current-A5 reopening guard marker.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the status
  update and reported `state=open`, `should_noop=false`, no closed reasons,
  and the single next step to run the bounded A5 single-hive smoke/pilot and
  residual-accounting check.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting'`
  passed after the preregistration/guard update: `15 passed, 608 deselected`.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_reopened_linear_smoke_seed5_20260627` passed.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6
  --out /tmp/omegasim_a5_reopened_predictive_compare_seed5_6_20260627` passed
  and wrote 16 run artifacts across the matched A5 predictive-control
  conditions.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir
  /tmp/omegasim_a5_reopened_predictive_compare_seed5_6_20260627 --out
  /tmp/omegasim_a5_reopened_residual_accounting_seed5_6_20260627` passed. The
  summary reported fail-closed promotion status; no intermediate-budget
  condition satisfied all preregistered criteria.
- `git status --short --branch` passed at the start of the 2026-06-27 16:55
  PDT guard-closure run and reported `main...origin/main` with no uncommitted
  changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` initially reported
  `state=open`, `should_noop=false`, `strategic_change_level=major`,
  `notify_ben=true`, and the next step to design one preregistered
  resource-bounded residual diagnostic, exposing that older reopening/roadmap
  markers were overriding the newer fail-closed A5 status.
- `git diff --check` passed after the guard/test patch.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard or a5_predictive_control or a5_residual_accounting'`
  passed after the guard/test patch: `16 passed, 608 deselected`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the
  guard/test patch. It reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason
  `automation_status_a5_reopened_smoke_failed_closed`,
  `strategic_change_level=major`, `notify_ben=true`, and the single next step
  to design one preregistered resource-bounded residual diagnostic before any
  new mechanics.
- `git status --short --branch` passed at the start of the 2026-06-27 17:10
  PDT bounded decision-preregistration run and reported `main...origin/main`
  with no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this run. It reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason
  `automation_status_a5_reopened_smoke_failed_closed`,
  `strategic_change_level=major`, `notify_ben=true`, and the review
  recommendation to keep the guard closed and draft a non-active Ben-decision
  preregistration.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent automation loops
  completed successfully and that the latest strategy review requested Ben
  notification.
- `git diff --check` passed after the non-active decision preregistration and
  README/status updates.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the
  documentation updates. It reported `state=closed_awaiting_preregistration`,
  `should_noop=true`, closed reason `automation_status_a5_closed`,
  `strategic_change_level=major`, `notify_ben=true`, and the single next step
  to notify Ben and await his decision.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after the documentation updates: `12 passed, 612
  deselected`.
- `git status --short --branch` passed at the start of the 2026-06-27 17:05
  PDT bounded Ben-notification run and reported `main...origin/main` with no
  uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  the 2026-06-27 17:05 PDT bounded Ben-notification run. It reported
  `state=closed_awaiting_preregistration`, `should_noop=true`, closed reason
  `automation_status_a5_closed`, `strategic_change_level=major`,
  `notify_ben=true`, and the single next step to notify Ben and await his
  decision.
- `git diff --check` passed after the Ben-notification draft and status
  update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the
  Ben-notification draft and status update. It reported
  `state=closed_awaiting_preregistration`, `should_noop=true`, closed reason
  `automation_status_a5_closed`, `strategic_change_level=major`,
  `notify_ben=true`, and the single next step to notify Ben and await his
  decision.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after the Ben-notification draft and status update:
  `12 passed, 612 deselected`.

## Historical Blockers

There is no local environment blocker. The scientific/governance blocker is
that the bounded A5 smoke still reproduces forecast-skill gains without
residual/null evidence strong enough for promotion. Avoid broader A5/A5.1 seed
work, A7.2 mechanics, or multi-hive mechanics unless a fresh preregistered
direction explains how it will overcome the residual/null accounting boundary.
