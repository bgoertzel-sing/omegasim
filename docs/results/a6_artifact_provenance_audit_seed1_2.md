# A6 Artifact Provenance Audit, Seeds 1-2

Run date: 2026-06-27.

This note records a bounded read-only artifact-update provenance audit over the
existing seed `1..2` A6 smoke comparison artifacts. It is an alias-risk audit,
not promotion evidence.

## Inputs

```bash
.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal \
  --compare-dir runs/a6_logistic_appraisal_compare \
  --out runs/a6_artifact_provenance_audit
```

The analyzer consumed existing artifacts only. No simulations were rerun.

## Generated Audit Artifact

The ignored analysis directory now includes:

```text
runs/a6_artifact_provenance_audit/a6_logistic_appraisal_artifact_provenance.csv
```

Row counts, excluding header rows:

```text
artifact_provenance: 80
endpoints: 8
manifest: 7
control_deltas: 6
control_summary: 42
residual_preflight: 112
residual_timeseries: 1792
residual_contrast_summary: 84
residual_contrast_rollup: 42
comparison_consistency: 4
effects_consistency: 3
```

## Alias-Risk Summary

Across all four smoke conditions and both seeds:

```text
high_action_alias_risk: 57
no_change: 15
mixed_or_low_alias_risk_smoke: 6
action_coupled_smoke: 2
```

Logistic condition rows for the fields most relevant to prior A6 interpretation:

```text
seed  field                       total_abs_delta  dominant_event   event_share  dominant_action  action_share  alias_risk
1     artifact_readiness          0.332805         handoff_success  1.0          handoff          0.462222      high_action_alias_risk
1     artifact_utility            0.576679         handoff_success  1.0          handoff          0.462222      high_action_alias_risk
2     artifact_readiness          0.181760         handoff_success  1.0          handoff          0.506667      high_action_alias_risk
2     artifact_utility            0.379809         handoff_success  1.0          handoff          0.506667      high_action_alias_risk
```

The same-tick event attribution is overlapping rather than causal: a tick may
contain artifact-update, handoff-attempt, handoff-success, and other A6 events.
The result is therefore a conservative warning that the current utility and
readiness fields are too tightly coupled to handoff/action provenance for
promotion claims from the seed `1..2` smoke packet.

## Interpretation

The audit strengthens the previous A6 gate conclusion. A6 remains
smoke/analyzer-only. The existing artifact utility and readiness signals should
be treated as action-count/handoff-coupled until a future preregistered A6.1
design separates ambient artifact drift, handoff success/failure effects,
prediction expenditure, and queue/work accounting.

Do not broaden A6 seeds or claim attractor, lobe grammar, synchrony, recurrence,
or causal nonlinear collective structure from these artifacts.
