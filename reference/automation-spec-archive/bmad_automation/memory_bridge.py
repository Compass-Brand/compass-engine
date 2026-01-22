"""Memory Bridge component for writing workflow decisions to Forgetful memory.

This module implements the Memory Bridge which writes workflow decisions
and outcomes to Forgetful memory for cross-session learning.

Story 4.1: Writing Workflow Decisions to Memory
Story 4.3 Task 6: Integration with Graceful Degradation
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from enum import IntEnum

from pcmrp_tools.bmad_automation.memory_degradation import (
    AvailabilityResult,
    DegradedQueryResult,
    MemoryAvailabilityChecker,
    MemoryAvailabilityStatus,
    MemorySaveQueue,
    MemoryStatus,
    NotificationManager,
)


class ImportanceLevel(IntEnum):
    """Importance levels for memory entries matching Forgetful schema.

    Higher numbers indicate more important memories that should be
    preserved longer and prioritized in search results.
    """

    ARCHITECTURAL = 10  # Major architectural decisions
    ARCHITECTURAL_LOW = 9  # Important architectural decisions
    PATTERN_HIGH = 8  # High-value technical patterns
    PATTERN = 7  # Standard technical patterns
    MILESTONE = 6  # Workflow milestones
    SELECTION = 5  # Menu selection patterns


@dataclass
class WorkflowDecision:
    """Captures a decision made during workflow execution.

    Attributes:
        decision_type: Category of decision ("architectural", "technical", "process")
        description: What was decided
        rationale: Why this decision was made
        outcome: Result of the decision (optional)
        importance: How important this decision is for future reference
    """

    decision_type: str  # "architectural", "technical", "process"
    description: str
    rationale: str
    outcome: Optional[str] = None
    importance: ImportanceLevel = ImportanceLevel.PATTERN


@dataclass
class FixPattern:
    """Records a successful fix pattern for validation errors.

    Attributes:
        error_signature: Unique identifier for the error type
        solution: How the error was resolved
        workflow_step: Which workflow step this occurred in
        validation_type: Type of validation that caught the error
        success_rate: Historical success rate of this fix (0.0-1.0)
    """

    error_signature: str  # Unique identifier for the error type
    solution: str
    workflow_step: str
    validation_type: str
    success_rate: float = 1.0  # Initially 100%


@dataclass
class MenuSelectionPattern:
    """Records a menu selection pattern for future reference.

    Attributes:
        context: The context in which the selection was made
        selection: What was selected
        outcome: Whether the selection led to success
        success_signal: Numeric indicator of outcome quality (0.0-1.0)
    """

    context: str
    selection: str
    outcome: str
    success_signal: float = 1.0


@dataclass
class MemoryEntry:
    """Memory entry matching Forgetful MCP schema.

    Attributes:
        title: Short title (<200 chars)
        content: Memory content (<2000 chars)
        context: Why this matters (<500 chars)
        keywords: Search keywords (max 10)
        tags: Categorization tags (max 10)
        importance: Importance level (1-10)
        project_ids: Associated project IDs
        workflow_id: Optional workflow identifier for traceability
    """

    title: str
    content: str
    context: str
    keywords: List[str]
    tags: List[str]
    importance: int
    project_ids: List[int]
    workflow_id: Optional[str] = None


class MemoryBridge:
    """Bridge for writing workflow decisions to Forgetful memory.

    This class provides methods to:
    - Extract significant decisions from workflow context
    - Create memories for fix patterns
    - Record menu selection patterns
    - Summarize content to fit memory limits
    - Write memories to Forgetful MCP
    - Handle graceful degradation when memory is unavailable

    Attributes:
        project_id: The project ID to associate memories with
        workflow_id: The workflow ID for traceability
        record_selections: Whether to record menu selection patterns
        mcp_client: Optional MCP client for writing memories
        availability_checker: Checker for memory system availability
        save_queue: Queue for storing memories during degraded mode
        notification_manager: Manager for user notifications
    """

    def __init__(
        self,
        project_id: int,
        workflow_id: str,
        record_selections: bool = False,
        mcp_client: Optional[Callable] = None,
    ):
        """Initialize the Memory Bridge.

        Args:
            project_id: The project ID to associate memories with
            workflow_id: The workflow ID for traceability
            record_selections: Whether to record menu selection patterns
            mcp_client: Optional MCP client callable for writing memories
        """
        self.project_id = project_id
        self.workflow_id = workflow_id
        self.record_selections = record_selections
        self.mcp_client = mcp_client

        # Degradation components (Task 6)
        self.availability_checker = MemoryAvailabilityChecker()
        self.save_queue = MemorySaveQueue()
        self.notification_manager = NotificationManager()
        self._is_degraded = False

    @property
    def is_degraded(self) -> bool:
        """Check if the memory bridge is currently in degraded mode.

        Returns:
            True if operating in degraded mode, False otherwise
        """
        return self._is_degraded

    def get_queue_size(self) -> int:
        """Get the number of items currently in the save queue.

        Returns:
            Number of queued items
        """
        return len(self.save_queue.get_queue())

    def query(
        self, query_text: str, context: str
    ) -> Union[Any, DegradedQueryResult]:
        """Query memory with graceful degradation support.

        Checks availability before executing query. If degraded,
        returns a DegradedQueryResult and notifies user once.

        Args:
            query_text: The query string to execute
            context: Context for the query

        Returns:
            Query results if available, DegradedQueryResult if degraded
        """
        # Check availability
        status = self.availability_checker.check_availability(self.mcp_client)

        if status != MemoryAvailabilityStatus.AVAILABLE:
            self._is_degraded = True
            self.notification_manager.notify_user_once()
            return DegradedQueryResult()

        self._is_degraded = False

        # Execute query
        if self.mcp_client is None:
            return DegradedQueryResult(reason="mcp_client_not_configured")

        # If mcp_client is a callable (for sync usage), call it appropriately
        if hasattr(self.mcp_client, "execute_forgetful_tool"):
            return self.mcp_client.execute_forgetful_tool(
                "query_memory",
                {"query": query_text, "query_context": context},
            )
        return DegradedQueryResult(reason="invalid_client_type")

    async def save(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save memory with graceful degradation support.

        Checks availability before saving. If degraded, queues the
        memory for later saving.

        Args:
            memory_data: The memory data to save

        Returns:
            Save result or queued status
        """
        # Check availability
        status = self.availability_checker.check_availability(self.mcp_client)

        if status != MemoryAvailabilityStatus.AVAILABLE:
            self._is_degraded = True
            self.notification_manager.notify_user_once()
            self.save_queue.add_to_queue(memory_data)
            return {"status": "queued"}

        self._is_degraded = False

        # Execute save
        if self.mcp_client is None:
            raise RuntimeError("MCP client not configured")

        return await self.mcp_client("create_memory", memory_data)

    async def trigger_health_check(self) -> AvailabilityResult:
        """Trigger a health check and process queue on recovery.

        Checks the current availability status. If recovering from
        degraded mode to available, processes the queued saves.

        Returns:
            AvailabilityResult with current status
        """
        # Create async client wrapper for availability check
        async def check_client():
            if self.mcp_client is None:
                raise RuntimeError("MCP client not configured")
            return await self.mcp_client("get_current_user", {})

        result = await self.availability_checker.check_availability_async(check_client)

        # Check if we're recovering from degraded mode
        was_degraded = self._is_degraded

        if result.status == MemoryStatus.AVAILABLE:
            self._is_degraded = False

            # If recovering from degraded mode, process queued saves
            if was_degraded and len(self.save_queue.get_queue()) > 0:
                # Create save wrapper
                async def save_wrapper(memory_data: Dict[str, Any]):
                    return await self.mcp_client("create_memory", memory_data)

                await self.save_queue.process_queued_saves(save_wrapper)

                # Reset notification state for next degradation
                self.notification_manager.reset()
        else:
            self._is_degraded = True

        return result

    def extract_decisions(
        self, workflow_context: Dict[str, Any]
    ) -> List[WorkflowDecision]:
        """Extract significant decisions from workflow context.

        Args:
            workflow_context: Dictionary containing workflow execution data

        Returns:
            List of WorkflowDecision objects for significant decisions
        """
        decisions: List[WorkflowDecision] = []

        # Get decisions from context, default to empty list
        raw_decisions = workflow_context.get("decisions", [])

        for raw in raw_decisions:
            # Skip invalid decisions missing required fields
            if not all(key in raw for key in ("type", "description", "rationale")):
                continue

            # Map decision type to importance level
            decision_type = raw["type"]
            importance = self._get_importance_for_type(decision_type)

            decision = WorkflowDecision(
                decision_type=decision_type,
                description=raw["description"],
                rationale=raw["rationale"],
                outcome=raw.get("outcome"),
                importance=importance,
            )
            decisions.append(decision)

        return decisions

    def _get_importance_for_type(self, decision_type: str) -> ImportanceLevel:
        """Map decision type to importance level.

        Args:
            decision_type: The type of decision

        Returns:
            Appropriate ImportanceLevel for the decision type
        """
        importance_map = {
            "architectural": ImportanceLevel.ARCHITECTURAL,
            "technical": ImportanceLevel.PATTERN,
            "process": ImportanceLevel.PATTERN,
        }
        return importance_map.get(decision_type, ImportanceLevel.PATTERN)

    def create_fix_pattern_memory(self, pattern: FixPattern) -> MemoryEntry:
        """Create memory entry for a successful fix pattern.

        Args:
            pattern: The fix pattern to create a memory for

        Returns:
            MemoryEntry ready to be written to Forgetful
        """
        # Generate title (max 200 chars)
        title = f"Fix Pattern: {pattern.error_signature}"
        if len(title) > 200:
            title = title[:197] + "..."

        # Generate content with error signature, solution, and workflow context
        content = (
            f"Error Signature: {pattern.error_signature}\n\n"
            f"Solution: {pattern.solution}\n\n"
            f"Workflow Step: {pattern.workflow_step}\n"
            f"Validation Type: {pattern.validation_type}\n"
            f"Success Rate: {pattern.success_rate:.0%}"
        )

        # Generate context
        context = (
            f"Fix pattern discovered during {pattern.validation_type} validation "
            f"that resolved '{pattern.error_signature[:50]}...' errors."
            if len(pattern.error_signature) > 50
            else f"Fix pattern discovered during {pattern.validation_type} validation "
            f"that resolved '{pattern.error_signature}' errors."
        )
        if len(context) > 500:
            context = context[:497] + "..."

        # Generate keywords from error signature
        keywords = self._generate_keywords_from_error(pattern.error_signature)

        # Generate tags
        tags = [
            "fix_pattern",
            pattern.validation_type,
            f"workflow:{self.workflow_id}",
        ]
        # Limit tags to 10
        tags = tags[:10]

        return MemoryEntry(
            title=title,
            content=content,
            context=context,
            keywords=keywords,
            tags=tags,
            importance=ImportanceLevel.PATTERN,
            project_ids=[self.project_id],
            workflow_id=self.workflow_id,
        )

    def _generate_keywords_from_error(self, error_signature: str) -> List[str]:
        """Generate searchable keywords from error signature.

        Args:
            error_signature: The error signature string

        Returns:
            List of keywords (max 10)
        """
        # Split on common delimiters and clean up
        import re

        parts = re.split(r"[:\-_\s]+", error_signature)
        # Filter out empty strings and very short parts
        keywords = [p.lower() for p in parts if len(p) >= 2]
        # Add the full signature as a keyword if short enough
        if len(error_signature) <= 50:
            keywords.insert(0, error_signature.lower())
        # Deduplicate while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        # Limit to 10 keywords
        return unique_keywords[:10]

    def record_selection_pattern(
        self, context: str, selection: str, outcome: str
    ) -> Optional[MemoryEntry]:
        """Optionally record menu selection pattern.

        Args:
            context: The context in which the selection was made
            selection: What was selected
            outcome: The result of the selection

        Returns:
            MemoryEntry if recording is enabled, None otherwise
        """
        # Return None if recording is disabled
        if not self.record_selections:
            return None

        # Generate title (max 200 chars)
        title = f"Selection Pattern: {selection}"
        if len(title) > 200:
            title = title[:197] + "..."

        # Generate content
        content = (
            f"Context: {context}\n\n"
            f"Selection: {selection}\n\n"
            f"Outcome: {outcome}"
        )

        # Generate memory context
        memory_context = (
            f"Menu selection pattern recorded during workflow execution. "
            f"This selection led to the outcome: {outcome[:100]}..."
            if len(outcome) > 100
            else f"Menu selection pattern recorded during workflow execution. "
            f"This selection led to the outcome: {outcome}"
        )
        if len(memory_context) > 500:
            memory_context = memory_context[:497] + "..."

        # Generate keywords from context and selection
        keywords = self._generate_selection_keywords(context, selection)

        # Generate tags
        tags = [
            "selection_pattern",
            f"workflow:{self.workflow_id}",
        ]
        tags = tags[:10]

        return MemoryEntry(
            title=title,
            content=content,
            context=memory_context,
            keywords=keywords,
            tags=tags,
            importance=ImportanceLevel.SELECTION,
            project_ids=[self.project_id],
            workflow_id=self.workflow_id,
        )

    def _generate_selection_keywords(
        self, context: str, selection: str
    ) -> List[str]:
        """Generate keywords from context and selection.

        Args:
            context: The context string
            selection: The selection string

        Returns:
            List of keywords (max 10)
        """
        import re

        # Combine context and selection for keyword extraction
        combined = f"{context} {selection}"
        # Split on whitespace and common punctuation
        words = re.split(r"[\s\[\]\(\)\-_:,]+", combined)
        # Filter and lowercase
        keywords = [w.lower() for w in words if len(w) >= 3]
        # Deduplicate while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        # Limit to 10 keywords
        return unique_keywords[:10]

    def summarize_content(self, content: str, max_length: int = 2000) -> str:
        """Summarize content to fit atomic memory limit.

        Preserves key information sections (Decision, Rationale, Outcome,
        Error Signature, Solution) when present.

        Args:
            content: The content to summarize
            max_length: Maximum allowed length (default 2000)

        Returns:
            Content truncated/summarized to fit the limit
        """
        # Handle empty content
        if not content:
            return ""

        # If content is within limit, return unchanged
        if len(content) <= max_length:
            return content

        # Key sections to preserve (in priority order)
        key_sections = [
            "Decision:",
            "Rationale:",
            "Outcome:",
            "Error Signature:",
            "Solution:",
            "Context:",
            "Selection:",
        ]

        # Try to preserve key sections
        preserved_parts = []
        remaining_content = content

        for section in key_sections:
            if section in content:
                # Find the section and extract it (up to next section or double newline)
                start_idx = content.find(section)
                if start_idx != -1:
                    # Find the end of this section (next section or double newline)
                    end_idx = len(content)
                    for other_section in key_sections:
                        if other_section != section:
                            other_idx = content.find(other_section, start_idx + len(section))
                            if other_idx != -1 and other_idx < end_idx:
                                end_idx = other_idx

                    # Also check for double newline as section delimiter
                    double_newline_idx = content.find("\n\n", start_idx + len(section))
                    if double_newline_idx != -1 and double_newline_idx < end_idx:
                        end_idx = double_newline_idx

                    section_text = content[start_idx:end_idx].strip()
                    if section_text and section_text not in preserved_parts:
                        preserved_parts.append(section_text)

        # Build summarized content from preserved parts
        if preserved_parts:
            summarized = "\n\n".join(preserved_parts)
            # Add ellipsis if we had to truncate
            if len(summarized) > max_length - 3:
                summarized = summarized[: max_length - 3] + "..."
            elif len(content) > len(summarized):
                summarized += "\n\n[Content summarized...]"
                if len(summarized) > max_length - 3:
                    summarized = summarized[: max_length - 3] + "..."
            return summarized

        # No key sections found, simple truncation
        return content[: max_length - 3] + "..."

    async def write_memory(self, entry: MemoryEntry) -> Dict[str, Any]:
        """Write memory to Forgetful MCP.

        Args:
            entry: The memory entry to write

        Returns:
            Response from Forgetful MCP

        Raises:
            RuntimeError: If MCP client is not configured
        """
        if self.mcp_client is None:
            raise RuntimeError("MCP client not configured")

        # Summarize content if needed
        content = self.summarize_content(entry.content)

        # Ensure workflow_id is in tags for traceability
        tags = list(entry.tags)
        if entry.workflow_id and not any(entry.workflow_id in tag for tag in tags):
            tags.append(f"workflow:{entry.workflow_id}")
        # Limit tags to 10
        tags = tags[:10]

        # Prepare arguments for Forgetful MCP
        arguments = {
            "title": entry.title,
            "content": content,
            "context": entry.context,
            "keywords": entry.keywords[:10],  # Max 10 keywords
            "tags": tags,
            "importance": entry.importance,
            "project_ids": entry.project_ids,
        }

        # Call MCP client
        return await self.mcp_client("create_memory", arguments)

    async def process_workflow_outcome(
        self,
        workflow_context: Dict[str, Any],
        fix_patterns: Optional[List[FixPattern]] = None,
        record_selections: bool = False,
    ) -> Dict[str, Any]:
        """Main entry point for processing workflow outcomes.

        Orchestrates the extraction of decisions, creation of memories,
        and writing to Forgetful MCP.

        Args:
            workflow_context: The workflow execution context
            fix_patterns: Optional list of fix patterns to record
            record_selections: Whether to record selection patterns

        Returns:
            Summary of memories created with counts
        """
        decisions_written = 0
        fix_patterns_written = 0
        selections_written = 0

        # 1. Extract and write decision memories
        decisions = self.extract_decisions(workflow_context)
        for decision in decisions:
            entry = self._create_decision_memory(decision)
            await self.write_memory(entry)
            decisions_written += 1

        # 2. Write fix pattern memories
        if fix_patterns:
            for pattern in fix_patterns:
                entry = self.create_fix_pattern_memory(pattern)
                await self.write_memory(entry)
                fix_patterns_written += 1

        # 3. Optionally record selection patterns
        if record_selections:
            # Temporarily enable recording
            original_setting = self.record_selections
            self.record_selections = True

            raw_selections = workflow_context.get("selections", [])
            for sel in raw_selections:
                if all(key in sel for key in ("context", "selection", "outcome")):
                    entry = self.record_selection_pattern(
                        context=sel["context"],
                        selection=sel["selection"],
                        outcome=sel["outcome"],
                    )
                    if entry:
                        await self.write_memory(entry)
                        selections_written += 1

            # Restore original setting
            self.record_selections = original_setting

        # Return summary
        total_written = decisions_written + fix_patterns_written + selections_written
        return {
            "decisions_written": decisions_written,
            "fix_patterns_written": fix_patterns_written,
            "selections_written": selections_written,
            "total_written": total_written,
        }

    def _create_decision_memory(self, decision: WorkflowDecision) -> MemoryEntry:
        """Create memory entry for a workflow decision.

        Args:
            decision: The workflow decision to create a memory for

        Returns:
            MemoryEntry ready to be written to Forgetful
        """
        # Generate title (max 200 chars)
        title = f"Decision: {decision.description}"
        if len(title) > 200:
            title = title[:197] + "..."

        # Generate content
        content = (
            f"Decision: {decision.description}\n\n"
            f"Rationale: {decision.rationale}"
        )
        if decision.outcome:
            content += f"\n\nOutcome: {decision.outcome}"

        # Generate context
        context = (
            f"Workflow decision ({decision.decision_type}) made during workflow "
            f"execution. This decision may inform future similar workflows."
        )

        # Generate keywords
        import re
        words = re.split(r"[\s\-_:,]+", decision.description)
        keywords = [w.lower() for w in words if len(w) >= 3][:10]

        # Generate tags
        tags = [
            "decision",
            decision.decision_type,
            f"workflow:{self.workflow_id}",
        ]

        return MemoryEntry(
            title=title,
            content=content,
            context=context,
            keywords=keywords,
            tags=tags,
            importance=int(decision.importance),
            project_ids=[self.project_id],
            workflow_id=self.workflow_id,
        )
