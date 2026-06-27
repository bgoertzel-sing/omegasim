# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

A6/A6.1 remain conservatively closed as evidence, and A6.2 is now the active
residual-recurrence route from the accepted provisional roadmap. The seed `1..2`
A6.2 analyzer gate has already passed schema/source-field completeness and
failed closed as `insufficient_horizon`; the current bounded focus is the
preregistered longer-horizon validation design, not a simulation run.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Do not broaden seeds, add new A6 mechanisms, or
promote attractor/lobe-like claims from the seed `1..2` smoke artifacts.

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: minor`
- `notify_ben: false`
- Accepted: publish the actual A6 analyzer gate status before new simulations
  or mechanisms.
- Applied to the current roadmap by adding the A6.2 read-only gate report.
- Accepted extension: preregister a narrow longer-horizon A6.2 validation before
  any longer-horizon run.
- Rejected/deferred: no scientifically sensible GPT-5.5-Pro recommendation was
  rejected.

## Latest Changes

- Added `docs/a6_2_long_horizon_validation_preregistration.md`.
- Documented the new A6.2 longer-horizon design gate in `README.md`.
- The preregistration freezes a 96-tick, paired seed `1..2`, single-hive
  validation with the existing A6 mechanics and the same source-preserving null
  controls.
- No simulations were run, no configs were added, no mechanisms were changed,
  and no broader seed or multi-hive work was started.

## Verification

- Documentation-only change; no simulator or analyzer code changed.
- `git diff --check` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed: `7 passed, 595 deselected`.

## Blockers

None for the bounded design gate. Scientifically, A6.2 remains unpromoted; the
existing 16-tick smoke artifacts are too short for residual-recurrence
interpretation, and the longer-horizon validation is preregistered only as an
eligibility/closure test.

## Recommended Next Step

Create the fixed 96-tick A6.2 validation configs and the smallest comparison
helper needed to regenerate the six required paired conditions, then run only
seeds `1` and `2` and analyze them with the existing read-only A6.2 analyzer.
