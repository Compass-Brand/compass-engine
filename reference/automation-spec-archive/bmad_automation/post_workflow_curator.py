"""Post-Workflow Learning Extraction - Story 4-2.

This module implements the Post-Workflow Curator which automatically extracts
key learnings after workflow completion, including:
- Architectural decisions (importance 9-10)
- Implementation patterns (importance 7-8)
- Milestones (importance 6-7)
- Problem-solution pairs (importance 7-8)

The curator integrates with Memory Bridge to persist learnings to Forgetful.
"""

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel


# ============================================================================
# Module-Level Constants
# ============================================================================

# Task E1.4 / Issue 6: Duplication threshold (>80% similarity)
DUPLICATE_OVERLAP_THRESHOLD = 0.8

# Alias for backward compatibility with tests
DUPLICATION_THRESHOLD = DUPLICATE_OVERLAP_THRESHOLD

# Issue 6: Maximum length for rationale text
MAX_RATIONALE_LENGTH = 200


# ============================================================================
# Pre-compiled Regex Patterns (Issue 4)
# ============================================================================

# Architectural decision detection patterns
COMPILED_DECISION_PATTERNS = [
    re.compile(r"chose\s+(\w+(?:\s+\w+)?)\s+over\s+(\w+(?:\s+\w+)?)", re.IGNORECASE),
    re.compile(r"architecture\s+uses\s+(\w+(?:\s+\w+)?)", re.IGNORECASE),
    re.compile(r"design\s+decision[:\s]+(.+?)(?:\.|$|\n)", re.IGNORECASE),
    re.compile(r"decided\s+to\s+use\s+(\w+(?:\s+\w+)?)", re.IGNORECASE),
    re.compile(r"selected\s+(\w+(?:\s+\w+)?)\s+for\s+", re.IGNORECASE),
]

# System-wide scope indicators
COMPILED_SYSTEM_SCOPE_PATTERNS = [
    re.compile(r"all\s+services", re.IGNORECASE),
    re.compile(r"entire\s+system", re.IGNORECASE),
    re.compile(r"platform[-\s]?wide", re.IGNORECASE),
    re.compile(r"across\s+the\s+platform", re.IGNORECASE),
    re.compile(r"organization[-\s]?wide", re.IGNORECASE),
    re.compile(r"system\s+architecture", re.IGNORECASE),
    re.compile(r"infrastructure", re.IGNORECASE),
    re.compile(r"enterprise", re.IGNORECASE),
]

# Component-level scope indicators
COMPILED_COMPONENT_SCOPE_PATTERNS = [
    re.compile(r"the\s+\w+\s+module", re.IGNORECASE),
    re.compile(r"the\s+\w+\s+service", re.IGNORECASE),
    re.compile(r"\w+\s+component", re.IGNORECASE),
    re.compile(r"this\s+module", re.IGNORECASE),
    re.compile(r"this\s+service", re.IGNORECASE),
    re.compile(r"this\s+component", re.IGNORECASE),
]

# Implementation pattern indicators
COMPILED_PATTERN_INDICATORS = [
    re.compile(r"used\s+(\w+(?:\s+\w+)?)\s+pattern", re.IGNORECASE),
    re.compile(r"(\w+(?:\s+\w+)?)\s+approach", re.IGNORECASE),
    re.compile(r"(\w+(?:\s+\w+)?)\s+technique", re.IGNORECASE),
    re.compile(r"(\w+(?:\s+\w+)?)\s+strategy", re.IGNORECASE),
    re.compile(r"used\s+(\w+(?:\s+\w+)?)\s+for\s+(\w+(?:\s+\w+)*)", re.IGNORECASE),
    re.compile(r"implemented\s+(\w+(?:\s+\w+)?)", re.IGNORECASE),
]

# Problem detection patterns
COMPILED_PROBLEM_INDICATORS = [
    re.compile(r"fixed\s+(.+?)(?:\s+by\s+|\.|$|\n)", re.IGNORECASE),
    re.compile(r"resolved\s+(.+?)(?:\s+by\s+|\.|$|\n)", re.IGNORECASE),
    re.compile(r"solved\s+(.+?)(?:\s+by\s+|\.|$|\n)", re.IGNORECASE),
    re.compile(r"error[:\s]+(.+?)(?:\s*[-–]\s*|\.|$|\n)", re.IGNORECASE),
    re.compile(r"issue[:\s]+(.+?)(?:\s+resolved|\s+fixed|\.|$|\n)", re.IGNORECASE),
    re.compile(r"bug\s+(?:in\s+)?(.+?)(?:\s+was\s+fixed|\s+fixed|\.|$|\n)", re.IGNORECASE),
]

# Milestone completion indicators
COMPILED_COMPLETION_INDICATORS = [
    re.compile(r"([\w\-\.]+(?:\s+[\w\-\.]+){0,5})\s+(?:is\s+)?complete[d]?\b", re.IGNORECASE),
    re.compile(r"([\w\-\.]+(?:\s+[\w\-\.]+){0,5})\s+finished\b", re.IGNORECASE),
    re.compile(r"([\w\-\.]+(?:\s+[\w\-\.]+){0,5})\s+(?:is\s+)?done\b", re.IGNORECASE),
    re.compile(r"([\w\-\.]+(?:\s+[\w\-\.]+){0,5})\s+shipped\b", re.IGNORECASE),
    re.compile(r"([\w\-\.]+(?:\s+[\w\-\.]+){0,5})\s+released\b", re.IGNORECASE),
    re.compile(r"completed\s+([\w\-\.]+(?:\s+[\w\-\.]+){0,5})", re.IGNORECASE),
]

# Negation patterns for filtering false positives
COMPILED_NEGATION_PATTERNS = [
    re.compile(r"not\s+(?:yet\s+)?(?:complete|done|finished)", re.IGNORECASE),
    re.compile(r"isn['`]t\s+(?:complete|done|finished)", re.IGNORECASE),
    re.compile(r"still\s+incomplete", re.IGNORECASE),
    re.compile(r"not\s+done", re.IGNORECASE),
    re.compile(r"incomplete", re.IGNORECASE),
]

# Rationale extraction patterns
COMPILED_RATIONALE_PATTERNS = [
    re.compile(r"because\s+(?:of\s+)?(.+?)(?:\.|,|$|\n)", re.IGNORECASE),
    re.compile(r"for\s+(.+?)(?:\.|,|$|\n)", re.IGNORECASE),
    re.compile(r"due\s+to\s+(.+?)(?:\.|,|$|\n)", re.IGNORECASE),
    re.compile(r"to\s+achieve\s+(.+?)(?:\.|,|$|\n)", re.IGNORECASE),
    re.compile(r"to\s+ensure\s+(.+?)(?:\.|,|$|\n)", re.IGNORECASE),
    re.compile(r"as\s+it\s+(.+?)(?:\.|,|$|\n)", re.IGNORECASE),
    re.compile(r"since\s+(.+?)(?:\.|,|$|\n)", re.IGNORECASE),
]

# Problem-solution linking patterns
COMPILED_FIX_PATTERN = re.compile(
    r"(?:fixed|resolved|solved)\s+(.+?)\s+by\s+(.+?)(?:\.|$|\n)", re.IGNORECASE
)
COMPILED_ERROR_FIX_PATTERN = re.compile(
    r"error[:\s]+(.+?)(?:\s*[-–]\s*|\s+)(?:fixed|resolved)\s+by\s+(.+?)(?:\.|$|\n)",
    re.IGNORECASE,
)
COMPILED_ISSUE_PATTERN = re.compile(
    r"issue\s+(?:with\s+)?(.+?)\s+(?:resolved|fixed)\s+by\s+(.+?)(?:\.|$|\n)",
    re.IGNORECASE,
)
COMPILED_BUG_PATTERN = re.compile(
    r"bug\s+(?:in\s+)?(.+?)\s+(?:was\s+)?(?:fixed|resolved)\s+by\s+(.+?)(?:\.|$|\n)",
    re.IGNORECASE,
)
COMPILED_SIMPLE_FIX_PATTERN = re.compile(
    r"(?:fixed|resolved|solved)\s+(.+?)(?:\.|$|\n)", re.IGNORECASE
)


# ============================================================================
# Module-Level Helper Functions (Issue 2 & 3)
# ============================================================================


def extract_text_from_context(context: Dict[str, Any]) -> List[str]:
    """Extract all text values from context dictionary.

    This is a shared utility function used by all extractors to pull
    text content from various context fields.

    Args:
        context: The context dictionary containing workflow data

    Returns:
        List of string values found in context
    """
    if context is None:
        return []

    texts: List[str] = []

    # Common fields to check (union of all extractor needs)
    fields_to_check = [
        "workflow_output",
        "notes",
        "summary",
        "decisions",
        "output",
        "content",
        "text",
        "messages",
        "log",
        "result",
    ]

    for key in fields_to_check:
        value = context.get(key)
        if value is None:
            continue
        if isinstance(value, str) and value:
            texts.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item:
                    texts.append(item)
                elif isinstance(item, dict):
                    # Check common nested content fields
                    for content_key in ("content", "text"):
                        content = item.get(content_key, "")
                        if isinstance(content, str) and content:
                            texts.append(content)

    # Also check any other string values not in fields_to_check
    for key, value in context.items():
        if key not in fields_to_check and isinstance(value, str) and value:
            texts.append(value)

    return texts


def generate_keywords(
    text: str,
    extra_stopwords: Optional[Set[str]] = None,
    max_keywords: int = 10,
) -> List[str]:
    """Generate searchable keywords from text.

    This is a shared utility function used by all extractors to generate
    keywords for memory storage.

    Args:
        text: The text to extract keywords from
        extra_stopwords: Additional stopwords to filter out
        max_keywords: Maximum number of keywords to return (default 10)

    Returns:
        List of unique keywords (lowercase, deduplicated)
    """
    # Base stopwords common to all extractors
    stopwords: Set[str] = {
        "the", "a", "an", "for", "to", "and", "or", "with", "used",
        "over", "use", "uses", "using", "by", "in", "on", "was", "is",
        "are", "of", "that", "this", "has", "have", "been", "being",
    }

    if extra_stopwords:
        stopwords = stopwords | extra_stopwords

    # Split on whitespace and punctuation
    words = re.split(r"[\s\-_:,.\(\)\[\]]+", text)

    # Filter out short words and stopwords
    keywords = [
        w.lower()
        for w in words
        if len(w) >= 2 and w.lower() not in stopwords
    ]

    # Deduplicate while preserving order
    seen: Set[str] = set()
    unique_keywords: List[str] = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    return unique_keywords[:max_keywords]


# ============================================================================
# Task A1: ExtractedDecision dataclass and ArchitecturalDecisionExtractor
# ============================================================================


@dataclass
class ExtractedDecision:
    """Captures an architectural decision extracted from workflow context.

    Attributes:
        decision: The decision that was made
        rationale: Why the decision was made
        alternatives_considered: Other options that were evaluated
        importance: Importance level (9-10 for architectural)
        scope: Scope of impact ("system" or "component")
        keywords: Searchable keywords for the decision
        tags: Categorization tags
    """

    decision: str
    rationale: str
    alternatives_considered: List[str] = field(default_factory=list)
    importance: int = ImportanceLevel.ARCHITECTURAL_LOW  # 9
    scope: str = "component"  # "system" or "component"
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class ArchitecturalDecisionExtractor:
    """Extracts architectural decisions from workflow context.

    Detects decisions using pattern matching and extracts related metadata
    like rationale and alternatives considered.

    Patterns detected:
    - "chose X over Y" - technology/approach selection with alternative
    - "architecture uses X" - architectural pattern selection
    - "design decision: X" - explicit design decisions
    - "decided to use X" - usage decisions
    - "selected X for" - selection with purpose

    Note: Uses pre-compiled patterns from module level (COMPILED_DECISION_PATTERNS,
    COMPILED_SYSTEM_SCOPE_PATTERNS, COMPILED_COMPONENT_SCOPE_PATTERNS).

    Attributes:
        DECISION_PATTERNS: Reference to pre-compiled patterns (for backward compatibility)
    """

    # Class-level pattern strings (backward compatibility with tests)
    # Pre-compiled versions are available at module level (COMPILED_DECISION_PATTERNS)
    DECISION_PATTERNS = [
        r"chose\s+(\w+(?:\s+\w+)?)\s+over\s+(\w+(?:\s+\w+)?)",
        r"architecture\s+uses\s+(\w+(?:\s+\w+)?)",
        r"design\s+decision[:\s]+(.+?)(?:\.|$|\n)",
        r"decided\s+to\s+use\s+(\w+(?:\s+\w+)?)",
        r"selected\s+(\w+(?:\s+\w+)?)\s+for\s+",
    ]

    def detect_architectural_decisions(
        self, context: Dict[str, Any]
    ) -> List[ExtractedDecision]:
        """Scan workflow context for architectural decisions.

        Searches through all string values in the context dictionary
        for patterns indicating architectural decisions.

        Args:
            context: Dictionary containing workflow execution data

        Returns:
            List of ExtractedDecision objects for detected decisions
        """
        # Issue 7: Validate context is not None
        if context is None:
            return []

        decisions: List[ExtractedDecision] = []

        # Get all text content from context (using module-level function)
        text_content = extract_text_from_context(context)

        if not text_content:
            return decisions

        # Process each pre-compiled pattern
        for pattern_idx, compiled_pattern in enumerate(COMPILED_DECISION_PATTERNS):
            for text in text_content:
                matches = compiled_pattern.finditer(text)
                for match in matches:
                    decision = self._create_decision_from_match(
                        match, pattern_idx, text
                    )
                    if decision and not self._is_duplicate_decision(
                        decision, decisions
                    ):
                        decisions.append(decision)

        return decisions

    def _create_decision_from_match(
        self, match: re.Match, pattern_idx: int, full_text: str
    ) -> Optional[ExtractedDecision]:
        """Create ExtractedDecision from regex match.

        Args:
            match: The regex match object
            pattern_idx: Index of the pattern that matched
            full_text: The full text the match was found in

        Returns:
            ExtractedDecision or None if invalid
        """
        groups = match.groups()
        matched_text = match.group(0)

        # Build decision text based on pattern type
        if pattern_idx == 0:  # chose X over Y
            chosen = groups[0] if groups else ""
            alternative = groups[1] if len(groups) > 1 else ""
            decision_text = f"Chose {chosen} over {alternative}"
            alternatives = [alternative] if alternative else []
        elif pattern_idx == 1:  # architecture uses X
            tech = groups[0] if groups else ""
            decision_text = f"Architecture uses {tech}"
            alternatives = []
        elif pattern_idx == 2:  # design decision: X
            detail = groups[0].strip() if groups else ""
            decision_text = f"Design decision: {detail}"
            alternatives = []
        elif pattern_idx == 3:  # decided to use X
            tech = groups[0] if groups else ""
            decision_text = f"Decided to use {tech}"
            alternatives = []
        elif pattern_idx == 4:  # selected X for
            tech = groups[0] if groups else ""
            decision_text = f"Selected {tech}"
            alternatives = []
        else:
            decision_text = matched_text
            alternatives = []

        if not decision_text:
            return None

        # Extract rationale
        rationale = self.extract_rationale(full_text, matched_text)

        # Detect scope
        scope = self._detect_scope(full_text)

        # Generate keywords (using module-level function)
        keywords = generate_keywords(decision_text, max_keywords=10)

        # Generate tags
        tags = ["architecture", "decision"]

        return ExtractedDecision(
            decision=decision_text,
            rationale=rationale,
            alternatives_considered=alternatives,
            importance=ImportanceLevel.ARCHITECTURAL_LOW,  # Default, updated later
            scope=scope,
            keywords=keywords,
            tags=tags,
        )

    def _is_duplicate_decision(
        self, decision: ExtractedDecision, existing: List[ExtractedDecision]
    ) -> bool:
        """Check if decision is a duplicate of existing ones.

        Args:
            decision: The decision to check
            existing: List of existing decisions

        Returns:
            True if duplicate, False otherwise
        """
        for existing_decision in existing:
            # Check for exact match or high overlap
            if decision.decision.lower() == existing_decision.decision.lower():
                return True
            # Check for significant word overlap
            decision_words = set(decision.decision.lower().split())
            existing_words = set(existing_decision.decision.lower().split())
            overlap = len(decision_words & existing_words)
            if overlap >= len(decision_words) * DUPLICATE_OVERLAP_THRESHOLD:
                return True
        return False

    def extract_rationale(self, text: str, decision: str) -> str:
        """Extract rationale near the decision.

        Looks for common rationale indicators like "because", "for",
        "due to", "to achieve", etc.

        Args:
            text: The full text containing the decision
            decision: The decision text to find rationale for

        Returns:
            Extracted rationale or empty string if not found
        """
        # Find the position of the decision in the text
        decision_lower = decision.lower()
        text_lower = text.lower()

        # Find decision position (using first significant word if full match fails)
        decision_pos = text_lower.find(decision_lower)
        if decision_pos == -1:
            # Try to find position using key words from decision
            significant_words = [
                w for w in decision_lower.split() if len(w) > 3
            ]
            for word in significant_words:
                pos = text_lower.find(word)
                if pos != -1:
                    decision_pos = pos
                    break

        if decision_pos == -1:
            return ""

        # Get text after the decision
        after_text = text[decision_pos:]

        # Look for rationale patterns (using pre-compiled patterns)
        for compiled_pattern in COMPILED_RATIONALE_PATTERNS:
            match = compiled_pattern.search(after_text)
            if match:
                rationale = match.group(1).strip()
                # Limit rationale length using constant
                if len(rationale) > MAX_RATIONALE_LENGTH:
                    rationale = rationale[:MAX_RATIONALE_LENGTH - 3] + "..."
                return rationale

        return ""

    def _detect_scope(self, text: str) -> str:
        """Detect whether decision is system-wide or component-level.

        Args:
            text: The text to analyze for scope indicators

        Returns:
            "system" for system-wide, "component" for component-level
        """
        # Check for system-wide indicators (using pre-compiled patterns)
        for compiled_pattern in COMPILED_SYSTEM_SCOPE_PATTERNS:
            if compiled_pattern.search(text):
                return "system"

        # Check for component indicators (using pre-compiled patterns)
        for compiled_pattern in COMPILED_COMPONENT_SCOPE_PATTERNS:
            if compiled_pattern.search(text):
                return "component"

        # Default to component
        return "component"

    # ========================================================================
    # Task A2: Importance Assignment
    # ========================================================================

    def assign_importance(self, decision: ExtractedDecision) -> int:
        """Assign importance level based on decision scope.

        System-wide decisions get importance 10 (ARCHITECTURAL).
        Component-level decisions get importance 9 (ARCHITECTURAL_LOW).

        Args:
            decision: The ExtractedDecision to assign importance to

        Returns:
            Importance level (9 or 10)
        """
        if decision.scope == "system":
            return ImportanceLevel.ARCHITECTURAL  # 10
        else:
            return ImportanceLevel.ARCHITECTURAL_LOW  # 9


# ============================================================================
# Task B1-B2: ExtractedPattern and ImplementationPatternExtractor (Group B)
# ============================================================================


@dataclass
class ExtractedPattern:
    """Captures an implementation pattern extracted from workflow context.

    Attributes:
        pattern_name: Name of the pattern (e.g., "Retry with exponential backoff")
        description: What the pattern does
        context: Where/why this pattern was used
        reusability: How reusable this pattern is ("low", "medium", "high")
        category: Category of pattern (e.g., "retry", "caching", "validation")
        importance: Importance level (7-8 for patterns)
        keywords: Searchable keywords for the pattern
        tags: Categorization tags
    """

    pattern_name: str
    description: str
    context: str = ""
    reusability: str = "medium"  # "low", "medium", "high"
    category: str = ""  # e.g., "retry", "caching", "validation"
    importance: int = ImportanceLevel.PATTERN  # 7
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class ImplementationPatternExtractor:
    """Extracts implementation patterns from workflow context.

    Detects patterns using keyword matching and extracts related metadata
    like description and context.

    Patterns detected:
    - "used X pattern" - explicit pattern usage
    - "X approach" - approach description
    - "X technique" - technique description
    - "X strategy" - strategy description
    - "used X for Y" - usage with purpose
    - "implemented X" - implementation description

    Note: Uses pre-compiled patterns from module level (COMPILED_PATTERN_INDICATORS).

    Attributes:
        PATTERN_INDICATORS: Reference to pre-compiled patterns (for backward compatibility)
        CATEGORIES: Known pattern categories for classification
        CATEGORY_KEYWORDS: Mapping of keywords to categories
    """

    # Class-level pattern strings (backward compatibility with tests)
    # Pre-compiled versions are available at module level (COMPILED_PATTERN_INDICATORS)
    PATTERN_INDICATORS = [
        r"used\s+(\w+(?:\s+\w+)?)\s+pattern",
        r"(\w+(?:\s+\w+)?)\s+approach",
        r"(\w+(?:\s+\w+)?)\s+technique",
        r"(\w+(?:\s+\w+)?)\s+strategy",
        r"used\s+(\w+(?:\s+\w+)?)\s+for\s+(\w+(?:\s+\w+)*)",
        r"implemented\s+(\w+(?:\s+\w+)?)",
    ]

    # Known pattern categories (Task B2.1)
    CATEGORIES = [
        "retry",
        "caching",
        "validation",
        "error-handling",
        "logging",
        "testing",
        "integration",
    ]

    # Keywords that map to categories
    CATEGORY_KEYWORDS: Dict[str, List[str]] = {
        "retry": ["retry", "retries", "backoff", "exponential", "attempt", "reattempt"],
        "caching": ["cache", "caching", "cached", "memoization", "memoize", "memo"],
        "validation": ["validation", "validate", "validator", "verify", "check", "sanitize"],
        "error-handling": ["error", "exception", "handling", "handler", "catch", "throw", "graceful"],
        "logging": ["log", "logging", "logger", "structured", "audit", "trace"],
        "testing": ["test", "testing", "mock", "stub", "fixture", "doubles", "tdd"],
        "integration": ["integration", "integrate", "api", "external", "third-party", "connect"],
    }

    def detect_patterns(self, context: Dict[str, Any]) -> List[ExtractedPattern]:
        """Scan workflow context for implementation patterns.

        Searches through all string values in the context dictionary
        for patterns indicating implementation approaches.

        Args:
            context: Dictionary containing workflow execution data

        Returns:
            List of ExtractedPattern objects for detected patterns
        """
        # Issue 7: Validate context is not None
        if context is None:
            return []

        patterns: List[ExtractedPattern] = []

        # Get all text content from context (using module-level function)
        text_content = extract_text_from_context(context)

        if not text_content:
            return patterns

        # Process each pre-compiled pattern indicator
        for pattern_idx, compiled_pattern in enumerate(COMPILED_PATTERN_INDICATORS):
            for text in text_content:
                if not text:
                    continue
                matches = compiled_pattern.finditer(text)
                for match in matches:
                    pattern = self._create_pattern_from_match(
                        match, pattern_idx, text
                    )
                    if pattern and not self._is_duplicate_pattern(pattern, patterns):
                        patterns.append(pattern)

        return patterns

    def _create_pattern_from_match(
        self, match: re.Match, pattern_idx: int, full_text: str
    ) -> Optional[ExtractedPattern]:
        """Create ExtractedPattern from regex match.

        Args:
            match: The regex match object
            pattern_idx: Index of the pattern that matched
            full_text: The full text the match was found in

        Returns:
            ExtractedPattern or None if invalid
        """
        groups = match.groups()
        matched_text = match.group(0)

        # Build pattern name and description based on pattern type
        if pattern_idx == 0:  # used X pattern
            name = groups[0] if groups else ""
            pattern_name = f"{name} pattern"
            description = matched_text
        elif pattern_idx == 1:  # X approach
            name = groups[0] if groups else ""
            pattern_name = f"{name} approach"
            description = matched_text
        elif pattern_idx == 2:  # X technique
            name = groups[0] if groups else ""
            pattern_name = f"{name} technique"
            description = matched_text
        elif pattern_idx == 3:  # X strategy
            name = groups[0] if groups else ""
            pattern_name = f"{name} strategy"
            description = matched_text
        elif pattern_idx == 4:  # used X for Y
            tech = groups[0] if groups else ""
            purpose = groups[1] if len(groups) > 1 else ""
            pattern_name = f"{tech} for {purpose}"
            description = matched_text
        elif pattern_idx == 5:  # implemented X
            tech = groups[0] if groups else ""
            pattern_name = f"{tech} implementation"
            description = matched_text
        else:
            pattern_name = matched_text
            description = matched_text

        if not pattern_name.strip():
            return None

        # Capitalize first letter
        pattern_name = pattern_name.strip()
        pattern_name = pattern_name[0].upper() + pattern_name[1:] if pattern_name else ""

        # Generate keywords (using module-level function)
        combined = f"{pattern_name} {description}"
        keywords = generate_keywords(combined, max_keywords=10)

        # Generate tags
        tags = ["pattern", "implementation"]

        return ExtractedPattern(
            pattern_name=pattern_name,
            description=description,
            context="",
            reusability="medium",  # Default, can be adjusted
            category="",  # Will be set by categorize_pattern
            importance=ImportanceLevel.PATTERN,  # 7, may be adjusted
            keywords=keywords,
            tags=tags,
        )

    def _is_duplicate_pattern(
        self, pattern: ExtractedPattern, existing: List[ExtractedPattern]
    ) -> bool:
        """Check if pattern is a duplicate of existing ones.

        Args:
            pattern: The pattern to check
            existing: List of existing patterns

        Returns:
            True if duplicate, False otherwise
        """
        for existing_pattern in existing:
            # Check for exact match
            if pattern.pattern_name.lower() == existing_pattern.pattern_name.lower():
                return True
            # Check for significant word overlap
            pattern_words = set(pattern.pattern_name.lower().split())
            existing_words = set(existing_pattern.pattern_name.lower().split())
            overlap = len(pattern_words & existing_words)
            if pattern_words and overlap >= len(pattern_words) * DUPLICATE_OVERLAP_THRESHOLD:
                return True
        return False

    # ========================================================================
    # Task B2: Pattern Categorization and Importance Assignment
    # ========================================================================

    def categorize_pattern(self, pattern: ExtractedPattern) -> str:
        """Categorize pattern into known categories.

        Analyzes pattern name and description to determine the category.

        Args:
            pattern: The ExtractedPattern to categorize

        Returns:
            Category string (e.g., "retry", "caching") or empty string if unknown
        """
        # Combine name and description for analysis
        text = f"{pattern.pattern_name} {pattern.description}".lower()

        # Check each category's keywords
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return category

        # No category found
        return ""

    def assign_importance(self, pattern: ExtractedPattern) -> int:
        """Assign importance level based on pattern reusability.

        High reusability patterns get importance 8 (PATTERN_HIGH).
        Medium and low reusability patterns get importance 7 (PATTERN).

        Args:
            pattern: The ExtractedPattern to assign importance to

        Returns:
            Importance level (7 or 8)
        """
        if pattern.reusability == "high":
            return ImportanceLevel.PATTERN_HIGH  # 8
        else:
            return ImportanceLevel.PATTERN  # 7


# ============================================================================
# Task D1: ExtractedProblemSolution and ProblemSolutionExtractor (Group D)
# ============================================================================


@dataclass
class ExtractedProblemSolution:
    """Captures a problem-solution pair extracted from workflow context.

    Story 4.2 AC #5: Problem-solution pairs with problem signature
    and successful solution approach.

    Attributes:
        problem_signature: Hash-based signature for matching similar problems
        problem_description: Description of the problem encountered
        solution_approach: How the problem was resolved
        success_indicator: Evidence that the solution worked
        importance: Importance level (7-8 for problem-solution pairs)
        keywords: Searchable keywords
        tags: Categorization tags
    """

    problem_signature: str
    problem_description: str
    solution_approach: str
    success_indicator: str = ""
    importance: int = ImportanceLevel.PATTERN  # 7
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class ProblemSolutionExtractor:
    """Extracts problem-solution pairs from workflow context.

    Detects fix patterns where problems were identified and resolved,
    extracting both the problem description and solution approach.

    Task D1.4: Problem indicators include:
    - "fixed" - Something was fixed
    - "resolved" - Something was resolved
    - "solved" - Something was solved
    - "error" - An error occurred
    - "issue" - An issue was encountered
    - "bug" - A bug was found

    Note: Uses pre-compiled patterns from module level (COMPILED_PROBLEM_INDICATORS,
    COMPILED_FIX_PATTERN, etc.).

    Attributes:
        PROBLEM_INDICATORS: Reference to pre-compiled patterns (for backward compatibility)
        SOLUTION_INDICATORS: Solution detection patterns (for backward compatibility)
    """

    # Class-level pattern strings (backward compatibility with tests)
    # Pre-compiled versions are available at module level (COMPILED_PROBLEM_INDICATORS)
    PROBLEM_INDICATORS = [
        r"fixed\s+(.+?)(?:\s+by\s+|\.|$|\n)",
        r"resolved\s+(.+?)(?:\s+by\s+|\.|$|\n)",
        r"solved\s+(.+?)(?:\s+by\s+|\.|$|\n)",
        r"error[:\s]+(.+?)(?:\s*[-–]\s*|\.|$|\n)",
        r"issue[:\s]+(.+?)(?:\s+resolved|\s+fixed|\.|$|\n)",
        r"bug\s+(?:in\s+)?(.+?)(?:\s+was\s+fixed|\s+fixed|\.|$|\n)",
    ]

    # Solution detection patterns (backward compatibility)
    SOLUTION_INDICATORS = [
        r"by\s+(.+?)(?:\.|$|\n)",
        r"solution[:\s]+(.+?)(?:\.|$|\n)",
        r"fix[:\s]+(.+?)(?:\.|$|\n)",
        r"workaround[:\s]+(.+?)(?:\.|$|\n)",
        r"resolved\s+by\s+(.+?)(?:\.|$|\n)",
        r"fixed\s+by\s+(.+?)(?:\.|$|\n)",
    ]

    def detect_problem_solutions(
        self, context: Dict[str, Any]
    ) -> List[ExtractedProblemSolution]:
        """Scan workflow context for problem-solution pairs.

        Task D1.3: Searches through context for patterns indicating
        problems that were fixed, resolved, or solved.

        Args:
            context: Dictionary containing workflow execution data

        Returns:
            List of ExtractedProblemSolution objects for detected pairs
        """
        # Issue 7: Validate context is not None
        if context is None:
            return []

        pairs: List[ExtractedProblemSolution] = []

        # Get all text content from context (using module-level function)
        text_content = extract_text_from_context(context)

        if not text_content:
            return pairs

        # Process each text block
        for text in text_content:
            if not text:
                continue
            found_pairs = self._find_problem_solution_pairs(text)
            for pair in found_pairs:
                if not self._is_duplicate_pair(pair, pairs):
                    pairs.append(pair)

        return pairs

    def _find_problem_solution_pairs(
        self, text: str
    ) -> List[ExtractedProblemSolution]:
        """Find problem-solution pairs in text.

        Args:
            text: The text to search

        Returns:
            List of ExtractedProblemSolution objects
        """
        pairs: List[ExtractedProblemSolution] = []

        # Try to find fix patterns (most reliable) using pre-compiled patterns
        # Pattern: "Fixed X by Y"
        for match in COMPILED_FIX_PATTERN.finditer(text):
            problem = match.group(1).strip()
            solution = match.group(2).strip()
            if problem and solution:
                pair = self.link_problem_to_solution(problem, solution)
                pairs.append(pair)

        # Pattern: "Error: X - fixed by Y"
        for match in COMPILED_ERROR_FIX_PATTERN.finditer(text):
            problem = match.group(1).strip()
            solution = match.group(2).strip()
            if problem and solution:
                pair = self.link_problem_to_solution(problem, solution)
                pairs.append(pair)

        # Pattern: "Issue with X resolved by Y"
        for match in COMPILED_ISSUE_PATTERN.finditer(text):
            problem = match.group(1).strip()
            solution = match.group(2).strip()
            if problem and solution:
                pair = self.link_problem_to_solution(problem, solution)
                pairs.append(pair)

        # Pattern: "Bug in X was fixed by Y"
        for match in COMPILED_BUG_PATTERN.finditer(text):
            problem = match.group(1).strip()
            solution = match.group(2).strip()
            if problem and solution:
                pair = self.link_problem_to_solution(f"Bug in {problem}", solution)
                pairs.append(pair)

        # If no pairs found with "by", try simpler patterns
        if not pairs:
            # Pattern: "Fixed X" (solution is implicit)
            for match in COMPILED_SIMPLE_FIX_PATTERN.finditer(text):
                problem_solution = match.group(1).strip()

                # Try to split on "by" if present
                if " by " in problem_solution.lower():
                    parts = re.split(r"\s+by\s+", problem_solution, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        problem = parts[0].strip()
                        solution = parts[1].strip()
                        pair = self.link_problem_to_solution(problem, solution)
                        pairs.append(pair)
                        continue

                # Use the full match as both problem and implied solution
                pair = self.link_problem_to_solution(
                    problem_solution,
                    f"Applied fix: {problem_solution}"
                )
                pairs.append(pair)

        return pairs

    def _is_duplicate_pair(
        self, pair: ExtractedProblemSolution,
        existing: List[ExtractedProblemSolution]
    ) -> bool:
        """Check if pair is a duplicate of existing ones.

        Args:
            pair: The pair to check
            existing: List of existing pairs

        Returns:
            True if duplicate, False otherwise
        """
        for existing_pair in existing:
            # Check signature match
            if pair.problem_signature == existing_pair.problem_signature:
                return True
            # Check for similar problem descriptions
            pair_words = set(pair.problem_description.lower().split())
            existing_words = set(existing_pair.problem_description.lower().split())
            if pair_words and existing_words:
                overlap = len(pair_words & existing_words)
                min_len = min(len(pair_words), len(existing_words))
                if min_len > 0 and overlap >= min_len * DUPLICATE_OVERLAP_THRESHOLD:
                    return True
        return False

    # ========================================================================
    # Task D2: Solution Linking and Signature Generation
    # ========================================================================

    def link_problem_to_solution(
        self, problem: str, solution: str
    ) -> ExtractedProblemSolution:
        """Create linked problem-solution pair.

        Task D2.1: Pairs related problem and solution content together
        with appropriate metadata for memory storage.

        Args:
            problem: Description of the problem
            solution: Description of the solution

        Returns:
            ExtractedProblemSolution with linked content
        """
        # Generate problem signature (Task D2.2)
        signature = self.generate_problem_signature(problem)

        # Generate keywords from both problem and solution (using module-level function)
        combined = f"{problem} {solution}"
        keywords = generate_keywords(combined, max_keywords=10)

        # Generate tags
        tags = ["problem-solution", "fix-pattern"]

        # Determine success indicator (empty for now, set by context)
        success_indicator = ""

        # Create the pair with importance 7 by default
        pair = ExtractedProblemSolution(
            problem_signature=signature,
            problem_description=problem,
            solution_approach=solution,
            success_indicator=success_indicator,
            importance=ImportanceLevel.PATTERN,  # 7, may be upgraded to 8
            keywords=keywords,
            tags=tags,
        )

        # Assign final importance based on solution quality
        pair.importance = self.assign_importance(pair)

        return pair

    def generate_problem_signature(self, problem: str) -> str:
        """Generate hash-based signature for future matching.

        Task D2.2: Creates a deterministic signature from the problem
        description that can be used to find similar problems.

        Args:
            problem: The problem description

        Returns:
            Hash-based signature string
        """
        # Normalize the problem text
        normalized = self._normalize_text(problem)

        # Generate MD5 hash (fast, sufficient for matching)
        hash_value = hashlib.md5(normalized.encode("utf-8")).hexdigest()

        return f"hash:{hash_value[:16]}"

    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent hashing.

        Args:
            text: The text to normalize

        Returns:
            Normalized text
        """
        # Convert to lowercase
        normalized = text.lower()

        # Normalize whitespace (multiple spaces/tabs to single space)
        normalized = re.sub(r"\s+", " ", normalized)

        # Strip leading/trailing whitespace
        normalized = normalized.strip()

        return normalized

    # ========================================================================
    # Task D2.3: Importance Assignment for Problem-Solution Pairs
    # ========================================================================

    def assign_importance(self, pair: ExtractedProblemSolution) -> int:
        """Assign importance 7-8 based on solution quality.

        Task D2.3: Problem-solution pairs get importance 7-8.
        - 8 for detailed solutions with success indicators
        - 7 for simple solutions without verification

        Args:
            pair: The ExtractedProblemSolution to evaluate

        Returns:
            Importance level (7 or 8)
        """
        # Start with base importance of 7
        importance = ImportanceLevel.PATTERN  # 7

        # Check for indicators of a high-quality solution
        high_quality_indicators = 0

        # Has success indicator
        if pair.success_indicator and len(pair.success_indicator) >= 10:
            high_quality_indicators += 1

        # Has detailed solution (more than just a few words)
        solution_words = pair.solution_approach.split()
        if len(solution_words) >= 10:
            high_quality_indicators += 1

        # Has detailed problem description
        problem_words = pair.problem_description.split()
        if len(problem_words) >= 5:
            high_quality_indicators += 1

        # If enough high-quality indicators, upgrade to 8
        if high_quality_indicators >= 2:
            importance = ImportanceLevel.PATTERN_HIGH  # 8

        return importance


# ============================================================================
# Task C1: ExtractedMilestone and MilestoneExtractor (Group C)
# ============================================================================


@dataclass
class ExtractedMilestone:
    """Captures a milestone completion extracted from workflow context.

    Story 4.2 AC #4: Milestone completions with importance 6-7.
    Epic/phase completions get 7, story completions get 6.

    Attributes:
        milestone_name: Name/description of the milestone
        scope: Level of the milestone ("epic", "phase", "story", "task")
        completion_date: Optional date when completed
        importance: Importance level (6-7 for milestones)
        keywords: Searchable keywords
        tags: Categorization tags
    """

    milestone_name: str
    scope: str = "story"  # epic, phase, story, task
    completion_date: Optional[str] = None
    importance: int = ImportanceLevel.MILESTONE  # 6
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class MilestoneExtractor:
    """Extracts milestone completions from workflow context.

    Detects when phases, epics, stories, or features are completed,
    assigning appropriate importance based on scope.

    Task C1.4: Completion indicators include:
    - "complete/completed" - Something was completed
    - "finished" - Something was finished
    - "done" - Something is done
    - "shipped" - Something was shipped
    - "released" - Something was released

    Note: Uses pre-compiled patterns from module level (COMPILED_COMPLETION_INDICATORS,
    COMPILED_NEGATION_PATTERNS).

    Attributes:
        COMPLETION_INDICATORS: Reference to pre-compiled patterns (for backward compatibility)
        SCOPE_KEYWORDS: Mapping of scope types to importance levels
        NEGATION_PATTERNS: Patterns to filter false positives (for backward compatibility)
    """

    # Class-level pattern strings (backward compatibility with tests)
    # Pre-compiled versions are available at module level (COMPILED_COMPLETION_INDICATORS)
    COMPLETION_INDICATORS = [
        r"([\w\-\.]+(?:\s+[\w\-\.]+){0,5})\s+(?:is\s+)?complete[d]?\b",
        r"([\w\-\.]+(?:\s+[\w\-\.]+){0,5})\s+finished\b",
        r"([\w\-\.]+(?:\s+[\w\-\.]+){0,5})\s+(?:is\s+)?done\b",
        r"([\w\-\.]+(?:\s+[\w\-\.]+){0,5})\s+shipped\b",
        r"([\w\-\.]+(?:\s+[\w\-\.]+){0,5})\s+released\b",
        r"completed\s+([\w\-\.]+(?:\s+[\w\-\.]+){0,5})",
    ]

    # Negation patterns to filter false positives (backward compatibility)
    NEGATION_PATTERNS = [
        r"not\s+(?:yet\s+)?(?:complete|done|finished)",
        r"isn['`]t\s+(?:complete|done|finished)",
        r"still\s+incomplete",
        r"not\s+done",
        r"incomplete",
    ]

    # Task C2.2: Scope to importance mapping
    # Epic/phase = 7, Story/task = 6
    SCOPE_KEYWORDS = {
        "epic": 7,
        "phase": 7,
        "story": 6,
        "task": 6,
    }

    def detect_milestones(self, context: Dict[str, Any]) -> List[ExtractedMilestone]:
        """Scan workflow context for milestone completions.

        Task C1.3: Searches through context for patterns indicating
        completions of phases, epics, stories, or features.

        Args:
            context: Dictionary containing workflow execution data

        Returns:
            List of ExtractedMilestone objects for detected completions
        """
        # Issue 7: Validate context is not None
        if context is None:
            return []

        milestones: List[ExtractedMilestone] = []

        # Get all text content from context (using module-level function)
        text_content = extract_text_from_context(context)

        if not text_content:
            return milestones

        # Collect unique milestone names to avoid duplicates
        seen_milestone_names: Set[str] = set()

        # Process each text block
        for text in text_content:
            if not text:
                continue

            # Skip if text contains negation patterns
            if self._contains_negation(text):
                continue

            # Find milestones in this text
            found_milestones = self._find_milestones_in_text(text)
            for milestone in found_milestones:
                # Normalize milestone name for deduplication
                normalized_name = milestone.milestone_name.lower().strip()
                if normalized_name not in seen_milestone_names:
                    seen_milestone_names.add(normalized_name)
                    milestones.append(milestone)

        return milestones

    def _contains_negation(self, text: str) -> bool:
        """Check if text contains negation patterns.

        Args:
            text: The text to check

        Returns:
            True if negation pattern found, False otherwise
        """
        # Use pre-compiled negation patterns
        for compiled_pattern in COMPILED_NEGATION_PATTERNS:
            if compiled_pattern.search(text):
                return True
        return False

    def _find_milestones_in_text(self, text: str) -> List[ExtractedMilestone]:
        """Find milestone completions in text.

        Args:
            text: The text to search

        Returns:
            List of ExtractedMilestone objects
        """
        milestones: List[ExtractedMilestone] = []

        # Use pre-compiled completion indicators
        for compiled_pattern in COMPILED_COMPLETION_INDICATORS:
            for match in compiled_pattern.finditer(text):
                milestone_name = match.group(1).strip()

                # Skip very short or generic matches
                if len(milestone_name) < 3:
                    continue

                # Skip if just the completion word itself
                skip_words = {"is", "was", "been", "being", "have", "has"}
                if milestone_name.lower() in skip_words:
                    continue

                # Determine scope from milestone name
                scope = self.determine_scope(milestone_name, {})

                # Assign importance based on scope
                importance = self.assign_importance(
                    ExtractedMilestone(milestone_name=milestone_name, scope=scope)
                )

                # Generate keywords (using module-level function)
                # Add "complete" as milestone-specific keyword
                keywords = generate_keywords(milestone_name, max_keywords=9)
                if "complete" not in keywords:
                    keywords.append("complete")

                # Generate tags
                tags = ["milestone", scope]

                milestone = ExtractedMilestone(
                    milestone_name=milestone_name,
                    scope=scope,
                    completion_date=None,  # Could extract from context
                    importance=importance,
                    keywords=keywords,
                    tags=tags,
                )
                milestones.append(milestone)

        return milestones

    def determine_scope(self, milestone_name: str, context: Dict[str, Any]) -> str:
        """Determine if milestone is story, epic, phase, or task level.

        Args:
            milestone_name: The name of the milestone
            context: Additional context (currently unused)

        Returns:
            Scope string: "epic", "phase", "story", or "task"
        """
        name_lower = milestone_name.lower()

        # Check for explicit scope keywords
        if "epic" in name_lower:
            return "epic"
        if "phase" in name_lower:
            return "phase"
        if "story" in name_lower:
            return "story"
        if "task" in name_lower:
            return "task"

        # Default to story level
        return "story"

    def assign_importance(self, milestone: ExtractedMilestone) -> int:
        """Assign importance level based on milestone scope.

        Task C2.1, C2.2: Assigns importance 6-7 based on scope.
        - Epic/phase completions get importance 7
        - Story/task completions get importance 6

        Args:
            milestone: The ExtractedMilestone to assign importance to

        Returns:
            Importance level (6 or 7)
        """
        # Look up scope in SCOPE_KEYWORDS mapping
        importance = self.SCOPE_KEYWORDS.get(
            milestone.scope.lower(),
            ImportanceLevel.MILESTONE,  # Default to 6
        )
        return importance


# ============================================================================
# Task E1, E2: DuplicationChecker (AC: #6)
# ============================================================================


@dataclass
class LinkResult:
    """Result of a duplication check.

    Indicates whether content should be linked to an existing memory
    instead of creating a new one.

    Attributes:
        should_link: True if content duplicates existing memory
        existing_memory_id: ID of the existing memory to link to
        similarity_score: How similar the content is (0.0-1.0)
    """

    should_link: bool
    existing_memory_id: Optional[int] = None
    similarity_score: float = 0.0


class DuplicationChecker:
    """Checks for duplicate memories before creating new ones.

    Task E1.1: Queries Forgetful MCP to find similar existing memories
    and determines whether to link instead of create.

    Attributes:
        _mcp_client: Optional callable for MCP tool invocation
    """

    def __init__(self, mcp_client: Optional[Any] = None):
        """Initialize DuplicationChecker.

        Args:
            mcp_client: Optional callable for Forgetful MCP queries.
                       Signature: mcp_client(tool_name: str, args: dict) -> dict
        """
        self._mcp_client = mcp_client

    def check_for_duplicates(
        self, content: str, keywords: List[str]
    ) -> LinkResult:
        """Query Forgetful for similar memories.

        Task E1.2: Searches existing memories for similar content
        and returns whether to link instead of create.

        Args:
            content: The content to check for duplicates
            keywords: Keywords to use for searching

        Returns:
            LinkResult indicating if duplicate found and details
        """
        # If no MCP client or empty content, can't check for duplicates
        if not self._mcp_client or not content:
            return LinkResult(should_link=False)

        try:
            # Query Forgetful for similar memories using keywords
            query_args = {
                "query": " ".join(keywords) if keywords else content[:100],
                "query_context": "Checking for duplicate memories",
                "include_links": False,
            }
            result = self._mcp_client("query_memory", query_args)

            # Check each returned memory for similarity
            memories = result.get("memories", [])
            for memory in memories:
                existing_content = memory.get("content", "")
                memory_id = memory.get("id")

                if existing_content and memory_id is not None:
                    score = self.similarity_score(content, existing_content)
                    if score >= DUPLICATE_OVERLAP_THRESHOLD:
                        return LinkResult(
                            should_link=True,
                            existing_memory_id=memory_id,
                            similarity_score=score,
                        )

        except Exception:
            # If query fails, allow creating new memory
            pass

        return LinkResult(should_link=False)

    def similarity_score(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings.

        Task E1.3: Uses word-based Jaccard similarity for comparison.
        Case-insensitive comparison.

        Args:
            content1: First content string
            content2: Second content string

        Returns:
            Similarity score from 0.0 (different) to 1.0 (identical)
        """
        # Handle empty strings
        if not content1 and not content2:
            return 1.0  # Both empty = identical
        if not content1 or not content2:
            return 0.0  # One empty = no similarity

        # Normalize and tokenize
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        # Handle edge case of no words
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return 0.0

        return intersection / union

    def link_to_existing(self, memory_id: int) -> LinkResult:
        """Return result indicating link to existing memory.

        Task E2.1: Creates a LinkResult for linking to an existing
        memory instead of creating a duplicate.

        Args:
            memory_id: ID of the existing memory to link to

        Returns:
            LinkResult with should_link=True and the memory ID
        """
        return LinkResult(
            should_link=True,
            existing_memory_id=memory_id,
            similarity_score=1.0,  # Perfect match when explicitly linking
        )


# ============================================================================
# Task F1, F2: PostWorkflowCurator and CurationReport (AC: #1)
# ============================================================================


@dataclass
class CurationReport:
    """Report of extraction and curation results.

    Task F2.1: Tracks counts of memories created, linked, and skipped
    during post-workflow curation.

    Attributes:
        memories_created: Number of new memories created
        memories_linked: Number of items linked to existing memories
        skipped_duplicates: Number of items skipped as duplicates
        items_by_type: Count of extracted items by type
    """

    memories_created: int = 0
    memories_linked: int = 0
    skipped_duplicates: int = 0
    items_by_type: Dict[str, int] = field(default_factory=dict)


class PostWorkflowCurator:
    """Orchestrates post-workflow learning extraction.

    Task F1.1: Coordinates all extractors to analyze workflow sessions
    and extract key learnings for memory persistence.

    Integrates:
    - ArchitecturalDecisionExtractor (importance 9-10)
    - ImplementationPatternExtractor (importance 7-8)
    - MilestoneExtractor (importance 6-7)
    - ProblemSolutionExtractor (importance 7-8)
    - DuplicationChecker (prevents duplicates)

    Attributes:
        arch_extractor: Extractor for architectural decisions
        pattern_extractor: Extractor for implementation patterns
        milestone_extractor: Extractor for milestones
        problem_extractor: Extractor for problem-solution pairs
        dedup_checker: Checker for duplicate memories
        _mcp_client: Optional callable for MCP tool invocation
    """

    def __init__(self, mcp_client: Optional[Any] = None):
        """Initialize PostWorkflowCurator.

        Args:
            mcp_client: Optional callable for Forgetful MCP operations.
                       Signature: mcp_client(tool_name: str, args: dict) -> dict
        """
        self._mcp_client = mcp_client
        self.arch_extractor = ArchitecturalDecisionExtractor()
        self.pattern_extractor = ImplementationPatternExtractor()
        self.milestone_extractor = MilestoneExtractor()
        self.problem_extractor = ProblemSolutionExtractor()
        self.dedup_checker = DuplicationChecker(mcp_client)

    def analyze_session(self, context: Dict[str, Any]) -> CurationReport:
        """Analyze workflow session and extract learnings.

        Task F1.1: Calls all extractors, runs duplication checks,
        and generates a curation report.

        Args:
            context: Dictionary containing workflow execution data

        Returns:
            CurationReport with extraction results
        """
        # Task F1.2: Collect all extracted items
        results: Dict[str, List[Any]] = {
            "decisions": [],
            "patterns": [],
            "milestones": [],
            "problem_solutions": [],
        }

        # Extract architectural decisions
        results["decisions"] = self.arch_extractor.detect_architectural_decisions(
            context
        )

        # Extract implementation patterns
        results["patterns"] = self.pattern_extractor.detect_patterns(context)

        # Extract milestones
        results["milestones"] = self.milestone_extractor.detect_milestones(context)

        # Extract problem-solution pairs
        results["problem_solutions"] = self.problem_extractor.detect_problem_solutions(
            context
        )

        # Task F2: Generate the report
        return self._create_report(results)

    def _create_report(self, results: Dict[str, List[Any]]) -> CurationReport:
        """Generate curation report from results.

        Task F2.1, F2.2: Creates a CurationReport with counts by type
        and memory operation statistics.

        Args:
            results: Dictionary of extracted items by type

        Returns:
            CurationReport with counts and statistics
        """
        # Count items by type
        items_by_type = {
            "decisions": len(results.get("decisions", [])),
            "patterns": len(results.get("patterns", [])),
            "milestones": len(results.get("milestones", [])),
            "problem_solutions": len(results.get("problem_solutions", [])),
        }

        # For now, without Memory Bridge integration, all items are
        # counted but not actually persisted
        # TODO: Integrate with Memory Bridge for actual persistence
        total_items = sum(items_by_type.values())

        return CurationReport(
            memories_created=0,  # No MCP client = no persistence
            memories_linked=0,
            skipped_duplicates=0,
            items_by_type=items_by_type,
        )