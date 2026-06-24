# A2 Extreme-Pressure Baseline, Seeds 1-69

This freezes the current A2 extreme-pressure result as a compact checked-in
baseline. The ignored source artifacts were generated under:

- `runs/a2_attention_extreme_pressure_compare_seed1_69_20260624T_run/`
- `runs/a2_attention_extreme_pressure_analysis_seed1_69_20260624T_run/`

The comparison used normal pressure `1.0`, high-pressure fixtures as the medium
endpoint `1.8`, and extreme-pressure fixtures as the high endpoint `2.2`, across
seeds `1` through `69`.

## Primary Reading

The robust baseline-level finding is pressure-amplified queue depth. The full
seed set's top global response is `internal_improvement` final queue depth under
the normal-to-medium pressure interval:

- condition means: `19.681159 -> 45.956522 -> 56.057971`
- normal-to-medium slope: `32.844204`
- medium-to-high slope: `25.253622`
- curvature: `-7.590582`
- high-minus-normal delta: `36.376812`

This should be interpreted as pressure sensitivity, not as evidence that
`internal_improvement` is a better operational policy. Task creation pressure is
part of the simulator mechanism, so queue depth remains a necessary baseline
observable rather than a sufficient emergent-dynamics result.

## Secondary Signals

The strongest class-specific capture-pressure response is baseline peak
`long_term_research` capture pressure:

- condition means: `0.282358 -> 0.158838 -> 0.133015`
- normal-to-medium slope: `-0.154400`
- medium-to-high slope: `-0.064558`
- curvature: `0.089842`
- high-minus-normal delta: `-0.149343`

The last ordered prefix matched this class-specific winner, but all-prefix
stability is not claimed.

The top value-yield divergence remains secondary and unstable. The selected
full-seed row is `research_heavy` medium-to-high slope, with completion-normalized
yield changing by `-0.003015` and effort-normalized yield changing by `-0.125100`.
Both yield normalizations degrade, so this is a same-direction divergence, not a
reliable completion-vs-effort tradeoff.

## Stability Notes

- Global top-response stability starts at the ordered prefix `1-8`.
- Class-specific capture-pressure stability starts at the ordered prefix `1-15`.
- The last proper prefix, seeds `1-68`, matched both the global and class-specific
  full-seed selections.
- Ordered-prefix stability is not uncertainty estimation. The next analysis
  should use bootstrap or shuffled-prefix rank stability before drawing stronger
  claims from top-response rankings.

## Compact CSV

`docs/results/a2_pressure_seed1_69_top_responses.csv` records the global,
class-specific, and value-yield rows needed for lightweight review without
parsing the ignored run artifacts.
