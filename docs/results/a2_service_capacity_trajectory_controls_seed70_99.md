# A2 service-capacity trajectory analysis

- source: runs/a2_service_capacity_holdout_seed70_99_20260624
- grid rows: 9

## Grid trajectory metrics

- normal_pressure / low_service: queue_per_created=0.665997, queued_age_final=4.002693, transition_entropy=1.769076, normalized_entropy=0.966843, dwell_length_mean=2.043968, dwell_length_max_mean=4.4, backlog_growth_dwell_share=0.680556, dominant_lobes=backlog_growth:28|coordination:2
- normal_pressure / baseline_service: queue_per_created=0.50777, queued_age_final=3.338109, transition_entropy=2.141011, normalized_entropy=0.961042, dwell_length_mean=1.603059, dwell_length_max_mean=3.233333, backlog_growth_dwell_share=0.513889, dominant_lobes=backlog_growth:25|execution:5
- normal_pressure / high_service: queue_per_created=0.350852, queued_age_final=2.400855, transition_entropy=2.106739, normalized_entropy=0.950608, dwell_length_mean=1.464488, dwell_length_max_mean=2.866667, backlog_growth_dwell_share=0.358333, dominant_lobes=backlog_growth:9|coordination:4|execution:17
- high_pressure / low_service: queue_per_created=0.823851, queued_age_final=4.658975, transition_entropy=0.895393, normalized_entropy=0.627922, dwell_length_mean=5.831429, dwell_length_max_mean=8.233333, backlog_growth_dwell_share=0.891667, dominant_lobes=backlog_growth:30
- high_pressure / baseline_service: queue_per_created=0.752801, queued_age_final=4.280544, transition_entropy=1.340621, normalized_entropy=0.914135, dwell_length_mean=2.83381, dwell_length_max_mean=6.066667, backlog_growth_dwell_share=0.802778, dominant_lobes=backlog_growth:30
- high_pressure / high_service: queue_per_created=0.655784, queued_age_final=3.897979, transition_entropy=1.561217, normalized_entropy=0.966551, dwell_length_mean=2.11381, dwell_length_max_mean=4.3, backlog_growth_dwell_share=0.677778, dominant_lobes=backlog_growth:30
- extreme_pressure / low_service: queue_per_created=0.871407, queued_age_final=4.771899, transition_entropy=0.602941, normalized_entropy=0.53061, dwell_length_mean=7.273333, dwell_length_max_mean=9.7, backlog_growth_dwell_share=0.936111, dominant_lobes=backlog_growth:30
- extreme_pressure / baseline_service: queue_per_created=0.806282, queued_age_final=4.503385, transition_entropy=0.848225, normalized_entropy=0.725199, dwell_length_mean=5.378095, dwell_length_max_mean=8.5, backlog_growth_dwell_share=0.888889, dominant_lobes=backlog_growth:30
- extreme_pressure / high_service: queue_per_created=0.720144, queued_age_final=4.138014, transition_entropy=1.403745, normalized_entropy=0.880108, dwell_length_mean=3.070159, dwell_length_max_mean=5.866667, backlog_growth_dwell_share=0.786111, dominant_lobes=backlog_growth:30

## Fixed-pressure service-capacity trajectory effects

- normal_pressure: queue_per_created_delta=-0.315145, transition_entropy_delta=0.337663, dwell_length_max_delta=-1.533333, backlog_growth_dwell_share_delta=-0.322223
- high_pressure: queue_per_created_delta=-0.168067, transition_entropy_delta=0.665824, dwell_length_max_delta=-3.933333, backlog_growth_dwell_share_delta=-0.213889
- extreme_pressure: queue_per_created_delta=-0.151263, transition_entropy_delta=0.800804, dwell_length_max_delta=-3.833333, backlog_growth_dwell_share_delta=-0.15

## Fixed-service demand-pressure trajectory effects

- low_service: queue_per_created_delta=0.20541, transition_entropy_delta=-1.166135, dwell_length_max_delta=5.3, backlog_growth_dwell_share_delta=0.255555
- baseline_service: queue_per_created_delta=0.298512, transition_entropy_delta=-1.292786, dwell_length_max_delta=5.266667, backlog_growth_dwell_share_delta=0.375
- high_service: queue_per_created_delta=0.369292, transition_entropy_delta=-0.702994, dwell_length_max_delta=3, backlog_growth_dwell_share_delta=0.427778

## Paired bootstrap uncertainty

- paired seed bootstrap rows: 30; sign-stable rows at >=0.95: 29
- service_capacity / normal_pressure / transition_entropy: delta=0.337663, ci=[0.135608, 0.551771], sign_stability=1
- service_capacity / normal_pressure / dwell_length_max: delta=-1.533333, ci=[-2.2, -0.833333], sign_stability=1
- service_capacity / high_pressure / transition_entropy: delta=0.665825, ci=[0.393827, 0.92576], sign_stability=1
- service_capacity / high_pressure / dwell_length_max: delta=-3.933333, ci=[-5.233333, -2.7], sign_stability=1
- service_capacity / extreme_pressure / transition_entropy: delta=0.800804, ci=[0.55598, 1.066953], sign_stability=1
- service_capacity / extreme_pressure / dwell_length_max: delta=-3.833333, ci=[-4.733333, -2.866667], sign_stability=1
- task_creation_pressure / low_service / transition_entropy: delta=-1.166135, ci=[-1.395874, -0.93273], sign_stability=1
- task_creation_pressure / low_service / dwell_length_max: delta=5.3, ci=[4.433333, 6.233333], sign_stability=1
- task_creation_pressure / baseline_service / transition_entropy: delta=-1.292787, ci=[-1.54357, -1.035164], sign_stability=1
- task_creation_pressure / baseline_service / dwell_length_max: delta=5.266667, ci=[4.366667, 6.2], sign_stability=1
- task_creation_pressure / high_service / transition_entropy: delta=-0.702994, ci=[-0.929284, -0.470688], sign_stability=1
- task_creation_pressure / high_service / dwell_length_max: delta=3, ci=[1.866667, 4.133333], sign_stability=1

## Label-count null control

- normal_pressure / low_service: transition_entropy_observed_minus_null=0.014704, normalized_entropy_observed_minus_null=0.003633, dwell_length_max_observed_minus_null=-0.220867
- normal_pressure / baseline_service: transition_entropy_observed_minus_null=0.028283, normalized_entropy_observed_minus_null=0.000276, dwell_length_max_observed_minus_null=-0.0152
- normal_pressure / high_service: transition_entropy_observed_minus_null=-0.007706, normalized_entropy_observed_minus_null=-0.012099, dwell_length_max_observed_minus_null=0.046534
- high_pressure / low_service: transition_entropy_observed_minus_null=0.004408, normalized_entropy_observed_minus_null=-0.017622, dwell_length_max_observed_minus_null=-0.214667
- high_pressure / baseline_service: transition_entropy_observed_minus_null=0.013364, normalized_entropy_observed_minus_null=-0.012704, dwell_length_max_observed_minus_null=-0.245866
- high_pressure / high_service: transition_entropy_observed_minus_null=0.02712, normalized_entropy_observed_minus_null=0.019241, dwell_length_max_observed_minus_null=-0.287667
- extreme_pressure / low_service: transition_entropy_observed_minus_null=0.022687, normalized_entropy_observed_minus_null=0.030272, dwell_length_max_observed_minus_null=0.098
- extreme_pressure / baseline_service: transition_entropy_observed_minus_null=0.030354, normalized_entropy_observed_minus_null=0.03542, dwell_length_max_observed_minus_null=0.203
- extreme_pressure / high_service: transition_entropy_observed_minus_null=-0.00389, normalized_entropy_observed_minus_null=-0.022684, dwell_length_max_observed_minus_null=-0.3154

## Interpretation

- Strongest fixed-service pressure locking by backlog dwell share: high_service backlog_growth_dwell_share_delta=0.427778.
- Strongest fixed-pressure service-capacity entropy gain: extreme_pressure transition_entropy_delta=0.800804.
- Compare these trajectory deltas with queue_per_created deltas before treating raw queue depth as an emergent lobe-dynamics result.
- Strongest observed-minus-null dwell locking: extreme_pressure / baseline_service dwell_length_max_observed_minus_null=0.203.
