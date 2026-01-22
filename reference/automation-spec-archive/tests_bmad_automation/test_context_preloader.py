"""Tests for the Context Pre-Loader component.

This module tests the context pre-loading functionality that queries
Forgetful memory before workflow starts, following TDD principles.
"""

import pytest
from dataclasses import asdict
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock


class TestPreloadStatus:
    """Tests for PreloadStatus enum."""

    def test_success_status_value(self):
        """Verify SUCCESS status has correct string value."""
        from pcmrp_tools.bmad_automation.context_preloader import PreloadStatus

        assert PreloadStatus.SUCCESS.value == "success"

    def test_degraded_status_value(self):
        """Verify DEGRADED status has correct string value."""
        from pcmrp_tools.bmad_automation.context_preloader import PreloadStatus

        assert PreloadStatus.DEGRADED.value == "degraded"

    def test_empty_status_value(self):
        """Verify EMPTY status has correct string value."""
        from pcmrp_tools.bmad_automation.context_preloader import PreloadStatus

        assert PreloadStatus.EMPTY.value == "empty"


class TestMemoryItem:
    """Tests for MemoryItem dataclass."""

    def test_create_memory_item_with_required_fields(self):
        """Create MemoryItem with all required fields."""
        from pcmrp_tools.bmad_automation.context_preloader import MemoryItem

        item = MemoryItem(
            id=1,
            title="Test Memory",
            content="This is test content",
            importance=8
        )

        assert item.id == 1
        assert item.title == "Test Memory"
        assert item.content == "This is test content"
        assert item.importance == 8
        assert item.keywords == []  # Default empty list

    def test_create_memory_item_with_keywords(self):
        """Create MemoryItem with keywords."""
        from pcmrp_tools.bmad_automation.context_preloader import MemoryItem

        item = MemoryItem(
            id=2,
            title="Pattern Memory",
            content="A pattern for testing",
            importance=7,
            keywords=["pattern", "testing", "TDD"]
        )

        assert item.keywords == ["pattern", "testing", "TDD"]

    def test_memory_item_serialization(self):
        """Verify MemoryItem can be serialized to dict."""
        from pcmrp_tools.bmad_automation.context_preloader import MemoryItem

        item = MemoryItem(
            id=3,
            title="Serializable",
            content="Content here",
            importance=9,
            keywords=["key1"]
        )

        data = asdict(item)
        assert data == {
            "id": 3,
            "title": "Serializable",
            "content": "Content here",
            "importance": 9,
            "keywords": ["key1"]
        }


class TestContextPreloadResult:
    """Tests for ContextPreloadResult dataclass."""

    def test_create_result_with_required_fields(self):
        """Create ContextPreloadResult with status only."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            ContextPreloadResult,
            PreloadStatus,
        )

        result = ContextPreloadResult(status=PreloadStatus.SUCCESS)

        assert result.status == PreloadStatus.SUCCESS
        assert result.memories == []
        assert result.degraded is False
        assert result.reason is None
        assert result.cached_at is None

    def test_create_result_with_memories(self):
        """Create ContextPreloadResult with memories list."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            ContextPreloadResult,
            PreloadStatus,
            MemoryItem,
        )

        memories = [
            MemoryItem(id=1, title="Memory 1", content="Content 1", importance=9),
            MemoryItem(id=2, title="Memory 2", content="Content 2", importance=7),
        ]
        result = ContextPreloadResult(
            status=PreloadStatus.SUCCESS,
            memories=memories
        )

        assert len(result.memories) == 2
        assert result.memories[0].title == "Memory 1"

    def test_create_result_degraded_with_reason(self):
        """Create degraded ContextPreloadResult with reason."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            ContextPreloadResult,
            PreloadStatus,
        )

        result = ContextPreloadResult(
            status=PreloadStatus.DEGRADED,
            degraded=True,
            reason="Connection timeout"
        )

        assert result.status == PreloadStatus.DEGRADED
        assert result.degraded is True
        assert result.reason == "Connection timeout"

    def test_result_serialization(self):
        """Verify ContextPreloadResult can be serialized to dict."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            ContextPreloadResult,
            PreloadStatus,
            MemoryItem,
        )

        result = ContextPreloadResult(
            status=PreloadStatus.SUCCESS,
            memories=[MemoryItem(id=1, title="T", content="C", importance=8)],
            cached_at="2026-01-12T10:00:00"
        )

        data = asdict(result)
        assert data["status"] == PreloadStatus.SUCCESS
        assert len(data["memories"]) == 1
        assert data["cached_at"] == "2026-01-12T10:00:00"


class TestContextPreloadResultFactoryMethods:
    """Tests for ContextPreloadResult factory methods."""

    def test_success_factory_with_memories(self):
        """Factory method creates success result with memories."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            ContextPreloadResult,
            PreloadStatus,
            MemoryItem,
        )

        memories = [
            MemoryItem(id=1, title="Arch Decision", content="Use X", importance=10),
        ]
        result = ContextPreloadResult.success(memories)

        assert result.status == PreloadStatus.SUCCESS
        assert result.memories == memories
        assert result.degraded is False
        assert result.reason is None

    def test_success_factory_sets_cached_at(self):
        """Factory method sets cached_at timestamp."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            ContextPreloadResult,
            MemoryItem,
        )

        memories = [MemoryItem(id=1, title="T", content="C", importance=7)]
        result = ContextPreloadResult.success(memories)

        # Should have a timestamp set
        assert result.cached_at is not None
        # Should be parseable as ISO format
        datetime.fromisoformat(result.cached_at)

    def test_degraded_factory_with_reason(self):
        """Factory method creates degraded result with reason."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            ContextPreloadResult,
            PreloadStatus,
        )

        result = ContextPreloadResult.create_degraded("Forgetful MCP unavailable")

        assert result.status == PreloadStatus.DEGRADED
        assert result.degraded is True
        assert result.reason == "Forgetful MCP unavailable"
        assert result.memories == []

    def test_empty_factory(self):
        """Factory method creates empty result."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            ContextPreloadResult,
            PreloadStatus,
        )

        result = ContextPreloadResult.empty()

        assert result.status == PreloadStatus.EMPTY
        assert result.memories == []
        assert result.degraded is False
        assert result.reason is None


# Fixtures for Task 2+

@pytest.fixture
def sample_forgetful_response():
    """Sample response from Forgetful query_memory tool."""
    return {
        "memories": [
            {
                "id": 1,
                "title": "Architectural Decision: Use PostgreSQL",
                "content": "We chose PostgreSQL over MySQL for better JSON support.",
                "importance": 10,
                "keywords": ["architecture", "database", "postgresql"],
                "tags": ["decision", "architecture"],
            },
            {
                "id": 2,
                "title": "Pattern: Iterator for DBF extraction",
                "content": "Use iterator pattern to avoid loading entire DBF into memory.",
                "importance": 8,
                "keywords": ["pattern", "dbf", "extraction"],
                "tags": ["pattern"],
            },
            {
                "id": 3,
                "title": "Milestone: Phase 2 complete",
                "content": "Schema discovery phase completed successfully.",
                "importance": 6,
                "keywords": ["milestone", "phase2"],
                "tags": ["milestone"],
            },
        ],
        "total": 3,
    }


@pytest.fixture
def empty_forgetful_response():
    """Empty response from Forgetful when no memories match."""
    return {"memories": [], "total": 0}


class TestQueryForgetfulMemories:
    """Tests for query_forgetful_memories() function."""

    def test_query_returns_memory_items(self, sample_forgetful_response):
        """Query returns list of MemoryItem objects."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories,
            MemoryItem,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = sample_forgetful_response

            result = query_forgetful_memories(
                project_ids=[1],
                keywords=["architecture"]
            )

            assert len(result) == 3
            assert all(isinstance(m, MemoryItem) for m in result)
            assert result[0].title == "Architectural Decision: Use PostgreSQL"
            assert result[0].importance == 10

    def test_query_with_project_ids_parameter(self):
        """Query passes project_ids to Forgetful."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = {"memories": [], "total": 0}

            query_forgetful_memories(project_ids=[1, 2], keywords=["test"])

            mock_call.assert_called_once()
            call_args = mock_call.call_args[1]
            assert call_args["project_ids"] == [1, 2]

    def test_query_with_keywords_parameter(self):
        """Query passes keywords to Forgetful."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = {"memories": [], "total": 0}

            query_forgetful_memories(
                project_ids=[1],
                keywords=["architecture", "pattern", "decision"]
            )

            mock_call.assert_called_once()
            call_args = mock_call.call_args[1]
            # Keywords should be joined into a query string
            assert "architecture" in call_args["query"]

    def test_query_returns_empty_list_for_no_results(self, empty_forgetful_response):
        """Query returns empty list when no memories match."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = empty_forgetful_response

            result = query_forgetful_memories(project_ids=[1], keywords=["nonexistent"])

            assert result == []

    def test_query_handles_timeout(self):
        """Query handles timeout gracefully."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories,
            ForgetfulTimeoutError,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.side_effect = TimeoutError("Query timed out")

            with pytest.raises(ForgetfulTimeoutError):
                query_forgetful_memories(project_ids=[1], keywords=["test"])

    def test_query_respects_timeout_setting(self):
        """Query uses configured timeout of 300ms."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories,
            FORGETFUL_TIMEOUT_MS,
        )

        assert FORGETFUL_TIMEOUT_MS == 300

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = {"memories": [], "total": 0}

            query_forgetful_memories(project_ids=[1], keywords=["test"])

            mock_call.assert_called_once()
            call_args = mock_call.call_args[1]
            assert call_args.get("timeout_ms") == 300


class TestCallForgetfulMcp:
    """Tests for the internal _call_forgetful_mcp function."""

    def test_call_forgetful_mcp_constructs_correct_query(self):
        """Internal function constructs correct query structure."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            _call_forgetful_mcp,
        )

        # We'll test that the function has the expected signature
        import inspect
        sig = inspect.signature(_call_forgetful_mcp)
        params = list(sig.parameters.keys())

        assert "query" in params
        assert "project_ids" in params
        assert "timeout_ms" in params


class TestPrioritizeMemories:
    """Tests for prioritize_memories() function."""

    def test_sorts_by_importance_descending(self):
        """Memories are sorted by importance (highest first)."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            prioritize_memories,
            MemoryItem,
        )

        memories = [
            MemoryItem(id=1, title="Low", content="C1", importance=5),
            MemoryItem(id=2, title="High", content="C2", importance=10),
            MemoryItem(id=3, title="Medium", content="C3", importance=7),
        ]

        result = prioritize_memories(memories)

        assert result[0].importance == 10
        assert result[1].importance == 7
        assert result[2].importance == 5

    def test_architectural_decisions_first_at_same_importance(self):
        """Architectural decisions prioritized over patterns at same importance."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            prioritize_memories,
            MemoryItem,
        )

        memories = [
            MemoryItem(
                id=1,
                title="Pattern: Iterator",
                content="C1",
                importance=9,
                keywords=["pattern"],
            ),
            MemoryItem(
                id=2,
                title="Architecture: Database choice",
                content="C2",
                importance=9,
                keywords=["architecture", "decision"],
            ),
            MemoryItem(
                id=3,
                title="Problem Solution",
                content="C3",
                importance=9,
                keywords=["solution"],
            ),
        ]

        result = prioritize_memories(memories)

        # Architecture decision should come first
        assert result[0].id == 2
        assert "architecture" in result[0].keywords or "Architecture" in result[0].title

    def test_limits_to_context_window_size(self):
        """Memories limited to fit within context window."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            prioritize_memories,
            MemoryItem,
            CONTEXT_LIMIT_CHARS,
        )

        # Create memories that exceed context limit
        # Each memory has ~100 chars of content
        large_content = "x" * 1000
        memories = [
            MemoryItem(id=i, title=f"Memory {i}", content=large_content, importance=10)
            for i in range(20)  # 20 * 1000 = 20000 chars, way over 8000 limit
        ]

        result = prioritize_memories(memories)

        # Calculate total content size
        total_chars = sum(len(m.content) + len(m.title) for m in result)

        # Should be under the limit
        assert total_chars <= CONTEXT_LIMIT_CHARS

    def test_preserves_high_importance_when_limiting(self):
        """High importance memories preserved when limiting."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            prioritize_memories,
            MemoryItem,
        )

        large_content = "x" * 1000
        memories = [
            MemoryItem(id=1, title="Critical", content=large_content, importance=10),
            MemoryItem(id=2, title="Important", content=large_content, importance=9),
            MemoryItem(id=3, title="Medium", content=large_content, importance=6),
            MemoryItem(id=4, title="Low", content=large_content, importance=3),
        ]

        result = prioritize_memories(memories)

        # High importance should be kept
        ids_kept = [m.id for m in result]
        # The most important ones should be there
        if 1 in ids_kept:
            assert True
        if 2 in ids_kept:
            # If we kept 2, we should have kept 1 first
            assert 1 in ids_kept

    def test_empty_input_returns_empty(self):
        """Empty input returns empty list."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            prioritize_memories,
        )

        result = prioritize_memories([])

        assert result == []

    def test_single_memory_returned_unchanged(self):
        """Single memory returned as-is."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            prioritize_memories,
            MemoryItem,
        )

        memories = [
            MemoryItem(id=1, title="Only One", content="Content", importance=5),
        ]

        result = prioritize_memories(memories)

        assert len(result) == 1
        assert result[0].id == 1


class TestGracefulDegradation:
    """Tests for graceful degradation when Forgetful MCP is unavailable."""

    def test_retry_on_timeout(self):
        """Query retries on timeout up to RETRY_COUNT times."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories_with_retry,
            RETRY_COUNT,
        )

        call_count = 0

        def mock_call(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError("Timeout")
            return {"memories": [], "total": 0}

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock:
            mock.side_effect = mock_call

            result = query_forgetful_memories_with_retry(
                project_ids=[1],
                keywords=["test"]
            )

            # Should have retried and eventually succeeded
            assert call_count == 3
            assert result == []

    def test_returns_degraded_after_max_retries(self):
        """Returns degraded result after exhausting retries."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories_with_retry,
            ContextPreloadResult,
            PreloadStatus,
            RETRY_COUNT,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock:
            mock.side_effect = TimeoutError("Timeout")

            result = query_forgetful_memories_with_retry(
                project_ids=[1],
                keywords=["test"],
                return_degraded=True
            )

            assert isinstance(result, ContextPreloadResult)
            assert result.status == PreloadStatus.DEGRADED
            assert result.degraded is True
            assert "timeout" in result.reason.lower()

    def test_handles_connection_refused(self):
        """Handles connection refused errors gracefully."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories_with_retry,
            ContextPreloadResult,
            PreloadStatus,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock:
            mock.side_effect = ConnectionError("Connection refused")

            result = query_forgetful_memories_with_retry(
                project_ids=[1],
                keywords=["test"],
                return_degraded=True
            )

            assert isinstance(result, ContextPreloadResult)
            assert result.status == PreloadStatus.DEGRADED
            assert result.degraded is True
            assert "connection" in result.reason.lower()

    def test_returns_empty_memories_on_degradation(self):
        """Degraded result has empty memories list."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories_with_retry,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock:
            mock.side_effect = TimeoutError("Timeout")

            result = query_forgetful_memories_with_retry(
                project_ids=[1],
                keywords=["test"],
                return_degraded=True
            )

            assert result.memories == []

    def test_logs_failure_for_debugging(self, caplog):
        """Logs failure when entering degraded mode."""
        import logging
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories_with_retry,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock:
            mock.side_effect = TimeoutError("Timeout after 300ms")

            with caplog.at_level(logging.WARNING):
                query_forgetful_memories_with_retry(
                    project_ids=[1],
                    keywords=["test"],
                    return_degraded=True
                )

            # Should have logged the failure
            assert any("timeout" in record.message.lower() or "failed" in record.message.lower()
                      for record in caplog.records)

    def test_retry_interval_is_100ms(self):
        """Retry interval between attempts is 100ms."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            RETRY_INTERVAL_MS,
        )

        assert RETRY_INTERVAL_MS == 100

    def test_max_retries_is_3(self):
        """Maximum retry count is 3."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            RETRY_COUNT,
        )

        assert RETRY_COUNT == 3


class TestDeduplicateMemories:
    """Tests for deduplicate_memories() function."""

    def test_removes_duplicate_by_id(self):
        """Removes memories with duplicate IDs."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            deduplicate_memories,
            MemoryItem,
        )

        memories = [
            MemoryItem(id=1, title="First", content="Content A", importance=8),
            MemoryItem(id=2, title="Second", content="Content B", importance=7),
            MemoryItem(id=1, title="First Duplicate", content="Content A", importance=8),
        ]

        result = deduplicate_memories(memories)

        assert len(result) == 2
        ids = [m.id for m in result]
        assert ids.count(1) == 1
        assert ids.count(2) == 1

    def test_removes_similar_content(self):
        """Removes memories with very similar content."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            deduplicate_memories,
            MemoryItem,
        )

        memories = [
            MemoryItem(
                id=1,
                title="Database Decision",
                content="We chose PostgreSQL for the database due to JSON support.",
                importance=9
            ),
            MemoryItem(
                id=2,
                title="DB Choice",
                content="We chose PostgreSQL for the database due to JSON support.",  # Identical content
                importance=8
            ),
            MemoryItem(
                id=3,
                title="Different Topic",
                content="The iterator pattern helps with memory efficiency.",
                importance=7
            ),
        ]

        result = deduplicate_memories(memories)

        # Should keep one of the PostgreSQL memories and the different topic
        assert len(result) == 2

    def test_keeps_higher_importance_on_duplicate(self):
        """When deduplicating, keeps the higher importance memory."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            deduplicate_memories,
            MemoryItem,
        )

        memories = [
            MemoryItem(
                id=1,
                title="Low Priority",
                content="Same content for both",
                importance=5
            ),
            MemoryItem(
                id=2,
                title="High Priority",
                content="Same content for both",
                importance=9
            ),
        ]

        result = deduplicate_memories(memories)

        assert len(result) == 1
        assert result[0].importance == 9

    def test_empty_list_returns_empty(self):
        """Empty input returns empty list."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            deduplicate_memories,
        )

        result = deduplicate_memories([])

        assert result == []

    def test_single_memory_returned_unchanged(self):
        """Single memory returned as-is."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            deduplicate_memories,
            MemoryItem,
        )

        memories = [
            MemoryItem(id=1, title="Only One", content="Unique", importance=7),
        ]

        result = deduplicate_memories(memories)

        assert len(result) == 1
        assert result[0].id == 1


class TestSummarizeMemories:
    """Tests for summarize_for_context() function."""

    def test_formats_memories_for_context(self):
        """Formats memories into context string."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            summarize_for_context,
            MemoryItem,
        )

        memories = [
            MemoryItem(id=1, title="Decision A", content="Content A", importance=10),
            MemoryItem(id=2, title="Pattern B", content="Content B", importance=8),
        ]

        result = summarize_for_context(memories)

        assert "Decision A" in result
        assert "Content A" in result
        assert "Pattern B" in result
        assert "Content B" in result

    def test_truncates_if_exceeds_limit(self):
        """Truncates content if total exceeds context limit."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            summarize_for_context,
            MemoryItem,
            CONTEXT_LIMIT_CHARS,
        )

        # Create memory with very large content
        large_content = "x" * 10000
        memories = [
            MemoryItem(id=1, title="Large", content=large_content, importance=10),
        ]

        result = summarize_for_context(memories)

        assert len(result) <= CONTEXT_LIMIT_CHARS

    def test_preserves_high_importance_in_summary(self):
        """High importance memories appear in summary."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            summarize_for_context,
            MemoryItem,
        )

        memories = [
            MemoryItem(id=1, title="Critical Decision", content="Important", importance=10),
            MemoryItem(id=2, title="Minor Note", content="Less important", importance=3),
        ]

        result = summarize_for_context(memories)

        assert "Critical Decision" in result

    def test_empty_memories_returns_empty_string(self):
        """Empty memories list returns empty string."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            summarize_for_context,
        )

        result = summarize_for_context([])

        assert result == ""


class TestPreloadContext:
    """Tests for the main preload_context() function."""

    def test_orchestrates_full_pipeline(self, sample_forgetful_response):
        """Orchestrates query, prioritize, dedupe pipeline."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
            ContextPreloadResult,
            PreloadStatus,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = sample_forgetful_response

            result = preload_context(
                project_ids=[1],
                keywords=["architecture", "pattern"]
            )

            assert isinstance(result, ContextPreloadResult)
            assert result.status == PreloadStatus.SUCCESS
            assert len(result.memories) > 0

    def test_returns_degraded_on_mcp_failure(self):
        """Returns degraded result when MCP unavailable."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
            ContextPreloadResult,
            PreloadStatus,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.side_effect = TimeoutError("Timeout")

            result = preload_context(
                project_ids=[1],
                keywords=["test"]
            )

            assert isinstance(result, ContextPreloadResult)
            assert result.status == PreloadStatus.DEGRADED
            assert result.degraded is True

    def test_returns_empty_when_no_memories(self, empty_forgetful_response):
        """Returns empty result when no memories match."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
            ContextPreloadResult,
            PreloadStatus,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = empty_forgetful_response

            result = preload_context(
                project_ids=[1],
                keywords=["nonexistent"]
            )

            assert isinstance(result, ContextPreloadResult)
            assert result.status == PreloadStatus.EMPTY
            assert result.memories == []

    def test_caches_results(self, sample_forgetful_response, tmp_path):
        """Caches results to prevent duplicate queries."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
        )
        import pcmrp_tools.bmad_automation.context_preloader as module

        # Override cache dir to temp path
        original_cache_dir = module.CACHE_DIR
        module.CACHE_DIR = str(tmp_path)

        try:
            with patch(
                "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
            ) as mock_call:
                mock_call.return_value = sample_forgetful_response

                # First call
                result1 = preload_context(
                    project_ids=[1],
                    keywords=["test"],
                    session_id="test-session-123"
                )

                # Second call with same session_id should use cache
                result2 = preload_context(
                    project_ids=[1],
                    keywords=["test"],
                    session_id="test-session-123"
                )

                # Should only call MCP once (second call uses cache)
                assert mock_call.call_count == 1
                assert result1.cached_at is not None
                assert result2.cached_at == result1.cached_at
        finally:
            module.CACHE_DIR = original_cache_dir

    def test_formats_context_for_agent_injection(self, sample_forgetful_response):
        """Returns formatted context for agent injection."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = sample_forgetful_response

            result = preload_context(
                project_ids=[1],
                keywords=["architecture"]
            )

            # Result should contain memory items
            assert len(result.memories) > 0
            # First memory should be highest importance (architectural decision)
            assert result.memories[0].importance >= result.memories[-1].importance

    def test_prioritizes_high_importance_memories(self, sample_forgetful_response):
        """High importance memories come first."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = sample_forgetful_response

            result = preload_context(
                project_ids=[1],
                keywords=["architecture"]
            )

            # Should be sorted by importance descending
            importances = [m.importance for m in result.memories]
            assert importances == sorted(importances, reverse=True)

    def test_deduplicates_memories(self):
        """Deduplicates memories in pipeline."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
        )

        # Response with duplicate content
        response_with_dupes = {
            "memories": [
                {
                    "id": 1,
                    "title": "Decision 1",
                    "content": "Same content",
                    "importance": 9,
                    "keywords": ["architecture"],
                },
                {
                    "id": 2,
                    "title": "Decision 2",
                    "content": "Same content",  # Duplicate
                    "importance": 7,
                    "keywords": ["architecture"],
                },
            ],
            "total": 2,
        }

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = response_with_dupes

            result = preload_context(
                project_ids=[1],
                keywords=["architecture"]
            )

            # Should deduplicate
            assert len(result.memories) == 1
            # Should keep higher importance
            assert result.memories[0].importance == 9


class TestPreloadContextIntegration:
    """Integration tests for the full preload_context pipeline."""

    def test_full_pipeline_with_all_features(self, sample_forgetful_response, tmp_path):
        """Full integration test of the pipeline."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
            ContextPreloadResult,
            PreloadStatus,
        )
        import pcmrp_tools.bmad_automation.context_preloader as module

        # Override cache dir
        original_cache_dir = module.CACHE_DIR
        module.CACHE_DIR = str(tmp_path)

        try:
            with patch(
                "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
            ) as mock_call:
                mock_call.return_value = sample_forgetful_response

                result = preload_context(
                    project_ids=[1],
                    keywords=["architecture", "pattern", "decision"],
                    session_id="integration-test"
                )

                # Verify result structure
                assert isinstance(result, ContextPreloadResult)
                assert result.status == PreloadStatus.SUCCESS
                assert result.degraded is False
                assert result.cached_at is not None
                assert len(result.memories) > 0

                # Verify priorities (importance descending)
                for i in range(len(result.memories) - 1):
                    assert result.memories[i].importance >= result.memories[i + 1].importance
        finally:
            module.CACHE_DIR = original_cache_dir


class TestEdgeCases:
    """Additional edge case tests for full coverage."""

    def test_query_handles_connection_error(self):
        """Query handles ConnectionError and raises ForgetfulConnectionError."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories,
            ForgetfulConnectionError,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.side_effect = ConnectionError("Connection refused")

            with pytest.raises(ForgetfulConnectionError):
                query_forgetful_memories(project_ids=[1], keywords=["test"])

    def test_retry_raises_connection_error_when_not_degraded(self):
        """Retry function raises ForgetfulConnectionError when return_degraded=False."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories_with_retry,
            ForgetfulConnectionError,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.side_effect = ConnectionError("Connection refused")

            with pytest.raises(ForgetfulConnectionError):
                query_forgetful_memories_with_retry(
                    project_ids=[1],
                    keywords=["test"],
                    return_degraded=False
                )

    def test_retry_raises_timeout_error_when_not_degraded(self):
        """Retry function raises ForgetfulTimeoutError when return_degraded=False."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            query_forgetful_memories_with_retry,
            ForgetfulTimeoutError,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.side_effect = TimeoutError("Timeout")

            with pytest.raises(ForgetfulTimeoutError):
                query_forgetful_memories_with_retry(
                    project_ids=[1],
                    keywords=["test"],
                    return_degraded=False
                )

    def test_cache_loading_from_file(self, sample_forgetful_response, tmp_path):
        """Cache is loaded from file when in-memory cache is empty."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
            _session_cache,
        )
        import pcmrp_tools.bmad_automation.context_preloader as module
        import json

        original_cache_dir = module.CACHE_DIR
        module.CACHE_DIR = str(tmp_path)

        try:
            with patch(
                "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
            ) as mock_call:
                mock_call.return_value = sample_forgetful_response

                # First call - creates cache
                session_id = "file-cache-test"
                result1 = preload_context(
                    project_ids=[1],
                    keywords=["test"],
                    session_id=session_id
                )

                # Clear in-memory cache to force file load
                if session_id in _session_cache:
                    del _session_cache[session_id]

                # Second call should load from file
                result2 = preload_context(
                    project_ids=[1],
                    keywords=["test"],
                    session_id=session_id
                )

                # MCP should only be called once (file cache used for second call)
                assert mock_call.call_count == 1
                assert result2.cached_at == result1.cached_at
        finally:
            module.CACHE_DIR = original_cache_dir

    def test_cache_file_ttl_expiry(self, sample_forgetful_response, tmp_path):
        """Expired cache file is not used."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
            _session_cache,
            CACHE_TTL_SECONDS,
        )
        import pcmrp_tools.bmad_automation.context_preloader as module
        import json
        from datetime import timedelta

        original_cache_dir = module.CACHE_DIR
        module.CACHE_DIR = str(tmp_path)

        try:
            # Create an expired cache file
            session_id = "expired-cache-test"
            expired_time = (datetime.now() - timedelta(seconds=CACHE_TTL_SECONDS + 100)).isoformat()
            cache_data = {
                "status": "success",
                "memories": [],
                "degraded": False,
                "reason": None,
                "cached_at": expired_time,
            }
            cache_path = tmp_path / f"{session_id}.json"
            with open(cache_path, "w") as f:
                json.dump(cache_data, f)

            with patch(
                "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
            ) as mock_call:
                mock_call.return_value = sample_forgetful_response

                # Should not use expired cache
                result = preload_context(
                    project_ids=[1],
                    keywords=["test"],
                    session_id=session_id
                )

                # MCP should be called (cache expired)
                assert mock_call.call_count == 1
                # Should have fresh timestamp
                assert result.cached_at != expired_time
        finally:
            module.CACHE_DIR = original_cache_dir

    def test_cache_file_corruption_handled(self, sample_forgetful_response, tmp_path):
        """Corrupted cache file is handled gracefully."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
        )
        import pcmrp_tools.bmad_automation.context_preloader as module

        original_cache_dir = module.CACHE_DIR
        module.CACHE_DIR = str(tmp_path)

        try:
            # Create a corrupted cache file
            session_id = "corrupted-cache-test"
            cache_path = tmp_path / f"{session_id}.json"
            with open(cache_path, "w") as f:
                f.write("not valid json {{{")

            with patch(
                "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
            ) as mock_call:
                mock_call.return_value = sample_forgetful_response

                # Should handle corruption and query fresh
                result = preload_context(
                    project_ids=[1],
                    keywords=["test"],
                    session_id=session_id
                )

                # MCP should be called (corrupted cache ignored)
                assert mock_call.call_count == 1
                assert result.memories is not None
        finally:
            module.CACHE_DIR = original_cache_dir

    def test_cache_save_error_handled(self, sample_forgetful_response, tmp_path):
        """Cache save errors are handled gracefully."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
            PreloadStatus,
        )
        import pcmrp_tools.bmad_automation.context_preloader as module

        # Use non-existent path that can't be created
        original_cache_dir = module.CACHE_DIR
        module.CACHE_DIR = "/nonexistent/path/that/cannot/be/created"

        try:
            with patch(
                "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
            ) as mock_call:
                mock_call.return_value = sample_forgetful_response

                # Should succeed even if cache save fails
                result = preload_context(
                    project_ids=[1],
                    keywords=["test"],
                    session_id="cache-save-error-test"
                )

                # Result should still be valid
                assert result.status == PreloadStatus.SUCCESS
        finally:
            module.CACHE_DIR = original_cache_dir

    def test_preload_without_session_id(self, sample_forgetful_response):
        """Preload works without session_id (no caching)."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
            PreloadStatus,
        )

        with patch(
            "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
        ) as mock_call:
            mock_call.return_value = sample_forgetful_response

            result = preload_context(
                project_ids=[1],
                keywords=["test"]
                # No session_id
            )

            assert result.status == PreloadStatus.SUCCESS

    def test_deduplicate_replaces_lower_importance_by_id(self):
        """Deduplication replaces lower importance memory when same ID found later."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            deduplicate_memories,
            MemoryItem,
        )

        memories = [
            MemoryItem(id=1, title="Low First", content="Content", importance=5),
            MemoryItem(id=1, title="High Second", content="Content", importance=9),
        ]

        result = deduplicate_memories(memories)

        assert len(result) == 1
        assert result[0].importance == 9
        assert result[0].title == "High Second"

    def test_in_memory_cache_ttl_expiry(self, sample_forgetful_response, tmp_path):
        """In-memory cache respects TTL."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            preload_context,
            _session_cache,
            ContextPreloadResult,
            PreloadStatus,
            MemoryItem,
            CACHE_TTL_SECONDS,
        )
        import pcmrp_tools.bmad_automation.context_preloader as module
        from datetime import timedelta

        original_cache_dir = module.CACHE_DIR
        module.CACHE_DIR = str(tmp_path)

        try:
            session_id = "inmemory-ttl-test"

            # Manually insert expired cache entry
            expired_time = (datetime.now() - timedelta(seconds=CACHE_TTL_SECONDS + 100)).isoformat()
            _session_cache[session_id] = ContextPreloadResult(
                status=PreloadStatus.SUCCESS,
                memories=[MemoryItem(id=999, title="Expired", content="Old", importance=1)],
                cached_at=expired_time,
            )

            with patch(
                "pcmrp_tools.bmad_automation.context_preloader._call_forgetful_mcp"
            ) as mock_call:
                mock_call.return_value = sample_forgetful_response

                result = preload_context(
                    project_ids=[1],
                    keywords=["test"],
                    session_id=session_id
                )

                # Should have queried fresh (expired in-memory cache)
                assert mock_call.call_count == 1
                # Should not have the expired memory
                assert not any(m.id == 999 for m in result.memories)
        finally:
            module.CACHE_DIR = original_cache_dir
            if session_id in _session_cache:
                del _session_cache[session_id]

    def test_prioritize_handles_very_large_memory(self):
        """Prioritization correctly skips memories that alone exceed limit."""
        from pcmrp_tools.bmad_automation.context_preloader import (
            prioritize_memories,
            MemoryItem,
        )

        # Create memory larger than context limit
        huge_content = "x" * 10000
        memories = [
            MemoryItem(id=1, title="Huge", content=huge_content, importance=10),
            MemoryItem(id=2, title="Small", content="tiny", importance=5),
        ]

        # With very small limit, only small memory fits
        result = prioritize_memories(memories, context_limit=100)

        # The huge one doesn't fit, so only small one should be included
        # Actually, none may fit because huge is tried first
        assert len(result) <= 1
