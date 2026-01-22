# BMAD Validation Rules

This document defines all validation rules for BMAD components. Rules are organized by component type and severity level.

---

## Rule ID Format

- **AGT-###** - Agent validation rules
- **WFL-###** - Workflow validation rules
- **MOD-###** - Module validation rules

Numbering convention:
- **001-099** - Structural requirements
- **101-199** - Content requirements
- **201-299** - Format-specific requirements (e.g., YAML)

---

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **CRITICAL** | Blocks all operations | Must fix before proceeding |
| **HIGH** | Major issue | Should fix before proceeding |
| **MEDIUM** | Quality concern | Warning, can proceed |
| **LOW** | Minor issue | Informational |

---

## 1. Agent Validation Rules (AGT-*)

### 1.1 Structural Requirements

| Rule ID | Rule | Severity | Check Method |
|---------|------|----------|--------------|
| AGT-001 | File must be markdown (`.md` extension) | CRITICAL | Extension check |
| AGT-002 | Optional YAML frontmatter must be valid YAML | HIGH | YAML parse test |
| AGT-003 | Must have exactly one H1 heading (`# Agent Name`) | CRITICAL | Regex match |
| AGT-004 | H1 must appear before any other content (after frontmatter) | HIGH | Line position check |
| AGT-005 | Must contain persona/role section (H2 or H3) | HIGH | Section search |
| AGT-006 | Must contain capabilities section | MEDIUM | Section search |
| AGT-007 | Tool references must be valid tool names | MEDIUM | Tool registry lookup |
| AGT-008 | Internal links must resolve | LOW | Link resolution |

### 1.2 Content Requirements

| Rule ID | Rule | Severity | Check Method |
|---------|------|----------|--------------|
| AGT-101 | Persona must be substantive (>50 characters) | MEDIUM | Length check |
| AGT-102 | Capabilities must be listed (bullet or numbered) | MEDIUM | Format check |
| AGT-103 | No duplicate section headings at same level | LOW | Heading analysis |
| AGT-104 | No empty sections | LOW | Content check |

### 1.3 Validation Regex Patterns

```regex
# H1 Heading (exactly one # followed by space and text)
H1_HEADING: ^# (?!#).+$

# H2 Heading
H2_HEADING: ^## (?!#).+$

# YAML Frontmatter block
YAML_FRONTMATTER: ^---\n[\s\S]*?\n---

# Tool references (MCP tools and built-in tools)
TOOL_REFERENCE: \b(mcp__\w+__\w+|Read|Write|Edit|Bash|Glob|Grep)\b

# Internal links (non-http links)
INTERNAL_LINK: \[.*?\]\(((?!https?://)[^)]+)\)
```

---

## 2. Workflow Validation Rules (WFL-*)

### 2.1 Directory Structure Requirements

| Rule ID | Rule | Severity | Check Method |
|---------|------|----------|--------------|
| WFL-001 | Must have `workflow.md` OR `workflow.yaml` at root | CRITICAL | File exists |
| WFL-002 | If `steps/` exists, must contain step files | HIGH | Directory contents |
| WFL-003 | Step files must be numbered (`step-NN-name.md`) | MEDIUM | Naming pattern |
| WFL-004 | Step numbers must be sequential (no gaps >1) | LOW | Number sequence |
| WFL-005 | If `data/` exists, referenced files must exist | MEDIUM | File references |

### 2.2 Workflow.md Requirements

| Rule ID | Rule | Severity | Check Method |
|---------|------|----------|--------------|
| WFL-101 | Must have H1 heading | CRITICAL | Heading check |
| WFL-102 | Must describe workflow purpose | HIGH | Content presence |
| WFL-103 | Step references must match actual step files | HIGH | Cross-reference |
| WFL-104 | Internal anchors must resolve | MEDIUM | Anchor resolution |

### 2.3 Workflow.yaml Requirements

| Rule ID | Rule | Severity | Check Method |
|---------|------|----------|--------------|
| WFL-201 | Must be valid YAML | CRITICAL | YAML parse |
| WFL-202 | Must have `name` field | CRITICAL | Field presence |
| WFL-203 | Must have `description` field | HIGH | Field presence |
| WFL-204 | `steps` array elements must reference existing files | HIGH | File resolution |
| WFL-205 | `tools` array must contain valid tool names | MEDIUM | Tool registry |

### 2.4 Step File Naming Pattern

```regex
# Valid step file names
STEP_FILE_PATTERN: ^step-(\d{2}[a-z]?\d?)-([a-z0-9-]+)\.md$

# Examples:
# step-01-init.md       -> Valid (01, init)
# step-01b-continue.md  -> Valid (01b, continue)
# step-04a1-agent-simple.md -> Valid (04a1, agent-simple)
# step-4-init.md        -> Invalid (single digit)
# step_01_init.md       -> Invalid (underscores)
```

---

## 3. Module Validation Rules (MOD-*)

### 3.1 Directory Structure Requirements

| Rule ID | Rule | Severity | Check Method |
|---------|------|----------|--------------|
| MOD-001 | Must have `module.yaml` at root | CRITICAL | File exists |
| MOD-002 | If `agents/` exists, must contain valid agent files | HIGH | Agent validation |
| MOD-003 | If `workflows/` exists, must contain valid workflow dirs | HIGH | Workflow validation |
| MOD-004 | README.md recommended but not required | LOW | File exists |

### 3.2 Module.yaml Requirements

| Rule ID | Rule | Severity | Check Method |
|---------|------|----------|--------------|
| MOD-101 | Must be valid YAML | CRITICAL | YAML parse |
| MOD-102 | Must have `name` field | CRITICAL | Field presence |
| MOD-103 | Must have `version` field (semver format) | HIGH | Semver regex |
| MOD-104 | Must have `description` field | HIGH | Field presence |
| MOD-105 | `agents` array must match actual agent files | HIGH | Cross-reference |
| MOD-106 | `workflows` array must match actual workflow dirs | HIGH | Cross-reference |
| MOD-107 | `dependencies` must reference valid modules | MEDIUM | Module lookup |

### 3.3 Semver Validation Pattern

```regex
# Semantic versioning pattern
SEMVER_PATTERN: ^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$

# Examples:
# 1.0.0       -> Valid
# 1.2.3       -> Valid
# 1.0.0-beta  -> Valid
# 1.0.0-rc.1  -> Valid
# v1.0.0      -> Invalid (no 'v' prefix)
# 1.0         -> Invalid (missing patch)
```

---

## 4. Compliance Check Algorithm

```
BMAD COMPLIANCE CHECK
=====================

INPUT:  Path to component (agent file, workflow dir, or module dir)
OUTPUT: ComplianceResult { passed: bool, issues: Issue[], severity: string }

STEP 1: Determine Component Type
  IF path ends with .md AND parent is agents/  -> AGENT
  IF path contains workflow.md or workflow.yaml -> WORKFLOW
  IF path contains module.yaml                  -> MODULE
  ELSE -> ERROR: "Unknown component type"

STEP 2: Load Applicable Rules
  agent    -> AGT-* rules
  workflow -> WFL-* rules
  module   -> MOD-* rules (includes recursive check of agents/workflows)

STEP 3: Execute Each Rule
  FOR each rule in applicable_rules:
    result = execute_check(rule, component)
    IF result.failed:
      issues.append(Issue(rule.id, rule.severity, result.message))

STEP 4: Calculate Overall Result
  IF any CRITICAL issue -> passed = false, severity = "CRITICAL"
  ELIF any HIGH issue   -> passed = false, severity = "HIGH"
  ELIF any MEDIUM issue -> passed = true (warn), severity = "MEDIUM"
  ELSE                  -> passed = true, severity = "CLEAN"

RETURN ComplianceResult(passed, issues, severity)
```

---

## 5. Compliance Check Output Format

```
BMAD Compliance Check: {component_name}
================================================================

Status: {PASSED|FAILED} ({critical_count} CRITICAL, {high_count} HIGH, {medium_count} MEDIUM, {low_count} LOW)

CRITICAL Issues:
  [{rule_id}] {rule_description}
              Found: {actual_value}
              Fix: {suggested_fix}

HIGH Issues:
  [{rule_id}] {rule_description}
              Found: {actual_value}
              Fix: {suggested_fix}

MEDIUM Issues (Warnings):
  [{rule_id}] {rule_description}
              Found: {actual_value}
              Fix: {suggested_fix}

LOW Issues (Info):
  [{rule_id}] {rule_description}
              Found: {actual_value}
              Fix: {suggested_fix}

----------------------------------------------------------------
Recommendation: {action_recommendation}
```

---

## 6. Example Validation Output

```
BMAD Compliance Check: analyst.md
================================================================

Status: FAILED (2 CRITICAL, 1 HIGH, 0 MEDIUM, 0 LOW)

CRITICAL Issues:
  [AGT-001] File must be markdown extension
            Found: analyst.txt
            Fix: Rename to analyst.md

  [AGT-003] Must have exactly one H1 heading
            Found: 0 H1 headings
            Fix: Add "# Agent Name" at top of file

HIGH Issues:
  [AGT-005] Must contain persona/role section
            Found: No section matching /persona|role/i
            Fix: Add "## Persona" or "## Role" section

----------------------------------------------------------------
Recommendation: Fix CRITICAL issues before proceeding with edit.
```
