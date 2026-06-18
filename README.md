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
manifest.yaml
metrics.csv
events.csv
summary.md
```

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

