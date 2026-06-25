# A2 exogenous-arrival control analysis

- source: runs/a2_exogenous_arrival_holdout_seed70_99_20260625_v2
- conditions: 4
- bootstrap: paired by seed against endogenous_control
- null control: label-count-preserving baseline-lobe shuffles
- queue-blind labels use agent_tasks_created_tick when present

## Condition Metrics

- endogenous_control: rate=0, queue_per_created=0.50777, baseline_entropy=2.141011, baseline_backlog_share=0.513889, queue_blind_entropy=2.35307, queue_blind_generation_share=0.194444
- exogenous_low: rate=1, queue_per_created=0.60027, baseline_entropy=2.151228, baseline_backlog_share=0.516667, queue_blind_entropy=2.349544, queue_blind_generation_share=0.194444
- exogenous_medium: rate=2, queue_per_created=0.682632, baseline_entropy=2.1187, baseline_backlog_share=0.513889, queue_blind_entropy=2.303605, queue_blind_generation_share=0.191667
- exogenous_high: rate=3, queue_per_created=0.749526, baseline_entropy=2.11643, baseline_backlog_share=0.513889, queue_blind_entropy=2.254402, queue_blind_generation_share=0.191667

## Bootstrap Highlights

- stable rows at >=0.95 sign stability: 5 / 24
- high exogenous load delta: 0.241756, ci=[0.209972, 0.276361], sign_stability=1
- high exogenous queue-blind entropy delta: -0.098668, ci=[-0.239733, 0.029129], sign_stability=0.885
- high exogenous queue-blind task-generation share delta: -0.002778, ci=[-0.036111, 0.030556], sign_stability=0.575

## Null Control

- endogenous_control: baseline_entropy_observed_minus_null=0.034, baseline_dwell_max_observed_minus_null=-0.010667
- exogenous_low: baseline_entropy_observed_minus_null=0.066637, baseline_dwell_max_observed_minus_null=-0.055333
- exogenous_medium: baseline_entropy_observed_minus_null=0.047202, baseline_dwell_max_observed_minus_null=0.053
- exogenous_high: baseline_entropy_observed_minus_null=0.019209, baseline_dwell_max_observed_minus_null=-0.020334

## Interpretation

- Strong sign-stable load growth without a matching sign-stable queue-blind task-generation dwell-share increase supports the load-pressure interpretation over independent lobe grammar.
- Strongest baseline observed-minus-null dwell locking: exogenous_medium dwell_length_max_observed_minus_null=0.053.
