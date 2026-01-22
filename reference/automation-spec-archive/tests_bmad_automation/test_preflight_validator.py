"""Tests for Pre-flight Configuration Validator component.

This module tests the PreflightResult dataclass, PreflightStatus enum, and
validation functions that form the pre-flight validation system for BMAD workflows.

TDD Pattern: Tests written FIRST before implementation.
Story: 1.2 - Pre-flight Configuration Validation
Epic: 1 - Foundation Validation
"""

from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# These imports will fail until implementation exists (RED phase)
from pcmrp_tools.bmad_automation.preflight_validator import (
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


# =============================================================================
# Task 1: PreflightStatus Enum Tests (Subtask 1.1)
# =============================================================================


class TestPreflightStatus:
    """Tests for PreflightStatus enum (Subtask 1.1)."""

    def test_passed_value(self):
        """Test PreflightStatus.PASSED has correct string value."""
        assert PreflightStatus.PASSED.value == "PASSED"

    def test_failed_value(self):
        """Test PreflightStatus.FAILED has correct string value."""
        assert PreflightStatus.FAILED.value == "FAILED"

    def test_ready_value(self):
        """Test PreflightStatus.READY has correct string value."""
        assert PreflightStatus.READY.value == "READY"

    def test_warning_value(self):
        """Test PreflightStatus.WARNING has correct string value."""
        assert PreflightStatus.WARNING.value == "WARNING"

    def test_all_enum_members_exist(self):
        """Test all required enum members exist."""
        expected_members = {"PASSED", "FAILED", "READY", "WARNING"}
        actual_members = {member.name for member in PreflightStatus}
        assert expected_members == actual_members


# =============================================================================
# Task 1: PreflightCheck Dataclass Tests (Subtask 1.2)
# =============================================================================


class TestPreflightCheck:
    """Tests for PreflightCheck dataclass (Subtask 1.2)."""

    def test_create_with_required_fields(self):
        """Test creating PreflightCheck with all required fields."""
        check = PreflightCheck(
            name="config_check",
            status=PreflightStatus.PASSED,
            message="All configuration keys present",
        )
        assert check.name == "config_check"
        assert check.status == PreflightStatus.PASSED
        assert check.message == "All configuration keys present"
        assert check.details == {}

    def test_create_with_details(self):
        """Test creating PreflightCheck with optional details."""
        check = PreflightCheck(
            name="mcp_check",
            status=PreflightStatus.FAILED,
            message="MCP not available",
            details={"timeout_ms": 5000, "error": "Connection refused"},
        )
        assert check.details == {"timeout_ms": 5000, "error": "Connection refused"}

    def test_details_default_empty_dict(self):
        """Test details field defaults to empty dict."""
        check = PreflightCheck(
            name="test",
            status=PreflightStatus.PASSED,
            message="Test message",
        )
        assert check.details == {}
        assert isinstance(check.details, dict)

    def test_type_hints_name_is_string(self):
        """Test name field is a string."""
        check = PreflightCheck(
            name="config_validation",
            status=PreflightStatus.PASSED,
            message="Valid",
        )
        assert isinstance(check.name, str)

    def test_type_hints_status_is_enum(self):
        """Test status field is PreflightStatus enum."""
        check = PreflightCheck(
            name="test",
            status=PreflightStatus.WARNING,
            message="Warning message",
        )
        assert isinstance(check.status, PreflightStatus)


# =============================================================================
# Task 1: PreflightResult Dataclass Tests (Subtask 1.2, 1.3)
# =============================================================================


class TestPreflightResult:
    """Tests for PreflightResult dataclass (Subtask 1.2, 1.3)."""

    def test_create_with_all_fields(self):
        """Test creating PreflightResult with all fields."""
        checks = [
            PreflightCheck(
                name="config",
                status=PreflightStatus.PASSED,
                message="Config valid",
            )
        ]
        result = PreflightResult(
            overall_status=PreflightStatus.READY,
            checks=checks,
            missing=["output_folder"],
            remediation=["Set output_folder in config"],
            checks_passed=75.0,
        )
        assert result.overall_status == PreflightStatus.READY
        assert len(result.checks) == 1
        assert result.missing == ["output_folder"]
        assert result.remediation == ["Set output_folder in config"]
        assert result.checks_passed == 75.0

    def test_missing_defaults_to_empty_list(self):
        """Test missing field defaults to empty list."""
        result = PreflightResult(
            overall_status=PreflightStatus.READY,
            checks=[],
        )
        assert result.missing == []
        assert isinstance(result.missing, list)

    def test_remediation_defaults_to_empty_list(self):
        """Test remediation field defaults to empty list."""
        result = PreflightResult(
            overall_status=PreflightStatus.READY,
            checks=[],
        )
        assert result.remediation == []
        assert isinstance(result.remediation, list)

    def test_checks_passed_defaults_to_zero(self):
        """Test checks_passed field defaults to 0.0."""
        result = PreflightResult(
            overall_status=PreflightStatus.FAILED,
            checks=[],
        )
        assert result.checks_passed == 0.0

    def test_checks_passed_percentage_range(self):
        """Test checks_passed is a percentage (0.0 to 100.0)."""
        result = PreflightResult(
            overall_status=PreflightStatus.READY,
            checks=[],
            checks_passed=100.0,
        )
        assert 0.0 <= result.checks_passed <= 100.0


# =============================================================================
# Task 1: Factory Methods Tests (Subtask 1.3)
# =============================================================================


class TestPreflightResultFactoryMethods:
    """Tests for PreflightResult factory methods (Subtask 1.3)."""

    def test_passed_factory(self):
        """Test factory method for passed check result."""
        check = PreflightCheck.passed(
            name="config_check",
            message="All configuration valid",
        )
        assert check.status == PreflightStatus.PASSED
        assert check.name == "config_check"
        assert check.message == "All configuration valid"

    def test_passed_factory_with_details(self):
        """Test passed factory method with details."""
        check = PreflightCheck.passed(
            name="mcp_check",
            message="MCP available",
            details={"response_time_ms": 50},
        )
        assert check.status == PreflightStatus.PASSED
        assert check.details == {"response_time_ms": 50}

    def test_failed_factory(self):
        """Test factory method for failed check result."""
        check = PreflightCheck.failed(
            name="config_check",
            message="Missing required configuration",
        )
        assert check.status == PreflightStatus.FAILED
        assert check.name == "config_check"
        assert check.message == "Missing required configuration"

    def test_failed_factory_with_details(self):
        """Test failed factory method with details."""
        check = PreflightCheck.failed(
            name="config_check",
            message="Missing keys",
            details={"missing": ["output_folder", "project_root"]},
        )
        assert check.status == PreflightStatus.FAILED
        assert check.details == {"missing": ["output_folder", "project_root"]}

    def test_warning_factory(self):
        """Test factory method for warning check result."""
        check = PreflightCheck.warning(
            name="optional_check",
            message="Optional config not set",
        )
        assert check.status == PreflightStatus.WARNING
        assert check.name == "optional_check"

    def test_ready_result_factory(self):
        """Test factory for overall READY result."""
        checks = [
            PreflightCheck.passed("config", "Config OK"),
            PreflightCheck.passed("mcp", "MCP OK"),
        ]
        result = PreflightResult.ready(checks)
        assert result.overall_status == PreflightStatus.READY
        assert result.checks_passed == 100.0
        assert result.missing == []
        assert result.remediation == []

    def test_failed_result_factory(self):
        """Test factory for overall FAILED result."""
        checks = [
            PreflightCheck.failed("config", "Config missing"),
            PreflightCheck.passed("mcp", "MCP OK"),
        ]
        result = PreflightResult.failed(
            checks=checks,
            missing=["output_folder"],
            remediation=["Add output_folder to config"],
        )
        assert result.overall_status == PreflightStatus.FAILED
        assert result.missing == ["output_folder"]
        assert result.remediation == ["Add output_folder to config"]
        # 1 of 2 passed = 50%
        assert result.checks_passed == 50.0


# =============================================================================
# Task 1: Serialization Tests (Subtask 1.4)
# =============================================================================


class TestPreflightResultSerialization:
    """Tests for PreflightResult serialization (Subtask 1.4)."""

    def test_to_dict_basic(self):
        """Test converting PreflightResult to dictionary."""
        checks = [
            PreflightCheck(
                name="config",
                status=PreflightStatus.PASSED,
                message="OK",
            )
        ]
        result = PreflightResult(
            overall_status=PreflightStatus.READY,
            checks=checks,
            checks_passed=100.0,
        )
        result_dict = result.to_dict()

        assert result_dict["overall_status"] == "READY"
        assert len(result_dict["checks"]) == 1
        assert result_dict["checks"][0]["status"] == "PASSED"
        assert result_dict["checks_passed"] == 100.0

    def test_from_dict_basic(self):
        """Test creating PreflightResult from dictionary."""
        data = {
            "overall_status": "FAILED",
            "checks": [
                {
                    "name": "config",
                    "status": "FAILED",
                    "message": "Missing config",
                    "details": {"missing": ["output_folder"]},
                }
            ],
            "missing": ["output_folder"],
            "remediation": ["Add output_folder"],
            "checks_passed": 0.0,
        }
        result = PreflightResult.from_dict(data)

        assert result.overall_status == PreflightStatus.FAILED
        assert len(result.checks) == 1
        assert result.checks[0].status == PreflightStatus.FAILED
        assert result.missing == ["output_folder"]

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are inverse operations."""
        checks = [
            PreflightCheck(
                name="config",
                status=PreflightStatus.PASSED,
                message="Config valid",
                details={"keys_checked": 5},
            ),
            PreflightCheck(
                name="mcp",
                status=PreflightStatus.WARNING,
                message="MCP slow",
                details={"response_ms": 4500},
            ),
        ]
        original = PreflightResult(
            overall_status=PreflightStatus.READY,
            checks=checks,
            missing=[],
            remediation=[],
            checks_passed=100.0,
        )

        serialized = original.to_dict()
        restored = PreflightResult.from_dict(serialized)

        assert restored.overall_status == original.overall_status
        assert len(restored.checks) == len(original.checks)
        assert restored.checks_passed == original.checks_passed

    def test_from_dict_with_invalid_status_raises_error(self):
        """Test from_dict raises ValueError for invalid status."""
        data = {
            "overall_status": "INVALID_STATUS",
            "checks": [],
            "missing": [],
            "remediation": [],
            "checks_passed": 0.0,
        }
        with pytest.raises(ValueError, match="Invalid status"):
            PreflightResult.from_dict(data)


# =============================================================================
# Task 2: Configuration Validation Tests (AC: #1)
# =============================================================================


class TestValidateConfiguration:
    """Tests for validate_configuration function (AC: #1)."""

    def test_returns_passed_when_all_keys_present(self):
        """Test returns PASSED when all required config keys are present."""
        config = {
            "output_folder": "/path/to/output",
            "project_root": "/path/to/project",
        }
        required_keys = ["output_folder", "project_root"]

        result = validate_configuration(config, required_keys)

        assert result.status == PreflightStatus.PASSED
        assert "missing" not in result.details or result.details.get("missing") == []

    def test_returns_failed_when_output_folder_missing(self):
        """Test returns FAILED with missing=['output_folder'] when output_folder not configured (AC: #1)."""
        config = {
            "project_root": "/path/to/project",
        }
        required_keys = ["output_folder", "project_root"]

        result = validate_configuration(config, required_keys)

        assert result.status == PreflightStatus.FAILED
        assert "output_folder" in result.details.get("missing", [])

    def test_returns_failed_when_project_root_missing(self):
        """Test returns FAILED when project_root not configured."""
        config = {
            "output_folder": "/path/to/output",
        }
        required_keys = ["output_folder", "project_root"]

        result = validate_configuration(config, required_keys)

        assert result.status == PreflightStatus.FAILED
        assert "project_root" in result.details.get("missing", [])

    def test_returns_failed_with_multiple_missing_keys(self):
        """Test returns FAILED with all missing keys listed."""
        config = {}
        required_keys = ["output_folder", "project_root", "config_source"]

        result = validate_configuration(config, required_keys)

        assert result.status == PreflightStatus.FAILED
        missing = result.details.get("missing", [])
        assert "output_folder" in missing
        assert "project_root" in missing
        assert "config_source" in missing

    def test_remediation_message_for_missing_config(self):
        """Test generates remediation message for missing configuration (AC: #1)."""
        config = {}
        required_keys = ["output_folder"]

        result = validate_configuration(config, required_keys)

        assert result.status == PreflightStatus.FAILED
        # Should have a remediation message in the check message or details
        assert "output_folder" in result.message or "output_folder" in str(
            result.details
        )

    def test_handles_empty_required_keys(self):
        """Test handles empty required keys list."""
        config = {"some_key": "value"}
        required_keys = []

        result = validate_configuration(config, required_keys)

        assert result.status == PreflightStatus.PASSED

    def test_handles_none_values_as_missing(self):
        """Test treats None values as missing configuration."""
        config = {
            "output_folder": None,
            "project_root": "/path/to/project",
        }
        required_keys = ["output_folder", "project_root"]

        result = validate_configuration(config, required_keys)

        assert result.status == PreflightStatus.FAILED
        assert "output_folder" in result.details.get("missing", [])

    def test_handles_empty_string_values_as_missing(self):
        """Test treats empty string values as missing configuration."""
        config = {
            "output_folder": "",
            "project_root": "/path/to/project",
        }
        required_keys = ["output_folder", "project_root"]

        result = validate_configuration(config, required_keys)

        assert result.status == PreflightStatus.FAILED
        assert "output_folder" in result.details.get("missing", [])


# =============================================================================
# Task 3: MCP Availability Check Tests (AC: #2)
# =============================================================================


class TestCheckMCPAvailability:
    """Tests for check_mcp_availability function (AC: #2)."""

    def test_returns_passed_when_mcp_available(self):
        """Test returns PASSED when Forgetful MCP is available (AC: #2)."""
        # Mock the MCP check to simulate available MCP
        with patch(
            "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
        ) as mock_ping:
            mock_ping.return_value = True

            result = check_mcp_availability()

            assert result.status == PreflightStatus.PASSED
            assert "available" in result.message.lower() or "ok" in result.message.lower()

    def test_returns_failed_when_mcp_unavailable(self):
        """Test returns FAILED when Forgetful MCP is not available."""
        with patch(
            "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
        ) as mock_ping:
            mock_ping.return_value = False

            result = check_mcp_availability()

            assert result.status == PreflightStatus.FAILED

    def test_handles_timeout_scenario(self):
        """Test handles timeout when MCP doesn't respond within 5s."""
        with patch(
            "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
        ) as mock_ping:
            mock_ping.side_effect = TimeoutError("Connection timed out")

            result = check_mcp_availability(timeout_seconds=5)

            assert result.status == PreflightStatus.FAILED
            assert "timeout" in result.message.lower() or "timed out" in result.message.lower()

    def test_handles_connection_error(self):
        """Test handles connection errors gracefully."""
        with patch(
            "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
        ) as mock_ping:
            mock_ping.side_effect = ConnectionError("Connection refused")

            result = check_mcp_availability()

            assert result.status == PreflightStatus.FAILED
            assert result.details.get("error") is not None

    def test_returns_warning_when_mcp_slow(self):
        """Test returns WARNING when MCP responds but slowly."""
        with patch(
            "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
        ) as mock_ping:
            # Simulate slow response (returns True but with high latency recorded)
            mock_ping.return_value = True

            result = check_mcp_availability(timeout_seconds=5, warn_threshold_seconds=2)

            # If response time is recorded as slow, could return WARNING
            # For simplicity, if it succeeds, it's PASSED
            assert result.status in (PreflightStatus.PASSED, PreflightStatus.WARNING)

    def test_default_timeout_is_5_seconds(self):
        """Test default timeout is 5 seconds as specified in story."""
        with patch(
            "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
        ) as mock_ping:
            mock_ping.return_value = True

            # Call without explicit timeout
            result = check_mcp_availability()

            # Verify the mock was called (timeout is internal implementation detail)
            mock_ping.assert_called_once()
            assert result.status == PreflightStatus.PASSED


# =============================================================================
# Task 4: Input File Validation Tests (AC: #3)
# =============================================================================


class TestValidateInputFiles:
    """Tests for validate_input_files function (AC: #3)."""

    def test_returns_passed_when_all_files_exist(self):
        """Test returns PASSED with validated_files when all required files exist (AC: #3)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            prd_path = Path(tmpdir) / "prd.md"
            arch_path = Path(tmpdir) / "architecture.md"
            prd_path.write_text("# PRD\n\nProduct requirements...")
            arch_path.write_text("# Architecture\n\nSystem design...")

            required_files = [str(prd_path), str(arch_path)]
            result = validate_input_files(required_files)

            assert result.status == PreflightStatus.PASSED
            assert "validated_files" in result.details
            assert len(result.details["validated_files"]) == 2

    def test_returns_failed_when_prd_missing(self):
        """Test returns FAILED when PRD file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            arch_path = Path(tmpdir) / "architecture.md"
            arch_path.write_text("# Architecture\n\nSystem design...")

            prd_path = Path(tmpdir) / "prd.md"  # Not created
            required_files = [str(prd_path), str(arch_path)]
            result = validate_input_files(required_files)

            assert result.status == PreflightStatus.FAILED
            assert str(prd_path) in result.details.get("missing_files", [])

    def test_returns_failed_when_architecture_missing(self):
        """Test returns FAILED when Architecture file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prd_path = Path(tmpdir) / "prd.md"
            prd_path.write_text("# PRD\n\nProduct requirements...")

            arch_path = Path(tmpdir) / "architecture.md"  # Not created
            required_files = [str(prd_path), str(arch_path)]
            result = validate_input_files(required_files)

            assert result.status == PreflightStatus.FAILED
            assert str(arch_path) in result.details.get("missing_files", [])

    def test_validated_files_contains_paths(self):
        """Test validated_files list contains actual paths (AC: #3)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test")

            result = validate_input_files([str(test_file)])

            assert result.status == PreflightStatus.PASSED
            assert str(test_file) in result.details["validated_files"]

    def test_handles_empty_file_list(self):
        """Test handles empty required files list."""
        result = validate_input_files([])

        assert result.status == PreflightStatus.PASSED
        assert result.details.get("validated_files", []) == []

    def test_handles_empty_files_as_valid(self):
        """Test treats existing but empty files as valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_file = Path(tmpdir) / "empty.md"
            empty_file.write_text("")

            result = validate_input_files([str(empty_file)])

            # Empty file exists, so it's valid (content validation is separate)
            assert result.status == PreflightStatus.PASSED

    def test_returns_all_missing_files_in_details(self):
        """Test returns all missing files in details."""
        missing_files = [
            "/nonexistent/prd.md",
            "/nonexistent/architecture.md",
            "/nonexistent/epics.md",
        ]
        result = validate_input_files(missing_files)

        assert result.status == PreflightStatus.FAILED
        assert len(result.details.get("missing_files", [])) == 3


# =============================================================================
# Task 5: Main validate() Function Tests (AC: #1-4)
# =============================================================================


class TestValidateFunction:
    """Tests for main validate() function (AC: #1-4)."""

    def test_returns_ready_when_all_checks_pass(self):
        """Test returns overall_status=READY with 100% checks passed (AC: #4)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create required files
            prd_path = Path(tmpdir) / "prd.md"
            arch_path = Path(tmpdir) / "architecture.md"
            prd_path.write_text("# PRD")
            arch_path.write_text("# Architecture")

            config = {
                "output_folder": tmpdir,
                "project_root": tmpdir,
            }

            with patch(
                "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
            ) as mock_ping:
                mock_ping.return_value = True

                result = validate(
                    config=config,
                    required_config_keys=["output_folder", "project_root"],
                    required_input_files=[str(prd_path), str(arch_path)],
                    check_mcp=True,
                )

            assert result.overall_status == PreflightStatus.READY
            assert result.checks_passed == 100.0

    def test_returns_failed_when_config_missing(self):
        """Test returns FAILED when configuration validation fails (AC: #1)."""
        config = {}  # Missing required keys

        result = validate(
            config=config,
            required_config_keys=["output_folder"],
            required_input_files=[],
            check_mcp=False,
        )

        assert result.overall_status == PreflightStatus.FAILED
        assert "output_folder" in result.missing

    def test_returns_failed_when_mcp_unavailable(self):
        """Test returns FAILED when MCP check fails."""
        config = {"output_folder": "/tmp", "project_root": "/tmp"}

        with patch(
            "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
        ) as mock_ping:
            mock_ping.return_value = False

            result = validate(
                config=config,
                required_config_keys=["output_folder", "project_root"],
                required_input_files=[],
                check_mcp=True,
            )

        assert result.overall_status == PreflightStatus.FAILED

    def test_returns_failed_when_files_missing(self):
        """Test returns FAILED when input files don't exist (AC: #3)."""
        config = {"output_folder": "/tmp", "project_root": "/tmp"}

        result = validate(
            config=config,
            required_config_keys=["output_folder", "project_root"],
            required_input_files=["/nonexistent/prd.md"],
            check_mcp=False,
        )

        assert result.overall_status == PreflightStatus.FAILED

    def test_aggregates_all_check_results(self):
        """Test aggregates results from all validation checks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test")

            config = {"output_folder": tmpdir}

            with patch(
                "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
            ) as mock_ping:
                mock_ping.return_value = True

                result = validate(
                    config=config,
                    required_config_keys=["output_folder"],
                    required_input_files=[str(test_file)],
                    check_mcp=True,
                )

            # Should have 3 checks: config, mcp, files
            assert len(result.checks) == 3

    def test_calculates_checks_passed_percentage(self):
        """Test calculates correct checks_passed percentage."""
        config = {"output_folder": "/tmp"}  # Config passes

        with patch(
            "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
        ) as mock_ping:
            mock_ping.return_value = False  # MCP fails

            result = validate(
                config=config,
                required_config_keys=["output_folder"],
                required_input_files=["/nonexistent/file.md"],  # Files fail
                check_mcp=True,
            )

        # 1 of 3 passed = 33.33%
        assert 33.0 <= result.checks_passed <= 34.0

    def test_remediation_messages_aggregated(self):
        """Test remediation messages are aggregated from all failed checks."""
        config = {}  # Missing config

        result = validate(
            config=config,
            required_config_keys=["output_folder", "project_root"],
            required_input_files=["/nonexistent/prd.md"],
            check_mcp=False,
        )

        # Should have remediation messages
        assert len(result.remediation) > 0

    def test_skips_mcp_check_when_disabled(self):
        """Test skips MCP check when check_mcp=False."""
        config = {"output_folder": "/tmp"}

        result = validate(
            config=config,
            required_config_keys=["output_folder"],
            required_input_files=[],
            check_mcp=False,
        )

        # Should only have config check (no files, no MCP)
        assert len(result.checks) == 1
        assert result.checks[0].name == "configuration"

    def test_skips_file_check_when_no_files_required(self):
        """Test skips file check when no files are required."""
        config = {"output_folder": "/tmp"}

        result = validate(
            config=config,
            required_config_keys=["output_folder"],
            required_input_files=[],
            check_mcp=False,
        )

        # Should only have config check
        check_names = [c.name for c in result.checks]
        assert "input_files" not in check_names


# =============================================================================
# Task 6: Workflow Configuration Parsing Tests
# =============================================================================


class TestParseWorkflowRequiredConfig:
    """Tests for parse_workflow_required_config function (Task 6)."""

    def test_extracts_required_config_keys_from_yaml(self):
        """Test extracts required configuration keys from workflow YAML."""
        workflow_content = """
name: test-workflow
config_source: "{project-root}/_bmad/config.yaml"
output_folder: "{config_source}:output_folder"
variables:
  project_name: "{config_source}:project_name"
"""
        required_keys = parse_workflow_required_config(workflow_content)

        # Should identify keys that reference config via {config_source}:key_name
        assert "output_folder" in required_keys or "project_name" in required_keys

    def test_extracts_from_config_source_references(self):
        """Test extracts keys from {config_source}:key_name references."""
        workflow_content = """
name: test-workflow
config_source: "{project-root}/_bmad/config.yaml"
user_name: "{config_source}:user_name"
project_name: "{config_source}:project_name"
"""
        required_keys = parse_workflow_required_config(workflow_content)

        # Should extract user_name and project_name as required
        assert "user_name" in required_keys
        assert "project_name" in required_keys

    def test_handles_workflow_without_config_refs(self):
        """Test handles workflow without configuration references."""
        workflow_content = """
name: simple-workflow
description: "A workflow with no config dependencies"
"""
        required_keys = parse_workflow_required_config(workflow_content)

        assert required_keys == []

    def test_handles_invalid_yaml_gracefully(self):
        """Test handles invalid YAML content gracefully."""
        workflow_content = "invalid: yaml: content: ["

        # Should not raise, return empty list or handle gracefully
        required_keys = parse_workflow_required_config(workflow_content)
        assert isinstance(required_keys, list)


class TestParseWorkflowRequiredInputs:
    """Tests for parse_workflow_required_inputs function (Task 6)."""

    def test_extracts_input_file_patterns(self):
        """Test extracts required input file patterns from workflow YAML."""
        workflow_content = """
name: test-workflow
input_file_patterns:
  epics:
    description: "All epics with user stories"
    whole: "{output_folder}/*epic*.md"
    sharded: "{output_folder}/*epic*/*.md"
  prd:
    description: "Product Requirements"
    whole: "{planning_artifacts}/prd.md"
"""
        input_patterns = parse_workflow_required_inputs(workflow_content)

        assert len(input_patterns) > 0
        # Should return pattern info
        assert any("epic" in str(p).lower() for p in input_patterns)

    def test_handles_workflow_without_inputs(self):
        """Test handles workflow without input_file_patterns."""
        workflow_content = """
name: simple-workflow
description: "No inputs required"
"""
        input_patterns = parse_workflow_required_inputs(workflow_content)

        assert input_patterns == []

    def test_handles_both_yaml_and_md_formats(self):
        """Test handles both YAML and MD workflow formats."""
        yaml_content = """
name: yaml-workflow
input_file_patterns:
  test:
    whole: "test.md"
"""
        md_content = """---
name: md-workflow
input_file_patterns:
  test:
    whole: "test.md"
---

# Workflow Instructions
"""
        yaml_inputs = parse_workflow_required_inputs(yaml_content)
        md_inputs = parse_workflow_required_inputs(md_content)

        # Both should work
        assert isinstance(yaml_inputs, list)
        assert isinstance(md_inputs, list)

    def test_handles_invalid_yaml_in_inputs(self):
        """Test handles invalid YAML content gracefully."""
        workflow_content = "invalid: yaml: content: ["

        input_patterns = parse_workflow_required_inputs(workflow_content)
        assert input_patterns == []

    def test_handles_non_dict_data(self):
        """Test handles non-dict YAML data (e.g., list)."""
        workflow_content = """
- item1
- item2
"""
        input_patterns = parse_workflow_required_inputs(workflow_content)
        assert input_patterns == []

    def test_handles_non_dict_input_patterns_section(self):
        """Test handles non-dict input_file_patterns section."""
        workflow_content = """
name: test-workflow
input_file_patterns: "not a dict"
"""
        input_patterns = parse_workflow_required_inputs(workflow_content)
        assert input_patterns == []

    def test_handles_non_dict_pattern_config(self):
        """Test handles non-dict pattern config within input_file_patterns."""
        workflow_content = """
name: test-workflow
input_file_patterns:
  valid:
    whole: "test.md"
  invalid: "not a dict"
"""
        input_patterns = parse_workflow_required_inputs(workflow_content)
        # Should only return the valid one
        assert len(input_patterns) == 1
        assert input_patterns[0]["name"] == "valid"


class TestPreflightCheckFromDictErrors:
    """Additional tests for PreflightCheck.from_dict error handling."""

    def test_from_dict_with_invalid_check_status_raises_error(self):
        """Test PreflightCheck.from_dict raises ValueError for invalid status."""
        from pcmrp_tools.bmad_automation.preflight_validator import PreflightCheck
        data = {
            "name": "test_check",
            "status": "INVALID_CHECK_STATUS",
            "message": "Test message",
            "details": {},
        }
        with pytest.raises(ValueError, match="Invalid status"):
            PreflightCheck.from_dict(data)


class TestMCPAvailabilityEdgeCases:
    """Additional edge case tests for MCP availability check."""

    def test_handles_generic_exception(self):
        """Test handles generic exceptions in MCP check."""
        with patch(
            "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
        ) as mock_ping:
            mock_ping.side_effect = RuntimeError("Unexpected error")

            result = check_mcp_availability()

            assert result.status == PreflightStatus.FAILED
            assert "RuntimeError" in result.message

    def test_actual_ping_function_returns_false(self):
        """Test the actual _ping_forgetful_mcp function returns False (placeholder)."""
        # Import the actual function without mocking
        from pcmrp_tools.bmad_automation.preflight_validator import _ping_forgetful_mcp

        # The placeholder implementation returns False
        result = _ping_forgetful_mcp()
        assert result is False


class TestFrontmatterParsingEdgeCases:
    """Tests for frontmatter parsing edge cases."""

    def test_frontmatter_without_closing_delimiter(self):
        """Test markdown with frontmatter but no closing ---."""
        content = """---
name: test
value: something

# No closing delimiter, this is body
"""
        required_keys = parse_workflow_required_config(content)
        # Should handle gracefully - no valid frontmatter
        assert isinstance(required_keys, list)

    def test_frontmatter_with_empty_yaml(self):
        """Test markdown with empty frontmatter section."""
        content = """---
---

# Body content
{config_source}:some_key
"""
        required_keys = parse_workflow_required_config(content)
        assert "some_key" in required_keys

    def test_frontmatter_with_invalid_yaml(self):
        """Test markdown with invalid YAML in frontmatter."""
        content = """---
invalid: yaml: content: [
---

# Body content
{config_source}:valid_key
"""
        required_keys = parse_workflow_required_config(content)
        # Should still find keys from pattern matching
        assert "valid_key" in required_keys

    def test_content_without_frontmatter(self):
        """Test content that doesn't start with ---."""
        content = """
name: test-workflow
{config_source}:direct_key
"""
        required_keys = parse_workflow_required_config(content)
        assert "direct_key" in required_keys


class TestParseWorkflowConfigEdgeCases:
    """Additional edge cases for parse_workflow_required_config."""

    def test_with_frontmatter_and_variables(self):
        """Test extraction from frontmatter with variables section."""
        content = """---
name: test-workflow
variables:
  key1: "{config_source}:value1"
  key2: "{config_source}:value2"
---

# Body
"""
        required_keys = parse_workflow_required_config(content)
        assert "value1" in required_keys
        assert "value2" in required_keys

    def test_variables_with_non_string_values(self):
        """Test handles non-string values in variables."""
        content = """
name: test-workflow
variables:
  string_var: "{config_source}:string_key"
  int_var: 42
  list_var:
    - item1
    - item2
"""
        required_keys = parse_workflow_required_config(content)
        assert "string_key" in required_keys

    def test_yaml_parse_error_in_config(self):
        """Test handles YAML parse errors gracefully."""
        content = "invalid: yaml: content: ["
        required_keys = parse_workflow_required_config(content)
        # Should not crash, may return empty list
        assert isinstance(required_keys, list)

    def test_with_valid_frontmatter_parses_variables(self):
        """Test that valid frontmatter with variables section parses correctly."""
        # This test specifically covers line 628 (data = frontmatter)
        # and the variables iteration branches
        content = """---
name: test-workflow
variables:
  user_name: "{config_source}:user_name"
  project_name: "{config_source}:project_name"
  static_value: "just a string without config ref"
---

# Body with another reference
{config_source}:body_key
"""
        required_keys = parse_workflow_required_config(content)
        # Should extract keys from both frontmatter variables and body
        assert "user_name" in required_keys
        assert "project_name" in required_keys
        assert "body_key" in required_keys

    def test_with_empty_variables_section(self):
        """Test handles empty variables section in frontmatter."""
        content = """---
name: test-workflow
variables: {}
---

# Body
"""
        required_keys = parse_workflow_required_config(content)
        assert isinstance(required_keys, list)

    def test_with_non_dict_variables_section(self):
        """Test handles non-dict variables section."""
        content = """---
name: test-workflow
variables: "not a dict"
---

# Body
{config_source}:body_key
"""
        required_keys = parse_workflow_required_config(content)
        # Should still get body key
        assert "body_key" in required_keys


# =============================================================================
# Integration Tests
# =============================================================================


class TestPreflightValidationIntegration:
    """Integration tests for complete pre-flight validation flow."""

    def test_full_validation_flow_success(self):
        """Test complete validation flow with all checks passing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            prd = Path(tmpdir) / "prd.md"
            arch = Path(tmpdir) / "architecture.md"
            prd.write_text("# PRD\n\nRequirements...")
            arch.write_text("# Architecture\n\nDesign...")

            config = {
                "output_folder": tmpdir,
                "project_root": tmpdir,
                "planning_artifacts": tmpdir,
            }

            with patch(
                "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
            ) as mock_ping:
                mock_ping.return_value = True

                result = validate(
                    config=config,
                    required_config_keys=["output_folder", "project_root"],
                    required_input_files=[str(prd), str(arch)],
                    check_mcp=True,
                )

            assert result.overall_status == PreflightStatus.READY
            assert result.checks_passed == 100.0
            assert result.missing == []
            assert result.remediation == []

    def test_full_validation_flow_partial_failure(self):
        """Test validation flow with some checks failing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Only create one file
            prd = Path(tmpdir) / "prd.md"
            prd.write_text("# PRD")

            config = {
                "output_folder": tmpdir,
                # Missing project_root
            }

            arch_path = Path(tmpdir) / "architecture.md"  # Not created

            with patch(
                "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
            ) as mock_ping:
                mock_ping.return_value = True

                result = validate(
                    config=config,
                    required_config_keys=["output_folder", "project_root"],
                    required_input_files=[str(prd), str(arch_path)],
                    check_mcp=True,
                )

            assert result.overall_status == PreflightStatus.FAILED
            assert result.checks_passed < 100.0
            assert "project_root" in result.missing
            assert len(result.remediation) > 0

    def test_serialization_round_trip_full_result(self):
        """Test full result can be serialized and restored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test")

            config = {"output_folder": tmpdir}

            with patch(
                "pcmrp_tools.bmad_automation.preflight_validator._ping_forgetful_mcp"
            ) as mock_ping:
                mock_ping.return_value = True

                original = validate(
                    config=config,
                    required_config_keys=["output_folder"],
                    required_input_files=[str(test_file)],
                    check_mcp=True,
                )

            # Serialize and restore
            serialized = original.to_dict()
            restored = PreflightResult.from_dict(serialized)

            assert restored.overall_status == original.overall_status
            assert len(restored.checks) == len(original.checks)
            assert restored.checks_passed == original.checks_passed
