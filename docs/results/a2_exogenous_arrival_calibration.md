# A2 exogenous-arrival calibration

- seeds: 1, 2, 3
- candidate rates: 0, 0.5, 1, 1.5, 2, 2.5, 3
- control config: configs/a2_attention_smoke.yaml
- high-pressure target config: configs/a2_attention_high_pressure.yaml
- extreme-pressure target config: configs/a2_attention_extreme_pressure.yaml
- calibration criterion: total created-task mean only; no lobe, entropy, or value outcomes are used for rate selection

## Coupled-pressure targets

- endogenous_control: created_mean=40
- low_exogenous_target: created_mean=50
- high_pressure_target: created_mean=60
- extreme_pressure_target: created_mean=73.666667

## Candidate accounting

- endogenous_control_rate0: rate=0, target=endogenous_control, target_error=0, agent_created_mean=40, exogenous_created_mean=0, total_created_mean=40, completed_mean=18.666667, work_events_mean=44.666667, final_queue_mean=21.333333, queue_per_created=0.51428
- exogenous_rate_0p5: rate=0.5, target=endogenous_control, target_error=5, agent_created_mean=40, exogenous_created_mean=5, total_created_mean=45, completed_mean=18.333333, work_events_mean=44.666667, final_queue_mean=26.666667, queue_per_created=0.578565
- exogenous_rate_1p0: rate=1, target=low_exogenous_target, target_error=0.666667, agent_created_mean=39.666667, exogenous_created_mean=9.666667, total_created_mean=49.333333, completed_mean=18.666667, work_events_mean=45.666667, final_queue_mean=30.666667, queue_per_created=0.608493
- exogenous_rate_1p5: rate=1.5, target=high_pressure_target, target_error=3.666667, agent_created_mean=39.333333, exogenous_created_mean=17, total_created_mean=56.333333, completed_mean=18.666667, work_events_mean=46, final_queue_mean=37.666667, queue_per_created=0.651424
- exogenous_rate_2p0: rate=2, target=high_pressure_target, target_error=0.333333, agent_created_mean=39.333333, exogenous_created_mean=20.333333, total_created_mean=59.666667, completed_mean=19, work_events_mean=46, final_queue_mean=40.666667, queue_per_created=0.66825
- exogenous_rate_2p5: rate=2.5, target=high_pressure_target, target_error=1, agent_created_mean=39.333333, exogenous_created_mean=21.666667, total_created_mean=61, completed_mean=19.333333, work_events_mean=46, final_queue_mean=41.666667, queue_per_created=0.67252
- exogenous_rate_3p0: rate=3, target=extreme_pressure_target, target_error=1, agent_created_mean=39.333333, exogenous_created_mean=35.333333, total_created_mean=74.666667, completed_mean=19.333333, work_events_mean=46, final_queue_mean=55.333333, queue_per_created=0.736253

## Provisional frozen rates

- low_exogenous_target: rate_per_tick=1, created_mean=49.333333, target_error=0.666667
- high_pressure_target: rate_per_tick=2, created_mean=59.666667, target_error=0.333333
- extreme_pressure_target: rate_per_tick=3, created_mean=74.666667, target_error=1

## Interpretation

- These rates are calibration fixtures for the next exogenous-arrival holdout; they do not by themselves test lobe dynamics.
- Candidate selection used load/accounting targets only, following the preregistered decoupling plan.
