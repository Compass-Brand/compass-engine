"""BMAD Automation package for workflow automation components."""

from .validation_type_detector import (
    ValidationType,
    ValidationTypeResult,
    CustomPattern,
    VERDICT_PATTERNS,
    ERROR_PATTERNS,
    CHECKLIST_PATTERNS,
    CONFIDENCE_THRESHOLD,
    detect_validation_type,
    detect_validation_type_from_file,
    detect_verdict_patterns,
    detect_error_patterns,
    detect_checklist_patterns,
    parse_workflow_file,
    parse_custom_patterns_from_frontmatter,
    validate_custom_pattern,
    match_custom_patterns,
)

from .preflight_validator import (
    PreflightStatus,
    PreflightCheck,
    PreflightResult,
    validate_configuration,
    check_mcp_availability,
    validate_input_files,
    validate,
    parse_workflow_required_config,
    parse_workflow_required_inputs,
)

from .cross_reference_validator import (
    Severity,
    AlignmentStatus,
    AlignmentIssue,
    AlignmentResult,
    FR_PATTERNS,
    ADR_PATTERNS,
    extract_frs_from_content,
    extract_adrs_from_content,
    detect_orphaned_requirements,
    detect_unaddressed_decisions,
    validate_alignment,
)

from .context_preloader import (
    PreloadStatus,
    MemoryItem,
    ContextPreloadResult,
    ForgetfulTimeoutError,
    ForgetfulConnectionError,
    FORGETFUL_TIMEOUT_MS,
    RETRY_COUNT,
    RETRY_INTERVAL_MS,
    CONTEXT_LIMIT_CHARS,
    CACHE_TTL_SECONDS,
    CACHE_DIR,
    query_forgetful_memories,
    query_forgetful_memories_with_retry,
    prioritize_memories,
    deduplicate_memories,
    summarize_for_context,
    preload_context,
)

from .workflow_entry_wrapper import (
    # Story 2a.6: Workflow Configuration Parsing
    BMADModule,
    ConfigParseError,
    WorkflowConfig,
    parse_yaml_config,
    extract_frontmatter,
    parse_frontmatter_config,
    get_module_defaults,
    merge_with_defaults,
    parse_workflow_config,
)

from .tier_suggester import (
    # Story 2a.4: Tier Suggestion
    ProjectTier,
    TierConfidence,
    TierSuggestion,
    TIER_KEYWORDS,
    DEFAULT_TIER,
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
    LARGE_CODEBASE_THRESHOLD,
    VERY_LARGE_CODEBASE_THRESHOLD,
    analyze_description,
    calculate_keyword_confidence,
    analyze_codebase_metrics,
    suggest_tier,
)

from .step_executor import (
    # Story 2a.2: Autonomous Step Execution
    StepStatus,
    StepResult,
    StepExecutionConfig,
    WorkflowStatus,
    WorkflowExecutionResult,
    SUCCESS_VERDICTS,
    CONCERN_VERDICTS,
    FAILURE_VERDICTS,
    should_auto_transition,
    attempt_recovery,
    execute_step,
    execute_workflow_steps,
)

from .adaptive_behavior import (
    # Story 2a.7: Adaptive Behavior Configuration
    BehaviorProfile,
    ConfidenceThresholds,
    RegulatedDomainConfig,
    AdaptiveBehaviorConfig,
    DEFAULT_HIGH_THRESHOLD,
    DEFAULT_MEDIUM_THRESHOLD,
    TIER_PROFILES,
    REGULATED_DOMAINS,
    get_default_profile,
    get_regulated_config,
    create_behavior_config,
    update_thresholds,
)

from .memory_bridge import (
    # Story 4.1: Writing Workflow Decisions to Memory
    ImportanceLevel,
    WorkflowDecision,
    FixPattern,
    MenuSelectionPattern,
    MemoryEntry,
    MemoryBridge,
)

from .bmb_thresholds import (
    # Story 2b.3: BMB-Specific Menu Thresholds
    EscalationAction,
    EscalationResult,
    ValidationMetrics,
    BLOCKING_ERROR_THRESHOLD,
    MAJOR_ISSUE_THRESHOLD,
    COMPLIANCE_SCORE_THRESHOLD,
    MAX_THRESHOLD_CHECK_MS,
    check_blocking_errors,
    check_major_issues,
    check_compliance_score,
    evaluate_all_thresholds,
    is_within_thresholds,
    performance_check,
    BMBThresholdChecker,
)

from .menu_history import (
    # Story 2b-5: Menu History Tracking
    SelectionSource,
    MenuHistoryEntry,
    MenuHistoryManager,
    MAX_HISTORY_SIZE,
    HISTORY_DIR_NAME,
    MENU_HISTORY_SUBDIR,
)

from .batch_continue import (
    # Story 2b-6: Batch-Continue Logic (Tasks 1-3)
    BatchMode,
    BATCH_SIZE_BY_TIER,
    BatchConfig,
    get_batch_config,
    BatchState,
    BatchSummary,
    BatchContinueManager,
    CONTINUE_PATTERNS,
    is_continue_menu,
    AutoAllTracker,
)

from .checkpoint_presenter import (
    # Story 2b-7: Human Checkpoint Presentation (Tasks 1-6)
    CheckpointFormat,
    CONFIDENCE_THRESHOLDS,
    CheckpointConfig,
    get_format_for_confidence,
    CheckpointPresenter,
    MinimalCheckpoint,
    generate_summary_line,
    # Story 2b-7: Task 4 - Summary Format
    SummaryCheckpoint,
    extract_key_decisions,
    format_summary_checkpoint,
    # Story 2b-7: Task 5 - Full Audit Trail
    OperationLogEntry,
    AuditTrailCheckpoint,
    generate_operation_log,
    format_audit_trail_checkpoint,
    # Story 2b-7: Task 6 - Expandable Details
    ExpansionState,
    ExpandableDetails,
    expand_checkpoint,
    can_expand,
    get_expansion_state,
    # Story 2b-7: Task 7 - Integration with Automation Controller
    OrchestratorResult,
    CheckpointOrchestrator,
)

from .timeout_manager import (
    # Story 2b-9: Timeout Enforcement (Tasks 1-8)
    TimeoutLevel,
    TIMEOUT_SECONDS,
    TimeoutConfig,
    get_timeout_for_level,
    TimeoutState,
    TimeoutManager,
    # Task 3: Workflow Timeout
    WorkflowTimeoutError,
    enforce_workflow_timeout,
    # Task 4: Nested Timeout
    NestedTimeoutError,
    enforce_nested_timeout,
    # Task 5: Agent Timeout
    AgentTimeoutError,
    enforce_agent_timeout,
    # Task 6: State Preservation
    PreservedTimeoutState,
    preserve_state_on_timeout,
    get_preserved_state,
    clear_preserved_state,
    # Task 7: Timeout Logging
    TimeoutLog,
    log_timeout,
    get_timeout_logs,
    clear_timeout_logs,
    # Task 8: Context Managers
    workflow_timeout,
    nested_timeout,
    agent_timeout,
)

__all__ = [
    # Validation Type Detector
    "ValidationType",
    "ValidationTypeResult",
    "CustomPattern",
    "VERDICT_PATTERNS",
    "ERROR_PATTERNS",
    "CHECKLIST_PATTERNS",
    "CONFIDENCE_THRESHOLD",
    "detect_validation_type",
    "detect_validation_type_from_file",
    "detect_verdict_patterns",
    "detect_error_patterns",
    "detect_checklist_patterns",
    "parse_workflow_file",
    "parse_custom_patterns_from_frontmatter",
    "validate_custom_pattern",
    "match_custom_patterns",
    # Preflight Validator
    "PreflightStatus",
    "PreflightCheck",
    "PreflightResult",
    "validate_configuration",
    "check_mcp_availability",
    "validate_input_files",
    "validate",
    "parse_workflow_required_config",
    "parse_workflow_required_inputs",
    # Cross-Reference Validator
    "Severity",
    "AlignmentStatus",
    "AlignmentIssue",
    "AlignmentResult",
    "FR_PATTERNS",
    "ADR_PATTERNS",
    "extract_frs_from_content",
    "extract_adrs_from_content",
    "detect_orphaned_requirements",
    "detect_unaddressed_decisions",
    "validate_alignment",
    # Context Pre-Loader
    "PreloadStatus",
    "MemoryItem",
    "ContextPreloadResult",
    "ForgetfulTimeoutError",
    "ForgetfulConnectionError",
    "FORGETFUL_TIMEOUT_MS",
    "RETRY_COUNT",
    "RETRY_INTERVAL_MS",
    "CONTEXT_LIMIT_CHARS",
    "CACHE_TTL_SECONDS",
    "CACHE_DIR",
    "query_forgetful_memories",
    "query_forgetful_memories_with_retry",
    "prioritize_memories",
    "deduplicate_memories",
    "summarize_for_context",
    "preload_context",
    # Workflow Entry Wrapper (Story 2a.6)
    "BMADModule",
    "ConfigParseError",
    "WorkflowConfig",
    "parse_yaml_config",
    "extract_frontmatter",
    "parse_frontmatter_config",
    "get_module_defaults",
    "merge_with_defaults",
    "parse_workflow_config",
    # Tier Suggester (Story 2a.4)
    "ProjectTier",
    "TierConfidence",
    "TierSuggestion",
    "TIER_KEYWORDS",
    "DEFAULT_TIER",
    "HIGH_CONFIDENCE_THRESHOLD",
    "MEDIUM_CONFIDENCE_THRESHOLD",
    "LARGE_CODEBASE_THRESHOLD",
    "VERY_LARGE_CODEBASE_THRESHOLD",
    "analyze_description",
    "calculate_keyword_confidence",
    "analyze_codebase_metrics",
    "suggest_tier",
    # Step Executor (Story 2a.2)
    "StepStatus",
    "StepResult",
    "StepExecutionConfig",
    "WorkflowStatus",
    "WorkflowExecutionResult",
    "SUCCESS_VERDICTS",
    "CONCERN_VERDICTS",
    "FAILURE_VERDICTS",
    "should_auto_transition",
    "attempt_recovery",
    "execute_step",
    "execute_workflow_steps",
    # Adaptive Behavior (Story 2a.7)
    "BehaviorProfile",
    "ConfidenceThresholds",
    "RegulatedDomainConfig",
    "AdaptiveBehaviorConfig",
    "DEFAULT_HIGH_THRESHOLD",
    "DEFAULT_MEDIUM_THRESHOLD",
    "TIER_PROFILES",
    "REGULATED_DOMAINS",
    "get_default_profile",
    "get_regulated_config",
    "create_behavior_config",
    "update_thresholds",
    # Memory Bridge (Story 4.1)
    "ImportanceLevel",
    "WorkflowDecision",
    "FixPattern",
    "MenuSelectionPattern",
    "MemoryEntry",
    "MemoryBridge",
    # BMB Thresholds (Story 2b.3)
    "EscalationAction",
    "EscalationResult",
    "ValidationMetrics",
    "BLOCKING_ERROR_THRESHOLD",
    "MAJOR_ISSUE_THRESHOLD",
    "COMPLIANCE_SCORE_THRESHOLD",
    "MAX_THRESHOLD_CHECK_MS",
    "check_blocking_errors",
    "check_major_issues",
    "check_compliance_score",
    "evaluate_all_thresholds",
    "is_within_thresholds",
    "performance_check",
    "BMBThresholdChecker",
    # Menu History (Story 2b-5)
    "SelectionSource",
    "MenuHistoryEntry",
    "MenuHistoryManager",
    "MAX_HISTORY_SIZE",
    "HISTORY_DIR_NAME",
    "MENU_HISTORY_SUBDIR",
    # Batch-Continue Logic (Story 2b-6, Tasks 1-3)
    "BatchMode",
    "BATCH_SIZE_BY_TIER",
    "BatchConfig",
    "get_batch_config",
    "BatchState",
    "BatchSummary",
    "BatchContinueManager",
    "CONTINUE_PATTERNS",
    "is_continue_menu",
    "AutoAllTracker",
    # Checkpoint Presenter (Story 2b-7, Tasks 1-7)
    "CheckpointFormat",
    "CONFIDENCE_THRESHOLDS",
    "CheckpointConfig",
    "get_format_for_confidence",
    "CheckpointPresenter",
    "MinimalCheckpoint",
    "generate_summary_line",
    # Task 4 - Summary Format
    "SummaryCheckpoint",
    "extract_key_decisions",
    "format_summary_checkpoint",
    # Task 5 - Full Audit Trail
    "OperationLogEntry",
    "AuditTrailCheckpoint",
    "generate_operation_log",
    "format_audit_trail_checkpoint",
    # Task 6 - Expandable Details
    "ExpansionState",
    "ExpandableDetails",
    "expand_checkpoint",
    "can_expand",
    "get_expansion_state",
    # Task 7 - Integration with Automation Controller
    "OrchestratorResult",
    "CheckpointOrchestrator",
    # Timeout Manager (Story 2b-9, Tasks 1-8)
    "TimeoutLevel",
    "TIMEOUT_SECONDS",
    "TimeoutConfig",
    "get_timeout_for_level",
    "TimeoutState",
    "TimeoutManager",
    # Task 3: Workflow Timeout
    "WorkflowTimeoutError",
    "enforce_workflow_timeout",
    # Task 4: Nested Timeout
    "NestedTimeoutError",
    "enforce_nested_timeout",
    # Task 5: Agent Timeout
    "AgentTimeoutError",
    "enforce_agent_timeout",
    # Task 6: State Preservation
    "PreservedTimeoutState",
    "preserve_state_on_timeout",
    "get_preserved_state",
    "clear_preserved_state",
    # Task 7: Timeout Logging
    "TimeoutLog",
    "log_timeout",
    "get_timeout_logs",
    "clear_timeout_logs",
    # Task 8: Context Managers
    "workflow_timeout",
    "nested_timeout",
    "agent_timeout",
]
