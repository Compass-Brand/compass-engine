"""Workflow Entry Wrapper - Skill Invocation and Project Type Detection.

This module provides functionality to:
1. Detect and parse BMAD skill invocations in the format: /bmad:{module}:{type}:{name}
2. Detect project type (greenfield vs brownfield) based on directory structure

Examples:
    /bmad:bmm:workflows:dev-story
    /bmad:core:workflows:brainstorming
    /bmad:bmb:agents:agent-builder
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Match, Optional

import yaml


class BMADModule(Enum):
    """Valid BMAD module identifiers.

    Attributes:
        CORE: Core BMAD functionality
        BMM: BMAD Method Manager
        BMB: BMAD Module Builder
    """
    CORE = "core"
    BMM = "bmm"
    BMB = "bmb"


class SkillType(Enum):
    """Valid BMAD skill types.

    Attributes:
        WORKFLOWS: Multi-step workflow definitions
        AGENTS: Agent configurations
        TASKS: Individual task definitions
    """
    WORKFLOWS = "workflows"
    AGENTS = "agents"
    TASKS = "tasks"


# =============================================================================
# Skill Pattern Regex (Task 2)
# =============================================================================

# Pattern to match /bmad:{module}:{type}:{name}
# - Case-insensitive for /bmad prefix
# - Captures module, type, and name in named groups
# - Names can contain letters, numbers, hyphens, and underscores
SKILL_PATTERN = re.compile(
    r"/bmad:(?P<module>[a-zA-Z]+):(?P<type>[a-zA-Z]+):(?P<name>[a-zA-Z0-9_-]+)",
    re.IGNORECASE,
)


def match_skill_pattern(text: str) -> Optional[Match[str]]:
    """Search for a skill invocation pattern in the given text.

    Args:
        text: The input text to search for a skill pattern

    Returns:
        A Match object if a skill pattern is found, None otherwise.
        The match has named groups: 'module', 'type', 'name'
    """
    return SKILL_PATTERN.search(text)


# Forward declaration - detect_skill_invocation defined after SkillInvocation class


@dataclass
class SkillInvocation:
    """Result of skill invocation detection.

    Attributes:
        detected: Whether a valid skill pattern was detected
        module: The BMAD module (core, bmm, bmb) if detected
        skill_type: The skill type (workflows, agents, tasks) if detected
        name: The skill name if detected
        error: Error message if pattern was malformed
        raw_input: The original input string
    """
    detected: bool
    module: Optional[BMADModule] = None
    skill_type: Optional[SkillType] = None
    name: Optional[str] = None
    error: Optional[str] = None
    raw_input: str = ""

    @classmethod
    def detected_skill(
        cls,
        module: BMADModule,
        skill_type: SkillType,
        name: str,
        raw_input: str,
    ) -> "SkillInvocation":
        """Factory method for creating a successfully detected skill invocation.

        Args:
            module: The BMAD module
            skill_type: The skill type
            name: The skill name
            raw_input: The original input string

        Returns:
            SkillInvocation with detected=True and populated fields
        """
        return cls(
            detected=True,
            module=module,
            skill_type=skill_type,
            name=name,
            error=None,
            raw_input=raw_input,
        )

    @classmethod
    def not_detected(cls, raw_input: str) -> "SkillInvocation":
        """Factory method for when no skill pattern is found.

        Args:
            raw_input: The original input string

        Returns:
            SkillInvocation with detected=False and no error
        """
        return cls(
            detected=False,
            module=None,
            skill_type=None,
            name=None,
            error=None,
            raw_input=raw_input,
        )

    @classmethod
    def invalid(cls, error: str, raw_input: str) -> "SkillInvocation":
        """Factory method for malformed skill patterns.

        Args:
            error: Description of the validation error
            raw_input: The original input string

        Returns:
            SkillInvocation with detected=False and error message
        """
        return cls(
            detected=False,
            module=None,
            skill_type=None,
            name=None,
            error=error,
            raw_input=raw_input,
        )


# =============================================================================
# Project Type Detection (Story 2a.3)
# =============================================================================


class ProjectType(Enum):
    """Project type classification.

    Attributes:
        GREENFIELD: New project with minimal existing code
        BROWNFIELD: Existing project with established codebase
    """
    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"


@dataclass
class DetectionSignal:
    """A single signal used in project type detection.

    Attributes:
        name: Identifier for the signal (e.g., "has_source_directory")
        detected: Whether the signal condition was met
        details: Human-readable description of what was found
    """
    name: str
    detected: bool
    details: str = ""


@dataclass
class ProjectTypeResult:
    """Result of project type detection.

    Attributes:
        project_type: The detected project type (greenfield or brownfield)
        detection_signals: List of signals that contributed to the detection
        confidence: Confidence level of the detection (0.0 to 1.0)
    """
    project_type: ProjectType
    detection_signals: list[DetectionSignal] = field(default_factory=list)
    confidence: float = 1.0

    @classmethod
    def greenfield(
        cls,
        signals: list[DetectionSignal],
        confidence: float = 1.0,
    ) -> "ProjectTypeResult":
        """Factory method for creating a greenfield project result.

        Args:
            signals: Detection signals that led to this classification
            confidence: Confidence level of the detection

        Returns:
            ProjectTypeResult with project_type=GREENFIELD
        """
        return cls(
            project_type=ProjectType.GREENFIELD,
            detection_signals=signals,
            confidence=confidence,
        )

    @classmethod
    def brownfield(
        cls,
        signals: list[DetectionSignal],
        confidence: float = 1.0,
    ) -> "ProjectTypeResult":
        """Factory method for creating a brownfield project result.

        Args:
            signals: Detection signals that led to this classification
            confidence: Confidence level of the detection

        Returns:
            ProjectTypeResult with project_type=BROWNFIELD
        """
        return cls(
            project_type=ProjectType.BROWNFIELD,
            detection_signals=signals,
            confidence=confidence,
        )


# =============================================================================
# Skill Invocation Detection (Story 2a.3 continued)
# =============================================================================


def detect_skill_invocation(text: str) -> SkillInvocation:
    """Detect and parse a BMAD skill invocation pattern from input text.

    Args:
        text: The input text to search for a skill pattern

    Returns:
        SkillInvocation with detection results and parsed components
    """
    if not text or not text.strip():
        return SkillInvocation.not_detected(raw_input=text or "")

    match = SKILL_PATTERN.search(text)
    if not match:
        return SkillInvocation.not_detected(raw_input=text)

    module_str = match.group("module").lower()
    type_str = match.group("type").lower()
    name = match.group("name")

    try:
        module = BMADModule(module_str)
    except ValueError:
        return SkillInvocation.invalid(
            error=f"invalid_module:{module_str}",
            raw_input=text,
        )

    try:
        skill_type = SkillType(type_str)
    except ValueError:
        return SkillInvocation.invalid(
            error=f"invalid_type:{type_str}",
            raw_input=text,
        )

    return SkillInvocation.detected_skill(
        module=module,
        skill_type=skill_type,
        name=name,
        raw_input=text,
    )


# Main entry point alias for Task 6 integration
detect_and_parse_skill = detect_skill_invocation
"""Alias for detect_skill_invocation() - main entry point for skill detection.

This is the primary function to use when detecting BMAD skill invocations.
It combines pattern detection with validation and returns a complete SkillInvocation.
"""


# =============================================================================
# Story 2a.6: Workflow Configuration Parsing
# =============================================================================


@dataclass
class ConfigParseError:
    """Structured error from configuration parsing.

    Attributes:
        message: The error type/message (e.g., "config_parse_error")
        line_number: The line number where the error occurred (if available)
        details: Detailed error information
    """
    message: str
    line_number: Optional[int] = None
    details: str = ""


@dataclass
class WorkflowConfig:
    """Workflow configuration parsed from YAML or Markdown frontmatter.

    Attributes:
        module: The BMAD module type (core, bmm, bmb)
        settings: Configuration settings dict
        thresholds: Threshold values dict
        raw_config: The original parsed configuration dict
        error: Parse error if configuration failed to load
    """
    module: BMADModule
    settings: dict[str, Any] = field(default_factory=dict)
    thresholds: dict[str, int] = field(default_factory=dict)
    raw_config: dict = field(default_factory=dict)
    error: Optional[ConfigParseError] = None

    @classmethod
    def bmm_defaults(cls) -> "WorkflowConfig":
        """Factory method for creating BMM module default configuration.

        Returns:
            WorkflowConfig with BMM-specific defaults
        """
        return cls(
            module=BMADModule.BMM,
            settings={
                "batch_size": 5,
                "confidence_threshold": 80,
                "checkpoint_frequency": "per_step",
            },
            thresholds={},
        )

    @classmethod
    def bmb_defaults(cls) -> "WorkflowConfig":
        """Factory method for creating BMB module default configuration.

        Returns:
            WorkflowConfig with BMB-specific defaults including thresholds
        """
        return cls(
            module=BMADModule.BMB,
            settings={
                "party_mode_auto_trigger": True,
            },
            thresholds={
                "blocking_errors": 3,
                "major_issues": 5,
                "compliance_score": 70,
            },
        )

    @classmethod
    def core_defaults(cls) -> "WorkflowConfig":
        """Factory method for creating Core module default configuration.

        Returns:
            WorkflowConfig with Core-specific defaults
        """
        return cls(
            module=BMADModule.CORE,
            settings={
                "batch_size": "auto",
                "confidence_threshold": 80,
                "checkpoint_frequency": "minimal",
            },
            thresholds={},
        )

    @classmethod
    def from_error(cls, error: ConfigParseError) -> "WorkflowConfig":
        """Factory method for creating a config from a parse error.

        Args:
            error: The parse error that occurred

        Returns:
            WorkflowConfig with CORE module and the error attached
        """
        return cls(
            module=BMADModule.CORE,
            error=error,
        )


# =============================================================================
# Story 2a.3 - Task 2: Source Directory Detection
# =============================================================================

# Standard source directory names to check for
SOURCE_DIRECTORIES: frozenset[str] = frozenset({"src", "lib", "app"})


def detect_source_directories(project_path: Path) -> list[DetectionSignal]:
    """Detect source directories in a project.

    Checks for standard source directories (src/, lib/, app/) and counts
    files in each directory found.

    Args:
        project_path: Path to the project root directory

    Returns:
        List of DetectionSignal indicating which source directories were found
    """
    signals: list[DetectionSignal] = []

    for dir_name in SOURCE_DIRECTORIES:
        dir_path = project_path / dir_name
        if dir_path.is_dir():
            # Count all files recursively
            file_count = sum(1 for _ in dir_path.rglob("*") if _.is_file())
            signals.append(
                DetectionSignal(
                    name=f"has_{dir_name}_directory",
                    detected=True,
                    details=f"Found {dir_name}/ directory with {file_count} files",
                )
            )

    return signals


# =============================================================================
# Story 2a.3 - Task 3: Package File Detection
# =============================================================================

# Standard package file names to check for
PACKAGE_FILES: frozenset[str] = frozenset({
    "package.json",      # Node.js/JavaScript
    "pyproject.toml",    # Python (modern)
    "Cargo.toml",        # Rust
    "go.mod",            # Go
    "pom.xml",           # Java/Maven
})


def detect_package_files(project_path: Path) -> list[DetectionSignal]:
    """Detect package/manifest files in a project.

    Checks for standard package files (package.json, pyproject.toml, etc.)
    that indicate an existing project with dependencies.

    Args:
        project_path: Path to the project root directory

    Returns:
        List of DetectionSignal indicating which package files were found
    """
    signals: list[DetectionSignal] = []

    for file_name in PACKAGE_FILES:
        file_path = project_path / file_name
        if file_path.is_file():
            # Create a sanitized signal name
            signal_name = f"has_{file_name.replace('.', '_').replace('-', '_')}"
            signals.append(
                DetectionSignal(
                    name=signal_name,
                    detected=True,
                    details=f"Found {file_name}",
                )
            )

    return signals


# =============================================================================
# Story 2a.3 - Task 4: Source File Counting
# =============================================================================

# Source file extensions to count
SOURCE_EXTENSIONS: frozenset[str] = frozenset({
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".kt", ".scala",
    ".go", ".rs", ".c", ".cpp", ".h",
    ".rb", ".php", ".swift", ".m",
})

# Directories to exclude from source file counting
EXCLUDED_DIRS: frozenset[str] = frozenset({
    "node_modules", "__pycache__", ".git", ".svn",
    "venv", ".venv", "env", ".env",
    "dist", "build", "target", "out",
    ".idea", ".vscode", ".pytest_cache",
})

# Threshold for greenfield/brownfield determination
SOURCE_FILE_THRESHOLD = 10


def count_source_files(project_path: Path) -> tuple[int, DetectionSignal]:
    """Count source files in a project, excluding standard directories.

    Recursively counts files with source code extensions, excluding
    common non-source directories like node_modules, venv, etc.

    Args:
        project_path: Path to the project root directory

    Returns:
        Tuple of (count, signal) where:
        - count: Number of source files found
        - signal: DetectionSignal with detected=True if >= 10 files (brownfield indicator)
    """
    count = 0

    def should_skip_dir(path: Path) -> bool:
        """Check if directory should be skipped."""
        return path.name in EXCLUDED_DIRS

    def count_in_dir(dir_path: Path) -> int:
        """Recursively count source files in directory."""
        total = 0
        try:
            for item in dir_path.iterdir():
                if item.is_dir():
                    if not should_skip_dir(item):
                        total += count_in_dir(item)
                elif item.is_file():
                    if item.suffix.lower() in SOURCE_EXTENSIONS:
                        total += 1
        except PermissionError:
            pass  # Skip directories we can't access
        return total

    count = count_in_dir(project_path)

    # Signal is detected=True if >= threshold (indicating brownfield)
    is_brownfield_signal = count >= SOURCE_FILE_THRESHOLD
    signal = DetectionSignal(
        name="has_many_source_files",
        detected=is_brownfield_signal,
        details=f"Found {count} source files (threshold: {SOURCE_FILE_THRESHOLD})",
    )

    return count, signal


# =============================================================================
# Story 2a.3 - Task 5 & 6: Main Project Type Detection
# =============================================================================


def detect_project_type(project_path: Path) -> ProjectTypeResult:
    """Detect whether a project is greenfield or brownfield.

    Analyzes the directory structure, package files, and source file count
    to determine if this is a new project (greenfield) or existing project
    (brownfield).

    Args:
        project_path: Path to the project root directory

    Returns:
        ProjectTypeResult with project type, detection signals, and confidence

    Raises:
        FileNotFoundError: If the path does not exist
        NotADirectoryError: If the path is not a directory
    """
    if not project_path.exists():
        raise FileNotFoundError(f"Path does not exist: {project_path}")
    if not project_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {project_path}")

    signals: list[DetectionSignal] = []

    # Check source directories
    source_dir_signals = detect_source_directories(project_path)
    signals.extend(source_dir_signals)

    # Check package files
    package_signals = detect_package_files(project_path)
    signals.extend(package_signals)

    # Count source files
    file_count, file_signal = count_source_files(project_path)
    signals.append(file_signal)

    # Determine project type based on signals
    detected_count = sum(1 for s in signals if s.detected)

    if detected_count == 0:
        # No brownfield indicators
        return ProjectTypeResult.greenfield(signals=signals, confidence=1.0)
    else:
        # Calculate confidence based on number of signals detected
        confidence = min(0.5 + (detected_count * 0.15), 1.0)
        return ProjectTypeResult.brownfield(signals=signals, confidence=confidence)


# =============================================================================
# Story 2a.6 - Task 2: YAML File Parsing
# =============================================================================


def parse_yaml_config(file_path: Path) -> WorkflowConfig:
    """Parse a YAML workflow configuration file.

    Args:
        file_path: Path to the .yaml workflow file

    Returns:
        WorkflowConfig with parsed configuration or error
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        if not content.strip():
            return WorkflowConfig.core_defaults()

        data = yaml.safe_load(content)
        if data is None:
            # File had only comments or whitespace
            return WorkflowConfig.core_defaults()

        # Extract module (default to core)
        module_str = data.get("module", "core").lower()
        try:
            module = BMADModule(module_str)
        except ValueError:
            return WorkflowConfig.from_error(
                ConfigParseError(
                    message="config_parse_error",
                    details=f"Unknown module: {module_str}",
                )
            )

        # Extract settings and thresholds
        settings = data.get("settings", {})
        thresholds = data.get("thresholds", {})

        return WorkflowConfig(
            module=module,
            settings=settings if isinstance(settings, dict) else {},
            thresholds=thresholds if isinstance(thresholds, dict) else {},
            raw_config=data,
        )

    except yaml.YAMLError as e:
        # Extract line number if available
        line_number = None
        if hasattr(e, "problem_mark") and e.problem_mark is not None:
            line_number = e.problem_mark.line + 1

        return WorkflowConfig.from_error(
            ConfigParseError(
                message="config_parse_error",
                line_number=line_number,
                details=str(e),
            )
        )
    except Exception as e:
        return WorkflowConfig.from_error(
            ConfigParseError(
                message="config_parse_error",
                details=str(e),
            )
        )


# =============================================================================
# Story 2a.6 - Task 3: Markdown Frontmatter Parsing
# =============================================================================


def extract_frontmatter(content: str) -> tuple[Optional[str], bool]:
    """Extract YAML frontmatter from Markdown content.

    Args:
        content: The full Markdown file content

    Returns:
        Tuple of (frontmatter_yaml, found) where frontmatter_yaml is the
        extracted YAML string or None, and found indicates if frontmatter
        delimiters were detected.
    """
    lines = content.split("\n")

    # Check for opening delimiter
    if not lines or not lines[0].strip() == "---":
        return None, False

    # Find closing delimiter
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            # Extract content between delimiters
            frontmatter_lines = lines[1:i]
            return "\n".join(frontmatter_lines), True

    # No closing delimiter found
    return None, True  # Frontmatter detected but unclosed


def parse_frontmatter_config(file_path: Path) -> WorkflowConfig:
    """Parse workflow configuration from Markdown frontmatter.

    Args:
        file_path: Path to the .md workflow file

    Returns:
        WorkflowConfig with parsed configuration or error
    """
    try:
        content = file_path.read_text(encoding="utf-8")

        frontmatter_yaml, found = extract_frontmatter(content)

        if not found:
            # No frontmatter at all, return core defaults
            return WorkflowConfig.core_defaults()

        if frontmatter_yaml is None:
            # Frontmatter detected but unclosed
            return WorkflowConfig.core_defaults()

        if not frontmatter_yaml.strip():
            # Empty frontmatter
            return WorkflowConfig.core_defaults()

        # Parse the extracted YAML
        data = yaml.safe_load(frontmatter_yaml)
        if data is None:
            return WorkflowConfig.core_defaults()

        # Extract module (default to core)
        module_str = data.get("module", "core").lower()
        try:
            module = BMADModule(module_str)
        except ValueError:
            return WorkflowConfig.from_error(
                ConfigParseError(
                    message="config_parse_error",
                    details=f"Unknown module: {module_str}",
                )
            )

        # Extract settings and thresholds
        settings = data.get("settings", {})
        thresholds = data.get("thresholds", {})

        return WorkflowConfig(
            module=module,
            settings=settings if isinstance(settings, dict) else {},
            thresholds=thresholds if isinstance(thresholds, dict) else {},
            raw_config=data,
        )

    except yaml.YAMLError as e:
        line_number = None
        if hasattr(e, "problem_mark") and e.problem_mark is not None:
            line_number = e.problem_mark.line + 1

        return WorkflowConfig.from_error(
            ConfigParseError(
                message="config_parse_error",
                line_number=line_number,
                details=str(e),
            )
        )
    except Exception as e:
        return WorkflowConfig.from_error(
            ConfigParseError(
                message="config_parse_error",
                details=str(e),
            )
        )


# =============================================================================
# Story 2a.6 - Task 4: Module-Specific Defaults
# =============================================================================


def get_module_defaults(module: BMADModule) -> WorkflowConfig:
    """Get the default configuration for a specific BMAD module.

    Args:
        module: The BMAD module to get defaults for

    Returns:
        WorkflowConfig with module-specific default settings and thresholds
    """
    if module == BMADModule.BMM:
        return WorkflowConfig.bmm_defaults()
    elif module == BMADModule.BMB:
        return WorkflowConfig.bmb_defaults()
    else:
        return WorkflowConfig.core_defaults()


def merge_with_defaults(config: WorkflowConfig) -> WorkflowConfig:
    """Merge a parsed configuration with module-specific defaults.

    User-provided settings and thresholds override the defaults.

    Args:
        config: The parsed WorkflowConfig to merge with defaults

    Returns:
        WorkflowConfig with defaults applied (user settings take precedence)
    """
    if config.error is not None:
        # Don't merge if there's an error
        return config

    defaults = get_module_defaults(config.module)

    # Merge settings: defaults first, then user overrides
    merged_settings = {**defaults.settings, **config.settings}

    # Merge thresholds: defaults first, then user overrides
    merged_thresholds = {**defaults.thresholds, **config.thresholds}

    return WorkflowConfig(
        module=config.module,
        settings=merged_settings,
        thresholds=merged_thresholds,
        raw_config=config.raw_config,
        error=config.error,
    )


# =============================================================================
# Story 2a.6 - Task 6: Main parse_workflow_config() Function
# =============================================================================


def parse_workflow_config(file_path: Path) -> WorkflowConfig:
    """Parse workflow configuration from a YAML or Markdown file.

    Auto-detects the file format based on extension and parses accordingly.
    Applies module-specific defaults after parsing.

    Args:
        file_path: Path to the workflow configuration file (.yaml, .yml, or .md)

    Returns:
        WorkflowConfig with parsed configuration and defaults applied
    """
    # Check if file exists
    if not file_path.exists():
        return WorkflowConfig.from_error(
            ConfigParseError(
                message="config_parse_error",
                details=f"File not found: {file_path}",
            )
        )

    # Auto-detect format based on extension
    suffix = file_path.suffix.lower()

    if suffix == ".md":
        config = parse_frontmatter_config(file_path)
    elif suffix in (".yaml", ".yml"):
        config = parse_yaml_config(file_path)
    else:
        # Try YAML parsing as fallback for unknown extensions
        config = parse_yaml_config(file_path)

    # Apply module defaults if no error
    if config.error is None:
        config = merge_with_defaults(config)

    return config
