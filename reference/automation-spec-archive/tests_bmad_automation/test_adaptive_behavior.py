"""Tests for Adaptive Behavior Configuration.

This module tests the adaptive behavior configuration functionality that
calibrates automation settings based on project tier, domain, and custom thresholds.

Story: 2a.7 - Adaptive Behavior Configuration
Epic: 2a - Workflow Entry & Detection

TDD: Tests are written FIRST, before implementation.
"""

import pytest
from dataclasses import asdict

from pcmrp_tools.bmad_automation.adaptive_behavior import (
    BehaviorProfile,
    ConfidenceThresholds,
    RegulatedDomainConfig,
    AdaptiveBehaviorConfig,
    get_default_profile,
    get_regulated_config,
    create_behavior_config,
    update_thresholds,
    # Constants
    DEFAULT_HIGH_THRESHOLD,
    DEFAULT_MEDIUM_THRESHOLD,
    TIER_PROFILES,
    REGULATED_DOMAINS,
)

from pcmrp_tools.bmad_automation.tier_suggester import ProjectTier


# =============================================================================
# BehaviorProfile Dataclass Tests
# =============================================================================


class TestBehaviorProfileDataclass:
    """Tests for BehaviorProfile dataclass."""

    def test_behavior_profile_creation_with_all_fields(self):
        """BehaviorProfile should be creatable with all fields."""
        profile = BehaviorProfile(
            batch_size=5,
            checkpoint_frequency="standard",
            human_gates=["design", "final"],
            validation_scope="full",
        )
        assert profile.batch_size == 5
        assert profile.checkpoint_frequency == "standard"
        assert profile.human_gates == ["design", "final"]
        assert profile.validation_scope == "full"

    def test_behavior_profile_batch_size_can_be_string(self):
        """BehaviorProfile batch_size can be 'auto-all' string."""
        profile = BehaviorProfile(
            batch_size="auto-all",
            checkpoint_frequency="minimal",
            human_gates=["final"],
            validation_scope="workflow-specific",
        )
        assert profile.batch_size == "auto-all"

    def test_behavior_profile_batch_size_can_be_int(self):
        """BehaviorProfile batch_size can be integer."""
        profile = BehaviorProfile(
            batch_size=10,
            checkpoint_frequency="frequent",
            human_gates=["architecture", "design", "final"],
            validation_scope="full+consensus",
        )
        assert profile.batch_size == 10

    def test_behavior_profile_to_dict(self):
        """BehaviorProfile should be serializable to dict."""
        profile = BehaviorProfile(
            batch_size=5,
            checkpoint_frequency="standard",
            human_gates=["final"],
            validation_scope="full",
        )
        result = asdict(profile)
        assert result["batch_size"] == 5
        assert result["checkpoint_frequency"] == "standard"
        assert result["human_gates"] == ["final"]
        assert result["validation_scope"] == "full"


class TestBehaviorProfileValidCheckpointFrequency:
    """Tests for BehaviorProfile checkpoint_frequency valid values."""

    def test_checkpoint_frequency_minimal(self):
        """checkpoint_frequency 'minimal' should be valid."""
        profile = BehaviorProfile(
            batch_size=5,
            checkpoint_frequency="minimal",
            human_gates=[],
            validation_scope="workflow-specific",
        )
        assert profile.checkpoint_frequency == "minimal"

    def test_checkpoint_frequency_standard(self):
        """checkpoint_frequency 'standard' should be valid."""
        profile = BehaviorProfile(
            batch_size=5,
            checkpoint_frequency="standard",
            human_gates=[],
            validation_scope="workflow-specific",
        )
        assert profile.checkpoint_frequency == "standard"

    def test_checkpoint_frequency_frequent(self):
        """checkpoint_frequency 'frequent' should be valid."""
        profile = BehaviorProfile(
            batch_size=3,
            checkpoint_frequency="frequent",
            human_gates=[],
            validation_scope="full",
        )
        assert profile.checkpoint_frequency == "frequent"

    def test_checkpoint_frequency_every_step(self):
        """checkpoint_frequency 'every-step' should be valid."""
        profile = BehaviorProfile(
            batch_size=1,
            checkpoint_frequency="every-step",
            human_gates=[],
            validation_scope="full+consensus",
        )
        assert profile.checkpoint_frequency == "every-step"


class TestBehaviorProfileValidationScope:
    """Tests for BehaviorProfile validation_scope valid values."""

    def test_validation_scope_workflow_specific(self):
        """validation_scope 'workflow-specific' should be valid."""
        profile = BehaviorProfile(
            batch_size=5,
            checkpoint_frequency="minimal",
            human_gates=[],
            validation_scope="workflow-specific",
        )
        assert profile.validation_scope == "workflow-specific"

    def test_validation_scope_full(self):
        """validation_scope 'full' should be valid."""
        profile = BehaviorProfile(
            batch_size=3,
            checkpoint_frequency="standard",
            human_gates=[],
            validation_scope="full",
        )
        assert profile.validation_scope == "full"

    def test_validation_scope_full_consensus(self):
        """validation_scope 'full+consensus' should be valid."""
        profile = BehaviorProfile(
            batch_size=1,
            checkpoint_frequency="every-step",
            human_gates=[],
            validation_scope="full+consensus",
        )
        assert profile.validation_scope == "full+consensus"


# =============================================================================
# ConfidenceThresholds Dataclass Tests
# =============================================================================


class TestConfidenceThresholdsDataclass:
    """Tests for ConfidenceThresholds dataclass."""

    def test_confidence_thresholds_creation(self):
        """ConfidenceThresholds should be creatable with all fields."""
        thresholds = ConfidenceThresholds(
            high_threshold=80,
            medium_threshold=50,
        )
        assert thresholds.high_threshold == 80
        assert thresholds.medium_threshold == 50

    def test_confidence_thresholds_defaults(self):
        """ConfidenceThresholds should have default values."""
        thresholds = ConfidenceThresholds()
        assert thresholds.high_threshold == DEFAULT_HIGH_THRESHOLD
        assert thresholds.medium_threshold == DEFAULT_MEDIUM_THRESHOLD

    def test_confidence_thresholds_custom_values(self):
        """ConfidenceThresholds should accept custom values."""
        thresholds = ConfidenceThresholds(
            high_threshold=90,
            medium_threshold=60,
        )
        assert thresholds.high_threshold == 90
        assert thresholds.medium_threshold == 60

    def test_confidence_thresholds_to_dict(self):
        """ConfidenceThresholds should be serializable to dict."""
        thresholds = ConfidenceThresholds(high_threshold=85, medium_threshold=55)
        result = asdict(thresholds)
        assert result["high_threshold"] == 85
        assert result["medium_threshold"] == 55


# =============================================================================
# RegulatedDomainConfig Dataclass Tests
# =============================================================================


class TestRegulatedDomainConfigDataclass:
    """Tests for RegulatedDomainConfig dataclass."""

    def test_regulated_domain_config_creation(self):
        """RegulatedDomainConfig should be creatable with all fields."""
        config = RegulatedDomainConfig(
            domain="healthcare",
            extra_validation_gates=["hipaa_check", "phi_scan"],
            audit_logging=True,
        )
        assert config.domain == "healthcare"
        assert config.extra_validation_gates == ["hipaa_check", "phi_scan"]
        assert config.audit_logging is True

    def test_regulated_domain_config_finance(self):
        """RegulatedDomainConfig should support finance domain."""
        config = RegulatedDomainConfig(
            domain="finance",
            extra_validation_gates=["pci_check", "sox_compliance"],
            audit_logging=True,
        )
        assert config.domain == "finance"
        assert "pci_check" in config.extra_validation_gates

    def test_regulated_domain_config_to_dict(self):
        """RegulatedDomainConfig should be serializable to dict."""
        config = RegulatedDomainConfig(
            domain="healthcare",
            extra_validation_gates=["hipaa_check"],
            audit_logging=True,
        )
        result = asdict(config)
        assert result["domain"] == "healthcare"
        assert result["audit_logging"] is True


# =============================================================================
# AdaptiveBehaviorConfig Dataclass Tests
# =============================================================================


class TestAdaptiveBehaviorConfigDataclass:
    """Tests for AdaptiveBehaviorConfig dataclass."""

    def test_adaptive_behavior_config_creation(self):
        """AdaptiveBehaviorConfig should be creatable with all fields."""
        profile = BehaviorProfile(
            batch_size=5,
            checkpoint_frequency="standard",
            human_gates=["final"],
            validation_scope="full",
        )
        thresholds = ConfidenceThresholds(high_threshold=80, medium_threshold=50)
        config = AdaptiveBehaviorConfig(
            tier=ProjectTier.TIER_2,
            profile=profile,
            thresholds=thresholds,
            domain_config=None,
        )
        assert config.tier == ProjectTier.TIER_2
        assert config.profile.batch_size == 5
        assert config.thresholds.high_threshold == 80
        assert config.domain_config is None

    def test_adaptive_behavior_config_with_domain(self):
        """AdaptiveBehaviorConfig should support domain_config."""
        profile = BehaviorProfile(
            batch_size=3,
            checkpoint_frequency="frequent",
            human_gates=["architecture", "design", "final"],
            validation_scope="full",
        )
        thresholds = ConfidenceThresholds()
        domain_config = RegulatedDomainConfig(
            domain="healthcare",
            extra_validation_gates=["hipaa_check"],
            audit_logging=True,
        )
        config = AdaptiveBehaviorConfig(
            tier=ProjectTier.TIER_4,
            profile=profile,
            thresholds=thresholds,
            domain_config=domain_config,
        )
        assert config.domain_config is not None
        assert config.domain_config.domain == "healthcare"

    def test_adaptive_behavior_config_to_dict(self):
        """AdaptiveBehaviorConfig should be serializable to dict."""
        profile = BehaviorProfile(
            batch_size=5,
            checkpoint_frequency="standard",
            human_gates=["final"],
            validation_scope="full",
        )
        thresholds = ConfidenceThresholds()
        config = AdaptiveBehaviorConfig(
            tier=ProjectTier.TIER_2,
            profile=profile,
            thresholds=thresholds,
        )
        result = asdict(config)
        assert result["tier"] == ProjectTier.TIER_2
        assert result["profile"]["batch_size"] == 5


# =============================================================================
# get_default_profile() Function Tests
# =============================================================================


class TestGetDefaultProfile:
    """Tests for get_default_profile() function."""

    def test_get_default_profile_returns_behavior_profile(self):
        """get_default_profile() should return BehaviorProfile."""
        profile = get_default_profile(ProjectTier.TIER_2)
        assert isinstance(profile, BehaviorProfile)

    def test_get_default_profile_tier_0_aggressive_automation(self):
        """get_default_profile(TIER_0) should apply aggressive automation (AC #1)."""
        profile = get_default_profile(ProjectTier.TIER_0)
        assert profile.batch_size == "auto-all"
        assert profile.checkpoint_frequency == "minimal"
        assert profile.human_gates == ["final"]
        assert profile.validation_scope == "workflow-specific"

    def test_get_default_profile_tier_1_aggressive_automation(self):
        """get_default_profile(TIER_1) should apply aggressive automation (AC #1)."""
        profile = get_default_profile(ProjectTier.TIER_1)
        assert profile.batch_size == "auto-all"
        assert profile.checkpoint_frequency == "minimal"
        assert profile.human_gates == ["final"]
        assert profile.validation_scope == "workflow-specific"

    def test_get_default_profile_tier_2_standard_automation(self):
        """get_default_profile(TIER_2) should apply standard automation."""
        profile = get_default_profile(ProjectTier.TIER_2)
        assert isinstance(profile.batch_size, int)
        assert profile.checkpoint_frequency == "standard"
        assert "design" in profile.human_gates
        assert "final" in profile.human_gates

    def test_get_default_profile_tier_3_conservative_automation(self):
        """get_default_profile(TIER_3) should apply conservative automation (AC #2)."""
        profile = get_default_profile(ProjectTier.TIER_3)
        # Should have small batch sizes
        assert isinstance(profile.batch_size, int)
        assert profile.batch_size <= 5
        # Should have more checkpoints
        assert profile.checkpoint_frequency in ("frequent", "every-step")
        # Should have more human gates
        assert "architecture" in profile.human_gates
        assert "design" in profile.human_gates
        assert "final" in profile.human_gates
        # Should have thorough validation
        assert profile.validation_scope == "full"

    def test_get_default_profile_tier_4_conservative_automation(self):
        """get_default_profile(TIER_4) should apply most conservative automation (AC #2)."""
        profile = get_default_profile(ProjectTier.TIER_4)
        # Should have smallest batch sizes
        assert isinstance(profile.batch_size, int)
        assert profile.batch_size <= 3
        # Should have most checkpoints
        assert profile.checkpoint_frequency == "every-step"
        # Should have all human gates
        assert len(profile.human_gates) >= 3
        # Should have full validation with consensus
        assert profile.validation_scope == "full+consensus"


class TestGetDefaultProfileConstant:
    """Tests for TIER_PROFILES constant structure."""

    def test_tier_profiles_has_all_tiers(self):
        """TIER_PROFILES should have entries for all 5 tiers."""
        assert ProjectTier.TIER_0 in TIER_PROFILES
        assert ProjectTier.TIER_1 in TIER_PROFILES
        assert ProjectTier.TIER_2 in TIER_PROFILES
        assert ProjectTier.TIER_3 in TIER_PROFILES
        assert ProjectTier.TIER_4 in TIER_PROFILES


# =============================================================================
# get_regulated_config() Function Tests
# =============================================================================


class TestGetRegulatedConfig:
    """Tests for get_regulated_config() function."""

    def test_get_regulated_config_returns_regulated_domain_config_or_none(self):
        """get_regulated_config() should return RegulatedDomainConfig or None."""
        result = get_regulated_config("healthcare")
        assert result is None or isinstance(result, RegulatedDomainConfig)

    def test_get_regulated_config_healthcare_returns_config(self):
        """get_regulated_config('healthcare') should return config (AC #4)."""
        result = get_regulated_config("healthcare")
        assert result is not None
        assert isinstance(result, RegulatedDomainConfig)
        assert result.domain == "healthcare"
        assert result.audit_logging is True
        assert len(result.extra_validation_gates) > 0

    def test_get_regulated_config_finance_returns_config(self):
        """get_regulated_config('finance') should return config (AC #4)."""
        result = get_regulated_config("finance")
        assert result is not None
        assert isinstance(result, RegulatedDomainConfig)
        assert result.domain == "finance"
        assert result.audit_logging is True
        assert len(result.extra_validation_gates) > 0

    def test_get_regulated_config_unknown_domain_returns_none(self):
        """get_regulated_config() should return None for unknown domain."""
        result = get_regulated_config("retail")
        assert result is None

    def test_get_regulated_config_none_returns_none(self):
        """get_regulated_config(None) should return None."""
        result = get_regulated_config(None)
        assert result is None

    def test_get_regulated_config_empty_string_returns_none(self):
        """get_regulated_config('') should return None."""
        result = get_regulated_config("")
        assert result is None

    def test_get_regulated_config_case_insensitive(self):
        """get_regulated_config() should be case insensitive."""
        result = get_regulated_config("HEALTHCARE")
        assert result is not None
        assert result.domain == "healthcare"


class TestRegulatedDomainsConstant:
    """Tests for REGULATED_DOMAINS constant."""

    def test_regulated_domains_contains_healthcare(self):
        """REGULATED_DOMAINS should contain 'healthcare'."""
        assert "healthcare" in REGULATED_DOMAINS

    def test_regulated_domains_contains_finance(self):
        """REGULATED_DOMAINS should contain 'finance'."""
        assert "finance" in REGULATED_DOMAINS


# =============================================================================
# create_behavior_config() Function Tests
# =============================================================================


class TestCreateBehaviorConfig:
    """Tests for create_behavior_config() factory function."""

    def test_create_behavior_config_returns_adaptive_config(self):
        """create_behavior_config() should return AdaptiveBehaviorConfig."""
        config = create_behavior_config(ProjectTier.TIER_2)
        assert isinstance(config, AdaptiveBehaviorConfig)

    def test_create_behavior_config_uses_tier_profile(self):
        """create_behavior_config() should use tier's default profile."""
        config = create_behavior_config(ProjectTier.TIER_0)
        assert config.tier == ProjectTier.TIER_0
        assert config.profile.batch_size == "auto-all"

    def test_create_behavior_config_with_domain_healthcare(self):
        """create_behavior_config() with domain='healthcare' enables validation gates (AC #4)."""
        config = create_behavior_config(ProjectTier.TIER_4, domain="healthcare")
        assert config.domain_config is not None
        assert config.domain_config.domain == "healthcare"
        assert config.domain_config.audit_logging is True

    def test_create_behavior_config_with_domain_finance(self):
        """create_behavior_config() with domain='finance' enables validation gates (AC #4)."""
        config = create_behavior_config(ProjectTier.TIER_4, domain="finance")
        assert config.domain_config is not None
        assert config.domain_config.domain == "finance"
        assert config.domain_config.audit_logging is True

    def test_create_behavior_config_without_domain(self):
        """create_behavior_config() without domain has None domain_config."""
        config = create_behavior_config(ProjectTier.TIER_2)
        assert config.domain_config is None

    def test_create_behavior_config_with_custom_thresholds(self):
        """create_behavior_config() with custom_thresholds uses them (AC #3)."""
        custom = {"high_threshold": 90, "medium_threshold": 60}
        config = create_behavior_config(ProjectTier.TIER_2, custom_thresholds=custom)
        assert config.thresholds.high_threshold == 90
        assert config.thresholds.medium_threshold == 60

    def test_create_behavior_config_partial_custom_thresholds(self):
        """create_behavior_config() with partial custom thresholds merges with defaults."""
        custom = {"high_threshold": 90}
        config = create_behavior_config(ProjectTier.TIER_2, custom_thresholds=custom)
        assert config.thresholds.high_threshold == 90
        assert config.thresholds.medium_threshold == DEFAULT_MEDIUM_THRESHOLD

    def test_create_behavior_config_default_thresholds(self):
        """create_behavior_config() without custom_thresholds uses defaults."""
        config = create_behavior_config(ProjectTier.TIER_2)
        assert config.thresholds.high_threshold == DEFAULT_HIGH_THRESHOLD
        assert config.thresholds.medium_threshold == DEFAULT_MEDIUM_THRESHOLD


# =============================================================================
# update_thresholds() Function Tests
# =============================================================================


class TestUpdateThresholds:
    """Tests for update_thresholds() function."""

    def test_update_thresholds_returns_new_config(self):
        """update_thresholds() should return a new AdaptiveBehaviorConfig."""
        original = create_behavior_config(ProjectTier.TIER_2)
        updated = update_thresholds(original, {"high_threshold": 95})
        assert isinstance(updated, AdaptiveBehaviorConfig)
        assert updated is not original

    def test_update_thresholds_modifies_high_threshold(self):
        """update_thresholds() should update high_threshold (AC #5)."""
        original = create_behavior_config(ProjectTier.TIER_2)
        updated = update_thresholds(original, {"high_threshold": 95})
        assert updated.thresholds.high_threshold == 95
        assert updated.thresholds.medium_threshold == original.thresholds.medium_threshold

    def test_update_thresholds_modifies_medium_threshold(self):
        """update_thresholds() should update medium_threshold (AC #5)."""
        original = create_behavior_config(ProjectTier.TIER_2)
        updated = update_thresholds(original, {"medium_threshold": 65})
        assert updated.thresholds.medium_threshold == 65
        assert updated.thresholds.high_threshold == original.thresholds.high_threshold

    def test_update_thresholds_modifies_both(self):
        """update_thresholds() should update both thresholds."""
        original = create_behavior_config(ProjectTier.TIER_2)
        updated = update_thresholds(original, {"high_threshold": 95, "medium_threshold": 65})
        assert updated.thresholds.high_threshold == 95
        assert updated.thresholds.medium_threshold == 65

    def test_update_thresholds_preserves_tier(self):
        """update_thresholds() should preserve tier."""
        original = create_behavior_config(ProjectTier.TIER_3)
        updated = update_thresholds(original, {"high_threshold": 95})
        assert updated.tier == ProjectTier.TIER_3

    def test_update_thresholds_preserves_profile(self):
        """update_thresholds() should preserve profile."""
        original = create_behavior_config(ProjectTier.TIER_3)
        updated = update_thresholds(original, {"high_threshold": 95})
        assert updated.profile.batch_size == original.profile.batch_size
        assert updated.profile.checkpoint_frequency == original.profile.checkpoint_frequency

    def test_update_thresholds_preserves_domain_config(self):
        """update_thresholds() should preserve domain_config."""
        original = create_behavior_config(ProjectTier.TIER_4, domain="healthcare")
        updated = update_thresholds(original, {"high_threshold": 95})
        assert updated.domain_config is not None
        assert updated.domain_config.domain == "healthcare"

    def test_update_thresholds_empty_dict_no_changes(self):
        """update_thresholds() with empty dict preserves original thresholds."""
        original = create_behavior_config(ProjectTier.TIER_2)
        updated = update_thresholds(original, {})
        assert updated.thresholds.high_threshold == original.thresholds.high_threshold
        assert updated.thresholds.medium_threshold == original.thresholds.medium_threshold

    def test_update_thresholds_immediate_effect(self):
        """update_thresholds() changes apply immediately (AC #5)."""
        # This tests the immutable update pattern - new config has new values
        config = create_behavior_config(ProjectTier.TIER_2)
        assert config.thresholds.high_threshold == DEFAULT_HIGH_THRESHOLD

        # Update should produce new config with new values
        new_config = update_thresholds(config, {"high_threshold": 95})
        assert new_config.thresholds.high_threshold == 95

        # Original should be unchanged
        assert config.thresholds.high_threshold == DEFAULT_HIGH_THRESHOLD


# =============================================================================
# Acceptance Criteria Integration Tests
# =============================================================================


class TestAC1AggressiveAutomationTier0And1:
    """Tests for AC #1: Tier 0-1 aggressive automation."""

    def test_tier_0_has_auto_all_batch_size(self):
        """Tier 0 should have 'auto-all' batch size (AC #1)."""
        config = create_behavior_config(ProjectTier.TIER_0)
        assert config.profile.batch_size == "auto-all"

    def test_tier_0_has_minimal_checkpoints(self):
        """Tier 0 should have minimal checkpoints (AC #1)."""
        config = create_behavior_config(ProjectTier.TIER_0)
        assert config.profile.checkpoint_frequency == "minimal"

    def test_tier_0_has_final_only_human_gate(self):
        """Tier 0 should have only 'final' human gate (AC #1)."""
        config = create_behavior_config(ProjectTier.TIER_0)
        assert config.profile.human_gates == ["final"]

    def test_tier_1_has_auto_all_batch_size(self):
        """Tier 1 should have 'auto-all' batch size (AC #1)."""
        config = create_behavior_config(ProjectTier.TIER_1)
        assert config.profile.batch_size == "auto-all"

    def test_tier_1_has_minimal_checkpoints(self):
        """Tier 1 should have minimal checkpoints (AC #1)."""
        config = create_behavior_config(ProjectTier.TIER_1)
        assert config.profile.checkpoint_frequency == "minimal"


class TestAC2ConservativeAutomationTier3And4:
    """Tests for AC #2: Tier 3-4 conservative automation."""

    def test_tier_3_has_small_batch_size(self):
        """Tier 3 should have small batch size (AC #2)."""
        config = create_behavior_config(ProjectTier.TIER_3)
        assert isinstance(config.profile.batch_size, int)
        assert config.profile.batch_size <= 5

    def test_tier_3_has_more_checkpoints(self):
        """Tier 3 should have frequent checkpoints (AC #2)."""
        config = create_behavior_config(ProjectTier.TIER_3)
        assert config.profile.checkpoint_frequency in ("frequent", "every-step")

    def test_tier_3_has_multiple_human_gates(self):
        """Tier 3 should have multiple human gates (AC #2)."""
        config = create_behavior_config(ProjectTier.TIER_3)
        assert len(config.profile.human_gates) >= 3
        assert "architecture" in config.profile.human_gates

    def test_tier_4_has_smallest_batch_size(self):
        """Tier 4 should have smallest batch size (AC #2)."""
        config = create_behavior_config(ProjectTier.TIER_4)
        assert isinstance(config.profile.batch_size, int)
        assert config.profile.batch_size <= 3

    def test_tier_4_has_every_step_checkpoints(self):
        """Tier 4 should have every-step checkpoints (AC #2)."""
        config = create_behavior_config(ProjectTier.TIER_4)
        assert config.profile.checkpoint_frequency == "every-step"

    def test_tier_4_has_full_consensus_validation(self):
        """Tier 4 should have full+consensus validation scope (AC #2)."""
        config = create_behavior_config(ProjectTier.TIER_4)
        assert config.profile.validation_scope == "full+consensus"


class TestAC3WorkflowSpecificThresholds:
    """Tests for AC #3: Workflow-specific confidence thresholds."""

    def test_custom_thresholds_override_defaults(self):
        """Custom thresholds should override defaults (AC #3)."""
        custom = {"high_threshold": 90, "medium_threshold": 60}
        config = create_behavior_config(ProjectTier.TIER_2, custom_thresholds=custom)
        assert config.thresholds.high_threshold == 90
        assert config.thresholds.medium_threshold == 60

    def test_default_thresholds_when_not_specified(self):
        """Default thresholds used when not specified (AC #3)."""
        config = create_behavior_config(ProjectTier.TIER_2)
        assert config.thresholds.high_threshold == DEFAULT_HIGH_THRESHOLD
        assert config.thresholds.medium_threshold == DEFAULT_MEDIUM_THRESHOLD


class TestAC4RegulatedDomainValidationGates:
    """Tests for AC #4: Healthcare/Finance additional validation gates."""

    def test_healthcare_domain_enables_extra_gates(self):
        """Healthcare domain should enable additional validation gates (AC #4)."""
        config = create_behavior_config(ProjectTier.TIER_4, domain="healthcare")
        assert config.domain_config is not None
        assert config.domain_config.domain == "healthcare"
        assert len(config.domain_config.extra_validation_gates) > 0
        assert config.domain_config.audit_logging is True

    def test_finance_domain_enables_extra_gates(self):
        """Finance domain should enable additional validation gates (AC #4)."""
        config = create_behavior_config(ProjectTier.TIER_4, domain="finance")
        assert config.domain_config is not None
        assert config.domain_config.domain == "finance"
        assert len(config.domain_config.extra_validation_gates) > 0
        assert config.domain_config.audit_logging is True

    def test_non_regulated_domain_no_extra_gates(self):
        """Non-regulated domain should not have extra gates."""
        config = create_behavior_config(ProjectTier.TIER_4, domain="retail")
        assert config.domain_config is None


class TestAC5MidWorkflowThresholdUpdate:
    """Tests for AC #5: Configurable thresholds modified mid-workflow."""

    def test_update_applies_immediately(self):
        """Updated thresholds should apply immediately (AC #5)."""
        original = create_behavior_config(ProjectTier.TIER_2)
        original_high = original.thresholds.high_threshold

        # Simulate mid-workflow update
        updated = update_thresholds(original, {"high_threshold": 95})

        # New config should have updated value
        assert updated.thresholds.high_threshold == 95
        assert updated.thresholds.high_threshold != original_high

    def test_update_returns_new_config_instance(self):
        """update_thresholds should return new config (immutable update)."""
        original = create_behavior_config(ProjectTier.TIER_2)
        updated = update_thresholds(original, {"high_threshold": 95})

        # Should be different instances
        assert updated is not original

        # Original unchanged
        assert original.thresholds.high_threshold == DEFAULT_HIGH_THRESHOLD


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================


class TestBehaviorProfileValidation:
    """Tests for BehaviorProfile validation in __post_init__."""

    def test_invalid_batch_size_type_raises_error(self):
        """BehaviorProfile should reject invalid batch_size type."""
        with pytest.raises(ValueError, match="batch_size must be int or str"):
            BehaviorProfile(
                batch_size=3.5,  # float is invalid
                checkpoint_frequency="standard",
                human_gates=["final"],
                validation_scope="full",
            )

    def test_invalid_batch_size_string_raises_error(self):
        """BehaviorProfile should reject invalid batch_size string."""
        with pytest.raises(ValueError, match="batch_size string must be 'auto-all'"):
            BehaviorProfile(
                batch_size="invalid",
                checkpoint_frequency="standard",
                human_gates=["final"],
                validation_scope="full",
            )

    def test_invalid_checkpoint_frequency_raises_error(self):
        """BehaviorProfile should reject invalid checkpoint_frequency."""
        with pytest.raises(ValueError, match="Invalid checkpoint_frequency"):
            BehaviorProfile(
                batch_size=5,
                checkpoint_frequency="invalid",
                human_gates=["final"],
                validation_scope="full",
            )

    def test_invalid_validation_scope_raises_error(self):
        """BehaviorProfile should reject invalid validation_scope."""
        with pytest.raises(ValueError, match="Invalid validation_scope"):
            BehaviorProfile(
                batch_size=5,
                checkpoint_frequency="standard",
                human_gates=["final"],
                validation_scope="invalid",
            )


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_create_behavior_config_with_none_custom_thresholds(self):
        """create_behavior_config with None custom_thresholds uses defaults."""
        config = create_behavior_config(ProjectTier.TIER_2, custom_thresholds=None)
        assert config.thresholds.high_threshold == DEFAULT_HIGH_THRESHOLD

    def test_create_behavior_config_with_empty_custom_thresholds(self):
        """create_behavior_config with empty dict uses defaults."""
        config = create_behavior_config(ProjectTier.TIER_2, custom_thresholds={})
        assert config.thresholds.high_threshold == DEFAULT_HIGH_THRESHOLD

    def test_get_regulated_config_case_variations(self):
        """get_regulated_config handles various case inputs."""
        assert get_regulated_config("Healthcare") is not None
        assert get_regulated_config("FINANCE") is not None
        assert get_regulated_config("HeAlThCaRe") is not None

    def test_all_tiers_produce_valid_configs(self):
        """All project tiers should produce valid configs."""
        for tier in ProjectTier:
            config = create_behavior_config(tier)
            assert config.tier == tier
            assert config.profile is not None
            assert config.thresholds is not None

    def test_tier_4_with_all_options(self):
        """Tier 4 with domain and custom thresholds combines all features."""
        custom = {"high_threshold": 95, "medium_threshold": 70}
        config = create_behavior_config(
            ProjectTier.TIER_4,
            domain="healthcare",
            custom_thresholds=custom,
        )
        assert config.tier == ProjectTier.TIER_4
        assert config.profile.batch_size <= 3
        assert config.thresholds.high_threshold == 95
        assert config.domain_config is not None
        assert config.domain_config.audit_logging is True
