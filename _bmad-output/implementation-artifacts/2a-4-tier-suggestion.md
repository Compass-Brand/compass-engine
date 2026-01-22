# Story 2a.4: Tier Suggestion - Implementation Spec

**Epic:** 2a - Workflow Entry & Detection
**Story:** 2a.4 - Tier Suggestion
**Created:** 2026-01-12
**Status:** In Progress

## Story Definition

**As a** workflow user,
**I want** the system to recommend an appropriate project tier (0-4) based on my description,
**So that** the methodology depth matches my project's actual complexity.

## Acceptance Criteria

| AC# | Given | When | Then |
|-----|-------|------|------|
| 1 | User description containing "fix", "bug", "typo", or "patch" | Tier Suggester analyzes description | Suggests tier: 0 with matched keywords |
| 2 | User description containing "platform", "integration", "complex system" | Tier Suggester analyzes description | Suggests tier: 3 with matched keywords |
| 3 | Description with mixed signals ("simple dashboard with complex integrations") | Tier Suggester analyzes description | Suggests tier indicated by >50% of keywords with confidence score |
| 4 | Description with no recognizable tier keywords | Tier Suggester analyzes description | Defaults to tier: 2 with confidence: "low" |
| 5 | Brownfield project with existing codebase metrics | Tier Suggester combines description + code metrics | Adjusts tier based on codebase size/complexity |

## Tier Definitions (from BMAD)

| Tier | Name | Keywords | Description |
|------|------|----------|-------------|
| 0 | Single Atomic Change | fix, bug, typo, patch, hotfix, tweak | Minimal change, single file |
| 1 | Small Feature | small, simple, quick, minor, basic, straightforward | Small addition or change |
| 2 | Medium Project | feature, component, module, service | Standard feature work (DEFAULT) |
| 3 | Complex System | platform, integration, complex, enterprise, multi-component | Cross-cutting concerns |
| 4 | Enterprise/Regulated | compliance, regulated, audit, security-critical, healthcare, finance | Compliance requirements |

## Module Design

### File: `pcmrp_tools/bmad_automation/tier_suggester.py`

### Data Structures

```python
class ProjectTier(Enum):
    """Project complexity tier (0-4)."""
    TIER_0 = 0  # Single Atomic Change
    TIER_1 = 1  # Small Feature
    TIER_2 = 2  # Medium Project
    TIER_3 = 3  # Complex System
    TIER_4 = 4  # Enterprise/Regulated

class TierConfidence(Enum):
    """Confidence level in tier suggestion."""
    HIGH = "high"      # >66% keywords match single tier
    MEDIUM = "medium"  # 34-66% keywords match single tier
    LOW = "low"        # <34% or no keywords matched

@dataclass
class TierSuggestion:
    """Result of tier suggestion analysis."""
    tier: ProjectTier
    confidence: TierConfidence
    matched_keywords: list[str]
    reasoning: str
    all_matches: dict[ProjectTier, list[str]]  # All keyword matches by tier
```

### Constants

```python
TIER_KEYWORDS: dict[ProjectTier, frozenset[str]] = {
    ProjectTier.TIER_0: frozenset({"fix", "bug", "typo", "patch", "hotfix", "tweak"}),
    ProjectTier.TIER_1: frozenset({"small", "simple", "quick", "minor", "basic", "straightforward"}),
    ProjectTier.TIER_2: frozenset({"feature", "component", "module", "service"}),
    ProjectTier.TIER_3: frozenset({"platform", "integration", "complex", "enterprise", "multi-component"}),
    ProjectTier.TIER_4: frozenset({"compliance", "regulated", "audit", "security-critical", "healthcare", "finance"}),
}

DEFAULT_TIER = ProjectTier.TIER_2
```

### Functions

1. **analyze_description(description: str) -> dict[ProjectTier, list[str]]**
   - Tokenize and normalize description
   - Match tokens against TIER_KEYWORDS
   - Return all matches by tier

2. **calculate_keyword_confidence(matches: dict[ProjectTier, list[str]]) -> TierConfidence**
   - Count total matches
   - Calculate percentage for dominant tier
   - Return HIGH (>66%), MEDIUM (34-66%), or LOW (<34% or no matches)

3. **analyze_codebase_metrics(project_result: ProjectTypeResult) -> Optional[int]**
   - If brownfield with many files, suggest tier adjustment
   - Large codebase (>100 files) → +1 tier adjustment
   - Very large codebase (>500 files) → +2 tier adjustment
   - Return adjustment value or None for greenfield

4. **suggest_tier(description: str, project_path: Optional[Path] = None) -> TierSuggestion**
   - Main entry point
   - Call analyze_description() for keyword analysis
   - If project_path provided, call detect_project_type() and analyze_codebase_metrics()
   - Combine signals and return TierSuggestion

## Dependencies

- `workflow_entry_wrapper.py`: `detect_project_type()`, `ProjectTypeResult`, `count_source_files()`

## Test Cases

### AC1: Tier 0 Detection
- "Fix the bug in the login page" → Tier 0
- "Apply hotfix for memory leak" → Tier 0
- "Correct typo in README" → Tier 0

### AC2: Tier 3 Detection
- "Build a new integration platform" → Tier 3
- "Design complex multi-component system" → Tier 3
- "Enterprise-wide dashboard" → Tier 3

### AC3: Mixed Signals
- "Simple dashboard with complex integrations" → Tier depends on keyword count
- Confidence should reflect mixed signals

### AC4: No Keywords
- "Do something with the code" → Tier 2 (default), LOW confidence
- "Update the stuff" → Tier 2 (default), LOW confidence

### AC5: Brownfield Adjustment
- Description says "small fix" but codebase has 200 files → Adjust tier up
- Greenfield project → No adjustment

## Implementation Notes

1. Keyword matching is case-insensitive
2. Multi-word keywords (e.g., "multi-component") require special handling
3. Codebase metrics are optional enhancement, not required for basic suggestion
4. The suggest_tier() function should be usable without a project path
