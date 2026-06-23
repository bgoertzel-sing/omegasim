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

A contrasting research-heavy A2 fixture uses the same deterministic baseline with more reserved share for long-term research:

```bash
python -m ohdyn.run --config configs/a2_attention_research_heavy.yaml --seed 1 --out runs/a2_attention_research_heavy_seed1
```

The focused comparison test runs `configs/a2_attention_smoke.yaml` and `configs/a2_attention_research_heavy.yaml` with the same seed and verifies that the research-heavy policy shifts completed work toward `long_term_research` while changing value-weighted throughput and stale-task age.

A small deterministic comparison runner executes both A2 fixtures across a short seed set and writes per-run artifacts plus aggregate comparison outputs:

```bash
python -m ohdyn.compare_attention --seeds 1 2 3 --out runs/a2_attention_compare
```

The comparison directory contains `comparison_metrics.csv`, an aggregate `summary.md`, and one normal run artifact directory per policy/seed. The aggregate CSV uses stable run subdirectory names so same-seed comparisons are byte-reproducible across output parent directories.

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
