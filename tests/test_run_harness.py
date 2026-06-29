from __future__ import annotations

from collections import Counter, deque
from pathlib import Path
import csv
import subprocess
import sys

import pytest
import yaml

from ohdyn.sim import (
    A6_ARTIFACT_FIELDS,
    A6_ARTIFACT_UPDATE_SOURCE_FIELDS,
    A6_EVENT_TYPES,
    ATTENTION_EVENT_TYPES,
    BASELINE_EVENT_TYPES,
    BASELINE_LOBE_LABELS,
    BASELINE_LOBE_TRANSITION_FIELDS,
    BASELINE_ROLES,
    EVENT_FIELDS,
    EXOGENOUS_ARRIVAL_EVENT_TYPES,
    EXOGENOUS_ARRIVAL_METRIC_FIELDS,
    QUEUE_PRESSURE_METRIC_FIELDS,
    QUEUED_TASK_AGE_METRIC_FIELDS,
    SimulationResult,
    _initial_a6_artifact,
    attention_policy_metric_fields,
    logistic_appraisal_metric_fields,
    metrics_fieldnames,
    predictive_control_metric_fields,
    role_action_metric_fields,
    semantic_field_metric_fields,
    simulate,
)
from ohdyn.analyze_a6_logistic_appraisal import (
    A6_1_PILOT_NULL_GATE_FIELDS,
    A6_ANALYSIS_ENDPOINT_FIELDS,
    A6_ANALYSIS_MANIFEST_FIELDS,
    A6_ARTIFACT_PROVENANCE_FIELDS,
    A6_COMPARISON_CONSISTENCY_FIELDS,
    A6_CONTROL_DELTA_FIELDS,
    A6_CONTROL_SUMMARY_FIELDS,
    A6_EFFECTS_CONSISTENCY_FIELDS,
    A6_RESIDUAL_PREFLIGHT_FIELDS,
    A6_RESIDUAL_CONTRAST_ROLLUP_FIELDS,
    A6_RESIDUAL_CONTRAST_SUMMARY_FIELDS,
    A6_RESIDUAL_TIMESERIES_FIELDS,
    A6_SOURCE_ACCOUNTING_FIELDS,
    run_a6_logistic_appraisal_analysis,
)
from ohdyn.analyze_a6_2_residual_recurrence import (
    A6_2_COMPLETENESS_FIELDS,
    A6_2_DELTA_FIELDS,
    A6_2_MANIFEST_FIELDS,
    A6_2_RECURRENCE_FIELDS,
    run_a6_2_residual_recurrence_analysis,
)
from ohdyn.compare_a6_2_long_horizon import run_a6_2_long_horizon_comparison
from ohdyn.compare_a6_logistic_appraisal import (
    A6_COMPARISON_FIELDS,
    A6_EFFECT_FIELDS,
    run_a6_logistic_appraisal_comparison,
)
from ohdyn.config import (
    ATTENTION_CLASSES,
    A6_ACTIONS,
    ExogenousArrivalsConfig,
    OmegaConfig,
    load_config,
)
from ohdyn.analyze_pressure import (
    INTERPRETATION_FIELDS,
    PRESSURE_BOOTSTRAP_RANK_STABILITY_FIELDS,
    TRAJECTORY_PRESSURE_RANKING_FIELDS,
    VALUE_YIELD_DIVERGENCE_STABILITY_FIELDS,
    VALUE_YIELD_DIVERGENCE_RANKING_FIELDS,
    _yield_divergence_interpretation,
    run_analysis,
)
from ohdyn.analyze_service_capacity_trajectory import (
    SERVICE_CAPACITY_TRAJECTORY_BOOTSTRAP_FIELDS,
    SERVICE_CAPACITY_TRAJECTORY_EFFECT_FIELDS,
    SERVICE_CAPACITY_TRAJECTORY_FIELDS,
    SERVICE_CAPACITY_TRAJECTORY_NULL_FIELDS,
    run_service_capacity_trajectory_analysis,
)
from ohdyn.analyze_queue_blind_lobes import (
    QUEUE_BLIND_LOBE_EFFECT_FIELDS,
    QUEUE_BLIND_LOBE_FIELDS,
    _queue_blind_label,
    run_queue_blind_lobe_analysis,
)
from ohdyn.analyze_queue_flow_service import (
    QUEUE_FLOW_SERVICE_EFFECT_FIELDS,
    QUEUE_FLOW_SERVICE_FIELDS,
    run_queue_flow_service_analysis,
)
from ohdyn.analyze_lagged_service_sync import (
    LAGGED_SERVICE_SYNC_EFFECT_FIELDS,
    LAGGED_SERVICE_SYNC_FIELDS,
    run_lagged_service_sync_analysis,
)
from ohdyn.analyze_a4_smoke_contract import run_a4_smoke_contract_preflight
from ohdyn.analyze_a4_holdout import A4_EFFECT_FIELDS, run_a4_holdout_analysis
from ohdyn.analyze_a4_delayed_null import (
    A4_DELAYED_NULL_EFFECT_FIELDS,
    A4_DELAYED_NULL_ENDPOINT_FIELDS,
    run_a4_delayed_null_analysis,
)
from ohdyn.analyze_a4_accounting_controls import (
    A4_ACCOUNTING_CONTROL_EFFECT_FIELDS,
    A4_ACCOUNTING_CONTROL_ENDPOINT_FIELDS,
    run_a4_accounting_control_analysis,
)
from ohdyn.analyze_a5_residual_accounting import (
    A5_RESIDUAL_ACCOUNTING_EFFECT_FIELDS,
    A5_RESIDUAL_ACCOUNTING_METRIC_FIELDS,
    run_a5_residual_accounting_analysis,
)
from ohdyn.analyze_exogenous_arrival_controls import (
    EXOGENOUS_CONTROL_BOOTSTRAP_FIELDS,
    EXOGENOUS_CONTROL_METRIC_FIELDS,
    EXOGENOUS_CONTROL_NULL_FIELDS,
    run_exogenous_arrival_control_analysis,
)
from ohdyn.automation_guard import read_automation_state
from ohdyn.a7_2_delayed_prediction_contract import (
    A7_2_ACTIONS,
    A7_2_ANALYZER_COMPLETENESS_FIELDS,
    A7_2_ANALYZER_GUARDRAIL_FIELDS,
    A7_2_ANALYZER_MANIFEST_FIELDS,
    A7_2_ANALYZER_NULL_CONTRAST_FIELDS,
    A7_2_ANALYZER_PREFLIGHT_FIELDS,
    A7_2_ANALYZER_RESIDUAL_FIELDS,
    A7_2_COMPARISON_MANIFEST_FIELDS,
    A7_2_CONDITIONS,
    A7_2_CONTROL_FIELDS,
    A7_2_EVENT_FIELDS,
    A7_2_NULL_CONDITIONS,
    A7_2_POSITIVE_CONDITION,
    A7_2_PRIMARY_ENDPOINTS,
    A7_2_PRODUCTIVITY_GUARDRAILS,
    A7_2_SMOKE_PARAMETERS,
    A7_2_SOURCE_LEDGER_FIELDS,
    A7_2_STATE_FIELDS,
    a7_2_required_event_fields,
    a7_2_required_metric_fields,
)
from ohdyn.a7_3_dimensionless_contract import (
    A7_3_CONDITIONS,
    A7_3_DELAY_SOURCE_INVARIANTS,
    A7_3_DIMENSIONLESS_CONTROLS,
    A7_3_LIFTED_STATE_FIELDS,
    A7_3_MECHANICS_MANIFEST_FIELDS,
    A7_3_NULL_CONDITIONS,
    A7_3_POSITIVE_CONDITION,
    A7_3_SMOKE_PARAMETERS,
    A7_3_SOURCE_LEDGER_FIELDS,
    a7_3_required_event_fields,
    a7_3_required_metric_fields,
)
from ohdyn.analyze_a7_2_delayed_prediction import (
    run_a7_2_delayed_prediction_analysis,
)
from ohdyn.compare_a7_2_delayed_prediction import (
    run_a7_2_delayed_prediction_comparison,
)
from ohdyn.compare_a7_3_dimensionless_delayed import (
    run_a7_3_dimensionless_smoke,
)
from ohdyn.analyze_a7_3_preflight import (
    A7_3_PREFLIGHT_STATUS_ELIGIBLE,
    A7_3_PREFLIGHT_STATUS_SOURCE_LEDGER,
    run_a7_3_preflight_analysis,
)
from ohdyn.analyze_a7_3_residual_skeleton import (
    A7_3_RESIDUAL_STATUS_PREFLIGHT_REQUIRED,
    A7_3_RESIDUAL_STATUS_SMOKE_SCALE,
    run_a7_3_residual_skeleton_analysis,
)
from ohdyn.a7_semantic_field_contract import (
    A7_CONDITIONS,
    A7_CONTROL_FIELDS,
    A7_EVENT_FIELDS,
    A7_FIELD_VALUES,
    A7_ANALYZER_SMOKE_REPORT_FIELDS,
    A7_NULL_CONDITIONS,
    A7_POSITIVE_CONDITION,
    A7_PREDICTION_FIELDS,
    A7_SOURCE_COMPONENTS,
    A7_STATE_FIELDS,
    A7_UPDATE_EQUATIONS,
    A7_UTILITY_EQUATIONS,
    a7_required_event_fields,
    a7_required_metric_fields,
)
from ohdyn.three_hive_ring_contract import (
    THREE_HIVE_RING_ACTIONS,
    THREE_HIVE_RING_ANALYZER_COMPLETENESS_FIELDS,
    THREE_HIVE_RING_ANALYZER_GUARDRAIL_FIELDS,
    THREE_HIVE_RING_ANALYZER_MANIFEST_FIELDS,
    THREE_HIVE_RING_ANALYZER_NULL_CONTRAST_FIELDS,
    THREE_HIVE_RING_ANALYZER_RESIDUAL_FIELDS,
    THREE_HIVE_RING_ANALYZER_SOURCE_LEDGER_FIELDS,
    THREE_HIVE_RING_CONDITIONS,
    THREE_HIVE_RING_DIMENSIONLESS_MANIFEST_FIELDS,
    THREE_HIVE_RING_EDGE_FIELDS,
    THREE_HIVE_RING_EDGE_HIVES,
    THREE_HIVE_RING_EDGES,
    THREE_HIVE_RING_HIVES,
    THREE_HIVE_RING_MECHANICS_MANIFEST_FIELDS,
    THREE_HIVE_RING_NULL_CONDITIONS,
    THREE_HIVE_RING_POSITIVE_CONDITION,
    THREE_HIVE_RING_PRIMARY_ENDPOINTS,
    THREE_HIVE_RING_PREFLIGHT_COMPLETENESS_FIELDS,
    THREE_HIVE_RING_PREFLIGHT_MANIFEST_FIELDS,
    THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS,
    THREE_HIVE_RING_RESIDUAL_CONTROLS,
    THREE_HIVE_RING_ROLE_BIASES,
    THREE_HIVE_RING_SCHEMA_SMOKE_MANIFEST_FIELDS,
    THREE_HIVE_RING_SMOKE_PARAMETERS,
    THREE_HIVE_RING_SOURCE_LEDGER_CSV_FIELDS,
    THREE_HIVE_RING_SOURCE_LEDGER_FIELDS,
    THREE_HIVE_RING_STATE_FIELDS,
    three_hive_ring_required_event_fields,
    three_hive_ring_required_metric_fields,
)
from ohdyn.compare_three_hive_ring_mechanics import (
    THREE_HIVE_RING_MECHANICS_SCIENTIFIC_STATUS,
    THREE_HIVE_RING_MECHANICS_STATUS,
    run_three_hive_ring_mechanics_smoke,
)
from ohdyn.compare_three_hive_ring import (
    THREE_HIVE_RING_ARTIFACT_STATUS,
    THREE_HIVE_RING_SCIENTIFIC_STATUS,
    run_three_hive_ring_schema_smoke,
)
from ohdyn.analyze_three_hive_ring_preflight import (
    THREE_HIVE_RING_PREFLIGHT_STATUS_ELIGIBLE,
    THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SOURCE_LEDGER,
    THREE_HIVE_RING_PREFLIGHT_STATUS_NO_METRICS_EVENTS,
    run_three_hive_ring_preflight_analysis,
)
from ohdyn.analyze_three_hive_ring_residual_null import (
    run_three_hive_ring_residual_null_analysis,
)
from ohdyn.analyze_a7_semantic_field import (
    A7_ANALYZER_COMPLETENESS_FIELDS,
    A7_ANALYZER_MANIFEST_FIELDS,
    A7_ANALYZER_NULL_CONTRAST_FIELDS,
    A7_ANALYZER_RESIDUAL_FIELDS,
    run_a7_semantic_field_analysis,
)
from ohdyn.compare_a7_semantic_field import (
    A7_COMPARISON_MANIFEST_FIELDS,
    A7_PLACEHOLDER_MANIFEST_FIELDS,
    DEFAULT_A7_LONG_HORIZON_CONFIGS,
    run_a7_semantic_field_comparison,
    run_a7_semantic_field_placeholder_comparison,
)
from ohdyn.calibrate_exogenous_arrivals import (
    EXOGENOUS_CALIBRATION_FIELDS,
    run_exogenous_arrival_calibration,
)
from ohdyn.compare_exogenous_arrivals import (
    EXOGENOUS_COMPARISON_FIELDS,
    EXOGENOUS_EFFECT_FIELDS,
    run_exogenous_arrival_comparison,
)
from ohdyn.compare_predictive_control import (
    A5_PREDICTIVE_COMPARISON_FIELDS,
    A5_PREDICTIVE_EFFECT_FIELDS,
    run_predictive_control_comparison,
)
from ohdyn.compare_attention import run_comparison
from ohdyn.compare_pressure import (
    PRESSURE_COMPARISON_FIELDS,
    PRESSURE_RESPONSE_SELECTION_FIELDS,
    PRESSURE_STABILITY_AGREEMENT_FIELDS,
    PRESSURE_STABILITY_CONVERGENCE_FIELDS,
    PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
    run_pressure_comparison,
)
from ohdyn.compare_service_capacity import (
    SERVICE_CAPACITY_COMPARISON_FIELDS,
    SERVICE_CAPACITY_EFFECT_FIELDS,
    run_service_capacity_comparison,
)
from ohdyn.synthesize_service_capacity_decision import (
    DECISION_SYNTHESIS_FIELDS,
    run_service_capacity_decision_synthesis,
)
from ohdyn.run import run_experiment


CONFIG = Path("configs/a0_smoke.yaml")
A2_ATTENTION = Path("configs/a2_attention_smoke.yaml")
A2_ATTENTION_RANDOM_AVAILABLE = Path("configs/a2_attention_random_available.yaml")
A2_ATTENTION_RESEARCH_HEAVY = Path("configs/a2_attention_research_heavy.yaml")
A2_ATTENTION_INTERNAL_IMPROVEMENT = Path("configs/a2_attention_internal_improvement.yaml")
A2_ATTENTION_MEDIUM_PRESSURE = Path("configs/a2_attention_medium_pressure.yaml")
A2_ATTENTION_RESEARCH_HEAVY_MEDIUM_PRESSURE = Path(
    "configs/a2_attention_research_heavy_medium_pressure.yaml"
)
A2_ATTENTION_INTERNAL_IMPROVEMENT_MEDIUM_PRESSURE = Path(
    "configs/a2_attention_internal_improvement_medium_pressure.yaml"
)
A2_ATTENTION_HIGH_PRESSURE = Path("configs/a2_attention_high_pressure.yaml")
A2_ATTENTION_RANDOM_AVAILABLE_HIGH_PRESSURE = Path(
    "configs/a2_attention_random_available_high_pressure.yaml"
)
A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE = Path(
    "configs/a2_attention_research_heavy_high_pressure.yaml"
)
A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE = Path(
    "configs/a2_attention_internal_improvement_high_pressure.yaml"
)
A2_ATTENTION_EXTREME_PRESSURE = Path("configs/a2_attention_extreme_pressure.yaml")
A2_ATTENTION_LOW_SERVICE_CAPACITY = Path("configs/a2_attention_low_service_capacity.yaml")
A2_ATTENTION_HIGH_SERVICE_CAPACITY = Path("configs/a2_attention_high_service_capacity.yaml")
A2_ATTENTION_LOW_SERVICE_CAPACITY_HIGH_PRESSURE = Path(
    "configs/a2_attention_low_service_capacity_high_pressure.yaml"
)
A2_ATTENTION_HIGH_SERVICE_CAPACITY_HIGH_PRESSURE = Path(
    "configs/a2_attention_high_service_capacity_high_pressure.yaml"
)
A2_ATTENTION_LOW_SERVICE_CAPACITY_EXTREME_PRESSURE = Path(
    "configs/a2_attention_low_service_capacity_extreme_pressure.yaml"
)
A2_ATTENTION_HIGH_SERVICE_CAPACITY_EXTREME_PRESSURE = Path(
    "configs/a2_attention_high_service_capacity_extreme_pressure.yaml"
)
A2_ATTENTION_RANDOM_AVAILABLE_EXTREME_PRESSURE = Path(
    "configs/a2_attention_random_available_extreme_pressure.yaml"
)
A2_ATTENTION_RESEARCH_HEAVY_EXTREME_PRESSURE = Path(
    "configs/a2_attention_research_heavy_extreme_pressure.yaml"
)
A2_ATTENTION_INTERNAL_IMPROVEMENT_EXTREME_PRESSURE = Path(
    "configs/a2_attention_internal_improvement_extreme_pressure.yaml"
)
A2_EXOGENOUS_ARRIVALS = Path("configs/a2_exogenous_arrivals_smoke.yaml")
A2_EXOGENOUS_ARRIVALS_LOW = Path("configs/a2_exogenous_arrivals_low.yaml")
A2_EXOGENOUS_ARRIVALS_MEDIUM = Path("configs/a2_exogenous_arrivals_medium.yaml")
A2_EXOGENOUS_ARRIVALS_HIGH = Path("configs/a2_exogenous_arrivals_high.yaml")
A4_TWO_HIVE_NONE = Path("configs/a4_two_hive_none_smoke.yaml")
A4_TWO_HIVE_DIRECT = Path("configs/a4_two_hive_direct_smoke.yaml")
A4_TWO_HIVE_DELAYED = Path("configs/a4_two_hive_delayed_smoke.yaml")
A4_TWO_HIVE_SHUFFLED = Path("configs/a4_two_hive_shuffled_smoke.yaml")
A4_TWO_HIVE_NONE_HOLDOUT = Path("configs/a4_two_hive_none_holdout.yaml")
A4_TWO_HIVE_DIRECT_HOLDOUT = Path("configs/a4_two_hive_direct_holdout.yaml")
A4_TWO_HIVE_DELAYED_HOLDOUT = Path("configs/a4_two_hive_delayed_holdout.yaml")
A4_TWO_HIVE_SHUFFLED_HOLDOUT = Path("configs/a4_two_hive_shuffled_holdout.yaml")
A5_PREDICTIVE_LINEAR = Path("configs/a5_predictive_linear_smoke.yaml")
A5_1_PREDICTION_SPEND_LINEAR = Path("configs/a5_1_prediction_spend_linear_smoke.yaml")
A6_LOGISTIC_APPRAISAL = Path("configs/a6_logistic_appraisal_smoke.yaml")
A6_LINEAR_APPRAISAL = Path("configs/a6_linear_appraisal_smoke.yaml")
A6_THRESHOLD_SHUFFLED = Path("configs/a6_threshold_shuffled_smoke.yaml")
A6_PHASE_SHUFFLED = Path("configs/a6_phase_shuffled_smoke.yaml")
A7_LOGISTIC_SEMANTIC_COUPLING = Path("configs/a7_logistic_semantic_coupling_smoke.yaml")
A7_SEMANTIC_OFF_BASELINE = Path("configs/a7_semantic_off_baseline_smoke.yaml")
A7_AMPLITUDE_MATCHED_LINEAR = Path(
    "configs/a7_amplitude_matched_linear_semantic_coupling_smoke.yaml"
)
A7_SOURCE_PRESERVING_LABEL_SHUFFLE = Path(
    "configs/a7_source_preserving_semantic_label_shuffle_smoke.yaml"
)
A7_SEMANTIC_PHASE_SHUFFLE = Path("configs/a7_semantic_field_phase_shuffle_smoke.yaml")
A7_PREDICTION_TIMING_BROKEN = Path(
    "configs/a7_prediction_budget_timing_broken_matched_count_null_smoke.yaml"
)
A7_SMOKE_FIXTURES = (
    A7_LOGISTIC_SEMANTIC_COUPLING,
    A7_SEMANTIC_OFF_BASELINE,
    A7_AMPLITUDE_MATCHED_LINEAR,
    A7_SOURCE_PRESERVING_LABEL_SHUFFLE,
    A7_SEMANTIC_PHASE_SHUFFLE,
    A7_PREDICTION_TIMING_BROKEN,
)
A7_2_ZERO_BUDGET_REACTIVE = Path("configs/a7_2_zero_budget_reactive_smoke.yaml")
A7_2_INTERMEDIATE_ENDOGENOUS_DELAYED = Path(
    "configs/a7_2_intermediate_endogenous_delayed_prediction_smoke.yaml"
)
A7_2_HIGH_BUDGET_ORACLE = Path("configs/a7_2_high_budget_oracle_smoothing_smoke.yaml")
A7_2_AMPLITUDE_MATCHED_LINEAR = Path(
    "configs/a7_2_amplitude_matched_linear_delayed_prediction_smoke.yaml"
)
A7_2_SAME_TICK_LOGISTIC = Path("configs/a7_2_same_tick_logistic_prediction_smoke.yaml")
A7_2_PHASE_SHUFFLED_LAG_INPUT = Path("configs/a7_2_phase_shuffled_lag_input_smoke.yaml")
A7_2_THRESHOLD_SHUFFLED = Path("configs/a7_2_threshold_shuffled_smoke.yaml")
A7_2_SOURCE_PRESERVING_ARTIFACT_LABEL_SHUFFLE = Path(
    "configs/a7_2_source_preserving_artifact_label_shuffle_smoke.yaml"
)
A7_2_SPEND_ONLY_REPLAY = Path("configs/a7_2_spend_only_replay_smoke.yaml")
A7_2_ARTIFACT_OFF_SOURCE_LEDGER_NULL = Path(
    "configs/a7_2_artifact_off_source_ledger_null_smoke.yaml"
)
A7_3_DIMENSIONLESS_SMOKE = Path("configs/a7_3_dimensionless_smoke.yaml")
THREE_HIVE_RING_CONTRACT_VALIDATION = Path(
    "configs/three_hive_ring_contract_validation.yaml"
)
A7_2_SMOKE_FIXTURES = (
    A7_2_ZERO_BUDGET_REACTIVE,
    A7_2_INTERMEDIATE_ENDOGENOUS_DELAYED,
    A7_2_HIGH_BUDGET_ORACLE,
    A7_2_AMPLITUDE_MATCHED_LINEAR,
    A7_2_SAME_TICK_LOGISTIC,
    A7_2_PHASE_SHUFFLED_LAG_INPUT,
    A7_2_THRESHOLD_SHUFFLED,
    A7_2_SOURCE_PRESERVING_ARTIFACT_LABEL_SHUFFLE,
    A7_2_SPEND_ONLY_REPLAY,
    A7_2_ARTIFACT_OFF_SOURCE_LEDGER_NULL,
)
DEFAULT_OUTPUTS = Path("configs/a0_default_outputs.yaml")
REORDERED_ACTIONS = Path("configs/a0_reordered_actions.yaml")
CONFIG_ONLY = Path("configs/a0_config_only.yaml")
CONFIG_ONLY_REORDERED_ACTIONS = Path("configs/a0_config_only_reordered_actions.yaml")
MANIFEST_ONLY = Path("configs/a0_manifest_only.yaml")
MANIFEST_ONLY_REORDERED_ACTIONS = Path("configs/a0_manifest_only_reordered_actions.yaml")
NO_MANIFEST = Path("configs/a0_no_manifest.yaml")
NO_MANIFEST_REORDERED_ACTIONS = Path("configs/a0_no_manifest_reordered_actions.yaml")
FULL_OUTPUT_FIXTURES = (CONFIG, DEFAULT_OUTPUTS, REORDERED_ACTIONS)
CONFIG_ONLY_FIXTURES = (CONFIG_ONLY, CONFIG_ONLY_REORDERED_ACTIONS)
MANIFEST_ONLY_FIXTURES = (MANIFEST_ONLY, MANIFEST_ONLY_REORDERED_ACTIONS)
NO_MANIFEST_FIXTURES = (NO_MANIFEST, NO_MANIFEST_REORDERED_ACTIONS)

A0_FULL_ARTIFACTS = [
    "config.yaml",
    "manifest.yaml",
    "metrics.csv",
    "events.csv",
    "summary.md",
]
CONFIG_ONLY_ARTIFACTS = ["config.yaml"]
MANIFEST_ONLY_ARTIFACTS = ["config.yaml", "manifest.yaml"]
NO_MANIFEST_ARTIFACTS = ["config.yaml", "metrics.csv", "events.csv", "summary.md"]
OUTPUT_FIXTURE_ARTIFACTS = {
    CONFIG: A0_FULL_ARTIFACTS,
    A2_ATTENTION: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RANDOM_AVAILABLE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RESEARCH_HEAVY: A0_FULL_ARTIFACTS,
    A2_ATTENTION_INTERNAL_IMPROVEMENT: A0_FULL_ARTIFACTS,
    A2_ATTENTION_MEDIUM_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RESEARCH_HEAVY_MEDIUM_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_INTERNAL_IMPROVEMENT_MEDIUM_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RANDOM_AVAILABLE_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RANDOM_AVAILABLE_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_RESEARCH_HEAVY_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_INTERNAL_IMPROVEMENT_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_LOW_SERVICE_CAPACITY: A0_FULL_ARTIFACTS,
    A2_ATTENTION_HIGH_SERVICE_CAPACITY: A0_FULL_ARTIFACTS,
    A2_ATTENTION_LOW_SERVICE_CAPACITY_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_HIGH_SERVICE_CAPACITY_HIGH_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_LOW_SERVICE_CAPACITY_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_ATTENTION_HIGH_SERVICE_CAPACITY_EXTREME_PRESSURE: A0_FULL_ARTIFACTS,
    A2_EXOGENOUS_ARRIVALS: A0_FULL_ARTIFACTS,
    A2_EXOGENOUS_ARRIVALS_LOW: A0_FULL_ARTIFACTS,
    A2_EXOGENOUS_ARRIVALS_MEDIUM: A0_FULL_ARTIFACTS,
    A2_EXOGENOUS_ARRIVALS_HIGH: A0_FULL_ARTIFACTS,
    A4_TWO_HIVE_NONE: [
        *A0_FULL_ARTIFACTS,
        "hive_metrics.csv",
        "cross_hive_metrics.csv",
        "hive_events.csv",
        "coupling_events.csv",
    ],
    A4_TWO_HIVE_DIRECT: [
        *A0_FULL_ARTIFACTS,
        "hive_metrics.csv",
        "cross_hive_metrics.csv",
        "hive_events.csv",
        "coupling_events.csv",
    ],
    A4_TWO_HIVE_DELAYED: [
        *A0_FULL_ARTIFACTS,
        "hive_metrics.csv",
        "cross_hive_metrics.csv",
        "hive_events.csv",
        "coupling_events.csv",
    ],
    A4_TWO_HIVE_SHUFFLED: [
        *A0_FULL_ARTIFACTS,
        "hive_metrics.csv",
        "cross_hive_metrics.csv",
        "hive_events.csv",
        "coupling_events.csv",
    ],
    A4_TWO_HIVE_NONE_HOLDOUT: [
        *A0_FULL_ARTIFACTS,
        "hive_metrics.csv",
        "cross_hive_metrics.csv",
        "hive_events.csv",
        "coupling_events.csv",
    ],
    A4_TWO_HIVE_DIRECT_HOLDOUT: [
        *A0_FULL_ARTIFACTS,
        "hive_metrics.csv",
        "cross_hive_metrics.csv",
        "hive_events.csv",
        "coupling_events.csv",
    ],
    A4_TWO_HIVE_DELAYED_HOLDOUT: [
        *A0_FULL_ARTIFACTS,
        "hive_metrics.csv",
        "cross_hive_metrics.csv",
        "hive_events.csv",
        "coupling_events.csv",
    ],
    A4_TWO_HIVE_SHUFFLED_HOLDOUT: [
        *A0_FULL_ARTIFACTS,
        "hive_metrics.csv",
        "cross_hive_metrics.csv",
        "hive_events.csv",
        "coupling_events.csv",
    ],
    A5_PREDICTIVE_LINEAR: A0_FULL_ARTIFACTS,
    A6_LOGISTIC_APPRAISAL: A0_FULL_ARTIFACTS,
    A6_LINEAR_APPRAISAL: A0_FULL_ARTIFACTS,
    A6_THRESHOLD_SHUFFLED: A0_FULL_ARTIFACTS,
    A6_PHASE_SHUFFLED: A0_FULL_ARTIFACTS,
    DEFAULT_OUTPUTS: A0_FULL_ARTIFACTS,
    REORDERED_ACTIONS: A0_FULL_ARTIFACTS,
    CONFIG_ONLY: CONFIG_ONLY_ARTIFACTS,
    CONFIG_ONLY_REORDERED_ACTIONS: CONFIG_ONLY_ARTIFACTS,
    MANIFEST_ONLY: MANIFEST_ONLY_ARTIFACTS,
    MANIFEST_ONLY_REORDERED_ACTIONS: MANIFEST_ONLY_ARTIFACTS,
    NO_MANIFEST: NO_MANIFEST_ARTIFACTS,
    NO_MANIFEST_REORDERED_ACTIONS: NO_MANIFEST_ARTIFACTS,
}


def _expected_artifacts(config_path: Path) -> list[str]:
    return list(OUTPUT_FIXTURE_ARTIFACTS[config_path])


def _actions_from_normalized_config(normalized_config: dict[str, object]) -> list[str]:
    model = normalized_config["model"]
    assert isinstance(model, dict)
    actions = model["actions"]
    assert isinstance(actions, list)
    return actions


def _run_documented_cli(
    config_path: Path,
    out_dir: Path,
    *,
    seed: int = 1,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
            "--seed",
            str(seed),
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    return completed


def _run_documented_pressure_cli(
    out_dir: Path,
    *,
    seeds: tuple[int, ...] = (1, 2),
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.compare_pressure",
            "--seeds",
            *(str(seed) for seed in seeds),
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    return completed


def _run_documented_pressure_analysis_cli(
    pressure_dir: Path,
    out_dir: Path,
    *,
    limit: int = 5,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(out_dir),
            "--limit",
            str(limit),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    return completed


def _run_documented_cli_pair(
    config_path: Path,
    tmp_path: Path,
    *,
    first_seed: int,
    second_seed: int,
    first_name: str,
    second_name: str,
) -> tuple[Path, Path, subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    first = tmp_path / first_name
    second = tmp_path / second_name
    artifacts = _expected_artifacts(config_path)

    first_completed = _run_documented_cli(config_path, first, seed=first_seed)
    second_completed = _run_documented_cli(config_path, second, seed=second_seed)

    _assert_artifacts_match_output_directory(first, artifacts)
    _assert_artifacts_match_output_directory(second, artifacts)
    return first, second, first_completed, second_completed


def _replay_a0_lobes_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> list[dict[str, int | str]]:
    rows_by_tick: dict[int, list[dict[str, str]]] = {tick: [] for tick in range(ticks)}
    for row in event_rows:
        rows_by_tick[int(row["tick"])].append(row)

    replay_rows: list[dict[str, int | str]] = []
    previous_label = ""
    run_id = 0
    current_run_length = 0
    queue_depth = 0
    for tick in range(ticks):
        queue_depth_start = queue_depth
        action_counts = Counter(row["action"] for row in rows_by_tick[tick])
        created = action_counts["create_task"]
        completed = sum(
            1
            for row in rows_by_tick[tick]
            if row["event_type"] == "task_worked" and row["completed"] == "True"
        )
        queue_depth = queue_depth_start + created - completed
        label = _replayed_baseline_lobe_label(
            action_counts=action_counts,
            queue_depth_start=queue_depth_start,
            queue_depth_end=queue_depth,
        )
        transition = _replayed_baseline_lobe_transition(previous_label, label)
        if previous_label == label:
            current_run_length += 1
        else:
            run_id += 1
            current_run_length = 1
        replay_rows.append(
            {
                "tick": tick,
                "queue_depth": queue_depth,
                "queue_delta_tick": queue_depth - queue_depth_start,
                "baseline_lobe_label": label,
                "baseline_lobe_previous_label": previous_label,
                "baseline_lobe_transition": transition,
                "baseline_lobe_transition_tick": int(
                    bool(previous_label) and previous_label != label
                ),
                "baseline_lobe_run_id": run_id,
                "baseline_lobe_current_run_length": current_run_length,
            }
        )
        previous_label = label
    return replay_rows


def _replayed_baseline_lobe_label(
    *,
    action_counts: Counter[str],
    queue_depth_start: int,
    queue_depth_end: int,
) -> str:
    queue_delta = queue_depth_end - queue_depth_start
    if (
        queue_depth_end > 0
        and queue_delta > 0
        and action_counts["create_task"] >= action_counts["work_task"]
    ):
        return "backlog_growth"

    priority = ("work_task", "create_task", "message", "idle")
    dominant_action = max(
        priority,
        key=lambda action: (action_counts[action], -priority.index(action)),
    )
    if dominant_action == "work_task":
        return "execution"
    if dominant_action == "create_task":
        return "task_generation"
    if dominant_action == "message":
        return "coordination"
    return "low_activity"


def _replayed_baseline_lobe_transition(previous_label: str, current_label: str) -> str:
    if not previous_label:
        return "start"
    if previous_label == current_label:
        return "stable"
    return f"{previous_label}->{current_label}"


def _replayed_dwell_summary(
    replay_rows: list[dict[str, int | str]],
) -> dict[str, dict[str, int | float]]:
    runs_by_label: dict[str, list[int]] = {label: [] for label in BASELINE_LOBE_LABELS}
    previous_label = ""
    current_run_length = 0
    for row in replay_rows:
        label = str(row["baseline_lobe_label"])
        if label == previous_label:
            current_run_length += 1
        else:
            if previous_label:
                runs_by_label[previous_label].append(current_run_length)
            previous_label = label
            current_run_length = 1
    if previous_label:
        runs_by_label[previous_label].append(current_run_length)

    return {
        label: {
            "runs": len(runs),
            "total_ticks": sum(runs),
            "max_run": max(runs),
            "mean_run": round(sum(runs) / len(runs), 6),
        }
        for label, runs in runs_by_label.items()
        if runs
    }


def test_loads_a0_smoke_config() -> None:
    config = load_config(CONFIG)

    assert config.run.experiment_id == "a0_smoke"
    assert config.run.ticks == 100
    assert config.model.agent_count == 15
    assert config.model.task_creation_pressure == 1.0
    assert config.model.work_service_capacity == 1.0
    assert set(config.model.actions) == {"idle", "message", "create_task", "work_task"}
    assert config.hives == ()
    assert config.coupling is None


def test_automation_guard_reports_closed_state_from_status_and_review(tmp_path: Path) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "- Next step: leave OmegaSim closed at the current A4 boundary unless "
                "a concrete artifact bug is found.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: minor",
                "notify_ben: false",
                "recommended_next_action: Put OmegaSim into an explicit "
                "no-op/awaiting-preregistration state.",
                "",
                "Do not run new simulations or analyzers now.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, tmp_path / "missing-a5.md")

    assert state["state"] == "closed_awaiting_preregistration"
    assert state["should_noop"] is True
    assert state["repo_write_allowed"] is False
    assert state["strategic_change_level"] == "minor"
    assert state["notify_ben"] is False
    assert state["closed_reasons"] == [
        "automation_status_next_step_closed",
        "automation_status_a4_closed",
        "strategy_review_noop_awaiting_preregistration",
        "strategy_review_stop_new_work",
    ]
    assert (
        state["recommended_next_action"]
        == "leave OmegaSim closed at the current A4 boundary unless a concrete "
        "artifact bug is found."
    )
    assert (
        state["review_recommended_next_action"]
        == "Put OmegaSim into an explicit no-op/awaiting-preregistration state."
    )


def test_automation_guard_reports_open_without_closed_status(tmp_path: Path) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    status_path.write_text("# OmegaSim Automation Status\n\n- Next step: run A0 smoke.\n")
    review_path.write_text("strategic_change_level: minor\nnotify_ben: true\n")

    state = read_automation_state(status_path, review_path, tmp_path / "missing-a5.md")

    assert state["state"] == "open"
    assert state["should_noop"] is False
    assert state["repo_write_allowed"] is True
    assert state["closed_reasons"] == []
    assert state["notify_ben"] is True
    assert state["recommended_next_action"] == "run A0 smoke."
    assert state["review_recommended_next_action"] == ""


def test_automation_guard_does_not_close_from_stale_review_only(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    status_path.write_text("# OmegaSim Automation Status\n\n- Next step: run A0 smoke.\n")
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: minor",
                "notify_ben: false",
                "recommended_next_action: Put OmegaSim into an explicit "
                "no-op/awaiting-preregistration state.",
                "",
                "Do not run new simulations or analyzers now.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, tmp_path / "missing-a5.md")

    assert state["state"] == "open"
    assert state["should_noop"] is False
    assert state["closed_reasons"] == []
    assert (
        state["review_recommended_next_action"]
        == "Put OmegaSim into an explicit no-op/awaiting-preregistration state."
    )


def test_automation_guard_prefers_recommended_next_step_section(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "The current focus is A7.",
                "",
                "## Recommended Next Step",
                "",
                "Create the A7 implementation gate: freeze the semantic/artifact",
                "state vector before changing simulator mechanics.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: minor",
                "notify_ben: false",
                "recommended_next_action: Audit the old A6 analyzer.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, tmp_path / "missing-a5.md")

    assert state["state"] == "open"
    assert state["should_noop"] is False
    assert state["recommended_next_action"] == (
        "Create the A7 implementation gate: freeze the semantic/artifact "
        "state vector before changing simulator mechanics."
    )
    assert state["review_recommended_next_action"] == "Audit the old A6 analyzer."


def test_automation_guard_requires_explicit_noop_marker(tmp_path: Path) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    status_path.write_text(
        "# OmegaSim Automation Status\n\n"
        "- Prior guard state observed: closed_awaiting_preregistration.\n"
        "- Next step: run A0 smoke.\n"
    )
    review_path.write_text("strategic_change_level: minor\nnotify_ben: false\n")

    state = read_automation_state(status_path, review_path, tmp_path / "missing-a5.md")

    assert state["state"] == "open"
    assert state["should_noop"] is False
    assert state["closed_reasons"] == []


def test_automation_guard_opens_when_a5_preregistration_exists(tmp_path: Path) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    a5_path = tmp_path / "docs" / "a5_anticipatory_predictive_control_preregistration.md"
    a5_path.parent.mkdir()
    a5_path.write_text("# A5 Anticipatory Predictive-Control Preregistration\n")
    status_path.write_text(
        "# OmegaSim Automation Status\n\n"
        "- Next step: leave OmegaSim closed at the current A4 boundary unless "
        "a concrete artifact bug is found.\n"
        "- Result: state: closed_awaiting_preregistration and should_noop: true.\n"
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: none",
                "notify_ben: false",
                "recommended_next_action: Keep OmegaSim in an explicit "
                "no-op/awaiting-preregistration state.",
                "",
                "Do not run new simulations or analyzers now.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path)

    assert state["state"] == "open"
    assert state["should_noop"] is False
    assert state["closed_reasons"] == []
    assert state["a5_preregistration_active"] is True


def test_a7_semantic_field_contract_freezes_gate_names_and_equations() -> None:
    assert A7_FIELD_VALUES == (
        "semantic_novelty",
        "semantic_coherence",
        "semantic_contradiction",
        "semantic_risk",
        "artifact_readiness",
        "trust_weighted_salience",
    )
    assert A7_PREDICTION_FIELDS == (
        "prediction_budget_spent",
        "prediction_error",
    )
    assert A7_STATE_FIELDS == (*A7_FIELD_VALUES, *A7_PREDICTION_FIELDS)
    assert A7_SOURCE_COMPONENTS == (
        "ambient_decay",
        "self_contribution",
        "peer_contribution",
        "artifact_handoff",
        "prediction_expenditure",
        "prediction_error",
        "queue_work_accounting",
        "semantic_noise",
        "clip_residual",
    )
    assert A7_POSITIVE_CONDITION == "a7_logistic_semantic_coupling"
    assert A7_CONDITIONS == (
        "a7_logistic_semantic_coupling",
        "semantic_off_baseline",
        "amplitude_matched_linear_semantic_coupling",
        "source_preserving_semantic_label_shuffle",
        "semantic_field_phase_shuffle",
        "prediction_budget_timing_broken_matched_count_null",
    )
    assert A7_NULL_CONDITIONS == A7_CONDITIONS[1:]
    assert "queue_depth" in A7_CONTROL_FIELDS
    assert "a7_work_budget_tick" in A7_CONTROL_FIELDS
    assert "a7_delta_prediction_error" in A7_EVENT_FIELDS
    assert any(equation.startswith("linear:") for equation in A7_UTILITY_EQUATIONS)
    assert any(equation.startswith("logistic:") for equation in A7_UTILITY_EQUATIONS)
    assert any(equation.startswith("budget:") for equation in A7_UPDATE_EQUATIONS)
    assert "a7_semantic_novelty_tick" in a7_required_metric_fields()
    assert "a7_prediction_error_mean_tick" in a7_required_metric_fields()
    assert "a7_semantic_field" in a7_required_event_fields()


def test_a7_2_delayed_prediction_contract_freezes_preregistered_schema() -> None:
    assert A7_2_ACTIONS == ("predict", "work", "review", "synthesize")
    assert A7_2_POSITIVE_CONDITION == "intermediate_endogenous_delayed_prediction"
    assert A7_2_CONDITIONS == (
        "zero_budget_reactive",
        "intermediate_endogenous_delayed_prediction",
        "high_budget_oracle_smoothing",
        "amplitude_matched_linear_delayed_prediction",
        "same_tick_logistic_prediction",
        "phase_shuffled_lag_input",
        "threshold_shuffled",
        "source_preserving_artifact_label_shuffle",
        "spend_only_replay",
        "artifact_off_source_ledger_null",
    )
    assert A7_2_NULL_CONDITIONS == (
        "zero_budget_reactive",
        "high_budget_oracle_smoothing",
        "amplitude_matched_linear_delayed_prediction",
        "same_tick_logistic_prediction",
        "phase_shuffled_lag_input",
        "threshold_shuffled",
        "source_preserving_artifact_label_shuffle",
        "spend_only_replay",
        "artifact_off_source_ledger_null",
    )
    assert A7_2_SMOKE_PARAMETERS == {
        "horizon_ticks": 48,
        "forecast_delay_ticks": 2,
        "artifact_delay_ticks": 3,
        "prediction_cost_work_fraction": 0.25,
        "max_prediction_work_fraction_per_tick": 0.40,
        "fatigue_decay": 0.20,
        "fatigue_increment_predict": 0.08,
        "fatigue_increment_work": 0.05,
        "fatigue_increment_review": 0.04,
        "fatigue_increment_synthesize": 0.06,
        "threshold_learning_rate_error": 0.05,
        "threshold_recovery_rate": 0.02,
        "threshold_min": -2.0,
        "threshold_max": 2.0,
        "utility_slope_predict": 1.20,
        "utility_slope_work": 1.00,
        "utility_slope_review": 1.10,
        "utility_slope_synthesize": 1.15,
        "artifact_clip_min": 0.0,
        "artifact_clip_max": 1.0,
        "artifact_decay": 0.10,
    }
    assert "forecast_error_lag1" in A7_2_STATE_FIELDS
    assert "artifact_revision_pressure" in A7_2_STATE_FIELDS
    assert "source_ledger_artifact" in A7_2_SOURCE_LEDGER_FIELDS
    assert "source_ledger_queue_accounting" in A7_2_CONTROL_FIELDS
    assert "forecast_update_visible_tick" in A7_2_EVENT_FIELDS
    assert "lead_lag_mediation_error_to_spend_to_artifact_to_residual" in (
        A7_2_PRIMARY_ENDPOINTS
    )
    assert A7_2_PRODUCTIVITY_GUARDRAILS["completion_fraction_delta_min"] == -0.05
    assert "metrics_rows" in A7_2_COMPARISON_MANIFEST_FIELDS
    assert "source_reconstruction_status" in A7_2_ANALYZER_COMPLETENESS_FIELDS
    assert "forecast_delay_status" in A7_2_ANALYZER_PREFLIGHT_FIELDS
    assert "residual_variance" in A7_2_ANALYZER_RESIDUAL_FIELDS
    assert "gate_status" in A7_2_ANALYZER_NULL_CONTRAST_FIELDS
    assert "status" in A7_2_ANALYZER_GUARDRAIL_FIELDS
    assert "a7_2_forecast_error_lag1" in a7_2_required_metric_fields()
    assert "source_ledger_artifact_risk_delta" in a7_2_required_event_fields()


def test_three_hive_ring_contract_freezes_preregistered_schema() -> None:
    assert THREE_HIVE_RING_HIVES == (
        "hive_a_explore_research",
        "hive_b_formalize_implement",
        "hive_c_synthesize_review",
    )
    assert THREE_HIVE_RING_EDGES == ("A_to_B", "B_to_C", "C_to_A")
    assert THREE_HIVE_RING_EDGE_HIVES == (
        ("hive_a_explore_research", "hive_b_formalize_implement"),
        ("hive_b_formalize_implement", "hive_c_synthesize_review"),
        ("hive_c_synthesize_review", "hive_a_explore_research"),
    )
    assert THREE_HIVE_RING_ACTIONS == (
        "predict_cross_hive",
        "work_local",
        "review_inbound_artifact",
        "synthesize_outbound_artifact",
        "idle",
    )
    assert THREE_HIVE_RING_ROLE_BIASES["hive_a_explore_research"] == (
        "novelty_exploration",
        "contradiction_discovery",
    )
    assert THREE_HIVE_RING_POSITIVE_CONDITION == "delayed_logistic_ring"
    assert THREE_HIVE_RING_CONDITIONS == (
        "no_coupling",
        "delayed_logistic_ring",
        "heterogeneous_delay_logistic_ring",
        "amplitude_matched_linear_delayed_ring",
        "same_tick_logistic_ring",
        "target_shuffled_transfer",
        "phase_shuffled_transfer",
        "threshold_shuffled_ring",
        "transfer_opportunity_matched_replay",
        "spend_only_cross_hive_prediction_replay",
        "artifact_off_source_ledger_null",
        "source_preserving_artifact_label_shuffle",
        "high_budget_oracle_smoothing",
    )
    assert THREE_HIVE_RING_NULL_CONDITIONS == (
        "no_coupling",
        "amplitude_matched_linear_delayed_ring",
        "same_tick_logistic_ring",
        "target_shuffled_transfer",
        "phase_shuffled_transfer",
        "threshold_shuffled_ring",
        "transfer_opportunity_matched_replay",
        "spend_only_cross_hive_prediction_replay",
        "artifact_off_source_ledger_null",
        "source_preserving_artifact_label_shuffle",
    )
    assert THREE_HIVE_RING_SMOKE_PARAMETERS == {
        "seeds": (1, 2),
        "horizon_ticks": 72,
        "ring_hives": 3,
        "ring_edges": ("A_to_B", "B_to_C", "C_to_A"),
        "observation_delay_ticks": 1,
        "transfer_delay_ticks": 3,
        "forecast_delay_ticks": 2,
        "artifact_relaxation_time_ticks": 6,
        "artifact_decay": 0.12,
        "prediction_cost_work_fraction": 0.25,
        "max_prediction_work_fraction_per_tick": 0.35,
        "transfer_cost_work_fraction": 0.15,
        "max_transfer_work_fraction_per_tick": 0.25,
        "fatigue_decay": 0.18,
        "fatigue_increment_predict": 0.08,
        "fatigue_increment_work": 0.05,
        "fatigue_increment_review": 0.04,
        "fatigue_increment_synthesize": 0.06,
        "threshold_learning_rate_error": 0.05,
        "threshold_recovery_rate": 0.02,
        "threshold_min": -2.0,
        "threshold_max": 2.0,
        "utility_slope_cross_predict": 1.15,
        "utility_slope_work": 1.00,
        "utility_slope_review": 1.10,
        "utility_slope_synthesize": 1.15,
        "membrane_permeability": 0.55,
        "artifact_clip_min": 0.0,
        "artifact_clip_max": 1.0,
    }
    assert "artifact_revision_pressure" in THREE_HIVE_RING_STATE_FIELDS
    assert "cross_hive_forecast_uncertainty_lag" in THREE_HIVE_RING_STATE_FIELDS
    assert "membrane_acceptance" in THREE_HIVE_RING_EDGE_FIELDS
    assert "source_ledger_artifact_delta" in THREE_HIVE_RING_SOURCE_LEDGER_FIELDS
    assert "residual_phase_differentiated_motif_score" in (
        THREE_HIVE_RING_PRIMARY_ENDPOINTS
    )
    assert "transfer_opportunity" in THREE_HIVE_RING_RESIDUAL_CONTROLS
    assert "role_bias" in THREE_HIVE_RING_RESIDUAL_CONTROLS
    assert (
        THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS[
            "mean_completion_fraction_min_baseline_ratio"
        ]
        == 0.80
    )
    assert (
        THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS[
            "source_ledger_reconstruction_status_required"
        ]
        == "pass"
    )
    assert "coupling_gain" in THREE_HIVE_RING_DIMENSIONLESS_MANIFEST_FIELDS
    assert "delay_relaxation_ratio" in THREE_HIVE_RING_DIMENSIONLESS_MANIFEST_FIELDS
    assert "local_backlog" in three_hive_ring_required_metric_fields()
    assert "accepted_transfer_volume" in three_hive_ring_required_event_fields()
    assert "source_ledger_clip_residual" in three_hive_ring_required_event_fields()


def test_three_hive_ring_contract_validation_fixture_loads_frozen_schema() -> None:
    config = load_config(THREE_HIVE_RING_CONTRACT_VALIDATION)

    assert config.run.experiment_id == "three_hive_ring_contract_validation"
    assert config.run.ticks == THREE_HIVE_RING_SMOKE_PARAMETERS["horizon_ticks"]
    assert config.three_hive_ring is not None
    assert config.three_hive_ring.conditions == THREE_HIVE_RING_CONDITIONS
    assert config.three_hive_ring.hives == THREE_HIVE_RING_HIVES
    assert tuple(edge.edge_id for edge in config.three_hive_ring.edges) == (
        THREE_HIVE_RING_EDGES
    )
    assert tuple(
        (edge.source_hive, edge.target_hive) for edge in config.three_hive_ring.edges
    ) == THREE_HIVE_RING_EDGE_HIVES
    assert set(THREE_HIVE_RING_ACTIONS).issubset(set(config.model.actions))
    assert config.three_hive_ring.smoke_parameters["ring_edges"] == list(
        THREE_HIVE_RING_EDGES
    )
    assert config.three_hive_ring.smoke_parameters["seeds"] == [1, 2]
    assert config.three_hive_ring.role_biases == THREE_HIVE_RING_ROLE_BIASES
    assert config.three_hive_ring.state_fields == THREE_HIVE_RING_STATE_FIELDS
    assert config.three_hive_ring.edge_fields == THREE_HIVE_RING_EDGE_FIELDS
    assert config.three_hive_ring.source_ledger_fields == (
        THREE_HIVE_RING_SOURCE_LEDGER_FIELDS
    )
    assert config.three_hive_ring.primary_endpoints == THREE_HIVE_RING_PRIMARY_ENDPOINTS
    assert config.three_hive_ring.residual_controls == THREE_HIVE_RING_RESIDUAL_CONTROLS
    assert config.three_hive_ring.productivity_guardrails == (
        THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS
    )
    assert config.hives == ()
    assert config.coupling is None
    assert config.predictive_control is None
    assert config.logistic_appraisal is None
    assert config.semantic_field is None
    assert config.a7_2_delayed_prediction is None


def test_three_hive_ring_contract_validation_fixture_rejects_schema_drift(
    tmp_path: Path,
) -> None:
    raw = yaml.safe_load(THREE_HIVE_RING_CONTRACT_VALIDATION.read_text())
    raw["three_hive_ring"]["conditions"][0] = "renamed_no_coupling"
    bad_path = tmp_path / "bad_three_hive_ring_contract.yaml"
    bad_path.write_text(yaml.safe_dump(raw, sort_keys=True))

    with pytest.raises(ValueError, match="three_hive_ring.conditions"):
        load_config(bad_path)


def test_three_hive_ring_schema_smoke_emits_fixed_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "three_hive_ring_schema_smoke"

    rows = run_three_hive_ring_schema_smoke(out_dir=out_dir)

    assert len(rows) == len(THREE_HIVE_RING_CONDITIONS) * 2
    assert {row["seed"] for row in rows} == {1, 2}
    assert {row["tick_count"] for row in rows} == {
        THREE_HIVE_RING_SMOKE_PARAMETERS["horizon_ticks"]
    }
    assert {row["hive_count"] for row in rows} == {3}
    assert {row["edge_count"] for row in rows} == {3}
    assert {row["artifact_status"] for row in rows} == {
        THREE_HIVE_RING_ARTIFACT_STATUS
    }
    assert {row["scientific_status"] for row in rows} == {
        THREE_HIVE_RING_SCIENTIFIC_STATUS
    }

    manifest_rows = list(
        csv.DictReader((out_dir / "three_hive_ring_schema_smoke_manifest.csv").open())
    )
    assert list(manifest_rows[0]) == list(THREE_HIVE_RING_SCHEMA_SMOKE_MANIFEST_FIELDS)
    assert [row["condition"] for row in manifest_rows[::2]] == list(
        THREE_HIVE_RING_CONDITIONS
    )
    for row in manifest_rows:
        run_dir = out_dir / row["run_dir"]
        assert (run_dir / "config.yaml").exists()
        assert (run_dir / "manifest.yaml").exists()
        assert (run_dir / "metrics_schema.csv").exists()
        assert (run_dir / "events_schema.csv").exists()
        assert (run_dir / "source_ledger_schema.csv").exists()
        metric_fields = list(csv.DictReader((run_dir / "metrics_schema.csv").open()))
        event_fields = list(csv.DictReader((run_dir / "events_schema.csv").open()))
        source_ledger_fields = list(
            csv.DictReader((run_dir / "source_ledger_schema.csv").open())
        )
        assert len(metric_fields) == len(three_hive_ring_required_metric_fields())
        assert len(event_fields) == len(three_hive_ring_required_event_fields())
        assert len(source_ledger_fields) == len(THREE_HIVE_RING_SOURCE_LEDGER_FIELDS)
    assert "schema/source-ledger artifacts only" in (out_dir / "summary.md").read_text()


def test_three_hive_ring_schema_smoke_rejects_unregistered_seeds(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="fixed to paired seeds 1 and 2"):
        run_three_hive_ring_schema_smoke(seeds=(1,), out_dir=tmp_path / "bad")


def test_three_hive_ring_preflight_fails_closed_without_metrics_events(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "three_hive_ring_schema_smoke"
    out_dir = tmp_path / "three_hive_ring_preflight"
    run_three_hive_ring_schema_smoke(out_dir=compare_dir)

    result = run_three_hive_ring_preflight_analysis(
        compare_dir=compare_dir,
        out_dir=out_dir,
    )

    assert result["run_count"] == len(THREE_HIVE_RING_CONDITIONS) * 2
    assert result["status"] == THREE_HIVE_RING_PREFLIGHT_STATUS_NO_METRICS_EVENTS
    manifest_rows = list(
        csv.DictReader((out_dir / "three_hive_ring_preflight_manifest.csv").open())
    )
    assert list(manifest_rows[0]) == list(THREE_HIVE_RING_PREFLIGHT_MANIFEST_FIELDS)
    assert manifest_rows[0]["status"] == THREE_HIVE_RING_PREFLIGHT_STATUS_NO_METRICS_EVENTS
    assert int(manifest_rows[0]["schema_pass_count"]) == len(THREE_HIVE_RING_CONDITIONS) * 2
    assert int(manifest_rows[0]["metrics_events_present_count"]) == 0
    completeness_rows = list(
        csv.DictReader((out_dir / "three_hive_ring_preflight_completeness.csv").open())
    )
    assert list(completeness_rows[0]) == list(
        THREE_HIVE_RING_PREFLIGHT_COMPLETENESS_FIELDS
    )
    assert {row["status"] for row in completeness_rows} == {
        THREE_HIVE_RING_PREFLIGHT_STATUS_NO_METRICS_EVENTS
    }
    assert {row["metrics_events_status"] for row in completeness_rows} == {"absent"}
    assert "does not run the simulator" in (out_dir / "summary.md").read_text()


def test_three_hive_ring_preflight_fails_closed_on_missing_source_ledger_schema(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "three_hive_ring_schema_smoke"
    out_dir = tmp_path / "three_hive_ring_preflight"
    run_three_hive_ring_schema_smoke(out_dir=compare_dir)
    first_run = compare_dir / f"{THREE_HIVE_RING_CONDITIONS[0]}_seed1"
    (first_run / "source_ledger_schema.csv").unlink()

    result = run_three_hive_ring_preflight_analysis(
        compare_dir=compare_dir,
        out_dir=out_dir,
    )

    assert result["status"] == THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SOURCE_LEDGER
    completeness_rows = list(
        csv.DictReader((out_dir / "three_hive_ring_preflight_completeness.csv").open())
    )
    affected = [
        row
        for row in completeness_rows
        if row["condition"] == THREE_HIVE_RING_CONDITIONS[0] and row["seed"] == "1"
    ]
    assert len(affected) == 1
    assert affected[0]["status"] == THREE_HIVE_RING_PREFLIGHT_STATUS_MISSING_SOURCE_LEDGER
    assert "source_ledger_schema.csv" in affected[0]["required_artifact_status"]


def test_three_hive_ring_mechanics_smoke_emits_metrics_events_and_ledgers(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "three_hive_ring_mechanics"

    rows = run_three_hive_ring_mechanics_smoke(out_dir=out_dir)

    assert len(rows) == len(THREE_HIVE_RING_CONDITIONS) * 2
    assert {row["seed"] for row in rows} == {1, 2}
    assert {row["tick_count"] for row in rows} == {
        THREE_HIVE_RING_SMOKE_PARAMETERS["horizon_ticks"]
    }
    assert {row["hive_count"] for row in rows} == {3}
    assert {row["edge_count"] for row in rows} == {3}
    assert {row["metrics_rows"] for row in rows} == {
        THREE_HIVE_RING_SMOKE_PARAMETERS["horizon_ticks"] * 3
    }
    assert {row["events_rows"] for row in rows} == {
        THREE_HIVE_RING_SMOKE_PARAMETERS["horizon_ticks"] * 3
    }
    assert {row["source_ledger_rows"] for row in rows} == {
        THREE_HIVE_RING_SMOKE_PARAMETERS["horizon_ticks"] * 3
    }
    assert {row["mechanics_status"] for row in rows} == {
        THREE_HIVE_RING_MECHANICS_STATUS
    }
    assert {row["scientific_status"] for row in rows} == {
        THREE_HIVE_RING_MECHANICS_SCIENTIFIC_STATUS
    }

    manifest_rows = list(
        csv.DictReader((out_dir / "three_hive_ring_mechanics_manifest.csv").open())
    )
    assert list(manifest_rows[0]) == list(THREE_HIVE_RING_MECHANICS_MANIFEST_FIELDS)
    first_run = out_dir / f"{THREE_HIVE_RING_CONDITIONS[1]}_seed1"
    metric_rows = list(csv.DictReader((first_run / "metrics.csv").open()))
    event_rows = list(csv.DictReader((first_run / "events.csv").open()))
    ledger_rows = list(csv.DictReader((first_run / "source_ledger.csv").open()))
    assert list(metric_rows[0])[:3] == ["condition", "seed", "hive_id"]
    assert set(three_hive_ring_required_metric_fields()).issubset(metric_rows[0])
    assert list(event_rows[0]) == list(three_hive_ring_required_event_fields())
    assert list(ledger_rows[0]) == list(THREE_HIVE_RING_SOURCE_LEDGER_CSV_FIELDS)
    assert {row["selected_action"] for row in metric_rows}.issubset(
        set(THREE_HIVE_RING_ACTIONS)
    )
    assert sum(float(row["accepted_transfer_volume"]) for row in event_rows) > 0.0
    assert "does not compute promotion endpoints" in (out_dir / "summary.md").read_text()


def test_three_hive_ring_mechanics_smoke_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_three_hive_ring_mechanics_smoke(out_dir=first)
    run_three_hive_ring_mechanics_smoke(out_dir=second)

    run_name = f"{THREE_HIVE_RING_CONDITIONS[1]}_seed1"
    assert (first / run_name / "metrics.csv").read_text() == (
        second / run_name / "metrics.csv"
    ).read_text()
    assert (first / run_name / "events.csv").read_text() == (
        second / run_name / "events.csv"
    ).read_text()


def test_three_hive_ring_mechanics_smoke_rejects_unregistered_seeds(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="fixed to paired seeds 1 and 2"):
        run_three_hive_ring_mechanics_smoke(seeds=(1,), out_dir=tmp_path / "bad")


def test_three_hive_ring_preflight_accepts_mechanics_metrics_events(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "three_hive_ring_mechanics"
    out_dir = tmp_path / "three_hive_ring_preflight"
    run_three_hive_ring_mechanics_smoke(out_dir=compare_dir)

    result = run_three_hive_ring_preflight_analysis(
        compare_dir=compare_dir,
        out_dir=out_dir,
    )

    assert result["status"] == THREE_HIVE_RING_PREFLIGHT_STATUS_ELIGIBLE
    manifest_rows = list(
        csv.DictReader((out_dir / "three_hive_ring_preflight_manifest.csv").open())
    )
    assert manifest_rows[0]["status"] == THREE_HIVE_RING_PREFLIGHT_STATUS_ELIGIBLE
    assert int(manifest_rows[0]["metrics_events_present_count"]) == (
        len(THREE_HIVE_RING_CONDITIONS) * 2
    )


def test_three_hive_ring_residual_null_analyzer_fails_closed_on_smoke_artifacts(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "three_hive_ring_mechanics"
    out_dir = tmp_path / "three_hive_ring_residual_null"
    run_three_hive_ring_mechanics_smoke(out_dir=compare_dir)

    result = run_three_hive_ring_residual_null_analysis(
        compare_dir=compare_dir,
        out_dir=out_dir,
    )

    assert result["run_count"] == len(THREE_HIVE_RING_CONDITIONS) * 2
    assert result["status"].startswith("fail_closed_")
    manifest_rows = list(
        csv.DictReader(
            (out_dir / "three_hive_ring_residual_null_manifest.csv").open()
        )
    )
    assert list(manifest_rows[0]) == list(THREE_HIVE_RING_ANALYZER_MANIFEST_FIELDS)
    assert manifest_rows[0]["status"] == result["status"]
    completeness_rows = list(
        csv.DictReader(
            (out_dir / "three_hive_ring_residual_null_completeness.csv").open()
        )
    )
    assert list(completeness_rows[0]) == list(
        THREE_HIVE_RING_ANALYZER_COMPLETENESS_FIELDS
    )
    assert {row["status"] for row in completeness_rows} == {"pass"}
    source_rows = list(
        csv.DictReader(
            (out_dir / "three_hive_ring_residual_null_source_ledger.csv").open()
        )
    )
    assert list(source_rows[0]) == list(THREE_HIVE_RING_ANALYZER_SOURCE_LEDGER_FIELDS)
    assert {row["status"] for row in source_rows} == {"pass"}
    residual_rows = list(
        csv.DictReader((out_dir / "three_hive_ring_residual_null_metrics.csv").open())
    )
    assert list(residual_rows[0]) == list(THREE_HIVE_RING_ANALYZER_RESIDUAL_FIELDS)
    assert {row["status"] for row in residual_rows} == {"computed"}
    contrast_rows = list(
        csv.DictReader(
            (out_dir / "three_hive_ring_residual_null_contrasts.csv").open()
        )
    )
    assert list(contrast_rows[0]) == list(
        THREE_HIVE_RING_ANALYZER_NULL_CONTRAST_FIELDS
    )
    assert {
        row["gate_status"]
        for row in contrast_rows
        if row["gate_status"].startswith("fail_closed")
    }
    guardrail_rows = list(
        csv.DictReader(
            (
                out_dir
                / "three_hive_ring_residual_null_productivity_guardrails.csv"
            ).open()
        )
    )
    assert list(guardrail_rows[0]) == list(
        THREE_HIVE_RING_ANALYZER_GUARDRAIL_FIELDS
    )
    assert "read-only" in (out_dir / "summary.md").read_text()


def test_three_hive_ring_residual_null_analyzer_fails_closed_on_bad_source_ledger(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "three_hive_ring_mechanics"
    out_dir = tmp_path / "three_hive_ring_residual_null"
    run_three_hive_ring_mechanics_smoke(out_dir=compare_dir)
    first_run = compare_dir / f"{THREE_HIVE_RING_POSITIVE_CONDITION}_seed1"
    rows = list(csv.DictReader((first_run / "source_ledger.csv").open()))
    rows[0]["source_ledger_artifact_delta"] = "999.0"
    with (first_run / "source_ledger.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    result = run_three_hive_ring_residual_null_analysis(
        compare_dir=compare_dir,
        out_dir=out_dir,
    )

    assert result["status"] == "fail_closed_source_ledger"
    source_rows = list(
        csv.DictReader(
            (out_dir / "three_hive_ring_residual_null_source_ledger.csv").open()
        )
    )
    affected = [
        row
        for row in source_rows
        if row["condition"] == THREE_HIVE_RING_POSITIVE_CONDITION
        and row["seed"] == "1"
    ]
    assert len(affected) == 1
    assert affected[0]["status"] == "fail_closed"
    assert affected[0]["hive_ledger_status"] == "fail_hive_artifact_delta"


def test_a7_2_configs_load_in_preregistered_condition_order() -> None:
    loaded_conditions = []
    for config_path, condition in zip(A7_2_SMOKE_FIXTURES, A7_2_CONDITIONS, strict=True):
        config = load_config(config_path)
        assert config.run.ticks == A7_2_SMOKE_PARAMETERS["horizon_ticks"]
        assert config.a7_2_delayed_prediction is not None
        loaded_conditions.append(config.a7_2_delayed_prediction.condition)
        assert config.a7_2_delayed_prediction.condition == condition
        assert config.a7_2_delayed_prediction.forecast_delay_ticks == 2
        assert config.a7_2_delayed_prediction.artifact_delay_ticks == 3
        assert config.a7_2_delayed_prediction.prediction_cost_work_fraction == 0.25
        assert config.semantic_field is None
        assert config.predictive_control is None
        assert config.logistic_appraisal is None
        assert config.hives == ()

    assert tuple(loaded_conditions) == A7_2_CONDITIONS


def test_a7_2_config_schema_enforces_no_same_tick_feedback_except_control(
    tmp_path: Path,
) -> None:
    raw = yaml.safe_load(A7_2_INTERMEDIATE_ENDOGENOUS_DELAYED.read_text())
    raw["a7_2_delayed_prediction"]["same_tick_feedback_allowed"] = True
    bad_path = tmp_path / "bad_same_tick.yaml"
    bad_path.write_text(yaml.safe_dump(raw, sort_keys=True))

    with pytest.raises(ValueError, match="same-tick feedback is allowed only"):
        load_config(bad_path)


def test_a7_2_config_schema_requires_spend_only_replay_accounting_flag(
    tmp_path: Path,
) -> None:
    raw = yaml.safe_load(A7_2_SPEND_ONLY_REPLAY.read_text())
    del raw["a7_2_delayed_prediction"][
        "spend_only_replay_preserves_prediction_work_deductions"
    ]
    bad_path = tmp_path / "bad_spend_only.yaml"
    bad_path.write_text(yaml.safe_dump(raw, sort_keys=True))

    with pytest.raises(ValueError, match="preserve prediction-work deductions"):
        load_config(bad_path)


def test_a7_2_config_schema_requires_artifact_off_accounting_flag(
    tmp_path: Path,
) -> None:
    raw = yaml.safe_load(A7_2_ARTIFACT_OFF_SOURCE_LEDGER_NULL.read_text())
    del raw["a7_2_delayed_prediction"][
        "artifact_off_preserves_queue_accounting_controls"
    ]
    bad_path = tmp_path / "bad_artifact_off.yaml"
    bad_path.write_text(yaml.safe_dump(raw, sort_keys=True))

    with pytest.raises(ValueError, match="preserve queue/accounting controls"):
        load_config(bad_path)


def test_a7_2_config_schema_rejects_changed_frozen_parameters(tmp_path: Path) -> None:
    raw = yaml.safe_load(A7_2_INTERMEDIATE_ENDOGENOUS_DELAYED.read_text())
    raw["a7_2_delayed_prediction"]["utility_slope_predict"] = 1.25
    bad_path = tmp_path / "bad_tuned_parameter.yaml"
    bad_path.write_text(yaml.safe_dump(raw, sort_keys=True))

    with pytest.raises(ValueError, match="must remain preregistered at 1.2"):
        load_config(bad_path)


def test_a7_2_smoke_simulator_emits_frozen_contract_fields() -> None:
    config = load_config(A7_2_INTERMEDIATE_ENDOGENOUS_DELAYED)
    result = simulate(config, seed=1)

    assert len(result.metrics) == A7_2_SMOKE_PARAMETERS["horizon_ticks"]
    first_metric = result.metrics[0]
    for field in a7_2_required_metric_fields():
        assert field in first_metric
    assert first_metric["a7_2_selected_action"] in A7_2_ACTIONS
    assert first_metric["a7_2_delayed_forecast_update_queue"] >= 0
    assert first_metric["a7_2_delayed_artifact_update_queue"] >= 0

    a7_2_events = [
        event for event in result.events if event["event_type"] == "a7_2_action_selected"
    ]
    assert a7_2_events
    for field in a7_2_required_event_fields():
        assert field in a7_2_events[0]
    predict_events = [
        event
        for event in a7_2_events
        if event["selected_action"] == "predict"
        and event["forecast_update_created_tick"] != ""
    ]
    assert predict_events
    assert all(
        int(event["forecast_update_visible_tick"])
        - int(event["forecast_update_created_tick"])
        == A7_2_SMOKE_PARAMETERS["forecast_delay_ticks"]
        for event in predict_events
    )


def test_a7_2_delayed_prediction_comparison_runs_fixed_paired_smoke(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a7_2_compare"

    rows = run_a7_2_delayed_prediction_comparison(out_dir=out_dir)

    assert len(rows) == len(A7_2_CONDITIONS) * 2
    assert {row["seed"] for row in rows} == {1, 2}
    assert {row["tick_count"] for row in rows} == {48}
    manifest_rows = list(
        csv.DictReader(
            (out_dir / "a7_2_delayed_prediction_comparison_manifest.csv").open()
        )
    )
    assert list(manifest_rows[0]) == list(A7_2_COMPARISON_MANIFEST_FIELDS)
    assert {row["scientific_status"] for row in manifest_rows} == {
        "bounded_a7_2_smoke_artifacts_only_requires_read_only_analyzer"
    }
    assert [row["condition"] for row in manifest_rows[::2]] == list(A7_2_CONDITIONS)
    for row in manifest_rows:
        run_dir = out_dir / row["run_dir"]
        assert int(row["metrics_rows"]) == 48
        assert int(row["events_rows"]) > 0
        assert (run_dir / "config.yaml").exists()
        assert (run_dir / "manifest.yaml").exists()
        assert (run_dir / "metrics.csv").exists()
        assert (run_dir / "events.csv").exists()
    assert "Horizon: 48 ticks" in (out_dir / "summary.md").read_text()


def test_a7_2_delayed_prediction_comparison_rejects_unregistered_seeds(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="fixed to paired seeds 1 and 2"):
        run_a7_2_delayed_prediction_comparison(seeds=(1,), out_dir=tmp_path / "bad")


def test_a7_3_contract_freezes_required_nulls_and_delay_sources() -> None:
    assert A7_3_POSITIVE_CONDITION == "full_delayed_logistic"
    assert set(A7_3_NULL_CONDITIONS) == set(A7_3_CONDITIONS) - {
        A7_3_POSITIVE_CONDITION
    }
    assert {
        "low_gain_contraction",
        "no_delay_same_tick_blocked",
        "amplitude_matched_linear",
        "artifact_off",
        "cost_free_prediction",
        "spend_only_replay",
        "phase_shuffled_lag",
        "threshold_shuffled",
    }.issubset(A7_3_NULL_CONDITIONS)
    assert tuple(A7_3_DIMENSIONLESS_CONTROLS) == (
        "rho",
        "delta",
        "mu",
        "kappa",
        "nu",
        "chi",
        "eta",
    )
    assert {
        "delayed_agent_role_activity_predict",
        "peer_activity_lag_predict",
        "artifact_readiness",
        "artifact_coherence",
        "contradiction_risk",
        "prediction_error",
        "prediction_uncertainty",
        "adaptive_threshold_predict",
        "lost_work_opportunity_from_prediction",
        "memory_pressure",
        "task_arrivals",
    }.issubset(A7_3_LIFTED_STATE_FIELDS)
    assert {
        "source_ledger_delay_integrity",
        "source_ledger_peer_activity_lag",
        "source_ledger_artifact_memory",
        "source_ledger_prediction_cost",
        "source_ledger_queue_accounting",
        "source_ledger_threshold_update",
    }.issubset(A7_3_SOURCE_LEDGER_FIELDS)
    assert {
        "same_tick_influence_blocked",
        "feedback_created_tick",
        "feedback_visible_tick",
    }.issubset(a7_3_required_event_fields())
    assert set(A7_3_DELAY_SOURCE_INVARIANTS) >= {
        "same_tick_influence_blocked_for_positive_condition",
        "artifact_updates_visible_only_after_feedback_delay",
    }


def test_a7_3_dimensionless_config_loads_frozen_contract() -> None:
    config = load_config(A7_3_DIMENSIONLESS_SMOKE)

    assert config.run.ticks == A7_3_SMOKE_PARAMETERS["horizon_ticks"]
    assert config.a7_3_dimensionless_delayed is not None
    assert config.a7_3_dimensionless_delayed.conditions == A7_3_CONDITIONS
    assert (
        config.a7_3_dimensionless_delayed.smoke_parameters["horizon_ticks"]
        == A7_3_SMOKE_PARAMETERS["horizon_ticks"]
    )
    assert config.a7_3_dimensionless_delayed.lifted_state_fields == A7_3_LIFTED_STATE_FIELDS
    assert config.a7_2_delayed_prediction is None
    assert config.three_hive_ring is None
    assert config.hives == ()


def test_a7_3_config_schema_rejects_changed_frozen_contract(tmp_path: Path) -> None:
    raw = yaml.safe_load(A7_3_DIMENSIONLESS_SMOKE.read_text())
    raw["a7_3_dimensionless_delayed"]["smoke_parameters"]["horizon_ticks"] = 65
    bad_path = tmp_path / "bad_a7_3_contract.yaml"
    bad_path.write_text(yaml.safe_dump(raw, sort_keys=True))

    with pytest.raises(ValueError, match="must match the frozen contract"):
        load_config(bad_path)


def test_a7_3_dimensionless_smoke_emits_lifted_state_and_source_ledger(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a7_3_smoke"

    rows = run_a7_3_dimensionless_smoke(out_dir=out_dir)

    assert len(rows) == len(A7_3_CONDITIONS) * 2
    assert {row["seed"] for row in rows} == {1, 2}
    assert {row["tick_count"] for row in rows} == {64}
    manifest_rows = list(
        csv.DictReader((out_dir / "a7_3_dimensionless_smoke_manifest.csv").open())
    )
    assert list(manifest_rows[0]) == list(A7_3_MECHANICS_MANIFEST_FIELDS)
    assert [row["condition"] for row in manifest_rows[::2]] == list(A7_3_CONDITIONS)
    for row in manifest_rows:
        run_dir = out_dir / row["run_dir"]
        assert int(row["metrics_rows"]) == 64
        assert int(row["events_rows"]) == 64
        assert int(row["source_ledger_rows"]) == 64
        assert int(row["lifted_state_rows"]) == 64
        for artifact in (
            "config.yaml",
            "manifest.yaml",
            "metrics.csv",
            "events.csv",
            "source_ledger.csv",
            "lifted_state.csv",
            "metrics_schema.csv",
            "events_schema.csv",
            "source_ledger_schema.csv",
            "lifted_state_schema.csv",
        ):
            assert (run_dir / artifact).exists()
    full_run = out_dir / "full_delayed_logistic_seed1"
    first_metric = next(csv.DictReader((full_run / "metrics.csv").open()))
    for field in a7_3_required_metric_fields():
        assert field in first_metric
    assert first_metric["source_ledger_delay_integrity"] == "pass"
    first_event = next(csv.DictReader((full_run / "events.csv").open()))
    assert first_event["same_tick_influence_blocked"] == "True"
    no_delay_metric = next(
        csv.DictReader((out_dir / "no_delay_same_tick_blocked_seed1" / "metrics.csv").open())
    )
    assert no_delay_metric["source_ledger_delay_integrity"] == "control_no_delay"
    assert "Horizon: 64 ticks" in (out_dir / "summary.md").read_text()


def test_a7_3_dimensionless_smoke_rejects_unregistered_seeds(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="fixed to paired seeds 1 and 2"):
        run_a7_3_dimensionless_smoke(seeds=(1,), out_dir=tmp_path / "bad")


def test_a7_3_preflight_analyzer_accepts_complete_smoke_artifacts(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a7_3_smoke"
    out_dir = tmp_path / "a7_3_preflight"
    run_a7_3_dimensionless_smoke(out_dir=compare_dir)

    result = run_a7_3_preflight_analysis(compare_dir=compare_dir, out_dir=out_dir)

    assert result["status"] == A7_3_PREFLIGHT_STATUS_ELIGIBLE
    manifest_rows = list(csv.DictReader((out_dir / "a7_3_preflight_manifest.csv").open()))
    assert manifest_rows[0]["status"] == A7_3_PREFLIGHT_STATUS_ELIGIBLE
    assert int(manifest_rows[0]["observed_run_count"]) == len(A7_3_CONDITIONS) * 2
    assert int(manifest_rows[0]["completeness_pass_count"]) == len(A7_3_CONDITIONS) * 2
    source_rows = list(csv.DictReader((out_dir / "a7_3_preflight_source_ledger.csv").open()))
    assert {row["status"] for row in source_rows} == {"pass"}
    guardrail_rows = list(csv.DictReader((out_dir / "a7_3_preflight_guardrails.csv").open()))
    assert {row["status"] for row in guardrail_rows} == {"pass"}
    assert "does not rerun simulations" in (out_dir / "summary.md").read_text()


def test_a7_3_preflight_analyzer_fails_closed_on_source_ledger_leakage(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a7_3_smoke"
    out_dir = tmp_path / "a7_3_preflight"
    run_a7_3_dimensionless_smoke(out_dir=compare_dir)
    event_path = compare_dir / "full_delayed_logistic_seed1" / "events.csv"
    rows = list(csv.DictReader(event_path.open()))
    rows[0]["feedback_visible_tick"] = rows[0]["feedback_created_tick"]
    with event_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    result = run_a7_3_preflight_analysis(compare_dir=compare_dir, out_dir=out_dir)

    assert result["status"] == A7_3_PREFLIGHT_STATUS_SOURCE_LEDGER
    source_rows = list(csv.DictReader((out_dir / "a7_3_preflight_source_ledger.csv").open()))
    full_row = next(
        row
        for row in source_rows
        if row["condition"] == "full_delayed_logistic" and row["seed"] == "1"
    )
    assert full_row["status"] == "fail_closed"
    assert full_row["delay_integrity_status"] == "fail_same_tick_leakage"


def test_a7_3_preflight_analyzer_reconstructs_delayed_lag_sources(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a7_3_smoke"
    out_dir = tmp_path / "a7_3_preflight"
    run_a7_3_dimensionless_smoke(out_dir=compare_dir)
    metrics_path = compare_dir / "full_delayed_logistic_seed1" / "metrics.csv"
    rows = list(csv.DictReader(metrics_path.open()))
    rows[4]["delayed_agent_role_activity_predict"] = rows[4][
        "agent_role_activity_predict"
    ]
    with metrics_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    result = run_a7_3_preflight_analysis(compare_dir=compare_dir, out_dir=out_dir)

    assert result["status"] == A7_3_PREFLIGHT_STATUS_SOURCE_LEDGER
    source_rows = list(csv.DictReader((out_dir / "a7_3_preflight_source_ledger.csv").open()))
    full_row = next(
        row
        for row in source_rows
        if row["condition"] == "full_delayed_logistic" and row["seed"] == "1"
    )
    assert full_row["status"] == "fail_closed"
    assert full_row["peer_lag_status"] == "fail_delayed_role_reconstruction"


def test_a7_3_residual_skeleton_requires_eligible_preflight_and_stays_fail_closed(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a7_3_smoke"
    preflight_dir = tmp_path / "a7_3_preflight"
    out_dir = tmp_path / "a7_3_residual"
    run_a7_3_dimensionless_smoke(out_dir=compare_dir)
    run_a7_3_preflight_analysis(compare_dir=compare_dir, out_dir=preflight_dir)

    result = run_a7_3_residual_skeleton_analysis(
        compare_dir=compare_dir,
        preflight_dir=preflight_dir,
        out_dir=out_dir,
    )

    assert result["status"] == A7_3_RESIDUAL_STATUS_SMOKE_SCALE
    manifest_rows = list(
        csv.DictReader((out_dir / "a7_3_residual_skeleton_manifest.csv").open())
    )
    assert manifest_rows[0]["preflight_status"] == A7_3_PREFLIGHT_STATUS_ELIGIBLE
    assert manifest_rows[0]["status"] == A7_3_RESIDUAL_STATUS_SMOKE_SCALE
    metric_rows = list(
        csv.DictReader((out_dir / "a7_3_residual_skeleton_metrics.csv").open())
    )
    assert {row["status"] for row in metric_rows} == {A7_3_RESIDUAL_STATUS_SMOKE_SCALE}
    assert {row["preflight_status"] for row in metric_rows} == {
        A7_3_PREFLIGHT_STATUS_ELIGIBLE
    }
    assert all(float(row["delay_embedded_recurrence_rate"]) == 0.0 for row in metric_rows)
    contrast_rows = list(
        csv.DictReader((out_dir / "a7_3_residual_skeleton_contrasts.csv").open())
    )
    assert len(contrast_rows) == len(A7_3_NULL_CONDITIONS) * 2 * 8
    assert {row["gate_status"] for row in contrast_rows} == {
        A7_3_RESIDUAL_STATUS_SMOKE_SCALE
    }
    assert "no promotion endpoint" in (out_dir / "summary.md").read_text()


def test_a7_3_residual_skeleton_fails_closed_without_preflight(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a7_3_smoke"
    out_dir = tmp_path / "a7_3_residual"
    run_a7_3_dimensionless_smoke(out_dir=compare_dir)

    result = run_a7_3_residual_skeleton_analysis(
        compare_dir=compare_dir,
        preflight_dir=tmp_path / "missing_preflight",
        out_dir=out_dir,
    )

    assert result["status"] == A7_3_RESIDUAL_STATUS_PREFLIGHT_REQUIRED
    manifest_rows = list(
        csv.DictReader((out_dir / "a7_3_residual_skeleton_manifest.csv").open())
    )
    assert manifest_rows[0]["preflight_status"] == "missing_preflight_manifest"
    metric_rows = list(
        csv.DictReader((out_dir / "a7_3_residual_skeleton_metrics.csv").open())
    )
    assert {row["status"] for row in metric_rows} == {
        A7_3_RESIDUAL_STATUS_PREFLIGHT_REQUIRED
    }


def test_a7_2_delayed_prediction_analyzer_fails_closed_on_missing_schema(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a7_2_compare"
    run_dir = compare_dir / "intermediate_endogenous_delayed_prediction_seed1"
    out_dir = tmp_path / "a7_2_analysis"
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.yaml").write_text(
        yaml.safe_dump(
            {
                "seed": 1,
                "config": {
                    "a7_2_delayed_prediction": {
                        "condition": "intermediate_endogenous_delayed_prediction",
                    }
                },
            },
            sort_keys=True,
        )
    )
    (run_dir / "metrics.csv").write_text("tick,queue_depth\n0,1\n")
    (run_dir / "events.csv").write_text("tick,event_type\n0,task_created\n")

    result = run_a7_2_delayed_prediction_analysis(compare_dir, out_dir)

    assert result["status"] == "fail_closed_missing_conditions"
    completeness_rows = list(
        csv.DictReader((out_dir / "a7_2_delayed_prediction_completeness.csv").open())
    )
    manifest_rows = list(
        csv.DictReader((out_dir / "a7_2_delayed_prediction_manifest.csv").open())
    )
    preflight_rows = list(
        csv.DictReader((out_dir / "a7_2_delayed_prediction_preflight.csv").open())
    )
    residual_rows = list(
        csv.DictReader((out_dir / "a7_2_delayed_prediction_residual_metrics.csv").open())
    )
    guardrail_rows = list(
        csv.DictReader(
            (out_dir / "a7_2_delayed_prediction_productivity_guardrails.csv").open()
        )
    )
    assert list(completeness_rows[0]) == list(A7_2_ANALYZER_COMPLETENESS_FIELDS)
    assert list(manifest_rows[0]) == list(A7_2_ANALYZER_MANIFEST_FIELDS)
    assert list(preflight_rows[0]) == list(A7_2_ANALYZER_PREFLIGHT_FIELDS)
    assert list(residual_rows[0]) == list(A7_2_ANALYZER_RESIDUAL_FIELDS)
    assert list(guardrail_rows[0]) == list(A7_2_ANALYZER_GUARDRAIL_FIELDS)
    assert completeness_rows[0]["status"] == "fail_closed"
    assert "a7_2_forecast_error_lag1" in completeness_rows[0]["missing_required_fields"]
    assert manifest_rows[0]["status"] == "fail_closed_missing_conditions"
    assert "Positive interpretation remains blocked" in (
        out_dir / "summary.md"
    ).read_text()


def test_a7_2_delayed_prediction_analyzer_reports_fixed_smoke_preflight(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a7_2_compare"
    analysis_dir = tmp_path / "a7_2_analysis"
    run_a7_2_delayed_prediction_comparison(out_dir=compare_dir)

    result = run_a7_2_delayed_prediction_analysis(compare_dir, analysis_dir)

    assert result["run_count"] == len(A7_2_CONDITIONS) * 2
    assert result["seed_count"] == 2
    assert result["condition_count"] == len(A7_2_CONDITIONS)
    assert result["status"].startswith("fail_closed_") or result["status"].startswith(
        "computed_"
    )
    completeness_rows = list(
        csv.DictReader((analysis_dir / "a7_2_delayed_prediction_completeness.csv").open())
    )
    preflight_rows = list(
        csv.DictReader((analysis_dir / "a7_2_delayed_prediction_preflight.csv").open())
    )
    residual_rows = list(
        csv.DictReader(
            (analysis_dir / "a7_2_delayed_prediction_residual_metrics.csv").open()
        )
    )
    contrast_rows = list(
        csv.DictReader(
            (analysis_dir / "a7_2_delayed_prediction_null_contrasts.csv").open()
        )
    )
    guardrail_rows = list(
        csv.DictReader(
            (analysis_dir / "a7_2_delayed_prediction_productivity_guardrails.csv").open()
        )
    )
    assert {row["status"] for row in completeness_rows} == {"pass"}
    assert {row["source_reconstruction_status"] for row in completeness_rows} == {"pass"}
    assert len(preflight_rows) == len(A7_2_CONDITIONS) * 2
    assert all(int(row["varying_state_field_count"]) > 0 for row in preflight_rows)
    assert all(row["forecast_delay_status"] in {"pass", "no_predict_events"} for row in preflight_rows)
    assert all(row["artifact_delay_status"] in {"pass", "no_artifact_events"} for row in preflight_rows)
    assert {row["scientific_interpretation_status"] for row in preflight_rows} == {
        "preflight_only_no_a7_2_promotion_claim"
    }
    assert list(residual_rows[0]) == list(A7_2_ANALYZER_RESIDUAL_FIELDS)
    assert len(residual_rows) == len(A7_2_CONDITIONS) * 2 * 7
    assert {row["status"] for row in residual_rows} == {"computed"}
    assert list(contrast_rows[0]) == list(A7_2_ANALYZER_NULL_CONTRAST_FIELDS)
    assert len(contrast_rows) == len(A7_2_NULL_CONDITIONS) * 2 * 7
    assert list(guardrail_rows[0]) == list(A7_2_ANALYZER_GUARDRAIL_FIELDS)
    assert len(guardrail_rows) == len(A7_2_NULL_CONDITIONS) * 2
    assert "read-only" in (analysis_dir / "summary.md").read_text()


def test_a7_analyzer_fails_closed_on_missing_schema(tmp_path: Path) -> None:
    compare_dir = tmp_path / "a7_compare"
    run_dir = compare_dir / "a7_logistic_semantic_coupling_seed1"
    out_dir = tmp_path / "a7_analysis"
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.yaml").write_text(
        yaml.safe_dump(
            {
                "seed": 1,
                "config": {
                    "semantic_field": {
                        "condition": "a7_logistic_semantic_coupling",
                    }
                },
            },
            sort_keys=True,
        )
    )
    (run_dir / "metrics.csv").write_text("tick,queue_depth\n0,1\n")
    (run_dir / "events.csv").write_text("tick,event_type\n0,task_created\n")

    result = run_a7_semantic_field_analysis(compare_dir, out_dir)

    assert result["status"] == "fail_closed_missing_conditions"
    completeness_rows = list(
        csv.DictReader((out_dir / "a7_semantic_field_completeness.csv").open())
    )
    manifest_rows = list(
        csv.DictReader((out_dir / "a7_semantic_field_manifest.csv").open())
    )
    assert list(completeness_rows[0]) == list(A7_ANALYZER_COMPLETENESS_FIELDS)
    assert list(manifest_rows[0]) == list(A7_ANALYZER_MANIFEST_FIELDS)
    smoke_rows = list(
        csv.DictReader((out_dir / "a7_semantic_field_smoke_report.csv").open())
    )
    assert list(smoke_rows[0]) == list(A7_ANALYZER_SMOKE_REPORT_FIELDS)
    assert completeness_rows[0]["status"] == "fail_closed"
    assert completeness_rows[0]["required_field_status"] == "missing_fields"
    assert "a7_semantic_novelty_tick" in completeness_rows[0]["missing_required_fields"]
    assert "a7_delta_total" in completeness_rows[0]["missing_required_fields"]
    assert manifest_rows[0]["status"] == "fail_closed_missing_conditions"
    assert "Positive interpretation remains blocked" in (
        out_dir / "summary.md"
    ).read_text()


def test_a7_placeholder_comparison_writes_configs_and_manifests_only(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a7_placeholder_compare"

    rows = run_a7_semantic_field_placeholder_comparison(
        seeds=(1, 2),
        out_dir=out_dir,
    )

    assert len(rows) == len(A7_CONDITIONS) * 2
    assert [row["condition"] for row in rows[::2]] == list(A7_CONDITIONS)
    placeholder_rows = list(
        csv.DictReader((out_dir / "a7_semantic_field_placeholder_manifest.csv").open())
    )
    assert list(placeholder_rows[0]) == list(A7_PLACEHOLDER_MANIFEST_FIELDS)
    assert {row["placeholder_status"] for row in placeholder_rows} == {
        "config_manifest_only"
    }
    assert {row["scientific_status"] for row in placeholder_rows} == {
        "no_simulator_mechanics_no_a7_evidence"
    }

    for condition in A7_CONDITIONS:
        generated_config = out_dir / "configs" / f"{condition}.yaml"
        assert generated_config.exists()
        generated = yaml.safe_load(generated_config.read_text())
        assert generated["semantic_field"]["condition"] == condition
        for seed in (1, 2):
            run_dir = out_dir / f"{condition}_seed{seed}"
            assert (run_dir / "config.yaml").exists()
            assert (run_dir / "manifest.yaml").exists()
            assert (run_dir / "summary.md").exists()
            assert not (run_dir / "metrics.csv").exists()
            assert not (run_dir / "events.csv").exists()
            manifest = yaml.safe_load((run_dir / "manifest.yaml").read_text())
            assert manifest["seed"] == seed
            assert manifest["a7_semantic_field"]["condition"] == condition
            assert manifest["a7_semantic_field"]["simulator_mechanics_touched"] is False
            assert manifest["scientific_status"] == "no_simulator_mechanics_no_a7_evidence"
            assert manifest["artifacts"] == ["config.yaml", "manifest.yaml", "summary.md"]

    assert "does not run" in (out_dir / "summary.md").read_text()


def test_a7_placeholder_comparison_still_fails_closed_in_analyzer(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a7_placeholder_compare"
    analysis_dir = tmp_path / "a7_placeholder_analysis"
    run_a7_semantic_field_placeholder_comparison(seeds=(1,), out_dir=compare_dir)

    result = run_a7_semantic_field_analysis(compare_dir, analysis_dir)

    assert result["status"] == "fail_closed_missing_schema"
    completeness_rows = list(
        csv.DictReader((analysis_dir / "a7_semantic_field_completeness.csv").open())
    )
    assert len(completeness_rows) == len(A7_CONDITIONS)
    assert {row["status"] for row in completeness_rows} == {"fail_closed"}
    assert all(row["row_count"] == "0" for row in completeness_rows)
    smoke_rows = list(
        csv.DictReader((analysis_dir / "a7_semantic_field_smoke_report.csv").open())
    )
    residual_rows = list(
        csv.DictReader((analysis_dir / "a7_semantic_field_residual_metrics.csv").open())
    )
    contrast_rows = list(
        csv.DictReader((analysis_dir / "a7_semantic_field_null_contrasts.csv").open())
    )
    assert len(smoke_rows) == len(A7_CONDITIONS)
    assert {row["field_variation_status"] for row in smoke_rows} == {
        "no_field_variation"
    }
    assert {row["scientific_interpretation_status"] for row in smoke_rows} == {
        "fail_closed_residual_recurrence_and_null_contrasts_not_implemented"
    }
    assert len(residual_rows) == len(A7_CONDITIONS) * len(A7_FIELD_VALUES)
    assert list(residual_rows[0]) == list(A7_ANALYZER_RESIDUAL_FIELDS)
    assert {row["status"] for row in residual_rows} == {"missing_required_fields"}
    assert len(contrast_rows) == len(A7_NULL_CONDITIONS) * len(A7_FIELD_VALUES)
    assert list(contrast_rows[0]) == list(A7_ANALYZER_NULL_CONTRAST_FIELDS)
    assert {row["gate_status"] for row in contrast_rows} == {"missing_required_fields"}


def test_a7_long_horizon_configs_are_fixed_validation_derivatives() -> None:
    assert len(DEFAULT_A7_LONG_HORIZON_CONFIGS) == len(A7_CONDITIONS)
    for config_path, condition in zip(
        DEFAULT_A7_LONG_HORIZON_CONFIGS,
        A7_CONDITIONS,
        strict=True,
    ):
        config = load_config(config_path)
        source = load_config(A7_SMOKE_FIXTURES[A7_CONDITIONS.index(condition)])
        assert config.run.ticks == 96
        assert config.run.experiment_id.startswith("a7_long_horizon_")
        assert config.semantic_field is not None
        assert source.semantic_field is not None
        assert config.semantic_field.condition == condition
        assert config.model == source.model
        assert config.outputs == source.outputs
        assert config.semantic_field == source.semantic_field


def test_a7_long_horizon_comparison_runs_fixed_paired_validation(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a7_long_horizon_compare"

    rows = run_a7_semantic_field_comparison(out_dir=out_dir)

    assert len(rows) == len(A7_CONDITIONS) * 2
    assert {row["seed"] for row in rows} == {1, 2}
    assert {row["tick_count"] for row in rows} == {96}
    manifest_rows = list(
        csv.DictReader((out_dir / "a7_semantic_field_comparison_manifest.csv").open())
    )
    assert list(manifest_rows[0]) == list(A7_COMPARISON_MANIFEST_FIELDS)
    assert {row["scientific_status"] for row in manifest_rows} == {
        "bounded_validation_artifacts_only_requires_read_only_analyzer"
    }
    for row in manifest_rows:
        run_dir = out_dir / row["run_dir"]
        assert int(row["metrics_rows"]) == 96
        assert int(row["events_rows"]) > 0
        assert (run_dir / "config.yaml").exists()
        assert (run_dir / "manifest.yaml").exists()
        assert (run_dir / "metrics.csv").exists()
        assert (run_dir / "events.csv").exists()
    assert "Horizon: 96 ticks" in (out_dir / "summary.md").read_text()


def test_a7_long_horizon_comparison_rejects_unregistered_seeds(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="fixed to paired seeds 1 and 2"):
        run_a7_semantic_field_comparison(seeds=(1,), out_dir=tmp_path / "bad")


def test_a7_logistic_semantic_field_run_emits_schema_and_source_ledger(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a7_logistic_seed1"

    result = run_experiment(A7_LOGISTIC_SEMANTIC_COUPLING, seed=1, out_dir=out_dir)

    assert result.config.semantic_field is not None
    assert result.config.semantic_field.condition == A7_POSITIVE_CONDITION
    with (out_dir / "metrics.csv").open(newline="") as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open(newline="") as handle:
        event_rows = list(csv.DictReader(handle))
    assert metric_rows
    assert event_rows
    metrics_header = set(metric_rows[0])
    events_header = set(event_rows[0])
    assert set(a7_required_metric_fields()).issubset(metrics_header)
    assert set(a7_required_event_fields()).issubset(events_header)
    for field in semantic_field_metric_fields():
        assert field in metrics_header

    semantic_updates = [
        row for row in event_rows if row["event_type"] == "a7_semantic_field_update"
    ]
    assert semantic_updates
    assert {row["a7_condition"] for row in semantic_updates} == {A7_POSITIVE_CONDITION}
    for row in semantic_updates:
        source_sum = sum(
            float(row[f"a7_delta_{source}"] or 0.0)
            for source in A7_SOURCE_COMPONENTS
        )
        assert round(source_sum, 6) == round(float(row["a7_delta_total"]), 6)

    novelty_values = [float(row["a7_semantic_novelty_tick"]) for row in metric_rows]
    assert max(novelty_values) != min(novelty_values)
    assert any(float(row["a7_prediction_budget_spent_tick"]) > 0.0 for row in metric_rows)
    assert any(
        float(row["a7_work_budget_tick"]) < float(row["a7_action_opportunity_tick"])
        for row in metric_rows
    )
    assert any(float(row["a7_near_threshold_occupancy_tick"]) >= 0.0 for row in metric_rows)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["model"]["semantic_field"]["execution_mode"] == (
        "real_simulator_schema_smoke"
    )
    assert manifest["model"]["semantic_field"]["scientific_status"] == (
        "schema_complete_smoke_only_no_semantic_dynamics_claim"
    )


def test_a7_analyzer_reports_seed1_six_condition_smoke_without_interpretation(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a7_seed1_smoke"
    analysis_dir = tmp_path / "a7_seed1_analysis"
    for config_path, condition in zip(A7_SMOKE_FIXTURES, A7_CONDITIONS, strict=True):
        run_experiment(
            config_path,
            seed=1,
            out_dir=compare_dir / f"{condition}_seed1",
        )

    result = run_a7_semantic_field_analysis(compare_dir, analysis_dir)

    assert result["status"] == "fail_closed_insufficient_horizon"
    smoke_rows = list(
        csv.DictReader((analysis_dir / "a7_semantic_field_smoke_report.csv").open())
    )
    residual_rows = list(
        csv.DictReader((analysis_dir / "a7_semantic_field_residual_metrics.csv").open())
    )
    contrast_rows = list(
        csv.DictReader((analysis_dir / "a7_semantic_field_null_contrasts.csv").open())
    )
    assert list(smoke_rows[0]) == list(A7_ANALYZER_SMOKE_REPORT_FIELDS)
    assert len(smoke_rows) == len(A7_CONDITIONS)
    assert {row["condition"] for row in smoke_rows} == set(A7_CONDITIONS)
    assert {row["source_reconstruction_status"] for row in smoke_rows} == {"pass"}
    assert all(int(row["varying_field_count"]) > 0 for row in smoke_rows)
    assert any(
        row["prediction_work_budget_competition_status"] == "pass"
        for row in smoke_rows
    )
    assert all(
        row["near_threshold_occupancy_status"] == "measured" for row in smoke_rows
    )
    assert {row["scientific_interpretation_status"] for row in smoke_rows} == {
        "fail_closed_residual_recurrence_and_null_contrasts_not_implemented"
    }
    assert list(residual_rows[0]) == list(A7_ANALYZER_RESIDUAL_FIELDS)
    assert len(residual_rows) == len(A7_CONDITIONS) * len(A7_FIELD_VALUES)
    assert {row["status"] for row in residual_rows} == {"insufficient_horizon"}
    assert all(row["control_fields_used"] for row in residual_rows)
    assert list(contrast_rows[0]) == list(A7_ANALYZER_NULL_CONTRAST_FIELDS)
    assert len(contrast_rows) == len(A7_NULL_CONDITIONS) * len(A7_FIELD_VALUES)
    assert {row["gate_status"] for row in contrast_rows} == {"insufficient_horizon"}
    summary = (analysis_dir / "summary.md").read_text()
    assert "Prediction/work-budget competition pass rows" in summary
    assert "Null-contrast gate status" in summary


def test_automation_guard_closes_after_a5_closure_despite_preregistration(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    a5_path = tmp_path / "docs" / "a5_anticipatory_predictive_control_preregistration.md"
    a5_path.parent.mkdir()
    a5_path.write_text("# A5 Anticipatory Predictive-Control Preregistration\n")
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "The current A5 anticipatory predictive-control loop is closed.",
                "",
                "- Status: A5 closure note, 2026-06-26.",
                "- Result: Do not reopen A5 for more mechanics or larger seed sweeps "
                "from this result alone.",
                "- Recommended next step: remain in no-op/awaiting-preregistration "
                "state unless a concrete artifact/analyzer bug is found or Ben "
                "explicitly requests a new preregistered OmegaSim design.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: minor",
                "notify_ben: false",
                "recommended_next_action: Preregister guardrails before fresh A5.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path)

    assert state["state"] == "closed_awaiting_preregistration"
    assert state["should_noop"] is True
    assert state["closed_reasons"] == [
        "automation_status_next_step_noop",
        "automation_status_a5_closed",
    ]
    assert state["a5_preregistration_active"] is True
    assert state["recommended_next_action"] == (
        "remain in no-op/awaiting-preregistration state unless a concrete "
        "artifact/analyzer bug is found or Ben explicitly requests a new "
        "preregistered OmegaSim design."
    )
    assert state["review_recommended_next_action"] == (
        "Preregister guardrails before fresh A5."
    )


def test_automation_guard_closes_for_current_a5_status_wording(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    a5_path = tmp_path / "docs" / "a5_anticipatory_predictive_control_preregistration.md"
    a5_path.parent.mkdir()
    a5_path.write_text("# A5 Anticipatory Predictive-Control Preregistration\n")
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "The current A5 anticipatory predictive-control loop is closed "
                "against the fresh seed `7..16` confirmatory evidence.",
                "",
                "- Status: A5 preregistration/scaffold refresh completed, "
                "2026-06-26T22:59Z.",
                "- Result: A5 remains frozen against the seed `7..16` "
                "confirmatory evidence.",
                "- Recommended next step: have Ben decide whether A5 should stay "
                "closed or receive a new preregistered post-closure design target.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: none",
                "notify_ben: false",
                "recommended_next_action: Remain in no-op/awaiting-preregistration "
                "state and do not run new simulations or analyzers unless Ben "
                "requests a new preregistered design or a concrete "
                "artifact/analyzer bug is found.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path)

    assert state["state"] == "closed_awaiting_preregistration"
    assert state["should_noop"] is True
    assert state["closed_reasons"] == [
        "automation_status_a5_loop_closed",
    ]
    assert state["recommended_next_action"] == (
        "have Ben decide whether A5 should stay closed or receive a new "
        "preregistered post-closure design target."
    )


def test_automation_guard_reopens_for_explicit_current_a5_preregistration(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    a5_path = tmp_path / "docs" / "a5_anticipatory_predictive_control_preregistration.md"
    a5_path.parent.mkdir()
    a5_path.write_text("# A5 Anticipatory Predictive-Control Preregistration\n")
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "Historical note: Recommended next step: remain in "
                "no-op/awaiting-preregistration state.",
                "",
                "Current concise A5 gate: "
                "`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.",
                "That document records the 2026-06-27 explicit single-hive A5 "
                "reopening and is the active preregistration summary for the "
                "bounded smoke/pilot.",
                "",
                "## Recommended Next Step",
                "",
                "- Recommended next step: run the bounded A5 single-hive smoke.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: major",
                "notify_ben: true",
                "recommended_next_action: Do not broaden A5.1.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path)

    assert state["state"] == "open"
    assert state["should_noop"] is False
    assert state["closed_reasons"] == []
    assert state["recommended_next_action"] == "run the bounded A5 single-hive smoke."


def test_automation_guard_ignores_historical_a5_closure_when_current_gate_reopens(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    roadmap_path = tmp_path / "docs" / "omegasim_provisional_experiment_roadmap.md"
    a5_path = (
        tmp_path
        / "docs"
        / "a5_single_hive_anticipatory_predictive_control_preregistration.md"
    )
    a5_path.parent.mkdir()
    a5_path.write_text("# A5 Single-Hive Anticipatory Predictive-Control Preregistration\n")
    roadmap_path.write_text(
        "\n".join(
            [
                "# OmegaSim Provisional Experiment Roadmap",
                "",
                "Accepted by Ben on 2026-06-27.",
                "",
                "Update 2026-06-27: A6/A6.1/A6.2 are now closed conservatively. "
                "Ben accepted proceeding to A7 as the next preregistered direction.",
                "",
                "This roadmap replaces the closed A5 no-op posture as the "
                "provisional direction for OmegaSim experimentation.",
                "",
                "## Immediate Next Step",
                "",
                "Create an A7 implementation gate before any broad experiment.",
            ]
        )
    )
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "## Current Focus",
                "",
                "Current concise A5 gate: "
                "`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.",
                "That document records the 2026-06-27 explicit single-hive A5 "
                "reopening and is the active preregistration summary for the "
                "bounded smoke/pilot.",
                "",
                "## Latest Changes",
                "",
                "- Historical closure note: do not reopen A5 without a new explicit "
                "preregistration.",
                "- Historical verification: the reopened A5 smoke remained "
                "fail-closed.",
                "",
                "## Recommended Next Step",
                "",
                "- Recommended next step: run the bounded A5 single-hive smoke.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: major",
                "notify_ben: true",
                "recommended_next_action: Keep old A5 closed.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path, roadmap_path)

    assert state["state"] == "open"
    assert state["should_noop"] is False
    assert state["closed_reasons"] == []
    assert state["a5_preregistration_active"] is True
    assert state["recommended_next_action"] == "run the bounded A5 single-hive smoke."


def test_automation_guard_closes_after_reopened_a5_smoke_fail_closed(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    a5_path = tmp_path / "docs" / "a5_anticipatory_predictive_control_preregistration.md"
    a5_path.parent.mkdir()
    a5_path.write_text("# A5 Anticipatory Predictive-Control Preregistration\n")
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "Current concise A5 gate: "
                "`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.",
                "That document records the 2026-06-27 explicit single-hive A5 "
                "reopening and is the active preregistration summary for the "
                "bounded smoke/pilot.",
                "",
                "The reopened A5 smoke reproduced forecast-skill gains but "
                "remained fail-closed on residual/null promotion criteria.",
                "",
                "## Recommended Next Step",
                "",
                "- Recommended next step: design one preregistered "
                "resource-bounded residual diagnostic that can separate useful "
                "anticipation from accounting/null effects before adding any "
                "new mechanics.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: major",
                "notify_ben: true",
                "recommended_next_action: Do not broaden A5.1.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path)

    assert state["state"] == "closed_awaiting_preregistration"
    assert state["should_noop"] is True
    assert state["closed_reasons"] == [
        "automation_status_a5_reopened_smoke_failed_closed"
    ]
    assert state["notify_ben"] is True
    assert state["recommended_next_action"] == (
        "design one preregistered resource-bounded residual diagnostic that "
        "can separate useful anticipation from accounting/null effects before "
        "adding any new mechanics."
    )


def test_automation_guard_closes_when_current_status_stops_a5_broadening(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    a5_path = (
        tmp_path
        / "docs"
        / "a5_single_hive_anticipatory_predictive_control_preregistration.md"
    )
    a5_path.parent.mkdir()
    a5_path.write_text("# A5 Single-Hive Anticipatory Predictive-Control Preregistration\n")
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "## Current Focus",
                "",
                "Source-of-truth status: the current concise A5 gate is "
                "`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.",
                "That document records the explicit single-hive A5 reopening "
                "and is the active preregistration summary for the bounded "
                "smoke/pilot requested on 2026-06-28.",
                "",
                "## Recommended Next Step",
                "",
                "- Recommended next step: stop A5 broadening after this "
                "fail-closed smoke and ask Ben to choose the next separately "
                "preregistered scientific target.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: minor",
                "notify_ben: true",
                "recommended_next_action: Send Ben the existing A5-exit/A7.2 "
                "decision request now, then suspend repo-writing/status-loop "
                "automation while awaiting his choice.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path)

    assert state["state"] == "closed_awaiting_preregistration"
    assert state["should_noop"] is True
    assert state["repo_write_allowed"] is False
    assert state["closed_reasons"] == ["automation_status_a5_broadening_stopped"]
    assert state["notify_ben"] is True
    assert state["recommended_next_action"] == (
        "stop A5 broadening after this fail-closed smoke and ask Ben to "
        "choose the next separately preregistered scientific target."
    )


def test_automation_guard_opens_when_ben_accepts_a7_2_then_three_hive(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    a5_path = (
        tmp_path
        / "docs"
        / "a5_single_hive_anticipatory_predictive_control_preregistration.md"
    )
    a5_path.parent.mkdir()
    a5_path.write_text("# A5 Single-Hive Anticipatory Predictive-Control Preregistration\n")
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "## Current Focus",
                "",
                "Source-of-truth status: Ben's 2026-06-28 instruction opens "
                "A7.2 delayed artifact-mediated endogenous prediction as the "
                "active next OmegaSim gate.",
                "This supersedes the previous A5-family decision-awaiting "
                "posture.",
                "",
                "After A7.2 closes, whether positive or negative, proceed "
                "without another Ben decision to a separate three-hive ring "
                "preregistration and bounded experiment family.",
                "",
                "## Recommended Next Step",
                "",
                "- Recommended next step: open A7.2 as the active preregistered "
                "gate by freezing its mechanism equations, artifact schema, "
                "endpoints, controls/nulls, and tiny smoke contract.",
                "",
                "## Blockers",
                "",
                "Resolved: the old instruction to stop A5 broadening after "
                "this fail-closed smoke was superseded by Ben's A7.2 decision.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: minor",
                "notify_ben: true",
                "recommended_next_action: Send Ben the existing A5-exit/A7.2 "
                "decision request now, then suspend repo-writing/status-loop "
                "automation while awaiting his choice.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path)

    assert state["state"] == "open"
    assert state["should_noop"] is False
    assert state["repo_write_allowed"] is True
    assert state["closed_reasons"] == []
    assert state["notify_ben"] is True
    assert state["recommended_next_action"] == (
        "open A7.2 as the active preregistered gate by freezing its mechanism "
        "equations, artifact schema, endpoints, controls/nulls, and tiny "
        "smoke contract."
    )


def test_automation_guard_closes_after_a7_2_and_three_hive_fail_closed(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    a5_path = (
        tmp_path
        / "docs"
        / "a5_single_hive_anticipatory_predictive_control_preregistration.md"
    )
    a5_path.parent.mkdir()
    a5_path.write_text("# A5 Single-Hive Anticipatory Predictive-Control Preregistration\n")
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "## Current Focus",
                "",
                "Source-of-truth status: Ben's 2026-06-28 instruction opens "
                "A7.2 delayed artifact-mediated endogenous prediction as the "
                "active next OmegaSim gate.",
                "After A7.2 closes, whether positive or negative, proceed "
                "without another Ben decision to a separate three-hive ring.",
                "The immediate A7.2 gate closed fail-closed at seed 1,2.",
                "The post-A7.2 three-hive ring also closed fail-closed after "
                "the residual/null analyzer.",
                "",
                "## Recommended Next Step",
                "",
                "- Recommended next step: pause further three-hive ring expansion "
                "and prepare a fresh preregistered decision note only if Ben "
                "wants another scientific direction, such as a one-hive "
                "dimensionless delayed-dynamics sweep.",
                "",
                "## Blockers",
                "",
                "Ben should be notified that the A7.2 and three-hive ring "
                "line is awaiting-preregistration after fail-closed results.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: major",
                "notify_ben: true",
                "recommended_next_action: Close the automation into "
                "awaiting-preregistration, notify Ben that A7.2 and the "
                "three-hive ring both failed closed, and offer a fresh "
                "one-hive dimensionless delayed-dynamics preregistration as "
                "the next scientific choice.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path)

    assert state["state"] == "closed_awaiting_preregistration"
    assert state["should_noop"] is True
    assert state["repo_write_allowed"] is False
    assert state["closed_reasons"] == [
        "automation_status_a7_2_three_hive_failed_closed"
    ]
    assert state["strategic_change_level"] == "major"
    assert state["notify_ben"] is True
    assert state["recommended_next_action"] == (
        "pause further three-hive ring expansion and prepare a fresh "
        "preregistered decision note only if Ben wants another scientific "
        "direction, such as a one-hive dimensionless delayed-dynamics sweep."
    )


def test_automation_guard_opens_a7_3_when_ben_says_proceed_not_pause(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    a5_path = (
        tmp_path
        / "docs"
        / "a5_single_hive_anticipatory_predictive_control_preregistration.md"
    )
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "## Current Focus",
                "",
                "A7.2 and the three-hive ring remain fail-closed and "
                "awaiting-preregistration as historical evidence.",
                "Source-of-truth status: Ben's 2026-06-29 instruction says "
                "OmegaSim should proceed, not pause. This opens A7.3 "
                "one-hive dimensionless delayed dynamics as the active next "
                "OmegaSim gate.",
                "This supersedes the previous awaiting-preregistration "
                "posture and does not reopen A7.2 or the three-hive ring.",
                "",
                "## Recommended Next Step",
                "",
                "- Recommended next step: draft and freeze the A7.3 one-hive "
                "dimensionless delayed-dynamics preregistration and minimal "
                "implementation gate.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: major",
                "notify_ben: true",
                "recommended_next_action: Close the automation into "
                "awaiting-preregistration until Ben chooses a fresh "
                "one-hive dimensionless delayed-dynamics preregistration.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path)

    assert state["state"] == "open"
    assert state["should_noop"] is False
    assert state["repo_write_allowed"] is True
    assert state["closed_reasons"] == []
    assert state["strategic_change_level"] == "major"
    assert state["notify_ben"] is True
    assert state["recommended_next_action"] == (
        "draft and freeze the A7.3 one-hive dimensionless delayed-dynamics "
        "preregistration and minimal implementation gate."
    )


def test_automation_guard_keeps_closed_for_a5_exit_ben_decision_status(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    roadmap_path = tmp_path / "docs" / "omegasim_provisional_experiment_roadmap.md"
    a5_path = (
        tmp_path
        / "docs"
        / "a5_single_hive_anticipatory_predictive_control_preregistration.md"
    )
    a5_path.parent.mkdir()
    a5_path.write_text("# A5 Single-Hive Anticipatory Predictive-Control Preregistration\n")
    roadmap_path.write_text(
        "\n".join(
            [
                "# OmegaSim Provisional Experiment Roadmap",
                "",
                "Accepted by Ben on 2026-06-27.",
                "",
                "Update 2026-06-27: A6/A6.1/A6.2 are now closed conservatively. "
                "Ben accepted proceeding to A7 as the next preregistered direction.",
                "",
                "This roadmap replaces the closed A5 no-op posture as the "
                "provisional direction for OmegaSim experimentation.",
                "",
                "## Immediate Next Step",
                "",
                "Create an A7 implementation gate before any broad experiment.",
            ]
        )
    )
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "## Current Focus",
                "",
                "Source-of-truth status: the explicit 2026-06-27 concise "
                "single-hive A5 reopening has now been run and closed "
                "fail-closed.",
                "The concise preregistration remains a historical record for "
                "that bounded gate, not an active authorization for more "
                "A5-family automation.",
                "",
                "The latest GPT-5.5-Pro strategy review has "
                "`strategic_change_level: major` and `notify_ben: true`.",
                "Its A5-exit recommendation is accepted as scientifically "
                "sensible.",
                "",
                "## Recommended Next Step",
                "",
                "- Recommended next step: remain in no-op/awaiting-preregistration "
                "state and have Ben decide whether A5-family work should stay "
                "closed, A7.2 delayed artifact-mediated endogenous prediction "
                "should become the next active preregistered gate, or a separate "
                "three-hive ring preregistration should be drafted.",
                "",
                "## Latest Changes",
                "",
                "- Historical note: Current concise A5 gate recorded an explicit "
                "single-hive A5 reopening.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: major",
                "notify_ben: true",
                "recommended_next_action: Keep the guard closed and draft a "
                "non-active Ben-decision preregistration.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path, roadmap_path)

    assert state["state"] == "closed_awaiting_preregistration"
    assert state["should_noop"] is True
    assert state["repo_write_allowed"] is False
    assert state["closed_reasons"] == ["automation_status_next_step_noop"]
    assert state["a5_preregistration_active"] is True
    assert state["notify_ben"] is True
    assert state["recommended_next_action"] == (
        "remain in no-op/awaiting-preregistration state and have Ben decide "
        "whether A5-family work should stay closed, A7.2 delayed "
        "artifact-mediated endogenous prediction should become the next active "
        "preregistered gate, or a separate three-hive ring preregistration "
        "should be drafted."
    )


def test_automation_guard_reopens_when_accepted_roadmap_replaces_a5_noop(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    roadmap_path = tmp_path / "docs" / "omegasim_provisional_experiment_roadmap.md"
    a5_path = tmp_path / "docs" / "a5_anticipatory_predictive_control_preregistration.md"
    roadmap_path.parent.mkdir()
    a5_path.write_text("# A5 Anticipatory Predictive-Control Preregistration\n")
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "The current A5 anticipatory predictive-control loop is closed.",
                "",
                "## Recommended Next Step",
                "",
                "Remain in no-op/awaiting-preregistration state for A5 unless Ben",
                "explicitly requests a new preregistered A5 design.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: none",
                "notify_ben: false",
                "recommended_next_action: Verify guard/loop state, then create an "
                "A7 implementation contract.",
            ]
        )
    )
    roadmap_path.write_text(
        "\n".join(
            [
                "# OmegaSim Provisional Experiment Roadmap",
                "",
                "Accepted by Ben on 2026-06-27.",
                "",
                "Update 2026-06-27: A6/A6.1/A6.2 are now closed conservatively. "
                "Ben accepted proceeding to A7 as the next preregistered direction.",
                "",
                "This roadmap replaces the closed A5 no-op posture as the "
                "provisional direction for OmegaSim experimentation.",
                "",
                "## Immediate Next Step",
                "",
                "Create an A7 implementation gate before any broad experiment.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path, roadmap_path)

    assert state["state"] == "open"
    assert state["should_noop"] is False
    assert state["closed_reasons"] == []
    assert state["recommended_next_action"] == (
        "Verify guard/loop state, then create an A7 implementation contract."
    )


def test_automation_guard_prefers_newer_a5_1a_closure_over_old_a7_roadmap(
    tmp_path: Path,
) -> None:
    status_path = tmp_path / "AUTOMATION_STATUS.md"
    review_path = tmp_path / "latest-review.md"
    roadmap_path = tmp_path / "docs" / "omegasim_provisional_experiment_roadmap.md"
    a5_path = tmp_path / "docs" / "a5_anticipatory_predictive_control_preregistration.md"
    roadmap_path.parent.mkdir()
    a5_path.write_text("# A5 Anticipatory Predictive-Control Preregistration\n")
    status_path.write_text(
        "\n".join(
            [
                "# OmegaSim Automation Status",
                "",
                "A5.1a is now closed conservatively.",
                "The current A5 anticipatory predictive-control loop is closed "
                "at the A5.1a accounting boundary.",
                "Ben should be notified that the active direction shifted from "
                "the older A7 roadmap wording back to a narrow A5.1 accounting "
                "gate and that this gate failed closed.",
                "",
                "## Recommended Next Step",
                "",
                "- Recommended next step: remain in no-op/awaiting-preregistration "
                "state and notify Ben of the A5.1a fail-closed result.",
            ]
        )
    )
    review_path.write_text(
        "\n".join(
            [
                "strategic_change_level: major",
                "notify_ben: true",
                "recommended_next_action: Do not broaden A5.1.",
            ]
        )
    )
    roadmap_path.write_text(
        "\n".join(
            [
                "# OmegaSim Provisional Experiment Roadmap",
                "",
                "Accepted by Ben on 2026-06-27.",
                "",
                "Update 2026-06-27: A6/A6.1/A6.2 are now closed conservatively. "
                "Ben accepted proceeding to A7 as the next preregistered direction.",
                "",
                "This roadmap replaces the closed A5 no-op posture as the "
                "provisional direction for OmegaSim experimentation.",
                "",
                "## Immediate Next Step",
                "",
                "Create an A7 implementation gate before any broad experiment.",
            ]
        )
    )

    state = read_automation_state(status_path, review_path, a5_path, roadmap_path)

    assert state["state"] == "closed_awaiting_preregistration"
    assert state["should_noop"] is True
    assert state["closed_reasons"] == ["automation_status_next_step_noop"]
    assert state["notify_ben"] is True
    assert (
        state["recommended_next_action"]
        == "remain in no-op/awaiting-preregistration state and notify Ben of "
        "the A5.1a fail-closed result."
    )


def _write_config(path: Path, overrides: dict[str, object]) -> Path:
    data = {
        "run": {"experiment_id": "a4_config_validation", "ticks": 3},
        "model": {
            "agent_count": 15,
            "actions": ["idle", "message", "create_task", "work_task"],
        },
        "outputs": {
            "write_manifest": True,
            "write_metrics": True,
            "write_events": True,
            "write_summary": True,
        },
    }
    data.update(overrides)
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    return path


def test_loads_opt_in_two_hive_coupling_config(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path / "a4_two_hive_none.yaml",
        {
            "hives": [
                {
                    "hive_id": "hive_a",
                    "seed_offset": 0,
                    "exogenous_arrival_rate": 1.0,
                    "work_service_capacity": 1.0,
                },
                {
                    "hive_id": "hive_b",
                    "seed_offset": 1000,
                    "exogenous_arrival_rate": 1.5,
                    "work_service_capacity": 0.7,
                },
            ],
            "coupling": {
                "mode": "none",
                "transfer_probability": 0.0,
                "delay_ticks": 0,
                "shuffle_seed_offset": 2000,
            },
        },
    )

    config = load_config(config_path)

    assert [hive.hive_id for hive in config.hives] == ["hive_a", "hive_b"]
    assert [hive.seed_offset for hive in config.hives] == [0, 1000]
    assert config.hives[1].exogenous_arrival_rate == 1.5
    assert config.hives[1].work_service_capacity == 0.7
    assert config.coupling is not None
    assert config.coupling.mode == "none"
    assert config.coupling.transfer_probability == 0.0
    assert config.coupling.delay_ticks == 0
    assert config.coupling.shuffle_seed_offset == 2000


@pytest.mark.parametrize(
    ("overrides", "error"),
    [
        (
            {
                "hives": [
                    {"hive_id": "hive_a", "seed_offset": 0},
                    {"hive_id": "hive_a", "seed_offset": 1000},
                ]
            },
            "duplicate hive_id",
        ),
        (
            {"hives": [{"hive_id": " ", "seed_offset": 0}]},
            "non-empty string",
        ),
        (
            {"hives": [{"hive_id": "hive_a", "seed_offset": -1}]},
            "non-negative integer",
        ),
        (
            {
                "hives": [{"hive_id": "hive_a", "seed_offset": 0}],
                "coupling": {"mode": "mystery"},
            },
            "must be one of",
        ),
        (
            {
                "hives": [{"hive_id": "hive_a", "seed_offset": 0}],
                "coupling": {"mode": "none", "transfer_probability": 0.1},
            },
            "requires transfer_probability 0.0",
        ),
        (
            {
                "hives": [{"hive_id": "hive_a", "seed_offset": 0}],
                "coupling": {"mode": "delayed", "delay_ticks": 0},
            },
            "requires delay_ticks > 0",
        ),
        (
            {
                "hives": [{"hive_id": "hive_a", "seed_offset": 0}],
                "coupling": {"mode": "direct", "transfer_probability": 1.1},
            },
            "between 0.0 and 1.0",
        ),
        (
            {
                "hives": [{"hive_id": "hive_a", "seed_offset": 0}],
                "coupling": {"mode": "direct", "shuffle_seed_offset": 0},
            },
            "distinct from hive seed_offset",
        ),
        (
            {"coupling": {"mode": "none"}},
            "requires opt-in 'hives'",
        ),
    ],
)
def test_invalid_a4_hive_and_coupling_configs_fail(
    tmp_path: Path,
    overrides: dict[str, object],
    error: str,
) -> None:
    config_path = _write_config(tmp_path / "invalid_a4.yaml", overrides)

    with pytest.raises(ValueError, match=error):
        load_config(config_path)


def test_documented_cli_rejects_invalid_a4_config_before_writing_artifacts(
    tmp_path: Path,
) -> None:
    config_path = _write_config(
        tmp_path / "invalid_a4.yaml",
        {
            "hives": [
                {"hive_id": "hive_a", "seed_offset": 0},
                {"hive_id": "hive_a", "seed_offset": 1000},
            ],
        },
    )
    out_dir = tmp_path / "out"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "duplicate hive_id" in completed.stderr
    assert not out_dir.exists()


def test_a4_two_hive_none_writes_inert_multi_hive_artifacts_and_reproduces(
    tmp_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        A4_TWO_HIVE_NONE,
        tmp_path,
        first_seed=31,
        second_seed=31,
        first_name="a4_first",
        second_name="a4_second",
    )
    third = tmp_path / "a4_third"
    _run_documented_cli(A4_TWO_HIVE_NONE, third, seed=32)

    for out_dir in (first, second, third):
        _assert_artifacts_match_output_directory(
            out_dir,
            _expected_artifacts(A4_TWO_HIVE_NONE),
        )

    for artifact in _expected_artifacts(A4_TWO_HIVE_NONE):
        assert (first / artifact).read_text() == (second / artifact).read_text()
    assert (first / "hive_metrics.csv").read_text() != (
        third / "hive_metrics.csv"
    ).read_text()

    manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    summary = (first / "summary.md").read_text()
    with (first / "hive_metrics.csv").open() as handle:
        hive_rows = list(csv.DictReader(handle))
    with (first / "cross_hive_metrics.csv").open() as handle:
        cross_rows = list(csv.DictReader(handle))
    with (first / "hive_events.csv").open() as handle:
        hive_events = list(csv.DictReader(handle))
    with (first / "coupling_events.csv").open() as handle:
        coupling_events = list(csv.DictReader(handle))

    assert manifest["hive_count"] == 2
    assert manifest["hive_ids"] == ["hive_a", "hive_b"]
    assert manifest["coupling_mode"] == "none"
    assert manifest["model"]["multi_hive"]["hive_seed_streams"] == {
        "hive_a": "cli_seed + 0",
        "hive_b": "cli_seed + 1000",
    }
    assert "## Multi-hive coupling" in summary
    assert "- completed transfers: 0" in summary
    assert {row["hive_id"] for row in hive_rows} == {"hive_a", "hive_b"}
    assert {row["hive_id"] for row in hive_events} == {"hive_a", "hive_b"}
    assert coupling_events == []
    assert (first / "coupling_events.csv").read_text().splitlines()[0] == (
        "tick,source_hive_id,target_hive_id,task_id,coupling_mode,delay_ticks,"
        "transfer_decision,arrival_tick"
    )
    for row in cross_rows:
        assert row["coupling_mode"] == "none"
        assert row["transfer_attempts_tick"] == "0"
        assert row["transfers_completed_tick"] == "0"
        assert row["aggregate_inbound_transfers_tick"] == "0"
        assert row["aggregate_outbound_transfers_tick"] == "0"
        assert row["aggregate_explicit_drops_tick"] == "0"
        assert row["aggregate_queue_balance_residual_tick"] == "0"


def test_a4_two_hive_direct_records_coupling_and_conserves_queue_flow(
    tmp_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        A4_TWO_HIVE_DIRECT,
        tmp_path,
        first_seed=31,
        second_seed=31,
        first_name="a4_direct_first",
        second_name="a4_direct_second",
    )
    third = tmp_path / "a4_direct_third"
    _run_documented_cli(A4_TWO_HIVE_DIRECT, third, seed=32)

    for artifact in _expected_artifacts(A4_TWO_HIVE_DIRECT):
        assert (first / artifact).read_text() == (second / artifact).read_text()
    assert (first / "coupling_events.csv").read_text() != (
        third / "coupling_events.csv"
    ).read_text()

    manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    summary = (first / "summary.md").read_text()
    with (first / "hive_metrics.csv").open() as handle:
        hive_rows = list(csv.DictReader(handle))
    with (first / "cross_hive_metrics.csv").open() as handle:
        cross_rows = list(csv.DictReader(handle))
    with (first / "coupling_events.csv").open() as handle:
        coupling_events = list(csv.DictReader(handle))
    with (first / "hive_events.csv").open() as handle:
        hive_events = list(csv.DictReader(handle))

    assert manifest["coupling_mode"] == "direct"
    assert manifest["model"]["multi_hive"]["coupling_mode"] == "direct"
    assert coupling_events
    assert "- coupling mode: direct" in summary
    assert f"- completed transfers: {len(coupling_events)}" in summary
    assert {row["coupling_mode"] for row in coupling_events} == {"direct"}
    assert {row["delay_ticks"] for row in coupling_events} == {"0"}
    assert {row["transfer_decision"] for row in coupling_events} == {"True"}
    assert all(row["arrival_tick"] == row["tick"] for row in coupling_events)
    assert {
        (row["source_hive_id"], row["target_hive_id"])
        for row in coupling_events
    } == {("hive_a", "hive_b"), ("hive_b", "hive_a")}
    assert all(":" in row["task_id"] for row in coupling_events)
    assert any(
        row["event_type"] == "task_worked" and ":" in row["task_id"]
        for row in hive_events
    )

    for row in hive_rows:
        created = int(row["tasks_created_tick"])
        inbound = int(row["inbound_transfers_tick"])
        completed = int(row["tasks_completed_tick"])
        outbound = int(row["outbound_transfers_tick"])
        drops = int(row["explicit_drops_tick"])
        delta = int(row["queue_delta_tick"])
        assert int(row["queue_balance_residual_tick"]) == 0
        assert delta == created + inbound - completed - outbound - drops

    for row in cross_rows:
        assert row["coupling_mode"] == "direct"
        assert int(row["transfer_attempts_tick"]) == int(row["transfers_completed_tick"])
        assert int(row["aggregate_inbound_transfers_tick"]) == int(
            row["aggregate_outbound_transfers_tick"]
        )
        assert row["aggregate_queue_balance_residual_tick"] == "0"


def test_a4_two_hive_delayed_records_fixed_lag_arrivals_and_conserves_queue_flow(
    tmp_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        A4_TWO_HIVE_DELAYED,
        tmp_path,
        first_seed=31,
        second_seed=31,
        first_name="a4_delayed_first",
        second_name="a4_delayed_second",
    )
    third = tmp_path / "a4_delayed_third"
    _run_documented_cli(A4_TWO_HIVE_DELAYED, third, seed=32)

    for artifact in _expected_artifacts(A4_TWO_HIVE_DELAYED):
        assert (first / artifact).read_text() == (second / artifact).read_text()
    assert (first / "coupling_events.csv").read_text() != (
        third / "coupling_events.csv"
    ).read_text()

    manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    summary = (first / "summary.md").read_text()
    with (first / "hive_metrics.csv").open() as handle:
        hive_rows = list(csv.DictReader(handle))
    with (first / "cross_hive_metrics.csv").open() as handle:
        cross_rows = list(csv.DictReader(handle))
    with (first / "coupling_events.csv").open() as handle:
        coupling_events = list(csv.DictReader(handle))
    with (first / "hive_events.csv").open() as handle:
        hive_events = list(csv.DictReader(handle))

    assert manifest["coupling_mode"] == "delayed"
    assert manifest["model"]["multi_hive"]["coupling_mode"] == "delayed"
    assert coupling_events
    assert "- coupling mode: delayed" in summary
    assert "- delay ticks: 2" in summary
    assert {row["coupling_mode"] for row in coupling_events} == {"delayed"}
    assert {row["delay_ticks"] for row in coupling_events} == {"2"}
    assert {row["transfer_decision"] for row in coupling_events} == {"True"}
    assert all(int(row["arrival_tick"]) == int(row["tick"]) + 2 for row in coupling_events)
    assert any(
        row["event_type"] == "task_worked" and ":" in row["task_id"]
        for row in hive_events
    )

    inbound_by_tick = Counter(
        int(row["arrival_tick"])
        for row in coupling_events
        if int(row["arrival_tick"]) < len(cross_rows)
    )
    outbound_by_tick = Counter(int(row["tick"]) for row in coupling_events)
    assert any(tick + 2 in inbound_by_tick for tick in outbound_by_tick)

    for row in hive_rows:
        created = int(row["tasks_created_tick"])
        inbound = int(row["inbound_transfers_tick"])
        completed = int(row["tasks_completed_tick"])
        outbound = int(row["outbound_transfers_tick"])
        drops = int(row["explicit_drops_tick"])
        delta = int(row["queue_delta_tick"])
        assert int(row["queue_balance_residual_tick"]) == 0
        assert delta == created + inbound - completed - outbound - drops

    for row in cross_rows:
        tick = int(row["tick"])
        assert row["coupling_mode"] == "delayed"
        assert int(row["transfer_attempts_tick"]) == outbound_by_tick[tick]
        assert int(row["aggregate_inbound_transfers_tick"]) == inbound_by_tick[tick]
        assert row["aggregate_queue_balance_residual_tick"] == "0"


def test_a4_two_hive_shuffled_preserves_smoke_marginals_and_conserves_queue_flow(
    tmp_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        A4_TWO_HIVE_SHUFFLED,
        tmp_path,
        first_seed=31,
        second_seed=31,
        first_name="a4_shuffled_first",
        second_name="a4_shuffled_second",
    )
    direct = tmp_path / "a4_direct_reference"
    _run_documented_cli(A4_TWO_HIVE_DIRECT, direct, seed=31)

    for artifact in _expected_artifacts(A4_TWO_HIVE_SHUFFLED):
        assert (first / artifact).read_text() == (second / artifact).read_text()

    manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    summary = (first / "summary.md").read_text()
    with (first / "hive_metrics.csv").open() as handle:
        hive_rows = list(csv.DictReader(handle))
    with (first / "cross_hive_metrics.csv").open() as handle:
        cross_rows = list(csv.DictReader(handle))
    with (first / "coupling_events.csv").open() as handle:
        coupling_events = list(csv.DictReader(handle))
    with (direct / "coupling_events.csv").open() as handle:
        direct_coupling_events = list(csv.DictReader(handle))

    assert manifest["coupling_mode"] == "shuffled"
    assert manifest["model"]["multi_hive"]["coupling_mode"] == "shuffled"
    assert coupling_events
    assert "- coupling mode: shuffled" in summary
    assert {row["coupling_mode"] for row in coupling_events} == {"shuffled"}
    assert {row["delay_ticks"] for row in coupling_events} == {"0"}
    assert {row["transfer_decision"] for row in coupling_events} == {"True"}
    assert all(row["arrival_tick"] == row["tick"] for row in coupling_events)
    assert len(coupling_events) == len(direct_coupling_events)
    assert Counter(row["source_hive_id"] for row in coupling_events) == Counter(
        row["source_hive_id"] for row in direct_coupling_events
    )
    assert {
        (row["source_hive_id"], row["target_hive_id"])
        for row in coupling_events
    } == {("hive_a", "hive_b"), ("hive_b", "hive_a")}

    for row in hive_rows:
        created = int(row["tasks_created_tick"])
        inbound = int(row["inbound_transfers_tick"])
        completed = int(row["tasks_completed_tick"])
        outbound = int(row["outbound_transfers_tick"])
        drops = int(row["explicit_drops_tick"])
        delta = int(row["queue_delta_tick"])
        assert int(row["queue_balance_residual_tick"]) == 0
        assert delta == created + inbound - completed - outbound - drops

    for row in cross_rows:
        assert row["coupling_mode"] == "shuffled"
        assert int(row["transfer_attempts_tick"]) == int(row["transfers_completed_tick"])
        assert int(row["aggregate_inbound_transfers_tick"]) == int(
            row["aggregate_outbound_transfers_tick"]
        )
        assert row["aggregate_queue_balance_residual_tick"] == "0"


def test_a4_smoke_contract_preflight_writes_readiness_report(tmp_path: Path) -> None:
    out = tmp_path / "a4_smoke_contract_preflight.md"
    work_dir = tmp_path / "a4_smoke_contract_work"

    result = run_a4_smoke_contract_preflight(out=out, work_dir=work_dir, seed=31)

    assert result["passed"] is True
    report = out.read_text()
    assert "# A4 Smoke Contract Preflight" in report
    assert "- scientific holdout seeds run: none" in report
    assert "| none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |" in report
    assert "| direct | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |" in report
    assert "| delayed | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |" in report
    assert "| shuffled | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |" in report
    assert "Two-hive shuffled" in report
    assert (work_dir / "none_first" / "hive_metrics.csv").exists()
    assert (work_dir / "shuffled_second" / "coupling_events.csv").exists()


def test_a4_smoke_contract_preflight_refuses_existing_report_without_work(
    tmp_path: Path,
) -> None:
    out = tmp_path / "a4_smoke_contract_preflight.md"
    work_dir = tmp_path / "a4_smoke_contract_work"
    out.write_text("sentinel")

    with pytest.raises(FileExistsError, match="Output report already exists"):
        run_a4_smoke_contract_preflight(out=out, work_dir=work_dir, seed=31)

    assert out.read_text() == "sentinel"
    assert not work_dir.exists()


def test_a4_holdout_config_bundle_loads_without_running_holdout_seeds() -> None:
    expected = {
        A4_TWO_HIVE_NONE_HOLDOUT: ("none", 0.0, 0),
        A4_TWO_HIVE_DIRECT_HOLDOUT: ("direct", 1.0, 0),
        A4_TWO_HIVE_DELAYED_HOLDOUT: ("delayed", 1.0, 2),
        A4_TWO_HIVE_SHUFFLED_HOLDOUT: ("shuffled", 1.0, 0),
    }

    for path, (mode, probability, delay_ticks) in expected.items():
        config = load_config(path)

        assert config.run.experiment_id == f"a4_two_hive_{mode}_holdout"
        assert config.run.ticks == 100
        assert config.model.agent_count == 15
        assert config.model.actions == ("idle", "message", "create_task", "work_task")
        assert [hive.hive_id for hive in config.hives] == ["hive_a", "hive_b"]
        assert [hive.seed_offset for hive in config.hives] == [0, 1000]
        assert [hive.exogenous_arrival_rate for hive in config.hives] == [1.0, 1.0]
        assert [hive.work_service_capacity for hive in config.hives] == [1.0, 1.0]
        assert config.coupling is not None
        assert config.coupling.mode == mode
        assert config.coupling.transfer_probability == probability
        assert config.coupling.delay_ticks == delay_ticks
        assert config.coupling.shuffle_seed_offset == 2000


def test_a4_holdout_analyzer_consumes_existing_paired_seed_artifacts(
    tmp_path: Path,
) -> None:
    source = tmp_path / "a4_existing_artifacts"
    configs_by_mode = {
        "none": A4_TWO_HIVE_NONE,
        "direct": A4_TWO_HIVE_DIRECT,
        "delayed": A4_TWO_HIVE_DELAYED,
        "shuffled": A4_TWO_HIVE_SHUFFLED,
    }
    seeds = (31, 32)
    for seed in seeds:
        for mode, config_path in configs_by_mode.items():
            run_experiment(config_path, seed, source / f"{mode}_seed{seed}")
    out_dir = tmp_path / "a4_analysis"

    result = run_a4_holdout_analysis(holdout_dir=source, out_dir=out_dir, seeds=seeds)

    assert result["seed_count"] == 2
    assert result["run_count"] == 8
    assert result["hive_endpoint_rows"] == 16
    assert result["cross_endpoint_rows"] == 8
    assert (out_dir / "a4_holdout_hive_endpoints.csv").exists()
    assert (out_dir / "a4_holdout_cross_hive_endpoints.csv").exists()
    assert (out_dir / "a4_holdout_effects.csv").exists()
    assert (out_dir / "summary.md").exists()

    with (out_dir / "a4_holdout_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    assert list(effect_rows[0]) == list(A4_EFFECT_FIELDS)
    transfer_effect = next(
        row
        for row in effect_rows
        if row["comparison"] == "direct_minus_none"
        and row["endpoint"] == "transfer_attempts_total"
    )
    assert transfer_effect["paired_seed_count"] == "2"
    assert float(transfer_effect["mean_delta"]) > 0.0
    assert transfer_effect["bootstrap_reps"] == "1000"
    assert transfer_effect["bootstrap_seed"] == "4404"
    assert float(transfer_effect["bootstrap_mean_delta_ci_low"]) > 0.0
    assert float(transfer_effect["bootstrap_mean_delta_ci_high"]) > 0.0
    assert float(transfer_effect["bootstrap_sign_stability"]) == 1.0
    summary = (out_dir / "summary.md").read_text()
    assert "# A4 Holdout Paired-Seed Analysis" in summary
    assert "deterministic paired-bootstrap uncertainty fields" in summary
    assert "- This analyzer is read-only and does not run A4 holdout seeds." in summary

    with pytest.raises(FileExistsError, match="already contains A4 analysis artifacts"):
        run_a4_holdout_analysis(holdout_dir=source, out_dir=out_dir, seeds=seeds)
    overwritten = run_a4_holdout_analysis(
        holdout_dir=source,
        out_dir=out_dir,
        seeds=seeds,
        bootstrap_reps=25,
        bootstrap_seed=123,
        overwrite=True,
    )
    assert overwritten["bootstrap_reps"] == 25


def test_a4_holdout_analyzer_refuses_missing_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "a4_incomplete"
    source.mkdir()

    with pytest.raises(FileNotFoundError, match="missing artifacts"):
        run_a4_holdout_analysis(holdout_dir=source, out_dir=tmp_path / "out", seeds=(31,))


def test_a4_delayed_null_analyzer_builds_deterministic_shift_controls(
    tmp_path: Path,
) -> None:
    source = tmp_path / "a4_existing_artifacts"
    configs_by_mode = {
        "none": A4_TWO_HIVE_NONE,
        "direct": A4_TWO_HIVE_DIRECT,
        "delayed": A4_TWO_HIVE_DELAYED,
        "shuffled": A4_TWO_HIVE_SHUFFLED,
    }
    seeds = (31, 32)
    for seed in seeds:
        for mode, config_path in configs_by_mode.items():
            run_experiment(config_path, seed, source / f"{mode}_seed{seed}")
    out_dir = tmp_path / "a4_delayed_null"
    doc_out = tmp_path / "a4_delayed_null.md"

    result = run_a4_delayed_null_analysis(
        holdout_dir=source,
        out_dir=out_dir,
        doc_out=doc_out,
        seeds=seeds,
        block_sizes=(2, 3),
    )

    assert result["seed_count"] == 2
    assert result["null_endpoint_rows"] > 0
    assert result["null_effect_rows"] == 24
    assert (out_dir / "a4_delayed_null_endpoints.csv").exists()
    assert (out_dir / "a4_delayed_null_effects.csv").exists()
    assert (out_dir / "a4_delayed_null_manifest.csv").exists()
    assert (out_dir / "summary.md").exists()
    assert doc_out.exists()

    with (out_dir / "a4_delayed_null_endpoints.csv").open() as handle:
        endpoint_rows = list(csv.DictReader(handle))
    assert list(endpoint_rows[0]) == list(A4_DELAYED_NULL_ENDPOINT_FIELDS)
    delayed_offsets = {
        int(row["offset"])
        for row in endpoint_rows
        if row["mode"] == "delayed"
    }
    assert 0 not in delayed_offsets
    assert 2 not in delayed_offsets

    with (out_dir / "a4_delayed_null_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    assert list(effect_rows[0]) == list(A4_DELAYED_NULL_EFFECT_FIELDS)
    delayed_load_row = next(
        row
        for row in effect_rows
        if row["comparison"] == "delayed_minus_none"
        and row["endpoint"] == "load_backlog_corr_lag0"
    )
    assert delayed_load_row["paired_seed_count"] == "2"
    assert int(delayed_load_row["null_replicate_count"]) > 0
    summary = (out_dir / "summary.md").read_text()
    assert "# A4 Delayed-Coupling Temporal Null Analysis" in summary
    assert "read-only" in summary

    with pytest.raises(FileExistsError, match="delayed-null artifacts"):
        run_a4_delayed_null_analysis(
            holdout_dir=source,
            out_dir=out_dir,
            doc_out=doc_out,
            seeds=seeds,
            block_sizes=(2, 3),
        )

    second_out = tmp_path / "a4_delayed_null_second"
    second_doc = tmp_path / "a4_delayed_null_second.md"
    run_a4_delayed_null_analysis(
        holdout_dir=source,
        out_dir=second_out,
        doc_out=second_doc,
        seeds=seeds,
        block_sizes=(2, 3),
    )
    for artifact in (
        "a4_delayed_null_endpoints.csv",
        "a4_delayed_null_effects.csv",
        "a4_delayed_null_manifest.csv",
        "summary.md",
    ):
        assert (out_dir / artifact).read_bytes() == (second_out / artifact).read_bytes()


def test_a4_delayed_null_analyzer_refuses_missing_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "a4_incomplete"
    source.mkdir()

    with pytest.raises(FileNotFoundError, match="missing artifacts"):
        run_a4_delayed_null_analysis(
            holdout_dir=source,
            out_dir=tmp_path / "out",
            doc_out=None,
            seeds=(31,),
        )


def test_a4_accounting_control_analyzer_residualizes_completion_shift_controls(
    tmp_path: Path,
) -> None:
    source = tmp_path / "a4_existing_artifacts"
    configs_by_mode = {
        "none": A4_TWO_HIVE_NONE,
        "direct": A4_TWO_HIVE_DIRECT,
        "delayed": A4_TWO_HIVE_DELAYED,
        "shuffled": A4_TWO_HIVE_SHUFFLED,
    }
    seeds = (31, 32)
    for seed in seeds:
        for mode, config_path in configs_by_mode.items():
            run_experiment(config_path, seed, source / f"{mode}_seed{seed}")
    out_dir = tmp_path / "a4_accounting_controls"
    doc_out = tmp_path / "a4_accounting_controls.md"

    result = run_a4_accounting_control_analysis(
        holdout_dir=source,
        out_dir=out_dir,
        doc_out=doc_out,
        seeds=seeds,
        block_sizes=(2, 3),
    )

    assert result["seed_count"] == 2
    assert "combined_non_tautological" in result["control_groups"]
    assert "identity_inclusive" in result["control_groups"]
    assert result["observed_endpoint_rows"] == 48
    assert result["null_endpoint_rows"] > 0
    assert result["effect_rows"] == 48
    assert (out_dir / "a4_accounting_control_endpoints.csv").exists()
    assert (out_dir / "a4_accounting_control_effects.csv").exists()
    assert (out_dir / "a4_accounting_control_manifest.csv").exists()
    assert (out_dir / "summary.md").exists()
    assert doc_out.exists()

    with (out_dir / "a4_accounting_control_endpoints.csv").open() as handle:
        endpoint_rows = list(csv.DictReader(handle))
    assert list(endpoint_rows[0]) == list(A4_ACCOUNTING_CONTROL_ENDPOINT_FIELDS)
    delayed_null_offsets = {
        int(row["offset"])
        for row in endpoint_rows
        if row["mode"] == "delayed" and int(row["block_size"]) > 0
    }
    assert 0 not in delayed_null_offsets
    assert 2 not in delayed_null_offsets

    raw_observed = next(
        row
        for row in endpoint_rows
        if row["mode"] == "delayed"
        and row["control_group"] == "raw"
        and row["block_size"] == "0"
    )
    clock_observed = next(
        row
        for row in endpoint_rows
        if row["mode"] == "delayed"
        and row["control_group"] == "clock_trend"
        and row["block_size"] == "0"
    )
    assert raw_observed["completion_fraction_corr_lag0"] != "NA"
    assert clock_observed["completion_fraction_corr_lag0"] != "NA"

    with (out_dir / "a4_accounting_control_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    assert list(effect_rows[0]) == list(A4_ACCOUNTING_CONTROL_EFFECT_FIELDS)
    delayed_clock = next(
        row
        for row in effect_rows
        if row["comparison"] == "delayed_minus_none"
        and row["control_group"] == "clock_trend"
        and row["endpoint"] == "completion_fraction_corr_lag0"
    )
    assert delayed_clock["paired_seed_count"] == "2"
    assert int(delayed_clock["null_replicate_count"]) > 0
    summary = (out_dir / "summary.md").read_text()
    assert "# A4 Accounting-Control Completion Synchrony Analysis" in summary
    assert "read-only" in summary
    assert "identity_inclusive" in summary

    with pytest.raises(FileExistsError, match="accounting-control artifacts"):
        run_a4_accounting_control_analysis(
            holdout_dir=source,
            out_dir=out_dir,
            doc_out=doc_out,
            seeds=seeds,
            block_sizes=(2, 3),
        )

    second_out = tmp_path / "a4_accounting_controls_second"
    second_doc = tmp_path / "a4_accounting_controls_second.md"
    run_a4_accounting_control_analysis(
        holdout_dir=source,
        out_dir=second_out,
        doc_out=second_doc,
        seeds=seeds,
        block_sizes=(2, 3),
    )
    for artifact in (
        "a4_accounting_control_endpoints.csv",
        "a4_accounting_control_effects.csv",
        "a4_accounting_control_manifest.csv",
        "summary.md",
    ):
        assert (out_dir / artifact).read_bytes() == (second_out / artifact).read_bytes()


def test_a4_accounting_control_analyzer_refuses_missing_artifacts(
    tmp_path: Path,
) -> None:
    source = tmp_path / "a4_incomplete"
    source.mkdir()

    with pytest.raises(FileNotFoundError, match="missing artifacts"):
        run_a4_accounting_control_analysis(
            holdout_dir=source,
            out_dir=tmp_path / "out",
            doc_out=None,
            seeds=(31,),
        )


def test_loads_a0_default_outputs_fixture() -> None:
    config = load_config(DEFAULT_OUTPUTS)

    assert config.run.experiment_id == "a0_default_outputs"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("idle", "message", "create_task", "work_task")
    assert config.outputs.write_manifest is True
    assert config.outputs.write_metrics is True
    assert config.outputs.write_events is True
    assert config.outputs.write_summary is True


def test_loads_a0_reordered_actions_fixture() -> None:
    config = load_config(REORDERED_ACTIONS)

    assert config.run.experiment_id == "a0_reordered_actions"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("work_task", "create_task", "message", "idle")
    assert config.outputs.write_manifest is True
    assert config.outputs.write_metrics is True
    assert config.outputs.write_events is True
    assert config.outputs.write_summary is True


def test_loads_a0_config_only_fixture() -> None:
    config = load_config(CONFIG_ONLY)

    assert config.run.experiment_id == "a0_config_only"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("idle", "message", "create_task", "work_task")
    assert config.outputs.write_manifest is False
    assert config.outputs.write_metrics is False
    assert config.outputs.write_events is False
    assert config.outputs.write_summary is False


def test_loads_a0_config_only_reordered_actions_fixture() -> None:
    config = load_config(CONFIG_ONLY_REORDERED_ACTIONS)

    assert config.run.experiment_id == "a0_config_only_reordered_actions"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("work_task", "create_task", "message", "idle")
    assert config.outputs.write_manifest is False
    assert config.outputs.write_metrics is False
    assert config.outputs.write_events is False
    assert config.outputs.write_summary is False


def test_loads_a0_manifest_only_fixture() -> None:
    config = load_config(MANIFEST_ONLY)

    assert config.run.experiment_id == "a0_manifest_only"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("idle", "message", "create_task", "work_task")
    assert config.outputs.write_manifest is True
    assert config.outputs.write_metrics is False
    assert config.outputs.write_events is False
    assert config.outputs.write_summary is False


def test_loads_a0_manifest_only_reordered_actions_fixture() -> None:
    config = load_config(MANIFEST_ONLY_REORDERED_ACTIONS)

    assert config.run.experiment_id == "a0_manifest_only_reordered_actions"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("work_task", "create_task", "message", "idle")
    assert config.outputs.write_manifest is True
    assert config.outputs.write_metrics is False
    assert config.outputs.write_events is False
    assert config.outputs.write_summary is False


def test_loads_a0_no_manifest_fixture() -> None:
    config = load_config(NO_MANIFEST)

    assert config.run.experiment_id == "a0_no_manifest"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("idle", "message", "create_task", "work_task")
    assert config.outputs.write_manifest is False
    assert config.outputs.write_metrics is True
    assert config.outputs.write_events is True
    assert config.outputs.write_summary is True


def test_loads_a0_no_manifest_reordered_actions_fixture() -> None:
    config = load_config(NO_MANIFEST_REORDERED_ACTIONS)

    assert config.run.experiment_id == "a0_no_manifest_reordered_actions"
    assert config.run.ticks == 3
    assert config.model.agent_count == 15
    assert config.model.actions == ("work_task", "create_task", "message", "idle")
    assert config.outputs.write_manifest is False
    assert config.outputs.write_metrics is True
    assert config.outputs.write_events is True
    assert config.outputs.write_summary is True


def test_loads_a2_attention_smoke_config() -> None:
    config = load_config(A2_ATTENTION)

    assert config.run.experiment_id == "a2_attention_smoke"
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.attention_policy is not None
    assert config.attention_policy.shares() == {
        "near_term_external": 0.45,
        "long_term_research": 0.25,
        "internal_improvement": 0.2,
        "housekeeping": 0.1,
    }
    assert config.attention_policy.selection_strategy == "quota_balance"


def test_loads_a2_attention_random_available_config() -> None:
    config = load_config(A2_ATTENTION_RANDOM_AVAILABLE)

    assert config.run.experiment_id == "a2_attention_random_available"
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.attention_policy is not None
    assert config.attention_policy.shares() == {
        "near_term_external": 0.45,
        "long_term_research": 0.25,
        "internal_improvement": 0.2,
        "housekeeping": 0.1,
    }
    assert config.attention_policy.selection_strategy == "random_available"


def test_loads_a2_attention_research_heavy_config() -> None:
    config = load_config(A2_ATTENTION_RESEARCH_HEAVY)

    assert config.run.experiment_id == "a2_attention_research_heavy"
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.attention_policy is not None
    assert config.attention_policy.shares() == {
        "near_term_external": 0.2,
        "long_term_research": 0.55,
        "internal_improvement": 0.15,
        "housekeeping": 0.1,
    }


def test_loads_a2_attention_internal_improvement_config() -> None:
    config = load_config(A2_ATTENTION_INTERNAL_IMPROVEMENT)

    assert config.run.experiment_id == "a2_attention_internal_improvement"
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.attention_policy is not None
    assert config.attention_policy.shares() == {
        "near_term_external": 0.2,
        "long_term_research": 0.15,
        "internal_improvement": 0.55,
        "housekeeping": 0.1,
    }


@pytest.mark.parametrize(
    ("config_path", "experiment_id", "task_creation_pressure"),
    [
        (
            A2_ATTENTION_MEDIUM_PRESSURE,
            "a2_attention_medium_pressure",
            1.4,
        ),
        (
            A2_ATTENTION_RESEARCH_HEAVY_MEDIUM_PRESSURE,
            "a2_attention_research_heavy_medium_pressure",
            1.4,
        ),
        (
            A2_ATTENTION_INTERNAL_IMPROVEMENT_MEDIUM_PRESSURE,
            "a2_attention_internal_improvement_medium_pressure",
            1.4,
        ),
        (A2_ATTENTION_HIGH_PRESSURE, "a2_attention_high_pressure", 1.8),
        (
            A2_ATTENTION_RANDOM_AVAILABLE_HIGH_PRESSURE,
            "a2_attention_random_available_high_pressure",
            1.8,
        ),
        (
            A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE,
            "a2_attention_research_heavy_high_pressure",
            1.8,
        ),
        (
            A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE,
            "a2_attention_internal_improvement_high_pressure",
            1.8,
        ),
        (A2_ATTENTION_EXTREME_PRESSURE, "a2_attention_extreme_pressure", 2.2),
        (
            A2_ATTENTION_RANDOM_AVAILABLE_EXTREME_PRESSURE,
            "a2_attention_random_available_extreme_pressure",
            2.2,
        ),
        (
            A2_ATTENTION_RESEARCH_HEAVY_EXTREME_PRESSURE,
            "a2_attention_research_heavy_extreme_pressure",
            2.2,
        ),
        (
            A2_ATTENTION_INTERNAL_IMPROVEMENT_EXTREME_PRESSURE,
            "a2_attention_internal_improvement_extreme_pressure",
            2.2,
        ),
    ],
)
def test_loads_a2_attention_pressure_fixtures(
    config_path: Path,
    experiment_id: str,
    task_creation_pressure: float,
) -> None:
    config = load_config(config_path)

    assert config.run.experiment_id == experiment_id
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.model.task_creation_pressure == task_creation_pressure
    assert config.model.work_service_capacity == 1.0
    assert config.attention_policy is not None


@pytest.mark.parametrize(
    ("config_path", "experiment_id", "task_creation_pressure", "work_service_capacity"),
    [
        (
            A2_ATTENTION_LOW_SERVICE_CAPACITY,
            "a2_attention_low_service_capacity",
            1.0,
            0.7,
        ),
        (
            A2_ATTENTION_HIGH_SERVICE_CAPACITY,
            "a2_attention_high_service_capacity",
            1.0,
            1.3,
        ),
        (
            A2_ATTENTION_LOW_SERVICE_CAPACITY_HIGH_PRESSURE,
            "a2_attention_low_service_capacity_high_pressure",
            1.8,
            0.7,
        ),
        (
            A2_ATTENTION_HIGH_SERVICE_CAPACITY_HIGH_PRESSURE,
            "a2_attention_high_service_capacity_high_pressure",
            1.8,
            1.3,
        ),
        (
            A2_ATTENTION_LOW_SERVICE_CAPACITY_EXTREME_PRESSURE,
            "a2_attention_low_service_capacity_extreme_pressure",
            2.2,
            0.7,
        ),
        (
            A2_ATTENTION_HIGH_SERVICE_CAPACITY_EXTREME_PRESSURE,
            "a2_attention_high_service_capacity_extreme_pressure",
            2.2,
            1.3,
        ),
    ],
)
def test_loads_a2_attention_service_capacity_fixtures(
    config_path: Path,
    experiment_id: str,
    task_creation_pressure: float,
    work_service_capacity: float,
) -> None:
    config = load_config(config_path)

    assert config.run.experiment_id == experiment_id
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.model.task_creation_pressure == task_creation_pressure
    assert config.model.work_service_capacity == work_service_capacity
    assert config.attention_policy is not None
    assert config.attention_policy.selection_strategy == "quota_balance"


def test_loads_a2_exogenous_arrivals_fixture() -> None:
    config = load_config(A2_EXOGENOUS_ARRIVALS)

    assert config.run.experiment_id == "a2_exogenous_arrivals_smoke"
    assert config.run.ticks == 12
    assert config.model.agent_count == 15
    assert config.model.task_creation_pressure == 1.0
    assert config.model.work_service_capacity == 1.0
    assert config.attention_policy is not None
    assert config.attention_policy.selection_strategy == "quota_balance"
    assert config.exogenous_arrivals is not None
    assert config.exogenous_arrivals.enabled is True
    assert config.exogenous_arrivals.rate_per_tick == 1.0
    assert config.exogenous_arrivals.task_class_shares() == {
        "near_term_external": 0.45,
        "long_term_research": 0.25,
        "internal_improvement": 0.2,
        "housekeeping": 0.1,
    }


def test_run_writes_required_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    result = run_experiment(CONFIG, seed=1, out_dir=out_dir)

    assert result.bus_graph.number_of_nodes() == 16
    assert result.bus_graph.number_of_edges() == 15
    assert len(result.agents) == 15
    assert len(result.metrics) == 100
    assert len(result.events) == 1500
    assert result.metrics[0]["bus_density"] == 0.125
    assert result.metrics[0]["bus_mean_degree"] == 1.875
    assert result.metrics[0]["bus_degree_centralization"] == 1.0
    assert (out_dir / "manifest.yaml").is_file()
    assert (out_dir / "metrics.csv").is_file()
    assert (out_dir / "events.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["seed"] == 1
    assert manifest["agent_count"] == 15
    assert manifest["model"]["bus_edges"] == 15


def test_a0_cli_reproduces_artifacts_by_seed(tmp_path: Path) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        CONFIG,
        tmp_path,
        first_seed=23,
        second_seed=23,
        first_name="a0_first",
        second_name="a0_second",
    )
    third = tmp_path / "a0_third"
    _run_documented_cli(CONFIG, third, seed=24)
    _assert_artifacts_match_output_directory(third, _expected_artifacts(CONFIG))

    for artifact in _expected_artifacts(CONFIG):
        assert (first / artifact).read_text() == (second / artifact).read_text()
    assert (first / "metrics.csv").read_text() != (third / "metrics.csv").read_text()
    assert (first / "events.csv").read_text() != (third / "events.csv").read_text()


def test_a0_no_manifest_events_replay_lobe_transitions_and_dwell(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_no_manifest_replay"
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, out_dir, seed=29)
    _assert_artifacts_match_output_directory(
        out_dir,
        _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS),
    )
    assert not (out_dir / "manifest.yaml").exists()

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    replay_rows = _replay_a0_lobes_from_events(
        event_rows,
        ticks=int(normalized_config["run"]["ticks"]),
    )
    assert len(replay_rows) == len(metric_rows)
    for replay_row, metric_row in zip(replay_rows, metric_rows, strict=True):
        for field in (
            "queue_depth",
            "queue_delta_tick",
            "baseline_lobe_label",
            "baseline_lobe_previous_label",
            "baseline_lobe_transition",
            "baseline_lobe_transition_tick",
            "baseline_lobe_run_id",
            "baseline_lobe_current_run_length",
        ):
            assert str(replay_row[field]) == metric_row[field]

    transition_counts = Counter(
        str(row["baseline_lobe_transition"])
        for row in replay_rows
        if row["baseline_lobe_transition"] not in {"start", "stable"}
    )
    for transition, count in sorted(transition_counts.items()):
        assert f"- {transition}: {count}" in summary

    for label, dwell in _replayed_dwell_summary(replay_rows).items():
        assert (
            f"- {label}: runs={dwell['runs']}, total_ticks={dwell['total_ticks']}, "
            f"max_run={dwell['max_run']}, mean_run={dwell['mean_run']}"
        ) in summary


def test_a2_attention_run_records_policy_metrics_and_summary(tmp_path: Path) -> None:
    out_dir = tmp_path / "a2_attention_seed1"

    result = run_experiment(A2_ATTENTION, seed=1, out_dir=out_dir)

    assert result.config.attention_policy is not None
    assert len(result.metrics) == 12
    with (out_dir / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    assert rows
    assert event_rows
    assert manifest["config"]["attention_policy"] == {
        "near_term_external": 0.45,
        "long_term_research": 0.25,
        "internal_improvement": 0.2,
        "housekeeping": 0.1,
        "selection_strategy": "quota_balance",
    }
    assert manifest["model"]["attention_policy"] == {
        "classes": list(ATTENTION_CLASSES),
        "selection_strategy": "quota_balance",
        "fields": list(attention_policy_metric_fields()),
    }
    assert manifest["model"]["events"]["types"] == list(
        BASELINE_EVENT_TYPES + ATTENTION_EVENT_TYPES
    )
    assert set(attention_policy_metric_fields()) <= set(rows[0])
    assert "## Attention policy totals" in summary
    assert "- attention policy fields: " in summary
    assert "- selection strategy: quota_balance" in summary
    assert "- value-weighted completed work: " in summary
    assert "- value per completed task: " in summary
    assert "- value per work event: " in summary
    assert rows[-1]["attention_value_per_completed_task_total"]
    assert rows[-1]["attention_value_per_work_event_total"]
    for class_name in ATTENTION_CLASSES:
        assert f"attention_{class_name}_queued_tick" in rows[0]
        assert f"attention_{class_name}_worked_total" in rows[0]
        assert f"attention_{class_name}_spent_share_tick" in rows[0]
        assert f"attention_{class_name}_capture_pressure_tick" in rows[0]
        assert f"- {class_name}: target_share=" in summary
        assert "worked=" in summary
        assert "capture_pressure=" in summary
    assert rows[-1]["attention_capture_pressure_max_tick"] == "0.188889"
    capture_events = [
        row for row in event_rows
        if row["event_type"] == "attention_capture_pressure"
    ]
    assert len(capture_events) == 41
    assert capture_events[0]["attention_selected_class"] in ATTENTION_CLASSES
    assert capture_events[0]["attention_pressure_class"] in ATTENTION_CLASSES
    assert float(capture_events[0]["attention_capture_pressure"]) > 0.0
    assert "- max capture pressure: 0.188889" in summary


def test_a5_predictive_control_smoke_records_forecast_metrics(
    tmp_path: Path,
) -> None:
    first = run_experiment(
        A5_PREDICTIVE_LINEAR,
        seed=5,
        out_dir=tmp_path / "first",
    )
    second = run_experiment(
        A5_PREDICTIVE_LINEAR,
        seed=5,
        out_dir=tmp_path / "second",
    )

    assert first.config.predictive_control is not None
    assert first.config.predictive_control.condition == "linear"
    assert not first.config.hives
    assert len(first.metrics) == 18
    with (tmp_path / "first" / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    manifest = yaml.safe_load((tmp_path / "first" / "manifest.yaml").read_text())
    summary = (tmp_path / "first" / "summary.md").read_text()

    assert (tmp_path / "first" / "metrics.csv").read_text() == (
        tmp_path / "second" / "metrics.csv"
    ).read_text()
    assert first.metrics == second.metrics
    assert set(predictive_control_metric_fields()) <= set(rows[0])
    assert manifest["config"]["predictive_control"] == {
        "condition": "linear",
        "lead_ticks": 2,
        "memory_window": 3,
        "phase_shift_ticks": 5,
        "prediction_budget": 0.35,
        "signal_amplitude": 0.35,
        "signal_period": 12,
    }
    assert manifest["model"]["predictive_control"] == {
        "condition": "linear",
        "prediction_budget": 0.35,
        "lead_ticks": 2,
        "single_hive_only": True,
        "demand_stream": "deterministic periodic class-pressure shares",
        "fields": list(predictive_control_metric_fields()),
    }
    assert "- A5 predictive-control fields: " in summary
    assert "## A5 predictive control" in summary
    assert "- condition: linear" in summary
    assert "- prediction budget: 0.35" in summary
    assert rows[-1]["a5_predictive_condition"] == "linear"
    assert rows[-1]["a5_prediction_budget"] == "0.35"
    assert float(rows[-1]["a5_forecast_skill_tick"]) > 0.0
    assert float(rows[-1]["a5_forecast_skill_per_budget_tick"]) > 0.0
    assert float(rows[-1]["a5_work_future_demand_alignment_tick"]) >= 0.0
    for class_name in ATTENTION_CLASSES:
        assert f"a5_{class_name}_demand_share_tick" in rows[0]
        assert f"a5_{class_name}_future_demand_share_tick" in rows[0]
        assert f"a5_{class_name}_forecast_share_tick" in rows[0]
        assert f"a5_{class_name}_allocation_future_residual_tick" in rows[0]


def test_a5_1_prediction_spend_smoke_charges_work_budget(
    tmp_path: Path,
) -> None:
    result = run_experiment(
        A5_1_PREDICTION_SPEND_LINEAR,
        seed=5,
        out_dir=tmp_path / "a5_1",
    )

    assert result.config.predictive_control is not None
    assert result.config.predictive_control.charge_prediction_to_work is True
    with (tmp_path / "a5_1" / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (tmp_path / "a5_1" / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))
    manifest = yaml.safe_load((tmp_path / "a5_1" / "manifest.yaml").read_text())
    summary = (tmp_path / "a5_1" / "summary.md").read_text()

    assert rows[-1]["a5_prediction_charged_to_work"] == "true"
    assert float(rows[-1]["a5_prediction_work_charge_target_tick"]) == 5.25
    assert int(rows[-1]["a5_prediction_work_charged_tick"]) >= 0
    assert int(rows[-1]["a5_work_budget_remaining_tick"]) <= 15
    assert manifest["config"]["predictive_control"]["charge_prediction_to_work"] is True
    assert manifest["model"]["predictive_control"]["charge_prediction_to_work"] is True
    assert "a5_prediction_spent" in manifest["model"]["events"]["types"]
    assert "- charge prediction to work: True" in summary
    assert "- final prediction work charged: " in summary
    spend_events = [
        row for row in event_rows
        if row["event_type"] == "a5_prediction_spent"
    ]
    assert spend_events
    assert {row["action"] for row in spend_events} == {"idle"}
    assert {row["a5_prediction_spend_charged"] for row in spend_events} == {"1"}


def test_a5_1_prediction_spend_cost_scale_and_cap_are_explicit(
    tmp_path: Path,
) -> None:
    raw = yaml.safe_load(A5_1_PREDICTION_SPEND_LINEAR.read_text())
    raw["predictive_control"]["prediction_cost_scale"] = 0.5
    raw["predictive_control"]["max_prediction_work_fraction_per_tick"] = 0.1
    config_path = tmp_path / "a5_1_capped.yaml"
    config_path.write_text(yaml.safe_dump(raw, sort_keys=False))

    result = run_experiment(
        config_path,
        seed=5,
        out_dir=tmp_path / "a5_1_capped",
    )

    assert result.config.predictive_control is not None
    assert result.config.predictive_control.prediction_cost_scale == 0.5
    assert result.config.predictive_control.max_prediction_work_fraction_per_tick == 0.1
    with (tmp_path / "a5_1_capped" / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    manifest = yaml.safe_load((tmp_path / "a5_1_capped" / "manifest.yaml").read_text())
    summary = (tmp_path / "a5_1_capped" / "summary.md").read_text()

    assert float(rows[-1]["a5_prediction_cost_scale"]) == 0.5
    assert float(rows[-1]["a5_max_prediction_work_fraction_per_tick"]) == 0.1
    assert float(rows[-1]["a5_prediction_work_charge_target_tick"]) == 1.5
    assert manifest["config"]["predictive_control"]["prediction_cost_scale"] == 0.5
    assert manifest["config"]["predictive_control"]["max_prediction_work_fraction_per_tick"] == 0.1
    assert manifest["model"]["predictive_control"]["prediction_cost_scale"] == 0.5
    assert (
        manifest["model"]["predictive_control"]["max_prediction_work_fraction_per_tick"]
        == 0.1
    )
    assert "- prediction cost scale: 0.5" in summary
    assert "- max prediction work fraction per tick: 0.1" in summary


def test_a5_1_charged_comparison_generates_cost_calibration_replay_nulls(
    tmp_path: Path,
) -> None:
    rows = run_predictive_control_comparison(
        base_config=A5_1_PREDICTION_SPEND_LINEAR,
        seeds=(5,),
        out_dir=tmp_path / "a5_1a_compare",
    )

    assert [row["condition"] for row in rows] == [
        "linear_harsh_cost",
        "linear_harsh_cost_spend_only_replay",
        "linear_gentle_cost",
        "linear_gentle_cost_spend_only_replay",
        "linear_capped_cost",
        "linear_capped_cost_spend_only_replay",
        "linear_no_cost_diagnostic",
    ]
    by_condition = {row["condition"]: row for row in rows}
    assert by_condition["linear_harsh_cost"]["predictive_condition"] == "linear"
    assert (
        by_condition["linear_harsh_cost_spend_only_replay"]["predictive_condition"]
        == "spend_only_replay"
    )
    assert by_condition["linear_gentle_cost"]["prediction_cost_scale"] == 0.5
    assert by_condition["linear_gentle_cost"]["max_prediction_work_fraction_per_tick"] == 0.25
    assert by_condition["linear_capped_cost"]["prediction_cost_scale"] == 1.0
    assert by_condition["linear_capped_cost"]["max_prediction_work_fraction_per_tick"] == 0.25
    assert by_condition["linear_no_cost_diagnostic"]["charge_prediction_to_work"] == "false"

    with (
        tmp_path
        / "a5_1a_compare"
        / "configs"
        / "a5_predictive_linear_gentle_cost_spend_only_replay.yaml"
    ).open() as handle:
        replay_config = yaml.safe_load(handle)
    assert replay_config["predictive_control"]["condition"] == "spend_only_replay"
    assert replay_config["predictive_control"]["prediction_cost_scale"] == 0.5
    assert replay_config["predictive_control"]["max_prediction_work_fraction_per_tick"] == 0.25

    with (tmp_path / "a5_1a_compare" / "predictive_control_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    assert {row["effect_axis"] for row in effect_rows} >= {
        "a5_1a_spend_only_replay_null",
        "a5_1a_cost_scale",
        "a5_1a_cost_cap",
        "a5_1a_no_cost_diagnostic",
    }
    summary = (tmp_path / "a5_1a_compare" / "summary.md").read_text()
    assert "linear_gentle_cost_spend_only_replay" in summary
    assert "cost-matched replay nulls" in summary


def test_a5_predictive_control_comparison_runs_matched_conditions(
    tmp_path: Path,
) -> None:
    first_rows = run_predictive_control_comparison(
        seeds=(5, 6),
        out_dir=tmp_path / "first",
    )
    second_rows = run_predictive_control_comparison(
        seeds=(5, 6),
        out_dir=tmp_path / "second",
    )

    assert first_rows == second_rows
    assert [row["condition"] for row in first_rows] == [
        "reactive",
        "linear",
        "nonlinear",
        "nonlinear_high_budget",
        "oracle",
        "shuffled",
        "nonlinear_shuffled",
        "nonlinear_high_budget_shuffled",
    ]
    assert {row["run_count"] for row in first_rows} == {2}
    assert (tmp_path / "first" / "reactive_seed5" / "metrics.csv").is_file()
    assert (tmp_path / "first" / "configs" / "a5_predictive_oracle.yaml").is_file()
    assert (
        tmp_path / "first" / "configs" / "a5_predictive_nonlinear_shuffled.yaml"
    ).is_file()
    assert (
        tmp_path
        / "first"
        / "configs"
        / "a5_predictive_nonlinear_high_budget_shuffled.yaml"
    ).is_file()

    with (tmp_path / "first" / "predictive_control_comparison_metrics.csv").open() as handle:
        comparison_rows = list(csv.DictReader(handle))
    with (tmp_path / "first" / "predictive_control_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    summary = (tmp_path / "first" / "summary.md").read_text()
    oracle_config = yaml.safe_load(
        (tmp_path / "first" / "configs" / "a5_predictive_oracle.yaml").read_text()
    )
    high_budget_config = yaml.safe_load(
        (
            tmp_path
            / "first"
            / "configs"
            / "a5_predictive_nonlinear_high_budget.yaml"
        ).read_text()
    )

    assert set(comparison_rows[0]) == set(A5_PREDICTIVE_COMPARISON_FIELDS)
    assert set(effect_rows[0]) == set(A5_PREDICTIVE_EFFECT_FIELDS)
    assert len(comparison_rows) == 8
    assert len(effect_rows) == 9
    assert oracle_config["predictive_control"]["condition"] == "oracle"
    assert oracle_config["predictive_control"]["prediction_budget"] == 1.0
    assert high_budget_config["predictive_control"]["condition"] == "nonlinear_high_budget"
    assert high_budget_config["predictive_control"]["prediction_budget"] == 0.85
    assert high_budget_config["predictive_control"]["memory_window"] == 4
    assert "- scope: single-hive matched-demand pilot" in summary
    assert "## Condition Means" in summary
    assert "oracle minus reactive" in summary
    assert "nonlinear_shuffled" in summary
    assert "nonlinear_high_budget_shuffled" in summary


def test_a5_residual_accounting_analyzes_existing_comparison(
    tmp_path: Path,
) -> None:
    run_predictive_control_comparison(
        seeds=(5, 6),
        out_dir=tmp_path / "compare",
    )
    result = run_a5_residual_accounting_analysis(
        compare_dir=tmp_path / "compare",
        out_dir=tmp_path / "analysis",
    )

    assert result["condition_count"] == 8
    assert result["seed_count"] == 2
    assert result["metric_rows"] > 0
    assert result["effect_rows"] > 0

    with (tmp_path / "analysis" / "a5_residual_accounting_metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (tmp_path / "analysis" / "a5_residual_accounting_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    summary = (tmp_path / "analysis" / "summary.md").read_text()

    assert set(metric_rows[0]) == set(A5_RESIDUAL_ACCOUNTING_METRIC_FIELDS)
    assert set(effect_rows[0]) == set(A5_RESIDUAL_ACCOUNTING_EFFECT_FIELDS)
    assert {
        row["control_level"]
        for row in metric_rows
        if row["endpoint"] == "residual_state_predictability_r2"
    } == {"raw", "clock_demand", "load_opportunity", "full_accounting"}
    assert {
        "residual_state_lag2_autocorr",
        "residual_state_return_time_mean",
        "residual_state_return_time_entropy",
        "attention_starvation_count_final",
        "residual_state_compression_ratio",
    } <= {row["endpoint"] for row in metric_rows}
    assert any(
        row["contrast"] == "linear_minus_reactive"
        and row["control_level"] == "full_accounting"
        and row["endpoint"] == "residual_state_predictability_r2"
        for row in effect_rows
    )
    assert any(
        row["contrast"] == "oracle_minus_linear"
        and row["control_level"] == "full_accounting"
        and row["endpoint"] == "residual_state_predictability_r2"
        for row in effect_rows
    )
    assert any(
        row["contrast"] == "nonlinear_minus_nonlinear_shuffled"
        and row["control_level"] == "full_accounting"
        and row["endpoint"] == "residual_state_predictability_r2"
        for row in effect_rows
    )
    assert any(
        row["contrast"] == "nonlinear_high_budget_minus_nonlinear_high_budget_shuffled"
        and row["control_level"] == "full_accounting"
        and row["endpoint"] == "residual_state_predictability_r2"
        for row in effect_rows
    )
    assert "- scope: read-only single-hive A5 diagnostics" in summary
    assert "## Promotion Rule Audit" in summary
    assert "full accounting compression ratio" in summary
    assert "compression_vs_reactive=" in summary
    assert "compression_vs_shuffled=" in summary
    assert "Preregistered confirmatory guardrails" in summary
    assert any(
        row["endpoint"] == "attention_near_term_external_completed_final"
        for row in metric_rows
    )
    assert "promotion_satisfied=" in summary


def test_a5_residual_accounting_analyzes_a5_1a_cost_calibration_grid(
    tmp_path: Path,
) -> None:
    run_predictive_control_comparison(
        base_config=A5_1_PREDICTION_SPEND_LINEAR,
        seeds=(5, 6),
        out_dir=tmp_path / "a5_1a_compare",
    )
    result = run_a5_residual_accounting_analysis(
        compare_dir=tmp_path / "a5_1a_compare",
        out_dir=tmp_path / "a5_1a_analysis",
    )

    assert result["condition_count"] == 7
    assert result["seed_count"] == 2
    with (tmp_path / "a5_1a_analysis" / "a5_residual_accounting_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    assert "linear_gentle_cost_minus_linear_gentle_cost_spend_only_replay" in {
        row["contrast"] for row in effect_rows
    }
    summary = (tmp_path / "a5_1a_analysis" / "summary.md").read_text()
    assert "A5.1a audit: fail closed unless" in summary
    assert "skill_vs_spend_only_null=" in summary
    assert "compression_vs_spend_only_null=" in summary


def test_a2_exogenous_arrivals_run_records_accounting_and_reproduces(
    tmp_path: Path,
) -> None:
    first = run_experiment(
        A2_EXOGENOUS_ARRIVALS,
        seed=23,
        out_dir=tmp_path / "first",
    )
    second = run_experiment(
        A2_EXOGENOUS_ARRIVALS,
        seed=23,
        out_dir=tmp_path / "second",
    )

    with (tmp_path / "first" / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (tmp_path / "first" / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))
    manifest = yaml.safe_load((tmp_path / "first" / "manifest.yaml").read_text())
    summary = (tmp_path / "first" / "summary.md").read_text()

    assert first.metrics == second.metrics
    assert first.events == second.events
    assert (tmp_path / "first" / "metrics.csv").read_text() == (
        tmp_path / "second" / "metrics.csv"
    ).read_text()
    assert set(EXOGENOUS_ARRIVAL_METRIC_FIELDS) <= set(rows[0])
    assert manifest["config"]["exogenous_arrivals"] == {
        "enabled": True,
        "rate_per_tick": 1.0,
        "task_class_shares": {
            "near_term_external": 0.45,
            "long_term_research": 0.25,
            "internal_improvement": 0.2,
            "housekeeping": 0.1,
        },
    }
    assert manifest["model"]["exogenous_arrivals"]["rng_stream"] == {
        "agent_action_stream": "numpy.default_rng(seed)",
        "exogenous_arrival_stream": (
            "numpy.default_rng(SeedSequence([seed, 0xE906E, 0xA2]))"
        ),
        "separated_from_agent_actions": True,
    }
    assert manifest["model"]["exogenous_arrivals"]["event_types"] == list(
        EXOGENOUS_ARRIVAL_EVENT_TYPES
    )
    assert manifest["model"]["exogenous_arrivals"]["fields"] == list(
        EXOGENOUS_ARRIVAL_METRIC_FIELDS
    )
    assert "exogenous_task_arrived" in manifest["model"]["events"]["types"]
    exogenous_events = [
        row for row in event_rows
        if row["event_type"] == "exogenous_task_arrived"
    ]
    assert exogenous_events
    assert exogenous_events[0]["action"] == "exogenous_arrival"
    assert exogenous_events[0]["task_class"] in ATTENTION_CLASSES
    assert int(rows[-1]["exogenous_tasks_created_total"]) == len(exogenous_events)
    assert int(rows[-1]["tasks_created_total"]) == (
        int(rows[-1]["agent_tasks_created_total"])
        + int(rows[-1]["exogenous_tasks_created_total"])
    )
    assert "## Exogenous arrival totals" in summary
    assert "- exogenous tasks: " in summary


def test_a2_exogenous_arrivals_use_independent_rng_stream_for_agent_actions() -> None:
    baseline_config = load_config(A2_ATTENTION)
    exogenous_config = OmegaConfig(
        run=baseline_config.run,
        model=baseline_config.model,
        outputs=baseline_config.outputs,
        attention_policy=baseline_config.attention_policy,
        exogenous_arrivals=ExogenousArrivalsConfig(
            enabled=True,
            rate_per_tick=0.0,
            near_term_external=0.45,
            long_term_research=0.25,
            internal_improvement=0.2,
            housekeeping=0.1,
        ),
    )

    baseline = simulate(baseline_config, seed=17)
    exogenous_zero_rate = simulate(exogenous_config, seed=17)

    assert exogenous_zero_rate.events == baseline.events
    for baseline_row, exogenous_row in zip(
        baseline.metrics,
        exogenous_zero_rate.metrics,
        strict=True,
    ):
        common_fields = set(baseline_row) & set(exogenous_row)
        assert {
            field: exogenous_row[field]
            for field in common_fields
        } == {
            field: baseline_row[field]
            for field in common_fields
        }
        assert exogenous_row["exogenous_tasks_created_tick"] == 0
        assert exogenous_row["agent_tasks_created_tick"] == baseline_row[
            "tasks_created_tick"
        ]


def test_queue_blind_label_uses_agent_created_count_when_available() -> None:
    row = {
        "tasks_worked_tick": "1",
        "tasks_created_tick": "12",
        "agent_tasks_created_tick": "0",
        "messages_sent_tick": "2",
        "idle_tick": "0",
    }

    assert _queue_blind_label(row) == "coordination"


def test_a2_exogenous_arrival_calibration_writes_accounting_report(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_exogenous_arrival_calibration"

    rows = run_exogenous_arrival_calibration(
        candidate_rates=(0.0, 1.0, 2.0),
        seeds=(1, 2),
        out_dir=out_dir,
    )

    assert len(rows) == 3
    assert [row["rate_per_tick"] for row in rows] == [0.0, 1.0, 2.0]
    assert (out_dir / "exogenous_arrival_calibration.csv").is_file()
    assert (out_dir / "summary.md").is_file()
    assert (out_dir / "target_control" / "seed1" / "metrics.csv").is_file()
    assert (out_dir / "exogenous_rate_1p0" / "seed2" / "summary.md").is_file()

    with (out_dir / "exogenous_arrival_calibration.csv").open() as handle:
        csv_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert list(csv_rows[0]) == list(EXOGENOUS_CALIBRATION_FIELDS)
    assert int(csv_rows[0]["seed_count"]) == 2
    assert float(csv_rows[1]["exogenous_tasks_created_mean"]) > 0.0
    assert float(csv_rows[2]["tasks_created_mean"]) > float(
        csv_rows[1]["tasks_created_mean"]
    )
    assert csv_rows[1]["target_label"] in {
        "endogenous_control",
        "low_exogenous_target",
        "high_pressure_target",
        "extreme_pressure_target",
    }
    assert "## Coupled-pressure targets" in summary
    assert "## Candidate accounting" in summary
    assert "## Provisional frozen rates" in summary
    assert "total created-task mean only" in summary


def test_a2_frozen_exogenous_arrival_configs_use_calibrated_rates() -> None:
    expected_rates = {
        A2_EXOGENOUS_ARRIVALS_LOW: 1.0,
        A2_EXOGENOUS_ARRIVALS_MEDIUM: 2.0,
        A2_EXOGENOUS_ARRIVALS_HIGH: 3.0,
    }

    for config_path, expected_rate in expected_rates.items():
        config = load_config(config_path)

        assert config.model.task_creation_pressure == 1.0
        assert config.model.work_service_capacity == 1.0
        assert config.attention_policy is not None
        assert config.attention_policy.selection_strategy == "quota_balance"
        assert config.attention_policy.shares() == {
            "near_term_external": 0.45,
            "long_term_research": 0.25,
            "internal_improvement": 0.2,
            "housekeeping": 0.1,
        }
        assert config.exogenous_arrivals is not None
        assert config.exogenous_arrivals.enabled is True
        assert config.exogenous_arrivals.rate_per_tick == expected_rate
        assert config.exogenous_arrivals.task_class_shares() == {
            "near_term_external": 0.45,
            "long_term_research": 0.25,
            "internal_improvement": 0.2,
            "housekeeping": 0.1,
        }


def test_a2_exogenous_arrival_comparison_runner_writes_scaffold_summary(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_exogenous_arrival_compare"

    rows = run_exogenous_arrival_comparison(seeds=(1,), out_dir=out_dir)

    assert [row["condition"] for row in rows] == [
        "endogenous_control",
        "exogenous_low",
        "exogenous_medium",
        "exogenous_high",
    ]
    assert [row["rate_per_tick"] for row in rows] == [0.0, 1.0, 2.0, 3.0]
    assert (out_dir / "exogenous_arrival_comparison_metrics.csv").is_file()
    assert (out_dir / "exogenous_arrival_effects.csv").is_file()
    assert (out_dir / "summary.md").is_file()
    assert (out_dir / "endogenous_control_seed1" / "metrics.csv").is_file()
    assert (out_dir / "exogenous_high_seed1" / "summary.md").is_file()

    with (out_dir / "exogenous_arrival_comparison_metrics.csv").open() as handle:
        csv_rows = list(csv.DictReader(handle))
    with (out_dir / "exogenous_arrival_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(csv_rows) == 4
    assert len(effect_rows) == 3
    assert float(csv_rows[0]["agent_tasks_created_mean"]) == float(
        csv_rows[0]["tasks_created_mean"]
    )
    assert float(csv_rows[0]["exogenous_tasks_created_mean"]) == 0.0
    assert float(csv_rows[-1]["exogenous_tasks_created_mean"]) > 0.0
    assert effect_rows[-1]["queue_blind_transition_entropy_mean_delta"]
    assert "## Load and action accounting" in summary
    assert "## Trajectory summaries" in summary
    assert "## Endogenous-control deltas" in summary
    assert "frozen-rate holdout scaffold" in summary


def test_a2_exogenous_arrival_comparison_headers_match_declared_fields(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_exogenous_arrival_compare"

    run_exogenous_arrival_comparison(seeds=(1,), out_dir=out_dir)

    with (out_dir / "exogenous_arrival_comparison_metrics.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(EXOGENOUS_COMPARISON_FIELDS)

    with (out_dir / "exogenous_arrival_effects.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(EXOGENOUS_EFFECT_FIELDS)


def test_a2_exogenous_arrival_comparison_is_reproducible(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_exogenous_arrival_comparison(seeds=(1, 2), out_dir=first)
    run_exogenous_arrival_comparison(seeds=(1, 2), out_dir=second)

    assert (first / "exogenous_arrival_comparison_metrics.csv").read_text() == (
        second / "exogenous_arrival_comparison_metrics.csv"
    ).read_text()
    assert (first / "exogenous_arrival_effects.csv").read_text() == (
        second / "exogenous_arrival_effects.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_exogenous_arrival_control_analysis_writes_bootstrap_and_nulls(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    out_dir = tmp_path / "controls"
    run_exogenous_arrival_comparison(seeds=(1, 2), out_dir=source)

    rows = run_exogenous_arrival_control_analysis(
        exogenous_arrival_dir=source,
        out_dir=out_dir,
        bootstrap_reps=7,
        null_reps=5,
        random_seed=11,
    )

    assert [row["condition"] for row in rows] == [
        "endogenous_control",
        "exogenous_low",
        "exogenous_medium",
        "exogenous_high",
    ]
    assert (out_dir / "exogenous_arrival_control_metrics.csv").is_file()
    assert (out_dir / "exogenous_arrival_control_bootstrap.csv").is_file()
    assert (out_dir / "exogenous_arrival_control_nulls.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "exogenous_arrival_control_bootstrap.csv").open() as handle:
        bootstrap_rows = list(csv.DictReader(handle))
    with (out_dir / "exogenous_arrival_control_nulls.csv").open() as handle:
        null_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(bootstrap_rows) == 3 * 8
    assert len(null_rows) == 4
    assert {
        row["metric"] for row in bootstrap_rows if row["high_label"] == "exogenous_high"
    } >= {
        "queue_depth_per_created_task",
        "queue_blind_transition_entropy",
        "queue_blind_task_generation_dwell_share",
    }
    assert "label-count-preserving baseline-lobe shuffles" in summary
    assert "queue-blind labels use agent_tasks_created_tick" in summary


def test_a2_exogenous_arrival_control_analysis_headers_match_declared_fields(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    out_dir = tmp_path / "controls"
    run_exogenous_arrival_comparison(seeds=(1,), out_dir=source)

    run_exogenous_arrival_control_analysis(
        exogenous_arrival_dir=source,
        out_dir=out_dir,
        bootstrap_reps=3,
        null_reps=2,
    )

    with (out_dir / "exogenous_arrival_control_metrics.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(EXOGENOUS_CONTROL_METRIC_FIELDS)
    with (out_dir / "exogenous_arrival_control_bootstrap.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(EXOGENOUS_CONTROL_BOOTSTRAP_FIELDS)
    with (out_dir / "exogenous_arrival_control_nulls.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(EXOGENOUS_CONTROL_NULL_FIELDS)


def test_a2_exogenous_arrival_control_analysis_is_reproducible(tmp_path: Path) -> None:
    source = tmp_path / "source"
    first = tmp_path / "first"
    second = tmp_path / "second"
    run_exogenous_arrival_comparison(seeds=(1, 2), out_dir=source)

    run_exogenous_arrival_control_analysis(
        exogenous_arrival_dir=source,
        out_dir=first,
        bootstrap_reps=7,
        null_reps=5,
        random_seed=19,
    )
    run_exogenous_arrival_control_analysis(
        exogenous_arrival_dir=source,
        out_dir=second,
        bootstrap_reps=7,
        null_reps=5,
        random_seed=19,
    )

    for name in (
        "exogenous_arrival_control_metrics.csv",
        "exogenous_arrival_control_bootstrap.csv",
        "exogenous_arrival_control_nulls.csv",
        "summary.md",
    ):
        assert (first / name).read_text() == (second / name).read_text()


def test_a2_attention_cli_reproduces_metrics_across_same_seed(tmp_path: Path) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        A2_ATTENTION,
        tmp_path,
        first_seed=23,
        second_seed=23,
        first_name="a2_attention_first",
        second_name="a2_attention_second",
    )

    assert (first / "metrics.csv").read_text() == (second / "metrics.csv").read_text()
    assert (first / "events.csv").read_text() == (second / "events.csv").read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_random_available_scheduler_is_seeded_and_distinct(
    tmp_path: Path,
) -> None:
    quota = run_experiment(A2_ATTENTION, seed=23, out_dir=tmp_path / "quota")
    random_first = run_experiment(
        A2_ATTENTION_RANDOM_AVAILABLE,
        seed=23,
        out_dir=tmp_path / "random_first",
    )
    random_second = run_experiment(
        A2_ATTENTION_RANDOM_AVAILABLE,
        seed=23,
        out_dir=tmp_path / "random_second",
    )

    random_manifest = yaml.safe_load((tmp_path / "random_first" / "manifest.yaml").read_text())
    random_summary = (tmp_path / "random_first" / "summary.md").read_text()

    assert random_first.config.attention_policy is not None
    assert random_first.config.attention_policy.selection_strategy == "random_available"
    assert random_first.metrics == random_second.metrics
    assert random_first.events == random_second.events
    assert [event["task_id"] for event in random_first.events if event["event_type"] == "task_worked"] != [
        event["task_id"] for event in quota.events if event["event_type"] == "task_worked"
    ]
    assert random_manifest["model"]["attention_policy"]["selection_strategy"] == "random_available"
    assert random_manifest["config"]["attention_policy"]["selection_strategy"] == "random_available"
    assert "- selection strategy: random_available" in random_summary


def test_a2_attention_comparison_shifts_work_toward_research(tmp_path: Path) -> None:
    smoke = run_experiment(A2_ATTENTION, seed=23, out_dir=tmp_path / "a2_attention_smoke")
    research_heavy = run_experiment(
        A2_ATTENTION_RESEARCH_HEAVY,
        seed=23,
        out_dir=tmp_path / "a2_attention_research_heavy",
    )

    smoke_last = smoke.metrics[-1]
    research_last = research_heavy.metrics[-1]

    assert (
        research_last["attention_long_term_research_completed_total"]
        > smoke_last["attention_long_term_research_completed_total"]
    )
    assert (
        research_last["attention_near_term_external_completed_total"]
        < smoke_last["attention_near_term_external_completed_total"]
    )
    assert (
        research_last["attention_value_weighted_completed_total"]
        < smoke_last["attention_value_weighted_completed_total"]
    )
    assert (
        research_last["queued_task_age_mean_tick"]
        > smoke_last["queued_task_age_mean_tick"]
    )
    assert (
        "## Attention policy totals"
        in (tmp_path / "a2_attention_research_heavy" / "summary.md").read_text()
    )


def test_a2_attention_comparison_runner_writes_aggregate_summary(tmp_path: Path) -> None:
    out_dir = tmp_path / "a2_attention_compare"

    rows = run_comparison(seeds=(1, 2), out_dir=out_dir)

    assert len(rows) == 6
    assert {row["policy"] for row in rows} == {
        "baseline",
        "research_heavy",
        "internal_improvement",
    }
    assert (out_dir / "comparison_metrics.csv").is_file()
    assert (out_dir / "summary.md").is_file()
    for policy in ("baseline", "research_heavy", "internal_improvement"):
        for seed in (1, 2):
            assert (out_dir / f"{policy}_seed{seed}" / "metrics.csv").is_file()

    with (out_dir / "comparison_metrics.csv").open() as handle:
        csv_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(csv_rows) == 6
    assert csv_rows[0]["value_weighted_completed_total"]
    assert csv_rows[0]["value_per_completed_task_total"]
    assert csv_rows[0]["value_per_work_event_total"]
    assert csv_rows[0]["queue_depth_trajectory"].count("|") == 11
    assert csv_rows[0]["queued_task_age_mean_trajectory"].count("|") == 11
    assert csv_rows[0]["value_weighted_completed_total_trajectory"].count("|") == 11
    assert csv_rows[0]["value_per_completed_task_total_trajectory"].count("|") == 11
    assert csv_rows[0]["value_per_work_event_total_trajectory"].count("|") == 11
    assert csv_rows[0]["attention_capture_pressure_max_trajectory"].count("|") == 11
    assert csv_rows[0]["queue_depth_step_deltas"].count("|") == 10
    assert csv_rows[0]["queued_task_age_mean_step_deltas"].count("|") == 10
    assert csv_rows[0]["value_weighted_completed_total_step_deltas"].count("|") == 10
    assert csv_rows[0]["value_per_completed_task_total_step_deltas"].count("|") == 10
    assert csv_rows[0]["value_per_work_event_total_step_deltas"].count("|") == 10
    assert csv_rows[0]["attention_capture_pressure_max_step_deltas"].count("|") == 10
    assert csv_rows[0]["phase_space_regime_dwell_runs"]
    assert csv_rows[0]["phase_space_longest_dwell_label"] in csv_rows[0][
        "phase_space_regime_dwell_runs"
    ]
    assert int(csv_rows[0]["phase_space_longest_dwell_steps"]) >= 1
    assert int(csv_rows[0]["phase_space_turning_point_count"]) >= 0
    assert _step_deltas(csv_rows[0]["queue_depth_trajectory"]) == csv_rows[0][
        "queue_depth_step_deltas"
    ]
    assert _step_deltas(csv_rows[0]["queued_task_age_mean_trajectory"]) == csv_rows[0][
        "queued_task_age_mean_step_deltas"
    ]
    assert _step_deltas(csv_rows[0]["value_weighted_completed_total_trajectory"]) == csv_rows[0][
        "value_weighted_completed_total_step_deltas"
    ]
    assert _step_deltas(csv_rows[0]["value_per_completed_task_total_trajectory"]) == csv_rows[0][
        "value_per_completed_task_total_step_deltas"
    ]
    assert _step_deltas(csv_rows[0]["value_per_work_event_total_trajectory"]) == csv_rows[0][
        "value_per_work_event_total_step_deltas"
    ]
    assert _step_deltas(csv_rows[0]["attention_capture_pressure_max_trajectory"]) == csv_rows[0][
        "attention_capture_pressure_max_step_deltas"
    ]
    assert csv_rows[0]["attention_capture_pressure_max_trajectory"].split("|")[-1] == csv_rows[0][
        "attention_capture_pressure_max_final"
    ]
    assert csv_rows[0]["attention_capture_pressure_peak"] == str(
        max(float(value) for value in csv_rows[0]["attention_capture_pressure_max_trajectory"].split("|"))
    )
    for class_name in ATTENTION_CLASSES:
        trajectory_field = f"{class_name}_completed_total_trajectory"
        assert csv_rows[0][trajectory_field].count("|") == 11
        assert csv_rows[0][trajectory_field].split("|")[-1] == csv_rows[0][
            f"{class_name}_completed_total"
        ]
        worked_trajectory_field = f"{class_name}_worked_total_trajectory"
        assert csv_rows[0][worked_trajectory_field].count("|") == 11
        assert csv_rows[0][worked_trajectory_field].split("|")[-1] == csv_rows[0][
            f"{class_name}_worked_total"
        ]
        capture_trajectory_field = f"{class_name}_capture_pressure_trajectory"
        assert csv_rows[0][capture_trajectory_field].count("|") == 11
    assert "## Policy means" in summary
    assert "## Phase-space regimes" in summary
    assert "## Phase-space regime counts" in summary
    assert "## Phase-space regime distribution deltas vs baseline" in summary
    assert "## Phase-space dwell and turning points" in summary
    assert "## Policy deltas vs baseline" in summary
    assert "trajectory_final_queue_depth_mean=" in summary
    assert "trajectory_final_value_weighted_completed_mean=" in summary
    assert "trajectory_final_value_per_completed_task_mean=" in summary
    assert "trajectory_final_value_per_work_event_mean=" in summary
    assert "capture_pressure_max_final_mean=" in summary
    assert "capture_pressure_mean_over_ticks_mean=" in summary
    assert "capture_pressure_peak_mean=" in summary
    assert "queue_depth_step_delta_mean=" in summary
    assert "queued_task_age_mean_step_delta_mean=" in summary
    assert "value_weighted_step_delta_mean=" in summary
    assert "value_per_completed_task_step_delta_mean=" in summary
    assert "value_per_work_event_step_delta_mean=" in summary
    assert "capture_pressure_max_step_delta_mean=" in summary
    assert (
        "- baseline: label=queue_growth+stale_age_rising+value_throughput_rising, "
        "queue_depth_step_delta_sign=positive, queued_age_step_delta_sign=positive, "
        "value_throughput_step_delta_sign=positive"
    ) in summary
    assert "- baseline: total_steps=22, regime_counts=" in summary
    assert "regime_rates=" in summary
    assert (
        "queue_growth+stale_age_rising+value_throughput_rising:"
    ) in summary
    assert (
        "- research_heavy: total_steps=22, baseline_total_steps=22, "
        "regime_rate_deltas="
    ) in summary
    assert (
        "queue_growth+stale_age_rising+value_throughput_rising:0.045455"
    ) in summary
    assert "regime_count_deltas=" in summary
    assert (
        "- internal_improvement: total_steps=22, baseline_total_steps=22, "
        "regime_rate_deltas="
    ) in summary
    assert "- baseline: runs=2, turning_points_mean=" in summary
    assert "longest_dwell_labels=" in summary
    assert "- research_heavy queue-depth step delta mean: " in summary
    assert "- research_heavy queued-age step delta mean: " in summary
    assert "- research_heavy value-throughput step delta mean: " in summary
    assert "- research_heavy value-yield step delta mean: " in summary
    assert "- research_heavy value-effort step delta mean: " in summary
    assert "- research_heavy mean capture pressure: " in summary
    assert "- research_heavy peak capture pressure mean: " in summary
    assert "- research_heavy long-term research completions mean: " in summary
    assert "- research_heavy long-term research work events mean: " in summary
    assert "- internal_improvement internal-improvement completions mean: " in summary
    assert "- internal_improvement capture-pressure step delta mean: " in summary


def test_a2_attention_comparison_runner_is_reproducible(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_comparison(seeds=(1, 2), out_dir=first)
    run_comparison(seeds=(1, 2), out_dir=second)

    assert (first / "comparison_metrics.csv").read_text() == (
        second / "comparison_metrics.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_attention_comparison_runner_aggregates_research_heavy_shift(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_compare"

    run_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    baseline_research = _mean_csv_metric(
        rows,
        policy="baseline",
        field="long_term_research_completed_total",
    )
    research_heavy_research = _mean_csv_metric(
        rows,
        policy="research_heavy",
        field="long_term_research_completed_total",
    )
    baseline_value = _mean_csv_metric(
        rows,
        policy="baseline",
        field="value_weighted_completed_total",
    )
    research_heavy_value = _mean_csv_metric(
        rows,
        policy="research_heavy",
        field="value_weighted_completed_total",
    )

    assert research_heavy_research > baseline_research
    assert research_heavy_value < baseline_value


def test_a2_attention_comparison_runner_aggregates_internal_improvement_shift(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_compare"

    run_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    baseline_internal = _mean_csv_metric(
        rows,
        policy="baseline",
        field="internal_improvement_completed_total",
    )
    internal_heavy = _mean_csv_metric(
        rows,
        policy="internal_improvement",
        field="internal_improvement_completed_total",
    )
    baseline_near_term = _mean_csv_metric(
        rows,
        policy="baseline",
        field="near_term_external_completed_total",
    )
    internal_heavy_near_term = _mean_csv_metric(
        rows,
        policy="internal_improvement",
        field="near_term_external_completed_total",
    )

    assert internal_heavy > baseline_internal
    assert internal_heavy_near_term < baseline_near_term


def test_a2_attention_high_pressure_increases_creation_pressure(tmp_path: Path) -> None:
    baseline = run_experiment(A2_ATTENTION, seed=23, out_dir=tmp_path / "baseline")
    high_pressure = run_experiment(
        A2_ATTENTION_HIGH_PRESSURE,
        seed=23,
        out_dir=tmp_path / "high_pressure",
    )

    baseline_last = baseline.metrics[-1]
    high_pressure_last = high_pressure.metrics[-1]

    assert high_pressure.config.model.task_creation_pressure == 1.8
    assert (
        high_pressure_last["tasks_created_total"]
        > baseline_last["tasks_created_total"]
    )
    assert high_pressure_last["queue_depth"] > baseline_last["queue_depth"]


def test_a2_attention_medium_pressure_sits_between_normal_and_high_pressure(
    tmp_path: Path,
) -> None:
    normal = run_experiment(A2_ATTENTION, seed=23, out_dir=tmp_path / "normal")
    medium = run_experiment(
        A2_ATTENTION_MEDIUM_PRESSURE,
        seed=23,
        out_dir=tmp_path / "medium",
    )
    high = run_experiment(
        A2_ATTENTION_HIGH_PRESSURE,
        seed=23,
        out_dir=tmp_path / "high",
    )

    normal_last = normal.metrics[-1]
    medium_last = medium.metrics[-1]
    high_last = high.metrics[-1]

    assert medium.config.model.task_creation_pressure == 1.4
    assert (
        normal_last["tasks_created_total"]
        < medium_last["tasks_created_total"]
        < high_last["tasks_created_total"]
    )
    assert normal_last["queue_depth"] < medium_last["queue_depth"] < high_last["queue_depth"]


def test_a2_attention_service_capacity_changes_work_absorption(
    tmp_path: Path,
) -> None:
    low = run_experiment(
        A2_ATTENTION_LOW_SERVICE_CAPACITY_HIGH_PRESSURE,
        seed=23,
        out_dir=tmp_path / "low",
    )
    baseline = run_experiment(
        A2_ATTENTION_HIGH_PRESSURE,
        seed=23,
        out_dir=tmp_path / "baseline",
    )
    high = run_experiment(
        A2_ATTENTION_HIGH_SERVICE_CAPACITY_HIGH_PRESSURE,
        seed=23,
        out_dir=tmp_path / "high",
    )

    low_work = sum(int(row["tasks_worked_tick"]) for row in low.metrics)
    baseline_work = sum(int(row["tasks_worked_tick"]) for row in baseline.metrics)
    high_work = sum(int(row["tasks_worked_tick"]) for row in high.metrics)

    assert low.config.model.work_service_capacity == 0.7
    assert baseline.config.model.work_service_capacity == 1.0
    assert high.config.model.work_service_capacity == 1.3
    assert low_work < baseline_work < high_work
    assert low.metrics[-1]["queue_depth"] > baseline.metrics[-1]["queue_depth"] > high.metrics[-1]["queue_depth"]


def test_a2_service_capacity_comparison_runner_writes_grid_summary(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_service_capacity_compare"

    rows = run_service_capacity_comparison(seeds=(1, 2), out_dir=out_dir)

    assert len(rows) == 9
    assert {
        (row["task_creation_pressure"], row["work_service_capacity"])
        for row in rows
    } == {
        (1.0, 0.7),
        (1.0, 1.0),
        (1.0, 1.3),
        (1.8, 0.7),
        (1.8, 1.0),
        (1.8, 1.3),
        (2.2, 0.7),
        (2.2, 1.0),
        (2.2, 1.3),
    }
    assert (out_dir / "service_capacity_comparison_metrics.csv").is_file()
    assert (out_dir / "service_capacity_effects.csv").is_file()
    assert (out_dir / "summary.md").is_file()
    assert (out_dir / "normal_pressure_low_service_seed1" / "metrics.csv").is_file()
    assert (
        out_dir / "extreme_pressure_high_service_seed2" / "summary.md"
    ).is_file()

    with (out_dir / "service_capacity_comparison_metrics.csv").open() as handle:
        csv_rows = list(csv.DictReader(handle))
    with (out_dir / "service_capacity_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(csv_rows) == 9
    assert len(effect_rows) == 6
    assert {
        (row["effect_axis"], row["fixed_label"])
        for row in effect_rows
    } == {
        ("service_capacity", "normal_pressure"),
        ("service_capacity", "high_pressure"),
        ("service_capacity", "extreme_pressure"),
        ("task_creation_pressure", "low_service"),
        ("task_creation_pressure", "baseline_service"),
        ("task_creation_pressure", "high_service"),
    }
    assert effect_rows[0]["queue_depth_per_created_task_mean_delta"]
    assert effect_rows[0]["baseline_lobe_longest_dwell_ticks_mean_delta"]
    assert csv_rows[0]["queue_depth_per_created_task_mean"]
    assert csv_rows[0]["queue_depth_per_created_completed_balance_mean"]
    assert csv_rows[0]["value_per_work_event_mean"]
    assert csv_rows[0]["attention_capture_pressure_peak_mean"]
    assert csv_rows[0]["baseline_lobe_transition_count_mean"]
    assert csv_rows[0]["baseline_lobe_longest_dwell_label_counts"]
    assert "## Load-normalized backlog" in summary
    assert "## Queue age, value, and capture pressure" in summary
    assert "## Baseline lobe transition and dwell" in summary
    assert "## Fixed-pressure service-capacity effects" in summary
    assert "## Fixed-service demand-pressure effects" in summary
    assert "## Interpretation" in summary


def test_a2_service_capacity_comparison_metrics_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_service_capacity_compare"

    run_service_capacity_comparison(seeds=(1,), out_dir=out_dir)

    with (out_dir / "service_capacity_comparison_metrics.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_COMPARISON_FIELDS)

    with (out_dir / "service_capacity_effects.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_EFFECT_FIELDS)


def test_a2_service_capacity_comparison_runner_is_reproducible(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=first)
    run_service_capacity_comparison(seeds=(1, 2), out_dir=second)

    assert (first / "service_capacity_comparison_metrics.csv").read_text() == (
        second / "service_capacity_comparison_metrics.csv"
    ).read_text()
    assert (first / "service_capacity_effects.csv").read_text() == (
        second / "service_capacity_effects.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_service_capacity_trajectory_analysis_writes_grid_summary(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    out_dir = tmp_path / "a2_service_capacity_trajectory"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=source_dir)
    rows = run_service_capacity_trajectory_analysis(
        service_capacity_dir=source_dir,
        out_dir=out_dir,
    )

    assert len(rows) == 9
    assert (out_dir / "service_capacity_trajectory_metrics.csv").is_file()
    assert (out_dir / "service_capacity_trajectory_effects.csv").is_file()
    assert (out_dir / "service_capacity_trajectory_bootstrap.csv").is_file()
    assert (out_dir / "service_capacity_trajectory_nulls.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "service_capacity_trajectory_metrics.csv").open() as handle:
        trajectory_rows = list(csv.DictReader(handle))
    with (out_dir / "service_capacity_trajectory_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    with (out_dir / "service_capacity_trajectory_bootstrap.csv").open() as handle:
        bootstrap_rows = list(csv.DictReader(handle))
    with (out_dir / "service_capacity_trajectory_nulls.csv").open() as handle:
        null_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(trajectory_rows) == 9
    assert len(effect_rows) == 6
    assert len(bootstrap_rows) == 30
    assert len(null_rows) == 9
    assert trajectory_rows[0]["transition_entropy_mean"]
    assert trajectory_rows[0]["transition_entropy_normalized_mean"]
    assert trajectory_rows[0]["dwell_length_histogram"]
    assert trajectory_rows[0]["transition_pair_counts"]
    assert effect_rows[0]["backlog_growth_dwell_share_mean_delta"]
    assert bootstrap_rows[0]["ci_low"]
    assert bootstrap_rows[0]["ci_high"]
    assert bootstrap_rows[0]["sign_stability"]
    assert null_rows[0]["transition_entropy_observed_minus_null"]
    assert null_rows[0]["dwell_length_max_observed_minus_null"]
    assert "## Grid trajectory metrics" in summary
    assert "## Fixed-pressure service-capacity trajectory effects" in summary
    assert "## Fixed-service demand-pressure trajectory effects" in summary
    assert "## Paired bootstrap uncertainty" in summary
    assert "## Label-count null control" in summary


def test_a2_service_capacity_trajectory_analysis_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    out_dir = tmp_path / "a2_service_capacity_trajectory"

    run_service_capacity_comparison(seeds=(1,), out_dir=source_dir)
    run_service_capacity_trajectory_analysis(
        service_capacity_dir=source_dir,
        out_dir=out_dir,
    )

    with (out_dir / "service_capacity_trajectory_metrics.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_TRAJECTORY_FIELDS)

    with (out_dir / "service_capacity_trajectory_effects.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_TRAJECTORY_EFFECT_FIELDS)

    with (out_dir / "service_capacity_trajectory_bootstrap.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_TRAJECTORY_BOOTSTRAP_FIELDS)

    with (out_dir / "service_capacity_trajectory_nulls.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(SERVICE_CAPACITY_TRAJECTORY_NULL_FIELDS)


def test_a2_service_capacity_trajectory_analysis_is_reproducible(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=source_dir)
    run_service_capacity_trajectory_analysis(
        service_capacity_dir=source_dir,
        out_dir=first,
    )
    run_service_capacity_trajectory_analysis(
        service_capacity_dir=source_dir,
        out_dir=second,
    )

    assert (first / "service_capacity_trajectory_metrics.csv").read_text() == (
        second / "service_capacity_trajectory_metrics.csv"
    ).read_text()
    assert (first / "service_capacity_trajectory_effects.csv").read_text() == (
        second / "service_capacity_trajectory_effects.csv"
    ).read_text()
    assert (first / "service_capacity_trajectory_bootstrap.csv").read_text() == (
        second / "service_capacity_trajectory_bootstrap.csv"
    ).read_text()
    assert (first / "service_capacity_trajectory_nulls.csv").read_text() == (
        second / "service_capacity_trajectory_nulls.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_queue_blind_lobe_analysis_writes_grid_summary(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    out_dir = tmp_path / "a2_queue_blind_lobes"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=source_dir)
    rows = run_queue_blind_lobe_analysis(
        service_capacity_dir=source_dir,
        out_dir=out_dir,
    )

    assert len(rows) == 9
    assert (out_dir / "queue_blind_lobe_metrics.csv").is_file()
    assert (out_dir / "queue_blind_lobe_effects.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "queue_blind_lobe_metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "queue_blind_lobe_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(metric_rows) == 9
    assert len(effect_rows) == 6
    assert metric_rows[0]["transition_entropy_mean"]
    assert metric_rows[0]["task_generation_dwell_share_mean"]
    assert metric_rows[0]["execution_dwell_share_mean"]
    assert metric_rows[0]["dominant_queue_blind_lobe_counts"]
    assert effect_rows[0]["task_generation_dwell_share_mean_delta"]
    assert effect_rows[0]["execution_dwell_share_mean_delta"]
    assert "## Grid queue-blind lobe metrics" in summary
    assert "## Fixed-service pressure queue-blind effects" in summary
    assert "excluded inputs: queue_depth, queue_delta_tick, baseline_lobe_label" in summary


def test_a2_queue_blind_lobe_analysis_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    out_dir = tmp_path / "a2_queue_blind_lobes"

    run_service_capacity_comparison(seeds=(1,), out_dir=source_dir)
    run_queue_blind_lobe_analysis(
        service_capacity_dir=source_dir,
        out_dir=out_dir,
    )

    with (out_dir / "queue_blind_lobe_metrics.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(QUEUE_BLIND_LOBE_FIELDS)

    with (out_dir / "queue_blind_lobe_effects.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(QUEUE_BLIND_LOBE_EFFECT_FIELDS)


def test_a2_queue_blind_lobe_analysis_is_reproducible(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "a2_service_capacity_compare"
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=source_dir)
    run_queue_blind_lobe_analysis(service_capacity_dir=source_dir, out_dir=first)
    run_queue_blind_lobe_analysis(service_capacity_dir=source_dir, out_dir=second)

    assert (first / "queue_blind_lobe_metrics.csv").read_text() == (
        second / "queue_blind_lobe_metrics.csv"
    ).read_text()
    assert (first / "queue_blind_lobe_effects.csv").read_text() == (
        second / "queue_blind_lobe_effects.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a3_queue_flow_service_analysis_reads_existing_artifacts(
    tmp_path: Path,
) -> None:
    service_dir = tmp_path / "a2_service_capacity_compare"
    exogenous_dir = tmp_path / "a2_exogenous_arrival_compare"
    out_dir = tmp_path / "a3_queue_flow_service"

    run_service_capacity_comparison(seeds=(1,), out_dir=service_dir)
    run_exogenous_arrival_comparison(seeds=(1,), out_dir=exogenous_dir)
    rows = run_queue_flow_service_analysis(
        service_capacity_dir=service_dir,
        exogenous_arrival_dir=exogenous_dir,
        out_dir=out_dir,
    )

    assert len(rows) == 13
    assert (out_dir / "queue_flow_service_metrics.csv").is_file()
    assert (out_dir / "queue_flow_service_effects.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "queue_flow_service_metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "queue_flow_service_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(metric_rows) == 13
    assert len(effect_rows) == 9
    assert {
        row["source_family"]
        for row in metric_rows
    } == {"service_capacity", "exogenous_arrivals"}
    assert metric_rows[0]["queue_depth_per_created_task_mean"]
    assert metric_rows[0]["service_opportunity_completion_corr_mean"]
    assert metric_rows[0]["flow_balance_queue_delta_corr_mean"]
    assert effect_rows[-1]["queue_depth_per_created_task_mean_delta"]
    assert effect_rows[-1]["service_opportunity_completion_corr_mean_delta"]
    assert "## Service-capacity grid" in summary
    assert "## Exogenous-demand control" in summary
    assert "existing artifacts only" in summary


def test_a3_queue_flow_service_analysis_headers_match_declared_fields(
    tmp_path: Path,
) -> None:
    service_dir = tmp_path / "a2_service_capacity_compare"
    exogenous_dir = tmp_path / "a2_exogenous_arrival_compare"
    out_dir = tmp_path / "a3_queue_flow_service"

    run_service_capacity_comparison(seeds=(1,), out_dir=service_dir)
    run_exogenous_arrival_comparison(seeds=(1,), out_dir=exogenous_dir)
    run_queue_flow_service_analysis(
        service_capacity_dir=service_dir,
        exogenous_arrival_dir=exogenous_dir,
        out_dir=out_dir,
    )

    with (out_dir / "queue_flow_service_metrics.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(QUEUE_FLOW_SERVICE_FIELDS)

    with (out_dir / "queue_flow_service_effects.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(QUEUE_FLOW_SERVICE_EFFECT_FIELDS)


def test_a3_queue_flow_service_analysis_is_reproducible(
    tmp_path: Path,
) -> None:
    service_dir = tmp_path / "a2_service_capacity_compare"
    exogenous_dir = tmp_path / "a2_exogenous_arrival_compare"
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=service_dir)
    run_exogenous_arrival_comparison(seeds=(1, 2), out_dir=exogenous_dir)
    run_queue_flow_service_analysis(
        service_capacity_dir=service_dir,
        exogenous_arrival_dir=exogenous_dir,
        out_dir=first,
    )
    run_queue_flow_service_analysis(
        service_capacity_dir=service_dir,
        exogenous_arrival_dir=exogenous_dir,
        out_dir=second,
    )

    assert (first / "queue_flow_service_metrics.csv").read_text() == (
        second / "queue_flow_service_metrics.csv"
    ).read_text()
    assert (first / "queue_flow_service_effects.csv").read_text() == (
        second / "queue_flow_service_effects.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a3_lagged_service_sync_analysis_reads_existing_artifacts(
    tmp_path: Path,
) -> None:
    service_dir = tmp_path / "a2_service_capacity_compare"
    exogenous_dir = tmp_path / "a2_exogenous_arrival_compare"
    out_dir = tmp_path / "a3_lagged_service_sync"

    run_service_capacity_comparison(seeds=(1,), out_dir=service_dir)
    run_exogenous_arrival_comparison(seeds=(1,), out_dir=exogenous_dir)
    rows = run_lagged_service_sync_analysis(
        service_capacity_dir=service_dir,
        exogenous_arrival_dir=exogenous_dir,
        out_dir=out_dir,
    )

    assert len(rows) == 13
    assert (out_dir / "lagged_service_sync_metrics.csv").is_file()
    assert (out_dir / "lagged_service_sync_effects.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "lagged_service_sync_metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "lagged_service_sync_effects.csv").open() as handle:
        effect_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(metric_rows) == 13
    assert len(effect_rows) == 9
    assert {
        row["source_family"]
        for row in metric_rows
    } == {"service_capacity", "exogenous_arrivals"}
    assert metric_rows[0]["service_completion_best_lag"] in {"-1", "+1"}
    assert metric_rows[0]["service_completion_best_lagged_corr_mean"]
    assert metric_rows[0]["service_load_change_best_lagged_corr_mean"]
    assert metric_rows[0]["flow_balance_queue_delta_same_tick_corr_mean"]
    assert effect_rows[-1]["service_completion_best_lagged_corr_mean_delta"]
    assert effect_rows[-1]["service_completion_paired_seed_count"] == "1"
    assert effect_rows[-1]["service_completion_seed_median_delta"]
    assert effect_rows[-1]["service_completion_seed_bootstrap_median_ci_low"]
    assert effect_rows[-1]["service_completion_seed_bootstrap_median_ci_high"]
    assert effect_rows[-1]["service_completion_seed_sign_stability"]
    assert effect_rows[-1]["service_load_change_best_lagged_corr_mean_delta"]
    assert effect_rows[-1]["service_load_change_paired_seed_count"] == "1"
    assert effect_rows[-1]["service_load_change_seed_median_delta"]
    assert effect_rows[-1]["service_load_change_seed_bootstrap_median_ci_low"]
    assert effect_rows[-1]["service_load_change_seed_bootstrap_median_ci_high"]
    assert effect_rows[-1]["service_load_change_seed_sign_stability"]
    assert "primary endpoints: lagged service/completion" in summary
    assert "diagnostic only: same-tick created-completed balance versus queue delta" in summary
    assert "uncertainty: paired seed medians" in summary


def test_a3_lagged_service_sync_analysis_headers_match_declared_fields(
    tmp_path: Path,
) -> None:
    service_dir = tmp_path / "a2_service_capacity_compare"
    exogenous_dir = tmp_path / "a2_exogenous_arrival_compare"
    out_dir = tmp_path / "a3_lagged_service_sync"

    run_service_capacity_comparison(seeds=(1,), out_dir=service_dir)
    run_exogenous_arrival_comparison(seeds=(1,), out_dir=exogenous_dir)
    run_lagged_service_sync_analysis(
        service_capacity_dir=service_dir,
        exogenous_arrival_dir=exogenous_dir,
        out_dir=out_dir,
    )

    with (out_dir / "lagged_service_sync_metrics.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(LAGGED_SERVICE_SYNC_FIELDS)

    with (out_dir / "lagged_service_sync_effects.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(LAGGED_SERVICE_SYNC_EFFECT_FIELDS)


def test_a3_lagged_service_sync_analysis_is_reproducible(
    tmp_path: Path,
) -> None:
    service_dir = tmp_path / "a2_service_capacity_compare"
    exogenous_dir = tmp_path / "a2_exogenous_arrival_compare"
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=service_dir)
    run_exogenous_arrival_comparison(seeds=(1, 2), out_dir=exogenous_dir)
    run_lagged_service_sync_analysis(
        service_capacity_dir=service_dir,
        exogenous_arrival_dir=exogenous_dir,
        out_dir=first,
    )
    run_lagged_service_sync_analysis(
        service_capacity_dir=service_dir,
        exogenous_arrival_dir=exogenous_dir,
        out_dir=second,
    )

    assert (first / "lagged_service_sync_metrics.csv").read_text() == (
        second / "lagged_service_sync_metrics.csv"
    ).read_text()
    assert (first / "lagged_service_sync_effects.csv").read_text() == (
        second / "lagged_service_sync_effects.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_a2_service_capacity_decision_synthesis_adds_action_accounting_panel(
    tmp_path: Path,
) -> None:
    service_dir = tmp_path / "a2_service_capacity_compare"
    trajectory_dir = tmp_path / "a2_service_capacity_trajectory"
    out_md = tmp_path / "decision_synthesis.md"
    out_csv = tmp_path / "decision_synthesis.csv"

    run_service_capacity_comparison(seeds=(1, 2), out_dir=service_dir)
    run_service_capacity_trajectory_analysis(
        service_capacity_dir=service_dir,
        out_dir=trajectory_dir,
    )
    rows = run_service_capacity_decision_synthesis(
        service_capacity_dir=service_dir,
        trajectory_dir=trajectory_dir,
        out_md=out_md,
        out_csv=out_csv,
    )

    assert len(rows) == 5
    with out_csv.open() as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(DECISION_SYNTHESIS_FIELDS)
    summary = out_md.read_text()

    assert "# A2 service-capacity decision synthesis" in summary
    assert "## Load/action accounting panel" in summary
    assert "| normal_pressure | low_service |" in summary
    assert "Create actions" in summary
    assert "Work events" in summary
    assert "paired bootstrap rows: 30" in summary
    assert "strongest observed-minus-null dwell locking" in summary


def test_a2_attention_high_pressure_comparison_runner_is_reproducible(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_comparison(
        baseline_config=A2_ATTENTION_HIGH_PRESSURE,
        variant_config=A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE,
        internal_improvement_config=A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE,
        seeds=(1, 2),
        out_dir=first,
    )
    run_comparison(
        baseline_config=A2_ATTENTION_HIGH_PRESSURE,
        variant_config=A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE,
        internal_improvement_config=A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE,
        seeds=(1, 2),
        out_dir=second,
    )

    assert (first / "comparison_metrics.csv").read_text() == (
        second / "comparison_metrics.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()
    summary = (first / "summary.md").read_text()
    assert "configs/a2_attention_high_pressure.yaml" in summary
    assert "## Phase-space regime distribution deltas vs baseline" in summary


def test_a2_attention_pressure_comparison_runner_writes_fixed_policy_deltas(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    rows = run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    assert len(rows) == 3
    assert {row["policy"] for row in rows} == {
        "baseline",
        "research_heavy",
        "internal_improvement",
    }
    assert (out_dir / "normal_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "medium_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "high_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "pressure_comparison_metrics.csv").is_file()
    assert (out_dir / "pressure_response_selection.csv").is_file()
    assert (out_dir / "pressure_stability_agreement.csv").is_file()
    assert (out_dir / "pressure_stability_convergence.csv").is_file()
    assert (out_dir / "pressure_trajectory_structure.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        csv_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert len(csv_rows) == 3
    assert csv_rows[0]["normal_total_steps"] == "22"
    assert csv_rows[0]["medium_pressure_total_steps"] == "22"
    assert csv_rows[0]["high_pressure_total_steps"] == "22"
    assert csv_rows[0]["regime_rate_deltas"]
    assert csv_rows[0]["regime_count_deltas"]
    assert csv_rows[0]["queue_depth_mean_delta"]
    assert csv_rows[0]["value_per_completed_task_mean_delta"]
    assert csv_rows[0]["value_per_work_event_mean_delta"]
    assert csv_rows[0]["queue_depth_normal_to_medium_slope"]
    assert csv_rows[0]["queue_depth_medium_to_high_slope"]
    assert csv_rows[0]["queue_depth_pressure_curvature"]
    assert csv_rows[0]["value_per_completed_task_normal_to_medium_slope"]
    assert csv_rows[0]["value_per_completed_task_medium_to_high_slope"]
    assert csv_rows[0]["value_per_completed_task_pressure_curvature"]
    assert csv_rows[0]["value_per_work_event_normal_to_medium_slope"]
    assert csv_rows[0]["value_per_work_event_medium_to_high_slope"]
    assert csv_rows[0]["value_per_work_event_pressure_curvature"]
    assert csv_rows[0]["attention_capture_pressure_max_final_delta"]
    assert csv_rows[0]["attention_capture_pressure_mean_over_ticks_delta"]
    assert csv_rows[0]["attention_capture_pressure_peak_delta"]
    assert csv_rows[0]["attention_capture_pressure_max_final_normal_to_medium_slope"]
    assert csv_rows[0]["attention_capture_pressure_max_final_medium_to_high_slope"]
    assert csv_rows[0]["attention_capture_pressure_max_final_pressure_curvature"]
    assert csv_rows[0]["near_term_external_capture_pressure_final_delta"]
    assert csv_rows[0]["near_term_external_capture_pressure_mean_over_ticks_delta"]
    assert csv_rows[0]["near_term_external_capture_pressure_peak_delta"]
    assert csv_rows[0]["near_term_external_capture_pressure_final_normal_to_medium_slope"]
    assert csv_rows[0]["near_term_external_capture_pressure_final_medium_to_high_slope"]
    assert csv_rows[0]["near_term_external_capture_pressure_final_pressure_curvature"]
    assert "## Fixed-policy pressure deltas" in summary
    assert "## Most pressure-sensitive curve metric" in summary
    assert "## Pressure-curve response ranking" in summary
    assert "## Pressure-condition trajectory structure" in summary
    assert "## Value throughput vs effort interpretation" in summary
    assert "## Per-class capture-pressure interpretation" in summary
    assert "## Fixed-policy pressure curves" in summary
    assert (
        "- baseline: normal_total_steps=22, medium_pressure_total_steps=22, "
        "high_pressure_total_steps=22, "
    ) in summary
    assert "regime_rate_deltas=" in summary
    assert "- research_heavy final queue depth mean pressure delta: " in summary
    assert "- research_heavy value per completed task mean pressure delta: " in summary
    assert "- research_heavy value per work event mean pressure delta: " in summary
    assert "- baseline: value_throughput normal=" in summary
    assert "value_per_completed_task normal=" in summary
    assert "value_per_work_event normal=" in summary
    assert "- baseline reading: pressure " in summary
    assert "- internal_improvement peak queued task max age pressure delta: " in summary
    assert "- baseline final attention capture pressure delta: " in summary
    assert "- baseline mean attention capture pressure delta: " in summary
    assert "- baseline peak attention capture pressure delta: " in summary
    assert "- baseline near term external final capture pressure delta: " in summary
    assert "- baseline near term external mean capture pressure delta: " in summary
    assert "- baseline near term external peak capture pressure delta: " in summary
    assert "- baseline final queue depth pressure curve: " in summary
    assert "- baseline value per completed task pressure curve: " in summary
    assert "- baseline value per work event pressure curve: " in summary
    assert "- baseline final attention capture pressure curve: " in summary
    assert "- baseline mean attention capture pressure curve: " in summary
    assert "- baseline peak attention capture pressure curve: " in summary
    assert "- baseline near term external final capture pressure curve: " in summary
    assert "- baseline near term external mean capture pressure curve: " in summary
    assert "- baseline near term external peak capture pressure curve: " in summary
    assert "- baseline: turning_points_mean normal=" in summary
    assert "- baseline: longest_dwell_steps_mean normal=" in summary
    assert "- baseline: longest_dwell_labels normal=" in summary
    assert "normal_to_medium_slope=" in summary
    assert "medium_to_high_slope=" in summary
    assert "curvature=" in summary


def test_a2_attention_pressure_summary_includes_trajectory_structure(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "normal_pressure" / "comparison_metrics.csv").open() as handle:
        normal_rows = list(csv.DictReader(handle))

    baseline_rows = [row for row in normal_rows if row["policy"] == "baseline"]
    expected_turning_mean = round(
        sum(float(row["phase_space_turning_point_count"]) for row in baseline_rows)
        / len(baseline_rows),
        6,
    )
    expected_dwell_mean = round(
        sum(float(row["phase_space_longest_dwell_steps"]) for row in baseline_rows)
        / len(baseline_rows),
        6,
    )

    assert "## Pressure-condition trajectory structure" in summary
    assert f"- baseline: turning_points_mean normal={expected_turning_mean}" in summary
    assert f"- baseline: longest_dwell_steps_mean normal={expected_dwell_mean}" in summary
    for policy in ("baseline", "research_heavy", "internal_improvement"):
        assert f"- {policy}: longest_dwell_labels normal=" in summary


def test_a2_attention_pressure_trajectory_structure_csv_matches_condition_rows(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_trajectory_structure.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (out_dir / "normal_pressure" / "comparison_metrics.csv").open() as handle:
        normal_rows = list(csv.DictReader(handle))
    with (out_dir / "medium_pressure" / "comparison_metrics.csv").open() as handle:
        medium_rows = list(csv.DictReader(handle))
    with (out_dir / "high_pressure" / "comparison_metrics.csv").open() as handle:
        high_rows = list(csv.DictReader(handle))

    assert rows
    assert list(rows[0]) == list(PRESSURE_TRAJECTORY_STRUCTURE_FIELDS)
    assert [row["policy"] for row in rows] == [
        "baseline",
        "research_heavy",
        "internal_improvement",
    ]

    baseline = rows[0]
    normal_summary = _trajectory_structure_summary_from_csv(normal_rows, "baseline")
    medium_summary = _trajectory_structure_summary_from_csv(medium_rows, "baseline")
    high_summary = _trajectory_structure_summary_from_csv(high_rows, "baseline")

    assert baseline["normal_turning_points_mean"] == str(
        normal_summary["turning_points_mean"]
    )
    assert baseline["medium_pressure_turning_points_mean"] == str(
        medium_summary["turning_points_mean"]
    )
    assert baseline["high_pressure_turning_points_mean"] == str(
        high_summary["turning_points_mean"]
    )
    assert baseline["turning_points_high_minus_normal_delta"] == str(
        round(
            high_summary["turning_points_mean"]
            - normal_summary["turning_points_mean"],
            6,
        )
    )
    assert baseline["normal_longest_dwell_steps_mean"] == str(
        normal_summary["longest_dwell_steps_mean"]
    )
    assert baseline["medium_pressure_longest_dwell_steps_mean"] == str(
        medium_summary["longest_dwell_steps_mean"]
    )
    assert baseline["high_pressure_longest_dwell_steps_mean"] == str(
        high_summary["longest_dwell_steps_mean"]
    )
    assert baseline["longest_dwell_steps_high_minus_normal_delta"] == str(
        round(
            high_summary["longest_dwell_steps_mean"]
            - normal_summary["longest_dwell_steps_mean"],
            6,
        )
    )
    assert baseline["normal_longest_dwell_label_counts"] == normal_summary[
        "longest_dwell_labels"
    ]
    assert baseline["medium_pressure_longest_dwell_label_counts"] == medium_summary[
        "longest_dwell_labels"
    ]
    assert baseline["high_pressure_longest_dwell_label_counts"] == high_summary[
        "longest_dwell_labels"
    ]


def test_a2_attention_pressure_summary_interprets_per_class_capture_pressure(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()
    class_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if "_capture_pressure_" in field
        and any(field.startswith(f"{class_name}_") for class_name in ATTENTION_CLASSES)
        and field.endswith(
            (
                "_normal_to_medium_slope",
                "_medium_to_high_slope",
                "_pressure_curvature",
            )
        )
    ]
    candidates = [
        (
            -abs(float(row[field])),
            row["policy"],
            field,
            float(row[field]),
        )
        for row in rows
        for field in class_fields
    ]
    _, expected_policy, expected_field, _ = sorted(candidates)[0]
    expected_class = next(
        class_name
        for class_name in ATTENTION_CLASSES
        if expected_field.startswith(f"{class_name}_capture_pressure_")
    )
    statistic_and_metric = expected_field.removeprefix(
        f"{expected_class}_capture_pressure_"
    )
    metric_labels = {
        "normal_to_medium_slope": "normal_to_medium_slope",
        "medium_to_high_slope": "medium_to_high_slope",
        "pressure_curvature": "curvature",
    }
    expected_metric_suffix = next(
        suffix
        for suffix in metric_labels
        if statistic_and_metric.endswith(f"_{suffix}")
    )
    statistic = statistic_and_metric.removesuffix(f"_{expected_metric_suffix}")

    assert "## Per-class capture-pressure interpretation" in summary
    assert (
        f"- overall class response: policy={expected_policy}, "
        f"class={expected_class.replace('_', ' ')}, "
        f"statistic={statistic.replace('_', ' ')}, "
    ) in summary
    assert f"metric={metric_labels[expected_metric_suffix]}; condition means move " in summary
    for policy in ("baseline", "research_heavy", "internal_improvement"):
        assert f"- {policy} class response: policy={policy}, " in summary


def test_a2_attention_pressure_summary_compares_per_class_prefix_responses(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"
    readme = Path("README.md").read_text()

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()
    class_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if "_capture_pressure_" in field
        and any(field.startswith(f"{class_name}_") for class_name in ATTENTION_CLASSES)
        and field.endswith(
            (
                "_normal_to_medium_slope",
                "_medium_to_high_slope",
                "_pressure_curvature",
            )
        )
    ]
    candidates = [
        (
            -abs(float(row[field])),
            row["policy"],
            field,
            float(row[field]),
        )
        for row in rows
        for field in class_fields
    ]
    _, expected_policy, expected_field, expected_value = sorted(candidates)[0]

    assert "`Per-class capture-pressure prefix comparison`" in readme
    assert "class-specific pressure-response ranking" in readme
    assert "## Per-class capture-pressure prefix comparison" in summary
    assert "- comparison: full_seeds=1,2,3, prefix_seeds=1,2" in summary
    assert (
        f"- full class top response: policy={expected_policy}, "
    ) in summary
    assert f"field={expected_field}" in summary
    assert f"value={round(expected_value, 6)}" in summary
    assert "- class top response stable across prefix: " in summary
    assert "- class top response stable across all prefixes: " in summary
    assert "- class prefix instability causes: " in summary
    assert (
        "| prefix_seeds | class_top_response | stable_with_full | "
        "instability_causes |"
    ) in summary
    assert "| 1 | policy=" in summary
    assert "| 1,2 | policy=" in summary


def test_a2_attention_pressure_summary_identifies_most_sensitive_curve_metric(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()
    curve_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if field.endswith(
            (
                "_normal_to_medium_slope",
                "_medium_to_high_slope",
                "_pressure_curvature",
            )
        )
    ]
    candidates = [
        (
            -abs(float(row[field])),
            row["policy"],
            field,
            float(row[field]),
        )
        for row in rows
        for field in curve_fields
    ]
    _, expected_policy, expected_field, expected_value = sorted(candidates)[0]

    assert "## Most pressure-sensitive curve metric" in summary
    assert f"policy={expected_policy}" in summary
    assert f"field={expected_field}" in summary
    assert f"value={round(expected_value, 6)}" in summary
    assert f"abs_value={round(abs(expected_value), 6)}" in summary


def test_a2_attention_pressure_summary_ranks_all_curve_responses(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()
    curve_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if field.endswith(
            (
                "_normal_to_medium_slope",
                "_medium_to_high_slope",
                "_pressure_curvature",
            )
        )
    ]
    candidates = [
        (
            -abs(float(row[field])),
            row["policy"],
            field,
            float(row[field]),
        )
        for row in rows
        for field in curve_fields
    ]
    _, expected_policy, expected_field, expected_value = sorted(candidates)[0]
    ranking_section = summary.split("## Pressure-curve response ranking", maxsplit=1)[1]
    ranking_section = ranking_section.split("## Top pressure-response explanation", maxsplit=1)[0]
    table_lines = [
        line
        for line in ranking_section.splitlines()
        if line.startswith("| ") and not line.startswith("| ---")
    ]

    assert "## Pressure-curve response ranking" in summary
    assert table_lines[0] == (
        "| rank | policy | observable | metric | field | value | abs_value |"
    )
    assert len(table_lines) == len(candidates) + 1
    assert table_lines[1].startswith(
        f"| 1 | {expected_policy} | "
    )
    assert f" | {expected_field} | " in table_lines[1]
    assert f" | {round(expected_value, 6)} | " in table_lines[1]
    assert f" | {round(abs(expected_value), 6)} |" in table_lines[1]


def test_a2_attention_pressure_summary_explains_top_curve_response(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()
    curve_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if field.endswith(
            (
                "_normal_to_medium_slope",
                "_medium_to_high_slope",
                "_pressure_curvature",
            )
        )
    ]
    candidates = [
        (
            -abs(float(row[field])),
            row["policy"],
            field,
            float(row[field]),
        )
        for row in rows
        for field in curve_fields
    ]
    _, expected_policy, expected_field, _ = sorted(candidates)[0]
    observable_source_fields = {
        "value_weighted_completed": "value_weighted_completed_total",
        "tasks_completed": "tasks_completed_total",
        "queue_depth": "queue_depth",
        "queued_task_age_mean_final": "queued_task_age_mean_final",
        "queued_task_age_max_peak": "queued_task_age_max_peak",
        "attention_capture_pressure_max_final": "attention_capture_pressure_max_final",
        "attention_capture_pressure_mean_over_ticks": (
            "attention_capture_pressure_mean_over_ticks"
        ),
        "attention_capture_pressure_peak": "attention_capture_pressure_peak",
    }
    expected_prefix = next(
        prefix
        for prefix in observable_source_fields
        if expected_field.startswith(f"{prefix}_")
    )
    source_field = observable_source_fields[expected_prefix]
    condition_means = {}
    for condition in ("normal_pressure", "medium_pressure", "high_pressure"):
        with (out_dir / condition / "comparison_metrics.csv").open() as handle:
            condition_rows = [
                row for row in csv.DictReader(handle)
                if row["policy"] == expected_policy
            ]
        condition_means[condition] = _mean_csv_metric(
            condition_rows,
            policy=expected_policy,
            field=source_field,
        )

    assert "## Top pressure-response explanation" in summary
    assert (
        f"- selected response: policy={expected_policy}, "
    ) in summary
    assert f"field={expected_field}" in summary
    assert (
        f"- condition means: normal={round(condition_means['normal_pressure'], 6)}, "
        f"medium_pressure={round(condition_means['medium_pressure'], 6)}, "
        f"high_pressure={round(condition_means['high_pressure'], 6)}"
    ) in summary


def test_a2_attention_pressure_summary_interprets_unstable_prefix_response(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()

    assert "## Pressure-response interpretation" in summary
    assert (
        "- full-seed interpretation: policy=internal_improvement "
        "observable=final queue depth metric=normal_to_medium_slope "
        "is the largest absolute pressure response; condition means move"
    ) in summary
    assert "normal_to_medium_slope=46.666665" in summary
    assert "medium_to_high_slope=15.833335" in summary
    assert "curvature=-30.83333" in summary
    assert "high_minus_normal_delta=25.0" in summary
    assert (
        "- prefix interpretation: instability causes=policy,observable,metric "
        "because prefix_seeds=1,2 select policy=baseline "
        "observable=value-weighted completed work metric=curvature "
        "with condition means"
    ) in summary
    assert (
        "the full seed set selects policy=internal_improvement "
        "observable=final queue depth metric=normal_to_medium_slope."
    ) in summary


def test_a2_attention_pressure_summary_compares_selected_source_metric_by_condition(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"
    readme = Path("README.md").read_text()

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()

    assert "`Pressure-condition source metric comparison`" in readme
    assert "source metric behind the selected top pressure response" in readme
    assert "## Pressure-condition source metric comparison" in summary
    assert (
        "- selected source metric: policy=internal_improvement "
        "observable=final queue depth metric=normal_to_medium_slope "
        "source_field=queue_depth"
    ) in summary
    assert (
        "| pressure_condition | source_metric_mean | source_metric_min | "
        "source_metric_max | per_seed_values |"
    ) in summary
    assert "| normal | 20.666667 | " in summary
    assert "| medium | 39.333333 | " in summary
    assert "| high | 45.666667 | " in summary
    assert "1:" in summary
    assert "2:" in summary
    assert "3:" in summary


def test_a2_attention_pressure_summary_interprets_stable_prefix_response(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"
    readme = Path("README.md").read_text()

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()

    assert "`Pressure-response interpretation` restates the full seed set" in readme
    assert "Stable prefixes report that the leading explanation is stable" in readme
    assert "## Pressure-response interpretation" in summary
    assert (
        "- full-seed interpretation: policy=baseline "
        "observable=value-weighted completed work metric=curvature "
        "is the largest absolute pressure response; condition means move "
        "56.5 -> 45.0 -> 57.5 with normal_to_medium_slope=-28.75, "
        "medium_to_high_slope=31.25, curvature=60.0, and "
        "high_minus_normal_delta=1.0."
    ) in summary
    assert (
        "- prefix interpretation: the last prefix selects the same policy, "
        "observable, and metric, so the leading pressure-response explanation "
        "is stable for the checked prefix."
    ) in summary


def test_a2_attention_pressure_summary_reports_seed_set_sensitivity(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"
    readme = Path("README.md").read_text()

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()

    assert "`Seed-set sensitivity` is a deterministic prefix check" in readme
    assert "`full_seeds` is `1,2,3` and `prefix_seeds` is `1,2`" in readme
    assert "a prefix table for every proper prefix of the configured seed set" in readme
    assert "`top response stable across prefix: true`" in readme
    assert "`top response stable across all prefixes: true`" in readme
    assert "`prefix instability causes` reports which top-response dimensions changed" in readme
    assert "pressure-response ranking should be treated as seed-set-sensitive" in readme
    assert "## Seed-set sensitivity" in summary
    assert "- comparison: full_seeds=1,2,3, prefix_seeds=1,2" in summary
    assert (
        "- full top response: policy=internal_improvement, "
        "observable=final queue depth, metric=normal_to_medium_slope, "
        "field=queue_depth_normal_to_medium_slope"
    ) in summary
    assert (
        "- prefix top response: policy=baseline, "
        "observable=value-weighted completed work, metric=curvature, "
        "field=value_weighted_completed_pressure_curvature"
    ) in summary
    assert "- top response stable across prefix: false" in summary
    assert "- top response stable across all prefixes: false" in summary
    assert "- prefix instability causes: policy,observable,metric" in summary
    assert "| prefix_seeds | top_response | stable_with_full | instability_causes |" in summary
    assert (
        "| 1 | policy=baseline, observable=value-weighted completed work, "
        "metric=curvature, field=value_weighted_completed_pressure_curvature"
    ) in summary
    assert (
        "| 1 | policy=baseline, observable=value-weighted completed work, "
        "metric=curvature, field=value_weighted_completed_pressure_curvature, "
        "value="
    ) in summary
    assert "false | policy,observable,metric |" in summary
    assert (
        "| 1,2 | policy=baseline, observable=value-weighted completed work, "
        "metric=curvature, field=value_weighted_completed_pressure_curvature"
    ) in summary


def test_a2_attention_pressure_summary_compares_global_and_class_stability(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"
    readme = Path("README.md").read_text()

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()

    assert "`Pressure-response stability agreement`" in readme
    assert "global top-response prefix stability" in readme
    assert "class-specific capture-pressure prefix stability" in readme
    assert "## Pressure-response stability agreement" in summary
    assert "## Pressure-stability convergence inspection" in summary
    assert "- comparison: full_seeds=1,2,3, prefix_seeds=1,2" in summary
    assert "- last prefix stable together: " in summary
    assert "- all prefixes stable together: " in summary
    assert "- last prefix details: global_stable=" in summary
    assert (
        "| prefix_seeds | global_stable_with_full | class_stable_with_full | "
        "stable_together | global_instability_causes | class_instability_causes |"
    ) in summary
    assert "| 1 | false | " in summary
    assert "| 1,2 | false | " in summary


def test_a2_attention_pressure_stability_agreement_csv_records_prefix_rows(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "pressure_stability_agreement.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert list(rows[0]) == list(PRESSURE_STABILITY_AGREEMENT_FIELDS)
    assert [row["full_seeds"] for row in rows] == ["1,2,3", "1,2,3"]
    assert [row["prefix_seeds"] for row in rows] == ["1", "1,2"]
    assert rows[0]["global_stable_with_full"] == "false"
    assert rows[0]["class_stable_with_full"] in {"true", "false"}
    assert rows[0]["stable_together"] in {"true", "false"}
    assert rows[0]["global_instability_causes"]
    assert rows[0]["class_instability_causes"]
    assert rows[0]["global_policy"]
    assert rows[0]["global_observable"]
    assert rows[0]["global_metric"]
    assert rows[0]["global_field"]
    assert rows[0]["class_policy"]
    assert rows[0]["class_observable"]
    assert rows[0]["class_metric"]
    assert rows[0]["class_field"].startswith(
        tuple(f"{class_name}_capture_pressure_" for class_name in ATTENTION_CLASSES)
    )


def test_a2_attention_pressure_stability_convergence_csv_summarizes_prefix_rows(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "pressure_stability_agreement.csv").open() as handle:
        agreement_rows = list(csv.DictReader(handle))
    with (out_dir / "pressure_stability_convergence.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert list(rows[0]) == list(PRESSURE_STABILITY_CONVERGENCE_FIELDS)
    assert rows[0]["full_seeds"] == "1,2,3"
    assert rows[0]["prefix_count"] == str(len(agreement_rows))
    assert rows[0]["last_prefix"] == agreement_rows[-1]["prefix_seeds"]
    assert rows[0]["last_global_stable"] == agreement_rows[-1][
        "global_stable_with_full"
    ]
    assert rows[0]["last_class_stable"] == agreement_rows[-1][
        "class_stable_with_full"
    ]
    assert rows[0]["last_stable_together"] == agreement_rows[-1]["stable_together"]
    assert rows[0]["last_both_stable"] in {"true", "false"}
    assert rows[0]["first_global_stable_prefix"]
    assert rows[0]["first_class_stable_prefix"]
    assert rows[0]["first_stable_together_prefix"]
    assert rows[0]["first_both_stable_prefix"]
    summary = (out_dir / "summary.md").read_text()
    assert (
        "- convergence vs interpretation: pressure-response interpretation selects "
        "policy=internal_improvement observable=final queue depth "
        "metric=normal_to_medium_slope; first_global_stable_prefix="
    ) in summary
    assert (
        f"last_prefix={rows[0]['last_prefix']}, "
        f"last_global_stable={rows[0]['last_global_stable']}."
    ) in summary


def test_a2_attention_pressure_comparison_metrics_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        header = next(csv.reader(handle))

    assert header == list(PRESSURE_COMPARISON_FIELDS)


def test_a2_attention_pressure_response_selection_csv_records_full_and_prefix_top_responses(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2, 3), out_dir=out_dir)

    with (out_dir / "pressure_response_selection.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert list(rows[0]) == list(PRESSURE_RESPONSE_SELECTION_FIELDS)
    assert [row["selection_scope"] for row in rows] == [
        "full",
        "prefix",
        "prefix",
        "class_full",
        "class_prefix",
        "class_prefix",
    ]
    assert [row["seeds"] for row in rows] == ["1,2,3", "1", "1,2", "1,2,3", "1", "1,2"]
    assert rows[0]["policy"] == "internal_improvement"
    assert rows[0]["observable"] == "final queue depth"
    assert rows[0]["metric"] == "normal_to_medium_slope"
    assert rows[0]["field"] == "queue_depth_normal_to_medium_slope"
    assert rows[0]["source_field"] == "queue_depth"
    assert rows[0]["stable_with_full"] == "true"
    assert rows[0]["instability_causes"] == "none"
    assert rows[0]["normal_mean"] == "20.666667"
    assert rows[0]["medium_mean"] == "39.333333"
    assert rows[0]["high_mean"] == "45.666667"
    assert rows[0]["normal_to_medium_slope"] == "46.666665"
    assert rows[0]["medium_to_high_slope"] == "15.833335"
    assert rows[0]["curvature"] == "-30.83333"
    assert rows[0]["high_minus_normal_delta"] == "25.0"
    assert rows[0]["source_metric_normal_mean"] == "20.666667"
    assert rows[0]["source_metric_medium_mean"] == "39.333333"
    assert rows[0]["source_metric_high_mean"] == "45.666667"
    assert rows[0]["source_metric_normal_per_seed_values"].startswith("1:")
    assert "|2:" in rows[0]["source_metric_normal_per_seed_values"]
    assert "|3:" in rows[0]["source_metric_normal_per_seed_values"]
    assert rows[0]["source_metric_medium_min"]
    assert rows[0]["source_metric_high_max"]
    assert rows[2]["policy"] == "baseline"
    assert rows[2]["observable"] == "value-weighted completed work"
    assert rows[2]["metric"] == "curvature"
    assert rows[2]["stable_with_full"] == "false"
    assert rows[2]["instability_causes"] == "policy,observable,metric"
    assert rows[3]["selection_scope"] == "class_full"
    assert rows[3]["field"].startswith(
        tuple(f"{class_name}_capture_pressure_" for class_name in ATTENTION_CLASSES)
    )
    assert rows[3]["stable_with_full"] == "true"
    assert rows[3]["instability_causes"] == "none"
    assert rows[5]["selection_scope"] == "class_prefix"
    assert rows[5]["field"].startswith(
        tuple(f"{class_name}_capture_pressure_" for class_name in ATTENTION_CLASSES)
    )
    assert rows[5]["stable_with_full"] in {"true", "false"}
    assert rows[5]["normal_mean"]
    assert rows[5]["high_minus_normal_delta"]


def test_a2_attention_pressure_stability_agreement_csv_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_stability_agreement.csv").open() as handle:
        header = next(csv.reader(handle))

    assert header == list(PRESSURE_STABILITY_AGREEMENT_FIELDS)


def test_a2_attention_pressure_stability_convergence_csv_header_matches_declared_fields(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)

    with (out_dir / "pressure_stability_convergence.csv").open() as handle:
        header = next(csv.reader(handle))

    assert header == list(PRESSURE_STABILITY_CONVERGENCE_FIELDS)


def test_a2_attention_pressure_comparison_curve_metrics_match_condition_means(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare"

    rows = run_pressure_comparison(seeds=(1, 2), out_dir=out_dir)
    baseline_row = next(row for row in rows if row["policy"] == "baseline")
    means = {}
    class_means = {}
    for condition in ("normal_pressure", "medium_pressure", "high_pressure"):
        with (out_dir / condition / "comparison_metrics.csv").open() as handle:
            condition_rows = [
                row for row in csv.DictReader(handle)
                if row["policy"] == "baseline"
            ]
        means[condition] = _mean_csv_metric(
            condition_rows,
            policy="baseline",
            field="queue_depth",
        )
        class_means[condition] = round(
            _mean_csv_metric(
                condition_rows,
                policy="baseline",
                field="near_term_external_capture_pressure_final",
            ),
            6,
        )

    normal_to_medium = round(
        (means["medium_pressure"] - means["normal_pressure"]) / 0.4,
        6,
    )
    medium_to_high = round(
        (means["high_pressure"] - means["medium_pressure"]) / 0.4,
        6,
    )

    assert baseline_row["queue_depth_normal_to_medium_slope"] == normal_to_medium
    assert baseline_row["queue_depth_medium_to_high_slope"] == medium_to_high
    assert baseline_row["queue_depth_pressure_curvature"] == round(
        medium_to_high - normal_to_medium,
        6,
    )

    class_normal_to_medium = round(
        (class_means["medium_pressure"] - class_means["normal_pressure"]) / 0.4,
        6,
    )
    class_medium_to_high = round(
        (class_means["high_pressure"] - class_means["medium_pressure"]) / 0.4,
        6,
    )

    assert (
        baseline_row["near_term_external_capture_pressure_final_normal_to_medium_slope"]
        == pytest.approx(class_normal_to_medium, abs=2e-6)
    )
    assert (
        baseline_row["near_term_external_capture_pressure_final_medium_to_high_slope"]
        == pytest.approx(class_medium_to_high, abs=2e-6)
    )
    assert baseline_row[
        "near_term_external_capture_pressure_final_pressure_curvature"
    ] == pytest.approx(
        round(
            class_medium_to_high - class_normal_to_medium,
            6,
        ),
        abs=2e-6,
    )


def test_a2_attention_pressure_comparison_uses_custom_pressure_axis(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_extreme_pressure_compare"

    rows = run_pressure_comparison(
        medium_pressure_baseline_config=A2_ATTENTION_HIGH_PRESSURE,
        medium_pressure_variant_config=A2_ATTENTION_RESEARCH_HEAVY_HIGH_PRESSURE,
        medium_pressure_internal_improvement_config=(
            A2_ATTENTION_INTERNAL_IMPROVEMENT_HIGH_PRESSURE
        ),
        high_pressure_baseline_config=A2_ATTENTION_EXTREME_PRESSURE,
        high_pressure_variant_config=A2_ATTENTION_RESEARCH_HEAVY_EXTREME_PRESSURE,
        high_pressure_internal_improvement_config=(
            A2_ATTENTION_INTERNAL_IMPROVEMENT_EXTREME_PRESSURE
        ),
        seeds=(1,),
        out_dir=out_dir,
    )
    baseline_row = next(row for row in rows if row["policy"] == "baseline")
    means = {}
    for condition in ("medium_pressure", "high_pressure"):
        with (out_dir / condition / "comparison_metrics.csv").open() as handle:
            condition_rows = [
                row for row in csv.DictReader(handle)
                if row["policy"] == "baseline"
            ]
        means[condition] = _mean_csv_metric(
            condition_rows,
            policy="baseline",
            field="queue_depth",
        )

    expected_slope = round(
        (means["high_pressure"] - means["medium_pressure"]) / (2.2 - 1.8),
        6,
    )

    assert baseline_row["queue_depth_medium_to_high_slope"] == expected_slope


def test_a2_attention_pressure_comparison_runner_is_reproducible(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_pressure_comparison(seeds=(1, 2), out_dir=first)
    run_pressure_comparison(seeds=(1, 2), out_dir=second)

    assert (first / "pressure_comparison_metrics.csv").read_text() == (
        second / "pressure_comparison_metrics.csv"
    ).read_text()
    assert (first / "pressure_response_selection.csv").read_text() == (
        second / "pressure_response_selection.csv"
    ).read_text()
    assert (first / "pressure_stability_agreement.csv").read_text() == (
        second / "pressure_stability_agreement.csv"
    ).read_text()
    assert (first / "pressure_stability_convergence.csv").read_text() == (
        second / "pressure_stability_convergence.csv"
    ).read_text()
    assert (first / "pressure_trajectory_structure.csv").read_text() == (
        second / "pressure_trajectory_structure.csv"
    ).read_text()
    assert (first / "summary.md").read_text() == (second / "summary.md").read_text()


def test_documented_pressure_cli_writes_pressure_layout_and_curve_summary(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare_cli"
    readme = Path("README.md").read_text()

    _run_documented_pressure_cli(out_dir, seeds=(1, 2))

    assert (out_dir / "normal_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "normal_pressure" / "summary.md").is_file()
    assert (out_dir / "medium_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "medium_pressure" / "summary.md").is_file()
    assert (out_dir / "high_pressure" / "comparison_metrics.csv").is_file()
    assert (out_dir / "high_pressure" / "summary.md").is_file()
    assert (out_dir / "pressure_comparison_metrics.csv").is_file()
    assert (out_dir / "pressure_response_selection.csv").is_file()
    assert (out_dir / "pressure_stability_agreement.csv").is_file()
    assert (out_dir / "pressure_stability_convergence.csv").is_file()
    assert (out_dir / "pressure_trajectory_structure.csv").is_file()
    assert (out_dir / "summary.md").is_file()

    with (out_dir / "pressure_comparison_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (out_dir / "pressure_trajectory_structure.csv").open() as handle:
        trajectory_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    assert "treat `policy` as the stable join key" in readme
    assert "`pressure_comparison_metrics.csv`" in readme
    assert "`pressure_trajectory_structure.csv`" in readme
    assert len(rows) == 3
    assert [row["policy"] for row in trajectory_rows] == [row["policy"] for row in rows]
    assert {row["policy"] for row in rows} == {
        "baseline",
        "research_heavy",
        "internal_improvement",
    }
    assert rows[0]["normal_total_steps"] == "22"
    assert rows[0]["medium_pressure_total_steps"] == "22"
    assert rows[0]["high_pressure_total_steps"] == "22"
    assert "## Fixed-policy pressure deltas" in summary
    assert "## Most pressure-sensitive curve metric" in summary
    assert "## Pressure-curve response ranking" in summary
    assert "## Fixed-policy pressure curves" in summary
    assert "- medium-pressure baseline config: configs/a2_attention_medium_pressure.yaml" in summary
    assert "- baseline final queue depth pressure curve: " in summary
    assert "- baseline final attention capture pressure curve: " in summary
    assert "normal_to_medium_slope=" in summary
    assert "medium_to_high_slope=" in summary
    assert "curvature=" in summary


def test_documented_pressure_cli_reproduces_top_level_artifacts(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    _run_documented_pressure_cli(first, seeds=(1, 2))
    _run_documented_pressure_cli(second, seeds=(1, 2))

    _assert_artifacts_are_byte_identical(
        first,
        second,
        [
            "pressure_comparison_metrics.csv",
            "pressure_response_selection.csv",
            "pressure_stability_agreement.csv",
            "pressure_stability_convergence.csv",
            "pressure_trajectory_structure.csv",
            "summary.md",
        ],
    )


def test_documented_pressure_cli_reproduces_source_metric_selection_fields(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    source_metric_fields = [
        field
        for field in PRESSURE_RESPONSE_SELECTION_FIELDS
        if field == "source_field" or field.startswith("source_metric_")
    ]

    _run_documented_pressure_cli(first, seeds=(1, 2, 3))
    _run_documented_pressure_cli(second, seeds=(1, 2, 3))

    with (first / "pressure_response_selection.csv").open() as first_handle:
        first_rows = list(csv.DictReader(first_handle))
    with (second / "pressure_response_selection.csv").open() as second_handle:
        second_rows = list(csv.DictReader(second_handle))

    assert first_rows
    assert len(first_rows) == len(second_rows)
    assert (first / "pressure_response_selection.csv").read_bytes() == (
        second / "pressure_response_selection.csv"
    ).read_bytes()
    assert [
        {field: row[field] for field in source_metric_fields}
        for row in first_rows
    ] == [
        {field: row[field] for field in source_metric_fields}
        for row in second_rows
    ]
    assert first_rows[0]["selection_scope"] == "full"
    assert first_rows[0]["source_field"] == "queue_depth"
    assert first_rows[0]["source_metric_normal_mean"] == "20.666667"
    assert first_rows[0]["source_metric_medium_mean"] == "39.333333"
    assert first_rows[0]["source_metric_high_mean"] == "45.666667"


def test_pressure_analysis_reads_joined_csv_pair_and_ranks_responses(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"

    run_pressure_comparison(seeds=(1, 2), out_dir=pressure_dir)
    rows = run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert len(rows) == 5
    assert (analysis_dir / "trajectory_pressure_ranking.csv").is_file()
    assert (analysis_dir / "value_yield_divergence_ranking.csv").is_file()
    assert (analysis_dir / "value_yield_divergence_stability.csv").is_file()
    assert (analysis_dir / "pressure_bootstrap_rank_stability.csv").is_file()
    assert (analysis_dir / "interpretation.csv").is_file()
    assert (analysis_dir / "summary.md").is_file()

    with (analysis_dir / "trajectory_pressure_ranking.csv").open() as handle:
        csv_rows = list(csv.DictReader(handle))
    with (analysis_dir / "value_yield_divergence_ranking.csv").open() as handle:
        divergence_rows = list(csv.DictReader(handle))
    with (analysis_dir / "value_yield_divergence_stability.csv").open() as handle:
        stability_rows = list(csv.DictReader(handle))
    with (analysis_dir / "pressure_bootstrap_rank_stability.csv").open() as handle:
        bootstrap_rows = list(csv.DictReader(handle))
    with (analysis_dir / "interpretation.csv").open() as handle:
        interpretation_rows = list(csv.DictReader(handle))
    summary = (analysis_dir / "summary.md").read_text()

    assert list(csv_rows[0]) == list(TRAJECTORY_PRESSURE_RANKING_FIELDS)
    assert list(divergence_rows[0]) == list(VALUE_YIELD_DIVERGENCE_RANKING_FIELDS)
    assert list(stability_rows[0]) == list(VALUE_YIELD_DIVERGENCE_STABILITY_FIELDS)
    assert list(bootstrap_rows[0]) == list(PRESSURE_BOOTSTRAP_RANK_STABILITY_FIELDS)
    assert list(interpretation_rows[0]) == list(INTERPRETATION_FIELDS)
    assert [row["rank"] for row in csv_rows] == ["1", "2", "3", "4", "5"]
    assert [row["rank"] for row in divergence_rows] == ["1", "2", "3", "4", "5"]
    assert csv_rows[0]["response_field"] == rows[0]["response_field"]
    assert csv_rows[0]["response_abs_value"]
    assert csv_rows[0]["trajectory_abs_delta_total"]
    assert divergence_rows[0]["value_per_completed_task_field"]
    assert divergence_rows[0]["value_per_work_event_field"]
    assert divergence_rows[0]["abs_divergence"]
    assert stability_rows[0]["full_seeds"] == "1,2"
    assert stability_rows[0]["prefix_seeds"] == "1"
    assert stability_rows[0]["stable_with_full"] in {"true", "false"}
    assert {row["selection_scope"] for row in bootstrap_rows} == {
        "class_capture_pressure",
        "global",
        "value_yield_divergence",
    }
    assert bootstrap_rows[0]["full_seeds"] == "1,2"
    assert bootstrap_rows[0]["resamples"] == "200"
    assert bootstrap_rows[0]["bootstrap_seed"] == "1"
    assert float(bootstrap_rows[0]["top_selection_probability"]) >= 0.0
    assert float(bootstrap_rows[0]["sign_stability"]) >= 0.0
    assert len(interpretation_rows) == 1
    assert interpretation_rows[0]["top_divergence_policy"] == divergence_rows[0]["policy"]
    assert interpretation_rows[0]["top_divergence_metric"] == divergence_rows[0]["metric"]
    assert (
        interpretation_rows[0]["top_divergence_stable_last_prefix"]
        == stability_rows[-1]["stable_with_full"]
    )
    assert (
        interpretation_rows[0]["top_trajectory_response_field"]
        == csv_rows[0]["response_field"]
    )
    assert "## Ranking" in summary
    assert "## Value-yield divergence ranking" in summary
    assert "## Top value-yield divergence interpretation" in summary
    assert "## Value-yield divergence prefix stability" in summary
    assert "## Bootstrap rank stability" in summary
    assert "- top divergence: " in summary
    assert "- top divergence stable across last prefix: " in summary
    assert "completion-normalized yield" in summary
    assert "effort-normalized yield" in summary
    assert "pressure_comparison_metrics.csv" not in summary


def test_pressure_analysis_five_seed_interpretation_regression(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"

    run_pressure_comparison(seeds=(1, 2, 3, 4, 5), out_dir=pressure_dir)
    run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=10)

    with (analysis_dir / "interpretation.csv").open() as handle:
        interpretation_rows = list(csv.DictReader(handle))
    summary = (analysis_dir / "summary.md").read_text()

    assert interpretation_rows == [
        {
            "top_divergence_policy": "baseline",
            "top_divergence_metric": "curvature",
            "top_divergence_value_per_completed_task_response": "0.147768",
            "top_divergence_value_per_work_event_response": "0.65523",
            "top_divergence": "-0.507462",
            "top_divergence_abs": "0.507462",
            "top_divergence_stable_last_prefix": "true",
            "top_divergence_stable_all_prefixes": "false",
            "top_divergence_full_seeds": "1,2,3,4,5",
            "top_divergence_last_prefix_seeds": "1,2,3,4",
            "top_divergence_last_prefix_instability_causes": "none",
            "top_trajectory_policy": "internal_improvement",
            "top_trajectory_response_observable": "final queue depth",
            "top_trajectory_response_metric": "normal_to_medium_slope",
            "top_trajectory_response_field": "queue_depth_normal_to_medium_slope",
            "top_trajectory_response_value": "45.0",
            "top_trajectory_response_abs_value": "45.0",
            "top_trajectory_abs_delta_total": "4.2",
        }
    ]
    assert (
        "pressure improves both yield normalizations, with a larger "
        "effort-normalized response; this is a same-direction divergence, not a "
        "completion-vs-effort tradeoff."
    ) in summary


@pytest.mark.parametrize(
    ("completed_response", "work_response", "expected"),
    [
        (
            0.25,
            -0.75,
            (
                "pressure improves completion-normalized yield while degrading "
                "effort-normalized yield"
            ),
        ),
        (
            -0.25,
            0.75,
            (
                "pressure degrades completion-normalized yield while improving "
                "effort-normalized yield"
            ),
        ),
        (
            0.0,
            0.0,
            "pressure leaves both yield normalizations unchanged",
        ),
        (
            0.0,
            0.75,
            (
                "pressure leaves completion-normalized yield unchanged while "
                "improves effort-normalized yield"
            ),
        ),
        (
            0.0,
            -0.75,
            (
                "pressure leaves completion-normalized yield unchanged while "
                "degrades effort-normalized yield"
            ),
        ),
        (
            0.25,
            0.0,
            (
                "pressure improves completion-normalized yield while leaving "
                "effort-normalized yield unchanged"
            ),
        ),
        (
            -0.25,
            0.0,
            (
                "pressure degrades completion-normalized yield while leaving "
                "effort-normalized yield unchanged"
            ),
        ),
    ],
)
def test_pressure_analysis_value_yield_branch_wording(
    completed_response: float,
    work_response: float,
    expected: str,
) -> None:
    assert _yield_divergence_interpretation(completed_response, work_response) == expected


def test_pressure_analysis_requires_pressure_input_csv_pair(tmp_path: Path) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="pressure_comparison_metrics.csv"):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert not analysis_dir.exists()


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_pressure_analysis_rejects_invalid_limit_without_partial_outputs(
    tmp_path: Path,
    limit: object,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    with pytest.raises(ValueError, match="limit must be a positive integer"):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=limit)  # type: ignore[arg-type]

    assert not analysis_dir.exists()


def test_pressure_analysis_reports_malformed_pressure_csv_schema_without_partial_outputs(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()
    pressure_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if field != "queue_depth_pressure_curvature"
    ]

    _write_pressure_analysis_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        pressure_fields,
        {"policy": "baseline"},
    )
    _write_pressure_analysis_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        {"policy": "baseline"},
    )

    with pytest.raises(
        ValueError,
        match="pressure_comparison_metrics.csv is missing required fields: "
        "queue_depth_pressure_curvature",
    ):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert not analysis_dir.exists()


def test_pressure_analysis_reports_policy_mismatch_without_partial_outputs(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    _write_pressure_analysis_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        PRESSURE_COMPARISON_FIELDS,
        {"policy": "baseline"},
    )
    _write_pressure_analysis_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        {"policy": "research_heavy"},
    )

    with pytest.raises(
        ValueError,
        match=(
            "Policy mismatch between pressure_comparison_metrics.csv and "
            "pressure_trajectory_structure.csv: missing policies in trajectory: "
            "baseline; extra policies in trajectory: research_heavy"
        ),
    ):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert not analysis_dir.exists()


@pytest.mark.parametrize(
    ("artifact_name", "pressure_overrides", "trajectory_overrides", "error"),
    [
        (
            "pressure_comparison_metrics.csv",
            [{"policy": ""}],
            [{"policy": "baseline"}],
            "pressure_comparison_metrics.csv contains a row without policy",
        ),
        (
            "pressure_comparison_metrics.csv",
            [{"policy": "baseline"}, {"policy": "baseline"}],
            [{"policy": "baseline"}],
            "pressure_comparison_metrics.csv contains duplicate policy: baseline",
        ),
        (
            "pressure_trajectory_structure.csv",
            [{"policy": "baseline"}],
            [{"policy": ""}],
            "pressure_trajectory_structure.csv contains a row without policy",
        ),
        (
            "pressure_trajectory_structure.csv",
            [{"policy": "baseline"}],
            [{"policy": "baseline"}, {"policy": "baseline"}],
            "pressure_trajectory_structure.csv contains duplicate policy: baseline",
        ),
    ],
)
def test_pressure_analysis_rejects_blank_or_duplicate_policy_keys_without_partial_outputs(
    tmp_path: Path,
    artifact_name: str,
    pressure_overrides: list[dict[str, str]],
    trajectory_overrides: list[dict[str, str]],
    error: str,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    _write_pressure_analysis_rows_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        PRESSURE_COMPARISON_FIELDS,
        pressure_overrides,
    )
    _write_pressure_analysis_rows_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        trajectory_overrides,
    )

    assert artifact_name in error
    with pytest.raises(ValueError, match=error):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert not analysis_dir.exists()


@pytest.mark.parametrize(
    "collision_artifact",
    [
        "trajectory_pressure_ranking.csv",
        "value_yield_divergence_ranking.csv",
        "value_yield_divergence_stability.csv",
        "pressure_bootstrap_rank_stability.csv",
        "interpretation.csv",
        "summary.md",
    ],
)
def test_pressure_analysis_refuses_existing_output_artifacts_without_modifying_them(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    sentinel = f"preexisting {collision_artifact} sentinel\n"

    analysis_dir.mkdir()
    (analysis_dir / collision_artifact).write_text(sentinel)

    with pytest.raises(FileExistsError, match=collision_artifact):
        run_analysis(pressure_dir=pressure_dir, out_dir=analysis_dir, limit=5)

    assert (analysis_dir / collision_artifact).read_text() == sentinel
    assert sorted(path.name for path in analysis_dir.iterdir()) == [collision_artifact]


def test_documented_pressure_analysis_cli_reproduces_ranking_artifacts(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    first = tmp_path / "first"
    second = tmp_path / "second"

    _run_documented_pressure_cli(pressure_dir, seeds=(1, 2))
    _run_documented_pressure_analysis_cli(pressure_dir, first, limit=5)
    _run_documented_pressure_analysis_cli(pressure_dir, second, limit=5)

    _assert_artifacts_are_byte_identical(
        first,
        second,
        [
            "trajectory_pressure_ranking.csv",
            "value_yield_divergence_ranking.csv",
            "value_yield_divergence_stability.csv",
            "pressure_bootstrap_rank_stability.csv",
            "interpretation.csv",
            "summary.md",
        ],
    )


def test_documented_pressure_analysis_cli_reports_missing_input_without_partial_outputs(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "pressure_comparison_metrics.csv" in completed.stderr
    assert not analysis_dir.exists()


@pytest.mark.parametrize("limit", ["0", "-1"])
def test_documented_pressure_analysis_cli_rejects_invalid_limit_without_partial_outputs(
    tmp_path: Path,
    limit: str,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            limit,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "limit must be a positive integer" in completed.stderr
    assert not analysis_dir.exists()


def test_documented_pressure_analysis_cli_reports_malformed_schema_without_partial_outputs(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()
    pressure_fields = [
        field
        for field in PRESSURE_COMPARISON_FIELDS
        if field != "queue_depth_pressure_curvature"
    ]

    _write_pressure_analysis_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        pressure_fields,
        {"policy": "baseline"},
    )
    _write_pressure_analysis_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        {"policy": "baseline"},
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert (
        "pressure_comparison_metrics.csv is missing required fields: "
        "queue_depth_pressure_curvature"
    ) in completed.stderr
    assert not analysis_dir.exists()


def test_documented_pressure_analysis_cli_reports_policy_mismatch_without_partial_outputs(
    tmp_path: Path,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    _write_pressure_analysis_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        PRESSURE_COMPARISON_FIELDS,
        {"policy": "baseline"},
    )
    _write_pressure_analysis_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        {"policy": "research_heavy"},
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert (
        "Policy mismatch between pressure_comparison_metrics.csv and "
        "pressure_trajectory_structure.csv: missing policies in trajectory: "
        "baseline; extra policies in trajectory: research_heavy"
    ) in completed.stderr
    assert not analysis_dir.exists()


@pytest.mark.parametrize(
    ("artifact_name", "pressure_overrides", "trajectory_overrides", "error"),
    [
        (
            "pressure_comparison_metrics.csv",
            [{"policy": ""}],
            [{"policy": "baseline"}],
            "pressure_comparison_metrics.csv contains a row without policy",
        ),
        (
            "pressure_comparison_metrics.csv",
            [{"policy": "baseline"}, {"policy": "baseline"}],
            [{"policy": "baseline"}],
            "pressure_comparison_metrics.csv contains duplicate policy: baseline",
        ),
        (
            "pressure_trajectory_structure.csv",
            [{"policy": "baseline"}],
            [{"policy": ""}],
            "pressure_trajectory_structure.csv contains a row without policy",
        ),
        (
            "pressure_trajectory_structure.csv",
            [{"policy": "baseline"}],
            [{"policy": "baseline"}, {"policy": "baseline"}],
            "pressure_trajectory_structure.csv contains duplicate policy: baseline",
        ),
    ],
)
def test_documented_pressure_analysis_cli_reports_blank_or_duplicate_policy_keys_without_partial_outputs(
    tmp_path: Path,
    artifact_name: str,
    pressure_overrides: list[dict[str, str]],
    trajectory_overrides: list[dict[str, str]],
    error: str,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    pressure_dir.mkdir()

    _write_pressure_analysis_rows_csv(
        pressure_dir / "pressure_comparison_metrics.csv",
        PRESSURE_COMPARISON_FIELDS,
        pressure_overrides,
    )
    _write_pressure_analysis_rows_csv(
        pressure_dir / "pressure_trajectory_structure.csv",
        PRESSURE_TRAJECTORY_STRUCTURE_FIELDS,
        trajectory_overrides,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert artifact_name in error
    assert completed.returncode != 0
    assert error in completed.stderr
    assert not analysis_dir.exists()


@pytest.mark.parametrize(
    "collision_artifact",
    [
        "trajectory_pressure_ranking.csv",
        "value_yield_divergence_ranking.csv",
        "value_yield_divergence_stability.csv",
        "pressure_bootstrap_rank_stability.csv",
        "interpretation.csv",
        "summary.md",
    ],
)
def test_documented_pressure_analysis_cli_refuses_existing_output_artifacts_without_modifying_them(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    pressure_dir = tmp_path / "pressure"
    analysis_dir = tmp_path / "analysis"
    sentinel = f"preexisting {collision_artifact} sentinel\n"

    analysis_dir.mkdir()
    (analysis_dir / collision_artifact).write_text(sentinel)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.analyze_pressure",
            "--pressure-dir",
            str(pressure_dir),
            "--out",
            str(analysis_dir),
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert collision_artifact in completed.stderr
    assert (analysis_dir / collision_artifact).read_text() == sentinel
    assert sorted(path.name for path in analysis_dir.iterdir()) == [collision_artifact]


def test_documented_pressure_cli_refuses_existing_top_level_artifacts_without_modifying_them(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a2_attention_pressure_compare_cli"

    _run_documented_pressure_cli(out_dir, seeds=(1, 2))
    original_metrics = (out_dir / "pressure_comparison_metrics.csv").read_bytes()
    original_selection = (out_dir / "pressure_response_selection.csv").read_bytes()
    original_agreement = (out_dir / "pressure_stability_agreement.csv").read_bytes()
    original_convergence = (
        out_dir / "pressure_stability_convergence.csv"
    ).read_bytes()
    original_trajectory = (out_dir / "pressure_trajectory_structure.csv").read_bytes()
    original_summary = (out_dir / "summary.md").read_bytes()

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.compare_pressure",
            "--seeds",
            "1",
            "2",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert completed.stdout == ""
    assert "already contains pressure comparison artifacts" in completed.stderr
    assert (out_dir / "pressure_comparison_metrics.csv").read_bytes() == original_metrics
    assert (out_dir / "pressure_response_selection.csv").read_bytes() == original_selection
    assert (
        (out_dir / "pressure_stability_agreement.csv").read_bytes()
        == original_agreement
    )
    assert (
        (out_dir / "pressure_stability_convergence.csv").read_bytes()
        == original_convergence
    )
    assert (
        (out_dir / "pressure_trajectory_structure.csv").read_bytes()
        == original_trajectory
    )
    assert (out_dir / "summary.md").read_bytes() == original_summary


def test_metrics_csv_records_bus_graph_summary(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    metrics_header = (out_dir / "metrics.csv").read_text().splitlines()[0].split(",")
    first_row = (out_dir / "metrics.csv").read_text().splitlines()[1].split(",")
    row = dict(zip(metrics_header, first_row))

    assert row["bus_density"] == "0.125"
    assert row["bus_mean_degree"] == "1.875"
    assert row["bus_degree_centralization"] == "1.0"
    assert "- bus density: 0.125" in (out_dir / "summary.md").read_text()
    assert "- bus mean degree: 1.875" in (out_dir / "summary.md").read_text()


def _write_pressure_analysis_csv(
    path: Path,
    fieldnames: tuple[str, ...] | list[str],
    overrides: dict[str, str],
) -> None:
    _write_pressure_analysis_rows_csv(path, fieldnames, [overrides])


def _write_pressure_analysis_rows_csv(
    path: Path,
    fieldnames: tuple[str, ...] | list[str],
    overrides_rows: list[dict[str, str]],
) -> None:
    row = {field: "0" for field in fieldnames}
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for overrides in overrides_rows:
            output_row = dict(row)
            output_row.update(overrides)
            writer.writerow(output_row)


def _mean_csv_metric(
    rows: list[dict[str, str]],
    *,
    policy: str,
    field: str,
) -> float:
    policy_rows = [row for row in rows if row["policy"] == policy]
    return sum(float(row[field]) for row in policy_rows) / len(policy_rows)


def _trajectory_structure_summary_from_csv(
    rows: list[dict[str, str]],
    policy: str,
) -> dict[str, float | str]:
    policy_rows = [row for row in rows if row["policy"] == policy]
    turning_points = [
        float(row["phase_space_turning_point_count"])
        for row in policy_rows
    ]
    dwell_steps = [
        float(row["phase_space_longest_dwell_steps"])
        for row in policy_rows
    ]
    labels = Counter(row["phase_space_longest_dwell_label"] for row in policy_rows)

    return {
        "turning_points_mean": round(sum(turning_points) / len(turning_points), 6),
        "longest_dwell_steps_mean": round(sum(dwell_steps) / len(dwell_steps), 6),
        "longest_dwell_labels": "|".join(
            f"{label}:{labels[label]}"
            for label in sorted(labels)
        ),
    }


def _step_deltas(trajectory: str) -> str:
    values = [float(value) for value in trajectory.split("|")]
    deltas = [
        _format_number(values[index] - values[index - 1])
        for index in range(1, len(values))
    ]
    return "|".join(deltas)


def _format_number(value: float) -> str:
    rounded = round(value, 6)
    if rounded.is_integer():
        return str(int(rounded))
    return str(rounded)


def test_metrics_csv_records_role_action_counts(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    metrics_lines = (out_dir / "metrics.csv").read_text().splitlines()
    metrics_header = metrics_lines[0].split(",")
    first_row = dict(zip(metrics_header, metrics_lines[1].split(",")))
    actions = ("idle", "message", "create_task", "work_task")

    for role in BASELINE_ROLES:
        assert {f"role_{role}_{action}_tick" for action in actions} <= set(metrics_header)
        assert sum(int(first_row[f"role_{role}_{action}_tick"]) for action in actions) == 3

    assert sum(int(first_row[f"role_{role}_message_tick"]) for role in BASELINE_ROLES) == int(
        first_row["messages_sent_tick"]
    )
    assert sum(int(first_row[f"role_{role}_create_task_tick"]) for role in BASELINE_ROLES) == int(
        first_row["tasks_created_tick"]
    )
    assert sum(int(first_row[f"role_{role}_work_task_tick"]) for role in BASELINE_ROLES) == int(
        first_row["tasks_worked_tick"]
    )
    assert sum(int(first_row[f"role_{role}_idle_tick"]) for role in BASELINE_ROLES) == int(
        first_row["idle_tick"]
    )

    summary = (out_dir / "summary.md").read_text()
    assert "## Role action totals" in summary
    assert "- coordinator: idle=" in summary


def test_metrics_and_events_headers_match_documented_a0_schema(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))

    assert metrics_header == list(metrics_fieldnames(("idle", "message", "create_task", "work_task")))
    assert events_header == list(EVENT_FIELDS)


def test_summary_records_event_type_totals(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    result = run_experiment(CONFIG, seed=1, out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()
    assert "## Event type totals" in summary
    for event_type, count in sorted(Counter(event["event_type"] for event in result.events).items()):
        assert f"- {event_type}: {count}" in summary


def test_metrics_csv_records_baseline_lobe_labels(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert set(row["baseline_lobe_label"] for row in rows) <= set(BASELINE_LOBE_LABELS)
    assert any(row["baseline_lobe_label"] == "backlog_growth" for row in rows)
    assert any(row["baseline_lobe_label"] == "execution" for row in rows)

    previous_queue_depth = 0
    for row in rows:
        queue_depth = int(row["queue_depth"])
        queue_delta = int(row["queue_delta_tick"])
        assert queue_depth - previous_queue_depth == queue_delta
        previous_queue_depth = queue_depth

    summary = (out_dir / "summary.md").read_text()
    assert "## Baseline lobe totals" in summary
    assert "- backlog_growth: " in summary


def test_metrics_csv_records_queue_pressure_balances(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    created_completed_balance = 0
    created_worked_balance = 0
    work_completion_gap = 0
    for row in rows:
        created = int(row["tasks_created_tick"])
        worked = int(row["tasks_worked_tick"])
        completed = int(row["tasks_completed_tick"])

        assert int(row["created_completed_balance_tick"]) == created - completed
        assert int(row["created_worked_balance_tick"]) == created - worked
        assert int(row["work_completion_gap_tick"]) == worked - completed
        assert int(row["backlog_pressure_tick"]) == int(row["queue_depth"])

        created_completed_balance += int(row["created_completed_balance_tick"])
        created_worked_balance += int(row["created_worked_balance_tick"])
        work_completion_gap += int(row["work_completion_gap_tick"])

    last = rows[-1]
    assert created_completed_balance == int(last["queue_depth"])
    assert created_completed_balance == created_worked_balance + work_completion_gap

    summary = (out_dir / "summary.md").read_text()
    assert f"- final backlog pressure: {last['queue_depth']}" in summary
    assert f"- created-completed balance: {created_completed_balance}" in summary
    assert f"- created-worked balance: {created_worked_balance}" in summary
    assert f"- work-completion gap: {work_completion_gap}" in summary


def test_metrics_csv_records_queued_task_age(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metrics_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    summary = (out_dir / "summary.md").read_text()

    _assert_event_replay_reproduces_queued_task_age_metrics(
        metric_rows=metrics_rows,
        event_rows=event_rows,
    )
    _assert_queued_task_age_summary_matches_metrics(
        summary,
        metric_rows=metrics_rows,
    )


def test_metrics_csv_records_baseline_lobe_transitions(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["baseline_lobe_previous_label"] == ""
    assert rows[0]["baseline_lobe_transition"] == "start"
    assert rows[0]["baseline_lobe_transition_tick"] == "0"

    transition_counts: dict[str, int] = {}
    previous_label = rows[0]["baseline_lobe_label"]
    for row in rows[1:]:
        current_label = row["baseline_lobe_label"]
        expected_transition = (
            "stable"
            if previous_label == current_label
            else f"{previous_label}->{current_label}"
        )
        assert row["baseline_lobe_previous_label"] == previous_label
        assert row["baseline_lobe_transition"] == expected_transition
        assert row["baseline_lobe_transition_tick"] == str(int(previous_label != current_label))
        if expected_transition != "stable":
            transition_counts[expected_transition] = transition_counts.get(expected_transition, 0) + 1
        previous_label = current_label

    assert transition_counts
    summary = (out_dir / "summary.md").read_text()
    assert "## Baseline lobe transitions" in summary
    for transition, count in transition_counts.items():
        assert f"- {transition}: {count}" in summary


def test_metrics_csv_records_baseline_lobe_run_state(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert rows[0]["baseline_lobe_run_id"] == "1"
    assert rows[0]["baseline_lobe_current_run_length"] == "1"

    previous_label = ""
    expected_run_id = 0
    expected_run_length = 0
    completed_runs: list[tuple[int, str, int]] = []
    for row in rows:
        label = row["baseline_lobe_label"]
        if label == previous_label:
            expected_run_length += 1
        else:
            if previous_label:
                completed_runs.append((expected_run_id, previous_label, expected_run_length))
            expected_run_id += 1
            expected_run_length = 1

        assert int(row["baseline_lobe_run_id"]) == expected_run_id
        assert int(row["baseline_lobe_current_run_length"]) == expected_run_length
        previous_label = label

    completed_runs.append((expected_run_id, previous_label, expected_run_length))
    assert expected_run_id == sum(dwell["runs"] for dwell in _lobe_dwell_runs(rows).values())
    assert max(run_length for _, _, run_length in completed_runs) == max(
        dwell["max_run"] for dwell in _lobe_dwell_runs(rows).values()
    )


def test_summary_records_baseline_lobe_dwell_runs(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    result = run_experiment(CONFIG, seed=1, out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()
    assert "## Baseline lobe dwell runs" in summary
    for label, dwell in _lobe_dwell_runs(result.metrics).items():
        assert (
            f"- {label}: runs={dwell['runs']}, total_ticks={dwell['total_ticks']}, "
            f"max_run={dwell['max_run']}, mean_run={dwell['mean_run']}"
        ) in summary


def test_manifest_records_environment_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    environment = manifest["environment"]

    assert environment["git_commit"]
    assert environment["python_version"] == sys.version.split()[0]
    assert set(environment["package_versions"]) == {
        "mesa",
        "networkx",
        "numpy",
        "pandas",
        "pydantic",
        "pyyaml",
    }


def test_manifest_and_config_match_documented_a0_provenance_schema(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())

    actions = _actions_from_normalized_config(normalized_config)
    agent_ids = [f"agent_{index:02d}" for index in range(1, 16)]
    roles = {
        agent_id: BASELINE_ROLES[(index - 1) % len(BASELINE_ROLES)]
        for index, agent_id in enumerate(agent_ids, start=1)
    }
    expected_config = {
        "run": {
            "experiment_id": "a0_smoke",
            "ticks": 100,
        },
        "model": {
            "agent_count": 15,
            "task_creation_pressure": 1.0,
            "work_service_capacity": 1.0,
            "actions": actions,
        },
        "outputs": {
            "write_manifest": True,
            "write_metrics": True,
            "write_events": True,
            "write_summary": True,
        },
    }

    assert normalized_config == expected_config
    assert set(manifest) == {
        "experiment_id",
        "seed",
        "ticks",
        "agent_count",
        "actions",
        "outputs",
        "artifacts",
        "environment",
        "model",
        "config",
    }
    assert manifest["experiment_id"] == "a0_smoke"
    assert manifest["seed"] == 1
    assert manifest["ticks"] == 100
    assert manifest["agent_count"] == 15
    assert manifest["actions"] == actions
    assert manifest["outputs"] == expected_config["outputs"]
    assert manifest["artifacts"] == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]
    assert manifest["config"] == normalized_config
    assert manifest["model"] == {
        "agent_ids": agent_ids,
        "roles": roles,
        "bus_nodes": 16,
        "bus_edges": 15,
        "baseline_lobes": {
            "labels": list(BASELINE_LOBE_LABELS),
            "transition_fields": list(BASELINE_LOBE_TRANSITION_FIELDS),
        },
        "queue_dynamics_metrics": {
            "pressure_fields": list(QUEUE_PRESSURE_METRIC_FIELDS),
            "queued_task_age_fields": list(QUEUED_TASK_AGE_METRIC_FIELDS),
        },
        "events": {
            "types": list(BASELINE_EVENT_TYPES),
            "fields": list(EVENT_FIELDS),
        },
        "metrics": {
            "fields": list(metrics_fieldnames(tuple(actions))),
        },
        "role_action_metrics": {
            "roles": list(BASELINE_ROLES),
            "actions": actions,
            "fields": list(role_action_metric_fields(tuple(actions))),
        },
    }


def test_manifest_records_baseline_lobe_metric_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    baseline_lobes = manifest["model"]["baseline_lobes"]
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    assert baseline_lobes == {
        "labels": list(BASELINE_LOBE_LABELS),
        "transition_fields": list(BASELINE_LOBE_TRANSITION_FIELDS),
    }
    assert "baseline_lobe_label" in metrics_header
    for field in baseline_lobes["transition_fields"]:
        assert field in metrics_header


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_manifest_lobe_transition_fields_exactly_match_metrics_columns_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    emitted_transition_fields = [
        field
        for field in metrics_header
        if field.startswith("baseline_lobe_") and field != "baseline_lobe_label"
    ]

    assert manifest["model"]["baseline_lobes"]["transition_fields"] == emitted_transition_fields
    assert emitted_transition_fields == list(BASELINE_LOBE_TRANSITION_FIELDS)


def test_manifest_records_role_action_metric_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    role_action_metrics = manifest["model"]["role_action_metrics"]
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    expected_fields = list(role_action_metric_fields(tuple(manifest["actions"])))
    assert role_action_metrics == {
        "roles": list(BASELINE_ROLES),
        "actions": manifest["actions"],
        "fields": expected_fields,
    }
    for field in role_action_metrics["fields"]:
        assert field in metrics_header


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_manifest_role_action_fields_exactly_match_metrics_columns_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    emitted_role_action_fields = [
        field for field in metrics_header if field.startswith("role_")
    ]

    assert manifest["model"]["role_action_metrics"]["fields"] == emitted_role_action_fields
    assert emitted_role_action_fields == list(role_action_metric_fields(tuple(manifest["actions"])))


def test_manifest_records_queue_dynamics_metric_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    queue_dynamics_metrics = manifest["model"]["queue_dynamics_metrics"]
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    assert queue_dynamics_metrics == {
        "pressure_fields": list(QUEUE_PRESSURE_METRIC_FIELDS),
        "queued_task_age_fields": list(QUEUED_TASK_AGE_METRIC_FIELDS),
    }
    for field in [
        *queue_dynamics_metrics["pressure_fields"],
        *queue_dynamics_metrics["queued_task_age_fields"],
    ]:
        assert field in metrics_header


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_manifest_queue_dynamics_fields_exactly_match_metrics_columns_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    queue_dynamics_metrics = manifest["model"]["queue_dynamics_metrics"]
    emitted_pressure_fields = [
        field for field in metrics_header if field in QUEUE_PRESSURE_METRIC_FIELDS
    ]
    emitted_queued_task_age_fields = [
        field for field in metrics_header if field in QUEUED_TASK_AGE_METRIC_FIELDS
    ]

    assert queue_dynamics_metrics["pressure_fields"] == emitted_pressure_fields
    assert queue_dynamics_metrics["queued_task_age_fields"] == emitted_queued_task_age_fields
    assert emitted_pressure_fields == list(QUEUE_PRESSURE_METRIC_FIELDS)
    assert emitted_queued_task_age_fields == list(QUEUED_TASK_AGE_METRIC_FIELDS)


def test_manifest_records_full_metrics_schema_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    expected_fields = list(metrics_fieldnames(tuple(manifest["actions"])))
    assert manifest["model"]["metrics"] == {"fields": expected_fields}
    assert metrics_header == expected_fields


def test_reordered_action_fixture_keeps_config_manifest_and_metrics_schema_aligned(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_reordered_actions"

    run_experiment(REORDERED_ACTIONS, seed=1, out_dir=out_dir)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    actions = _actions_from_normalized_config(normalized_config)
    expected_role_action_fields = list(role_action_metric_fields(tuple(actions)))
    expected_metrics_fields = list(metrics_fieldnames(tuple(actions)))

    assert actions == ["work_task", "create_task", "message", "idle"]
    assert manifest["actions"] == actions
    assert manifest["config"]["model"]["actions"] == actions
    assert manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert manifest["model"]["role_action_metrics"]["actions"] == actions
    assert manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert metrics_header == expected_metrics_fields
    assert [
        field for field in metrics_header if field.startswith("role_")
    ] == expected_role_action_fields


def test_manifest_records_event_schema_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    event_schema = manifest["model"]["events"]
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    assert event_schema == {
        "types": list(BASELINE_EVENT_TYPES),
        "fields": list(EVENT_FIELDS),
    }
    assert event_rows
    assert list(event_rows[0]) == list(EVENT_FIELDS)
    assert set(event["event_type"] for event in event_rows) <= set(BASELINE_EVENT_TYPES)
    assert set(event["event_type"] for event in event_rows) == set(BASELINE_EVENT_TYPES)


def test_summary_records_artifact_schema_provenance(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))
    summary = (out_dir / "summary.md").read_text()

    _assert_summary_records_artifact_schema_provenance(
        summary,
        metrics_header=metrics_header,
        events_header=events_header,
        actions=tuple(manifest["actions"]),
    )
    assert manifest["model"]["metrics"]["fields"] == metrics_header
    assert manifest["model"]["events"]["fields"] == events_header


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_summary_schema_provenance_counts_match_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    _assert_summary_schema_provenance_counts_match_manifest(summary, manifest)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_schema_provenance_counts_match_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_schema_counts"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    _assert_summary_schema_provenance_counts_match_manifest(summary, manifest)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_artifacts_and_output_flags_match_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_artifacts_outputs"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    assert _summary_written_artifacts(summary) == manifest["artifacts"]
    assert manifest["artifacts"] == _expected_artifacts(config_path)
    assert manifest["outputs"] == normalized_config["outputs"]
    _assert_summary_output_flags_match_config(summary, normalized_config["outputs"])


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_config_manifest_and_summary_run_fields_match_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_run_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()

    _assert_config_manifest_and_summary_run_fields_match(
        normalized_config,
        manifest=manifest,
        summary=summary,
        seed=1,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_agent_identity_and_roles_match_baseline_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_agent_identity_roles"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())

    _assert_manifest_agent_identity_and_roles_match_baseline(manifest)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_bus_counts_match_summary_and_first_metrics_row_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_bus_counts"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        first_metrics_row = next(csv.DictReader(handle))

    _assert_manifest_bus_counts_match_summary_and_metrics_row(
        manifest,
        summary=summary,
        metrics_row=first_metrics_row,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_static_bus_metrics_match_first_metrics_row_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_static_bus_metrics"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        first_metrics_row = next(csv.DictReader(handle))

    _assert_summary_static_bus_metrics_match_metrics_row(
        summary,
        metrics_row=first_metrics_row,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_first_row_queue_pressure_fields_match_summary_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_first_row_queue_pressure"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_first_row_queue_pressure_fields_match_summary(
        summary,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_queued_task_age_summary_matches_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_queued_task_age"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_queued_task_age_summary_matches_metrics(
        summary,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_event_type_totals_match_events_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_event_type_totals"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_summary_event_type_totals_match_events(summary, event_rows=event_rows)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_top_level_totals_match_metrics_and_events_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_top_level_totals"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_summary_top_level_totals_match_metrics_and_events(
        summary,
        metric_rows=metric_rows,
        event_rows=event_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_bus_graph_fields_match_metrics_and_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_bus_graph"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_bus_graph_fields_match_metrics_and_manifest(
        summary,
        metric_rows=metric_rows,
        manifest=manifest,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_role_action_totals_match_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_role_action_totals"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_role_action_totals_match_metrics(
        summary,
        metric_rows=metric_rows,
        actions=tuple(manifest["actions"]),
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_queue_dynamics_match_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_queue_dynamics"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_queue_dynamics_match_metrics(summary, metric_rows=metric_rows)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_lobe_aggregates_match_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_lobe_aggregates"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_lobe_aggregates_match_metrics(summary, metric_rows=metric_rows)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_dwell_runs_summary_matches_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_lobe_dwell_runs"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_lobe_dwell_run_summary_matches_metrics(summary, metric_rows=metric_rows)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_run_state_matches_recomputed_dwell_runs_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_lobe_run_state"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_lobe_run_state_matches_recomputed_dwell_runs(metric_rows)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_transitions_match_adjacent_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_lobe_transitions"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_lobe_transitions_match_adjacent_labels(metric_rows)


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_lobe_transition_totals_match_adjacent_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_lobe_transition_totals"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_lobe_transition_totals_match_adjacent_labels(
        summary,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_lobe_transition_endpoints_use_only_manifest_lobe_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_lobe_transition_manifest_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_lobe_transition_endpoints_use_only_manifest_lobe_labels(
        summary,
        manifest=manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_lobe_labels_cover_observed_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_lobe_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_manifest_lobe_labels_cover_observed_metrics(
        manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_lobe_labels_cover_previous_metrics_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_previous_lobe_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_manifest_lobe_labels_cover_previous_metrics_labels(
        manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_lobe_labels_cover_metrics_transition_endpoints_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_transition_lobe_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_manifest_lobe_labels_cover_metrics_transition_endpoints(
        manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_label_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_lobe_label_sequence_first",
        second_name=f"{config_path.stem}_cli_lobe_label_sequence_second",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_label_sequence(first_metric_rows)
    second_sequence = _lobe_label_sequence(second_metric_rows)

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_label_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_lobe_label_sequence_seed1",
        second_name=f"{config_path.stem}_cli_lobe_label_sequence_seed2",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_label_sequence(first_metric_rows)
    second_sequence = _lobe_label_sequence(second_metric_rows)

    assert first_sequence
    assert second_sequence
    assert first_sequence != second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_transition_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_transition_sequence_first",
        second_name=f"{config_path.stem}_cli_transition_sequence_second",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_transition_sequence(first_metric_rows)
    second_sequence = _lobe_transition_sequence(second_metric_rows)

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_transition_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_transition_sequence_seed1",
        second_name=f"{config_path.stem}_cli_transition_sequence_seed2",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_transition_field_sequence(first_metric_rows)
    second_sequence = _lobe_transition_field_sequence(second_metric_rows)

    assert first_sequence
    assert second_sequence
    assert first_sequence != second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_run_state_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_run_state_sequence_first",
        second_name=f"{config_path.stem}_cli_run_state_sequence_second",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_run_state_sequence(first_metric_rows)
    second_sequence = _lobe_run_state_sequence(second_metric_rows)

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_run_state_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_run_state_sequence_seed1",
        second_name=f"{config_path.stem}_cli_run_state_sequence_seed2",
    )

    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _lobe_run_state_sequence(first_metric_rows)
    second_sequence = _lobe_run_state_sequence(second_metric_rows)
    first_state_signature = (_lobe_label_sequence(first_metric_rows), first_sequence)
    second_state_signature = (_lobe_label_sequence(second_metric_rows), second_sequence)

    assert first_sequence
    assert second_sequence
    assert first_state_signature != second_state_signature


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_lobe_dwell_run_summary_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_dwell_run_summary_seed1",
        second_name=f"{config_path.stem}_cli_dwell_run_summary_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_dwell_runs = _summary_lobe_dwell_runs(first_summary)
    second_dwell_runs = _summary_lobe_dwell_runs(second_summary)

    assert first_dwell_runs == _lobe_dwell_runs(first_metric_rows)
    assert second_dwell_runs == _lobe_dwell_runs(second_metric_rows)
    assert first_dwell_runs
    assert second_dwell_runs
    assert first_dwell_runs != second_dwell_runs


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_role_action_summary_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_role_action_summary_first",
        second_name=f"{config_path.stem}_cli_role_action_summary_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_role_action_totals = _summary_role_action_totals(first_summary)
    second_role_action_totals = _summary_role_action_totals(second_summary)
    first_actions = tuple(first_manifest["actions"])
    second_actions = tuple(second_manifest["actions"])

    assert first_role_action_totals == _role_action_totals_from_metrics(
        first_metric_rows,
        first_actions,
    )
    assert second_role_action_totals == _role_action_totals_from_metrics(
        second_metric_rows,
        second_actions,
    )
    assert first_role_action_totals
    assert first_role_action_totals == second_role_action_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_role_action_metric_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_role_action_sequence_first",
        second_name=f"{config_path.stem}_cli_role_action_sequence_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_sequence = _role_action_metric_sequence(
        first_metric_rows,
        tuple(first_manifest["actions"]),
    )
    second_sequence = _role_action_metric_sequence(
        second_metric_rows,
        tuple(second_manifest["actions"]),
    )

    assert first_sequence
    assert first_sequence == second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_role_action_counts_sum_to_role_population_for_every_metrics_row_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_role_action_row_population"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    actions = tuple(manifest["actions"])
    role_populations = Counter(manifest["model"]["roles"].values())

    assert metric_rows
    assert role_populations == {role: 3 for role in BASELINE_ROLES}
    for row in metric_rows:
        for role, population in role_populations.items():
            assert (
                sum(int(row[f"role_{role}_{action}_tick"]) for action in actions)
                == population
            )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_role_action_counts_sum_to_top_level_action_totals_for_every_metrics_row_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_role_action_row_action_totals"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    actions = tuple(manifest["actions"])
    top_level_action_fields = {
        "idle": "idle_tick",
        "message": "messages_sent_tick",
        "create_task": "tasks_created_tick",
        "work_task": "tasks_worked_tick",
    }

    assert metric_rows
    assert set(actions) == set(top_level_action_fields)
    for row in metric_rows:
        for action in actions:
            assert sum(
                int(row[f"role_{role}_{action}_tick"])
                for role in BASELINE_ROLES
            ) == int(row[top_level_action_fields[action]])


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_events_per_tick_action_counts_match_metrics_top_level_action_totals_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_metrics_row_action_totals"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_per_tick_action_counts_match_metrics_top_level_action_totals(
        metric_rows=metric_rows,
        event_rows=event_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_events_per_tick_counts_match_configured_agent_population_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_tick_population"

    _run_documented_cli(config_path, out_dir)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_per_tick_counts_match_configured_agent_population(
        event_rows=event_rows,
        ticks=normalized_config["run"]["ticks"],
        agent_count=normalized_config["model"]["agent_count"],
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_events_per_tick_agent_ids_match_manifest_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_tick_manifest_agents"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_per_tick_agent_ids_match_manifest(
        event_rows=event_rows,
        ticks=manifest["ticks"],
        manifest_agent_ids=manifest["model"]["agent_ids"],
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_events_replay_to_role_action_metrics_through_manifest_roles_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_role_action_metrics"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_replay_to_role_action_metrics_through_manifest_roles(
        metric_rows=metric_rows,
        event_rows=event_rows,
        manifest_roles=manifest["model"]["roles"],
        actions=tuple(manifest["actions"]),
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_events_replay_to_summary_role_action_totals_through_manifest_roles_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_summary_role_action_totals"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_replay_to_summary_role_action_totals_through_manifest_roles(
        summary,
        event_rows=event_rows,
        manifest_roles=manifest["model"]["roles"],
        actions=tuple(manifest["actions"]),
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_role_action_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_event_replayed_role_action_first",
        second_name=f"{config_path.stem}_cli_event_replayed_role_action_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_totals = _role_action_totals_from_events(
        first_event_rows,
        manifest_roles=first_manifest["model"]["roles"],
        actions=tuple(first_manifest["actions"]),
    )
    second_replayed_totals = _role_action_totals_from_events(
        second_event_rows,
        manifest_roles=second_manifest["model"]["roles"],
        actions=tuple(second_manifest["actions"]),
    )

    assert first_replayed_totals == _summary_role_action_totals(first_summary)
    assert second_replayed_totals == _summary_role_action_totals(second_summary)
    assert first_replayed_totals
    assert first_replayed_totals == second_replayed_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_role_action_totals_change_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_event_replayed_role_action_seed1",
        second_name=f"{config_path.stem}_cli_event_replayed_role_action_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_totals = _role_action_totals_from_events(
        first_event_rows,
        manifest_roles=first_manifest["model"]["roles"],
        actions=tuple(first_manifest["actions"]),
    )
    second_replayed_totals = _role_action_totals_from_events(
        second_event_rows,
        manifest_roles=second_manifest["model"]["roles"],
        actions=tuple(second_manifest["actions"]),
    )

    assert first_replayed_totals == _summary_role_action_totals(first_summary)
    assert second_replayed_totals == _summary_role_action_totals(second_summary)
    assert first_replayed_totals
    assert second_replayed_totals
    assert first_replayed_totals != second_replayed_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_role_action_metric_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_event_replayed_role_action_sequence_seed1",
        second_name=f"{config_path.stem}_cli_event_replayed_role_action_sequence_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_actions = tuple(first_manifest["actions"])
    second_actions = tuple(second_manifest["actions"])
    first_replayed_sequence = _role_action_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
        manifest_roles=first_manifest["model"]["roles"],
        actions=first_actions,
    )
    second_replayed_sequence = _role_action_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
        manifest_roles=second_manifest["model"]["roles"],
        actions=second_actions,
    )

    assert first_replayed_sequence == _role_action_metric_sequence(
        first_metric_rows,
        first_actions,
    )
    assert second_replayed_sequence == _role_action_metric_sequence(
        second_metric_rows,
        second_actions,
    )
    assert first_replayed_sequence
    assert second_replayed_sequence
    assert first_replayed_sequence != second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_top_level_metric_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_event_replayed_top_level_sequence_first",
        second_name=f"{config_path.stem}_cli_event_replayed_top_level_sequence_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _top_level_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _top_level_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _top_level_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _top_level_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert first_replayed_sequence == second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_top_level_metric_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_event_replayed_top_level_sequence_seed1",
        second_name=f"{config_path.stem}_cli_event_replayed_top_level_sequence_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _top_level_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _top_level_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _top_level_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _top_level_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert second_replayed_sequence
    assert first_replayed_sequence != second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_queue_pressure_metric_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_event_replayed_queue_pressure_first",
        second_name=f"{config_path.stem}_cli_event_replayed_queue_pressure_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _queue_pressure_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _queue_pressure_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _queue_pressure_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _queue_pressure_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert first_replayed_sequence == second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_queue_pressure_metric_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_event_replayed_queue_pressure_seed1",
        second_name=f"{config_path.stem}_cli_event_replayed_queue_pressure_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _queue_pressure_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _queue_pressure_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _queue_pressure_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _queue_pressure_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert second_replayed_sequence
    assert first_replayed_sequence != second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_queue_pressure_totals_change_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_queue_pressure_seed1",
        second_name=f"{config_path.stem}_cli_summary_queue_pressure_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_queue_pressure_totals(first_summary)
    second_summary_totals = _summary_queue_pressure_totals(second_summary)

    assert first_summary_totals == _queue_pressure_totals_from_metrics(first_metric_rows)
    assert second_summary_totals == _queue_pressure_totals_from_metrics(second_metric_rows)
    assert first_summary_totals
    assert second_summary_totals
    assert first_summary_totals != second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_queue_pressure_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_queue_pressure_first",
        second_name=f"{config_path.stem}_cli_summary_queue_pressure_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_queue_pressure_totals(first_summary)
    second_summary_totals = _summary_queue_pressure_totals(second_summary)

    assert first_summary_totals == _queue_pressure_totals_from_metrics(first_metric_rows)
    assert second_summary_totals == _queue_pressure_totals_from_metrics(second_metric_rows)
    assert first_summary_totals
    assert first_summary_totals == second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_task_and_queue_totals_change_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_task_queue_totals_seed1",
        second_name=f"{config_path.stem}_cli_summary_task_queue_totals_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_task_and_queue_totals(first_summary)
    second_summary_totals = _summary_task_and_queue_totals(second_summary)

    assert first_summary_totals == _task_and_queue_totals_from_metrics(first_metric_rows)
    assert second_summary_totals == _task_and_queue_totals_from_metrics(second_metric_rows)
    assert first_summary_totals
    assert second_summary_totals
    assert first_summary_totals != second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_task_and_queue_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_task_queue_totals_first",
        second_name=f"{config_path.stem}_cli_summary_task_queue_totals_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_task_and_queue_totals(first_summary)
    second_summary_totals = _summary_task_and_queue_totals(second_summary)

    assert first_summary_totals == _task_and_queue_totals_from_metrics(first_metric_rows)
    assert second_summary_totals == _task_and_queue_totals_from_metrics(second_metric_rows)
    assert first_summary_totals
    assert first_summary_totals == second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_event_type_totals_change_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_event_type_totals_seed1",
        second_name=f"{config_path.stem}_cli_summary_event_type_totals_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_event_type_totals(first_summary)
    second_summary_totals = _summary_event_type_totals(second_summary)

    assert first_summary_totals == _event_type_totals_from_events(first_event_rows)
    assert second_summary_totals == _event_type_totals_from_events(second_event_rows)
    assert first_summary_totals
    assert second_summary_totals
    assert first_summary_totals != second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_event_type_totals_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_event_type_totals_first",
        second_name=f"{config_path.stem}_cli_summary_event_type_totals_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_summary_totals = _summary_event_type_totals(first_summary)
    second_summary_totals = _summary_event_type_totals(second_summary)

    assert first_summary_totals == _event_type_totals_from_events(first_event_rows)
    assert second_summary_totals == _event_type_totals_from_events(second_event_rows)
    assert first_summary_totals
    assert first_summary_totals == second_summary_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_queued_task_age_aggregates_change_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_queued_task_age_seed1",
        second_name=f"{config_path.stem}_cli_summary_queued_task_age_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_aggregates = _summary_queued_task_age_aggregates(first_summary)
    second_summary_aggregates = _summary_queued_task_age_aggregates(second_summary)

    assert first_summary_aggregates == _queued_task_age_aggregates_from_metrics(
        first_metric_rows
    )
    assert second_summary_aggregates == _queued_task_age_aggregates_from_metrics(
        second_metric_rows
    )
    assert first_summary_aggregates
    assert second_summary_aggregates
    assert first_summary_aggregates != second_summary_aggregates


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_queued_task_age_aggregates_reproduce_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_queued_task_age_first",
        second_name=f"{config_path.stem}_cli_summary_queued_task_age_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_summary_aggregates = _summary_queued_task_age_aggregates(first_summary)
    second_summary_aggregates = _summary_queued_task_age_aggregates(second_summary)

    assert first_summary_aggregates == _queued_task_age_aggregates_from_metrics(
        first_metric_rows
    )
    assert second_summary_aggregates == _queued_task_age_aggregates_from_metrics(
        second_metric_rows
    )
    assert first_summary_aggregates
    assert first_summary_aggregates == second_summary_aggregates


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_task_queue_pressure_and_age_aggregates_match_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_queue_integrity"

    _run_documented_cli(config_path, out_dir)

    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    summary_task_queue_totals = _summary_task_and_queue_totals(summary)
    summary_queue_pressure_totals = _summary_queue_pressure_totals(summary)
    summary_age_aggregates = _summary_queued_task_age_aggregates(summary)

    assert summary_task_queue_totals == _task_and_queue_totals_from_metrics(metric_rows)
    assert summary_queue_pressure_totals == _queue_pressure_totals_from_metrics(metric_rows)
    assert summary_age_aggregates == _queued_task_age_aggregates_from_metrics(metric_rows)
    assert (
        summary_task_queue_totals["queue_depth"]
        == summary_queue_pressure_totals["created_completed_balance_tick"]
    )
    assert (
        summary_age_aggregates["final_queued_task_max_age"]
        >= summary_age_aggregates["final_queued_task_mean_age"]
    )
    assert (
        summary_age_aggregates["peak_queued_task_max_age"]
        >= summary_age_aggregates["final_queued_task_max_age"]
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_task_queue_pressure_and_age_aggregate_tuple_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_queue_integrity_first",
        second_name=f"{config_path.stem}_cli_summary_queue_integrity_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_tuple = _summary_task_queue_pressure_and_age_aggregate_tuple(first_summary)
    second_tuple = _summary_task_queue_pressure_and_age_aggregate_tuple(second_summary)

    assert first_tuple == _task_queue_pressure_and_age_aggregate_tuple_from_metrics(
        first_metric_rows
    )
    assert second_tuple == _task_queue_pressure_and_age_aggregate_tuple_from_metrics(
        second_metric_rows
    )
    assert first_tuple["task_queue_totals"]
    assert first_tuple["queue_pressure_totals"]
    assert first_tuple["queued_task_age_aggregates"]
    assert first_tuple == second_tuple


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_integrated_summary_aggregate_bundle_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_summary_bundle_first",
        second_name=f"{config_path.stem}_cli_summary_bundle_second",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=tuple(first_manifest["actions"]),
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=tuple(second_manifest["actions"]),
    )

    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=tuple(first_manifest["actions"]),
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=tuple(second_manifest["actions"]),
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert first_bundle == second_bundle


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_integrated_summary_aggregate_bundle_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_bundle_seed1",
        second_name=f"{config_path.stem}_cli_summary_bundle_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=tuple(first_manifest["actions"]),
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=tuple(second_manifest["actions"]),
    )

    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=tuple(first_manifest["actions"]),
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=tuple(second_manifest["actions"]),
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert second_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert second_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert second_bundle["role_action_totals"]
    assert first_bundle != second_bundle


@pytest.mark.parametrize("config_path", NO_MANIFEST_FIXTURES)
def test_documented_cli_no_manifest_integrated_summary_aggregate_bundle_matches_metrics_with_config_actions(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_bundle"

    _run_documented_cli(config_path, out_dir)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    actions = tuple(normalized_config["model"]["actions"])
    summary_bundle = _summary_integrated_aggregate_bundle(summary, actions=actions)
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert not (out_dir / "manifest.yaml").exists()
    assert _summary_written_artifacts(summary) == _expected_artifacts(config_path)
    assert normalized_config["outputs"]["write_manifest"] is False
    assert metrics_header == expected_metrics_fields
    assert [
        field for field in metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert summary_bundle == _integrated_aggregate_bundle_from_metrics(
        metric_rows,
        actions=actions,
    )
    assert summary_bundle["task_queue_pressure_and_age"]
    assert summary_bundle["lobe_aggregates"]
    assert summary_bundle["role_action_totals"]


def test_run_api_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_matches_metrics(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_no_manifest_reordered_actions_api_summary_bundle"

    result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=1, out_dir=out_dir)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    actions = tuple(normalized_config["model"]["actions"])
    summary_bundle = _summary_integrated_aggregate_bundle(summary, actions=actions)
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert result.config.to_dict() == normalized_config
    assert result.seed == 1
    assert actions == ("work_task", "create_task", "message", "idle")
    assert normalized_config["outputs"]["write_manifest"] is False
    assert not (out_dir / "manifest.yaml").exists()
    assert _summary_written_artifacts(summary) == _expected_artifacts(
        NO_MANIFEST_REORDERED_ACTIONS
    )
    assert metrics_header == expected_metrics_fields
    assert [
        field for field in metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert summary_bundle == _integrated_aggregate_bundle_from_metrics(
        metric_rows,
        actions=actions,
    )
    assert summary_bundle["task_queue_pressure_and_age"]
    assert summary_bundle["lobe_aggregates"]
    assert summary_bundle["role_action_totals"]


def test_run_api_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reproduces_across_same_seed(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_api_summary_bundle_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_api_summary_bundle_second"

    first_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=first)
    second_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=second)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_actions = tuple(first_config["model"]["actions"])
    second_actions = tuple(second_config["model"]["actions"])
    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=first_actions,
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=second_actions,
    )

    assert first_result.seed == second_result.seed == 17
    assert first_result.config.to_dict() == first_config
    assert second_result.config.to_dict() == second_config
    assert first_result.metrics == second_result.metrics
    assert first_result.events == second_result.events
    assert first_actions == second_actions == ("work_task", "create_task", "message", "idle")
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert not (first / "manifest.yaml").exists()
    assert not (second / "manifest.yaml").exists()
    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=first_actions,
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=second_actions,
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert first_bundle == second_bundle


def test_run_api_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_changes_across_different_seeds(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_api_summary_bundle_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_api_summary_bundle_seed2"

    first_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=1, out_dir=first)
    second_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=2, out_dir=second)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_actions = tuple(first_config["model"]["actions"])
    second_actions = tuple(second_config["model"]["actions"])
    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=first_actions,
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=second_actions,
    )

    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == 1
    assert second_result.seed == 2
    assert first_actions == second_actions == ("work_task", "create_task", "message", "idle")
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert not (first / "manifest.yaml").exists()
    assert not (second / "manifest.yaml").exists()
    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=first_actions,
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=second_actions,
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert second_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert second_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert second_bundle["role_action_totals"]
    assert first_bundle != second_bundle


def test_documented_cli_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reproduces_across_same_seed(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_summary_bundle_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_summary_bundle_second"

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=17)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=17)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_actions = tuple(first_config["model"]["actions"])
    second_actions = tuple(second_config["model"]["actions"])
    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=first_actions,
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=second_actions,
    )

    assert first_config == second_config
    assert first_metric_rows == second_metric_rows
    assert first_actions == second_actions == ("work_task", "create_task", "message", "idle")
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert not (first / "manifest.yaml").exists()
    assert not (second / "manifest.yaml").exists()
    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=first_actions,
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=second_actions,
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert first_bundle == second_bundle


def test_documented_cli_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reconstructs_from_events(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_event_bundle_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_event_bundle_second"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=17)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=17)

    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        first,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest_reordered_actions",
        expected_actions=("work_task", "create_task", "message", "idle"),
    )
    second_event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        second,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest_reordered_actions",
        expected_actions=("work_task", "create_task", "message", "idle"),
    )

    assert first_event_rows == second_event_rows
    assert first_event_bundle["task_queue_pressure_and_age"]
    assert first_event_bundle["lobe_aggregates"]
    assert first_event_bundle["role_action_totals"]
    assert first_event_bundle == second_event_bundle


def test_documented_cli_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_changes_across_different_seeds(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_summary_bundle_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_summary_bundle_seed2"

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=1)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=2)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_actions = tuple(first_config["model"]["actions"])
    second_actions = tuple(second_config["model"]["actions"])
    first_bundle = _summary_integrated_aggregate_bundle(
        first_summary,
        actions=first_actions,
    )
    second_bundle = _summary_integrated_aggregate_bundle(
        second_summary,
        actions=second_actions,
    )

    assert first_config == second_config
    assert first_actions == second_actions == ("work_task", "create_task", "message", "idle")
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert not (first / "manifest.yaml").exists()
    assert not (second / "manifest.yaml").exists()
    assert first_bundle == _integrated_aggregate_bundle_from_metrics(
        first_metric_rows,
        actions=first_actions,
    )
    assert second_bundle == _integrated_aggregate_bundle_from_metrics(
        second_metric_rows,
        actions=second_actions,
    )
    assert first_bundle["task_queue_pressure_and_age"]
    assert second_bundle["task_queue_pressure_and_age"]
    assert first_bundle["lobe_aggregates"]
    assert second_bundle["lobe_aggregates"]
    assert first_bundle["role_action_totals"]
    assert second_bundle["role_action_totals"]
    assert first_bundle != second_bundle


def test_documented_cli_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reconstructs_from_events_across_different_seeds(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_event_bundle_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_event_bundle_seed2"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=1)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=2)

    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        first,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest_reordered_actions",
        expected_actions=("work_task", "create_task", "message", "idle"),
    )
    second_event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        second,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest_reordered_actions",
        expected_actions=("work_task", "create_task", "message", "idle"),
    )

    assert first_event_rows != second_event_rows
    assert first_event_bundle["task_queue_pressure_and_age"]
    assert second_event_bundle["task_queue_pressure_and_age"]
    assert first_event_bundle["lobe_aggregates"]
    assert second_event_bundle["lobe_aggregates"]
    assert first_event_bundle["role_action_totals"]
    assert second_event_bundle["role_action_totals"]
    assert first_event_bundle != second_event_bundle


def test_documented_cli_no_manifest_reordered_actions_per_tick_sequences_reconstruct_from_events(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_event_sequences_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_event_sequences_seed2"

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=1)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=2)

    first_replay = _no_manifest_reordered_actions_event_replay_sequences(first)
    second_replay = _no_manifest_reordered_actions_event_replay_sequences(second)

    assert first_replay["config"] == second_replay["config"]
    assert first_replay["top_level"] == _top_level_metric_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["top_level"] == _top_level_metric_sequence(
        second_replay["metric_rows"]
    )
    assert first_replay["queue_pressure"] == _queue_pressure_metric_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["queue_pressure"] == _queue_pressure_metric_sequence(
        second_replay["metric_rows"]
    )
    assert first_replay["queue_age"] == _queued_task_age_metric_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["queue_age"] == _queued_task_age_metric_sequence(
        second_replay["metric_rows"]
    )
    assert first_replay["role_action"] == _role_action_metric_sequence(
        first_replay["metric_rows"],
        first_replay["actions"],
    )
    assert second_replay["role_action"] == _role_action_metric_sequence(
        second_replay["metric_rows"],
        second_replay["actions"],
    )
    assert first_replay["top_level"]
    assert first_replay["queue_pressure"]
    assert first_replay["queue_age"]
    assert first_replay["role_action"]
    assert (
        first_replay["top_level"],
        first_replay["queue_pressure"],
        first_replay["queue_age"],
        first_replay["role_action"],
    ) != (
        second_replay["top_level"],
        second_replay["queue_pressure"],
        second_replay["queue_age"],
        second_replay["role_action"],
    )


def test_documented_cli_no_manifest_reordered_actions_lobe_sequences_reconstruct_from_events(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_cli_lobe_sequences_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_cli_lobe_sequences_seed2"

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=1)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=2)

    first_replay = _no_manifest_reordered_actions_event_replay_sequences(first)
    second_replay = _no_manifest_reordered_actions_event_replay_sequences(second)
    first_event_lobe_rows = first_replay["event_lobe_rows"]
    second_event_lobe_rows = second_replay["event_lobe_rows"]

    assert first_replay["config"] == second_replay["config"]
    assert set(_lobe_label_sequence(first_event_lobe_rows)) <= set(BASELINE_LOBE_LABELS)
    assert set(_lobe_label_sequence(second_event_lobe_rows)) <= set(BASELINE_LOBE_LABELS)
    assert first_replay["lobe_labels"] == _lobe_label_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["lobe_labels"] == _lobe_label_sequence(
        second_replay["metric_rows"]
    )
    assert first_replay["lobe_transitions"] == _lobe_transition_field_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["lobe_transitions"] == _lobe_transition_field_sequence(
        second_replay["metric_rows"]
    )
    assert first_replay["lobe_run_state"] == _lobe_run_state_sequence(
        first_replay["metric_rows"]
    )
    assert second_replay["lobe_run_state"] == _lobe_run_state_sequence(
        second_replay["metric_rows"]
    )
    _assert_lobe_transitions_match_adjacent_labels(first_event_lobe_rows)
    _assert_lobe_transitions_match_adjacent_labels(second_event_lobe_rows)
    _assert_lobe_run_state_matches_recomputed_dwell_runs(first_event_lobe_rows)
    _assert_lobe_run_state_matches_recomputed_dwell_runs(second_event_lobe_rows)
    assert (
        first_replay["lobe_labels"],
        first_replay["lobe_transitions"],
        first_replay["lobe_run_state"],
    ) != (
        second_replay["lobe_labels"],
        second_replay["lobe_transitions"],
        second_replay["lobe_run_state"],
    )


def test_readme_no_manifest_reordered_actions_lobe_replay_smoke_command(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_no_manifest_reordered_actions_readme_smoke"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_no_manifest_reordered_actions.yaml "
        "--seed 1 --out runs/a0_no_manifest_reordered_actions_seed1"
    )

    assert expected_command in readme

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, out_dir, seed=1)

    event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        out_dir,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest_reordered_actions",
        expected_actions=("work_task", "create_task", "message", "idle"),
    )

    assert event_bundle["task_queue_pressure_and_age"]
    assert event_bundle["lobe_aggregates"]
    assert event_bundle["role_action_totals"]


def test_readme_no_manifest_reordered_actions_same_seed_reproduces_enabled_artifacts(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_readme_seed1_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_readme_seed1_second"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_no_manifest_reordered_actions.yaml "
        "--seed 1 --out runs/a0_no_manifest_reordered_actions_seed1"
    )

    assert expected_command in readme
    assert "manifest.yaml" not in artifacts

    for out_dir in [first, second]:
        _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_config_only_same_seed_preserves_normalized_config_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_config_only_readme_seed1_first"
    second = tmp_path / "a0_config_only_readme_seed1_second"
    artifacts = _expected_artifacts(CONFIG_ONLY)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_config_only.yaml "
        "--seed 1 --out runs/a0_config_only_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml"]

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG_ONLY, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        _assert_config_only_writes_normalized_config(out_dir)
        assert not (out_dir / "manifest.yaml").exists()
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_config_only_reordered_actions_same_seed_preserves_normalized_config_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_config_only_reordered_actions_readme_seed1_first"
    second = tmp_path / "a0_config_only_reordered_actions_readme_seed1_second"
    artifacts = _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_config_only_reordered_actions.yaml "
        "--seed 1 --out runs/a0_config_only_reordered_actions_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml"]

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG_ONLY_REORDERED_ACTIONS, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        _assert_config_only_writes_normalized_config(
            out_dir,
            experiment_id="a0_config_only_reordered_actions",
            actions=["work_task", "create_task", "message", "idle"],
        )
        assert not (out_dir / "manifest.yaml").exists()
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_manifest_only_same_seed_preserves_manifest_provenance(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_manifest_only_readme_seed1_first"
    second = tmp_path / "a0_manifest_only_readme_seed1_second"
    artifacts = _expected_artifacts(MANIFEST_ONLY)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_manifest_only.yaml "
        "--seed 1 --out runs/a0_manifest_only_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml", "manifest.yaml"]

    for out_dir in [first, second]:
        _run_documented_cli(MANIFEST_ONLY, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        _assert_manifest_only_preserves_full_schema_provenance(out_dir, MANIFEST_ONLY)

        normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        actions = _actions_from_normalized_config(normalized_config)

        assert normalized_config["run"]["experiment_id"] == "a0_manifest_only"
        assert actions == ["idle", "message", "create_task", "work_task"]
        assert manifest["experiment_id"] == normalized_config["run"]["experiment_id"]
        assert manifest["seed"] == 1
        assert manifest["actions"] == actions
        assert manifest["config"] == normalized_config
        assert manifest["model"]["metrics"]["fields"] == list(
            metrics_fieldnames(tuple(actions))
        )
        assert manifest["model"]["role_action_metrics"]["fields"] == list(
            role_action_metric_fields(tuple(actions))
        )
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_manifest_only_reordered_actions_same_seed_preserves_manifest_provenance(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_manifest_only_reordered_actions_readme_seed1_first"
    second = tmp_path / "a0_manifest_only_reordered_actions_readme_seed1_second"
    artifacts = _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_manifest_only_reordered_actions.yaml "
        "--seed 1 --out runs/a0_manifest_only_reordered_actions_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml", "manifest.yaml"]

    for out_dir in [first, second]:
        _run_documented_cli(MANIFEST_ONLY_REORDERED_ACTIONS, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        _assert_manifest_only_preserves_full_schema_provenance(
            out_dir,
            MANIFEST_ONLY_REORDERED_ACTIONS,
        )

        normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        actions = _actions_from_normalized_config(normalized_config)

        assert normalized_config["run"]["experiment_id"] == "a0_manifest_only_reordered_actions"
        assert actions == ["work_task", "create_task", "message", "idle"]
        assert manifest["experiment_id"] == normalized_config["run"]["experiment_id"]
        assert manifest["seed"] == 1
        assert manifest["actions"] == actions
        assert manifest["config"] == normalized_config
        assert manifest["model"]["metrics"]["fields"] == list(
            metrics_fieldnames(tuple(actions))
        )
        assert manifest["model"]["role_action_metrics"]["fields"] == list(
            role_action_metric_fields(tuple(actions))
        )

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_no_manifest_same_seed_preserves_emitted_schema_provenance(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_readme_seed1_first"
    second = tmp_path / "a0_no_manifest_readme_seed1_second"
    artifacts = _expected_artifacts(NO_MANIFEST)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_no_manifest.yaml "
        "--seed 1 --out runs/a0_no_manifest_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml", "metrics.csv", "events.csv", "summary.md"]

    for out_dir in [first, second]:
        _run_documented_cli(NO_MANIFEST, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)

        normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
        actions = _actions_from_normalized_config(normalized_config)
        summary = (out_dir / "summary.md").read_text()
        with (out_dir / "metrics.csv").open() as handle:
            metrics_header = next(csv.reader(handle))
        with (out_dir / "events.csv").open() as handle:
            events_header = next(csv.reader(handle))

        assert normalized_config["run"]["experiment_id"] == "a0_no_manifest"
        assert normalized_config["outputs"] == {
            "write_manifest": False,
            "write_metrics": True,
            "write_events": True,
            "write_summary": True,
        }
        assert actions == ["idle", "message", "create_task", "work_task"]
        assert metrics_header == list(metrics_fieldnames(tuple(actions)))
        assert [
            field for field in metrics_header if field.startswith("role_")
        ] == list(role_action_metric_fields(tuple(actions)))
        assert events_header == list(EVENT_FIELDS)
        assert _summary_written_artifacts(summary) == artifacts
        assert "- manifest mirrors emitted artifact schemas: yes" in summary
        assert not (out_dir / "manifest.yaml").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_no_manifest_default_actions_event_replay_bundle_reproducibility(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_readme_event_bundle_first"
    second = tmp_path / "a0_no_manifest_readme_event_bundle_second"
    different = tmp_path / "a0_no_manifest_readme_event_bundle_different"
    artifacts = _expected_artifacts(NO_MANIFEST)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_no_manifest.yaml "
        "--seed 1 --out runs/a0_no_manifest_seed1"
    )

    assert expected_command in readme
    assert artifacts == ["config.yaml", "metrics.csv", "events.csv", "summary.md"]

    _run_documented_cli(NO_MANIFEST, first, seed=17)
    _run_documented_cli(NO_MANIFEST, second, seed=17)
    _run_documented_cli(NO_MANIFEST, different, seed=18)

    bundles = []
    for out_dir in [first, second, different]:
        bundles.append(
            _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
                out_dir,
                expected_artifacts=artifacts,
                expected_experiment_id="a0_no_manifest",
                expected_actions=("idle", "message", "create_task", "work_task"),
            )
        )

    assert bundles[0]
    assert bundles[0] == bundles[1]
    assert bundles[0] != bundles[2]


def test_documented_cli_no_manifest_default_actions_event_replay_reconstructs_lobes_queue_and_roles(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_no_manifest_default_actions_event_replay"
    artifacts = _expected_artifacts(NO_MANIFEST)

    _run_documented_cli(NO_MANIFEST, out_dir, seed=1)
    _assert_artifacts_match_output_directory(out_dir, artifacts)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        out_dir,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest",
        expected_actions=("idle", "message", "create_task", "work_task"),
    )

    assert normalized_config["run"]["experiment_id"] == "a0_no_manifest"
    assert normalized_config["outputs"]["write_manifest"] is False
    assert not (out_dir / "manifest.yaml").exists()
    assert event_bundle["task_queue_pressure_and_age"]
    assert event_bundle["lobe_aggregates"]
    assert event_bundle["role_action_totals"]


def test_run_api_no_manifest_default_actions_event_replay_reconstructs_lobes_queue_and_roles(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_no_manifest_default_actions_api_event_replay"
    artifacts = _expected_artifacts(NO_MANIFEST)

    result = run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)
    _assert_artifacts_match_output_directory(out_dir, artifacts)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    event_bundle = _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
        out_dir,
        expected_artifacts=artifacts,
        expected_experiment_id="a0_no_manifest",
        expected_actions=("idle", "message", "create_task", "work_task"),
    )

    assert result.config.to_dict() == normalized_config
    assert result.seed == 1
    assert normalized_config["run"]["experiment_id"] == "a0_no_manifest"
    assert normalized_config["outputs"]["write_manifest"] is False
    assert not (out_dir / "manifest.yaml").exists()
    assert len(result.metrics) == normalized_config["run"]["ticks"]
    assert len(result.events) == (
        normalized_config["run"]["ticks"] * normalized_config["model"]["agent_count"]
    )
    assert event_bundle["task_queue_pressure_and_age"]
    assert event_bundle["lobe_aggregates"]
    assert event_bundle["role_action_totals"]


def test_run_api_no_manifest_default_actions_event_replay_bundle_reproducibility(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_default_actions_api_event_bundle_first"
    second = tmp_path / "a0_no_manifest_default_actions_api_event_bundle_second"
    different = tmp_path / "a0_no_manifest_default_actions_api_event_bundle_different"
    artifacts = _expected_artifacts(NO_MANIFEST)

    run_experiment(NO_MANIFEST, seed=17, out_dir=first)
    run_experiment(NO_MANIFEST, seed=17, out_dir=second)
    run_experiment(NO_MANIFEST, seed=18, out_dir=different)

    bundles = []
    for out_dir in [first, second, different]:
        bundles.append(
            _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
                out_dir,
                expected_artifacts=artifacts,
                expected_experiment_id="a0_no_manifest",
                expected_actions=("idle", "message", "create_task", "work_task"),
            )
        )

    assert bundles[0]
    assert bundles[0] == bundles[1]
    assert bundles[0] != bundles[2]


def test_documented_cli_no_manifest_default_actions_event_replay_bundle_reproducibility(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_default_actions_cli_event_bundle_first"
    second = tmp_path / "a0_no_manifest_default_actions_cli_event_bundle_second"
    different = tmp_path / "a0_no_manifest_default_actions_cli_event_bundle_different"
    artifacts = _expected_artifacts(NO_MANIFEST)

    _run_documented_cli(NO_MANIFEST, first, seed=17)
    _run_documented_cli(NO_MANIFEST, second, seed=17)
    _run_documented_cli(NO_MANIFEST, different, seed=18)

    bundles = []
    for out_dir in [first, second, different]:
        bundles.append(
            _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
                out_dir,
                expected_artifacts=artifacts,
                expected_experiment_id="a0_no_manifest",
                expected_actions=("idle", "message", "create_task", "work_task"),
            )
        )

    assert bundles[0]
    assert bundles[0] == bundles[1]
    assert bundles[0] != bundles[2]


def test_readme_default_outputs_same_seed_preserves_full_schema_provenance(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_default_outputs_readme_seed1_first"
    second = tmp_path / "a0_default_outputs_readme_seed1_second"
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_default_outputs.yaml "
        "--seed 1 --out runs/a0_default_outputs_seed1"
    )

    assert expected_command in readme
    assert artifacts == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    for out_dir in [first, second]:
        _run_documented_cli(DEFAULT_OUTPUTS, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)

        normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        summary = (out_dir / "summary.md").read_text()
        with (out_dir / "metrics.csv").open() as handle:
            metrics_header = next(csv.reader(handle))
        with (out_dir / "events.csv").open() as handle:
            events_header = next(csv.reader(handle))

        actions = _actions_from_normalized_config(normalized_config)

        assert normalized_config["run"]["experiment_id"] == "a0_default_outputs"
        assert normalized_config["outputs"] == {
            "write_manifest": True,
            "write_metrics": True,
            "write_events": True,
            "write_summary": True,
        }
        assert actions == ["idle", "message", "create_task", "work_task"]
        assert manifest["experiment_id"] == normalized_config["run"]["experiment_id"]
        assert manifest["seed"] == 1
        assert manifest["actions"] == actions
        assert manifest["outputs"] == normalized_config["outputs"]
        assert manifest["artifacts"] == artifacts
        assert manifest["config"] == normalized_config
        assert manifest["model"]["metrics"]["fields"] == list(
            metrics_fieldnames(tuple(actions))
        )
        assert manifest["model"]["role_action_metrics"]["actions"] == actions
        assert manifest["model"]["role_action_metrics"]["fields"] == list(
            role_action_metric_fields(tuple(actions))
        )
        assert metrics_header == manifest["model"]["metrics"]["fields"]
        assert [
            field for field in metrics_header if field.startswith("role_")
        ] == manifest["model"]["role_action_metrics"]["fields"]
        assert events_header == manifest["model"]["events"]["fields"]
        assert _summary_written_artifacts(summary) == artifacts
        _assert_summary_schema_provenance_counts_match_manifest(summary, manifest)
        _assert_summary_output_flags_match_config(summary, normalized_config["outputs"])

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_a0_smoke_first_milestone_command_preserves_full_schema_provenance(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_smoke_readme_seed1"
    artifacts = _expected_artifacts(CONFIG)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_smoke.yaml "
        "--seed 1 --out runs/a0_seed1"
    )

    assert expected_command in readme
    assert artifacts == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    _run_documented_cli(CONFIG, out_dir, seed=1)
    _assert_artifacts_match_output_directory(out_dir, artifacts)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
        metric_rows = list(csv.DictReader(handle, fieldnames=metrics_header))
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))
        event_rows = list(csv.DictReader(handle, fieldnames=events_header))

    actions = _actions_from_normalized_config(normalized_config)

    assert normalized_config["run"]["experiment_id"] == "a0_smoke"
    assert normalized_config["run"]["ticks"] == 100
    assert normalized_config["model"]["agent_count"] == 15
    assert normalized_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert len(metric_rows) == normalized_config["run"]["ticks"]
    assert len(event_rows) == (
        normalized_config["run"]["ticks"] * normalized_config["model"]["agent_count"]
    )
    assert manifest["experiment_id"] == normalized_config["run"]["experiment_id"]
    assert manifest["seed"] == 1
    assert manifest["ticks"] == normalized_config["run"]["ticks"]
    assert manifest["agent_count"] == normalized_config["model"]["agent_count"]
    assert manifest["actions"] == actions
    assert manifest["outputs"] == normalized_config["outputs"]
    assert manifest["artifacts"] == artifacts
    assert manifest["config"] == normalized_config
    assert manifest["model"]["metrics"]["fields"] == list(metrics_fieldnames(tuple(actions)))
    assert manifest["model"]["events"]["fields"] == list(EVENT_FIELDS)
    assert manifest["model"]["role_action_metrics"]["fields"] == list(
        role_action_metric_fields(tuple(actions))
    )
    assert metrics_header == manifest["model"]["metrics"]["fields"]
    assert events_header == manifest["model"]["events"]["fields"]
    assert _summary_written_artifacts(summary) == artifacts
    _assert_config_manifest_and_summary_run_fields_match(
        normalized_config,
        manifest=manifest,
        summary=summary,
        seed=1,
    )
    _assert_manifest_agent_identity_and_roles_match_baseline(manifest)
    _assert_summary_schema_provenance_counts_match_manifest(summary, manifest)
    _assert_summary_output_flags_match_config(summary, normalized_config["outputs"])


def test_readme_a0_smoke_same_seed_reproduces_full_first_milestone_artifacts(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_smoke_readme_seed1_first"
    second = tmp_path / "a0_smoke_readme_seed1_second"
    artifacts = _expected_artifacts(CONFIG)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_smoke.yaml "
        "--seed 1 --out runs/a0_seed1"
    )

    assert expected_command in readme
    assert artifacts == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG, out_dir, seed=1)
        _assert_artifacts_match_output_directory(out_dir, artifacts)

        normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        with (out_dir / "metrics.csv").open() as handle:
            metric_rows = list(csv.DictReader(handle))
        with (out_dir / "events.csv").open() as handle:
            event_rows = list(csv.DictReader(handle))

        assert normalized_config["run"]["experiment_id"] == "a0_smoke"
        assert normalized_config["run"]["ticks"] == 100
        assert normalized_config["model"]["agent_count"] == 15
        assert manifest["seed"] == 1
        assert manifest["artifacts"] == artifacts
        assert len(metric_rows) == normalized_config["run"]["ticks"]
        assert len(event_rows) == (
            normalized_config["run"]["ticks"] * normalized_config["model"]["agent_count"]
        )

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_readme_a0_smoke_different_seed_changes_dynamics_preserving_provenance(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_smoke_readme_seed1"
    second = tmp_path / "a0_smoke_readme_seed2"
    artifacts = _expected_artifacts(CONFIG)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_smoke.yaml "
        "--seed 1 --out runs/a0_seed1"
    )

    assert expected_command in readme
    assert artifacts == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    _run_documented_cli(CONFIG, first, seed=1)
    _run_documented_cli(CONFIG, second, seed=2)

    for out_dir in [first, second]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()

    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
        first_metric_rows = list(csv.DictReader(handle, fieldnames=first_metrics_header))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
        second_metric_rows = list(csv.DictReader(handle, fieldnames=second_metrics_header))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
        first_event_rows = list(csv.DictReader(handle, fieldnames=first_events_header))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))
        second_event_rows = list(csv.DictReader(handle, fieldnames=second_events_header))

    actions = tuple(_actions_from_normalized_config(first_config))

    assert first_config == second_config
    assert first_manifest["seed"] == 1
    assert second_manifest["seed"] == 2
    assert first_manifest["config"] == second_manifest["config"] == first_config
    assert first_manifest["actions"] == second_manifest["actions"] == list(actions)
    assert first_manifest["outputs"] == second_manifest["outputs"] == first_config["outputs"]
    assert first_manifest["artifacts"] == second_manifest["artifacts"] == artifacts
    assert first_manifest["model"] == second_manifest["model"]
    assert first_metrics_header == second_metrics_header == list(metrics_fieldnames(actions))
    assert first_events_header == second_events_header == list(EVENT_FIELDS)
    assert len(first_metric_rows) == len(second_metric_rows) == first_config["run"]["ticks"]
    assert len(first_event_rows) == len(second_event_rows) == (
        first_config["run"]["ticks"] * first_config["model"]["agent_count"]
    )
    _assert_summary_schema_provenance_counts_match_manifest(first_summary, first_manifest)
    _assert_summary_schema_provenance_counts_match_manifest(second_summary, second_manifest)

    assert first_metric_rows != second_metric_rows
    assert first_event_rows != second_event_rows
    assert _summary_integrated_aggregate_bundle(
        first_summary,
        actions=actions,
    ) != _summary_integrated_aggregate_bundle(
        second_summary,
        actions=actions,
    )


def test_readme_a0_smoke_event_replay_reconstructs_first_milestone_summaries(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a0_smoke_readme_event_replay"
    artifacts = _expected_artifacts(CONFIG)
    readme = Path("README.md").read_text()
    expected_command = (
        "python -m ohdyn.run --config configs/a0_smoke.yaml "
        "--seed 1 --out runs/a0_seed1"
    )

    assert expected_command in readme
    assert artifacts == [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    _run_documented_cli(CONFIG, out_dir, seed=1)
    _assert_artifacts_match_output_directory(out_dir, artifacts)

    _assert_full_output_event_replay_matches_metrics_and_summary(
        out_dir,
        expected_experiment_id="a0_smoke",
        expected_ticks=100,
        expected_artifacts=artifacts,
    )


@pytest.mark.parametrize("config_path", (DEFAULT_OUTPUTS, REORDERED_ACTIONS))
def test_documented_cli_full_output_fixture_event_replay_reconstructs_summaries(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_event_replay"
    artifacts = _expected_artifacts(config_path)
    expected_ticks = load_config(config_path).run.ticks

    _run_documented_cli(config_path, out_dir, seed=1)
    _assert_artifacts_match_output_directory(out_dir, artifacts)

    _assert_full_output_event_replay_matches_metrics_and_summary(
        out_dir,
        expected_experiment_id=config_path.stem,
        expected_ticks=expected_ticks,
        expected_artifacts=artifacts,
    )


def test_documented_cli_no_manifest_reordered_actions_seed_difference_preserves_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_seed2"

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, first, seed=1)
    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, second, seed=2)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = tuple(first_config["model"]["actions"])
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert actions == ("work_task", "create_task", "message", "idle")
    assert second_config["model"]["actions"] == list(actions)
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert not (first / "manifest.yaml").exists()
    assert not (second / "manifest.yaml").exists()
    assert _summary_written_artifacts(first_summary) == _expected_artifacts(
        NO_MANIFEST_REORDERED_ACTIONS
    )
    assert _summary_written_artifacts(second_summary) == _expected_artifacts(
        NO_MANIFEST_REORDERED_ACTIONS
    )
    assert first_metrics_header == expected_metrics_fields
    assert second_metrics_header == expected_metrics_fields
    assert first_events_header == list(EVENT_FIELDS)
    assert second_events_header == list(EVENT_FIELDS)
    assert [
        field for field in first_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert [
        field for field in second_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


def test_documented_cli_no_manifest_reordered_actions_same_seed_reproduces_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_seed17_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_seed17_second"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    for out_dir in [first, second]:
        _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, out_dir, seed=17)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = tuple(first_config["model"]["actions"])
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert actions == ("work_task", "create_task", "message", "idle")
    assert second_config["model"]["actions"] == list(actions)
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert _summary_written_artifacts(first_summary) == artifacts
    assert _summary_written_artifacts(second_summary) == artifacts
    assert first_metrics_header == expected_metrics_fields
    assert second_metrics_header == expected_metrics_fields
    assert first_events_header == list(EVENT_FIELDS)
    assert second_events_header == list(EVENT_FIELDS)
    assert [
        field for field in first_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert [
        field for field in second_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_run_api_no_manifest_reordered_actions_same_seed_reproduces_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_api_seed17_first"
    second = tmp_path / "a0_no_manifest_reordered_actions_api_seed17_second"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    first_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=first)
    second_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=second)

    for out_dir in [first, second]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = tuple(first_config["model"]["actions"])
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == second_result.seed == 17
    assert first_result.metrics == second_result.metrics
    assert first_result.events == second_result.events
    assert actions == ("work_task", "create_task", "message", "idle")
    assert second_config["model"]["actions"] == list(actions)
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert _summary_written_artifacts(first_summary) == artifacts
    assert _summary_written_artifacts(second_summary) == artifacts
    assert first_metrics_header == expected_metrics_fields
    assert second_metrics_header == expected_metrics_fields
    assert first_events_header == list(EVENT_FIELDS)
    assert second_events_header == list(EVENT_FIELDS)
    assert [
        field for field in first_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert [
        field for field in second_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_run_api_no_manifest_reordered_actions_seed_difference_preserves_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_reordered_actions_api_seed1"
    second = tmp_path / "a0_no_manifest_reordered_actions_api_seed2"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    first_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=1, out_dir=first)
    second_result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=2, out_dir=second)

    for out_dir in [first, second]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = tuple(first_config["model"]["actions"])
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == 1
    assert second_result.seed == 2
    assert actions == ("work_task", "create_task", "message", "idle")
    assert second_config["model"]["actions"] == list(actions)
    assert first_config["outputs"]["write_manifest"] is False
    assert second_config["outputs"]["write_manifest"] is False
    assert _summary_written_artifacts(first_summary) == artifacts
    assert _summary_written_artifacts(second_summary) == artifacts
    assert first_metrics_header == expected_metrics_fields
    assert second_metrics_header == expected_metrics_fields
    assert first_events_header == list(EVENT_FIELDS)
    assert second_events_header == list(EVENT_FIELDS)
    assert [
        field for field in first_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert [
        field for field in second_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert (
        first_result.metrics != second_result.metrics
        or first_result.events != second_result.events
    )
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_task_queue_pressure_and_age_aggregate_tuple_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_summary_queue_integrity_seed1",
        second_name=f"{config_path.stem}_cli_summary_queue_integrity_seed2",
    )

    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_tuple = _summary_task_queue_pressure_and_age_aggregate_tuple(first_summary)
    second_tuple = _summary_task_queue_pressure_and_age_aggregate_tuple(second_summary)

    assert first_tuple == _task_queue_pressure_and_age_aggregate_tuple_from_metrics(
        first_metric_rows
    )
    assert second_tuple == _task_queue_pressure_and_age_aggregate_tuple_from_metrics(
        second_metric_rows
    )
    assert first_tuple["task_queue_totals"]
    assert second_tuple["task_queue_totals"]
    assert first_tuple["queue_pressure_totals"]
    assert second_tuple["queue_pressure_totals"]
    assert first_tuple["queued_task_age_aggregates"]
    assert second_tuple["queued_task_age_aggregates"]
    assert first_tuple != second_tuple


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_events_per_tick_task_lifecycle_matches_queue_and_task_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_events_task_lifecycle_metrics"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_events_per_tick_task_lifecycle_matches_queue_and_task_metrics(
        metric_rows=metric_rows,
        event_rows=event_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replay_reproduces_queued_task_age_metrics_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_event_replay_queue_age"

    _run_documented_cli(config_path, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_event_replay_reproduces_queued_task_age_metrics(
        metric_rows=metric_rows,
        event_rows=event_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_queued_task_age_metric_sequence_reproduces_across_same_seed_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_cli_event_replayed_queue_age_first",
        second_name=f"{config_path.stem}_cli_event_replayed_queue_age_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _queued_task_age_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _queued_task_age_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _queued_task_age_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _queued_task_age_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert first_replayed_sequence == second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_event_replayed_queued_task_age_metric_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_event_replayed_queue_age_seed1",
        second_name=f"{config_path.stem}_cli_event_replayed_queue_age_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
    with (first / "events.csv").open() as handle:
        first_event_rows = list(csv.DictReader(handle))
    with (second / "events.csv").open() as handle:
        second_event_rows = list(csv.DictReader(handle))

    first_replayed_sequence = _queued_task_age_metric_sequence_from_events(
        first_event_rows,
        ticks=first_manifest["ticks"],
    )
    second_replayed_sequence = _queued_task_age_metric_sequence_from_events(
        second_event_rows,
        ticks=second_manifest["ticks"],
    )

    assert first_replayed_sequence == _queued_task_age_metric_sequence(first_metric_rows)
    assert second_replayed_sequence == _queued_task_age_metric_sequence(second_metric_rows)
    assert first_replayed_sequence
    assert second_replayed_sequence
    assert first_replayed_sequence != second_replayed_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_role_action_summary_totals_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name=f"{config_path.stem}_cli_role_action_summary_seed1",
        second_name=f"{config_path.stem}_cli_role_action_summary_seed2",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))

    first_role_action_totals = _summary_role_action_totals(first_summary)
    second_role_action_totals = _summary_role_action_totals(second_summary)
    first_actions = tuple(first_manifest["actions"])
    second_actions = tuple(second_manifest["actions"])

    assert first_role_action_totals == _role_action_totals_from_metrics(
        first_metric_rows,
        first_actions,
    )
    assert second_role_action_totals == _role_action_totals_from_metrics(
        second_metric_rows,
        second_actions,
    )
    assert first_role_action_totals
    assert second_role_action_totals
    assert first_role_action_totals != second_role_action_totals


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_role_action_metric_sequence_changes_across_different_seeds_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    first = tmp_path / f"{config_path.stem}_cli_role_action_sequence_seed1"
    second = tmp_path / f"{config_path.stem}_cli_role_action_sequence_seed2"

    _run_documented_cli(config_path, first, seed=1)
    _run_documented_cli(config_path, second, seed=2)

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    with (first / "metrics.csv").open() as handle:
        first_metric_rows = list(csv.DictReader(handle))
        first_header = list(first_metric_rows[0])
    with (second / "metrics.csv").open() as handle:
        second_metric_rows = list(csv.DictReader(handle))
        second_header = list(second_metric_rows[0])

    first_actions = tuple(first_manifest["actions"])
    second_actions = tuple(second_manifest["actions"])
    first_expected_fields = list(role_action_metric_fields(first_actions))
    second_expected_fields = list(role_action_metric_fields(second_actions))
    first_sequence = _role_action_metric_sequence(first_metric_rows, first_actions)
    second_sequence = _role_action_metric_sequence(second_metric_rows, second_actions)

    assert first_manifest["model"]["role_action_metrics"]["fields"] == first_expected_fields
    assert second_manifest["model"]["role_action_metrics"]["fields"] == second_expected_fields
    assert [field for field in first_header if field.startswith("role_")] == first_expected_fields
    assert [field for field in second_header if field.startswith("role_")] == second_expected_fields
    assert first_sequence
    assert second_sequence
    assert first_sequence != second_sequence


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_lobe_totals_use_only_manifest_lobe_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_lobe_manifest_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_lobe_totals_use_only_manifest_lobe_labels(
        summary,
        manifest=manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_summary_lobe_dwell_runs_use_only_manifest_lobe_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_summary_lobe_dwell_manifest_labels"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))

    _assert_summary_lobe_dwell_runs_use_only_manifest_lobe_labels(
        summary,
        manifest=manifest,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_lobe_fields_match_metrics_header_and_observed_labels_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_lobe_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    _assert_manifest_lobe_fields_match_metrics_header_and_observed_labels(
        manifest,
        metrics_header=metrics_header,
        metric_rows=metric_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_event_types_cover_observed_events_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_event_types"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    _assert_manifest_event_types_cover_observed_events(
        manifest,
        event_rows=event_rows,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_metrics_fields_exactly_match_metrics_header_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_metrics_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    _assert_manifest_metrics_fields_match_metrics_header(
        manifest,
        metrics_header=metrics_header,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_role_action_fields_exactly_match_metrics_header_subset_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_role_action_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    _assert_manifest_role_action_fields_match_metrics_header_subset(
        manifest,
        metrics_header=metrics_header,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_queue_dynamics_fields_exactly_match_metrics_header_subsets_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_queue_dynamics_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))

    _assert_manifest_queue_dynamics_fields_match_metrics_header_subsets(
        manifest,
        metrics_header=metrics_header,
    )


@pytest.mark.parametrize("config_path", FULL_OUTPUT_FIXTURES)
def test_documented_cli_manifest_event_fields_exactly_match_events_header_across_full_output_fixtures(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_manifest_event_fields"

    _run_documented_cli(config_path, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))

    _assert_manifest_event_fields_match_events_header(
        manifest,
        events_header=events_header,
    )


def test_summary_records_written_artifacts_and_output_flags(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()
    assert "## Run artifacts and outputs" in summary
    assert "- written artifacts: config.yaml, manifest.yaml, metrics.csv, events.csv, summary.md" in summary
    assert "- write_manifest: enabled" in summary
    assert "- write_metrics: enabled" in summary
    assert "- write_events: enabled" in summary
    assert "- write_summary: enabled" in summary


def test_summary_written_artifacts_match_manifest_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    summary_artifacts = _summary_written_artifacts(summary)

    assert summary_artifacts == manifest["artifacts"]


def test_summary_written_artifacts_match_output_directory_contents(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    _assert_summary_written_artifacts_match_output_directory(out_dir)


def test_summary_written_artifacts_match_output_directory_contents_without_manifest(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest"

    run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)

    summary_artifacts = _assert_summary_written_artifacts_match_output_directory(out_dir)

    assert "manifest.yaml" not in summary_artifacts


@pytest.mark.parametrize(
    ("config_path", "expected_artifacts"),
    [
        (DEFAULT_OUTPUTS, _expected_artifacts(DEFAULT_OUTPUTS)),
        (CONFIG_ONLY, _expected_artifacts(CONFIG_ONLY)),
        (
            CONFIG_ONLY_REORDERED_ACTIONS,
            _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
        ),
        (MANIFEST_ONLY, _expected_artifacts(MANIFEST_ONLY)),
        (
            MANIFEST_ONLY_REORDERED_ACTIONS,
            _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS),
        ),
        (NO_MANIFEST, _expected_artifacts(NO_MANIFEST)),
        (
            NO_MANIFEST_REORDERED_ACTIONS,
            _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS),
        ),
    ],
)
def test_artifact_indexes_match_directory_contents_across_output_flag_fixtures(
    tmp_path: Path,
    config_path: Path,
    expected_artifacts: list[str],
) -> None:
    out_dir = tmp_path / config_path.stem

    run_experiment(config_path, seed=1, out_dir=out_dir)

    _assert_artifact_indexes_match_directory_contents(out_dir, expected_artifacts)


def test_summary_records_disabled_manifest_output_flag(tmp_path: Path) -> None:
    out_dir = tmp_path / "no_manifest"

    run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)

    summary = (out_dir / "summary.md").read_text()
    assert "- written artifacts: config.yaml, metrics.csv, events.csv, summary.md" in summary
    assert "- write_manifest: disabled" in summary
    assert "- write_metrics: enabled" in summary
    assert "- write_events: enabled" in summary
    assert "- write_summary: enabled" in summary
    assert not (out_dir / "manifest.yaml").exists()


def test_manifest_lists_only_written_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "manifest_only"

    run_experiment(MANIFEST_ONLY, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_manifest_artifacts_match_output_directory_contents_when_manifest_only(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only"

    run_experiment(MANIFEST_ONLY, seed=1, out_dir=out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())

    _assert_artifacts_match_output_directory(out_dir, manifest["artifacts"])
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)


@pytest.mark.parametrize("config_path", MANIFEST_ONLY_FIXTURES)
def test_manifest_only_records_full_schema_provenance_without_disabled_artifacts(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_schema"

    run_experiment(config_path, seed=1, out_dir=out_dir)

    _assert_manifest_only_preserves_full_schema_provenance(out_dir, config_path)


def test_manifest_only_reordered_actions_records_schema_order_without_disabled_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_reordered_actions_schema"

    run_experiment(MANIFEST_ONLY_REORDERED_ACTIONS, seed=1, out_dir=out_dir)

    _assert_manifest_only_preserves_full_schema_provenance(
        out_dir,
        MANIFEST_ONLY_REORDERED_ACTIONS,
    )

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    actions = _actions_from_normalized_config(normalized_config)
    expected_role_action_fields = list(role_action_metric_fields(tuple(actions)))
    expected_metrics_fields = list(metrics_fieldnames(tuple(actions)))

    assert actions == ["work_task", "create_task", "message", "idle"]
    assert manifest["actions"] == actions
    assert manifest["config"]["model"]["actions"] == actions
    assert manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert manifest["model"]["role_action_metrics"]["actions"] == actions
    assert manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields


def test_documented_cli_manifest_only_artifacts_match_output_directory_contents(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_cli"

    _run_documented_cli(MANIFEST_ONLY, out_dir)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())

    _assert_artifacts_match_output_directory(out_dir, manifest["artifacts"])
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


@pytest.mark.parametrize("config_path", MANIFEST_ONLY_FIXTURES)
def test_documented_cli_manifest_only_records_full_schema_provenance_without_disabled_artifacts(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_schema"

    _run_documented_cli(config_path, out_dir)

    _assert_manifest_only_preserves_full_schema_provenance(out_dir, config_path)


def test_documented_cli_manifest_only_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_cli_stale_disabled"
    stale_disabled_artifacts = _write_manifest_only_disabled_artifact_sentinels(out_dir)

    _run_documented_cli(MANIFEST_ONLY, out_dir)
    _assert_manifest_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)
    assert manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["seed"] == 1
    assert manifest["experiment_id"] == "a0_manifest_only"


@pytest.mark.parametrize("collision_artifact", ["config.yaml", "manifest.yaml"])
def test_documented_cli_manifest_only_refuses_enabled_artifact_collisions_while_preserving_stale_disabled_artifacts(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    out_dir = tmp_path / f"manifest_only_cli_collision_{collision_artifact.replace('.', '_')}"
    stale_disabled_artifacts, collision_content = _write_manifest_only_collision_sentinels(
        out_dir,
        collision_artifact,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(MANIFEST_ONLY),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "already contains run artifacts" in completed.stderr
    assert collision_artifact in completed.stderr
    assert "metrics.csv" not in completed.stderr
    assert "events.csv" not in completed.stderr
    assert "summary.md" not in completed.stderr
    assert "Traceback" not in completed.stderr
    _assert_manifest_only_collision_preserves_stale_disabled_artifacts(
        out_dir,
        collision_artifact,
        stale_disabled_artifacts=stale_disabled_artifacts,
        collision_content=collision_content,
    )


def test_documented_cli_config_only_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_cli_stale_disabled"
    stale_disabled_artifacts = _write_config_only_disabled_artifact_sentinels(out_dir)

    _run_documented_cli(CONFIG_ONLY, out_dir)
    _assert_config_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )
    _assert_config_only_writes_normalized_config(out_dir)


def test_run_api_config_only_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_api_stale_disabled"
    stale_disabled_artifacts = _write_config_only_disabled_artifact_sentinels(out_dir)

    result = run_experiment(CONFIG_ONLY, seed=1, out_dir=out_dir)

    assert result.config.run.experiment_id == "a0_config_only"
    assert result.seed == 1
    assert len(result.metrics) == 3
    assert len(result.events) == 45
    _assert_config_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )
    _assert_config_only_writes_normalized_config(out_dir)


def test_run_api_manifest_only_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_api_stale_disabled"
    stale_disabled_artifacts = _write_manifest_only_disabled_artifact_sentinels(out_dir)

    result = run_experiment(MANIFEST_ONLY, seed=1, out_dir=out_dir)

    assert result.config.run.experiment_id == "a0_manifest_only"
    assert result.seed == 1
    assert len(result.metrics) == 3
    assert len(result.events) == 45
    _assert_manifest_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)
    assert manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["seed"] == 1
    assert manifest["experiment_id"] == "a0_manifest_only"


@pytest.mark.parametrize("collision_artifact", ["config.yaml", "manifest.yaml"])
def test_run_api_manifest_only_refuses_enabled_artifact_collisions_while_preserving_stale_disabled_artifacts(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    out_dir = tmp_path / f"manifest_only_api_collision_{collision_artifact.replace('.', '_')}"
    stale_disabled_artifacts, collision_content = _write_manifest_only_collision_sentinels(
        out_dir,
        collision_artifact,
    )

    with pytest.raises(FileExistsError, match="already contains run artifacts") as exc_info:
        run_experiment(MANIFEST_ONLY, seed=1, out_dir=out_dir)

    message = str(exc_info.value)
    assert str(out_dir) in message
    assert collision_artifact in message
    assert "metrics.csv" not in message
    assert "events.csv" not in message
    assert "summary.md" not in message
    _assert_manifest_only_collision_preserves_stale_disabled_artifacts(
        out_dir,
        collision_artifact,
        stale_disabled_artifacts=stale_disabled_artifacts,
        collision_content=collision_content,
    )


def test_documented_cli_no_manifest_summary_artifacts_match_output_directory_contents(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_cli"

    _run_documented_cli(NO_MANIFEST, out_dir)

    _assert_summary_written_artifacts_match_output_directory(out_dir)
    _assert_no_manifest_writes_enabled_artifacts(out_dir)


@pytest.mark.parametrize("config_path", NO_MANIFEST_FIXTURES)
def test_documented_cli_no_manifest_emitted_artifacts_preserve_schema_provenance(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_cli_schema"

    _run_documented_cli(config_path, out_dir)

    _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)


def test_documented_cli_no_manifest_preserves_stale_manifest_sentinel(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_cli_stale_manifest"
    stale_manifest = _write_no_manifest_disabled_manifest_sentinel(out_dir)

    _run_documented_cli(NO_MANIFEST, out_dir)
    _assert_no_manifest_preserves_stale_disabled_manifest(
        out_dir,
        stale_manifest=stale_manifest,
    )


@pytest.mark.parametrize("collision_artifact", ["config.yaml", "metrics.csv", "events.csv", "summary.md"])
def test_documented_cli_no_manifest_refuses_enabled_artifact_collisions_while_preserving_stale_manifest(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    out_dir = tmp_path / f"no_manifest_cli_collision_{collision_artifact.replace('.', '_')}"
    stale_manifest, collision_content = _write_no_manifest_collision_sentinels(
        out_dir,
        collision_artifact,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(NO_MANIFEST),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "already contains run artifacts" in completed.stderr
    assert collision_artifact in completed.stderr
    assert "manifest.yaml" not in completed.stderr
    assert "Traceback" not in completed.stderr
    _assert_no_manifest_collision_preserves_stale_manifest(
        out_dir,
        collision_artifact,
        stale_manifest=stale_manifest,
        collision_content=collision_content,
    )


def test_run_api_no_manifest_preserves_stale_disabled_manifest_sentinel(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_api_stale_manifest"
    stale_manifest = _write_no_manifest_disabled_manifest_sentinel(out_dir)

    result = run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)

    assert result.config.run.experiment_id == "a0_no_manifest"
    assert result.seed == 1
    assert result.config.outputs.write_manifest is False
    assert len(result.metrics) == 3
    assert len(result.events) == 45
    _assert_no_manifest_preserves_stale_disabled_manifest(
        out_dir,
        stale_manifest=stale_manifest,
    )

    with (out_dir / "metrics.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 3
    with (out_dir / "events.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 45


@pytest.mark.parametrize("config_path", NO_MANIFEST_FIXTURES)
def test_run_api_no_manifest_emitted_artifacts_preserve_schema_provenance(
    tmp_path: Path,
    config_path: Path,
) -> None:
    out_dir = tmp_path / f"{config_path.stem}_api_schema"

    result = run_experiment(config_path, seed=1, out_dir=out_dir)

    assert result.config.run.experiment_id == load_config(config_path).run.experiment_id
    assert result.seed == 1
    assert result.config.outputs.write_manifest is False

    _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)


@pytest.mark.parametrize("collision_artifact", ["config.yaml", "metrics.csv", "events.csv", "summary.md"])
def test_run_api_no_manifest_refuses_enabled_artifact_collisions_while_ignoring_stale_manifest(
    tmp_path: Path,
    collision_artifact: str,
) -> None:
    out_dir = tmp_path / f"no_manifest_api_collision_{collision_artifact.replace('.', '_')}"
    stale_manifest, collision_content = _write_no_manifest_collision_sentinels(
        out_dir,
        collision_artifact,
    )

    with pytest.raises(FileExistsError, match=collision_artifact):
        run_experiment(NO_MANIFEST, seed=1, out_dir=out_dir)

    _assert_no_manifest_collision_preserves_stale_manifest(
        out_dir,
        collision_artifact,
        stale_manifest=stale_manifest,
        collision_content=collision_content,
    )


def test_output_flags_must_be_yaml_booleans(tmp_path: Path) -> None:
    config_path = tmp_path / "string_bool.yaml"
    config_path.write_text(
        """
run:
  experiment_id: string_bool
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  write_metrics: "false"
"""
    )

    with pytest.raises(ValueError, match="outputs.write_metrics"):
        load_config(config_path)


@pytest.mark.parametrize(
    ("config_text", "message"),
    [
        (
            """
model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task
""",
            "section 'run'",
        ),
        (
            """
run:
  experiment_id: missing_model
  ticks: 3
""",
            "section 'model'",
        ),
        (
            """
run:
  experiment_id: list_outputs
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

outputs:
  - write_metrics
""",
            "section 'outputs'",
        ),
    ],
)
def test_required_config_sections_must_be_yaml_mappings(
    tmp_path: Path,
    config_text: str,
    message: str,
) -> None:
    config_path = tmp_path / "invalid_section.yaml"
    config_path.write_text(config_text)

    with pytest.raises(ValueError, match=message):
        load_config(config_path)


@pytest.mark.parametrize(
    ("actions_yaml", "message"),
    [
        (
            """
    - idle
    - message
    - create_task
""",
            "missing required baseline actions: work_task",
        ),
        (
            """
    - idle
    - message
    - create_task
    - work_task
    - browse_web
""",
            "unsupported baseline actions: browse_web",
        ),
        (
            """
    - idle
    - message
    - create_task
    - work_task
    - work_task
""",
            "must not contain duplicates",
        ),
    ],
)
def test_baseline_actions_must_be_required_unique_and_supported(
    tmp_path: Path,
    actions_yaml: str,
    message: str,
) -> None:
    config_path = tmp_path / "invalid_actions.yaml"
    config_path.write_text(
        f"""
run:
  experiment_id: invalid_actions
  ticks: 3

model:
  agent_count: 15
  actions:{actions_yaml}
"""
    )

    with pytest.raises(ValueError, match=message):
        load_config(config_path)


def test_documented_cli_smoke_writes_required_a0_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"
    expected_artifacts = _expected_artifacts(CONFIG)

    _run_documented_cli(CONFIG, out_dir)
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == expected_artifacts
    assert manifest["seed"] == 1
    assert manifest["experiment_id"] == "a0_smoke"


def test_documented_cli_omitted_outputs_defaults_to_full_a0_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "default_outputs_seed1"
    expected_artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    _run_documented_cli(DEFAULT_OUTPUTS, out_dir)
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert normalized_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert manifest["outputs"] == normalized_config["outputs"]
    assert manifest["artifacts"] == expected_artifacts
    assert manifest["experiment_id"] == "a0_default_outputs"


def test_documented_cli_omitted_outputs_same_seed_reproduces_byte_identical_artifacts(
    tmp_path: Path,
) -> None:
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)
    first, second, _, _ = _run_documented_cli_pair(
        DEFAULT_OUTPUTS,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name="default_outputs_seed17_first",
        second_name="default_outputs_seed17_second",
    )

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    assert first_manifest["experiment_id"] == "a0_default_outputs"
    assert second_manifest["experiment_id"] == "a0_default_outputs"
    assert first_manifest["outputs"] == second_manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    _assert_artifacts_are_byte_identical(first, second, artifacts)


@pytest.mark.parametrize("config_path", (DEFAULT_OUTPUTS, REORDERED_ACTIONS))
def test_documented_cli_full_output_fixture_same_seed_reproduces_byte_identical_enabled_artifacts(
    tmp_path: Path,
    config_path: Path,
) -> None:
    artifacts = _expected_artifacts(config_path)

    assert artifacts == A0_FULL_ARTIFACTS

    first, second, _, _ = _run_documented_cli_pair(
        config_path,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name=f"{config_path.stem}_full_output_seed17_first",
        second_name=f"{config_path.stem}_full_output_seed17_second",
    )

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    actions = _actions_from_normalized_config(first_config)

    assert first_config == second_config
    assert first_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert first_manifest["experiment_id"] == first_config["run"]["experiment_id"]
    assert second_manifest["experiment_id"] == second_config["run"]["experiment_id"]
    assert first_manifest["actions"] == second_manifest["actions"] == actions
    assert first_manifest["artifacts"] == second_manifest["artifacts"] == artifacts

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_documented_cli_reordered_actions_different_seed_preserves_full_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_reordered_actions_seed1"
    second = tmp_path / "a0_reordered_actions_seed2"
    artifacts = _expected_artifacts(REORDERED_ACTIONS)

    for seed, out_dir in [(1, first), (2, second)]:
        _run_documented_cli(REORDERED_ACTIONS, out_dir, seed=seed)
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = _actions_from_normalized_config(first_config)
    expected_metrics_fields = list(metrics_fieldnames(tuple(actions)))

    assert actions == ["work_task", "create_task", "message", "idle"]
    assert first_config == second_config
    assert first_manifest["seed"] == 1
    assert second_manifest["seed"] == 2
    assert first_manifest["config"] == second_manifest["config"] == first_config
    assert first_manifest["actions"] == second_manifest["actions"] == actions
    assert first_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert second_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert first_manifest["model"]["events"]["fields"] == list(EVENT_FIELDS)
    assert second_manifest["model"]["events"]["fields"] == list(EVENT_FIELDS)
    assert first_metrics_header == second_metrics_header == expected_metrics_fields
    assert first_events_header == second_events_header == list(EVENT_FIELDS)
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


def test_documented_cli_default_outputs_different_seed_preserves_full_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_default_outputs_seed1"
    second = tmp_path / "a0_default_outputs_seed2"
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    for seed, out_dir in [(1, first), (2, second)]:
        _run_documented_cli(DEFAULT_OUTPUTS, out_dir, seed=seed)
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = _actions_from_normalized_config(first_config)
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(tuple(actions)))

    assert artifacts == A0_FULL_ARTIFACTS
    assert actions == ["idle", "message", "create_task", "work_task"]
    assert first_config == second_config
    assert first_config["outputs"] == expected_outputs
    assert first_manifest["seed"] == 1
    assert second_manifest["seed"] == 2
    assert first_manifest["outputs"] == second_manifest["outputs"] == expected_outputs
    assert first_manifest["config"] == second_manifest["config"] == first_config
    assert first_manifest["actions"] == second_manifest["actions"] == actions
    assert first_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert second_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert first_manifest["model"]["events"]["fields"] == list(EVENT_FIELDS)
    assert second_manifest["model"]["events"]["fields"] == list(EVENT_FIELDS)
    assert first_metrics_header == second_metrics_header == expected_metrics_fields
    assert first_events_header == second_events_header == list(EVENT_FIELDS)
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


def test_documented_cli_no_manifest_different_seed_preserves_emitted_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_seed1"
    second = tmp_path / "a0_no_manifest_seed2"
    artifacts = _expected_artifacts(NO_MANIFEST)

    for seed, out_dir in [(1, first), (2, second)]:
        _run_documented_cli(NO_MANIFEST, out_dir, seed=seed)
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = _actions_from_normalized_config(first_config)
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(tuple(actions)))

    assert artifacts == NO_MANIFEST_ARTIFACTS
    assert actions == ["idle", "message", "create_task", "work_task"]
    assert first_config == second_config
    assert first_config["outputs"] == expected_outputs
    assert second_config["outputs"] == expected_outputs
    assert first_metrics_header == second_metrics_header == expected_metrics_fields
    assert first_events_header == second_events_header == list(EVENT_FIELDS)
    assert _summary_written_artifacts(first_summary) == artifacts
    assert _summary_written_artifacts(second_summary) == artifacts
    for summary in [first_summary, second_summary]:
        _assert_summary_records_artifact_schema_provenance(
            summary,
            metrics_header=first_metrics_header,
            events_header=first_events_header,
            actions=tuple(actions),
        )
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


def test_run_api_no_manifest_different_seed_preserves_emitted_schema_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a0_no_manifest_api_seed1"
    second = tmp_path / "a0_no_manifest_api_seed2"
    artifacts = _expected_artifacts(NO_MANIFEST)

    first_result = run_experiment(NO_MANIFEST, seed=1, out_dir=first)
    second_result = run_experiment(NO_MANIFEST, seed=2, out_dir=second)

    for out_dir in [first, second]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()
        _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)

    first_config = yaml.safe_load((first / "config.yaml").read_text())
    second_config = yaml.safe_load((second / "config.yaml").read_text())
    first_summary = (first / "summary.md").read_text()
    second_summary = (second / "summary.md").read_text()
    first_metrics_text = (first / "metrics.csv").read_text()
    second_metrics_text = (second / "metrics.csv").read_text()
    first_events_text = (first / "events.csv").read_text()
    second_events_text = (second / "events.csv").read_text()
    with (first / "metrics.csv").open() as handle:
        first_metrics_header = next(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics_header = next(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events_header = next(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events_header = next(csv.reader(handle))

    actions = tuple(first_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))

    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == 1
    assert second_result.seed == 2
    assert artifacts == NO_MANIFEST_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert second_config["model"]["actions"] == list(actions)
    assert first_config["outputs"] == expected_outputs
    assert second_config["outputs"] == expected_outputs
    assert first_metrics_header == second_metrics_header == expected_metrics_fields
    assert first_events_header == second_events_header == list(EVENT_FIELDS)
    assert _summary_written_artifacts(first_summary) == artifacts
    assert _summary_written_artifacts(second_summary) == artifacts
    assert (
        first_result.metrics != second_result.metrics
        or first_result.events != second_result.events
    )
    assert first_metrics_text != second_metrics_text or first_events_text != second_events_text


def test_documented_cli_and_run_api_default_outputs_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_default_outputs_cli_seed1"
    api_out = tmp_path / "a0_default_outputs_api_seed1"
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    _run_documented_cli(DEFAULT_OUTPUTS, cli_out, seed=1)
    result = run_experiment(DEFAULT_OUTPUTS, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    cli_manifest = yaml.safe_load((cli_out / "manifest.yaml").read_text())
    api_manifest = yaml.safe_load((api_out / "manifest.yaml").read_text())
    with (api_out / "metrics.csv").open() as handle:
        api_metrics_header = next(csv.reader(handle))
    with (api_out / "events.csv").open() as handle:
        api_events_header = next(csv.reader(handle))
    api_summary = (api_out / "summary.md").read_text()
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    assert artifacts == A0_FULL_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert cli_config == api_config
    assert cli_manifest == api_manifest
    assert api_config["outputs"] == expected_outputs
    assert api_manifest["outputs"] == expected_outputs
    assert api_manifest["artifacts"] == artifacts
    assert api_manifest["actions"] == list(actions)
    assert api_manifest["config"] == api_config
    assert api_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert api_manifest["model"]["role_action_metrics"]["actions"] == list(actions)
    assert api_manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert api_metrics_header == expected_metrics_fields
    assert api_events_header == list(EVENT_FIELDS)
    assert _summary_written_artifacts(api_summary) == artifacts
    _assert_summary_records_artifact_schema_provenance(
        api_summary,
        metrics_header=api_metrics_header,
        events_header=api_events_header,
        actions=actions,
    )
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_smoke_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_smoke_cli_seed1"
    api_out = tmp_path / "a0_smoke_api_seed1"
    artifacts = _expected_artifacts(CONFIG)

    _run_documented_cli(CONFIG, cli_out, seed=1)
    result = run_experiment(CONFIG, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    cli_manifest = yaml.safe_load((cli_out / "manifest.yaml").read_text())
    api_manifest = yaml.safe_load((api_out / "manifest.yaml").read_text())
    with (api_out / "metrics.csv").open() as handle:
        api_metrics_rows = list(csv.reader(handle))
    with (api_out / "events.csv").open() as handle:
        api_events_rows = list(csv.reader(handle))
    api_metrics_header = api_metrics_rows[0]
    api_events_header = api_events_rows[0]
    api_summary = (api_out / "summary.md").read_text()
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    assert artifacts == A0_FULL_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert cli_config == api_config
    assert cli_manifest == api_manifest
    assert api_config["run"]["experiment_id"] == "a0_smoke"
    assert api_config["run"]["ticks"] == 100
    assert api_config["outputs"] == expected_outputs
    assert api_manifest["experiment_id"] == "a0_smoke"
    assert api_manifest["seed"] == 1
    assert api_manifest["ticks"] == 100
    assert api_manifest["outputs"] == expected_outputs
    assert api_manifest["artifacts"] == artifacts
    assert api_manifest["actions"] == list(actions)
    assert api_manifest["config"] == api_config
    assert api_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert api_manifest["model"]["role_action_metrics"]["actions"] == list(actions)
    assert api_manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert len(api_metrics_rows) == 101
    assert len(api_events_rows) == 1501
    assert len(result.metrics) == 100
    assert len(result.events) == 1500
    assert api_metrics_header == expected_metrics_fields
    assert api_events_header == list(EVENT_FIELDS)
    assert _summary_written_artifacts(api_summary) == artifacts
    _assert_summary_records_artifact_schema_provenance(
        api_summary,
        metrics_header=api_metrics_header,
        events_header=api_events_header,
        actions=actions,
    )
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_reordered_actions_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_reordered_actions_cli_seed1"
    api_out = tmp_path / "a0_reordered_actions_api_seed1"
    artifacts = _expected_artifacts(REORDERED_ACTIONS)

    _run_documented_cli(REORDERED_ACTIONS, cli_out, seed=1)
    result = run_experiment(REORDERED_ACTIONS, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    cli_manifest = yaml.safe_load((cli_out / "manifest.yaml").read_text())
    api_manifest = yaml.safe_load((api_out / "manifest.yaml").read_text())
    with (api_out / "metrics.csv").open() as handle:
        api_metrics_header = next(csv.reader(handle))
    with (api_out / "events.csv").open() as handle:
        api_events_header = next(csv.reader(handle))
    api_summary = (api_out / "summary.md").read_text()
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)

    assert artifacts == A0_FULL_ARTIFACTS
    assert actions == ("work_task", "create_task", "message", "idle")
    assert cli_config == api_config
    assert cli_manifest == api_manifest
    assert api_config["outputs"] == expected_outputs
    assert api_manifest["outputs"] == expected_outputs
    assert api_manifest["artifacts"] == artifacts
    assert api_manifest["actions"] == list(actions)
    assert api_manifest["config"] == api_config
    assert api_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert api_manifest["model"]["role_action_metrics"]["actions"] == list(actions)
    assert api_manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert api_metrics_header == expected_metrics_fields
    assert api_events_header == list(EVENT_FIELDS)
    assert _summary_written_artifacts(api_summary) == artifacts
    _assert_summary_records_artifact_schema_provenance(
        api_summary,
        metrics_header=api_metrics_header,
        events_header=api_events_header,
        actions=actions,
    )
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_no_manifest_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_no_manifest_cli_seed1"
    api_out = tmp_path / "a0_no_manifest_api_seed1"
    artifacts = _expected_artifacts(NO_MANIFEST)

    _run_documented_cli(NO_MANIFEST, cli_out, seed=1)
    result = run_experiment(NO_MANIFEST, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    with (api_out / "metrics.csv").open() as handle:
        api_metrics_rows = list(csv.reader(handle))
    with (api_out / "events.csv").open() as handle:
        api_events_rows = list(csv.reader(handle))
    api_metrics_header = api_metrics_rows[0]
    api_events_header = api_events_rows[0]
    api_summary = (api_out / "summary.md").read_text()
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()
        _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)

    assert artifacts == NO_MANIFEST_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert cli_config == api_config
    assert api_config["run"]["experiment_id"] == "a0_no_manifest"
    assert api_config["run"]["ticks"] == 3
    assert api_config["outputs"] == expected_outputs
    assert api_metrics_header == expected_metrics_fields
    assert api_events_header == list(EVENT_FIELDS)
    assert [
        field for field in api_metrics_header if field.startswith("role_")
    ] == expected_role_action_fields
    assert len(api_metrics_rows) == 4
    assert len(api_events_rows) == 46
    assert len(result.metrics) == 3
    assert len(result.events) == 45
    assert _summary_written_artifacts(api_summary) == artifacts
    _assert_summary_records_artifact_schema_provenance(
        api_summary,
        metrics_header=api_metrics_header,
        events_header=api_events_header,
        actions=actions,
    )
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_no_manifest_reordered_actions_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_no_manifest_reordered_actions_cli_seed1"
    api_out = tmp_path / "a0_no_manifest_reordered_actions_api_seed1"
    artifacts = _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)

    _run_documented_cli(NO_MANIFEST_REORDERED_ACTIONS, cli_out, seed=1)
    result = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()
        _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(out_dir)

    assert artifacts == NO_MANIFEST_ARTIFACTS
    assert actions == ("work_task", "create_task", "message", "idle")
    assert cli_config == api_config
    assert api_config["outputs"] == expected_outputs
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_config_only_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_config_only_cli_seed1"
    api_out = tmp_path / "a0_config_only_api_seed1"
    artifacts = _expected_artifacts(CONFIG_ONLY)

    _run_documented_cli(CONFIG_ONLY, cli_out, seed=1)
    result = run_experiment(CONFIG_ONLY, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    assert artifacts == CONFIG_ONLY_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert cli_config == api_config
    assert api_config["outputs"] == expected_outputs
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_config_only_reordered_actions_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_config_only_reordered_actions_cli_seed1"
    api_out = tmp_path / "a0_config_only_reordered_actions_api_seed1"
    artifacts = _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS)

    _run_documented_cli(CONFIG_ONLY_REORDERED_ACTIONS, cli_out, seed=1)
    result = run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "manifest.yaml").exists()
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    assert artifacts == CONFIG_ONLY_ARTIFACTS
    assert actions == ("work_task", "create_task", "message", "idle")
    assert cli_config == api_config
    assert api_config["outputs"] == expected_outputs
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_manifest_only_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_manifest_only_cli_seed1"
    api_out = tmp_path / "a0_manifest_only_api_seed1"
    artifacts = _expected_artifacts(MANIFEST_ONLY)

    _run_documented_cli(MANIFEST_ONLY, cli_out, seed=1)
    result = run_experiment(MANIFEST_ONLY, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    cli_manifest = yaml.safe_load((cli_out / "manifest.yaml").read_text())
    api_manifest = yaml.safe_load((api_out / "manifest.yaml").read_text())
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    assert artifacts == MANIFEST_ONLY_ARTIFACTS
    assert actions == ("idle", "message", "create_task", "work_task")
    assert cli_config == api_config
    assert cli_manifest == api_manifest
    assert api_config["outputs"] == expected_outputs
    assert api_manifest["outputs"] == expected_outputs
    assert api_manifest["artifacts"] == artifacts
    assert api_manifest["actions"] == list(actions)
    assert api_manifest["config"] == api_config
    assert api_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert api_manifest["model"]["role_action_metrics"]["actions"] == list(actions)
    assert api_manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_and_run_api_manifest_only_reordered_actions_seed1_emit_identical_artifacts(
    tmp_path: Path,
) -> None:
    cli_out = tmp_path / "a0_manifest_only_reordered_actions_cli_seed1"
    api_out = tmp_path / "a0_manifest_only_reordered_actions_api_seed1"
    artifacts = _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS)

    _run_documented_cli(MANIFEST_ONLY_REORDERED_ACTIONS, cli_out, seed=1)
    result = run_experiment(MANIFEST_ONLY_REORDERED_ACTIONS, seed=1, out_dir=api_out)

    cli_config = yaml.safe_load((cli_out / "config.yaml").read_text())
    api_config = yaml.safe_load((api_out / "config.yaml").read_text())
    cli_manifest = yaml.safe_load((cli_out / "manifest.yaml").read_text())
    api_manifest = yaml.safe_load((api_out / "manifest.yaml").read_text())
    actions = tuple(api_config["model"]["actions"])
    expected_outputs = {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    expected_metrics_fields = list(metrics_fieldnames(actions))
    expected_role_action_fields = list(role_action_metric_fields(actions))

    for out_dir in [cli_out, api_out]:
        _assert_artifacts_match_output_directory(out_dir, artifacts)
        assert not (out_dir / "metrics.csv").exists()
        assert not (out_dir / "events.csv").exists()
        assert not (out_dir / "summary.md").exists()

    assert artifacts == MANIFEST_ONLY_ARTIFACTS
    assert actions == ("work_task", "create_task", "message", "idle")
    assert cli_config == api_config
    assert cli_manifest == api_manifest
    assert api_config["outputs"] == expected_outputs
    assert api_manifest["outputs"] == expected_outputs
    assert api_manifest["artifacts"] == artifacts
    assert api_manifest["actions"] == list(actions)
    assert api_manifest["config"] == api_config
    assert api_manifest["model"]["metrics"]["fields"] == expected_metrics_fields
    assert api_manifest["model"]["role_action_metrics"]["actions"] == list(actions)
    assert api_manifest["model"]["role_action_metrics"]["fields"] == expected_role_action_fields
    assert result.seed == 1
    assert result.config.to_dict() == api_config
    _assert_artifacts_are_byte_identical(cli_out, api_out, artifacts)


def test_documented_cli_omitted_outputs_refuses_collision_without_partial_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "default_outputs_collision"
    out_dir.mkdir()
    sentinels = {
        "config.yaml": "sentinel config\n",
        "events.csv": "sentinel events\n",
    }
    for artifact, content in sentinels.items():
        (out_dir / artifact).write_text(content)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(DEFAULT_OUTPUTS),
            "--seed",
            "17",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "already contains run artifacts" in completed.stderr
    assert "config.yaml" in completed.stderr
    assert "events.csv" in completed.stderr
    assert "Traceback" not in completed.stderr
    _assert_artifacts_match_output_directory(out_dir, list(sentinels))
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_run_api_omitted_outputs_defaults_to_full_a0_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "default_outputs_api_seed1"
    expected_artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    result = run_experiment(DEFAULT_OUTPUTS, seed=1, out_dir=out_dir)

    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)
    assert result.config.outputs.write_manifest is True
    assert result.config.outputs.write_metrics is True
    assert result.config.outputs.write_events is True
    assert result.config.outputs.write_summary is True
    assert len(result.metrics) == 3
    assert len(result.events) == 45

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert normalized_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert manifest["outputs"] == normalized_config["outputs"]
    assert manifest["artifacts"] == expected_artifacts
    assert manifest["experiment_id"] == "a0_default_outputs"
    with (out_dir / "metrics.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 3
    with (out_dir / "events.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 45
    assert "# a0_default_outputs" in (out_dir / "summary.md").read_text()


def test_run_api_omitted_outputs_same_seed_reproduces_byte_identical_artifacts(
    tmp_path: Path,
) -> None:
    first, second, first_result, second_result = _run_api_pair(
        DEFAULT_OUTPUTS,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name="default_outputs_api_seed17_first",
        second_name="default_outputs_api_seed17_second",
    )
    artifacts = _expected_artifacts(DEFAULT_OUTPUTS)

    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == second_result.seed == 17
    assert first_result.metrics == second_result.metrics
    assert first_result.events == second_result.events
    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_run_api_omitted_outputs_refuses_collision_without_partial_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "default_outputs_api_collision"
    out_dir.mkdir()
    sentinels = {
        "config.yaml": "sentinel config\n",
        "events.csv": "sentinel events\n",
    }
    for artifact, content in sentinels.items():
        (out_dir / artifact).write_text(content)

    with pytest.raises(FileExistsError, match="already contains run artifacts") as exc_info:
        run_experiment(DEFAULT_OUTPUTS, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert str(out_dir) in message
    assert "config.yaml" in message
    assert "events.csv" in message
    _assert_artifacts_match_output_directory(out_dir, list(sentinels))
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_documented_cli_smoke_writes_expected_metrics_and_events_rows(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    _run_documented_cli(CONFIG, out_dir)

    config = load_config(CONFIG)
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    assert len(metric_rows) == config.run.ticks
    assert len(event_rows) == config.run.ticks * config.model.agent_count
    assert [int(row["tick"]) for row in metric_rows] == list(range(config.run.ticks))

    events_by_tick = Counter(int(row["tick"]) for row in event_rows)
    assert events_by_tick == {
        tick: config.model.agent_count
        for tick in range(config.run.ticks)
    }


def test_documented_cli_smoke_writes_core_a0_summary_sections(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed1"

    _run_documented_cli(CONFIG, out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))
    summary = (out_dir / "summary.md").read_text()

    for heading in [
        "## Artifact schema provenance",
        "## Event type totals",
        "## Baseline lobe totals",
        "## Baseline lobe transitions",
        "## Baseline lobe dwell runs",
        "## Role action totals",
    ]:
        assert heading in summary

    event_type_totals = Counter(row["event_type"] for row in event_rows)
    lobe_totals = Counter(row["baseline_lobe_label"] for row in metric_rows)
    lobe_transitions = Counter(
        row["baseline_lobe_transition"]
        for row in metric_rows
        if row["baseline_lobe_transition"] not in {"start", "stable"}
    )
    role_action_totals = {
        role: {
            action: sum(int(row[f"role_{role}_{action}_tick"]) for row in metric_rows)
            for action in ("idle", "message", "create_task", "work_task")
        }
        for role in BASELINE_ROLES
    }

    assert event_type_totals
    assert lobe_totals
    assert lobe_transitions
    for event_type, count in sorted(event_type_totals.items()):
        assert f"- {event_type}: {count}" in summary
    for label, count in sorted(lobe_totals.items()):
        assert f"- {label}: {count}" in summary
    for transition, count in sorted(lobe_transitions.items()):
        assert f"- {transition}: {count}" in summary
    for label, dwell in _lobe_dwell_runs(metric_rows).items():
        assert (
            f"- {label}: runs={dwell['runs']}, total_ticks={dwell['total_ticks']}, "
            f"max_run={dwell['max_run']}, mean_run={dwell['mean_run']}"
        ) in summary
    for role, totals in role_action_totals.items():
        assert (
            f"- {role}: idle={totals['idle']}, message={totals['message']}, "
            f"create_task={totals['create_task']}, work_task={totals['work_task']}"
        ) in summary


def test_documented_cli_same_seed_reproduces_byte_identical_a0_artifacts(tmp_path: Path) -> None:
    artifacts = _expected_artifacts(CONFIG)
    first, second, _, _ = _run_documented_cli_pair(
        CONFIG,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name="a0_seed17_first",
        second_name="a0_seed17_second",
    )

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_documented_cli_refuses_to_overwrite_complete_run_directory(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed17"
    artifacts = _expected_artifacts(CONFIG)
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(CONFIG),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = _artifact_bytes_snapshot(out_dir, artifacts)

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert "already contains run artifacts" in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(out_dir, artifacts)
    _assert_output_directory_preserved(out_dir, before)


def test_documented_cli_respects_disabled_optional_outputs(tmp_path: Path) -> None:
    out_dir = tmp_path / "manifest_only_cli_outputs"
    expected_artifacts = _expected_artifacts(MANIFEST_ONLY)

    _run_documented_cli(MANIFEST_ONLY, out_dir, seed=17)
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == expected_artifacts
    assert manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["seed"] == 17
    assert manifest["experiment_id"] == "a0_manifest_only"
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_documented_cli_respects_disabled_manifest_output(tmp_path: Path) -> None:
    out_dir = tmp_path / "no_manifest_cli_outputs"

    _run_documented_cli(NO_MANIFEST, out_dir, seed=17)
    _assert_no_manifest_writes_enabled_artifacts(out_dir)
    assert "# a0_no_manifest" in (out_dir / "summary.md").read_text()


def test_run_api_respects_no_manifest_fixture_outputs(tmp_path: Path) -> None:
    out_dir = tmp_path / "no_manifest_api_outputs"
    out_dir.mkdir()
    stale_manifest = "stale manifest sentinel\n"
    (out_dir / "manifest.yaml").write_text(stale_manifest)
    expected_artifacts = [*_expected_artifacts(NO_MANIFEST), "manifest.yaml"]

    result = run_experiment(NO_MANIFEST, seed=17, out_dir=out_dir)

    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)
    assert (out_dir / "manifest.yaml").read_text() == stale_manifest
    assert result.config.outputs.write_manifest is False
    assert len(result.metrics) == 3
    assert len(result.events) == 45
    _assert_no_manifest_writes_enabled_artifacts(
        out_dir,
        stale_manifest=stale_manifest.encode(),
    )
    assert "# a0_no_manifest" in (out_dir / "summary.md").read_text()


def test_run_api_without_manifest_refuses_enabled_artifact_collisions(tmp_path: Path) -> None:
    out_dir = tmp_path / "no_manifest_api_collision"
    out_dir.mkdir()
    sentinels = {
        "manifest.yaml": "ignored stale manifest\n",
        "metrics.csv": "sentinel metrics\n",
        "summary.md": "sentinel summary\n",
    }
    for artifact, content in sentinels.items():
        (out_dir / artifact).write_text(content)

    with pytest.raises(FileExistsError, match="already contains run artifacts") as exc_info:
        run_experiment(NO_MANIFEST, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert str(out_dir) in message
    assert "metrics.csv" in message
    assert "summary.md" in message
    assert "manifest.yaml" not in message
    _assert_artifacts_match_output_directory(out_dir, list(sentinels))
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "config.yaml").exists()
    assert not (out_dir / "events.csv").exists()


def test_documented_cli_same_seed_without_manifest_reproduces_byte_identical_artifacts(
    tmp_path: Path,
) -> None:
    artifacts = _expected_artifacts(NO_MANIFEST)
    first, second, _, _ = _run_documented_cli_pair(
        NO_MANIFEST,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name="no_manifest_repro_first",
        second_name="no_manifest_repro_second",
    )

    for out_dir in [first, second]:
        assert not (out_dir / "manifest.yaml").exists()

    _assert_artifacts_are_byte_identical(first, second, artifacts)


def test_documented_cli_without_manifest_refuses_partial_output_directory(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_partial_collision"
    out_dir.mkdir()
    sentinels = {
        "config.yaml": "sentinel config\n",
        "events.csv": "sentinel events\n",
    }
    for artifact, content in sentinels.items():
        (out_dir / artifact).write_text(content)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(NO_MANIFEST),
            "--seed",
            "17",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "already contains run artifacts" in completed.stderr
    assert "config.yaml" in completed.stderr
    assert "events.csv" in completed.stderr
    assert "manifest.yaml" not in completed.stderr
    assert "Traceback" not in completed.stderr
    _assert_artifacts_match_output_directory(out_dir, list(sentinels))
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "summary.md").exists()
    assert not (out_dir / "manifest.yaml").exists()


def test_documented_cli_different_seeds_change_events_but_preserve_schema(tmp_path: Path) -> None:
    first = tmp_path / "a0_seed17"
    second = tmp_path / "a0_seed18"

    for seed, out_dir in [(17, first), (18, second)]:
        _run_documented_cli(CONFIG, out_dir, seed=seed)

    with (first / "metrics.csv").open() as handle:
        first_metrics = list(csv.reader(handle))
    with (second / "metrics.csv").open() as handle:
        second_metrics = list(csv.reader(handle))
    with (first / "events.csv").open() as handle:
        first_events = list(csv.reader(handle))
    with (second / "events.csv").open() as handle:
        second_events = list(csv.reader(handle))

    assert first_metrics[0] == second_metrics[0]
    assert first_events[0] == second_events[0]
    assert len(first_metrics) == len(second_metrics) == 101
    assert len(first_events) == len(second_events) == 1501
    assert first_events[1:] != second_events[1:]

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())
    assert first_manifest["seed"] == 17
    assert second_manifest["seed"] == 18
    assert first_manifest["actions"] == second_manifest["actions"]
    assert first_manifest["model"] == second_manifest["model"]


def test_cli_validation_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid_actions.yaml"
    out_dir = tmp_path / "invalid_run"
    config_path.write_text(
        """
run:
  experiment_id: invalid_actions
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task
    - browse_web
"""
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error: model.actions contains unsupported baseline actions: browse_web" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert not out_dir.exists()


def test_cli_invalid_seed_error_does_not_write_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "invalid_seed_run"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(CONFIG),
            "--seed",
            "-1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error: seed must be a non-negative integer." in completed.stderr
    assert "Traceback" not in completed.stderr
    assert not out_dir.exists()


@pytest.mark.parametrize("seed", [-1, True, "1"])
def test_run_experiment_invalid_seed_error_does_not_write_artifacts(
    tmp_path: Path,
    seed: object,
) -> None:
    out_dir = tmp_path / "invalid_seed_run"

    with pytest.raises(ValueError, match="seed must be a non-negative integer"):
        run_experiment(tmp_path / "missing_config.yaml", seed=seed, out_dir=out_dir)  # type: ignore[arg-type]

    assert not out_dir.exists()


def test_run_experiment_missing_config_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "missing.yaml"
    out_dir = tmp_path / "missing_config_run"

    with pytest.raises(FileNotFoundError, match="missing.yaml"):
        run_experiment(config_path, seed=1, out_dir=out_dir)

    assert not out_dir.exists()


def test_run_experiment_malformed_yaml_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "malformed.yaml"
    out_dir = tmp_path / "malformed_run"
    config_path.write_text(
        """
run:
  experiment_id: malformed
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task
    - [unterminated
"""
    )

    with pytest.raises(ValueError, match="invalid YAML"):
        run_experiment(config_path, seed=1, out_dir=out_dir)

    assert not out_dir.exists()


def test_run_experiment_invalid_config_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid_actions.yaml"
    out_dir = tmp_path / "invalid_run"
    config_path.write_text(
        """
run:
  experiment_id: invalid_actions
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task
    - browse_web
"""
    )

    with pytest.raises(ValueError, match="unsupported baseline actions: browse_web"):
        run_experiment(config_path, seed=1, out_dir=out_dir)

    assert not out_dir.exists()


def test_run_experiment_refuses_to_overwrite_complete_run_directory(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0_seed17"
    artifacts = [
        "config.yaml",
        "manifest.yaml",
        "metrics.csv",
        "events.csv",
        "summary.md",
    ]

    run_experiment(CONFIG, seed=17, out_dir=out_dir)
    before = _artifact_bytes_snapshot(out_dir, artifacts)

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        run_experiment(CONFIG, seed=17, out_dir=out_dir)

    _assert_artifacts_match_output_directory(out_dir, artifacts)
    _assert_output_directory_preserved(out_dir, before)


def test_run_experiment_refuses_partial_output_directory_without_writing_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "partial_collision"
    out_dir.mkdir()
    sentinels = {
        "config.yaml": "sentinel config\n",
        "events.csv": "sentinel events\n",
    }
    for artifact, content in sentinels.items():
        (out_dir / artifact).write_text(content)

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        run_experiment(CONFIG, seed=17, out_dir=out_dir)

    _assert_artifacts_match_output_directory(out_dir, list(sentinels))
    for artifact, content in sentinels.items():
        assert (out_dir / artifact).read_text() == content
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_run_experiment_output_path_file_does_not_overwrite(tmp_path: Path) -> None:
    out_path = tmp_path / "file_output"
    out_path.write_text("sentinel output path\n")

    with pytest.raises(FileExistsError, match="exists and is not a directory"):
        run_experiment(CONFIG, seed=17, out_dir=out_path)

    assert out_path.read_text() == "sentinel output path\n"


def test_run_experiment_output_artifact_collision_does_not_write_partial_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "collision_run"
    out_dir.mkdir()
    existing_metrics = out_dir / "metrics.csv"
    existing_metrics.write_text("sentinel metrics\n")

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        run_experiment(CONFIG, seed=1, out_dir=out_dir)

    assert existing_metrics.read_text() == "sentinel metrics\n"
    _assert_artifacts_match_output_directory(out_dir, ["metrics.csv"])
    assert not (out_dir / "config.yaml").exists()
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_run_experiment_ignores_disabled_output_collisions_but_blocks_enabled_artifacts(
    tmp_path: Path,
) -> None:
    success_dir = tmp_path / "disabled_optional_collisions_success"
    blocked_dir = tmp_path / "disabled_optional_collisions_blocked"
    disabled_sentinels = {
        "metrics.csv": "sentinel disabled metrics\n",
        "events.csv": "sentinel disabled events\n",
        "summary.md": "sentinel disabled summary\n",
    }
    success_dir.mkdir()
    for artifact, content in disabled_sentinels.items():
        (success_dir / artifact).write_text(content)

    run_experiment(MANIFEST_ONLY, seed=17, out_dir=success_dir)

    assert (success_dir / "config.yaml").is_file()
    assert (success_dir / "manifest.yaml").is_file()
    for artifact, content in disabled_sentinels.items():
        assert (success_dir / artifact).read_text() == content
    manifest = yaml.safe_load((success_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)

    blocked_dir.mkdir()
    for artifact, content in disabled_sentinels.items():
        (blocked_dir / artifact).write_text(content)
    (blocked_dir / "manifest.yaml").write_text("sentinel enabled manifest\n")

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        run_experiment(MANIFEST_ONLY, seed=17, out_dir=blocked_dir)

    assert (blocked_dir / "manifest.yaml").read_text() == "sentinel enabled manifest\n"
    _assert_artifacts_match_output_directory(blocked_dir, [*disabled_sentinels, "manifest.yaml"])
    assert not (blocked_dir / "config.yaml").exists()
    for artifact, content in disabled_sentinels.items():
        assert (blocked_dir / artifact).read_text() == content


def test_run_experiment_config_artifact_collision_blocks_when_all_optional_outputs_disabled(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_collision"
    stale_disabled_artifacts, collision_content = _write_config_only_collision_sentinels(out_dir)

    with pytest.raises(FileExistsError, match="already contains run artifacts: config.yaml"):
        run_experiment(CONFIG_ONLY, seed=17, out_dir=out_dir)

    _assert_config_only_collision_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
        collision_content=collision_content,
    )


def test_run_experiment_config_only_outputs_succeed_and_are_byte_stable(
    tmp_path: Path,
) -> None:
    first = tmp_path / "config_only_first"
    second = tmp_path / "config_only_second"

    first_result = run_experiment(CONFIG_ONLY, seed=17, out_dir=first)
    second_result = run_experiment(CONFIG_ONLY, seed=17, out_dir=second)

    artifacts = _expected_artifacts(CONFIG_ONLY)
    _assert_artifacts_match_output_directory(first, artifacts)
    _assert_artifacts_match_output_directory(second, artifacts)
    _assert_artifacts_are_byte_identical(first, second, artifacts)
    normalized_config = yaml.safe_load((first / "config.yaml").read_text())
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"
    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == second_result.seed == 17
    assert len(first_result.metrics) == len(second_result.metrics) == 3
    assert len(first_result.events) == len(second_result.events) == 45


def test_config_only_reordered_actions_writes_only_normalized_config_with_yaml_action_order(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions"

    result = run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    actions = _actions_from_normalized_config(normalized_config)

    _assert_artifacts_match_output_directory(
        out_dir,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )
    assert actions == ["work_task", "create_task", "message", "idle"]
    assert result.config.model.actions == tuple(actions)
    assert normalized_config["run"]["experiment_id"] == "a0_config_only_reordered_actions"
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_run_experiment_config_only_reordered_actions_outputs_are_byte_stable(
    tmp_path: Path,
) -> None:
    first = tmp_path / "config_only_reordered_actions_first"
    second = tmp_path / "config_only_reordered_actions_second"

    first_result = run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=first)
    second_result = run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=second)

    artifacts = _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS)
    _assert_artifacts_match_output_directory(first, artifacts)
    _assert_artifacts_match_output_directory(second, artifacts)
    _assert_artifacts_are_byte_identical(first, second, artifacts)
    _assert_config_only_writes_normalized_config(
        first,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )
    assert first_result.config.to_dict() == second_result.config.to_dict()
    assert first_result.seed == second_result.seed == 17
    assert len(first_result.metrics) == len(second_result.metrics) == 3
    assert len(first_result.events) == len(second_result.events) == 45


def test_run_experiment_config_only_reordered_actions_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions_api_stale_disabled"
    stale_disabled_artifacts = _write_config_only_disabled_artifact_sentinels(out_dir)

    result = run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)

    _assert_config_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )
    _assert_config_only_writes_normalized_config(
        out_dir,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )
    assert result.config.model.actions == ("work_task", "create_task", "message", "idle")
    assert result.seed == 17
    assert len(result.metrics) == 3
    assert len(result.events) == 45


def test_run_experiment_config_only_rerun_refuses_to_overwrite_existing_config(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_rerun"

    run_experiment(CONFIG_ONLY, seed=17, out_dir=out_dir)
    before = _artifact_bytes_snapshot(out_dir, _expected_artifacts(CONFIG_ONLY))

    with pytest.raises(FileExistsError, match="already contains run artifacts: config.yaml"):
        run_experiment(CONFIG_ONLY, seed=17, out_dir=out_dir)

    _assert_artifacts_match_output_directory(out_dir, _expected_artifacts(CONFIG_ONLY))
    _assert_output_directory_preserved(out_dir, before)
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_run_experiment_config_only_reordered_actions_rerun_refuses_to_overwrite_existing_config(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions_rerun"

    run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)
    before = _artifact_bytes_snapshot(
        out_dir,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )

    with pytest.raises(FileExistsError) as exc_info:
        run_experiment(CONFIG_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert "already contains run artifacts: config.yaml" in message
    assert "manifest.yaml" not in message
    assert "metrics.csv" not in message
    assert "events.csv" not in message
    assert "summary.md" not in message
    _assert_artifacts_match_output_directory(
        out_dir,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )
    _assert_output_directory_preserved(out_dir, before)
    _assert_config_only_writes_normalized_config(
        out_dir,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )


def test_run_experiment_config_only_rerun_preserves_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_rerun_with_disabled_sentinels"
    disabled_sentinels = {
        "manifest.yaml": b"sentinel disabled manifest\n",
        "metrics.csv": b"sentinel disabled metrics\n",
        "events.csv": b"sentinel disabled events\n",
        "summary.md": b"sentinel disabled summary\n",
    }

    run_experiment(CONFIG_ONLY, seed=17, out_dir=out_dir)
    for artifact, content in disabled_sentinels.items():
        (out_dir / artifact).write_bytes(content)
    before = _artifact_bytes_snapshot(out_dir)

    with pytest.raises(FileExistsError) as exc_info:
        run_experiment(CONFIG_ONLY, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert "already contains run artifacts: config.yaml" in message
    assert "manifest.yaml" not in message
    assert "metrics.csv" not in message
    assert "events.csv" not in message
    assert "summary.md" not in message
    _assert_artifacts_match_output_directory(
        out_dir,
        [*_expected_artifacts(CONFIG_ONLY), *disabled_sentinels],
    )
    _assert_output_directory_preserved(out_dir, before)
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_cli_malformed_yaml_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "malformed.yaml"
    out_dir = tmp_path / "malformed_run"
    config_path.write_text(
        """
run:
  experiment_id: malformed
  ticks: 3

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task
    - [unterminated
"""
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(config_path) in completed.stderr
    assert "expected ',' or ']'" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert not out_dir.exists()


def test_cli_missing_config_error_does_not_write_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "missing.yaml"
    out_dir = tmp_path / "missing_config_run"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(config_path),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(config_path) in completed.stderr
    assert "No such file or directory" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert not out_dir.exists()


def test_cli_output_artifact_collision_does_not_write_partial_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "collision_run"
    out_dir.mkdir()
    existing_metrics = out_dir / "metrics.csv"
    existing_metrics.write_text("sentinel metrics\n")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(CONFIG),
            "--seed",
            "1",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "metrics.csv" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert existing_metrics.read_text() == "sentinel metrics\n"
    assert not (out_dir / "config.yaml").exists()
    assert not (out_dir / "manifest.yaml").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()


def test_cli_ignores_disabled_output_collisions_but_blocks_enabled_artifacts(
    tmp_path: Path,
) -> None:
    success_dir = tmp_path / "disabled_optional_cli_collisions_success"
    blocked_dir = tmp_path / "disabled_optional_cli_collisions_blocked"
    disabled_sentinels = {
        "metrics.csv": "sentinel disabled metrics\n",
        "events.csv": "sentinel disabled events\n",
        "summary.md": "sentinel disabled summary\n",
    }
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(MANIFEST_ONLY),
        "--seed",
        "17",
    ]
    success_dir.mkdir()
    for artifact, content in disabled_sentinels.items():
        (success_dir / artifact).write_text(content)

    success = subprocess.run(
        [*command, "--out", str(success_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert success.returncode == 0
    assert success.stderr == ""
    assert (success_dir / "config.yaml").is_file()
    assert (success_dir / "manifest.yaml").is_file()
    for artifact, content in disabled_sentinels.items():
        assert (success_dir / artifact).read_text() == content
    manifest = yaml.safe_load((success_dir / "manifest.yaml").read_text())
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY)

    blocked_dir.mkdir()
    for artifact, content in disabled_sentinels.items():
        (blocked_dir / artifact).write_text(content)
    (blocked_dir / "manifest.yaml").write_text("sentinel enabled manifest\n")

    blocked = subprocess.run(
        [*command, "--out", str(blocked_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert blocked.returncode != 0
    assert "error:" in blocked.stderr
    assert str(blocked_dir) in blocked.stderr
    assert "manifest.yaml" in blocked.stderr
    assert "metrics.csv" not in blocked.stderr
    assert "events.csv" not in blocked.stderr
    assert "summary.md" not in blocked.stderr
    assert "Traceback" not in blocked.stderr
    assert (blocked_dir / "manifest.yaml").read_text() == "sentinel enabled manifest\n"
    _assert_artifacts_match_output_directory(blocked_dir, [*disabled_sentinels, "manifest.yaml"])
    assert not (blocked_dir / "config.yaml").exists()
    for artifact, content in disabled_sentinels.items():
        assert (blocked_dir / artifact).read_text() == content


def test_cli_config_artifact_collision_blocks_when_all_optional_outputs_disabled(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_cli_collision"
    stale_disabled_artifacts, collision_content = _write_config_only_collision_sentinels(out_dir)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(CONFIG_ONLY),
            "--seed",
            "17",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_dir) in completed.stderr
    assert "config.yaml" in completed.stderr
    assert "manifest.yaml" not in completed.stderr
    assert "metrics.csv" not in completed.stderr
    assert "events.csv" not in completed.stderr
    assert "summary.md" not in completed.stderr
    assert "Traceback" not in completed.stderr
    _assert_config_only_collision_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
        collision_content=collision_content,
    )


def test_cli_config_only_outputs_succeed_and_are_byte_stable(tmp_path: Path) -> None:
    first = tmp_path / "config_only_cli_first"
    second = tmp_path / "config_only_cli_second"

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG_ONLY, out_dir, seed=17)
        _assert_artifacts_match_output_directory(out_dir, _expected_artifacts(CONFIG_ONLY))

    _assert_artifacts_are_byte_identical(first, second, _expected_artifacts(CONFIG_ONLY))
    normalized_config = yaml.safe_load((first / "config.yaml").read_text())
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"


def test_cli_config_only_reordered_actions_outputs_succeed_and_are_byte_stable(
    tmp_path: Path,
) -> None:
    first = tmp_path / "config_only_reordered_actions_cli_first"
    second = tmp_path / "config_only_reordered_actions_cli_second"

    for out_dir in [first, second]:
        _run_documented_cli(CONFIG_ONLY_REORDERED_ACTIONS, out_dir, seed=17)
        _assert_artifacts_match_output_directory(
            out_dir,
            _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
        )

    _assert_artifacts_are_byte_identical(
        first,
        second,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )
    normalized_config = yaml.safe_load((first / "config.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_config_only_reordered_actions"
    assert _actions_from_normalized_config(normalized_config) == [
        "work_task",
        "create_task",
        "message",
        "idle",
    ]
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_cli_config_only_reordered_actions_preserves_stale_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions_cli_stale_disabled"
    stale_disabled_artifacts = _write_config_only_disabled_artifact_sentinels(out_dir)

    _run_documented_cli(CONFIG_ONLY_REORDERED_ACTIONS, out_dir, seed=17)

    _assert_config_only_preserves_stale_disabled_artifacts(
        out_dir,
        stale_disabled_artifacts=stale_disabled_artifacts,
    )
    _assert_config_only_writes_normalized_config(
        out_dir,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )


def test_cli_config_only_reordered_actions_rerun_preserves_disabled_artifact_sentinels(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions_cli_rerun_with_disabled_sentinels"
    disabled_sentinels = {
        "manifest.yaml": b"sentinel disabled manifest\n",
        "metrics.csv": b"sentinel disabled metrics\n",
        "events.csv": b"sentinel disabled events\n",
        "summary.md": b"sentinel disabled summary\n",
    }
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(CONFIG_ONLY_REORDERED_ACTIONS),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    for artifact, content in disabled_sentinels.items():
        (out_dir / artifact).write_bytes(content)
    before = _artifact_bytes_snapshot(out_dir)

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert str(out_dir) in second.stderr
    assert "already contains run artifacts: config.yaml" in second.stderr
    assert "manifest.yaml" not in second.stderr
    assert "metrics.csv" not in second.stderr
    assert "events.csv" not in second.stderr
    assert "summary.md" not in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(
        out_dir,
        [*_expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS), *disabled_sentinels],
    )
    _assert_output_directory_preserved(out_dir, before)
    _assert_config_only_writes_normalized_config(
        out_dir,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )


def test_cli_config_only_reordered_actions_rerun_refuses_to_overwrite_existing_config(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "config_only_reordered_actions_cli_rerun"
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(CONFIG_ONLY_REORDERED_ACTIONS),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = _artifact_bytes_snapshot(
        out_dir,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert str(out_dir) in second.stderr
    assert "already contains run artifacts: config.yaml" in second.stderr
    assert "manifest.yaml" not in second.stderr
    assert "metrics.csv" not in second.stderr
    assert "events.csv" not in second.stderr
    assert "summary.md" not in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(
        out_dir,
        _expected_artifacts(CONFIG_ONLY_REORDERED_ACTIONS),
    )
    _assert_output_directory_preserved(out_dir, before)
    _assert_config_only_writes_normalized_config(
        out_dir,
        experiment_id="a0_config_only_reordered_actions",
        actions=["work_task", "create_task", "message", "idle"],
    )


def test_cli_manifest_only_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_reordered_actions_cli_rerun"
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(MANIFEST_ONLY_REORDERED_ACTIONS),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = _artifact_bytes_snapshot(
        out_dir,
        _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS),
    )

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert str(out_dir) in second.stderr
    assert "already contains run artifacts: config.yaml, manifest.yaml" in second.stderr
    assert "metrics.csv" not in second.stderr
    assert "events.csv" not in second.stderr
    assert "summary.md" not in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(
        out_dir,
        _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS),
    )
    _assert_output_directory_preserved(out_dir, before)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_manifest_only_reordered_actions"
    assert _actions_from_normalized_config(normalized_config) == [
        "work_task",
        "create_task",
        "message",
        "idle",
    ]
    assert normalized_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["experiment_id"] == "a0_manifest_only_reordered_actions"
    assert manifest["actions"] == _actions_from_normalized_config(normalized_config)
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS)
    assert manifest["outputs"] == normalized_config["outputs"]


def test_run_api_manifest_only_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "manifest_only_reordered_actions_api_rerun"

    first = run_experiment(MANIFEST_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)
    before = _artifact_bytes_snapshot(
        out_dir,
        _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS),
    )

    with pytest.raises(FileExistsError, match="already contains run artifacts") as exc_info:
        run_experiment(MANIFEST_ONLY_REORDERED_ACTIONS, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert first.config.run.experiment_id == "a0_manifest_only_reordered_actions"
    assert first.seed == 17
    assert str(out_dir) in message
    assert "config.yaml, manifest.yaml" in message
    assert "metrics.csv" not in message
    assert "events.csv" not in message
    assert "summary.md" not in message
    _assert_artifacts_match_output_directory(
        out_dir,
        _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS),
    )
    _assert_output_directory_preserved(out_dir, before)

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    actions = _actions_from_normalized_config(normalized_config)

    assert actions == ["work_task", "create_task", "message", "idle"]
    assert normalized_config["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["experiment_id"] == "a0_manifest_only_reordered_actions"
    assert manifest["actions"] == actions
    assert manifest["artifacts"] == _expected_artifacts(MANIFEST_ONLY_REORDERED_ACTIONS)
    assert manifest["outputs"] == normalized_config["outputs"]


def test_cli_no_manifest_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts_and_preserves_stale_manifest(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_reordered_actions_cli_rerun"
    stale_manifest = _write_no_manifest_disabled_manifest_sentinel(out_dir)
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(NO_MANIFEST_REORDERED_ACTIONS),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = _artifact_bytes_snapshot(
        out_dir,
        [*_expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS), "manifest.yaml"],
    )

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert str(out_dir) in second.stderr
    assert (
        "already contains run artifacts: config.yaml, metrics.csv, events.csv, summary.md"
        in second.stderr
    )
    assert "manifest.yaml" not in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(
        out_dir,
        [*_expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS), "manifest.yaml"],
    )
    _assert_output_directory_preserved(out_dir, before)
    _assert_no_manifest_preserves_stale_disabled_manifest(
        out_dir,
        stale_manifest=stale_manifest,
    )

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    actions = _actions_from_normalized_config(normalized_config)

    assert normalized_config["run"]["experiment_id"] == "a0_no_manifest_reordered_actions"
    assert actions == ["work_task", "create_task", "message", "idle"]
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert _summary_written_artifacts(summary) == _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)
    assert "manifest.yaml" not in _summary_written_artifacts(summary)
    assert f"role_{BASELINE_ROLES[0]}_work_task_tick" in (out_dir / "metrics.csv").read_text()


def test_run_api_no_manifest_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts_and_preserves_stale_manifest(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "no_manifest_reordered_actions_api_rerun"
    stale_manifest = _write_no_manifest_disabled_manifest_sentinel(out_dir)

    first = run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=out_dir)
    before = _artifact_bytes_snapshot(
        out_dir,
        [*_expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS), "manifest.yaml"],
    )

    with pytest.raises(FileExistsError) as exc_info:
        run_experiment(NO_MANIFEST_REORDERED_ACTIONS, seed=17, out_dir=out_dir)

    message = str(exc_info.value)
    assert first.config.run.experiment_id == "a0_no_manifest_reordered_actions"
    assert first.seed == 17
    assert str(out_dir) in message
    assert "already contains run artifacts: config.yaml, metrics.csv, events.csv, summary.md" in message
    assert "manifest.yaml" not in message
    _assert_artifacts_match_output_directory(
        out_dir,
        [*_expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS), "manifest.yaml"],
    )
    _assert_output_directory_preserved(out_dir, before)
    _assert_no_manifest_preserves_stale_disabled_manifest(
        out_dir,
        stale_manifest=stale_manifest,
    )

    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    actions = _actions_from_normalized_config(normalized_config)

    assert actions == ["work_task", "create_task", "message", "idle"]
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    assert _summary_written_artifacts(summary) == _expected_artifacts(NO_MANIFEST_REORDERED_ACTIONS)
    assert "manifest.yaml" not in _summary_written_artifacts(summary)
    assert f"role_{BASELINE_ROLES[0]}_work_task_tick" in (out_dir / "metrics.csv").read_text()


def test_cli_config_only_rerun_refuses_to_overwrite_existing_config(tmp_path: Path) -> None:
    out_dir = tmp_path / "config_only_cli_rerun"
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(CONFIG_ONLY),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    before = _artifact_bytes_snapshot(out_dir, _expected_artifacts(CONFIG_ONLY))

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert str(out_dir) in second.stderr
    assert "already contains run artifacts" in second.stderr
    assert "config.yaml" in second.stderr
    assert "manifest.yaml" not in second.stderr
    assert "metrics.csv" not in second.stderr
    assert "events.csv" not in second.stderr
    assert "summary.md" not in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(out_dir, _expected_artifacts(CONFIG_ONLY))
    _assert_output_directory_preserved(out_dir, before)
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_cli_config_only_rerun_preserves_disabled_artifact_sentinels(tmp_path: Path) -> None:
    out_dir = tmp_path / "config_only_cli_rerun_with_disabled_sentinels"
    disabled_sentinels = {
        "manifest.yaml": b"sentinel disabled manifest\n",
        "metrics.csv": b"sentinel disabled metrics\n",
        "events.csv": b"sentinel disabled events\n",
        "summary.md": b"sentinel disabled summary\n",
    }
    command = [
        sys.executable,
        "-m",
        "ohdyn.run",
        "--config",
        str(CONFIG_ONLY),
        "--seed",
        "17",
        "--out",
        str(out_dir),
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False)
    for artifact, content in disabled_sentinels.items():
        (out_dir / artifact).write_bytes(content)
    before = _artifact_bytes_snapshot(out_dir)

    second = subprocess.run(command, capture_output=True, text=True, check=False)

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode != 0
    assert "error:" in second.stderr
    assert str(out_dir) in second.stderr
    assert "already contains run artifacts: config.yaml" in second.stderr
    assert "manifest.yaml" not in second.stderr
    assert "metrics.csv" not in second.stderr
    assert "events.csv" not in second.stderr
    assert "summary.md" not in second.stderr
    assert "Traceback" not in second.stderr
    _assert_artifacts_match_output_directory(
        out_dir,
        [*_expected_artifacts(CONFIG_ONLY), *disabled_sentinels],
    )
    _assert_output_directory_preserved(out_dir, before)
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    assert normalized_config["run"]["experiment_id"] == "a0_config_only"
    assert normalized_config["outputs"] == {
        "write_manifest": False,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }


def test_cli_output_path_file_does_not_overwrite_or_traceback(tmp_path: Path) -> None:
    out_path = tmp_path / "file_output"
    out_path.write_text("sentinel output path\n")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.run",
            "--config",
            str(CONFIG),
            "--seed",
            "1",
            "--out",
            str(out_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "error:" in completed.stderr
    assert str(out_path) in completed.stderr
    assert "exists and is not a directory" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert out_path.read_text() == "sentinel output path\n"


def test_a0_baseline_requires_fifteen_agents(tmp_path: Path) -> None:
    config_path = tmp_path / "wrong_agent_count.yaml"
    config_path.write_text(
        """
run:
  experiment_id: wrong_agent_count
  ticks: 3

model:
  agent_count: 14
  actions:
    - idle
    - message
    - create_task
    - work_task
"""
    )

    with pytest.raises(ValueError, match="model.agent_count"):
        load_config(config_path)


def test_same_seed_reproduces_byte_stable_outputs(tmp_path: Path) -> None:
    first, second, _, _ = _run_api_pair(
        CONFIG,
        tmp_path,
        first_seed=17,
        second_seed=17,
        first_name="first",
        second_name="second",
    )

    _assert_artifacts_are_byte_identical(
        first,
        second,
        _expected_artifacts(CONFIG),
    )


def test_different_seed_changes_events(tmp_path: Path) -> None:
    first, second, _, _ = _run_api_pair(
        CONFIG,
        tmp_path,
        first_seed=1,
        second_seed=2,
        first_name="seed1",
        second_name="seed2",
    )

    assert (first / "events.csv").read_text() != (second / "events.csv").read_text()


def test_fixed_seed_lobe_and_transition_totals_are_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "lobes": {
                "backlog_growth": 44,
                "coordination": 25,
                "execution": 29,
                "low_activity": 2,
            },
            "transitions": {
                "backlog_growth->coordination": 10,
                "backlog_growth->execution": 11,
                "backlog_growth->low_activity": 2,
                "coordination->backlog_growth": 8,
                "coordination->execution": 9,
                "execution->backlog_growth": 15,
                "execution->coordination": 6,
                "low_activity->coordination": 1,
                "low_activity->execution": 1,
            },
        },
        2: {
            "lobes": {
                "backlog_growth": 49,
                "coordination": 16,
                "execution": 31,
                "low_activity": 4,
            },
            "transitions": {
                "backlog_growth->coordination": 8,
                "backlog_growth->execution": 18,
                "backlog_growth->low_activity": 1,
                "coordination->backlog_growth": 8,
                "coordination->execution": 5,
                "execution->backlog_growth": 18,
                "execution->coordination": 3,
                "execution->low_activity": 3,
                "low_activity->backlog_growth": 1,
                "low_activity->coordination": 2,
                "low_activity->execution": 1,
            },
        },
        17: {
            "lobes": {
                "backlog_growth": 52,
                "coordination": 24,
                "execution": 22,
                "low_activity": 2,
            },
            "transitions": {
                "backlog_growth->coordination": 14,
                "backlog_growth->execution": 9,
                "backlog_growth->low_activity": 2,
                "coordination->backlog_growth": 12,
                "coordination->execution": 6,
                "execution->backlog_growth": 11,
                "execution->coordination": 4,
                "low_activity->backlog_growth": 2,
            },
        },
    }

    observed = {}
    for seed in expected:
        result = run_experiment(CONFIG, seed=seed, out_dir=tmp_path / f"seed{seed}")
        lobe_totals = Counter(row["baseline_lobe_label"] for row in result.metrics)
        transition_totals = Counter(
            row["baseline_lobe_transition"]
            for row in result.metrics
            if row["baseline_lobe_transition"] not in {"start", "stable"}
        )
        observed[seed] = {
            "lobes": dict(sorted(lobe_totals.items())),
            "transitions": dict(sorted(transition_totals.items())),
        }

    assert observed == expected
    assert len({tuple(seed_totals["lobes"].items()) for seed_totals in observed.values()}) == len(expected)


def test_fixed_seed_lobe_dwell_runs_are_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "backlog_growth": {"runs": 24, "total_ticks": 44, "max_run": 6, "mean_run": 1.833333},
            "coordination": {"runs": 17, "total_ticks": 25, "max_run": 3, "mean_run": 1.470588},
            "execution": {"runs": 21, "total_ticks": 29, "max_run": 4, "mean_run": 1.380952},
            "low_activity": {"runs": 2, "total_ticks": 2, "max_run": 1, "mean_run": 1.0},
        },
        2: {
            "backlog_growth": {"runs": 28, "total_ticks": 49, "max_run": 5, "mean_run": 1.75},
            "coordination": {"runs": 13, "total_ticks": 16, "max_run": 3, "mean_run": 1.230769},
            "execution": {"runs": 24, "total_ticks": 31, "max_run": 3, "mean_run": 1.291667},
            "low_activity": {"runs": 4, "total_ticks": 4, "max_run": 1, "mean_run": 1.0},
        },
        17: {
            "backlog_growth": {"runs": 25, "total_ticks": 52, "max_run": 4, "mean_run": 2.08},
            "coordination": {"runs": 19, "total_ticks": 24, "max_run": 2, "mean_run": 1.263158},
            "execution": {"runs": 15, "total_ticks": 22, "max_run": 3, "mean_run": 1.466667},
            "low_activity": {"runs": 2, "total_ticks": 2, "max_run": 1, "mean_run": 1.0},
        },
    }

    observed = {}
    for seed in expected:
        out_dir = tmp_path / f"seed{seed}"
        result = run_experiment(CONFIG, seed=seed, out_dir=out_dir)
        summary = (out_dir / "summary.md").read_text()
        observed[seed] = _lobe_dwell_runs(result.metrics)

        for label, dwell in expected[seed].items():
            assert (
                f"- {label}: runs={dwell['runs']}, total_ticks={dwell['total_ticks']}, "
                f"max_run={dwell['max_run']}, mean_run={dwell['mean_run']}"
            ) in summary

    assert observed == expected


def test_fixed_seed_lobe_run_state_is_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "final_label": "backlog_growth",
            "final_run_id": 64,
            "final_run_length": 1,
        },
        2: {
            "final_label": "backlog_growth",
            "final_run_id": 69,
            "final_run_length": 3,
        },
        17: {
            "final_label": "coordination",
            "final_run_id": 61,
            "final_run_length": 1,
        },
    }

    observed = {}
    for seed in expected:
        result = run_experiment(CONFIG, seed=seed, out_dir=tmp_path / f"seed{seed}")
        final = result.metrics[-1]
        observed[seed] = {
            "final_label": final["baseline_lobe_label"],
            "final_run_id": final["baseline_lobe_run_id"],
            "final_run_length": final["baseline_lobe_current_run_length"],
        }

    assert observed == expected


def test_fixed_seed_queue_age_summaries_are_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "final_max_age": 47,
            "final_mean_age": 18.4,
            "peak_max_age": 47,
            "mean_mean_age": 8.038303,
        },
        2: {
            "final_max_age": 63,
            "final_mean_age": 25.142857,
            "peak_max_age": 64,
            "mean_mean_age": 13.034658,
        },
        17: {
            "final_max_age": 73,
            "final_mean_age": 29.914439,
            "peak_max_age": 73,
            "mean_mean_age": 15.881428,
        },
    }

    observed = {}
    for seed in expected:
        out_dir = tmp_path / f"seed{seed}"
        result = run_experiment(CONFIG, seed=seed, out_dir=out_dir)
        final_metrics = result.metrics[-1]
        summary = (out_dir / "summary.md").read_text()

        observed[seed] = {
            "final_max_age": final_metrics["queued_task_age_max_tick"],
            "final_mean_age": final_metrics["queued_task_age_mean_tick"],
            "peak_max_age": max(
                int(row["queued_task_age_max_tick"])
                for row in result.metrics
            ),
            "mean_mean_age": round(
                sum(float(row["queued_task_age_mean_tick"]) for row in result.metrics)
                / len(result.metrics),
                6,
            ),
        }

        assert f"- final queued task max age: {expected[seed]['final_max_age']}" in summary
        assert f"- final queued task mean age: {expected[seed]['final_mean_age']}" in summary
        assert f"- peak queued task max age: {expected[seed]['peak_max_age']}" in summary
        assert f"- mean queued task mean age: {expected[seed]['mean_mean_age']}" in summary

    assert observed == expected


def _lobe_dwell_runs(metrics: list[dict[str, object]]) -> dict[str, dict[str, int | float]]:
    runs_by_label: dict[str, list[int]] = {label: [] for label in BASELINE_LOBE_LABELS}
    previous_label = ""
    current_run_length = 0

    for row in metrics:
        label = str(row["baseline_lobe_label"])
        if label == previous_label:
            current_run_length += 1
        else:
            if previous_label:
                runs_by_label[previous_label].append(current_run_length)
            previous_label = label
            current_run_length = 1

    if previous_label:
        runs_by_label[previous_label].append(current_run_length)

    return {
        label: {
            "runs": len(runs),
            "total_ticks": sum(runs),
            "max_run": max(runs),
            "mean_run": round(sum(runs) / len(runs), 6),
        }
        for label, runs in runs_by_label.items()
        if runs
    }


def _assert_manifest_only_preserves_full_schema_provenance(
    out_dir: Path,
    config_path: Path,
) -> None:
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    actions = tuple(normalized_config["model"]["actions"])

    assert manifest["outputs"] == {
        "write_manifest": True,
        "write_metrics": False,
        "write_events": False,
        "write_summary": False,
    }
    assert manifest["artifacts"] == _expected_artifacts(config_path)
    assert not (out_dir / "metrics.csv").exists()
    assert not (out_dir / "events.csv").exists()
    assert not (out_dir / "summary.md").exists()
    assert manifest["model"]["baseline_lobes"] == {
        "labels": list(BASELINE_LOBE_LABELS),
        "transition_fields": list(BASELINE_LOBE_TRANSITION_FIELDS),
    }
    assert manifest["model"]["queue_dynamics_metrics"] == {
        "pressure_fields": list(QUEUE_PRESSURE_METRIC_FIELDS),
        "queued_task_age_fields": list(QUEUED_TASK_AGE_METRIC_FIELDS),
    }
    assert manifest["model"]["events"] == {
        "types": list(BASELINE_EVENT_TYPES),
        "fields": list(EVENT_FIELDS),
    }
    assert manifest["model"]["metrics"] == {
        "fields": list(metrics_fieldnames(actions)),
    }
    assert manifest["model"]["role_action_metrics"] == {
        "roles": list(BASELINE_ROLES),
        "actions": list(actions),
        "fields": list(role_action_metric_fields(actions)),
    }


def _write_manifest_only_disabled_artifact_sentinels(out_dir: Path) -> dict[str, bytes]:
    out_dir.mkdir()
    stale_disabled_artifacts = {
        "metrics.csv": b"stale disabled metrics sentinel\n",
        "events.csv": b"stale disabled events sentinel\n",
        "summary.md": b"stale disabled summary sentinel\n",
    }

    for artifact, content in stale_disabled_artifacts.items():
        (out_dir / artifact).write_bytes(content)

    return stale_disabled_artifacts


def _assert_manifest_only_preserves_stale_disabled_artifacts(
    out_dir: Path,
    *,
    stale_disabled_artifacts: dict[str, bytes],
) -> None:
    assert (out_dir / "config.yaml").is_file()
    assert (out_dir / "manifest.yaml").is_file()
    _assert_stale_artifacts_preserved(
        out_dir,
        stale_disabled_artifacts,
        expected_artifacts=[*_expected_artifacts(MANIFEST_ONLY), *stale_disabled_artifacts],
    )


def _write_manifest_only_collision_sentinels(
    out_dir: Path,
    collision_artifact: str,
) -> tuple[dict[str, bytes], bytes]:
    stale_disabled_artifacts = _write_manifest_only_disabled_artifact_sentinels(out_dir)
    collision_content = f"preexisting enabled {collision_artifact} sentinel\n".encode()

    (out_dir / collision_artifact).write_bytes(collision_content)

    return stale_disabled_artifacts, collision_content


def _assert_manifest_only_collision_preserves_stale_disabled_artifacts(
    out_dir: Path,
    collision_artifact: str,
    *,
    stale_disabled_artifacts: dict[str, bytes],
    collision_content: bytes,
) -> None:
    _assert_stale_artifacts_preserved(
        out_dir,
        {**stale_disabled_artifacts, collision_artifact: collision_content},
        expected_artifacts=[*stale_disabled_artifacts, collision_artifact],
    )


def _assert_config_only_writes_normalized_config(
    out_dir: Path,
    *,
    experiment_id: str = "a0_config_only",
    actions: list[str] | None = None,
) -> None:
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    expected_actions = actions or ["idle", "message", "create_task", "work_task"]

    assert normalized_config == {
        "run": {
            "experiment_id": experiment_id,
            "ticks": 3,
        },
        "model": {
            "agent_count": 15,
            "task_creation_pressure": 1.0,
            "work_service_capacity": 1.0,
            "actions": expected_actions,
        },
        "outputs": {
            "write_manifest": False,
            "write_metrics": False,
            "write_events": False,
            "write_summary": False,
        },
    }


def _write_config_only_disabled_artifact_sentinels(out_dir: Path) -> dict[str, bytes]:
    out_dir.mkdir()
    stale_disabled_artifacts = {
        "manifest.yaml": b"stale disabled manifest sentinel\n",
        "metrics.csv": b"stale disabled metrics sentinel\n",
        "events.csv": b"stale disabled events sentinel\n",
        "summary.md": b"stale disabled summary sentinel\n",
    }

    for artifact, content in stale_disabled_artifacts.items():
        (out_dir / artifact).write_bytes(content)

    return stale_disabled_artifacts


def _assert_config_only_preserves_stale_disabled_artifacts(
    out_dir: Path,
    *,
    stale_disabled_artifacts: dict[str, bytes],
) -> None:
    assert (out_dir / "config.yaml").is_file()
    _assert_stale_artifacts_preserved(
        out_dir,
        stale_disabled_artifacts,
        expected_artifacts=[*_expected_artifacts(CONFIG_ONLY), *stale_disabled_artifacts],
    )


def _write_config_only_collision_sentinels(out_dir: Path) -> tuple[dict[str, bytes], bytes]:
    stale_disabled_artifacts = _write_config_only_disabled_artifact_sentinels(out_dir)
    collision_content = b"sentinel mandatory config\n"

    (out_dir / "config.yaml").write_bytes(collision_content)

    return stale_disabled_artifacts, collision_content


def _assert_config_only_collision_preserves_stale_disabled_artifacts(
    out_dir: Path,
    *,
    stale_disabled_artifacts: dict[str, bytes],
    collision_content: bytes,
) -> None:
    _assert_stale_artifacts_preserved(
        out_dir,
        {**stale_disabled_artifacts, "config.yaml": collision_content},
        expected_artifacts=[*_expected_artifacts(CONFIG_ONLY), *stale_disabled_artifacts],
    )


def _assert_no_manifest_writes_enabled_artifacts(
    out_dir: Path,
    *,
    stale_manifest: bytes | None = None,
) -> None:
    expected_artifacts = _expected_artifacts(NO_MANIFEST)
    expected_outputs = {
        "write_manifest": False,
        "write_metrics": True,
        "write_events": True,
        "write_summary": True,
    }
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    summary = (out_dir / "summary.md").read_text()
    summary_artifacts = _summary_written_artifacts(summary)

    assert summary_artifacts == expected_artifacts
    _assert_artifacts_match_output_directory(
        out_dir,
        [*expected_artifacts, *(["manifest.yaml"] if stale_manifest is not None else [])],
    )
    assert normalized_config["outputs"] == expected_outputs
    assert "- write_manifest: disabled" in summary
    assert "- write_metrics: enabled" in summary
    assert "- write_events: enabled" in summary
    assert "- write_summary: enabled" in summary
    _assert_no_manifest_enabled_artifact_row_counts(out_dir)
    if stale_manifest is None:
        assert not (out_dir / "manifest.yaml").exists()
    else:
        assert (out_dir / "manifest.yaml").read_bytes() == stale_manifest


def _assert_no_manifest_enabled_artifact_row_counts(out_dir: Path) -> None:
    with (out_dir / "metrics.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 3
    with (out_dir / "events.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 45


def _summary_written_artifacts(summary: str) -> list[str]:
    written_artifacts_line = next(
        line for line in summary.splitlines() if line.startswith("- written artifacts: ")
    )
    return written_artifacts_line.removeprefix("- written artifacts: ").split(", ")


def _assert_summary_output_flags_match_config(
    summary: str,
    output_flags: dict[str, bool],
) -> None:
    for name, enabled in output_flags.items():
        state = "enabled" if enabled else "disabled"
        assert f"- {name}: {state}" in summary


def _assert_config_manifest_and_summary_run_fields_match(
    normalized_config: dict[str, object],
    *,
    manifest: dict[str, object],
    summary: str,
    seed: int,
) -> None:
    run_config = normalized_config["run"]
    model_config = normalized_config["model"]
    assert isinstance(run_config, dict)
    assert isinstance(model_config, dict)

    assert manifest["config"] == normalized_config
    assert manifest["experiment_id"] == run_config["experiment_id"]
    assert manifest["seed"] == seed
    assert manifest["ticks"] == run_config["ticks"]
    assert manifest["agent_count"] == model_config["agent_count"]
    assert manifest["actions"] == model_config["actions"]

    assert f"# {run_config['experiment_id']}" in summary
    assert f"- seed: {seed}" in summary
    assert f"- ticks: {run_config['ticks']}" in summary
    assert f"- agents: {model_config['agent_count']}" in summary


def _assert_manifest_agent_identity_and_roles_match_baseline(
    manifest: dict[str, object],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)

    agent_count = manifest["agent_count"]
    assert isinstance(agent_count, int)
    expected_agent_ids = [
        f"agent_{index:02d}"
        for index in range(1, agent_count + 1)
    ]
    expected_roles = {
        agent_id: BASELINE_ROLES[(index - 1) % len(BASELINE_ROLES)]
        for index, agent_id in enumerate(expected_agent_ids, start=1)
    }

    assert agent_count == 15
    assert model["agent_ids"] == expected_agent_ids
    assert model["roles"] == expected_roles
    assert model["role_action_metrics"]["roles"] == list(BASELINE_ROLES)


def _baseline_roles_for_agent_count(agent_count: int) -> dict[str, str]:
    assert agent_count == 15
    return {
        f"agent_{index:02d}": BASELINE_ROLES[(index - 1) % len(BASELINE_ROLES)]
        for index in range(1, agent_count + 1)
    }


def _assert_full_output_event_replay_matches_metrics_and_summary(
    out_dir: Path,
    *,
    expected_experiment_id: str,
    expected_ticks: int,
    expected_artifacts: list[str],
) -> None:
    replay = _event_replay_context(out_dir, require_manifest=True)
    normalized_config = replay["config"]
    manifest = replay["manifest"]
    summary = replay["summary"]
    metric_rows = replay["metric_rows"]
    event_rows = replay["event_rows"]
    actions = replay["actions"]
    ticks = replay["ticks"]
    agent_count = replay["agent_count"]
    roles = replay["roles"]
    event_lobe_rows = replay["event_lobe_rows"]
    event_bundle = _integrated_aggregate_bundle_from_events(
        event_rows,
        ticks=ticks,
        roles=roles,
        actions=actions,
    )

    assert normalized_config["run"]["experiment_id"] == expected_experiment_id
    assert ticks == expected_ticks
    assert agent_count == 15
    assert manifest["config"] == normalized_config
    assert manifest["actions"] == list(actions)
    assert manifest["artifacts"] == expected_artifacts
    assert len(metric_rows) == ticks
    assert len(event_rows) == ticks * agent_count
    assert _top_level_metric_sequence_from_events(
        event_rows,
        ticks=ticks,
    ) == _top_level_metric_sequence(metric_rows)
    assert _queue_pressure_metric_sequence_from_events(
        event_rows,
        ticks=ticks,
    ) == _queue_pressure_metric_sequence(metric_rows)
    assert _queued_task_age_metric_sequence_from_events(
        event_rows,
        ticks=ticks,
    ) == _queued_task_age_metric_sequence(metric_rows)
    assert _role_action_metric_sequence_from_events(
        event_rows,
        ticks=ticks,
        manifest_roles=roles,
        actions=actions,
    ) == _role_action_metric_sequence(metric_rows, actions)
    assert _lobe_label_sequence(event_lobe_rows) == _lobe_label_sequence(metric_rows)
    assert _lobe_transition_field_sequence(event_lobe_rows) == _lobe_transition_field_sequence(
        metric_rows
    )
    assert _lobe_run_state_sequence(event_lobe_rows) == _lobe_run_state_sequence(metric_rows)
    assert event_bundle == _integrated_aggregate_bundle_from_metrics(
        metric_rows,
        actions=actions,
    )
    assert event_bundle == _summary_integrated_aggregate_bundle(
        summary,
        actions=actions,
    )


def _assert_no_manifest_event_replay_bundle_matches_metrics_and_summary(
    out_dir: Path,
    *,
    expected_artifacts: list[str],
    expected_experiment_id: str,
    expected_actions: tuple[str, ...],
) -> dict[str, object]:
    replay = _no_manifest_event_replay_context(out_dir)
    normalized_config = replay["config"]
    summary = replay["summary"]
    metric_rows = replay["metric_rows"]
    event_rows = replay["event_rows"]
    actions = replay["actions"]
    ticks = replay["ticks"]
    agent_count = replay["agent_count"]
    event_lobe_rows = replay["event_lobe_rows"]
    event_bundle = _integrated_aggregate_bundle_from_events(
        event_rows,
        ticks=ticks,
        roles=replay["roles"],
        actions=actions,
    )
    metrics_bundle = _integrated_aggregate_bundle_from_metrics(
        metric_rows,
        actions=actions,
    )
    summary_bundle = _summary_integrated_aggregate_bundle(summary, actions=actions)

    assert normalized_config["run"]["experiment_id"] == expected_experiment_id
    assert normalized_config["outputs"]["write_manifest"] is False
    assert actions == expected_actions
    assert len(metric_rows) == ticks
    assert len(event_rows) == ticks * agent_count
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)
    assert not (out_dir / "manifest.yaml").exists()
    assert _summary_written_artifacts(summary) == expected_artifacts
    assert _lobe_label_sequence(event_lobe_rows) == _lobe_label_sequence(metric_rows)
    assert _lobe_transition_field_sequence(event_lobe_rows) == _lobe_transition_field_sequence(
        metric_rows
    )
    assert _lobe_dwell_runs(event_lobe_rows) == _lobe_dwell_runs(metric_rows)
    assert event_bundle == metrics_bundle
    assert event_bundle == summary_bundle
    return event_bundle


def _no_manifest_reordered_actions_event_replay_sequences(
    out_dir: Path,
) -> dict[str, object]:
    replay = _no_manifest_event_replay_context(out_dir)
    normalized_config = replay["config"]
    metric_rows = replay["metric_rows"]
    event_rows = replay["event_rows"]
    actions = replay["actions"]
    ticks = replay["ticks"]
    roles = replay["roles"]
    event_lobe_rows = replay["event_lobe_rows"]

    assert actions == ("work_task", "create_task", "message", "idle")

    return {
        "config": normalized_config,
        "metric_rows": metric_rows,
        "event_lobe_rows": event_lobe_rows,
        "actions": actions,
        "top_level": _top_level_metric_sequence_from_events(
            event_rows,
            ticks=ticks,
        ),
        "queue_pressure": _queue_pressure_metric_sequence_from_events(
            event_rows,
            ticks=ticks,
        ),
        "queue_age": _queued_task_age_metric_sequence_from_events(
            event_rows,
            ticks=ticks,
        ),
        "role_action": _role_action_metric_sequence_from_events(
            event_rows,
            ticks=ticks,
            manifest_roles=roles,
            actions=actions,
        ),
        "lobe_labels": _lobe_label_sequence(event_lobe_rows),
        "lobe_transitions": _lobe_transition_field_sequence(event_lobe_rows),
        "lobe_run_state": _lobe_run_state_sequence(event_lobe_rows),
    }


def _no_manifest_event_replay_context(out_dir: Path) -> dict[str, object]:
    replay = _event_replay_context(out_dir, require_manifest=False)
    normalized_config = replay["config"]

    assert normalized_config["outputs"]["write_manifest"] is False
    assert not (out_dir / "manifest.yaml").exists()

    return replay


def _event_replay_context(
    out_dir: Path,
    *,
    require_manifest: bool,
) -> dict[str, object]:
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    manifest = (
        yaml.safe_load((out_dir / "manifest.yaml").read_text())
        if require_manifest
        else None
    )
    summary = (out_dir / "summary.md").read_text()
    with (out_dir / "metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    with (out_dir / "events.csv").open() as handle:
        event_rows = list(csv.DictReader(handle))

    actions = tuple(_actions_from_normalized_config(normalized_config))
    ticks = normalized_config["run"]["ticks"]
    agent_count = normalized_config["model"]["agent_count"]
    roles = (
        manifest["model"]["roles"]
        if manifest is not None
        else _baseline_roles_for_agent_count(agent_count)
    )
    event_lobe_rows = _lobe_metric_rows_from_events(event_rows, ticks=ticks)

    assert len(metric_rows) == ticks
    assert len(event_rows) == ticks * agent_count

    return {
        "config": normalized_config,
        "manifest": manifest,
        "summary": summary,
        "metric_rows": metric_rows,
        "event_rows": event_rows,
        "event_lobe_rows": event_lobe_rows,
        "actions": actions,
        "ticks": ticks,
        "agent_count": agent_count,
        "roles": roles,
    }


def _assert_manifest_bus_counts_match_summary_and_metrics_row(
    manifest: dict[str, object],
    *,
    summary: str,
    metrics_row: dict[str, str],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)

    bus_nodes = model["bus_nodes"]
    bus_edges = model["bus_edges"]

    assert int(metrics_row["bus_nodes"]) == bus_nodes
    assert int(metrics_row["bus_edges"]) == bus_edges
    assert f"- bus graph: {bus_nodes} nodes, {bus_edges} edges" in summary


def _assert_summary_static_bus_metrics_match_metrics_row(
    summary: str,
    *,
    metrics_row: dict[str, str],
) -> None:
    assert f"- bus density: {metrics_row['bus_density']}" in summary
    assert f"- bus mean degree: {metrics_row['bus_mean_degree']}" in summary
    assert (
        f"- bus degree centralization: "
        f"{metrics_row['bus_degree_centralization']}"
    ) in summary


def _directory_artifacts(out_dir: Path) -> list[str]:
    return sorted(path.name for path in out_dir.iterdir() if path.is_file())


def _assert_artifacts_match_output_directory(
    out_dir: Path,
    artifacts: list[str],
) -> None:
    assert sorted(artifacts) == _directory_artifacts(out_dir)


def _assert_stale_artifacts_preserved(
    out_dir: Path,
    expected_contents: dict[str, bytes],
    *,
    expected_artifacts: list[str],
) -> None:
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)
    for artifact, content in expected_contents.items():
        assert (out_dir / artifact).read_bytes() == content


def _artifact_bytes_snapshot(
    out_dir: Path,
    artifacts: list[str] | None = None,
) -> dict[str, bytes]:
    artifact_names = artifacts if artifacts is not None else _directory_artifacts(out_dir)
    return {artifact: (out_dir / artifact).read_bytes() for artifact in artifact_names}


def _assert_output_directory_preserved(
    out_dir: Path,
    before: dict[str, bytes],
) -> None:
    assert _artifact_bytes_snapshot(out_dir) == before


def _run_api_pair(
    config_path: Path,
    tmp_path: Path,
    *,
    first_seed: int,
    second_seed: int,
    first_name: str,
    second_name: str,
) -> tuple[Path, Path, SimulationResult, SimulationResult]:
    first = tmp_path / first_name
    second = tmp_path / second_name
    artifacts = _expected_artifacts(config_path)

    first_result = run_experiment(config_path, seed=first_seed, out_dir=first)
    second_result = run_experiment(config_path, seed=second_seed, out_dir=second)

    _assert_artifacts_match_output_directory(first, artifacts)
    _assert_artifacts_match_output_directory(second, artifacts)
    return first, second, first_result, second_result


def _assert_artifacts_are_byte_identical(
    first: Path,
    second: Path,
    artifacts: list[str],
) -> None:
    for artifact in artifacts:
        assert (first / artifact).read_bytes() == (second / artifact).read_bytes()


def _assert_summary_written_artifacts_match_output_directory(out_dir: Path) -> list[str]:
    summary_artifacts = _summary_written_artifacts((out_dir / "summary.md").read_text())
    _assert_artifacts_match_output_directory(out_dir, summary_artifacts)
    return summary_artifacts


def _assert_artifact_indexes_match_directory_contents(
    out_dir: Path,
    expected_artifacts: list[str],
) -> None:
    _assert_artifacts_match_output_directory(out_dir, expected_artifacts)

    if (out_dir / "manifest.yaml").exists():
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        assert manifest["artifacts"] == expected_artifacts

    if (out_dir / "summary.md").exists():
        assert _summary_written_artifacts((out_dir / "summary.md").read_text()) == expected_artifacts


def _write_no_manifest_disabled_manifest_sentinel(out_dir: Path) -> bytes:
    out_dir.mkdir()
    stale_manifest = b"stale disabled manifest sentinel\n"
    (out_dir / "manifest.yaml").write_bytes(stale_manifest)
    return stale_manifest


def _assert_no_manifest_preserves_stale_disabled_manifest(
    out_dir: Path,
    *,
    stale_manifest: bytes,
) -> None:
    _assert_no_manifest_writes_enabled_artifacts(
        out_dir,
        stale_manifest=stale_manifest,
    )


def _write_no_manifest_collision_sentinels(
    out_dir: Path,
    collision_artifact: str,
) -> tuple[bytes, bytes]:
    out_dir.mkdir()
    stale_manifest = b"stale disabled manifest sentinel\n"
    collision_content = f"preexisting enabled {collision_artifact} sentinel\n".encode()

    (out_dir / "manifest.yaml").write_bytes(stale_manifest)
    (out_dir / collision_artifact).write_bytes(collision_content)

    return stale_manifest, collision_content


def _assert_no_manifest_collision_preserves_stale_manifest(
    out_dir: Path,
    collision_artifact: str,
    *,
    stale_manifest: bytes,
    collision_content: bytes,
) -> None:
    _assert_stale_artifacts_preserved(
        out_dir,
        {
            "manifest.yaml": stale_manifest,
            collision_artifact: collision_content,
        },
        expected_artifacts=["manifest.yaml", collision_artifact],
    )


def _assert_no_manifest_emitted_artifacts_preserve_schema_provenance(
    out_dir: Path,
) -> None:
    normalized_config = yaml.safe_load((out_dir / "config.yaml").read_text())
    actions = tuple(normalized_config["model"]["actions"])

    assert not (out_dir / "manifest.yaml").exists()
    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    with (out_dir / "events.csv").open() as handle:
        events_header = next(csv.reader(handle))
        event_rows = list(csv.DictReader(handle, fieldnames=events_header))
    summary = (out_dir / "summary.md").read_text()

    assert metrics_header == list(metrics_fieldnames(actions))
    assert events_header == list(EVENT_FIELDS)
    assert event_rows
    assert set(event["event_type"] for event in event_rows) <= set(BASELINE_EVENT_TYPES)
    _assert_summary_records_artifact_schema_provenance(
        summary,
        metrics_header=metrics_header,
        events_header=events_header,
        actions=actions,
    )


def _assert_summary_records_artifact_schema_provenance(
    summary: str,
    *,
    metrics_header: list[str],
    events_header: list[str],
    actions: tuple[str, ...],
) -> None:
    assert "## Artifact schema provenance" in summary
    assert f"- metrics fields: {len(metrics_header)}" in summary
    assert f"- event fields: {len(events_header)}" in summary
    assert f"- event types: {len(BASELINE_EVENT_TYPES)}" in summary
    assert f"- baseline lobe labels: {len(BASELINE_LOBE_LABELS)}" in summary
    assert f"- baseline lobe transition fields: {len(BASELINE_LOBE_TRANSITION_FIELDS)}" in summary
    assert f"- queue pressure fields: {len(QUEUE_PRESSURE_METRIC_FIELDS)}" in summary
    assert f"- queued task age fields: {len(QUEUED_TASK_AGE_METRIC_FIELDS)}" in summary
    assert f"- role/action fields: {len(role_action_metric_fields(actions))}" in summary
    assert "- metrics schema source: ohdyn.sim.metrics_fieldnames" in summary
    assert "- events schema source: ohdyn.sim.EVENT_FIELDS" in summary
    assert "- manifest mirrors emitted artifact schemas: yes" in summary


def _assert_summary_schema_provenance_counts_match_manifest(
    summary: str,
    manifest: dict[str, object],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)

    metrics = model["metrics"]
    events = model["events"]
    baseline_lobes = model["baseline_lobes"]
    queue_dynamics = model["queue_dynamics_metrics"]
    role_action_metrics = model["role_action_metrics"]
    assert isinstance(metrics, dict)
    assert isinstance(events, dict)
    assert isinstance(baseline_lobes, dict)
    assert isinstance(queue_dynamics, dict)
    assert isinstance(role_action_metrics, dict)

    assert f"- metrics fields: {len(metrics['fields'])}" in summary
    assert f"- event fields: {len(events['fields'])}" in summary
    assert f"- event types: {len(events['types'])}" in summary
    assert f"- baseline lobe labels: {len(baseline_lobes['labels'])}" in summary
    assert (
        f"- baseline lobe transition fields: "
        f"{len(baseline_lobes['transition_fields'])}"
    ) in summary
    assert f"- queue pressure fields: {len(queue_dynamics['pressure_fields'])}" in summary
    assert (
        f"- queued task age fields: "
        f"{len(queue_dynamics['queued_task_age_fields'])}"
    ) in summary
    assert f"- role/action fields: {len(role_action_metrics['fields'])}" in summary


def _assert_summary_event_type_totals_match_events(
    summary: str,
    *,
    event_rows: list[dict[str, str]],
) -> None:
    assert event_rows
    assert "## Event type totals" in summary

    event_type_totals = Counter(row["event_type"] for row in event_rows)
    for event_type, count in sorted(event_type_totals.items()):
        assert f"- {event_type}: {count}" in summary


def _assert_summary_top_level_totals_match_metrics_and_events(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert event_rows
    final = metric_rows[-1]

    messages_sent = sum(int(row["messages_sent_tick"]) for row in metric_rows)
    task_work_events = sum(int(row["tasks_worked_tick"]) for row in metric_rows)
    tasks_created = sum(int(row["tasks_created_tick"]) for row in metric_rows)
    tasks_completed = sum(int(row["tasks_completed_tick"]) for row in metric_rows)

    event_type_totals = Counter(row["event_type"] for row in event_rows)
    assert messages_sent == event_type_totals["message_sent"]
    assert task_work_events == event_type_totals["task_worked"]
    assert tasks_created == event_type_totals["task_created"]
    assert tasks_created == int(final["tasks_created_total"])
    assert tasks_completed == int(final["tasks_completed_total"])

    assert f"- events: {len(event_rows)}" in summary
    assert f"- messages sent: {messages_sent}" in summary
    assert f"- task work events: {task_work_events}" in summary
    assert f"- tasks created: {tasks_created}" in summary
    assert f"- tasks completed: {tasks_completed}" in summary
    assert f"- final queue depth: {final['queue_depth']}" in summary


def _assert_events_per_tick_action_counts_match_metrics_top_level_action_totals(
    *,
    metric_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert event_rows

    event_type_metric_fields = {
        "agent_idle": "idle_tick",
        "message_sent": "messages_sent_tick",
        "task_created": "tasks_created_tick",
        "task_worked": "tasks_worked_tick",
    }
    expected_ticks = [int(row["tick"]) for row in metric_rows]
    observed_event_ticks = sorted({int(event["tick"]) for event in event_rows})
    event_counts_by_tick = {
        tick: Counter(
            event["event_type"]
            for event in event_rows
            if int(event["tick"]) == tick
        )
        for tick in expected_ticks
    }

    assert set(event_type_metric_fields) == set(BASELINE_EVENT_TYPES)
    assert observed_event_ticks == expected_ticks
    assert sorted(event_counts_by_tick) == expected_ticks
    for row in metric_rows:
        tick = int(row["tick"])
        event_counts = event_counts_by_tick[tick]

        for event_type, metric_field in event_type_metric_fields.items():
            assert event_counts[event_type] == int(row[metric_field])
        assert sum(event_counts.values()) == int(row["agent_count"])


def _assert_events_per_tick_counts_match_configured_agent_population(
    *,
    event_rows: list[dict[str, str]],
    ticks: int,
    agent_count: int,
) -> None:
    assert event_rows

    expected_ticks = list(range(ticks))
    events_by_tick = Counter(int(row["tick"]) for row in event_rows)

    assert sorted(events_by_tick) == expected_ticks
    assert events_by_tick == {
        tick: agent_count
        for tick in expected_ticks
    }
    assert len(event_rows) == ticks * agent_count


def _assert_events_per_tick_agent_ids_match_manifest(
    *,
    event_rows: list[dict[str, str]],
    ticks: int,
    manifest_agent_ids: list[str],
) -> None:
    assert event_rows

    expected_ticks = list(range(ticks))
    expected_agent_ids = sorted(manifest_agent_ids)
    agent_ids_by_tick = {
        tick: [
            event["agent_id"]
            for event in event_rows
            if int(event["tick"]) == tick
        ]
        for tick in expected_ticks
    }

    assert sorted({int(event["tick"]) for event in event_rows}) == expected_ticks
    for tick, agent_ids in agent_ids_by_tick.items():
        assert len(agent_ids) == len(expected_agent_ids), tick
        assert len(set(agent_ids)) == len(expected_agent_ids), tick
        assert sorted(agent_ids) == expected_agent_ids


def _assert_events_replay_to_role_action_metrics_through_manifest_roles(
    *,
    metric_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
    manifest_roles: dict[str, str],
    actions: tuple[str, ...],
) -> None:
    assert metric_rows
    assert event_rows

    expected_ticks = [int(row["tick"]) for row in metric_rows]
    role_action_counts_by_tick = {
        tick: Counter(
            (manifest_roles[event["agent_id"]], event["action"])
            for event in event_rows
            if int(event["tick"]) == tick
        )
        for tick in expected_ticks
    }

    assert sorted({int(event["tick"]) for event in event_rows}) == expected_ticks
    assert set(actions) == {"idle", "message", "create_task", "work_task"}
    assert set(manifest_roles.values()) == set(BASELINE_ROLES)
    for event in event_rows:
        assert event["agent_id"] in manifest_roles
        assert event["action"] in actions

    for row in metric_rows:
        tick = int(row["tick"])
        role_action_counts = role_action_counts_by_tick[tick]
        for role in BASELINE_ROLES:
            for action in actions:
                assert role_action_counts[(role, action)] == int(
                    row[f"role_{role}_{action}_tick"]
                )


def _assert_events_replay_to_summary_role_action_totals_through_manifest_roles(
    summary: str,
    *,
    event_rows: list[dict[str, str]],
    manifest_roles: dict[str, str],
    actions: tuple[str, ...],
) -> None:
    assert _summary_role_action_totals(summary) == _role_action_totals_from_events(
        event_rows,
        manifest_roles=manifest_roles,
        actions=actions,
    )


def _role_action_totals_from_events(
    event_rows: list[dict[str, str]],
    *,
    manifest_roles: dict[str, str],
    actions: tuple[str, ...],
) -> dict[str, dict[str, int]]:
    assert event_rows
    assert set(actions) == {"idle", "message", "create_task", "work_task"}
    assert set(manifest_roles.values()) == set(BASELINE_ROLES)
    for event in event_rows:
        assert event["agent_id"] in manifest_roles
        assert event["action"] in actions

    role_action_counts = Counter(
        (manifest_roles[event["agent_id"]], event["action"])
        for event in event_rows
    )
    return {
        role: {
            action: role_action_counts[(role, action)]
            for action in actions
        }
        for role in BASELINE_ROLES
    }


def _role_action_metric_sequence_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
    manifest_roles: dict[str, str],
    actions: tuple[str, ...],
) -> list[tuple[int, ...]]:
    assert event_rows
    assert set(actions) == {"idle", "message", "create_task", "work_task"}
    assert set(manifest_roles.values()) == set(BASELINE_ROLES)
    for event in event_rows:
        assert event["agent_id"] in manifest_roles
        assert event["action"] in actions

    fields = [
        (role, action)
        for role in BASELINE_ROLES
        for action in actions
    ]
    role_action_counts_by_tick = {
        tick: Counter(
            (manifest_roles[event["agent_id"]], event["action"])
            for event in event_rows
            if int(event["tick"]) == tick
        )
        for tick in range(ticks)
    }

    assert sorted({int(event["tick"]) for event in event_rows}) == list(range(ticks))
    return [
        tuple(role_action_counts_by_tick[tick][field] for field in fields)
        for tick in range(ticks)
    ]


def _top_level_metric_sequence_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> list[tuple[int, ...]]:
    assert event_rows

    events_by_tick: dict[int, list[dict[str, str]]] = {
        tick: [] for tick in range(ticks)
    }
    for event in event_rows:
        events_by_tick[int(event["tick"])].append(event)

    assert sorted({int(event["tick"]) for event in event_rows}) == list(range(ticks))

    sequence: list[tuple[int, ...]] = []
    created_total = 0
    completed_total = 0
    previous_queue_depth = 0
    for tick in range(ticks):
        tick_events = events_by_tick[tick]
        event_type_counts = Counter(event["event_type"] for event in tick_events)
        tasks_created_tick = event_type_counts["task_created"]
        tasks_worked_tick = event_type_counts["task_worked"]
        tasks_completed_tick = sum(
            1
            for event in tick_events
            if event["event_type"] == "task_worked" and event["completed"] == "True"
        )
        created_total += tasks_created_tick
        completed_total += tasks_completed_tick
        queue_depth = created_total - completed_total
        queue_delta = queue_depth - previous_queue_depth

        sequence.append(
            (
                queue_depth,
                queue_delta,
                created_total,
                completed_total,
                tasks_completed_tick,
                event_type_counts["message_sent"],
                tasks_created_tick,
                tasks_worked_tick,
                event_type_counts["agent_idle"],
                tasks_created_tick - tasks_completed_tick,
                tasks_created_tick - tasks_worked_tick,
                tasks_worked_tick - tasks_completed_tick,
                queue_depth,
            )
        )
        previous_queue_depth = queue_depth

    return sequence


def _queue_pressure_metric_sequence_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> list[tuple[int, ...]]:
    return [
        row[-len(QUEUE_PRESSURE_METRIC_FIELDS):]
        for row in _top_level_metric_sequence_from_events(event_rows, ticks=ticks)
    ]


def _assert_events_per_tick_task_lifecycle_matches_queue_and_task_metrics(
    *,
    metric_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert event_rows

    events_by_tick: dict[int, list[dict[str, str]]] = {
        int(row["tick"]): [] for row in metric_rows
    }
    for event in event_rows:
        events_by_tick[int(event["tick"])].append(event)

    expected_ticks = [int(row["tick"]) for row in metric_rows]
    assert sorted(events_by_tick) == expected_ticks

    created_total = 0
    completed_total = 0
    previous_queue_depth = 0
    created_task_ids: set[str] = set()
    worked_task_ids: set[str] = set()

    for row in metric_rows:
        tick = int(row["tick"])
        tick_events = events_by_tick[tick]
        created_events = [
            event for event in tick_events if event["event_type"] == "task_created"
        ]
        worked_events = [
            event for event in tick_events if event["event_type"] == "task_worked"
        ]
        completed_events = [
            event for event in worked_events if event["completed"] == "True"
        ]

        for event in created_events:
            assert event["task_id"]
            assert int(event["work_units"]) > 0
            created_task_ids.add(event["task_id"])
        for event in worked_events:
            assert event["task_id"]
            assert int(event["remaining_work"]) >= 0
            assert event["completed"] in {"False", "True"}
            worked_task_ids.add(event["task_id"])

        created_total += len(created_events)
        completed_total += len(completed_events)
        queue_depth = int(row["queue_depth"])

        assert len(created_events) == int(row["tasks_created_tick"])
        assert len(worked_events) == int(row["tasks_worked_tick"])
        assert len(completed_events) == int(row["tasks_completed_tick"])
        assert created_total == int(row["tasks_created_total"])
        assert completed_total == int(row["tasks_completed_total"])
        assert queue_depth - previous_queue_depth == int(row["queue_delta_tick"])
        assert int(row["queue_delta_tick"]) == len(created_events) - len(completed_events)
        assert queue_depth == created_total - completed_total

        previous_queue_depth = queue_depth

    assert worked_task_ids <= created_task_ids


def _assert_event_replay_reproduces_queued_task_age_metrics(
    *,
    metric_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert event_rows

    assert _queued_task_age_metric_sequence_from_events(
        event_rows,
        ticks=len(metric_rows),
    ) == _queued_task_age_metric_sequence(metric_rows)


def _queued_task_age_metric_sequence_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> list[tuple[int, float]]:
    assert event_rows

    events_by_tick: dict[int, list[dict[str, str]]] = {
        tick: [] for tick in range(ticks)
    }
    for event in event_rows:
        events_by_tick[int(event["tick"])].append(event)

    assert sorted({int(event["tick"]) for event in event_rows}) == list(range(ticks))

    task_queue: deque[dict[str, int | str]] = deque()
    sequence: list[tuple[int, float]] = []
    for tick in range(ticks):
        for event in events_by_tick[tick]:
            if event["event_type"] == "task_created":
                task_queue.append(
                    {
                        "task_id": event["task_id"],
                        "created_tick": tick,
                        "remaining_work": int(event["work_units"]),
                    }
                )
            elif event["event_type"] == "task_worked":
                task = task_queue.popleft()
                assert task["task_id"] == event["task_id"]
                task["remaining_work"] = int(event["remaining_work"])
                if event["completed"] != "True":
                    task_queue.append(task)

        ages = [tick - int(task["created_tick"]) for task in task_queue]
        expected_max_age = max(ages, default=0)
        expected_mean_age = round(sum(ages) / len(ages), 6) if ages else 0.0

        sequence.append((expected_max_age, expected_mean_age))

    return sequence


def _assert_summary_bus_graph_fields_match_metrics_and_manifest(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
    manifest: dict[str, object],
) -> None:
    assert metric_rows
    final = metric_rows[-1]
    model = manifest["model"]
    assert isinstance(model, dict)

    assert int(final["bus_nodes"]) == model["bus_nodes"]
    assert int(final["bus_edges"]) == model["bus_edges"]
    assert f"- bus graph: {model['bus_nodes']} nodes, {model['bus_edges']} edges" in summary
    assert f"- bus density: {final['bus_density']}" in summary
    assert f"- bus degree centralization: {final['bus_degree_centralization']}" in summary


def _assert_summary_role_action_totals_match_metrics(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
    actions: tuple[str, ...],
) -> None:
    assert "## Role action totals" in summary

    for role, totals in _role_action_totals_from_metrics(metric_rows, actions).items():
        assert (
            f"- {role}: idle={totals['idle']}, message={totals['message']}, "
            f"create_task={totals['create_task']}, work_task={totals['work_task']}"
        ) in summary


def _role_action_totals_from_metrics(
    metric_rows: list[dict[str, str]],
    actions: tuple[str, ...],
) -> dict[str, dict[str, int]]:
    return {
        role: {
            action: sum(int(row[f"role_{role}_{action}_tick"]) for row in metric_rows)
            for action in actions
        }
        for role in BASELINE_ROLES
    }


def _assert_summary_queue_dynamics_match_metrics(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    final = metric_rows[-1]
    pressure_totals = _queue_pressure_totals_from_metrics(metric_rows)
    peak_queued_task_age = max(
        int(row["queued_task_age_max_tick"]) for row in metric_rows
    )
    mean_queued_task_mean_age = round(
        sum(float(row["queued_task_age_mean_tick"]) for row in metric_rows)
        / len(metric_rows),
        6,
    )

    assert f"- final backlog pressure: {final['backlog_pressure_tick']}" in summary
    assert f"- final queued task max age: {final['queued_task_age_max_tick']}" in summary
    assert f"- final queued task mean age: {final['queued_task_age_mean_tick']}" in summary
    assert f"- peak queued task max age: {peak_queued_task_age}" in summary
    assert f"- mean queued task mean age: {mean_queued_task_mean_age}" in summary
    assert (
        f"- created-completed balance: "
        f"{pressure_totals['created_completed_balance_tick']}"
    ) in summary
    assert (
        f"- created-worked balance: "
        f"{pressure_totals['created_worked_balance_tick']}"
    ) in summary
    assert f"- work-completion gap: {pressure_totals['work_completion_gap_tick']}" in summary


def _assert_first_row_queue_pressure_fields_match_summary(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    first = metric_rows[0]
    pressure_totals = _queue_pressure_totals_from_metrics(metric_rows)

    created = int(first["tasks_created_tick"])
    worked = int(first["tasks_worked_tick"])
    completed = int(first["tasks_completed_tick"])

    assert int(first["created_completed_balance_tick"]) == created - completed
    assert int(first["created_worked_balance_tick"]) == created - worked
    assert int(first["work_completion_gap_tick"]) == worked - completed
    assert first["backlog_pressure_tick"] == first["queue_depth"]

    assert f"- final backlog pressure: {metric_rows[-1]['backlog_pressure_tick']}" in summary
    assert (
        f"- created-completed balance: "
        f"{pressure_totals['created_completed_balance_tick']}"
    ) in summary
    assert (
        f"- created-worked balance: "
        f"{pressure_totals['created_worked_balance_tick']}"
    ) in summary
    assert f"- work-completion gap: {pressure_totals['work_completion_gap_tick']}" in summary


def _assert_queued_task_age_summary_matches_metrics(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    final = metric_rows[-1]
    peak_queued_task_age = max(
        int(row["queued_task_age_max_tick"]) for row in metric_rows
    )
    mean_queued_task_mean_age = round(
        sum(float(row["queued_task_age_mean_tick"]) for row in metric_rows)
        / len(metric_rows),
        6,
    )

    assert f"- final queued task max age: {final['queued_task_age_max_tick']}" in summary
    assert f"- final queued task mean age: {final['queued_task_age_mean_tick']}" in summary
    assert f"- peak queued task max age: {peak_queued_task_age}" in summary
    assert f"- mean queued task mean age: {mean_queued_task_mean_age}" in summary


def _queue_pressure_totals_from_metrics(
    metric_rows: list[dict[str, str]],
) -> dict[str, int]:
    return {
        field: sum(int(row[field]) for row in metric_rows)
        for field in QUEUE_PRESSURE_METRIC_FIELDS
        if field != "backlog_pressure_tick"
    }


def _summary_queue_pressure_totals(summary: str) -> dict[str, int]:
    labels = {
        "created-completed balance": "created_completed_balance_tick",
        "created-worked balance": "created_worked_balance_tick",
        "work-completion gap": "work_completion_gap_tick",
    }
    totals: dict[str, int] = {}
    for line in summary.splitlines():
        for label, field in labels.items():
            prefix = f"- {label}: "
            if line.startswith(prefix):
                totals[field] = int(line.removeprefix(prefix))

    assert set(totals) == set(labels.values())
    return totals


def _task_and_queue_totals_from_metrics(
    metric_rows: list[dict[str, str]],
) -> dict[str, int]:
    assert metric_rows
    final = metric_rows[-1]
    return {
        "tasks_created_total": int(final["tasks_created_total"]),
        "tasks_completed_total": int(final["tasks_completed_total"]),
        "queue_depth": int(final["queue_depth"]),
    }


def _summary_task_and_queue_totals(summary: str) -> dict[str, int]:
    labels = {
        "tasks created": "tasks_created_total",
        "tasks completed": "tasks_completed_total",
        "final queue depth": "queue_depth",
    }
    totals: dict[str, int] = {}
    for line in summary.splitlines():
        for label, field in labels.items():
            prefix = f"- {label}: "
            if line.startswith(prefix):
                totals[field] = int(line.removeprefix(prefix))

    assert set(totals) == set(labels.values())
    return totals


def _event_type_totals_from_events(
    event_rows: list[dict[str, str]],
) -> dict[str, int]:
    assert event_rows
    return dict(sorted(Counter(row["event_type"] for row in event_rows).items()))


def _summary_event_type_totals(summary: str) -> dict[str, int]:
    totals: dict[str, int] = {}
    in_section = False
    for line in summary.splitlines():
        if line == "## Event type totals":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- "):
            continue

        event_type, count = line.removeprefix("- ").split(": ", maxsplit=1)
        totals[event_type] = int(count)

    assert totals
    return dict(sorted(totals.items()))


def _queued_task_age_aggregates_from_metrics(
    metric_rows: list[dict[str, str]],
) -> dict[str, float]:
    assert metric_rows
    final = metric_rows[-1]
    return {
        "final_queued_task_max_age": float(final["queued_task_age_max_tick"]),
        "final_queued_task_mean_age": float(final["queued_task_age_mean_tick"]),
        "peak_queued_task_max_age": float(
            max(int(row["queued_task_age_max_tick"]) for row in metric_rows)
        ),
        "mean_queued_task_mean_age": round(
            sum(float(row["queued_task_age_mean_tick"]) for row in metric_rows)
            / len(metric_rows),
            6,
        ),
    }


def _summary_queued_task_age_aggregates(summary: str) -> dict[str, float]:
    labels = {
        "final queued task max age": "final_queued_task_max_age",
        "final queued task mean age": "final_queued_task_mean_age",
        "peak queued task max age": "peak_queued_task_max_age",
        "mean queued task mean age": "mean_queued_task_mean_age",
    }
    aggregates: dict[str, float] = {}
    for line in summary.splitlines():
        for label, field in labels.items():
            prefix = f"- {label}: "
            if line.startswith(prefix):
                aggregates[field] = float(line.removeprefix(prefix))

    assert set(aggregates) == set(labels.values())
    return aggregates


def _task_and_queue_totals_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> dict[str, int]:
    assert event_rows
    final = _top_level_metric_sequence_from_events(event_rows, ticks=ticks)[-1]
    return {
        "tasks_created_total": final[2],
        "tasks_completed_total": final[3],
        "queue_depth": final[0],
    }


def _queue_pressure_totals_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> dict[str, int]:
    pressure_sequence = _queue_pressure_metric_sequence_from_events(
        event_rows,
        ticks=ticks,
    )
    return {
        field: sum(row[index] for row in pressure_sequence)
        for index, field in enumerate(QUEUE_PRESSURE_METRIC_FIELDS)
        if field != "backlog_pressure_tick"
    }


def _queued_task_age_aggregates_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> dict[str, float]:
    age_sequence = _queued_task_age_metric_sequence_from_events(event_rows, ticks=ticks)
    final_max_age, final_mean_age = age_sequence[-1]
    return {
        "final_queued_task_max_age": float(final_max_age),
        "final_queued_task_mean_age": float(final_mean_age),
        "peak_queued_task_max_age": float(max(row[0] for row in age_sequence)),
        "mean_queued_task_mean_age": round(
            sum(float(row[1]) for row in age_sequence) / len(age_sequence),
            6,
        ),
    }


def _task_queue_pressure_and_age_aggregate_tuple_from_metrics(
    metric_rows: list[dict[str, str]],
) -> dict[str, dict[str, int] | dict[str, float]]:
    return {
        "task_queue_totals": _task_and_queue_totals_from_metrics(metric_rows),
        "queue_pressure_totals": _queue_pressure_totals_from_metrics(metric_rows),
        "queued_task_age_aggregates": _queued_task_age_aggregates_from_metrics(
            metric_rows
        ),
    }


def _summary_task_queue_pressure_and_age_aggregate_tuple(
    summary: str,
) -> dict[str, dict[str, int] | dict[str, float]]:
    return {
        "task_queue_totals": _summary_task_and_queue_totals(summary),
        "queue_pressure_totals": _summary_queue_pressure_totals(summary),
        "queued_task_age_aggregates": _summary_queued_task_age_aggregates(summary),
    }


def _task_queue_pressure_and_age_aggregate_tuple_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> dict[str, dict[str, int] | dict[str, float]]:
    return {
        "task_queue_totals": _task_and_queue_totals_from_events(
            event_rows,
            ticks=ticks,
        ),
        "queue_pressure_totals": _queue_pressure_totals_from_events(
            event_rows,
            ticks=ticks,
        ),
        "queued_task_age_aggregates": _queued_task_age_aggregates_from_events(
            event_rows,
            ticks=ticks,
        ),
    }


def _integrated_aggregate_bundle_from_metrics(
    metric_rows: list[dict[str, str]],
    *,
    actions: tuple[str, ...],
) -> dict[str, object]:
    return {
        "task_queue_pressure_and_age": (
            _task_queue_pressure_and_age_aggregate_tuple_from_metrics(metric_rows)
        ),
        "lobe_aggregates": {
            "totals": dict(
                sorted(Counter(row["baseline_lobe_label"] for row in metric_rows).items())
            ),
            "transitions": _lobe_transition_totals_from_adjacent_labels(metric_rows),
            "dwell_runs": _lobe_dwell_runs(metric_rows),
        },
        "role_action_totals": _role_action_totals_from_metrics(metric_rows, actions),
    }


def _integrated_aggregate_bundle_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
    roles: dict[str, str],
    actions: tuple[str, ...],
) -> dict[str, object]:
    lobe_rows = _lobe_metric_rows_from_events(event_rows, ticks=ticks)
    return {
        "task_queue_pressure_and_age": (
            _task_queue_pressure_and_age_aggregate_tuple_from_events(
                event_rows,
                ticks=ticks,
            )
        ),
        "lobe_aggregates": {
            "totals": dict(
                sorted(Counter(row["baseline_lobe_label"] for row in lobe_rows).items())
            ),
            "transitions": _lobe_transition_totals_from_adjacent_labels(lobe_rows),
            "dwell_runs": _lobe_dwell_runs(lobe_rows),
        },
        "role_action_totals": _role_action_totals_from_events(
            event_rows,
            manifest_roles=roles,
            actions=actions,
        ),
    }


def _summary_integrated_aggregate_bundle(
    summary: str,
    *,
    actions: tuple[str, ...],
) -> dict[str, object]:
    role_action_totals = _summary_role_action_totals(summary)

    return {
        "task_queue_pressure_and_age": (
            _summary_task_queue_pressure_and_age_aggregate_tuple(summary)
        ),
        "lobe_aggregates": {
            "totals": _summary_lobe_totals(summary),
            "transitions": _summary_lobe_transition_totals(summary),
            "dwell_runs": _summary_lobe_dwell_runs(summary),
        },
        "role_action_totals": {
            role: {
                action: role_action_totals[role][action]
                for action in actions
            }
            for role in BASELINE_ROLES
        },
    }


def _assert_summary_lobe_aggregates_match_metrics(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert "## Baseline lobe totals" in summary
    assert "## Baseline lobe transitions" in summary
    assert "## Baseline lobe dwell runs" in summary

    lobe_totals = Counter(row["baseline_lobe_label"] for row in metric_rows)
    lobe_transitions = Counter(
        row["baseline_lobe_transition"]
        for row in metric_rows
        if row["baseline_lobe_transition"] not in {"start", "stable"}
    )

    for label, count in sorted(lobe_totals.items()):
        assert f"- {label}: {count}" in summary
    for transition, count in sorted(lobe_transitions.items()):
        assert f"- {transition}: {count}" in summary
    _assert_lobe_dwell_run_summary_matches_metrics(summary, metric_rows=metric_rows)


def _assert_lobe_dwell_run_summary_matches_metrics(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert "## Baseline lobe dwell runs" in summary

    for label, dwell in _lobe_dwell_runs(metric_rows).items():
        assert (
            f"- {label}: runs={dwell['runs']}, total_ticks={dwell['total_ticks']}, "
            f"max_run={dwell['max_run']}, mean_run={dwell['mean_run']}"
        ) in summary


def _assert_lobe_run_state_matches_recomputed_dwell_runs(
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows

    previous_label = ""
    expected_run_id = 0
    expected_run_length = 0
    completed_run_lengths: list[int] = []
    completed_run_labels: list[str] = []

    for row in metric_rows:
        label = row["baseline_lobe_label"]
        if label == previous_label:
            expected_run_length += 1
        else:
            if previous_label:
                completed_run_labels.append(previous_label)
                completed_run_lengths.append(expected_run_length)
            expected_run_id += 1
            expected_run_length = 1

        assert int(row["baseline_lobe_run_id"]) == expected_run_id
        assert int(row["baseline_lobe_current_run_length"]) == expected_run_length
        previous_label = label

    completed_run_labels.append(previous_label)
    completed_run_lengths.append(expected_run_length)

    dwell_runs = _lobe_dwell_runs(metric_rows)
    assert expected_run_id == sum(dwell["runs"] for dwell in dwell_runs.values())
    assert len(completed_run_lengths) == expected_run_id
    assert sum(completed_run_lengths) == len(metric_rows)
    assert max(completed_run_lengths) == max(dwell["max_run"] for dwell in dwell_runs.values())
    assert set(completed_run_labels) == set(dwell_runs)


def _assert_lobe_transitions_match_adjacent_labels(
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows

    assert metric_rows[0]["baseline_lobe_previous_label"] == ""
    assert metric_rows[0]["baseline_lobe_transition"] == "start"
    assert metric_rows[0]["baseline_lobe_transition_tick"] == "0"

    previous_label = metric_rows[0]["baseline_lobe_label"]
    for row in metric_rows[1:]:
        current_label = row["baseline_lobe_label"]
        changed = previous_label != current_label
        expected_transition = (
            f"{previous_label}->{current_label}"
            if changed
            else "stable"
        )

        assert row["baseline_lobe_previous_label"] == previous_label
        assert row["baseline_lobe_transition"] == expected_transition
        assert row["baseline_lobe_transition_tick"] == str(int(changed))
        previous_label = current_label


def _assert_summary_lobe_transition_totals_match_adjacent_labels(
    summary: str,
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    assert "## Baseline lobe transitions" in summary

    assert _summary_lobe_transition_totals(summary) == _lobe_transition_totals_from_adjacent_labels(
        metric_rows
    )


def _assert_summary_lobe_transition_endpoints_use_only_manifest_lobe_labels(
    summary: str,
    *,
    manifest: dict[str, object],
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = set(baseline_lobes["labels"])
    summary_totals = _summary_lobe_transition_totals(summary)
    observed_totals = _lobe_transition_totals_from_adjacent_labels(metric_rows)

    assert summary_totals
    assert summary_totals == observed_totals
    for transition in summary_totals:
        source_label, target_label = transition.split("->", maxsplit=1)
        assert source_label in manifest_labels
        assert target_label in manifest_labels


def _assert_manifest_lobe_labels_cover_observed_metrics(
    manifest: dict[str, object],
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = baseline_lobes["labels"]
    assert manifest_labels == list(BASELINE_LOBE_LABELS)
    assert set(row["baseline_lobe_label"] for row in metric_rows) <= set(manifest_labels)


def _assert_manifest_lobe_labels_cover_previous_metrics_labels(
    manifest: dict[str, object],
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = baseline_lobes["labels"]
    previous_labels = [row["baseline_lobe_previous_label"] for row in metric_rows]

    assert manifest_labels == list(BASELINE_LOBE_LABELS)
    assert previous_labels[0] == ""
    assert "" not in previous_labels[1:]
    assert set(previous_labels[1:]) <= set(manifest_labels)


def _assert_manifest_lobe_labels_cover_metrics_transition_endpoints(
    manifest: dict[str, object],
    *,
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = baseline_lobes["labels"]
    transitions = [
        row["baseline_lobe_transition"]
        for row in metric_rows
        if row["baseline_lobe_transition"] not in {"start", "stable"}
    ]

    assert manifest_labels == list(BASELINE_LOBE_LABELS)
    assert transitions
    for transition in transitions:
        source_label, target_label = transition.split("->", maxsplit=1)
        assert source_label in manifest_labels
        assert target_label in manifest_labels


def _assert_summary_lobe_totals_use_only_manifest_lobe_labels(
    summary: str,
    *,
    manifest: dict[str, object],
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = set(baseline_lobes["labels"])
    observed_totals = Counter(row["baseline_lobe_label"] for row in metric_rows)
    summary_totals = _summary_lobe_totals(summary)

    assert summary_totals
    assert set(summary_totals) <= manifest_labels
    assert set(summary_totals) == set(observed_totals)
    assert summary_totals == dict(sorted(observed_totals.items()))


def _assert_summary_lobe_dwell_runs_use_only_manifest_lobe_labels(
    summary: str,
    *,
    manifest: dict[str, object],
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    manifest_labels = set(baseline_lobes["labels"])
    observed_dwell_runs = _lobe_dwell_runs(metric_rows)
    summary_dwell_runs = _summary_lobe_dwell_runs(summary)

    assert summary_dwell_runs
    assert set(summary_dwell_runs) <= manifest_labels
    assert set(summary_dwell_runs) == set(observed_dwell_runs)
    assert summary_dwell_runs == dict(sorted(observed_dwell_runs.items()))


def _assert_manifest_lobe_fields_match_metrics_header_and_observed_labels(
    manifest: dict[str, object],
    *,
    metrics_header: list[str],
    metric_rows: list[dict[str, str]],
) -> None:
    assert metric_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    baseline_lobes = model["baseline_lobes"]
    assert isinstance(baseline_lobes, dict)

    emitted_transition_fields = [
        field
        for field in metrics_header
        if field.startswith("baseline_lobe_") and field != "baseline_lobe_label"
    ]

    assert baseline_lobes["labels"] == list(BASELINE_LOBE_LABELS)
    assert baseline_lobes["transition_fields"] == emitted_transition_fields
    assert emitted_transition_fields == list(BASELINE_LOBE_TRANSITION_FIELDS)
    assert set(row["baseline_lobe_label"] for row in metric_rows) <= set(BASELINE_LOBE_LABELS)


def _assert_manifest_event_types_cover_observed_events(
    manifest: dict[str, object],
    *,
    event_rows: list[dict[str, str]],
) -> None:
    assert event_rows
    model = manifest["model"]
    assert isinstance(model, dict)
    events = model["events"]
    assert isinstance(events, dict)

    manifest_event_types = events["types"]
    assert manifest_event_types == list(BASELINE_EVENT_TYPES)
    assert set(event["event_type"] for event in event_rows) <= set(manifest_event_types)


def _assert_manifest_metrics_fields_match_metrics_header(
    manifest: dict[str, object],
    *,
    metrics_header: list[str],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)
    metrics = model["metrics"]
    assert isinstance(metrics, dict)

    manifest_metrics_fields = metrics["fields"]
    assert manifest_metrics_fields == metrics_header
    assert metrics_header == list(metrics_fieldnames(tuple(manifest["actions"])))


def _assert_manifest_role_action_fields_match_metrics_header_subset(
    manifest: dict[str, object],
    *,
    metrics_header: list[str],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)
    role_action_metrics = model["role_action_metrics"]
    assert isinstance(role_action_metrics, dict)

    emitted_role_action_fields = [
        field for field in metrics_header if field.startswith("role_")
    ]
    manifest_role_action_fields = role_action_metrics["fields"]
    assert manifest_role_action_fields == emitted_role_action_fields
    assert emitted_role_action_fields == list(role_action_metric_fields(tuple(manifest["actions"])))


def _assert_manifest_queue_dynamics_fields_match_metrics_header_subsets(
    manifest: dict[str, object],
    *,
    metrics_header: list[str],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)
    queue_dynamics_metrics = model["queue_dynamics_metrics"]
    assert isinstance(queue_dynamics_metrics, dict)

    emitted_pressure_fields = [
        field for field in metrics_header if field in QUEUE_PRESSURE_METRIC_FIELDS
    ]
    emitted_queued_task_age_fields = [
        field for field in metrics_header if field in QUEUED_TASK_AGE_METRIC_FIELDS
    ]

    assert queue_dynamics_metrics["pressure_fields"] == emitted_pressure_fields
    assert queue_dynamics_metrics["queued_task_age_fields"] == emitted_queued_task_age_fields
    assert emitted_pressure_fields == list(QUEUE_PRESSURE_METRIC_FIELDS)
    assert emitted_queued_task_age_fields == list(QUEUED_TASK_AGE_METRIC_FIELDS)


def _assert_manifest_event_fields_match_events_header(
    manifest: dict[str, object],
    *,
    events_header: list[str],
) -> None:
    model = manifest["model"]
    assert isinstance(model, dict)
    events = model["events"]
    assert isinstance(events, dict)

    manifest_event_fields = events["fields"]
    assert manifest_event_fields == events_header
    assert events_header == list(EVENT_FIELDS)


def _summary_lobe_transition_totals(summary: str) -> dict[str, int]:
    totals: dict[str, int] = {}
    in_section = False

    for line in summary.splitlines():
        if line == "## Baseline lobe transitions":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- "):
            continue

        transition, count = line.removeprefix("- ").split(": ", maxsplit=1)
        totals[transition] = int(count)

    return totals


def _summary_lobe_totals(summary: str) -> dict[str, int]:
    totals: dict[str, int] = {}
    in_section = False

    for line in summary.splitlines():
        if line == "## Baseline lobe totals":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- "):
            continue

        label, count = line.removeprefix("- ").split(": ", maxsplit=1)
        totals[label] = int(count)

    return totals


def _summary_lobe_dwell_runs(summary: str) -> dict[str, dict[str, int | float]]:
    dwell_runs: dict[str, dict[str, int | float]] = {}
    in_section = False

    for line in summary.splitlines():
        if line == "## Baseline lobe dwell runs":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- "):
            continue

        label, raw_fields = line.removeprefix("- ").split(": ", maxsplit=1)
        fields = dict(field.split("=", maxsplit=1) for field in raw_fields.split(", "))
        dwell_runs[label] = {
            "runs": int(fields["runs"]),
            "total_ticks": int(fields["total_ticks"]),
            "max_run": int(fields["max_run"]),
            "mean_run": float(fields["mean_run"]),
        }

    return dwell_runs


def _summary_role_action_totals(summary: str) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = {}
    in_section = False

    for line in summary.splitlines():
        if line == "## Role action totals":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- "):
            continue

        role, raw_fields = line.removeprefix("- ").split(": ", maxsplit=1)
        fields = dict(field.split("=", maxsplit=1) for field in raw_fields.split(", "))
        totals[role] = {
            "idle": int(fields["idle"]),
            "message": int(fields["message"]),
            "create_task": int(fields["create_task"]),
            "work_task": int(fields["work_task"]),
        }

    return totals


def _lobe_metric_rows_from_events(
    event_rows: list[dict[str, str]],
    *,
    ticks: int,
) -> list[dict[str, str]]:
    assert event_rows

    events_by_tick: dict[int, list[dict[str, str]]] = {
        tick: [] for tick in range(ticks)
    }
    for event in event_rows:
        events_by_tick[int(event["tick"])].append(event)

    assert sorted({int(event["tick"]) for event in event_rows}) == list(range(ticks))

    rows: list[dict[str, str]] = []
    queue_depth_start = 0
    previous_label = ""
    run_id = 0
    current_run_length = 0
    for tick in range(ticks):
        action_counts = Counter(event["action"] for event in events_by_tick[tick])
        completed_tick = sum(
            1
            for event in events_by_tick[tick]
            if event["event_type"] == "task_worked" and event["completed"] == "True"
        )
        queue_depth_end = (
            queue_depth_start + action_counts["create_task"] - completed_tick
        )
        queue_delta = queue_depth_end - queue_depth_start

        if (
            queue_depth_end > 0
            and queue_delta > 0
            and action_counts["create_task"] >= action_counts["work_task"]
        ):
            label = "backlog_growth"
        else:
            priority = ("work_task", "create_task", "message", "idle")
            dominant_action = max(
                priority,
                key=lambda action: (action_counts[action], -priority.index(action)),
            )
            label = {
                "work_task": "execution",
                "create_task": "task_generation",
                "message": "coordination",
                "idle": "low_activity",
            }[dominant_action]

        if label == previous_label:
            current_run_length += 1
        else:
            run_id += 1
            current_run_length = 1
        if not previous_label:
            transition = "start"
        elif previous_label == label:
            transition = "stable"
        else:
            transition = f"{previous_label}->{label}"

        rows.append(
            {
                "baseline_lobe_label": label,
                "baseline_lobe_previous_label": previous_label,
                "baseline_lobe_transition": transition,
                "baseline_lobe_transition_tick": str(
                    int(bool(previous_label) and previous_label != label)
                ),
                "baseline_lobe_run_id": str(run_id),
                "baseline_lobe_current_run_length": str(current_run_length),
            }
        )
        queue_depth_start = queue_depth_end
        previous_label = label

    return rows


def _lobe_transition_totals_from_adjacent_labels(
    metric_rows: list[dict[str, str]],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    previous_label = metric_rows[0]["baseline_lobe_label"]

    for row in metric_rows[1:]:
        current_label = row["baseline_lobe_label"]
        if previous_label != current_label:
            counts[f"{previous_label}->{current_label}"] += 1
        previous_label = current_label

    return dict(sorted(counts.items()))


def _lobe_transition_sequence(metric_rows: list[dict[str, str]]) -> list[str]:
    return [
        row["baseline_lobe_transition"]
        for row in metric_rows
        if row["baseline_lobe_transition"] not in {"start", "stable"}
    ]


def _lobe_transition_field_sequence(metric_rows: list[dict[str, str]]) -> list[str]:
    return [row["baseline_lobe_transition"] for row in metric_rows]


def _lobe_label_sequence(metric_rows: list[dict[str, str]]) -> list[str]:
    return [row["baseline_lobe_label"] for row in metric_rows]


def _lobe_run_state_sequence(metric_rows: list[dict[str, str]]) -> list[tuple[int, int]]:
    return [
        (
            int(row["baseline_lobe_run_id"]),
            int(row["baseline_lobe_current_run_length"]),
        )
        for row in metric_rows
    ]


def _role_action_metric_sequence(
    metric_rows: list[dict[str, str]],
    actions: tuple[str, ...],
) -> list[tuple[int, ...]]:
    fields = role_action_metric_fields(actions)
    return [
        tuple(int(row[field]) for field in fields)
        for row in metric_rows
    ]


def _top_level_metric_sequence(metric_rows: list[dict[str, str]]) -> list[tuple[int, ...]]:
    fields = (
        "queue_depth",
        "queue_delta_tick",
        "tasks_created_total",
        "tasks_completed_total",
        "tasks_completed_tick",
        "messages_sent_tick",
        "tasks_created_tick",
        "tasks_worked_tick",
        "idle_tick",
        "created_completed_balance_tick",
        "created_worked_balance_tick",
        "work_completion_gap_tick",
        "backlog_pressure_tick",
    )
    return [
        tuple(int(row[field]) for field in fields)
        for row in metric_rows
    ]


def _queue_pressure_metric_sequence(
    metric_rows: list[dict[str, str]],
) -> list[tuple[int, ...]]:
    return [
        tuple(int(row[field]) for field in QUEUE_PRESSURE_METRIC_FIELDS)
        for row in metric_rows
    ]


def _queued_task_age_metric_sequence(
    metric_rows: list[dict[str, str]],
) -> list[tuple[int, float]]:
    return [
        (
            int(row["queued_task_age_max_tick"]),
            float(row["queued_task_age_mean_tick"]),
        )
        for row in metric_rows
    ]


def test_fixed_seed_role_action_totals_are_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "coordinator": {"idle": 58, "message": 102, "create_task": 61, "work_task": 79},
            "researcher": {"idle": 42, "message": 106, "create_task": 57, "work_task": 95},
            "architect": {"idle": 51, "message": 93, "create_task": 82, "work_task": 74},
            "implementer": {"idle": 54, "message": 114, "create_task": 56, "work_task": 76},
            "reviewer": {"idle": 43, "message": 117, "create_task": 63, "work_task": 77},
        },
        2: {
            "coordinator": {"idle": 51, "message": 99, "create_task": 60, "work_task": 90},
            "researcher": {"idle": 54, "message": 95, "create_task": 63, "work_task": 88},
            "architect": {"idle": 69, "message": 94, "create_task": 62, "work_task": 75},
            "implementer": {"idle": 63, "message": 100, "create_task": 76, "work_task": 61},
            "reviewer": {"idle": 52, "message": 104, "create_task": 71, "work_task": 73},
        },
        17: {
            "coordinator": {"idle": 56, "message": 110, "create_task": 72, "work_task": 62},
            "researcher": {"idle": 54, "message": 107, "create_task": 71, "work_task": 68},
            "architect": {"idle": 59, "message": 107, "create_task": 56, "work_task": 78},
            "implementer": {"idle": 53, "message": 102, "create_task": 69, "work_task": 76},
            "reviewer": {"idle": 45, "message": 125, "create_task": 68, "work_task": 62},
        },
    }
    actions = ("idle", "message", "create_task", "work_task")

    observed = {}
    for seed in expected:
        out_dir = tmp_path / f"seed{seed}"
        result = run_experiment(CONFIG, seed=seed, out_dir=out_dir)
        summary = (out_dir / "summary.md").read_text()

        observed[seed] = {
            role: {
                action: sum(int(row[f"role_{role}_{action}_tick"]) for row in result.metrics)
                for action in actions
            }
            for role in BASELINE_ROLES
        }

        for role, totals in expected[seed].items():
            assert (
                f"- {role}: idle={totals['idle']}, message={totals['message']}, "
                f"create_task={totals['create_task']}, work_task={totals['work_task']}"
            ) in summary

    assert observed == expected


def test_fixed_seed_event_type_totals_are_stable(tmp_path: Path) -> None:
    expected = {
        1: {
            "agent_idle": 248,
            "message_sent": 532,
            "task_created": 319,
            "task_worked": 401,
        },
        2: {
            "agent_idle": 289,
            "message_sent": 492,
            "task_created": 332,
            "task_worked": 387,
        },
        17: {
            "agent_idle": 267,
            "message_sent": 551,
            "task_created": 336,
            "task_worked": 346,
        },
    }

    observed = {}
    for seed in expected:
        out_dir = tmp_path / f"seed{seed}"
        result = run_experiment(CONFIG, seed=seed, out_dir=out_dir)
        with (out_dir / "events.csv").open() as handle:
            event_rows = list(csv.DictReader(handle))

        observed[seed] = dict(sorted(Counter(event["event_type"] for event in result.events).items()))
        assert dict(sorted(Counter(row["event_type"] for row in event_rows).items())) == expected[seed]
        assert sum(observed[seed].values()) == 1500
        summary = (out_dir / "summary.md").read_text()
        for event_type, count in expected[seed].items():
            assert f"- {event_type}: {count}" in summary

    assert observed == expected


def test_loads_a6_logistic_appraisal_smoke_config() -> None:
    config = load_config(A6_LOGISTIC_APPRAISAL)

    assert config.run.experiment_id == "a6_logistic_appraisal_smoke"
    assert config.run.ticks == 16
    assert config.logistic_appraisal is not None
    assert config.logistic_appraisal.condition == "logistic"
    assert config.logistic_appraisal.handoff_threshold == 0.55
    assert config.logistic_appraisal.threshold_shuffle_probability == 0.35
    assert set(config.model.actions) == {
        "idle",
        "message",
        "create_task",
        "work_task",
        "synthesize",
        "review",
        "formalize",
        "maintain",
        "predict",
        "communicate",
        "pause",
    }


def test_a6_config_loading_rejects_unknown_fields_and_invalid_probabilities(
    tmp_path: Path,
) -> None:
    base = yaml.safe_load(A6_LOGISTIC_APPRAISAL.read_text())
    base["logistic_appraisal"]["surprise_knob"] = 1.0
    unknown_path = tmp_path / "unknown_a6.yaml"
    unknown_path.write_text(yaml.safe_dump(base))
    with pytest.raises(ValueError, match="unsupported keys: surprise_knob"):
        load_config(unknown_path)

    invalid = yaml.safe_load(A6_LOGISTIC_APPRAISAL.read_text())
    invalid["logistic_appraisal"]["threshold_shuffle_probability"] = 1.2
    invalid_path = tmp_path / "invalid_a6.yaml"
    invalid_path.write_text(yaml.safe_dump(invalid))
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        load_config(invalid_path)


def test_loads_a7_semantic_field_smoke_fixture_stubs() -> None:
    observed_conditions = []
    for config_path in A7_SMOKE_FIXTURES:
        config = load_config(config_path)

        assert config.run.ticks == 16
        assert config.model.agent_count == 15
        assert set(A6_ACTIONS).issubset(set(config.model.actions))
        assert config.semantic_field is not None
        assert config.semantic_field.prediction_budget_per_tick == 0.25
        assert config.semantic_field.lead_ticks == 2
        assert config.semantic_field.semantic_decay == 0.9
        assert config.semantic_field.logistic_beta == 4.0
        assert config.semantic_field.linear_gain == 1.0
        assert config.semantic_field.threshold_adaptation_rate == 0.03
        assert config.semantic_field.semantic_noise == 0.02
        assert config.semantic_field.phase_shift_ticks == 3
        assert config.logistic_appraisal is None
        assert config.predictive_control is None
        assert config.hives == ()
        observed_conditions.append(config.semantic_field.condition)

    assert tuple(observed_conditions) == A7_CONDITIONS


def test_a7_semantic_field_config_round_trips_to_normalized_dict() -> None:
    config = load_config(A7_LOGISTIC_SEMANTIC_COUPLING)
    normalized = config.to_dict()

    assert normalized["semantic_field"] == {
        "condition": "a7_logistic_semantic_coupling",
        "prediction_budget_per_tick": 0.25,
        "lead_ticks": 2,
        "semantic_decay": 0.9,
        "logistic_beta": 4.0,
        "linear_gain": 1.0,
        "threshold_adaptation_rate": 0.03,
        "semantic_noise": 0.02,
        "phase_shift_ticks": 3,
    }
    assert "logistic_appraisal" not in normalized
    assert "predictive_control" not in normalized


def test_a7_config_loading_rejects_unknown_invalid_and_out_of_scope_fields(
    tmp_path: Path,
) -> None:
    base = yaml.safe_load(A7_LOGISTIC_SEMANTIC_COUPLING.read_text())
    base["semantic_field"]["surprise_knob"] = 1.0
    unknown_path = tmp_path / "unknown_a7.yaml"
    unknown_path.write_text(yaml.safe_dump(base))
    with pytest.raises(ValueError, match="unsupported keys: surprise_knob"):
        load_config(unknown_path)

    invalid_condition = yaml.safe_load(A7_LOGISTIC_SEMANTIC_COUPLING.read_text())
    invalid_condition["semantic_field"]["condition"] = "a7_unregistered_condition"
    invalid_condition_path = tmp_path / "invalid_condition_a7.yaml"
    invalid_condition_path.write_text(yaml.safe_dump(invalid_condition))
    with pytest.raises(ValueError, match="must be one of"):
        load_config(invalid_condition_path)

    invalid_probability = yaml.safe_load(A7_LOGISTIC_SEMANTIC_COUPLING.read_text())
    invalid_probability["semantic_field"]["semantic_noise"] = 1.2
    invalid_probability_path = tmp_path / "invalid_probability_a7.yaml"
    invalid_probability_path.write_text(yaml.safe_dump(invalid_probability))
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        load_config(invalid_probability_path)

    mixed_a6 = yaml.safe_load(A7_LOGISTIC_SEMANTIC_COUPLING.read_text())
    mixed_a6["logistic_appraisal"] = yaml.safe_load(A6_LOGISTIC_APPRAISAL.read_text())[
        "logistic_appraisal"
    ]
    mixed_a6_path = tmp_path / "mixed_a6_a7.yaml"
    mixed_a6_path.write_text(yaml.safe_dump(mixed_a6))
    with pytest.raises(ValueError, match="must not be combined with A6 logistic_appraisal"):
        load_config(mixed_a6_path)

    multi_hive = yaml.safe_load(A7_LOGISTIC_SEMANTIC_COUPLING.read_text())
    multi_hive["hives"] = [{"hive_id": "hive_a", "seed_offset": 0}]
    multi_hive_path = tmp_path / "multi_hive_a7.yaml"
    multi_hive_path.write_text(yaml.safe_dump(multi_hive))
    with pytest.raises(ValueError, match="single-hive A7"):
        load_config(multi_hive_path)


def test_a6_smoke_run_is_deterministic_and_emits_schema(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    first_result = run_experiment(A6_LOGISTIC_APPRAISAL, seed=6, out_dir=first)
    second_result = run_experiment(A6_LOGISTIC_APPRAISAL, seed=6, out_dir=second)

    _assert_artifacts_match_output_directory(first, A0_FULL_ARTIFACTS)
    _assert_artifacts_match_output_directory(second, A0_FULL_ARTIFACTS)
    assert (first / "metrics.csv").read_text() == (second / "metrics.csv").read_text()
    assert (first / "events.csv").read_text() == (second / "events.csv").read_text()
    assert first_result.metrics == second_result.metrics

    with (first / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    for field in logistic_appraisal_metric_fields():
        assert field in metrics_header

    with (first / "events.csv").open() as handle:
        event_types = {row["event_type"] for row in csv.DictReader(handle)}
    assert event_types & set(A6_EVENT_TYPES)

    manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    assert manifest["model"]["logistic_appraisal"]["condition"] == "logistic"
    assert manifest["model"]["logistic_appraisal"]["fields"] == list(
        logistic_appraisal_metric_fields()
    )
    assert set(manifest["model"]["logistic_appraisal"]["event_types"]) == set(A6_EVENT_TYPES)

    summary = (first / "summary.md").read_text()
    assert "## A6 logistic appraisal" in summary
    assert "- total handoff attempts:" in summary
    assert "- final artifact readiness:" in summary


def test_a6_artifact_update_source_schema_reconstructs_smoke_fixture(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a6_source_schema"
    result = run_experiment(A6_LOGISTIC_APPRAISAL, seed=6, out_dir=out_dir)

    with (out_dir / "events.csv").open() as handle:
        reader = csv.DictReader(handle)
        assert set(A6_ARTIFACT_UPDATE_SOURCE_FIELDS) <= set(reader.fieldnames or [])
        source_rows = [
            row
            for row in reader
            if row["event_type"] == "a6_artifact_update"
            and row["a6_artifact_update_source"]
        ]
    assert source_rows

    source_delta_fields = (
        "a6_artifact_delta_ambient",
        "a6_artifact_delta_handoff_attempt",
        "a6_artifact_delta_handoff_success",
        "a6_artifact_delta_handoff_failure",
        "a6_artifact_delta_prediction_expenditure",
        "a6_artifact_delta_prediction_error",
        "a6_artifact_delta_queue_work_accounting",
        "a6_artifact_delta_noise",
    )
    for row in source_rows:
        source_sum = round(sum(float(row[field] or 0.0) for field in source_delta_fields), 6)
        assert float(row["a6_artifact_delta_unclipped"]) == source_sum
        reconstructed_total = round(
            source_sum + float(row["a6_artifact_delta_clip_residual"] or 0.0),
            6,
        )
        assert float(row["a6_artifact_delta_total"]) == reconstructed_total

    artifact_deltas: Counter[str] = Counter()
    for row in source_rows:
        artifact_deltas[row["a6_artifact_field"]] += float(row["a6_artifact_delta_total"])

    initial_artifact = _initial_a6_artifact(result.config)
    final_metrics = result.metrics[-1]
    for field in A6_ARTIFACT_FIELDS:
        reconstructed = round(initial_artifact[field] + artifact_deltas[field], 6)
        assert reconstructed == final_metrics[f"a6_{field}_tick"]

    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    for field in (
        "a6_prediction_budget_available_tick",
        "a6_prediction_actions_tick",
        "a6_prediction_error_mean_tick",
        "a6_queue_depth_tick",
        "a6_work_actions_tick",
        "a6_action_opportunity_tick",
        "a6_service_capacity_tick",
    ):
        assert field in metrics_header

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert manifest["model"]["logistic_appraisal"]["artifact_update_source_fields"] == list(
        A6_ARTIFACT_UPDATE_SOURCE_FIELDS
    )


def test_a6_non_a6_configs_preserve_existing_a0_schema(tmp_path: Path) -> None:
    out_dir = tmp_path / "a0"
    run_experiment(CONFIG, seed=1, out_dir=out_dir)

    with (out_dir / "metrics.csv").open() as handle:
        metrics_header = next(csv.reader(handle))
    assert metrics_header == list(metrics_fieldnames(("idle", "message", "create_task", "work_task")))
    assert all(not field.startswith("a6_") for field in metrics_header)

    manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
    assert "logistic_appraisal" not in manifest["model"]


def test_a6_smoke_conditions_share_stream_contract_and_action_opportunity(
    tmp_path: Path,
) -> None:
    configs = (
        A6_LOGISTIC_APPRAISAL,
        A6_LINEAR_APPRAISAL,
        A6_THRESHOLD_SHUFFLED,
        A6_PHASE_SHUFFLED,
    )
    stream_contracts = []
    action_opportunities = []
    for config_path in configs:
        out_dir = tmp_path / config_path.stem
        result = run_experiment(config_path, seed=8, out_dir=out_dir)
        manifest = yaml.safe_load((out_dir / "manifest.yaml").read_text())
        stream_contracts.append(manifest["model"]["logistic_appraisal"]["rng_streams"])
        action_opportunities.append(
            [
                sum(
                    int(row[f"role_{role}_{action}_tick"])
                    for role in BASELINE_ROLES
                    for action in result.config.model.actions
                )
                for row in result.metrics
            ]
        )

    assert all(contract == stream_contracts[0] for contract in stream_contracts)
    assert action_opportunities == [[15] * 16] * 4


def test_a6_read_only_analysis_skeleton_consumes_existing_artifacts(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "compare"
    for config_path in (A6_LOGISTIC_APPRAISAL, A6_LINEAR_APPRAISAL):
        run_experiment(config_path, seed=3, out_dir=compare_dir / config_path.stem)

    out_dir = tmp_path / "analysis"
    result = run_a6_logistic_appraisal_analysis(compare_dir, out_dir)

    assert result["run_count"] == 2
    with (out_dir / "a6_logistic_appraisal_endpoints.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_ANALYSIS_ENDPOINT_FIELDS)
    with (out_dir / "a6_logistic_appraisal_manifest.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_ANALYSIS_MANIFEST_FIELDS)
    with (out_dir / "a6_logistic_appraisal_control_deltas.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_CONTROL_DELTA_FIELDS)
    with (out_dir / "a6_logistic_appraisal_control_summary.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_CONTROL_SUMMARY_FIELDS)
    with (out_dir / "a6_logistic_appraisal_residual_preflight.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_RESIDUAL_PREFLIGHT_FIELDS)
    with (out_dir / "a6_logistic_appraisal_residual_timeseries.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_RESIDUAL_TIMESERIES_FIELDS)
    with (out_dir / "a6_logistic_appraisal_residual_contrast_summary.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_RESIDUAL_CONTRAST_SUMMARY_FIELDS)
    with (out_dir / "a6_logistic_appraisal_residual_contrast_rollup.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_RESIDUAL_CONTRAST_ROLLUP_FIELDS)
    with (out_dir / "a6_logistic_appraisal_comparison_consistency.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_COMPARISON_CONSISTENCY_FIELDS)
        consistency_rows = list(csv.DictReader(handle, fieldnames=A6_COMPARISON_CONSISTENCY_FIELDS))
    with (out_dir / "a6_logistic_appraisal_effects_consistency.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_EFFECTS_CONSISTENCY_FIELDS)
        effects_rows = list(csv.DictReader(handle, fieldnames=A6_EFFECTS_CONSISTENCY_FIELDS))
    with (out_dir / "a6_logistic_appraisal_artifact_provenance.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_ARTIFACT_PROVENANCE_FIELDS)
        provenance_rows = list(csv.DictReader(handle, fieldnames=A6_ARTIFACT_PROVENANCE_FIELDS))
    with (out_dir / "a6_logistic_appraisal_source_accounting.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_SOURCE_ACCOUNTING_FIELDS)
        source_rows = list(csv.DictReader(handle, fieldnames=A6_SOURCE_ACCOUNTING_FIELDS))
    assert {row["status"] for row in consistency_rows} == {"missing_comparison_csv"}
    assert {row["status"] for row in effects_rows} == {"missing_effects_csv"}
    assert result["artifact_provenance_count"] == 20
    assert result["source_accounting_count"] == 20
    assert {row["artifact_field"] for row in provenance_rows} >= {
        "a6_artifact_readiness_tick",
        "a6_artifact_utility_tick",
    }
    assert {row["artifact_field"] for row in source_rows} >= {
        "a6_artifact_readiness_tick",
        "a6_artifact_utility_tick",
    }
    assert result["comparison_consistency_count"] == 2
    assert result["effects_consistency_count"] == 3
    summary = (out_dir / "summary.md").read_text()
    assert "- reran simulations: no" in summary
    assert "## Control Levels" in summary
    assert "- comparison consistency rows: 2" in summary
    assert "- effects consistency rows: 3" in summary
    assert "- artifact provenance rows: 20" in summary
    assert "- source accounting rows: 20" in summary


def test_a6_read_only_analysis_writes_paired_control_deltas(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "compare"
    for config_path in (
        A6_LOGISTIC_APPRAISAL,
        A6_LINEAR_APPRAISAL,
        A6_THRESHOLD_SHUFFLED,
        A6_PHASE_SHUFFLED,
    ):
        run_experiment(config_path, seed=4, out_dir=compare_dir / config_path.stem)

    out_dir = tmp_path / "analysis"
    result = run_a6_logistic_appraisal_analysis(compare_dir, out_dir)

    assert result["control_delta_count"] == 3
    assert result["missing_required_fields"] == []
    with (out_dir / "a6_logistic_appraisal_control_deltas.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert [row["contrast"] for row in rows] == [
        "logistic_vs_linear",
        "logistic_vs_phase_shuffled",
        "logistic_vs_threshold_shuffled",
    ]
    assert {row["paired"] for row in rows} == {"true"}
    linear_row = next(row for row in rows if row["contrast"] == "logistic_vs_linear")
    assert linear_row["seed"] == "4"
    assert linear_row["missing_required_fields"] == ""
    assert linear_row["queue_depth_delta"] != ""
    assert linear_row["action_opportunity_total_delta"] == "0.0"
    summary = (out_dir / "summary.md").read_text()
    assert "- paired control delta rows: 3" in summary
    assert "- missing required fields: none" in summary


def test_a6_read_only_analysis_writes_residual_preflight(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "compare"
    for config_path in (
        A6_LOGISTIC_APPRAISAL,
        A6_LINEAR_APPRAISAL,
        A6_THRESHOLD_SHUFFLED,
        A6_PHASE_SHUFFLED,
    ):
        run_experiment(config_path, seed=4, out_dir=compare_dir / config_path.stem)

    out_dir = tmp_path / "analysis"
    result = run_a6_logistic_appraisal_analysis(compare_dir, out_dir)

    assert result["residual_preflight_count"] == 56
    assert result["residual_timeseries_count"] == 896
    assert result["residual_contrast_summary_count"] == 42
    assert result["residual_contrast_rollup_count"] == 42
    assert result["control_summary_count"] == 42
    with (out_dir / "a6_logistic_appraisal_residual_preflight.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (out_dir / "a6_logistic_appraisal_residual_timeseries.csv").open() as handle:
        timeseries_rows = list(csv.DictReader(handle))
    with (out_dir / "a6_logistic_appraisal_residual_contrast_summary.csv").open() as handle:
        residual_contrast_rows = list(csv.DictReader(handle))
    with (out_dir / "a6_logistic_appraisal_residual_contrast_rollup.csv").open() as handle:
        residual_rollup_rows = list(csv.DictReader(handle))
    with (out_dir / "a6_logistic_appraisal_control_summary.csv").open() as handle:
        summary_rows = list(csv.DictReader(handle))

    assert list(rows[0]) == list(A6_RESIDUAL_PREFLIGHT_FIELDS)
    assert list(timeseries_rows[0]) == list(A6_RESIDUAL_TIMESERIES_FIELDS)
    assert list(residual_contrast_rows[0]) == list(A6_RESIDUAL_CONTRAST_SUMMARY_FIELDS)
    assert list(residual_rollup_rows[0]) == list(A6_RESIDUAL_CONTRAST_ROLLUP_FIELDS)
    assert list(summary_rows[0]) == list(A6_CONTROL_SUMMARY_FIELDS)
    assert {row["condition"] for row in rows} == {
        "logistic",
        "linear",
        "phase_shuffled",
        "threshold_shuffled",
    }
    assert {
        row["outcome_field"] for row in rows if row["condition"] == "logistic"
    } == {
        "a6_latent_activation_mean_tick",
        "a6_latent_focus_mean_tick",
        "a6_latent_fatigue_mean_tick",
        "a6_latent_prediction_error_mean_tick",
        "a6_artifact_novelty_tick",
        "a6_artifact_coherence_tick",
        "a6_artifact_actionability_tick",
        "a6_artifact_provenance_debt_tick",
        "a6_artifact_risk_tick",
        "a6_artifact_contradiction_tick",
        "a6_artifact_readiness_tick",
        "a6_artifact_implementation_maturity_tick",
        "a6_artifact_communication_maturity_tick",
        "a6_artifact_utility_tick",
    }
    assert {row["row_count"] for row in rows} == {"16"}
    assert {row["missing_control_fields"] for row in rows} == {""}
    assert {row["status"] for row in rows} == {"underdetermined_smoke_scale"}
    logistic_utility = next(
        row
        for row in rows
        if row["condition"] == "logistic"
        and row["outcome_field"] == "a6_artifact_utility_tick"
    )
    assert logistic_utility["raw_variance"] != ""
    assert logistic_utility["residual_variance"] != ""
    assert "action_predict_tick" in logistic_utility["control_fields_used"]
    logistic_utility_trace = [
        row
        for row in timeseries_rows
        if row["condition"] == "logistic"
        and row["outcome_field"] == "a6_artifact_utility_tick"
    ]
    assert len(logistic_utility_trace) == 16
    assert {row["status"] for row in logistic_utility_trace} == {
        "underdetermined_smoke_scale"
    }
    assert all(row["raw_value"] != "" for row in logistic_utility_trace)
    assert all(row["fitted_value"] != "" for row in logistic_utility_trace)
    assert all(row["residual_value"] != "" for row in logistic_utility_trace)
    assert all("action_predict_tick" in row["control_fields_used"] for row in logistic_utility_trace)
    logistic_linear_utility_contrast = next(
        row
        for row in residual_contrast_rows
        if row["contrast"] == "logistic_vs_linear"
        and row["outcome_field"] == "a6_artifact_utility_tick"
    )
    assert logistic_linear_utility_contrast["seed"] == "4"
    assert logistic_linear_utility_contrast["paired"] == "true"
    assert logistic_linear_utility_contrast["status"] == "underdetermined_smoke_scale"
    assert logistic_linear_utility_contrast["tick_count"] == "16"
    assert logistic_linear_utility_contrast["control_tick_count"] == "16"
    assert logistic_linear_utility_contrast["residual_variance_delta"] != ""
    assert logistic_linear_utility_contrast["residual_lag1_autocorrelation_delta"] != ""
    assert logistic_linear_utility_contrast["residual_sign_change_count_delta"] != ""
    assert (
        logistic_linear_utility_contrast["interpretation"]
        == "smoke-scale residual timeseries contrast only; not recurrence evidence"
    )
    logistic_linear_utility_rollup = next(
        row
        for row in residual_rollup_rows
        if row["contrast"] == "logistic_vs_linear"
        and row["outcome_field"] == "a6_artifact_utility_tick"
    )
    assert logistic_linear_utility_rollup["control_condition"] == "linear"
    assert logistic_linear_utility_rollup["paired_seed_count"] == "1"
    assert logistic_linear_utility_rollup["complete_seed_count"] == "1"
    assert logistic_linear_utility_rollup["incomplete_seed_count"] == "0"
    assert logistic_linear_utility_rollup["status"] == "underdetermined_smoke_scale"
    assert logistic_linear_utility_rollup["statuses_observed"] == "underdetermined_smoke_scale"
    assert logistic_linear_utility_rollup["seeds_included"] == "4"
    assert logistic_linear_utility_rollup["mean_residual_variance_delta"] != ""
    assert logistic_linear_utility_rollup[
        "residual_variance_direction_agreement"
    ] == "1.0"
    assert logistic_linear_utility_rollup[
        "mean_residual_lag1_autocorrelation_delta"
    ] != ""
    assert logistic_linear_utility_rollup[
        "residual_lag1_autocorrelation_direction_agreement"
    ] == "1.0"
    assert logistic_linear_utility_rollup[
        "mean_residual_sign_change_count_delta"
    ] != ""
    assert logistic_linear_utility_rollup[
        "residual_sign_change_count_direction_agreement"
    ] == "1.0"
    assert (
        logistic_linear_utility_rollup["interpretation"]
        == "smoke-scale residual contrast rollup only; direction agreement is not recurrence evidence"
    )
    logistic_linear_utility_summary = next(
        row
        for row in summary_rows
        if row["contrast"] == "logistic_vs_linear"
        and row["outcome_field"] == "a6_artifact_utility_tick"
    )
    assert logistic_linear_utility_summary["paired_seed_count"] == "1"
    assert logistic_linear_utility_summary["residual_status"] == "underdetermined_smoke_scale"
    assert logistic_linear_utility_summary["mean_residual_variance_delta"] != ""
    assert logistic_linear_utility_summary["mean_residual_lag1_autocorrelation_delta"] != ""
    assert (
        logistic_linear_utility_summary["interpretation"]
        == "smoke-scale residual contrast only; not recurrence or promotion evidence"
    )
    summary = (out_dir / "summary.md").read_text()
    assert "- residual preflight rows: 56" in summary
    assert "- residual timeseries rows: 896" in summary
    assert "- residual contrast summary rows: 42" in summary
    assert "- residual contrast rollup rows: 42" in summary
    assert "- control summary rows: 42" in summary
    assert "underdetermined smoke-scale rows are not recurrence evidence" in summary
    assert "fitted and residual values for audit only" in summary
    assert (
        "aggregate per-seed residual variance, lag-1 autocorrelation, and sign-change deltas"
        in summary
    )
    assert "cross-seed direction agreement for audit only" in summary


def _write_a6_2_minimal_run(
    run_dir: Path,
    *,
    condition: str,
    seed: int,
    ticks: int = 16,
    omit_event_sources: bool = False,
) -> None:
    run_dir.mkdir(parents=True)
    (run_dir / "config.yaml").write_text(
        yaml.safe_dump({"logistic_appraisal": {"condition": condition}})
    )
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump({"seed": seed}))
    metric_fields = [
        "tick",
        "queue_depth",
        "tasks_created_total",
        "tasks_completed_total",
        "tasks_worked_tick",
        "a6_prediction_budget_spent_tick",
        "a6_prediction_actions_tick",
        "a6_latent_activation_mean_tick",
        "a6_latent_focus_mean_tick",
        "a6_latent_fatigue_mean_tick",
        "a6_latent_prediction_error_mean_tick",
        "a6_artifact_novelty_tick",
        "a6_artifact_coherence_tick",
        "a6_artifact_actionability_tick",
        "a6_artifact_provenance_debt_tick",
        "a6_artifact_risk_tick",
        "a6_artifact_contradiction_tick",
        "a6_artifact_readiness_tick",
        "a6_artifact_implementation_maturity_tick",
        "a6_artifact_communication_maturity_tick",
        "a6_handoff_attempts_tick",
        "a6_handoff_successes_tick",
        "a6_handoff_failures_tick",
        "a6_queue_depth_tick",
        "a6_work_actions_tick",
        "a6_action_opportunity_tick",
        "a6_service_capacity_tick",
    ]
    with (run_dir / "metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=metric_fields)
        writer.writeheader()
        for tick in range(ticks):
            base = 0.1 + (0.01 * tick)
            writer.writerow(
                {
                    "tick": tick,
                    "queue_depth": 3 + tick % 2,
                    "tasks_created_total": 10 + tick,
                    "tasks_completed_total": 4 + tick // 2,
                    "tasks_worked_tick": 2,
                    "a6_prediction_budget_spent_tick": 0,
                    "a6_prediction_actions_tick": 0,
                    "a6_latent_activation_mean_tick": base,
                    "a6_latent_focus_mean_tick": base + 0.01,
                    "a6_latent_fatigue_mean_tick": base + 0.02,
                    "a6_latent_prediction_error_mean_tick": base + 0.03,
                    "a6_artifact_novelty_tick": base + 0.04,
                    "a6_artifact_coherence_tick": base + 0.05,
                    "a6_artifact_actionability_tick": base + 0.06,
                    "a6_artifact_provenance_debt_tick": base + 0.07,
                    "a6_artifact_risk_tick": base + 0.08,
                    "a6_artifact_contradiction_tick": base + 0.09,
                    "a6_artifact_readiness_tick": base + 0.10,
                    "a6_artifact_implementation_maturity_tick": base + 0.11,
                    "a6_artifact_communication_maturity_tick": base + 0.12,
                    "a6_handoff_attempts_tick": 1,
                    "a6_handoff_successes_tick": 1 if tick % 2 == 0 else 0,
                    "a6_handoff_failures_tick": 0 if tick % 2 == 0 else 1,
                    "a6_queue_depth_tick": 3 + tick % 2,
                    "a6_work_actions_tick": 2,
                    "a6_action_opportunity_tick": 15,
                    "a6_service_capacity_tick": 1,
                }
            )
    event_fields = [
        "tick",
        "event_type",
        "a6_artifact_update_source",
        "a6_artifact_field",
        "a6_artifact_delta_total",
        "a6_artifact_delta_ambient",
        "a6_artifact_delta_handoff_attempt",
        "a6_artifact_delta_handoff_success",
        "a6_artifact_delta_handoff_failure",
        "a6_artifact_delta_prediction_expenditure",
        "a6_artifact_delta_prediction_error",
        "a6_artifact_delta_queue_work_accounting",
        "a6_artifact_delta_noise",
        "a6_artifact_delta_unclipped",
        "a6_artifact_delta_clip_residual",
    ]
    if omit_event_sources:
        event_fields = ["tick", "event_type"]
    with (run_dir / "events.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=event_fields)
        writer.writeheader()
        for tick in range(ticks):
            row = {"tick": tick, "event_type": "a6_artifact_update"}
            if not omit_event_sources:
                row.update(
                    {
                        "a6_artifact_update_source": "handoff_success",
                        "a6_artifact_field": "readiness",
                        "a6_artifact_delta_total": 0.01,
                        "a6_artifact_delta_ambient": 0,
                        "a6_artifact_delta_handoff_attempt": 0,
                        "a6_artifact_delta_handoff_success": 0.01,
                        "a6_artifact_delta_handoff_failure": 0,
                        "a6_artifact_delta_prediction_expenditure": 0,
                        "a6_artifact_delta_prediction_error": 0,
                        "a6_artifact_delta_queue_work_accounting": 0,
                        "a6_artifact_delta_noise": 0,
                        "a6_artifact_delta_unclipped": 0.01,
                        "a6_artifact_delta_clip_residual": 0,
                    }
                )
            writer.writerow(row)


def test_a6_2_residual_recurrence_gate_writes_insufficient_horizon_rows(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "compare"
    _write_a6_2_minimal_run(compare_dir / "logistic_seed1", condition="logistic", seed=1)
    _write_a6_2_minimal_run(compare_dir / "linear_seed1", condition="linear", seed=1)

    out_dir = tmp_path / "analysis"
    result = run_a6_2_residual_recurrence_analysis(compare_dir, out_dir)

    assert result["run_count"] == 2
    assert result["recurrence_count"] == 26
    assert result["delta_count"] == 65
    assert result["status"] == "insufficient_horizon"
    with (out_dir / "a6_2_paired_seed_completeness.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_2_COMPLETENESS_FIELDS)
        completeness_rows = list(csv.DictReader(handle, fieldnames=A6_2_COMPLETENESS_FIELDS))
    with (out_dir / "a6_2_residual_recurrence_metrics.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_2_RECURRENCE_FIELDS)
        recurrence_rows = list(csv.DictReader(handle, fieldnames=A6_2_RECURRENCE_FIELDS))
    with (out_dir / "a6_2_residual_recurrence_deltas.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_2_DELTA_FIELDS)
        delta_rows = list(csv.DictReader(handle, fieldnames=A6_2_DELTA_FIELDS))
    with (out_dir / "a6_2_manifest.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_2_MANIFEST_FIELDS)

    assert {row["required_field_status"] for row in completeness_rows} == {"complete"}
    assert {row["status"] for row in recurrence_rows} == {"insufficient_horizon"}
    linear_delta = next(
        row
        for row in delta_rows
        if row["contrast"] == "logistic_vs_linear"
        and row["target_field"] == "a6_artifact_readiness_tick"
    )
    assert linear_delta["paired"] == "true"
    assert linear_delta["gate_status"] == "insufficient_horizon"
    assert "Rows marked insufficient_horizon are not recurrence evidence" in (
        out_dir / "summary.md"
    ).read_text()


def test_a6_2_residual_recurrence_gate_reports_missing_source_fields(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "compare"
    _write_a6_2_minimal_run(
        compare_dir / "logistic_seed1",
        condition="logistic",
        seed=1,
        omit_event_sources=True,
    )

    out_dir = tmp_path / "analysis"
    result = run_a6_2_residual_recurrence_analysis(compare_dir, out_dir)

    assert result["status"] == "missing_required_fields"
    assert "a6_artifact_delta_total" in result["missing_required_fields"]
    with (out_dir / "a6_2_paired_seed_completeness.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["required_field_status"] == "missing_required_fields"
    assert "a6_artifact_update_source" in rows[0]["missing_required_fields"]
    with (out_dir / "a6_2_residual_recurrence_metrics.csv").open() as handle:
        recurrence_rows = list(csv.DictReader(handle))
    assert {row["status"] for row in recurrence_rows} == {"missing_required_fields"}


def test_a6_read_only_analysis_writes_artifact_provenance_audit(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "compare"
    for config_path in (
        A6_LOGISTIC_APPRAISAL,
        A6_LINEAR_APPRAISAL,
        A6_THRESHOLD_SHUFFLED,
        A6_PHASE_SHUFFLED,
    ):
        run_experiment(config_path, seed=4, out_dir=compare_dir / config_path.stem)

    out_dir = tmp_path / "analysis"
    result = run_a6_logistic_appraisal_analysis(compare_dir, out_dir)

    assert result["artifact_provenance_count"] == 40
    with (out_dir / "a6_logistic_appraisal_artifact_provenance.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert list(rows[0]) == list(A6_ARTIFACT_PROVENANCE_FIELDS)
    assert {row["condition"] for row in rows} == {
        "logistic",
        "linear",
        "phase_shuffled",
        "threshold_shuffled",
    }
    assert {
        row["artifact_field"] for row in rows if row["condition"] == "logistic"
    } == {
        "a6_artifact_novelty_tick",
        "a6_artifact_coherence_tick",
        "a6_artifact_actionability_tick",
        "a6_artifact_provenance_debt_tick",
        "a6_artifact_risk_tick",
        "a6_artifact_contradiction_tick",
        "a6_artifact_readiness_tick",
        "a6_artifact_implementation_maturity_tick",
        "a6_artifact_communication_maturity_tick",
        "a6_artifact_utility_tick",
    }
    logistic_utility = next(
        row
        for row in rows
        if row["condition"] == "logistic"
        and row["artifact_field"] == "a6_artifact_utility_tick"
    )
    assert logistic_utility["tick_count"] == "16"
    assert logistic_utility["total_abs_delta"] != ""
    assert logistic_utility["handoff_success_event_count"] != ""
    assert logistic_utility["handoff_failure_event_count"] != ""
    assert logistic_utility["dominant_event_source"] in {
        "artifact_update",
        "handoff_attempt",
        "handoff_failure",
        "handoff_success",
        "no_a6_event",
    }
    assert logistic_utility["dominant_action_source"] in {
        "handoff",
        "predict",
        "work_task",
        "create_task",
        "message",
    }
    assert logistic_utility["alias_risk"] in {
        "high_action_alias_risk",
        "action_coupled_smoke",
        "ambient_artifact_update_coupled",
        "mixed_or_low_alias_risk_smoke",
        "no_change",
    }
    summary = (out_dir / "summary.md").read_text()
    assert "- artifact provenance rows: 40" in summary
    assert "same-tick artifact field deltas" in summary


def test_a6_read_only_analysis_writes_source_accounting_audit(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "compare"
    for config_path in (
        A6_LOGISTIC_APPRAISAL,
        A6_LINEAR_APPRAISAL,
        A6_THRESHOLD_SHUFFLED,
        A6_PHASE_SHUFFLED,
    ):
        run_experiment(config_path, seed=4, out_dir=compare_dir / config_path.stem)

    out_dir = tmp_path / "analysis"
    result = run_a6_logistic_appraisal_analysis(compare_dir, out_dir)

    assert result["source_accounting_count"] == 40
    with (out_dir / "a6_logistic_appraisal_source_accounting.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    assert list(rows[0]) == list(A6_SOURCE_ACCOUNTING_FIELDS)
    assert {row["condition"] for row in rows} == {
        "logistic",
        "linear",
        "phase_shuffled",
        "threshold_shuffled",
    }
    assert {
        row["artifact_field"] for row in rows if row["condition"] == "logistic"
    } == {
        "a6_artifact_novelty_tick",
        "a6_artifact_coherence_tick",
        "a6_artifact_actionability_tick",
        "a6_artifact_provenance_debt_tick",
        "a6_artifact_risk_tick",
        "a6_artifact_contradiction_tick",
        "a6_artifact_readiness_tick",
        "a6_artifact_implementation_maturity_tick",
        "a6_artifact_communication_maturity_tick",
        "a6_artifact_utility_tick",
    }
    assert {row["required_field_status"] for row in rows} == {"schema_pass"}
    assert {row["reconstruction_status"] for row in rows} == {"schema_pass"}
    assert {row["max_abs_reconstruction_residual"] for row in rows} == {"0.0"}
    logistic_readiness = next(
        row
        for row in rows
        if row["condition"] == "logistic"
        and row["artifact_field"] == "a6_artifact_readiness_tick"
    )
    logistic_utility = next(
        row
        for row in rows
        if row["condition"] == "logistic"
        and row["artifact_field"] == "a6_artifact_utility_tick"
    )
    assert logistic_readiness["update_event_count"] != "0"
    assert logistic_readiness["handoff_success_alias_share"] != ""
    assert logistic_readiness["queue_work_alias_share"] != ""
    assert logistic_utility["update_event_count"] != "0"
    assert logistic_utility["total_abs_delta"] != ""
    assert logistic_utility["prediction_expenditure_alias_share"] != ""
    assert logistic_utility["status"] in {
        "high_handoff_alias_risk",
        "high_prediction_alias_risk",
        "high_queue_work_alias_risk",
        "underdetermined_smoke_scale",
    }
    summary = (out_dir / "summary.md").read_text()
    assert "- source accounting rows: 40" in summary
    assert "artifact-delta reconstruction" in summary


def test_a6_smoke_comparison_helper_runs_only_preregistered_fixtures(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "a6_compare"

    rows = run_a6_logistic_appraisal_comparison(seeds=(1, 2), out_dir=out_dir)

    assert [row["condition"] for row in rows] == [
        "logistic",
        "linear",
        "threshold_shuffled",
        "phase_shuffled",
    ]
    assert all(row["seed_count"] == 2 for row in rows)
    assert all(row["run_count"] == 2 for row in rows)
    for condition in ("logistic", "linear", "threshold_shuffled", "phase_shuffled"):
        for seed in (1, 2):
            _assert_artifacts_match_output_directory(
                out_dir / f"{condition}_seed{seed}",
                A0_FULL_ARTIFACTS,
            )

    with (out_dir / "a6_logistic_appraisal_comparison_metrics.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_COMPARISON_FIELDS)
    with (out_dir / "a6_logistic_appraisal_effects.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_EFFECT_FIELDS)
    summary = (out_dir / "summary.md").read_text()
    assert "- scope: four checked-in single-hive smoke fixtures only; no broad sweep" in summary
    assert "- scientific status: smoke artifact comparison, not promotion evidence" in summary


def test_a6_1_comparison_derives_source_preserving_nulls_and_gate(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a6_1_compare"

    rows = run_a6_logistic_appraisal_comparison(
        seeds=(1, 2),
        out_dir=compare_dir,
        include_a6_1_nulls=True,
    )

    assert [row["condition"] for row in rows] == [
        "logistic",
        "linear",
        "threshold_shuffled",
        "phase_shuffled",
        "source_label_shuffled_within_tick",
        "handoff_success_timing_broken_matched_counts",
    ]
    for condition in (
        "source_label_shuffled_within_tick",
        "handoff_success_timing_broken_matched_counts",
    ):
        for seed in (1, 2):
            run_dir = compare_dir / f"{condition}_seed{seed}"
            config = yaml.safe_load((run_dir / "config.yaml").read_text())
            assert config["logistic_appraisal"]["condition"] == condition
            _assert_artifacts_match_output_directory(run_dir, A0_FULL_ARTIFACTS)

    source_events = list(
        csv.DictReader(
            (compare_dir / "source_label_shuffled_within_tick_seed1" / "events.csv").open()
        )
    )
    source_update = next(
        row for row in source_events if row["event_type"] == "a6_artifact_update"
    )
    assert source_update["a6_artifact_update_source"] == "source_label_shuffled_within_tick"
    assert source_update["a6_artifact_delta_total"] != ""

    timing_metrics = list(
        csv.DictReader(
            (
                compare_dir
                / "handoff_success_timing_broken_matched_counts_seed1"
                / "metrics.csv"
            ).open()
        )
    )
    logistic_metrics = list(
        csv.DictReader((compare_dir / "logistic_seed1" / "metrics.csv").open())
    )
    assert [
        row["a6_artifact_readiness_tick"] for row in timing_metrics
    ] != [
        row["a6_artifact_readiness_tick"] for row in logistic_metrics
    ]

    analysis_dir = tmp_path / "a6_1_analysis"
    result = run_a6_logistic_appraisal_analysis(compare_dir, analysis_dir)

    assert result["condition_count"] == 6
    assert result["control_delta_count"] == 10
    assert result["a6_1_pilot_null_gate_count"] == 8
    with (analysis_dir / "a6_1_pilot_null_gate.csv").open() as handle:
        assert next(csv.reader(handle)) == list(A6_1_PILOT_NULL_GATE_FIELDS)
        gate_rows = list(csv.DictReader(handle, fieldnames=A6_1_PILOT_NULL_GATE_FIELDS))
    assert {row["paired"] for row in gate_rows} == {"true"}
    assert {row["endpoint"] for row in gate_rows} == {
        "final_artifact_readiness",
        "final_artifact_utility",
    }
    assert {
        row["contrast"]
        for row in gate_rows
    } == {
        "logistic_vs_source_label_shuffled_within_tick",
        "logistic_vs_handoff_success_timing_broken_matched_counts",
    }
    assert {row["logistic_required_field_status"] for row in gate_rows} == {
        "schema_pass"
    }
    assert {row["control_reconstruction_status"] for row in gate_rows} == {
        "schema_pass"
    }
    summary = (analysis_dir / "summary.md").read_text()
    assert "- A6.1 pilot null gate rows: 8" in summary
    assert "backlog-adjusted productivity" in summary


def test_a6_2_long_horizon_comparison_uses_fixed_configs_and_seeds(
    tmp_path: Path,
) -> None:
    compare_dir = tmp_path / "a6_2_long_horizon_compare"

    rows = run_a6_2_long_horizon_comparison(out_dir=compare_dir)

    assert [row["condition"] for row in rows] == [
        "logistic",
        "linear",
        "threshold_shuffled",
        "phase_shuffled",
        "source_label_shuffled_within_tick",
        "handoff_success_timing_broken_matched_counts",
    ]
    assert {row["tick_count"] for row in rows} == {96}
    for condition in (
        "logistic",
        "linear",
        "threshold_shuffled",
        "phase_shuffled",
        "source_label_shuffled_within_tick",
        "handoff_success_timing_broken_matched_counts",
    ):
        for seed in (1, 2):
            run_dir = compare_dir / f"{condition}_seed{seed}"
            config = yaml.safe_load((run_dir / "config.yaml").read_text())
            assert config["run"]["ticks"] == 96
            _assert_artifacts_match_output_directory(run_dir, A0_FULL_ARTIFACTS)

    with pytest.raises(ValueError, match="fixed to paired seeds 1 and 2"):
        run_a6_2_long_horizon_comparison(
            seeds=(1, 2, 3),
            out_dir=tmp_path / "a6_2_long_horizon_broadened",
        )

    analysis_dir = tmp_path / "a6_2_long_horizon_analysis"
    result = run_a6_2_residual_recurrence_analysis(compare_dir, analysis_dir)
    assert result["status"] in {"conservative_closure", "computed_no_promotion"}
    with (analysis_dir / "a6_2_residual_recurrence_metrics.csv").open() as handle:
        metric_rows = list(csv.DictReader(handle))
    readiness_rows = [
        row
        for row in metric_rows
        if row["condition"] == "logistic"
        and row["target_field"] == "a6_artifact_readiness_tick"
    ]
    assert readiness_rows
    assert {row["dominant_source"] for row in readiness_rows} != {""}


def test_a6_smoke_comparison_cli(tmp_path: Path) -> None:
    out_dir = tmp_path / "a6_compare_cli"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ohdyn.compare_a6_logistic_appraisal",
            "--seeds",
            "1",
            "2",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert (out_dir / "a6_logistic_appraisal_comparison_metrics.csv").exists()
    assert (out_dir / "a6_logistic_appraisal_effects.csv").exists()
    assert (out_dir / "summary.md").exists()
