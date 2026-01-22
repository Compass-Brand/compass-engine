"""Adaptive Behavior Configuration for BMAD Automation.

This module provides functionality to calibrate automation behavior based on:
1. Project tier (0-4) - complexity level from atomic change to enterprise
2. Domain classification - regulated domains like healthcare/finance
3. Custom confidence thresholds - workflow-specific threshold overrides

Story: 2a.7 - Adaptive Behavior Configuration
Epic: 2a - Workflow Entry & Detection

Tier -> Behavior Mapping:
    | Level | Human Gates | Subagent Depth | Party Mode | Validation Scope |
    |-------|-------------|----------------|------------|------------------|
    | 0-1   | Final only  | Single         | Deadlock   | Workflow-specific|
    | 2     | Design+Final| Parallel       | Deadlock+  | WF-specific+CR   |
    | 3     | Arch+Des+Fin| Parallel       | Deadlock++ | Full+thorough    |
    | 4     | All major   | Party consensus| Every phase| Full+consensus   |

Examples:
    >>> from pcmrp_tools.bmad_automation.tier_suggester import ProjectTier
    >>> config = create_behavior_config(ProjectTier.TIER_0)
    >>> config.profile.batch_size
    'auto-all'

    >>> config = create_behavior_config(ProjectTier.TIER_4, domain="healthcare")
    >>> config.domain_config.audit_logging
    True
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .tier_suggester import ProjectTier


# =============================================================================
# Constants
# =============================================================================

# Default confidence thresholds
DEFAULT_HIGH_THRESHOLD = 80
DEFAULT_MEDIUM_THRESHOLD = 50

# Valid checkpoint frequency values
VALID_CHECKPOINT_FREQUENCIES = frozenset({
    "minimal",
    "standard",
    "frequent",
    "every-step",
})

# Valid validation scope values
VALID_VALIDATION_SCOPES = frozenset({
    "workflow-specific",
    "full",
    "full+consensus",
})

# Regulated domains that require additional validation gates
REGULATED_DOMAINS: frozenset[str] = frozenset({"healthcare", "finance"})


# =============================================================================
# Dataclasses
# =============================================================================


@dataclass
class BehaviorProfile:
    """Automation behavior profile for a project tier.

    Attributes:
        batch_size: Number of steps to execute per batch, or "auto-all" for
            automatic batching of all steps.
        checkpoint_frequency: How often to pause for validation.
            Values: "minimal", "standard", "frequent", "every-step"
        human_gates: List of phases requiring human approval.
            Common values: "architecture", "design", "final"
        validation_scope: Scope of validation to perform.
            Values: "workflow-specific", "full", "full+consensus"
    """

    batch_size: int | str
    checkpoint_frequency: str
    human_gates: list[str]
    validation_scope: str

    def __post_init__(self) -> None:
        """Validate profile values after initialization."""
        # Validate batch_size
        if not isinstance(self.batch_size, (int, str)):
            raise ValueError(
                f"batch_size must be int or str, got {type(self.batch_size).__name__}"
            )
        if isinstance(self.batch_size, str) and self.batch_size != "auto-all":
            raise ValueError(
                f"batch_size string must be 'auto-all', got {self.batch_size!r}"
            )

        # Validate checkpoint_frequency
        if self.checkpoint_frequency not in VALID_CHECKPOINT_FREQUENCIES:
            raise ValueError(
                f"Invalid checkpoint_frequency: {self.checkpoint_frequency!r}. "
                f"Must be one of: {', '.join(sorted(VALID_CHECKPOINT_FREQUENCIES))}"
            )

        # Validate validation_scope
        if self.validation_scope not in VALID_VALIDATION_SCOPES:
            raise ValueError(
                f"Invalid validation_scope: {self.validation_scope!r}. "
                f"Must be one of: {', '.join(sorted(VALID_VALIDATION_SCOPES))}"
            )


@dataclass
class ConfidenceThresholds:
    """Confidence thresholds for automated decision-making.

    Attributes:
        high_threshold: Minimum confidence score to proceed automatically
            without human review (default 80).
        medium_threshold: Minimum confidence score for tentative decisions
            that may need confirmation (default 50).
    """

    high_threshold: int = DEFAULT_HIGH_THRESHOLD
    medium_threshold: int = DEFAULT_MEDIUM_THRESHOLD


@dataclass
class RegulatedDomainConfig:
    """Configuration for regulated domains (healthcare, finance).

    Attributes:
        domain: The regulated domain name (e.g., "healthcare", "finance")
        extra_validation_gates: Additional validation gates required for
            this domain (e.g., ["hipaa_check", "phi_scan"])
        audit_logging: Whether audit logging is enabled for this domain
    """

    domain: str
    extra_validation_gates: list[str]
    audit_logging: bool


@dataclass
class AdaptiveBehaviorConfig:
    """Complete adaptive behavior configuration for a project.

    Combines tier-based profile, confidence thresholds, and optional
    domain-specific configuration.

    Attributes:
        tier: The project complexity tier (TIER_0 through TIER_4)
        profile: The behavior profile with batch size, checkpoints, etc.
        thresholds: Confidence thresholds for automated decisions
        domain_config: Optional regulated domain configuration
    """

    tier: ProjectTier
    profile: BehaviorProfile
    thresholds: ConfidenceThresholds = field(default_factory=ConfidenceThresholds)
    domain_config: RegulatedDomainConfig | None = None


# =============================================================================
# Tier Profile Definitions
# =============================================================================

# Default behavior profiles for each project tier
# Based on the tier-behavior mapping from the design spec
TIER_PROFILES: dict[ProjectTier, BehaviorProfile] = {
    # Tier 0-1: Simple projects - aggressive automation
    ProjectTier.TIER_0: BehaviorProfile(
        batch_size="auto-all",
        checkpoint_frequency="minimal",
        human_gates=["final"],
        validation_scope="workflow-specific",
    ),
    ProjectTier.TIER_1: BehaviorProfile(
        batch_size="auto-all",
        checkpoint_frequency="minimal",
        human_gates=["final"],
        validation_scope="workflow-specific",
    ),
    # Tier 2: Medium projects - standard automation
    ProjectTier.TIER_2: BehaviorProfile(
        batch_size=5,
        checkpoint_frequency="standard",
        human_gates=["design", "final"],
        validation_scope="workflow-specific",
    ),
    # Tier 3: Complex projects - conservative automation
    ProjectTier.TIER_3: BehaviorProfile(
        batch_size=3,
        checkpoint_frequency="frequent",
        human_gates=["architecture", "design", "final"],
        validation_scope="full",
    ),
    # Tier 4: Enterprise/Regulated - most conservative
    ProjectTier.TIER_4: BehaviorProfile(
        batch_size=1,
        checkpoint_frequency="every-step",
        human_gates=["architecture", "design", "implementation", "final"],
        validation_scope="full+consensus",
    ),
}


# =============================================================================
# Regulated Domain Definitions
# =============================================================================

# Default configurations for regulated domains
_REGULATED_DOMAIN_CONFIGS: dict[str, RegulatedDomainConfig] = {
    "healthcare": RegulatedDomainConfig(
        domain="healthcare",
        extra_validation_gates=["hipaa_check", "phi_scan", "audit_trail"],
        audit_logging=True,
    ),
    "finance": RegulatedDomainConfig(
        domain="finance",
        extra_validation_gates=["pci_check", "sox_compliance", "audit_trail"],
        audit_logging=True,
    ),
}


# =============================================================================
# Factory Functions
# =============================================================================


def get_default_profile(tier: ProjectTier) -> BehaviorProfile:
    """Get the default behavior profile for a project tier.

    Returns a copy of the default profile to allow modification without
    affecting the shared definition.

    Args:
        tier: The project complexity tier (TIER_0 through TIER_4)

    Returns:
        BehaviorProfile with tier-appropriate settings

    Examples:
        >>> profile = get_default_profile(ProjectTier.TIER_0)
        >>> profile.batch_size
        'auto-all'

        >>> profile = get_default_profile(ProjectTier.TIER_4)
        >>> profile.checkpoint_frequency
        'every-step'
    """
    template = TIER_PROFILES[tier]
    # Return a new instance to avoid mutation of shared state
    return BehaviorProfile(
        batch_size=template.batch_size,
        checkpoint_frequency=template.checkpoint_frequency,
        human_gates=list(template.human_gates),  # Copy the list
        validation_scope=template.validation_scope,
    )


def get_regulated_config(domain: str | None) -> RegulatedDomainConfig | None:
    """Get regulated domain configuration if domain is regulated.

    For healthcare and finance domains, returns configuration with
    additional validation gates and audit logging enabled.

    Args:
        domain: Domain name (e.g., "healthcare", "finance") or None

    Returns:
        RegulatedDomainConfig if domain is regulated, None otherwise

    Examples:
        >>> config = get_regulated_config("healthcare")
        >>> config.audit_logging
        True

        >>> get_regulated_config("retail")
        None
    """
    if domain is None or not domain.strip():
        return None

    # Normalize domain to lowercase for case-insensitive matching
    normalized = domain.lower().strip()

    if normalized not in REGULATED_DOMAINS:
        return None

    template = _REGULATED_DOMAIN_CONFIGS[normalized]
    # Return a new instance to avoid mutation of shared state
    return RegulatedDomainConfig(
        domain=template.domain,
        extra_validation_gates=list(template.extra_validation_gates),
        audit_logging=template.audit_logging,
    )


def create_behavior_config(
    tier: ProjectTier,
    domain: str | None = None,
    custom_thresholds: dict[str, int] | None = None,
) -> AdaptiveBehaviorConfig:
    """Create an adaptive behavior configuration for a project.

    Combines tier-based profile, domain-specific settings, and custom
    thresholds into a complete configuration.

    Args:
        tier: The project complexity tier (TIER_0 through TIER_4)
        domain: Optional domain classification (e.g., "healthcare", "finance")
            for regulated domain settings
        custom_thresholds: Optional dict with threshold overrides:
            - "high_threshold": Minimum for automatic approval (default 80)
            - "medium_threshold": Minimum for tentative decisions (default 50)

    Returns:
        AdaptiveBehaviorConfig with all settings combined

    Examples:
        >>> config = create_behavior_config(ProjectTier.TIER_0)
        >>> config.profile.batch_size
        'auto-all'

        >>> config = create_behavior_config(
        ...     ProjectTier.TIER_4,
        ...     domain="healthcare",
        ...     custom_thresholds={"high_threshold": 90}
        ... )
        >>> config.domain_config.audit_logging
        True
        >>> config.thresholds.high_threshold
        90
    """
    # Get tier-appropriate profile
    profile = get_default_profile(tier)

    # Build confidence thresholds
    if custom_thresholds:
        thresholds = ConfidenceThresholds(
            high_threshold=custom_thresholds.get("high_threshold", DEFAULT_HIGH_THRESHOLD),
            medium_threshold=custom_thresholds.get("medium_threshold", DEFAULT_MEDIUM_THRESHOLD),
        )
    else:
        thresholds = ConfidenceThresholds()

    # Get domain configuration if applicable
    domain_config = get_regulated_config(domain)

    return AdaptiveBehaviorConfig(
        tier=tier,
        profile=profile,
        thresholds=thresholds,
        domain_config=domain_config,
    )


def update_thresholds(
    config: AdaptiveBehaviorConfig,
    new_thresholds: dict[str, int],
) -> AdaptiveBehaviorConfig:
    """Update confidence thresholds on an existing configuration.

    Creates a new configuration with updated thresholds while preserving
    all other settings. This supports mid-workflow threshold changes
    that apply immediately at the next decision point.

    Args:
        config: The existing AdaptiveBehaviorConfig to update
        new_thresholds: Dict with threshold updates:
            - "high_threshold": New high threshold value
            - "medium_threshold": New medium threshold value

    Returns:
        New AdaptiveBehaviorConfig with updated thresholds

    Examples:
        >>> original = create_behavior_config(ProjectTier.TIER_2)
        >>> updated = update_thresholds(original, {"high_threshold": 95})
        >>> updated.thresholds.high_threshold
        95
        >>> original.thresholds.high_threshold  # Original unchanged
        80
    """
    # Build new thresholds, preserving originals where not overridden
    updated_thresholds = ConfidenceThresholds(
        high_threshold=new_thresholds.get(
            "high_threshold", config.thresholds.high_threshold
        ),
        medium_threshold=new_thresholds.get(
            "medium_threshold", config.thresholds.medium_threshold
        ),
    )

    # Copy profile to avoid shared state
    copied_profile = BehaviorProfile(
        batch_size=config.profile.batch_size,
        checkpoint_frequency=config.profile.checkpoint_frequency,
        human_gates=list(config.profile.human_gates),
        validation_scope=config.profile.validation_scope,
    )

    # Copy domain config if present
    copied_domain_config = None
    if config.domain_config is not None:
        copied_domain_config = RegulatedDomainConfig(
            domain=config.domain_config.domain,
            extra_validation_gates=list(config.domain_config.extra_validation_gates),
            audit_logging=config.domain_config.audit_logging,
        )

    return AdaptiveBehaviorConfig(
        tier=config.tier,
        profile=copied_profile,
        thresholds=updated_thresholds,
        domain_config=copied_domain_config,
    )
