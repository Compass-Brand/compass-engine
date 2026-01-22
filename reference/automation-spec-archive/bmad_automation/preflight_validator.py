"""Pre-flight Configuration Validator for BMAD Automation.

This module provides the PreflightResult dataclass, PreflightStatus enum, and
validation functions that form the pre-flight validation system for BMAD workflows.

The Pre-flight Validator runs before workflow execution to validate:
- Required configuration keys are present and non-empty
- MCP (Forgetful) availability
- Required input files exist

Component: Pre-flight Validation Subagent (Tier 1 - No dependencies)
Story: 1.2 - Pre-flight Configuration Validation
Epic: 1 - Foundation Validation
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


# =============================================================================
# Status Enum (Task 1)
# =============================================================================


class PreflightStatus(Enum):
    """Status values for pre-flight validation checks.

    Each status indicates the outcome of a validation check:
    - PASSED: Check completed successfully
    - FAILED: Check failed, blocking workflow execution
    - READY: Overall status when all checks pass
    - WARNING: Check passed with warnings (non-blocking)
    """

    PASSED = "PASSED"
    FAILED = "FAILED"
    READY = "READY"
    WARNING = "WARNING"


# =============================================================================
# PreflightCheck Dataclass (Task 1)
# =============================================================================


@dataclass
class PreflightCheck:
    """Result of a single pre-flight validation check.

    Represents the outcome of one validation step (e.g., config check,
    MCP availability check, file existence check).

    Attributes:
        name: Identifier for the check (e.g., "configuration", "mcp", "input_files").
        status: The check result status.
        message: Human-readable description of the check result.
        details: Additional check-specific information (e.g., missing keys, validated files).
    """

    name: str
    status: PreflightStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    # Factory methods for common check results

    @classmethod
    def passed(
        cls,
        name: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> PreflightCheck:
        """Create a passed check result.

        Args:
            name: Check identifier.
            message: Success message.
            details: Optional additional details.

        Returns:
            PreflightCheck with PASSED status.
        """
        return cls(
            name=name,
            status=PreflightStatus.PASSED,
            message=message,
            details=details or {},
        )

    @classmethod
    def failed(
        cls,
        name: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> PreflightCheck:
        """Create a failed check result.

        Args:
            name: Check identifier.
            message: Failure message.
            details: Optional additional details (e.g., missing keys).

        Returns:
            PreflightCheck with FAILED status.
        """
        return cls(
            name=name,
            status=PreflightStatus.FAILED,
            message=message,
            details=details or {},
        )

    @classmethod
    def warning(
        cls,
        name: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> PreflightCheck:
        """Create a warning check result.

        Args:
            name: Check identifier.
            message: Warning message.
            details: Optional additional details.

        Returns:
            PreflightCheck with WARNING status.
        """
        return cls(
            name=name,
            status=PreflightStatus.WARNING,
            message=message,
            details=details or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert PreflightCheck to a dictionary.

        Returns:
            Dictionary representation with status as string value.
        """
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PreflightCheck:
        """Create PreflightCheck from a dictionary.

        Args:
            data: Dictionary with name, status, message, details.

        Returns:
            PreflightCheck instance.

        Raises:
            ValueError: If status string is not a valid PreflightStatus.
        """
        status_str = data["status"]
        status_mapping = {s.value: s for s in PreflightStatus}
        if status_str not in status_mapping:
            raise ValueError(
                f"Invalid status: '{status_str}'. "
                f"Valid statuses are: {list(status_mapping.keys())}"
            )

        return cls(
            name=data["name"],
            status=status_mapping[status_str],
            message=data["message"],
            details=data.get("details", {}),
        )


# =============================================================================
# PreflightResult Dataclass (Task 1)
# =============================================================================


@dataclass
class PreflightResult:
    """Result of complete pre-flight validation for a BMAD workflow.

    Contains the overall validation status along with individual check results,
    list of missing configuration/files, and remediation suggestions.

    Attributes:
        overall_status: READY if all checks pass, FAILED otherwise.
        checks: List of individual PreflightCheck results.
        missing: List of missing configuration keys or file names.
        remediation: List of remediation messages for failed checks.
        checks_passed: Percentage of checks that passed (0.0 to 100.0).
    """

    overall_status: PreflightStatus
    checks: list[PreflightCheck]
    missing: list[str] = field(default_factory=list)
    remediation: list[str] = field(default_factory=list)
    checks_passed: float = 0.0

    # Factory methods for overall results

    @classmethod
    def ready(cls, checks: list[PreflightCheck]) -> PreflightResult:
        """Create a READY result when all checks pass.

        Args:
            checks: List of all check results (all should be PASSED).

        Returns:
            PreflightResult with READY status and 100% checks passed.
        """
        return cls(
            overall_status=PreflightStatus.READY,
            checks=checks,
            missing=[],
            remediation=[],
            checks_passed=100.0,
        )

    @classmethod
    def failed(
        cls,
        checks: list[PreflightCheck],
        missing: list[str],
        remediation: list[str],
    ) -> PreflightResult:
        """Create a FAILED result when one or more checks fail.

        Args:
            checks: List of all check results.
            missing: List of missing configuration keys or files.
            remediation: List of remediation suggestions.

        Returns:
            PreflightResult with FAILED status and calculated checks_passed percentage.
        """
        passed_count = sum(
            1 for c in checks if c.status in (PreflightStatus.PASSED, PreflightStatus.WARNING)
        )
        total_count = len(checks)
        checks_passed = (passed_count / total_count * 100.0) if total_count > 0 else 0.0

        return cls(
            overall_status=PreflightStatus.FAILED,
            checks=checks,
            missing=missing,
            remediation=remediation,
            checks_passed=checks_passed,
        )

    # Serialization methods

    def to_dict(self) -> dict[str, Any]:
        """Convert PreflightResult to a dictionary.

        Returns:
            Dictionary representation with status values as strings.
        """
        return {
            "overall_status": self.overall_status.value,
            "checks": [c.to_dict() for c in self.checks],
            "missing": self.missing,
            "remediation": self.remediation,
            "checks_passed": self.checks_passed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PreflightResult:
        """Create PreflightResult from a dictionary.

        Args:
            data: Dictionary with overall_status, checks, missing, remediation, checks_passed.

        Returns:
            PreflightResult instance.

        Raises:
            ValueError: If overall_status string is not a valid PreflightStatus.
        """
        status_str = data["overall_status"]
        status_mapping = {s.value: s for s in PreflightStatus}
        if status_str not in status_mapping:
            raise ValueError(
                f"Invalid status: '{status_str}'. "
                f"Valid statuses are: {list(status_mapping.keys())}"
            )

        checks = [PreflightCheck.from_dict(c) for c in data.get("checks", [])]

        return cls(
            overall_status=status_mapping[status_str],
            checks=checks,
            missing=data.get("missing", []),
            remediation=data.get("remediation", []),
            checks_passed=data.get("checks_passed", 0.0),
        )


# =============================================================================
# Configuration Validation (Task 2)
# =============================================================================


def validate_configuration(
    config: dict[str, Any],
    required_keys: list[str],
) -> PreflightCheck:
    """Validate that required configuration keys are present and non-empty.

    Checks each required key exists in the config dict and has a non-empty value.
    None values and empty strings are treated as missing.

    Args:
        config: Configuration dictionary to validate.
        required_keys: List of required configuration key names.

    Returns:
        PreflightCheck with PASSED if all keys present, FAILED otherwise.
    """
    if not required_keys:
        return PreflightCheck.passed(
            name="configuration",
            message="No configuration keys required",
            details={"checked_keys": []},
        )

    missing_keys = []
    for key in required_keys:
        value = config.get(key)
        if value is None or value == "":
            missing_keys.append(key)

    if missing_keys:
        return PreflightCheck.failed(
            name="configuration",
            message=f"Missing required configuration: {', '.join(missing_keys)}",
            details={"missing": missing_keys, "checked_keys": required_keys},
        )

    return PreflightCheck.passed(
        name="configuration",
        message="All required configuration keys present",
        details={"checked_keys": required_keys},
    )


# =============================================================================
# MCP Availability Check (Task 3)
# =============================================================================


def _ping_forgetful_mcp() -> bool:
    """Internal function to ping Forgetful MCP.

    This is a placeholder that should be replaced with actual MCP connectivity check.
    In tests, this function is mocked.

    Returns:
        True if MCP is available, False otherwise.
    """
    # TODO: Implement actual MCP connectivity check
    # For now, this is a placeholder that will be mocked in tests
    return False


def check_mcp_availability(
    timeout_seconds: float = 5.0,
    warn_threshold_seconds: float = 2.0,
) -> PreflightCheck:
    """Check if Forgetful MCP is available.

    Attempts to connect to the Forgetful MCP server with a timeout.
    Returns PASSED if available, FAILED if not, WARNING if slow.

    Args:
        timeout_seconds: Maximum time to wait for MCP response (default 5s).
        warn_threshold_seconds: Response time above this triggers WARNING (default 2s).

    Returns:
        PreflightCheck with status based on MCP availability.
    """
    try:
        available = _ping_forgetful_mcp()

        if available:
            return PreflightCheck.passed(
                name="mcp_availability",
                message="Forgetful MCP is available",
                details={"timeout_used": timeout_seconds},
            )
        else:
            return PreflightCheck.failed(
                name="mcp_availability",
                message="Forgetful MCP is not available",
                details={"timeout_used": timeout_seconds},
            )

    except TimeoutError as e:
        return PreflightCheck.failed(
            name="mcp_availability",
            message=f"Forgetful MCP timed out after {timeout_seconds}s",
            details={"error": str(e), "timeout_used": timeout_seconds},
        )

    except ConnectionError as e:
        return PreflightCheck.failed(
            name="mcp_availability",
            message="Forgetful MCP connection failed",
            details={"error": str(e), "timeout_used": timeout_seconds},
        )

    except Exception as e:
        return PreflightCheck.failed(
            name="mcp_availability",
            message=f"Forgetful MCP check failed: {type(e).__name__}",
            details={"error": str(e), "timeout_used": timeout_seconds},
        )


# =============================================================================
# Input File Validation (Task 4)
# =============================================================================


def validate_input_files(required_files: list[str]) -> PreflightCheck:
    """Validate that required input files exist.

    Checks each required file path exists on the filesystem.

    Args:
        required_files: List of file paths to validate.

    Returns:
        PreflightCheck with PASSED if all files exist, FAILED otherwise.
        On success, details contains 'validated_files' list.
        On failure, details contains 'missing_files' list.
    """
    if not required_files:
        return PreflightCheck.passed(
            name="input_files",
            message="No input files required",
            details={"validated_files": []},
        )

    validated_files = []
    missing_files = []

    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            validated_files.append(str(path))
        else:
            missing_files.append(str(path))

    if missing_files:
        return PreflightCheck.failed(
            name="input_files",
            message=f"Missing required input files: {len(missing_files)} file(s)",
            details={
                "missing_files": missing_files,
                "validated_files": validated_files,
            },
        )

    return PreflightCheck.passed(
        name="input_files",
        message=f"All {len(validated_files)} required input files exist",
        details={"validated_files": validated_files},
    )


# =============================================================================
# Main Validate Function (Task 5)
# =============================================================================


def validate(
    config: dict[str, Any],
    required_config_keys: list[str],
    required_input_files: list[str],
    check_mcp: bool = True,
) -> PreflightResult:
    """Run all pre-flight validation checks and return aggregate result.

    Orchestrates configuration validation, MCP availability check, and
    input file validation. Returns READY only when all checks pass.

    Args:
        config: Configuration dictionary to validate.
        required_config_keys: List of required configuration key names.
        required_input_files: List of required input file paths.
        check_mcp: Whether to check MCP availability (default True).

    Returns:
        PreflightResult with overall_status READY if all pass, FAILED otherwise.
    """
    checks: list[PreflightCheck] = []
    all_missing: list[str] = []
    all_remediation: list[str] = []

    # Check 1: Configuration validation
    config_check = validate_configuration(config, required_config_keys)
    checks.append(config_check)

    if config_check.status == PreflightStatus.FAILED:
        missing_keys = config_check.details.get("missing", [])
        all_missing.extend(missing_keys)
        for key in missing_keys:
            all_remediation.append(f"Add '{key}' to workflow configuration")

    # Check 2: MCP availability (optional)
    if check_mcp:
        mcp_check = check_mcp_availability()
        checks.append(mcp_check)

        if mcp_check.status == PreflightStatus.FAILED:
            all_remediation.append("Ensure Forgetful MCP server is running and accessible")

    # Check 3: Input files (only if files are specified)
    if required_input_files:
        files_check = validate_input_files(required_input_files)
        checks.append(files_check)

        if files_check.status == PreflightStatus.FAILED:
            missing_files = files_check.details.get("missing_files", [])
            for f in missing_files:
                all_missing.append(Path(f).name)
                all_remediation.append(f"Create or locate required file: {f}")

    # Calculate overall status
    all_passed = all(
        c.status in (PreflightStatus.PASSED, PreflightStatus.WARNING) for c in checks
    )

    if all_passed:
        return PreflightResult.ready(checks)
    else:
        return PreflightResult.failed(
            checks=checks,
            missing=all_missing,
            remediation=all_remediation,
        )


# =============================================================================
# Workflow Configuration Parsing (Task 6)
# =============================================================================


def _extract_frontmatter(content: str) -> tuple[str, dict[str, Any] | None]:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Full content (may have YAML frontmatter).

    Returns:
        Tuple of (body_content, frontmatter_dict).
    """
    if not content.startswith("---"):
        return content, None

    lines = content.split("\n")
    end_index = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break

    if end_index is None:
        return content, None

    frontmatter_text = "\n".join(lines[1:end_index])
    body_text = "\n".join(lines[end_index + 1 :])

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if frontmatter is None:
            frontmatter = {}
    except yaml.YAMLError:
        frontmatter = {}

    return body_text, frontmatter


def parse_workflow_required_config(content: str) -> list[str]:
    """Parse workflow content to extract required configuration keys.

    Analyzes workflow YAML (or markdown with YAML frontmatter) to identify
    configuration keys that must be provided. Looks for:
    - References like {config_source}:key_name
    - Top-level keys that reference variables

    Args:
        content: Workflow file content (YAML or Markdown with frontmatter).

    Returns:
        List of required configuration key names.
    """
    required_keys: list[str] = []

    # Handle markdown with frontmatter
    body, frontmatter = _extract_frontmatter(content)

    # Determine which data to use for structure parsing
    data = None
    if frontmatter:
        # Use frontmatter directly (already parsed by _extract_frontmatter)
        data = frontmatter
    else:
        # Try to parse as plain YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError:
            data = None

    # Pattern to find {config_source}:key_name references
    config_ref_pattern = re.compile(r"\{config_source\}:(\w+)")

    # Search for config references in the raw content
    matches = config_ref_pattern.findall(content)
    required_keys.extend(matches)

    # Also look for common required keys in the parsed data
    if data and isinstance(data, dict):
        # Check for variable references
        variables = data.get("variables", {})
        if isinstance(variables, dict):
            for value in variables.values():
                if isinstance(value, str):
                    ref_matches = config_ref_pattern.findall(value)
                    required_keys.extend(ref_matches)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(required_keys))


def parse_workflow_required_inputs(content: str) -> list[dict[str, Any]]:
    """Parse workflow content to extract required input file patterns.

    Analyzes workflow YAML to identify input file patterns that must be provided.
    Looks for input_file_patterns section.

    Args:
        content: Workflow file content (YAML or Markdown with frontmatter).

    Returns:
        List of input file pattern dictionaries.
    """
    input_patterns: list[dict[str, Any]] = []

    # Handle markdown with frontmatter
    body, frontmatter = _extract_frontmatter(content)

    # Parse YAML content
    try:
        if frontmatter:
            data = frontmatter
        else:
            data = yaml.safe_load(content)
    except yaml.YAMLError:
        return []

    if not data or not isinstance(data, dict):
        return []

    # Look for input_file_patterns section
    patterns_section = data.get("input_file_patterns", {})
    if not isinstance(patterns_section, dict):
        return []

    for name, pattern_config in patterns_section.items():
        if isinstance(pattern_config, dict):
            input_patterns.append(
                {
                    "name": name,
                    "whole": pattern_config.get("whole"),
                    "sharded": pattern_config.get("sharded"),
                    "description": pattern_config.get("description"),
                }
            )

    return input_patterns
