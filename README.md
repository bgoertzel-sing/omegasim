# OmegaSim

OmegaSim is a lightweight Python simulator for OmegaHive1 and Moltbook-style multi-hive dynamics.

The first implementation is intentionally abstract and numeric. It should not call real LLMs, Lean, Slack, browsers, Atomspace, or live task boards. Early versions represent those systems as queues, graph edges, semantic fields, role policies, and events.

## Initial Mission

Explore whether OmegaHive-like agent societies display structured lobe dynamics, and whether multiple hives coupled through a Moltbook-style shared layer display useful phase-differentiated lobe grammars rather than global synchronization.

## First Milestone

Implement Phase A0/A1 from the experiment plan:

```bash
python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1
```

The first run harness should produce:

```text
config.yaml
manifest.yaml
metrics.csv
events.csv
summary.md
```

## Current A0/A1 Baseline

The baseline runner loads one YAML config, creates 15 static OmegaHive-like agents, connects them through one NetworkX bus graph, advances one in-memory task queue for the configured tick count, and writes deterministic artifacts for the supplied seed. The only supported baseline actions are `idle`, `message`, `create_task`, and `work_task`.

The 15 agents cycle through five roles, with three agents per role:

- `coordinator`
- `researcher`
- `architect`
- `implementer`
- `reviewer`

Baseline lobe labels are derived from per-tick queue movement and dominant action counts:

- `backlog_growth`
- `execution`
- `task_generation`
- `coordination`
- `low_activity`

## A2 Attention Allocation Smoke

The first opt-in A2 fixture keeps the A0/A1 agent population, bus graph, actions, and artifact contract, but adds a four-class `attention_policy` section:

```bash
python -m ohdyn.run --config configs/a2_attention_smoke.yaml --seed 1 --out runs/a2_attention_seed1
```

Attention-policy runs assign created tasks to `near_term_external`, `long_term_research`, `internal_improvement`, and `housekeeping`; work selection favors queued classes that are under their target share. `metrics.csv`, `manifest.yaml`, and `summary.md` add per-class queue, completion, queued-age, attention-share, share-deviation, and value-weighted completed-work fields only for configs that enable `attention_policy`.

Attention-policy runs also record deterministic capture-pressure telemetry. Per-class `attention_<class>_capture_pressure_tick` fields report how far each class's queued-task share exceeds its target share at the end of a tick, and `attention_capture_pressure_max_tick` reports the largest per-class pressure. When the quota-balancing scheduler works a different class while another available class is above target share, `events.csv` emits an `attention_capture_pressure` event with the selected class, pressure class, and pressure value. These fields are present only for configs that enable `attention_policy`; A0/A1 configs keep the baseline metrics shape.

A contrasting research-heavy A2 fixture uses the same deterministic baseline with more reserved share for long-term research:

```bash
python -m ohdyn.run --config configs/a2_attention_research_heavy.yaml --seed 1 --out runs/a2_attention_research_heavy_seed1
```

The focused comparison test runs `configs/a2_attention_smoke.yaml` and `configs/a2_attention_research_heavy.yaml` with the same seed and verifies that the research-heavy policy shifts completed work toward `long_term_research` while changing value-weighted throughput and stale-task age.

A contrasting internal-improvement-heavy A2 fixture reserves more share for self-analysis, policy improvement, and capability development:

```bash
python -m ohdyn.run --config configs/a2_attention_internal_improvement.yaml --seed 1 --out runs/a2_attention_internal_improvement_seed1
```

A small deterministic comparison runner executes the smoke, research-heavy, and internal-improvement-heavy A2 fixtures across a short seed set and writes per-run artifacts plus aggregate comparison outputs:

```bash
python -m ohdyn.compare_attention --seeds 1 2 3 --out runs/a2_attention_compare
```

The comparison directory contains `comparison_metrics.csv`, an aggregate `summary.md`, and one normal run artifact directory per policy/seed. The aggregate CSV uses stable run subdirectory names so same-seed comparisons are byte-reproducible across output parent directories. It records value-weighted throughput, queue depth, stale-task age, per-class completed work totals, pipe-delimited per-run trajectory columns for queue depth, queued-task mean age, value-weighted completed work, and each attention class's completed-work totals. It also records pipe-delimited first-difference columns for queue depth, queued-task mean age, and value-weighted completed work so policy summaries can report phase-space step deltas.

The aggregate comparison `summary.md` derives deterministic phase-space regime labels from the signs of each policy's mean queue-depth, queued-age, and value-throughput step deltas, for example `queue_growth+stale_age_rising+value_throughput_rising`. It also counts each per-run step-level regime label from the same delta sign sequence, reports per-policy regime counts and rates, and reports each variant policy's regime count/rate distribution deltas versus the baseline policy.

Attention comparison rows also carry capture-pressure trajectories from the A2 run metrics. `comparison_metrics.csv` records final, mean-over-ticks, peak, full max-capture-pressure trajectory, first differences, and per-class capture-pressure trajectories. The aggregate comparison `summary.md` reports per-policy capture-pressure final/mean/peak means, capture-pressure step-delta aggregates, and variant deltas versus the baseline policy.

A2 configs may also set `model.task_creation_pressure`, a deterministic scalar applied to the baseline `create_task` action weight. The default is `1.0`, preserving A0/A1 behavior. The checked-in high-pressure fixtures use `1.8` to compare the same policy shares under stronger backlog creation pressure:

The checked-in medium-pressure fixtures use `1.4` to provide a reproducible midpoint between the normal and high-pressure conditions:

```bash
python -m ohdyn.compare_attention \
  --baseline-config configs/a2_attention_medium_pressure.yaml \
  --variant-config configs/a2_attention_research_heavy_medium_pressure.yaml \
  --internal-improvement-config configs/a2_attention_internal_improvement_medium_pressure.yaml \
  --seeds 1 2 3 \
  --out runs/a2_attention_medium_pressure_compare
```

```bash
python -m ohdyn.compare_attention \
  --baseline-config configs/a2_attention_high_pressure.yaml \
  --variant-config configs/a2_attention_research_heavy_high_pressure.yaml \
  --internal-improvement-config configs/a2_attention_internal_improvement_high_pressure.yaml \
  --seeds 1 2 3 \
  --out runs/a2_attention_high_pressure_compare
```

The pressure comparison helper runs the normal, medium, and high-pressure policy sets together, preserving the per-condition comparison artifacts while adding fixed-policy high-minus-normal pressure deltas and pressure-curve slope/curvature metrics:

```bash
python -m ohdyn.compare_pressure --seeds 1 2 3 --out runs/a2_attention_pressure_compare
```

The output directory contains `normal_pressure/`, `medium_pressure/`, `high_pressure/`, `pressure_comparison_metrics.csv`, `pressure_response_selection.csv`, and a top-level `summary.md`. The three pressure-condition subdirectories are ordinary `ohdyn.compare_attention` outputs with their own `comparison_metrics.csv`, aggregate `summary.md`, and per-policy/per-seed run artifact directories.

`pressure_comparison_metrics.csv` has one row per fixed policy and records high-pressure minus normal-pressure deltas:

- `policy`, the fixed policy being compared across pressure conditions.
- `normal_total_steps`, `medium_pressure_total_steps`, and `high_pressure_total_steps`, the number of phase-space first-difference steps available for the policy in each condition.
- `regime_rate_deltas`, pipe-delimited `regime:delta` entries for high-minus-normal step-regime rates.
- `regime_count_deltas`, pipe-delimited `regime:delta` entries for high-minus-normal step-regime counts.
- `value_weighted_completed_mean_delta`, mean final value-weighted completed-work delta across seeds.
- `tasks_completed_mean_delta`, mean final completed-task delta across seeds.
- `queue_depth_mean_delta`, mean final queue-depth delta across seeds.
- `queued_task_age_mean_final_delta`, mean final queued-task mean-age delta across seeds.
- `queued_task_age_mean_over_ticks_delta`, mean over-ticks queued-task mean-age delta across seeds.
- `queued_task_age_max_peak_delta`, mean peak queued-task max-age delta across seeds.
- `attention_capture_pressure_max_final_delta`, mean final max capture-pressure delta across seeds.
- `attention_capture_pressure_mean_over_ticks_delta`, mean over-ticks max capture-pressure delta across seeds.
- `attention_capture_pressure_peak_delta`, mean peak max capture-pressure delta across seeds.
- Per-class capture-pressure final, mean-over-ticks, and peak high-minus-normal deltas for each attention class.
- Per-policy normal-to-medium slope, medium-to-high slope, and high-interval-minus-low-interval curvature fields for value-weighted completed work, completed tasks, final queue depth, final queued-task mean age, peak queued-task max age, final max capture pressure, mean max capture pressure, and peak max capture pressure.
- Per-class capture-pressure normal-to-medium slope, medium-to-high slope, and high-interval-minus-low-interval curvature fields for final, mean-over-ticks, and peak capture pressure.

The pressure comparison `summary.md` reports the normal, medium, and high-pressure config paths, seed set, policy-row count, a `Fixed-policy pressure deltas` section, a `Most pressure-sensitive curve metric` section, a `Pressure-curve response ranking` section, a `Top pressure-response explanation` section, a `Pressure-response interpretation` section, a `Per-class capture-pressure prefix comparison` section, a `Seed-set sensitivity` section, and a `Fixed-policy pressure curves` section. The sensitivity section identifies the policy/observable pair with the largest absolute slope or curvature response from the existing pressure-curve fields, including capture-pressure observables. The ranking section sorts every policy/observable pressure-curve response by absolute magnitude, the explanation section reports the top-ranked response's condition means, slopes, curvature, and high-minus-normal delta, the interpretation section turns the leading full-seed response into a compact deterministic reading and notes whether the last checked prefix selects the same response, and the curves section reports the same slope and curvature fields emitted in `pressure_comparison_metrics.csv`.

The pressure comparison summary also includes a `Per-class capture-pressure interpretation` section. It filters the same deterministic pressure-response ranking down to individual attention-class capture-pressure observables, reports the strongest overall class-specific response, and then reports the strongest class-specific response for each fixed policy with condition means, slopes, curvature, and high-minus-normal delta.

`Per-class capture-pressure prefix comparison` applies the same seed-prefix stability check to the class-specific pressure-response ranking only. It reports the full seed set's strongest class-specific capture-pressure response, the last proper prefix's strongest class-specific response, whether the class top response is stable for the last prefix and across all prefixes, prefix instability causes, and one table row for every proper seed prefix.

`pressure_response_selection.csv` is a companion machine-readable artifact for the top response selected by the same deterministic ranking used in `summary.md`. It has one `full` row for the configured full seed set and one `prefix` row for each proper seed prefix. It also has one `class_full` row and one `class_prefix` row for each proper seed prefix, filtered to individual attention-class capture-pressure observables. Each row records the selected policy, observable, metric, source field, signed and absolute response value, condition means, pressure slopes, curvature, high-minus-normal delta, and whether that prefix selected the same top response as the matching full-seed selection.

`Pressure-response interpretation` restates the full seed set's largest absolute pressure response as one sentence with the selected policy, observable, slope-or-curvature metric, normal/medium/high condition means, both pressure slopes, curvature, and high-minus-normal delta. When at least two seeds are configured, the section also compares the last proper prefix against the full seed set. Stable prefixes report that the leading explanation is stable for the checked prefix; unstable prefixes report the changed dimensions through `instability causes`, the prefix seed set, the prefix-selected policy/observable/metric, and that prefix response's same curve values.

`Seed-set sensitivity` is a deterministic prefix check over the already-generated per-seed comparison rows. For a run with `--seeds 1 2 3`, `full_seeds` is `1,2,3` and `prefix_seeds` is `1,2`; the summary recomputes pressure rows for the prefix subset and compares its top-ranked pressure response with the full seed set's top response. The section also reports a prefix table for every proper prefix of the configured seed set, such as `1` and `1,2`, so the top pressure-response ordering can be inspected as seeds accumulate. `top response stable across prefix: true` means the same policy, observable, and slope-or-curvature metric won under both seed sets. `top response stable across all prefixes: true` means every proper prefix selected the same top response as the full seed set. `false` means the current top response depends on the seed set, so the pressure-response ranking should be treated as seed-set-sensitive rather than as a stable ordering.

When a prefix ranking is unstable, `prefix instability causes` reports which top-response dimensions changed relative to the full seed set: `policy`, `observable`, `metric`, or a comma-separated combination. `metric` means the winning pressure-curve measure changed between a slope and curvature field, or between the normal-to-medium and medium-to-high slope fields. Stable prefix rows report `none`.

## Output Schema

Every run writes `config.yaml`, a normalized copy of the loaded config. Optional artifact flags in the config control the remaining outputs.

The `outputs` section may disable any optional artifact:

```yaml
outputs:
  write_manifest: false
  write_metrics: false
  write_events: false
  write_summary: false
```

With all optional outputs disabled, the run still simulates normally and writes only `config.yaml`. Output directories are append-safe: a run refuses to start when any artifact it would write already exists. Disabled artifacts are ignored for collision checks and are preserved byte-for-byte, so stale or sentinel `manifest.yaml`, `metrics.csv`, `events.csv`, or `summary.md` files do not block a config-only run. The mandatory `config.yaml` always participates in collision checks and blocks reruns into the same directory.

The checked-in config-only fixture can be exercised with:

```bash
python -m ohdyn.run --config configs/a0_config_only.yaml --seed 1 --out runs/a0_config_only_seed1
```

The checked-in default-output fixture omits the optional `outputs` section and therefore normalizes to all artifacts enabled:

```bash
python -m ohdyn.run --config configs/a0_default_outputs.yaml --seed 1 --out runs/a0_default_outputs_seed1
```

The checked-in config-only reordered-actions fixture writes only normalized config provenance while preserving YAML action order:

```bash
python -m ohdyn.run --config configs/a0_config_only_reordered_actions.yaml --seed 1 --out runs/a0_config_only_reordered_actions_seed1
```

The checked-in manifest-only fixture disables metrics, events, and summary output while preserving manifest provenance:

```bash
python -m ohdyn.run --config configs/a0_manifest_only.yaml --seed 1 --out runs/a0_manifest_only_seed1
```

The checked-in manifest-only reordered-actions fixture preserves manifest schema/order provenance without writing metrics, events, or summary output:

```bash
python -m ohdyn.run --config configs/a0_manifest_only_reordered_actions.yaml --seed 1 --out runs/a0_manifest_only_reordered_actions_seed1
```

The checked-in no-manifest fixture writes metrics, events, and summary output without manifest provenance:

```bash
python -m ohdyn.run --config configs/a0_no_manifest.yaml --seed 1 --out runs/a0_no_manifest_seed1
```

The checked-in no-manifest reordered-actions fixture combines disabled manifest output with non-default action order:

```bash
python -m ohdyn.run --config configs/a0_no_manifest_reordered_actions.yaml --seed 1 --out runs/a0_no_manifest_reordered_actions_seed1
```

This fixture is the current smoke path for replaying lobe state without manifest provenance: use the normalized `config.yaml` for ticks/actions and `events.csv` for per-tick action/task lifecycle replay, then compare reconstructed lobe labels, transitions, dwell runs, queue aggregates, and role/action totals against `metrics.csv` and `summary.md`.

The checked-in reordered-actions fixture keeps the same baseline action vocabulary but uses YAML-defined non-default action order:

```bash
python -m ohdyn.run --config configs/a0_reordered_actions.yaml --seed 1 --out runs/a0_reordered_actions_seed1
```

This fixture protects the schema-alignment invariant that normalized `config.yaml`, manifest `actions`, manifest metrics schema, manifest role/action schema, and emitted `metrics.csv` headers all preserve the action order from the loaded YAML config.

`manifest.yaml` records run provenance and model shape:

- `experiment_id`, `seed`, `ticks`, `agent_count`, and configured `actions`
- `outputs`, the artifact flags used by the run
- `artifacts`, the exact files written for the run
- `environment.git_commit`, `environment.python_version`, and package versions
- `model.agent_ids`, `model.roles`, `model.bus_nodes`, and `model.bus_edges`
- `model.baseline_lobes.labels`, the baseline lobe vocabulary used in `metrics.csv`
- `model.baseline_lobes.transition_fields`, the lobe transition/run-state metric fields
- `model.queue_dynamics_metrics.pressure_fields`, the queue pressure balance metric fields
- `model.queue_dynamics_metrics.queued_task_age_fields`, the queued-task-age metric fields
- `model.events.types`, the supported baseline event type vocabulary
- `model.events.fields`, the event schema fields emitted in `events.csv`
- `model.metrics.fields`, the complete metrics schema field order emitted in `metrics.csv`
- `model.role_action_metrics.fields`, the role/action metric fields emitted in `metrics.csv`
- `config`, the normalized run config

`metrics.csv` has one row per tick. The current fields include:

- Tick and static graph state: `tick`, `agent_count`, `bus_nodes`, `bus_edges`, `bus_density`, `bus_mean_degree`, `bus_degree_centralization`
- Queue and task totals: `queue_depth`, `queue_delta_tick`, `tasks_created_total`, `tasks_completed_total`, `tasks_completed_tick`
- Per-tick action counts: `messages_sent_tick`, `tasks_created_tick`, `tasks_worked_tick`, `idle_tick`
- Queue pressure balances: `created_completed_balance_tick`, `created_worked_balance_tick`, `work_completion_gap_tick`, `backlog_pressure_tick`
- Queue age metrics: `queued_task_age_max_tick`, `queued_task_age_mean_tick`
- Lobe state: `baseline_lobe_label`, `baseline_lobe_previous_label`, `baseline_lobe_transition`, `baseline_lobe_transition_tick`, `baseline_lobe_run_id`, `baseline_lobe_current_run_length`
- Role/action counts named `role_<role>_<action>_tick`
- Agent population summary: `mean_agent_bias`

`events.csv` has one row per agent action per tick. The current fields are `tick`, `event_type`, `agent_id`, `action`, `target_id`, `task_id`, `work_units`, `remaining_work`, and `completed`. Event types are `agent_idle`, `message_sent`, `task_created`, and `task_worked`.

`summary.md` is a human-readable run summary with bus node/edge counts, static bus metrics, event, task, queue pressure, queue age, written-artifact/output-flag, artifact schema provenance, lobe total, lobe transition, lobe dwell-run, and role/action aggregate sections. The written-artifact/output-flag section reports the exact artifacts written for the run and whether each optional output class was enabled. The schema provenance section reports the emitted metrics/event field counts, lobe/queue/role-action schema counts, and the helper names that define the CSV schemas mirrored in `manifest.yaml`.

## Early Guardrails

- Every run must be reproducible by seed.
- Save the full config and run manifest in the output directory.
- Do not implement dashboards before the metrics schema is stable.
- Do not add real LLM calls in early experiments.
- Every experiment must produce a `summary.md`.
- Every sweep must save per-run metrics and an aggregate summary.

## Planned Stack

- Python
- Mesa
- NetworkX
- NumPy/SciPy
- pandas or polars
- pydantic/PyYAML
- pytest
- Plotly/Jupyter later
- UMAP/HDBSCAN/ruptures/PySINDy later
