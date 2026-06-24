# A2 Scheduler Mechanism Ablation Preregistration

This preregisters the first scheduler-mechanism ablation after freezing the
69-seed A2 extreme-pressure baseline. The ablation tests whether the current
quota-balancing task selector, rather than task-creation pressure or attention
shares alone, contributes to the frozen pressure-response findings.

## Conditions

Use the baseline attention shares in both scheduler conditions:

- `quota_balance`: existing soft quota selector, using
  `configs/a2_attention_smoke.yaml`,
  `configs/a2_attention_high_pressure.yaml`, and
  `configs/a2_attention_extreme_pressure.yaml`.
- `random_available`: seeded random queued-task selector, using
  `configs/a2_attention_random_available.yaml`,
  `configs/a2_attention_random_available_high_pressure.yaml`, and
  `configs/a2_attention_random_available_extreme_pressure.yaml`.

Pressure points remain `1.0`, `1.8`, and `2.2` so the ablation is comparable to
the frozen extreme-pressure setup.

## Primary Outcomes

- final and mean queue depth;
- queued-task mean and max age;
- value per completed task;
- value per work event;
- class-specific capture pressure;
- lobe transition and dwell summaries.

## Interpretation Rule

Treat queue-depth differences as scheduler pressure sensitivity, not policy
success. Treat value-yield and capture-pressure differences as secondary unless
they are stable under seed-level uncertainty checks.
