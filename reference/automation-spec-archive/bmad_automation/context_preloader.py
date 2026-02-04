"""Context Pre-Loader for BMAD Automation.

This module provides functionality to pre-load relevant memories from
Forgetful MCP before workflow execution, enabling context-aware agent behavior.

Component: Context Pre-Loader (Design Spec S10)
Tier: 2 (Standalone - no dependencies on other Tier 2 components)
"""

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Union


logger = logging.getLogger(__name__)


# Configuration Constants
FORGETFUL_TIMEOUT_MS = 300  # Total timeout for Forgetful query
RETRY_COUNT = 3
RETRY_INTERVAL_MS = 100
CONTEXT_LIMIT_CHARS = 8000  # Max chars for context injection
CACHE_TTL_SECONDS = int(os.environ.get("CONTEXT_CACHE_TTL_SECONDS", "300"))  # Default: 5 minutes
CACHE_DIR = "_bmad-output/.context-cache"


class PreloadStatus(Enum):
    """Status of the context pre-load operation."""

    SUCCESS = "success"
    DEGRADED = "degraded"
    EMPTY = "empty"


@dataclass
class MemoryItem:
    """Represents a single memory item from Forgetful.

    Attributes:
        id: Unique identifier of the memory.
        title: Short, searchable title of the memory.
        content: The memory content (max 2000 chars per Forgetful spec).
        importance: Priority level (1-10, higher = more important).
        keywords: List of keywords for semantic clustering.
    """

    id: int
    title: str
    content: str
    importance: int
    keywords: list[str] = field(default_factory=list)


@dataclass
class ContextPreloadResult:
    """Result of a context pre-loading operation.

    Attributes:
        status: The status of the preload operation.
        memories: List of retrieved memory items.
        degraded: Whether the result is in degraded mode (MCP unavailable).
        reason: Reason for degraded status or empty result.
        cached_at: ISO timestamp when the result was cached.
    """

    status: PreloadStatus
    memories: list[MemoryItem] = field(default_factory=list)
    degraded: bool = False
    reason: Optional[str] = None
    cached_at: Optional[str] = None

    @classmethod
    def success(cls, memories: list[MemoryItem]) -> "ContextPreloadResult":
        """Create a successful preload result with memories.

        Args:
            memories: List of memory items retrieved from Forgetful.

        Returns:
            ContextPreloadResult with SUCCESS status and memories.
        """
        return cls(
            status=PreloadStatus.SUCCESS,
            memories=memories,
            degraded=False,
            cached_at=datetime.now().isoformat(),
        )

    @classmethod
    def create_degraded(cls, reason: str) -> "ContextPreloadResult":
        """Create a degraded preload result when MCP is unavailable.

        Args:
            reason: Description of why the preload failed.

        Returns:
            ContextPreloadResult with DEGRADED status and empty memories.
        """
        return cls(
            status=PreloadStatus.DEGRADED,
            memories=[],
            degraded=True,
            reason=reason,
        )

    @classmethod
    def empty(cls) -> "ContextPreloadResult":
        """Create an empty preload result when no memories match.

        Returns:
            ContextPreloadResult with EMPTY status.
        """
        return cls(
            status=PreloadStatus.EMPTY,
            memories=[],
            degraded=False,
        )


class ForgetfulTimeoutError(Exception):
    """Raised when Forgetful MCP query times out."""

    pass


class ForgetfulConnectionError(Exception):
    """Raised when connection to Forgetful MCP fails."""

    pass


def _call_forgetful_mcp(
    query: str,
    project_ids: list[int],
    timeout_ms: int = FORGETFUL_TIMEOUT_MS,
) -> dict:
    """Internal function to call Forgetful MCP.

    This is a placeholder that will be replaced/mocked in production.
    The actual implementation would use the MCP client to call
    mcp__forgetful__execute_forgetful_tool.

    Args:
        query: Search query string for memories.
        project_ids: List of project IDs to filter by.
        timeout_ms: Timeout in milliseconds.

    Returns:
        Dict containing 'memories' list and 'total' count.

    Raises:
        TimeoutError: If the query times out.
        ConnectionError: If MCP is unavailable.
    """
    # This is a stub that will be mocked in tests
    # In production, this would call the actual MCP tool
    raise NotImplementedError(
        "_call_forgetful_mcp must be mocked in tests or "
        "replaced with actual MCP client implementation"
    )


def query_forgetful_memories(
    project_ids: list[int],
    keywords: list[str],
) -> list[MemoryItem]:
    """Query Forgetful MCP for relevant memories.

    Args:
        project_ids: List of project IDs to filter memories by.
        keywords: List of keywords to search for.

    Returns:
        List of MemoryItem objects matching the query.

    Raises:
        ForgetfulTimeoutError: If the query times out after retries.
        ForgetfulConnectionError: If MCP connection fails.
    """
    # Build query string from keywords
    query = " ".join(keywords)

    try:
        response = _call_forgetful_mcp(
            query=query,
            project_ids=project_ids,
            timeout_ms=FORGETFUL_TIMEOUT_MS,
        )
    except TimeoutError as e:
        raise ForgetfulTimeoutError(f"Forgetful query timed out: {e}") from e
    except ConnectionError as e:
        raise ForgetfulConnectionError(f"Forgetful connection failed: {e}") from e

    # Parse response into MemoryItem objects
    memories = []
    for mem_data in response.get("memories", []):
        memory = MemoryItem(
            id=mem_data["id"],
            title=mem_data["title"],
            content=mem_data["content"],
            importance=mem_data["importance"],
            keywords=mem_data.get("keywords", []),
        )
        memories.append(memory)

    return memories


# Memory type classification keywords for prioritization
ARCHITECTURE_KEYWORDS = {"architecture", "architectural", "decision", "adr"}
PATTERN_KEYWORDS = {"pattern", "design", "implementation"}


def _get_memory_type_priority(memory: MemoryItem) -> int:
    """Get priority score for memory type classification.

    Architecture decisions get highest priority (0), patterns get medium (1),
    everything else gets lowest (2).

    Args:
        memory: The memory item to classify.

    Returns:
        Priority score (lower is higher priority).
    """
    # Check title and keywords for architecture indicators
    title_lower = memory.title.lower()
    keywords_lower = {k.lower() for k in memory.keywords}

    if any(kw in title_lower for kw in ARCHITECTURE_KEYWORDS) or \
       keywords_lower & ARCHITECTURE_KEYWORDS:
        return 0  # Highest priority

    if any(kw in title_lower for kw in PATTERN_KEYWORDS) or \
       keywords_lower & PATTERN_KEYWORDS:
        return 1  # Medium priority

    return 2  # Lowest priority


def prioritize_memories(
    memories: list[MemoryItem],
    context_limit: int = CONTEXT_LIMIT_CHARS,
) -> list[MemoryItem]:
    """Prioritize and limit memories to fit context window.

    Sorting order:
    1. By importance (descending, 10 first)
    2. By type (architecture > pattern > other)

    Args:
        memories: List of memory items to prioritize.
        context_limit: Maximum total characters for context.

    Returns:
        Prioritized and limited list of memory items.
    """
    if not memories:
        return []

    # Sort by importance (descending), then by type priority (ascending)
    sorted_memories = sorted(
        memories,
        key=lambda m: (-m.importance, _get_memory_type_priority(m)),
    )

    # Limit to context window
    result = []
    total_chars = 0

    for memory in sorted_memories:
        memory_size = len(memory.content) + len(memory.title)
        if total_chars + memory_size <= context_limit:
            result.append(memory)
            total_chars += memory_size
        else:
            # Skip this memory - would exceed limit
            break

    return result


def query_forgetful_memories_with_retry(
    project_ids: list[int],
    keywords: list[str],
    return_degraded: bool = False,
) -> Union[list[MemoryItem], ContextPreloadResult]:
    """Query Forgetful MCP with retry logic and graceful degradation.

    Attempts to query Forgetful up to RETRY_COUNT times with RETRY_INTERVAL_MS
    between attempts. If all attempts fail, returns degraded result or raises.

    Args:
        project_ids: List of project IDs to filter memories by.
        keywords: List of keywords to search for.
        return_degraded: If True, return ContextPreloadResult.create_degraded()
            on failure instead of raising exception.

    Returns:
        List of MemoryItem objects if successful, or ContextPreloadResult
        with degraded status if return_degraded=True and all retries fail.

    Raises:
        ForgetfulTimeoutError: If all retries fail and return_degraded=False.
        ForgetfulConnectionError: If connection fails and return_degraded=False.
    """
    last_error: Optional[Exception] = None

    for attempt in range(RETRY_COUNT):
        try:
            return query_forgetful_memories(project_ids, keywords)
        except (ForgetfulTimeoutError, ForgetfulConnectionError, TimeoutError, ConnectionError) as e:
            last_error = e
            logger.warning(
                f"Forgetful query attempt {attempt + 1}/{RETRY_COUNT} failed: {e}"
            )
            if attempt < RETRY_COUNT - 1:
                # Sleep between retries (convert ms to seconds)
                time.sleep(RETRY_INTERVAL_MS / 1000.0)

    # All retries exhausted
    error_msg = f"Forgetful query failed after {RETRY_COUNT} attempts: {last_error}"
    logger.warning(error_msg)

    if return_degraded:
        # Determine reason from error type
        if isinstance(last_error, (TimeoutError, ForgetfulTimeoutError)):
            reason = f"Timeout after {RETRY_COUNT} retries: {last_error}"
        else:
            reason = f"Connection failed after {RETRY_COUNT} retries: {last_error}"
        return ContextPreloadResult.create_degraded(reason)

    # Re-raise appropriate exception
    if isinstance(last_error, (TimeoutError, ForgetfulTimeoutError)):
        raise ForgetfulTimeoutError(error_msg) from last_error
    raise ForgetfulConnectionError(error_msg) from last_error


def deduplicate_memories(memories: list[MemoryItem]) -> list[MemoryItem]:
    """Remove duplicate memories based on ID and content similarity.

    When duplicates are found, keeps the memory with higher importance.

    Args:
        memories: List of memory items to deduplicate.

    Returns:
        Deduplicated list of memory items.
    """
    if not memories:
        return []

    # Track seen IDs and content hashes
    seen_ids: dict[int, MemoryItem] = {}
    seen_content: dict[str, MemoryItem] = {}
    result: list[MemoryItem] = []

    for memory in memories:
        # Check for duplicate ID
        if memory.id in seen_ids:
            existing = seen_ids[memory.id]
            if memory.importance > existing.importance:
                # Replace with higher importance version
                result.remove(existing)
                result.append(memory)
                seen_ids[memory.id] = memory
            continue

        # Check for similar content (exact match for now)
        content_key = memory.content.strip().lower()
        if content_key in seen_content:
            existing = seen_content[content_key]
            if memory.importance > existing.importance:
                # Replace with higher importance version
                result.remove(existing)
                result.append(memory)
                seen_content[content_key] = memory
                seen_ids[memory.id] = memory
            continue

        # New unique memory
        seen_ids[memory.id] = memory
        seen_content[content_key] = memory
        result.append(memory)

    return result


def summarize_for_context(
    memories: list[MemoryItem],
    context_limit: int = CONTEXT_LIMIT_CHARS,
) -> str:
    """Format memories into a context string for agent injection.

    Creates a formatted string representation of memories suitable for
    inclusion in an agent's context window.

    Args:
        memories: List of memory items to format.
        context_limit: Maximum characters for the output string.

    Returns:
        Formatted context string containing memory information.
    """
    if not memories:
        return ""

    parts: list[str] = []
    total_chars = 0

    # Sort by importance first to ensure high priority in output
    sorted_memories = sorted(memories, key=lambda m: -m.importance)

    for memory in sorted_memories:
        # Format each memory entry
        entry = f"## {memory.title} (importance: {memory.importance})\n{memory.content}\n"
        entry_len = len(entry)

        if total_chars + entry_len <= context_limit:
            parts.append(entry)
            total_chars += entry_len
        else:
            # Truncate this entry to fit
            remaining = context_limit - total_chars
            if remaining > 50:  # Only include if we have meaningful space
                truncated = entry[:remaining - 3] + "..."
                parts.append(truncated)
            break

    return "\n".join(parts)


# In-memory cache for session results
_session_cache: dict[str, ContextPreloadResult] = {}


def _get_cache_path(session_id: str) -> str:
    """Get file path for cache file."""
    import os
    return os.path.join(CACHE_DIR, f"{session_id}.json")


def _load_from_cache(session_id: str) -> Optional[ContextPreloadResult]:
    """Load cached result for session if available and not expired.

    Args:
        session_id: Unique session identifier.

    Returns:
        Cached ContextPreloadResult or None if not cached/expired.
    """
    import json
    import os

    # Check in-memory cache first
    if session_id in _session_cache:
        cached = _session_cache[session_id]
        if cached.cached_at:
            cached_time = datetime.fromisoformat(cached.cached_at)
            age_seconds = (datetime.now() - cached_time).total_seconds()
            if age_seconds < CACHE_TTL_SECONDS:
                return cached

    # Check file cache
    cache_path = _get_cache_path(session_id)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check TTL
            if data.get("cached_at"):
                cached_time = datetime.fromisoformat(data["cached_at"])
                age_seconds = (datetime.now() - cached_time).total_seconds()
                if age_seconds >= CACHE_TTL_SECONDS:
                    return None

            # Reconstruct result
            memories = [
                MemoryItem(
                    id=m["id"],
                    title=m["title"],
                    content=m["content"],
                    importance=m["importance"],
                    keywords=m.get("keywords", []),
                )
                for m in data.get("memories", [])
            ]
            return ContextPreloadResult(
                status=PreloadStatus(data["status"]),
                memories=memories,
                degraded=data.get("degraded", False),
                reason=data.get("reason"),
                cached_at=data.get("cached_at"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to load cache for session {session_id}: {e}")

    return None


def _save_to_cache(session_id: str, result: ContextPreloadResult) -> None:
    """Save result to cache.

    Args:
        session_id: Unique session identifier.
        result: Result to cache.
    """
    import json
    import os
    from dataclasses import asdict

    # Save to in-memory cache
    _session_cache[session_id] = result

    # Ensure cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Save to file cache
    cache_path = _get_cache_path(session_id)
    try:
        data = {
            "status": result.status.value,
            "memories": [asdict(m) for m in result.memories],
            "degraded": result.degraded,
            "reason": result.reason,
            "cached_at": result.cached_at,
        }
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        logger.warning(f"Failed to save cache for session {session_id}: {e}")


def preload_context(
    project_ids: list[int],
    keywords: list[str],
    session_id: Optional[str] = None,
) -> ContextPreloadResult:
    """Pre-load context from Forgetful memory before workflow execution.

    This is the main entry point for the Context Pre-Loader component.
    It orchestrates the full pipeline: query -> deduplicate -> prioritize.

    Args:
        project_ids: List of project IDs to filter memories by.
        keywords: List of keywords to search for relevant memories.
        session_id: Optional session ID for caching. If provided, results
            are cached and reused for subsequent calls with the same ID.

    Returns:
        ContextPreloadResult containing prioritized memories or degraded status.
    """
    # Check cache first
    if session_id:
        cached = _load_from_cache(session_id)
        if cached:
            logger.debug(f"Using cached context for session {session_id}")
            return cached

    # Query Forgetful with retry and graceful degradation
    query_result = query_forgetful_memories_with_retry(
        project_ids=project_ids,
        keywords=keywords,
        return_degraded=True,
    )

    # If query returned a degraded result, return it
    if isinstance(query_result, ContextPreloadResult):
        if session_id:
            _save_to_cache(session_id, query_result)
        return query_result

    # query_result is a list of MemoryItem
    memories = query_result

    # Return empty if no memories
    if not memories:
        result = ContextPreloadResult.empty()
        if session_id:
            _save_to_cache(session_id, result)
        return result

    # Pipeline: deduplicate -> prioritize
    deduped = deduplicate_memories(memories)
    prioritized = prioritize_memories(deduped)

    # Create success result
    result = ContextPreloadResult.success(prioritized)

    # Cache the result
    if session_id:
        _save_to_cache(session_id, result)

    return result
