# A2 exogenous-arrival comparison scaffold

- seeds: 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99
- conditions: 4
- task_creation_pressure: fixed at 1.0
- scheduler: quota_balance
- attention and exogenous task-class shares: baseline

## Load and action accounting

- endogenous_control: rate=0, agent_created_mean=41.433333, exogenous_created_mean=0, total_created_mean=41.433333, completed_mean=19.933333, work_events_mean=45.966667, queue_per_created=0.50777
- exogenous_low: rate=1, agent_created_mean=40.966667, exogenous_created_mean=11.666667, total_created_mean=52.633333, completed_mean=20.633333, work_events_mean=46.8, queue_per_created=0.60027
- exogenous_medium: rate=2, agent_created_mean=40.5, exogenous_created_mean=23.266667, total_created_mean=63.766667, completed_mean=19.833333, work_events_mean=47.466667, queue_per_created=0.682632
- exogenous_high: rate=3, agent_created_mean=40.166667, exogenous_created_mean=38.1, total_created_mean=78.266667, completed_mean=19.333333, work_events_mean=47.833333, queue_per_created=0.749526

## Trajectory summaries

- endogenous_control: baseline_entropy=2.141011, baseline_backlog_share=0.513889, queue_blind_entropy=2.35307, queue_blind_task_generation_share=0.194444, queue_blind_execution_share=0.280555
- exogenous_low: baseline_entropy=2.151228, baseline_backlog_share=0.516667, queue_blind_entropy=2.349544, queue_blind_task_generation_share=0.194444, queue_blind_execution_share=0.297222
- exogenous_medium: baseline_entropy=2.1187, baseline_backlog_share=0.513889, queue_blind_entropy=2.303605, queue_blind_task_generation_share=0.191667, queue_blind_execution_share=0.325
- exogenous_high: baseline_entropy=2.11643, baseline_backlog_share=0.513889, queue_blind_entropy=2.254402, queue_blind_task_generation_share=0.191667, queue_blind_execution_share=0.316667

## Endogenous-control deltas

- exogenous_low: created_delta=11.2, queue_per_created_delta=0.0925, baseline_entropy_delta=0.010217, queue_blind_entropy_delta=-0.003526, queue_blind_generation_share_delta=0
- exogenous_medium: created_delta=22.333334, queue_per_created_delta=0.174862, baseline_entropy_delta=-0.022311, queue_blind_entropy_delta=-0.049465, queue_blind_generation_share_delta=-0.002777
- exogenous_high: created_delta=36.833334, queue_per_created_delta=0.241756, baseline_entropy_delta=-0.024581, queue_blind_entropy_delta=-0.098668, queue_blind_generation_share_delta=-0.002777

## Interpretation guardrails

- Strongest load-normalized backlog delta: exogenous_high=0.241756.
- Strongest queue-blind entropy delta: exogenous_high=-0.098668.
- Treat this helper as the frozen-rate holdout scaffold; do not interpret small seed smoke outputs as lobe-dynamics evidence.
