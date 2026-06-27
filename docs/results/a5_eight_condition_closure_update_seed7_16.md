# A5 Eight-Condition Closure Update, Seeds 7..16

This update supersedes the older six-condition closure note in
`docs/results/a5_closure_note_seed7_16.md` for A5 interpretation. The older
note remains valid for its original six-condition artifact set, but the current
closed A5 evidence is the eight-condition confirmatory result in
`docs/results/a5_eight_condition_confirmatory_seed7_16.md`.

No simulations were rerun for this update. No simulator mechanics, multi-hive
coupling, lobe labels, dashboards, real LLM calls, Lean, Slack, browser
automation, Atomspace integration, or external services were added.

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: none`
- `notify_ben: false`
- Deferred: the review recommended proceeding to an A7 implementation gate.
  That recommendation is scientifically sensible, but this bounded run followed
  `AUTOMATION_STATUS.md` as the source of truth and first closed Ben's newer
  explicit A5 reopening with the requested eight-condition closure update.

## Supersession

The six-condition closure note is superseded in three places:

- the confirmatory scope is now eight matched A5 conditions, not six;
- `nonlinear_high_budget` and its budget-matched timing-broken null,
  `nonlinear_high_budget_shuffled`, are included in the closure decision;
- analyzer totals are now `6400` residual-accounting metric rows and `720`
  effect rows, not the older six-condition `4800` and `480` totals.

## Evidence Boundary

The eight-condition comparison ran 80 deterministic simulations across seeds
`7..16`:

- `reactive`
- `linear`
- `nonlinear`
- `nonlinear_high_budget`
- `oracle`
- `shuffled`
- `nonlinear_shuffled`
- `nonlinear_high_budget_shuffled`

Final task creation remained matched at `74.2` mean tasks for every condition.
Forecast skill improved for all predictive conditions versus their required
comparators:

| contrast | forecast-skill delta |
| --- | ---: |
| linear minus reactive | 0.033517 |
| nonlinear minus reactive | 0.084033 |
| nonlinear_high_budget minus reactive | 0.094796 |
| linear minus shuffled | 0.045425 |
| nonlinear minus nonlinear_shuffled | 0.095941 |
| nonlinear_high_budget minus nonlinear_high_budget_shuffled | 0.106704 |

The full-accounting residual-state predictability contrasts did not satisfy
the preregistered promotion rule:

| contrast | mean delta | positive delta rate | interpretation |
| --- | ---: | ---: | --- |
| linear minus reactive | 0.114949 | 0.5 | inside paired label-permutation interval |
| nonlinear minus reactive | 0.077593 | 0.7 | inside paired label-permutation interval |
| nonlinear_high_budget minus reactive | 0.162115 | 0.6 | inside paired label-permutation interval |
| linear minus shuffled | -0.053977 | 0.5 | inside paired label-permutation interval |
| nonlinear minus nonlinear_shuffled | -0.091333 | 0.3 | inside paired label-permutation interval |
| nonlinear_high_budget minus nonlinear_high_budget_shuffled | -0.006811 | 0.5 | inside paired label-permutation interval |

## Closure Decision

A5 remains closed. The high-budget nonlinear predictor improved forecast skill,
including against its own budget-matched timing-broken null, but it did not
produce promotion-worthy residual structure after full accounting controls and
did not change the conservative interpretation.

The defensible A5 claim is narrow: deterministic resource-bounded predictors
can improve forecast skill under matched single-hive demand streams. The
current A5 evidence does not support residual lobe grammar,
strange-attractor-like collective dynamics, downstream multi-hive coupling, or
new simulator mechanics.

## Reopening Rule

Do not reopen A5 from this result alone. Any future A5 mechanics, broader seed
runs, richer lobe labels, or anticipatory multi-hive coupling require a new
preregistration before implementation.
