"""Checkpoint Presenter for Human Checkpoints.

This module provides functionality to present human checkpoints with
appropriate detail based on confidence scores:
- High (>=80%): Minimal format (1-2 line summary + confirm)
- Medium (50-79%): Summary format (key decisions + expandable)
- Low (<50%): Full Audit Trail (complete log + explicit approval)

Story: 2b-7 - Human Checkpoint Presentation
Epic: 2b - Menu Selection & Navigation

Acceptance Criteria:
- AC #1: High confidence (>=80%) uses minimal format with 1-2 line summary
- AC #2: Medium confidence (50-79%) uses summary format with key decisions
- AC #3: Low confidence (<50%) uses full audit trail with complete log
- AC #4: Expandable formats (MINIMAL, SUMMARY) include expand_details link/action

API Design Notes:
    This module provides two complementary interfaces:

    **Primary API** - Use for most cases:
        - CheckpointPresenter: Class-based presenter for formatting checkpoints
        - CheckpointOrchestrator: High-level orchestrator for automation integration

    **Helper Functions** - Low-level utilities:
        - get_format_for_confidence(): Determine format from confidence score
        - generate_summary_line(): Create summary from operations
        - extract_key_decisions(): Extract decisions from operations
        - generate_operation_log(): Create detailed operation log
        - format_summary_checkpoint(): Format SummaryCheckpoint dataclass
        - format_audit_trail_checkpoint(): Format AuditTrailCheckpoint dataclass
        - expand_checkpoint() / collapse_checkpoint(): Manage expansion state
        - can_expand() / get_expansion_state(): Query expansion capabilities

    The standalone format functions are provided for advanced use cases where
    direct control over individual formatting steps is needed. For standard
    checkpoint presentation, use CheckpointPresenter or CheckpointOrchestrator.

Examples:
    >>> from pcmrp_tools.bmad_automation.checkpoint_presenter import (
    ...     CheckpointFormat, get_format_for_confidence, CheckpointPresenter
    ... )
    >>> get_format_for_confidence(85.0)
    <CheckpointFormat.MINIMAL: 'minimal'>

    >>> presenter = CheckpointPresenter()
    >>> checkpoint = {"confidence": 90.0, "operations": [{"type": "validate"}]}
    >>> output = presenter.format_checkpoint(checkpoint)
    >>> "[Confirm]" in output
    True
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any


# =============================================================================
# Constants
# =============================================================================

# Confidence thresholds for format selection (immutable)
CONFIDENCE_THRESHOLDS: MappingProxyType[str, int] = MappingProxyType({
    "HIGH": 80,
    "MEDIUM": 50,
    "LOW": 0,
})


# =============================================================================
# Enums
# =============================================================================


class CheckpointFormat(Enum):
    """Format type for checkpoint presentation.

    Determines the level of detail shown in human checkpoints based on
    the confidence score of the automation system.

    Attributes:
        MINIMAL: 1-2 line summary for high confidence (>=80%)
        SUMMARY: Key decisions and expandable details for medium confidence (50-79%)
        FULL_AUDIT: Complete log with explicit approval for low confidence (<50%)
    """

    MINIMAL = "minimal"
    SUMMARY = "summary"
    FULL_AUDIT = "full_audit"


# =============================================================================
# Dataclasses
# =============================================================================


@dataclass
class CheckpointConfig:
    """Configuration for checkpoint presentation.

    Attributes:
        format: The presentation format to use (MINIMAL, SUMMARY, FULL_AUDIT)
        confidence: The confidence score that determined this format
        expandable: Whether the checkpoint can be expanded for more details
    """

    format: CheckpointFormat
    confidence: float
    expandable: bool


@dataclass
class MinimalCheckpoint:
    """Minimal checkpoint representation for high confidence scenarios.

    This dataclass represents the minimal format used when confidence is
    high (>=80%). It contains only a summary line and confirm action.

    Attributes:
        summary_line: A 1-2 line summary of operations performed
        confirm_action: The confirm button/action text (e.g., "[Confirm]")
    """

    summary_line: str
    confirm_action: str


# =============================================================================
# Format Selection Functions
# =============================================================================


def get_format_for_confidence(confidence: float) -> CheckpointFormat:
    """Determine the checkpoint format based on confidence score.

    This function implements the confidence-to-format mapping:
    - High (>=80%): MINIMAL format
    - Medium (50-79%): SUMMARY format
    - Low (<50%): FULL_AUDIT format

    Args:
        confidence: Confidence score as a percentage. Values outside [0, 100]
            are clamped to the valid range.

    Returns:
        CheckpointFormat appropriate for the confidence level

    Examples:
        >>> get_format_for_confidence(85.0)
        <CheckpointFormat.MINIMAL: 'minimal'>

        >>> get_format_for_confidence(65.0)
        <CheckpointFormat.SUMMARY: 'summary'>

        >>> get_format_for_confidence(25.0)
        <CheckpointFormat.FULL_AUDIT: 'full_audit'>

        >>> get_format_for_confidence(-10.0)  # Clamped to 0
        <CheckpointFormat.FULL_AUDIT: 'full_audit'>

        >>> get_format_for_confidence(150.0)  # Clamped to 100
        <CheckpointFormat.MINIMAL: 'minimal'>
    """
    # Clamp confidence to valid range [0, 100]
    clamped_confidence = max(0.0, min(100.0, confidence))

    if clamped_confidence >= CONFIDENCE_THRESHOLDS["HIGH"]:
        return CheckpointFormat.MINIMAL
    elif clamped_confidence >= CONFIDENCE_THRESHOLDS["MEDIUM"]:
        return CheckpointFormat.SUMMARY
    else:
        return CheckpointFormat.FULL_AUDIT


# =============================================================================
# Summary Line Generation
# =============================================================================


def generate_summary_line(operations: list[dict[str, Any]]) -> str:
    """Generate a concise summary line from a list of operations.

    Creates a 1-2 line summary that includes:
    - Operation count
    - Key action types
    - Aggregated information

    Args:
        operations: List of operation dictionaries with 'type' key

    Returns:
        A concise summary string (1-2 lines)

    Examples:
        >>> generate_summary_line([{"type": "validate"}, {"type": "transform"}])
        '2 operations: validate (1), transform (1)'

        >>> generate_summary_line([])
        'No operations to confirm'
    """
    if not operations:
        return "No operations to confirm"

    # Count operation types
    type_counts = Counter(op.get("type", "unknown") for op in operations)

    # Format the summary
    total = len(operations)
    type_summary = ", ".join(f"{t} ({c})" for t, c in type_counts.most_common(3))

    if len(type_counts) > 3:
        type_summary += f" +{len(type_counts) - 3} more"

    return f"{total} operation{'s' if total != 1 else ''}: {type_summary}"


# =============================================================================
# CheckpointPresenter Class
# =============================================================================


class CheckpointPresenter:
    """Presenter for human checkpoints with confidence-based formatting.

    This class formats checkpoint data for human review, adjusting the
    level of detail based on confidence scores:
    - High confidence: Minimal format (quick confirmation)
    - Medium confidence: Summary format (key decisions visible)
    - Low confidence: Full audit trail (complete transparency)

    All formats include an expand option for additional details.

    Examples:
        >>> presenter = CheckpointPresenter()
        >>> checkpoint = {"confidence": 90.0, "operations": [{"type": "validate"}]}
        >>> output = presenter.format_checkpoint(checkpoint)
        >>> "[Confirm]" in output
        True

        >>> checkpoint = {"confidence": 25.0, "operations": [], "log": ["Entry"]}
        >>> output = presenter.format_checkpoint(checkpoint)
        >>> "audit" in output.lower() or "log" in output.lower()
        True
    """

    def format_checkpoint(self, checkpoint: dict[str, Any]) -> str:
        """Format a checkpoint for human presentation.

        Selects the appropriate format based on confidence and delegates
        to the corresponding format method.

        Args:
            checkpoint: Dictionary containing checkpoint data with keys:
                - confidence: float (0-100), defaults to 0 if missing
                - operations: list of operation dicts
                - decisions: list of decision strings (for summary)
                - log: list of log entries (for full audit)

        Returns:
            Formatted string for human presentation
        """
        confidence = checkpoint.get("confidence", 0.0)
        format_type = get_format_for_confidence(confidence)

        if format_type == CheckpointFormat.MINIMAL:
            return self.format_minimal(checkpoint)
        elif format_type == CheckpointFormat.SUMMARY:
            return self.format_summary(checkpoint)
        else:
            return self.format_full_audit(checkpoint)

    def format_minimal(self, checkpoint: dict[str, Any]) -> str:
        """Format checkpoint in minimal format (1-2 lines).

        Used for high confidence scenarios (>=80%). Shows:
        - Brief summary line
        - Single [Confirm] action
        - [Expand] option for details

        Args:
            checkpoint: Checkpoint data dictionary

        Returns:
            Concise formatted string (1-2 lines)
        """
        operations = checkpoint.get("operations", [])
        summary = generate_summary_line(operations)

        return f"{summary} [Confirm] [Expand]"

    def format_summary(self, checkpoint: dict[str, Any]) -> str:
        """Format checkpoint in summary format (key decisions).

        Used for medium confidence scenarios (50-79%). Shows:
        - Summary line
        - Key decisions made
        - [Expand] option for full details

        Args:
            checkpoint: Checkpoint data dictionary

        Returns:
            Summary formatted string with key decisions
        """
        operations = checkpoint.get("operations", [])
        decisions = checkpoint.get("decisions", [])

        lines = [
            generate_summary_line(operations),
            "",
            "Key Decisions:",
        ]

        if decisions:
            for decision in decisions[:5]:  # Limit to 5 decisions
                lines.append(f"  - {decision}")
        else:
            lines.append("  - (No decisions recorded)")

        lines.append("")
        lines.append("[Confirm] [Expand]")

        return "\n".join(lines)

    def format_full_audit(self, checkpoint: dict[str, Any]) -> str:
        """Format checkpoint as full audit trail (complete log).

        Used for low confidence scenarios (<50%). Shows:
        - Complete summary
        - All operations
        - Full audit log
        - Explicit [Approve] action

        Args:
            checkpoint: Checkpoint data dictionary

        Returns:
            Comprehensive formatted string with full audit trail
        """
        operations = checkpoint.get("operations", [])
        log_entries = checkpoint.get("log", [])
        decisions = checkpoint.get("decisions", [])

        lines = [
            "=== FULL AUDIT TRAIL ===",
            "",
            generate_summary_line(operations),
            "",
        ]

        # Operations detail
        lines.append("Operations:")
        if operations:
            for i, op in enumerate(operations, 1):
                op_type = op.get("type", "unknown")
                op_target = op.get("target", "")
                op_result = op.get("result", "")
                detail = f"  {i}. {op_type}"
                if op_target:
                    detail += f" -> {op_target}"
                if op_result:
                    detail += f" [{op_result}]"
                lines.append(detail)
        else:
            lines.append("  (No operations)")

        lines.append("")

        # Decisions
        lines.append("Decisions:")
        if decisions:
            for decision in decisions:
                lines.append(f"  - {decision}")
        else:
            lines.append("  (No decisions recorded)")

        lines.append("")

        # Audit log
        lines.append("Audit Log:")
        if log_entries:
            for entry in log_entries:
                lines.append(f"  > {entry}")
        else:
            lines.append("  (No log entries)")

        lines.append("")
        lines.append("=== END AUDIT TRAIL ===")
        lines.append("")
        # Note: No [Expand] here - full audit is already at maximum detail
        # can_expand(FULL_AUDIT) returns False
        lines.append("[Approve]")

        return "\n".join(lines)


# =============================================================================
# Task 4: Summary Format Implementation (Story 2b-7)
# =============================================================================


@dataclass
class SummaryCheckpoint:
    """Summary checkpoint representation for medium-confidence operations.

    Used when confidence is between 50-79%. Shows key decisions with an
    option to expand for more details.

    Attributes:
        decisions: List of key decision strings describing operations
        details_available: Whether full details can be expanded
    """

    decisions: list[str]
    details_available: bool


def extract_key_decisions(operations: list[dict[str, Any]]) -> list[str]:
    """Extract key decisions from a list of operations.

    Transforms operation dictionaries into human-readable decision strings.
    Uses description field if available, otherwise constructs from type/target.

    Args:
        operations: List of operation dictionaries with optional keys:
            - type: Operation type (create, update, delete, etc.)
            - target: Target of the operation
            - description: Human-readable description
            - outcome: Result of the operation

    Returns:
        List of decision strings describing each operation

    Examples:
        >>> ops = [{"type": "create", "target": "module.py", "outcome": "success"}]
        >>> decisions = extract_key_decisions(ops)
        >>> len(decisions)
        1
        >>> "create" in decisions[0].lower() or "module.py" in decisions[0]
        True
    """
    decisions: list[str] = []

    for op in operations:
        # Prefer description if available
        if "description" in op and op["description"]:
            decision = op["description"]
        else:
            # Build decision from type and target
            op_type = op.get("type", "operation")
            target = op.get("target", "")

            if target:
                decision = f"{op_type.capitalize()} {target}"
            else:
                decision = f"{op_type.capitalize()}"

        # Append outcome if not success
        outcome = op.get("outcome", "")
        if outcome and outcome.lower() != "success":
            decision = f"{decision} ({outcome})"

        decisions.append(decision)

    return decisions


def format_summary_checkpoint(checkpoint: SummaryCheckpoint) -> str:
    """Format a summary checkpoint as a numbered list with expand option.

    Creates a formatted string showing key decisions as a numbered list.
    Includes [Expand Details] action if details are available.

    Args:
        checkpoint: SummaryCheckpoint with decisions and expandable flag

    Returns:
        Formatted string with numbered decisions and optional expand action

    Examples:
        >>> cp = SummaryCheckpoint(decisions=["A", "B"], details_available=True)
        >>> result = format_summary_checkpoint(cp)
        >>> "1." in result and "2." in result
        True
        >>> "[Expand Details]" in result
        True
    """
    if not checkpoint.decisions:
        return "No decisions recorded"

    lines: list[str] = ["Key Decisions:"]
    for i, decision in enumerate(checkpoint.decisions, 1):
        lines.append(f"{i}. {decision}")

    if checkpoint.details_available:
        lines.append("")
        lines.append("[Expand Details]")

    return "\n".join(lines)


# =============================================================================
# Task 5: Full Audit Trail Format Implementation (Story 2b-7)
# =============================================================================


@dataclass
class OperationLogEntry:
    """Single entry in an operation log for full audit trail.

    Represents a complete record of a single operation including
    timestamp, details, and outcome.

    Attributes:
        timestamp: When the operation occurred
        operation_type: Type of operation (create, update, delete, etc.)
        target: Target of the operation (file, resource, etc.)
        details: Additional details about the operation
        outcome: Result of the operation (success, failed, etc.)
    """

    timestamp: datetime
    operation_type: str
    target: str
    details: str
    outcome: str


@dataclass
class AuditTrailCheckpoint:
    """Full audit trail checkpoint for low-confidence operations.

    Used when confidence is below 50%. Provides complete transparency
    with all operation details and requires explicit approval.

    Attributes:
        operation_log: List of OperationLogEntry objects
        approval_required: Whether explicit approval is required
    """

    operation_log: list[OperationLogEntry]
    approval_required: bool


def generate_operation_log(operations: list[dict[str, Any]]) -> str:
    """Generate a formatted operation log string from operations.

    Creates a detailed log string with timestamps, operation details,
    and outcomes for each operation.

    Args:
        operations: List of operation dictionaries with optional keys:
            - type: Operation type
            - target: Target of the operation
            - timestamp: ISO format timestamp or datetime string
            - description: Additional details
            - outcome: Result of the operation

    Returns:
        Formatted log string with timestamps, details, and outcomes

    Examples:
        >>> ops = [{"type": "create", "target": "file.py", "outcome": "success"}]
        >>> log = generate_operation_log(ops)
        >>> "create" in log.lower() or "file.py" in log
        True
    """
    if not operations:
        return "No operations logged"

    lines: list[str] = ["Operation Log:", ""]

    for i, op in enumerate(operations, 1):
        timestamp = op.get("timestamp", "N/A")
        op_type = op.get("type", "unknown").upper()
        target = op.get("target", "N/A")
        outcome = op.get("outcome", "unknown")
        details = op.get("description", "")

        # Format timestamp for display
        if isinstance(timestamp, str) and "T" in timestamp:
            # Extract time portion from ISO format
            time_part = timestamp.split("T")[1][:8]
        elif timestamp != "N/A":
            time_part = str(timestamp)
        else:
            time_part = "N/A"

        line = f"{i}. [{time_part}] {op_type} {target} - {outcome}"
        if details:
            line += f"\n   Details: {details}"

        lines.append(line)

    return "\n".join(lines)


def format_audit_trail_checkpoint(checkpoint: AuditTrailCheckpoint) -> str:
    """Format a full audit trail checkpoint with explicit approval requirement.

    Creates a comprehensive formatted string showing all operation details
    with explicit approval action (not just confirm).

    Args:
        checkpoint: AuditTrailCheckpoint with operation log and approval flag

    Returns:
        Formatted string with complete log and approval action

    Examples:
        >>> cp = AuditTrailCheckpoint(operation_log=[], approval_required=True)
        >>> result = format_audit_trail_checkpoint(cp)
        >>> "APPROVE" in result.upper()
        True
    """
    lines: list[str] = ["Full Audit Trail", "=" * 40, ""]

    if checkpoint.operation_log:
        for entry in checkpoint.operation_log:
            time_str = entry.timestamp.strftime("%H:%M:%S")
            line = f"[{time_str}] {entry.operation_type.upper()} {entry.target} - {entry.outcome}"
            lines.append(line)
            if entry.details:
                lines.append(f"   Details: {entry.details}")
    else:
        lines.append("No operations recorded")

    lines.append("")
    lines.append("=" * 40)

    if checkpoint.approval_required:
        lines.append("Approval Required: [APPROVE] [REJECT]")
    else:
        lines.append("Review complete")

    return "\n".join(lines)


# =============================================================================
# Task 6: Expandable Details Implementation (Story 2b-7)
# =============================================================================


class ExpansionState(Enum):
    """State of an expandable checkpoint.

    Tracks whether a checkpoint's details are currently visible or hidden.

    Attributes:
        COLLAPSED: Details are hidden, showing summary view
        EXPANDED: Full details are visible
    """

    COLLAPSED = "collapsed"
    EXPANDED = "expanded"


@dataclass
class ExpandableDetails:
    """Expandable details container for checkpoint expansion.

    Holds both collapsed and expanded views with state tracking
    for UI rendering.

    Attributes:
        collapsed_view: Summary view shown when collapsed
        expanded_view: Full details shown when expanded
        state: Current expansion state (defaults to COLLAPSED)
    """

    collapsed_view: str
    expanded_view: str
    state: ExpansionState = ExpansionState.COLLAPSED


def expand_checkpoint(details: ExpandableDetails) -> str:
    """Expand a checkpoint to reveal full details.

    Updates the expansion state and returns the expanded content.
    If already expanded, returns the expanded view without state change.

    Args:
        details: ExpandableDetails container to expand

    Returns:
        The expanded view content

    Examples:
        >>> d = ExpandableDetails("Summary", "Full details", ExpansionState.COLLAPSED)
        >>> result = expand_checkpoint(d)
        >>> d.state == ExpansionState.EXPANDED
        True
        >>> result
        'Full details'
    """
    details.state = ExpansionState.EXPANDED
    return details.expanded_view


def collapse_checkpoint(details: ExpandableDetails) -> str:
    """Collapse a checkpoint to show summary view.

    Updates the expansion state and returns the collapsed content.
    If already collapsed, returns the collapsed view without state change.

    Args:
        details: ExpandableDetails container to collapse

    Returns:
        The collapsed view content

    Examples:
        >>> d = ExpandableDetails("Summary", "Full details", ExpansionState.EXPANDED)
        >>> result = collapse_checkpoint(d)
        >>> d.state == ExpansionState.COLLAPSED
        True
        >>> result
        'Summary'
    """
    details.state = ExpansionState.COLLAPSED
    return details.collapsed_view


def can_expand(format_type: CheckpointFormat) -> bool:
    """Check if a checkpoint format can be expanded to full audit.

    MINIMAL and SUMMARY formats can expand to FULL_AUDIT.
    FULL_AUDIT format is already at maximum detail and cannot expand.

    Args:
        format_type: The checkpoint format to check

    Returns:
        True if the format can be expanded, False otherwise

    Examples:
        >>> can_expand(CheckpointFormat.MINIMAL)
        True
        >>> can_expand(CheckpointFormat.SUMMARY)
        True
        >>> can_expand(CheckpointFormat.FULL_AUDIT)
        False
    """
    return format_type in (CheckpointFormat.MINIMAL, CheckpointFormat.SUMMARY)


def get_expansion_state(details: ExpandableDetails) -> ExpansionState:
    """Get the current expansion state of a checkpoint.

    Allows UI code to check current state for rendering decisions.

    Args:
        details: ExpandableDetails container to check

    Returns:
        Current ExpansionState (COLLAPSED or EXPANDED)

    Examples:
        >>> d = ExpandableDetails("Summary", "Full", ExpansionState.COLLAPSED)
        >>> get_expansion_state(d)
        <ExpansionState.COLLAPSED: 'collapsed'>
    """
    return details.state


# =============================================================================
# Task 7: Integration with Automation Controller (Story 2b-7)
# =============================================================================


@dataclass
class OrchestratorResult:
    """Result from checkpoint orchestration.

    Contains the formatted output along with metadata about the
    format used and expansion capabilities.

    Attributes:
        formatted_output: The formatted checkpoint string for display
        format_used: The CheckpointFormat that was selected
        confidence_score: The confidence score that determined format
        expandable: Whether this checkpoint can be expanded for more details
    """

    formatted_output: str
    format_used: CheckpointFormat
    confidence_score: float
    expandable: bool


class CheckpointOrchestrator:
    """Orchestrator for checkpoint presentation with format selection.

    This class integrates confidence-based format selection with
    checkpoint presentation and expansion handling. It serves as
    the primary interface for the automation controller.

    The orchestrator:
    1. Receives checkpoint data with confidence score
    2. Selects appropriate format based on confidence
    3. Presents formatted checkpoint to user
    4. Handles expansion requests

    Examples:
        >>> orchestrator = CheckpointOrchestrator()
        >>> checkpoint = {"confidence": 85.0, "operations": [{"type": "validate"}]}
        >>> result = orchestrator.present_checkpoint(checkpoint)
        >>> result.format_used
        <CheckpointFormat.MINIMAL: 'minimal'>

        >>> orchestrator = CheckpointOrchestrator()
        >>> checkpoint = {"confidence": 30.0, "operations": []}
        >>> result = orchestrator.present_checkpoint(checkpoint)
        >>> result.format_used
        <CheckpointFormat.FULL_AUDIT: 'full_audit'>
    """

    def __init__(self) -> None:
        """Initialize the CheckpointOrchestrator with a presenter."""
        self._presenter = CheckpointPresenter()

    def present_checkpoint(self, checkpoint_data: dict[str, Any]) -> OrchestratorResult:
        """Present a checkpoint with confidence-based format selection.

        Receives checkpoint data including a confidence score, selects
        the appropriate format, and returns the formatted output with
        metadata.

        Args:
            checkpoint_data: Dictionary containing checkpoint data with keys:
                - confidence: float (0-100), defaults to 0.0 if missing
                - operations: list of operation dicts
                - decisions: list of decision strings (for summary)
                - log: list of log entries (for full audit)
                - source: optional source identifier (validation, batch, etc.)

        Returns:
            OrchestratorResult with formatted output and metadata

        Examples:
            >>> orchestrator = CheckpointOrchestrator()
            >>> result = orchestrator.present_checkpoint({"confidence": 90.0})
            >>> result.format_used == CheckpointFormat.MINIMAL
            True
        """
        confidence = float(checkpoint_data.get("confidence", 0.0))
        format_type = get_format_for_confidence(confidence)
        formatted_output = self._presenter.format_checkpoint(checkpoint_data)
        expandable = can_expand(format_type)

        return OrchestratorResult(
            formatted_output=formatted_output,
            format_used=format_type,
            confidence_score=confidence,
            expandable=expandable,
        )

    def handle_expansion(self, checkpoint_data: dict[str, Any]) -> str:
        """Handle expansion request to reveal full audit trail.

        When a user requests expansion from minimal or summary format,
        this method generates the full audit trail view.

        Args:
            checkpoint_data: Original checkpoint data dictionary

        Returns:
            Full audit trail formatted string

        Examples:
            >>> orchestrator = CheckpointOrchestrator()
            >>> checkpoint = {"confidence": 90.0, "operations": []}
            >>> expanded = orchestrator.handle_expansion(checkpoint)
            >>> "AUDIT" in expanded.upper()
            True
        """
        # Always return full audit format when expanding
        return self._presenter.format_full_audit(checkpoint_data)
