# A2 queue-blind lobe analysis

- source: runs/a2_service_capacity_holdout_seed70_99_20260624
- grid rows: 9
- label inputs: tasks_worked_tick, tasks_created_tick, messages_sent_tick, idle_tick
- excluded inputs: queue_depth, queue_delta_tick, baseline_lobe_label

## Grid queue-blind lobe metrics

- normal_pressure / low_service: transition_entropy=2.07857, normalized_entropy=0.966331, dwell_length_max_mean=3.766667, task_generation_share=0.263889, execution_share=0.111111, dominant_lobes=coordination:25|low_activity:1|task_generation:4
- normal_pressure / baseline_service: transition_entropy=2.35307, normalized_entropy=0.962738, dwell_length_max_mean=2.8, task_generation_share=0.194444, execution_share=0.280555, dominant_lobes=coordination:19|execution:7|low_activity:1|task_generation:3
- normal_pressure / high_service: transition_entropy=2.155133, normalized_entropy=0.954138, dwell_length_max_mean=3.333333, task_generation_share=0.138889, execution_share=0.427778, dominant_lobes=coordination:12|execution:18
- high_pressure / low_service: transition_entropy=1.75908, normalized_entropy=0.974918, dwell_length_max_mean=4.466667, task_generation_share=0.627778, execution_share=0.072222, dominant_lobes=coordination:2|task_generation:28
- high_pressure / baseline_service: transition_entropy=2.019343, normalized_entropy=0.955632, dwell_length_max_mean=3.7, task_generation_share=0.580556, execution_share=0.175, dominant_lobes=execution:1|task_generation:29
- high_pressure / high_service: transition_entropy=2.190675, normalized_entropy=0.959011, dwell_length_max_mean=3.033333, task_generation_share=0.45, execution_share=0.308333, dominant_lobes=coordination:1|execution:8|task_generation:21
- extreme_pressure / low_service: transition_entropy=1.521787, normalized_entropy=0.916872, dwell_length_max_mean=5.866667, task_generation_share=0.736111, execution_share=0.061111, dominant_lobes=task_generation:30
- extreme_pressure / baseline_service: transition_entropy=1.846563, normalized_entropy=0.916526, dwell_length_max_mean=4.866667, task_generation_share=0.686111, execution_share=0.133333, dominant_lobes=task_generation:30
- extreme_pressure / high_service: transition_entropy=1.9789, normalized_entropy=0.968307, dwell_length_max_mean=4.1, task_generation_share=0.611111, execution_share=0.213889, dominant_lobes=coordination:1|task_generation:29

## Fixed-pressure service-capacity queue-blind effects

- normal_pressure: transition_entropy_delta=0.076563, dwell_length_max_delta=-0.433334, task_generation_share_delta=-0.125, execution_share_delta=0.316667
- high_pressure: transition_entropy_delta=0.431595, dwell_length_max_delta=-1.433334, task_generation_share_delta=-0.177778, execution_share_delta=0.236111
- extreme_pressure: transition_entropy_delta=0.457113, dwell_length_max_delta=-1.766667, task_generation_share_delta=-0.125, execution_share_delta=0.152778

## Fixed-service pressure queue-blind effects

- low_service: transition_entropy_delta=-0.556783, dwell_length_max_delta=2.1, task_generation_share_delta=0.472222, execution_share_delta=-0.05
- baseline_service: transition_entropy_delta=-0.506507, dwell_length_max_delta=2.066667, task_generation_share_delta=0.491667, execution_share_delta=-0.147222
- high_service: transition_entropy_delta=-0.176233, dwell_length_max_delta=0.766667, task_generation_share_delta=0.472222, execution_share_delta=-0.213889

## Interpretation

- Strongest fixed-service pressure shift in queue-blind generation share: baseline_service task_generation_share_delta=0.491667.
- Strongest fixed-service pressure shift in queue-blind entropy: low_service transition_entropy_delta=-0.556783.
- Strongest fixed-pressure service shift in execution share: normal_pressure execution_share_delta=0.316667.
- Use this as a robustness check only: it tests whether pressure structure remains visible after removing queue-derived label rules.
