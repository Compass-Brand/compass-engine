# BMM Validation Patterns and Verdicts

**Purpose:** Comprehensive documentation of validation workflows, verdict systems, and escalation patterns used in BMAD Method (BMM).

**Date:** 2026-01-09

---

## Executive Summary

BMM uses several distinct validation workflows, each with its own verdict system:

| Workflow | Verdicts | Escalation Trigger |
|----------|----------|-------------------|
| **code-review** | Approve / Changes Requested / Blocked | Blocked = fundamental issues |
| **check-implementation-readiness** | READY / NEEDS WORK / NOT READY | NOT READY = critical blockers |
| **testarch-trace** | PASS / CONCERNS / FAIL / WAIVED | FAIL = P0 gaps; WAIVED = business exception |
| **testarch-nfr** | PASS / CONCERNS / FAIL | FAIL = NFR threshold breach |
| **testarch-test-review** | Quality Score 0-100 + Grade (A+/A/B/C/F) | Score < 60 = Critical Issues |
| **quick-dev adversarial** | Findings (Critical/High/Medium/Low) | Zero findings = suspicious |

---

## 1. Code Review Workflow

**Location:** `_bmad/bmm/workflows/4-implementation/code-review/`

### Workflow Structure

The code-review workflow uses a **checklist-based approach** with 22 validation items (NOT an adversarial "find minimum issues" approach, despite the workflow.yaml description suggesting otherwise).

**Files:**
- `workflow.yaml` - Workflow configuration
- `checklist.md` - 22-item validation checklist
- `instructions.xml` - Step-by-step execution instructions

### Checklist Items (22 total)

1. Story file loaded from story_path
2. Story Status verified as reviewable (review)
3. Epic and Story IDs resolved
4. Story Context located or warning recorded
5. Epic Tech Spec located or warning recorded
6. Architecture/standards docs loaded (as available)
7. Tech stack detected and documented
8. MCP doc search performed (or web fallback) and references captured
9. Acceptance Criteria cross-checked against implementation
10. File List reviewed and validated for completeness
11. Tests identified and mapped to ACs; gaps noted
12. Code quality review performed on changed files
13. Security review performed on changed files and dependencies
14. **Outcome decided (Approve/Changes Requested/Blocked)**
15. Review notes appended under "Senior Developer Review (AI)"
16. Change Log updated with review entry
17. Status updated according to settings (if enabled)
18. Sprint status synced (if sprint tracking enabled)
19. Story saved successfully

### Verdict System

| Verdict | Meaning | When Applied |
|---------|---------|--------------|
| **Approve** | Story meets all standards | All HIGH and MEDIUM issues fixed AND all ACs implemented |
| **Changes Requested** | Needs fixes before approval | HIGH or MEDIUM issues remain OR ACs not fully implemented |
| **Blocked** | Fundamental issues prevent progress | Critical structural problems, missing requirements, or security vulnerabilities |

### Finding Severity Levels

| Severity | Icon | Description | Examples |
|----------|------|-------------|----------|
| **CRITICAL** | Red | Tasks marked [x] but not implemented; ACs missing; Security vulnerabilities | False completion claims, unauthorized access |
| **HIGH** | Yellow | Story claims files changed but no git evidence; Performance problems | False documentation, N+1 queries |
| **MEDIUM** | Yellow | Files changed but not documented; Uncommitted changes; Poor test coverage | Transparency issues, test gaps |
| **LOW** | Green | Code style; Documentation gaps; Git commit message quality | Minor improvements |

### Git Integration

The workflow cross-references:
1. `git status --porcelain` - Uncommitted changes
2. `git diff --name-only` - Modified files
3. `git diff --cached --name-only` - Staged files

Discrepancies between story File List and git reality are flagged as findings.

### Outcome Decision Flow

```
IF all HIGH and MEDIUM issues fixed AND all ACs implemented:
  → Verdict: Approve (status = "done")
ELSE IF HIGH or MEDIUM issues remain OR ACs not fully implemented:
  → Verdict: Changes Requested (status = "in-progress")
ELSE IF fundamental structural issues:
  → Verdict: Blocked
```

---

## 2. Check-Implementation-Readiness Workflow

**Location:** `_bmad/bmm/workflows/3-solutioning/check-implementation-readiness/`

### Workflow Structure

A 6-step workflow validating PRD, Architecture, and Epics/Stories alignment before Phase 4 implementation.

**Steps:**
1. **step-01-document-discovery.md** - Discover and inventory all project documents
2. **step-02-prd-analysis.md** - Extract all FRs and NFRs from PRD
3. **step-03-epic-coverage-validation.md** - Validate FR coverage in epics
4. **step-04-ux-alignment.md** - Check UX document alignment
5. **step-05-epic-quality-review.md** - Validate epics against best practices
6. **step-06-final-assessment.md** - Compile final assessment and recommendations

### Verdict System

| Verdict | Meaning | Criteria |
|---------|---------|----------|
| **READY** | Implementation can proceed | All documents complete, aligned, no critical gaps |
| **NEEDS WORK** | Fixable issues exist | Gaps or misalignments that can be addressed |
| **NOT READY** | Critical blockers | Missing required documents, fundamental misalignments, broken dependencies |

### Validation Categories

#### Document Discovery (Step 1)
- **CRITICAL ISSUE:** Duplicate document formats (whole + sharded)
- **WARNING:** Required document not found

#### PRD Analysis (Step 2)
- Extract ALL Functional Requirements (FRs)
- Extract ALL Non-Functional Requirements (NFRs)
- Document completeness assessment

#### Epic Coverage (Step 3)
Coverage status per FR:
- **Covered** - FR mapped to specific Epic/Story
- **MISSING** - FR not covered in any epic

Coverage matrix output:
```
| FR Number | PRD Requirement | Epic Coverage | Status |
|-----------|-----------------|---------------|--------|
| FR1       | [PRD text]      | Epic X Story Y| Covered|
| FR2       | [PRD text]      | NOT FOUND     | MISSING|
```

#### UX Alignment (Step 4)
- UX ↔ PRD alignment check
- UX ↔ Architecture alignment check
- Warning if UX implied but missing

#### Epic Quality Review (Step 5)

**Critical Violations (Red):**
- Technical epics with no user value
- Forward dependencies breaking independence
- Epic-sized stories that cannot be completed

**Major Issues (Orange):**
- Vague acceptance criteria
- Stories requiring future stories
- Database creation violations

**Minor Concerns (Yellow):**
- Formatting inconsistencies
- Minor structure deviations
- Documentation gaps

### Best Practices Enforced

Per-epic verification:
- [ ] Epic delivers user value (NOT technical milestones)
- [ ] Epic can function independently
- [ ] Stories appropriately sized
- [ ] No forward dependencies
- [ ] Database tables created when needed (not upfront)
- [ ] Clear acceptance criteria
- [ ] Traceability to FRs maintained

---

## 3. Testarch-Trace Workflow (Traceability & Quality Gate)

**Location:** `_bmad/bmm/workflows/testarch/trace/`

### Workflow Structure

A **two-phase workflow**:
- **Phase 1:** Requirements Traceability Matrix
- **Phase 2:** Quality Gate Decision

### Coverage Classifications (Phase 1)

| Status | Meaning | Icon |
|--------|---------|------|
| **FULL** | All scenarios validated at appropriate level(s) | Checkmark |
| **PARTIAL** | Some coverage but missing edge cases or levels | Warning |
| **NONE** | No test coverage at any level | X |
| **UNIT-ONLY** | Only unit tests (missing integration/E2E) | Warning |
| **INTEGRATION-ONLY** | Only API/Component tests (missing unit) | Warning |

### Gap Severity Levels

| Severity | Priority | Action |
|----------|----------|--------|
| **CRITICAL** | P0 criteria without FULL coverage | Blocks release |
| **HIGH** | P1 criteria without FULL coverage | PR blocker |
| **MEDIUM** | P2 criteria without FULL coverage | Nightly test gap |
| **LOW** | P3 criteria without FULL coverage | Acceptable gap |

### Verdict System (Phase 2)

| Verdict | Meaning | Criteria |
|---------|---------|----------|
| **PASS** | All quality criteria met | P0=100%, P1>=90%, Overall>=80%, No security issues |
| **CONCERNS** | Minor gaps, non-blocking | P1 80-89%, some non-critical NFRs failing, minor quality issues |
| **FAIL** | Critical gaps, deployment blocked | P0<100%, P0 tests failing, P1<80%, critical NFRs failing |
| **WAIVED** | Business-approved exception | Would be FAIL, but stakeholder approved with mitigation |

### Deterministic Decision Rules

**PASS if ALL true:**
- P0 coverage >= 100%
- P1 coverage >= 90%
- Overall coverage >= 80%
- P0 test pass rate = 100%
- P1 test pass rate >= 95%
- Overall test pass rate >= 90%
- Critical NFRs passed
- No unresolved security issues
- No test quality red flags

**CONCERNS if ANY true:**
- P1 coverage 80-89%
- P1 test pass rate 90-94%
- Overall pass rate 85-89%
- P2 coverage < 50%
- Some non-critical NFRs failing
- Minor test quality concerns

**FAIL if ANY true:**
- P0 coverage < 100%
- P0 test pass rate < 100%
- P1 coverage < 80%
- P1 test pass rate < 90%
- Overall coverage < 80%
- Overall pass rate < 85%
- Critical NFRs failing
- Unresolved security issues
- Major test quality issues

**WAIVED only if:**
- allow_waivers: true
- Decision would be FAIL
- Business stakeholder approved waiver
- Waiver documented with:
  - Justification
  - Approver name and date
  - Mitigation plan
  - Evidence link

### Waiver Restrictions

Waivers **do NOT apply** to:
- P0 gaps (always blocking)
- Critical security issues (always blocking)
- Critical NFR failures (data integrity, etc.)

---

## 4. Testarch-NFR Workflow (Non-Functional Requirements Assessment)

**Location:** `_bmad/bmm/workflows/testarch/nfr-assess/`

### NFR Categories

| Category | Criteria | Default Thresholds |
|----------|----------|-------------------|
| **Performance** | Response time, throughput, resource usage | p95 < 500ms, 100 RPS, CPU < 70% |
| **Security** | Auth, authorization, data protection, vulnerabilities | Score >= 85, 0 critical vulns |
| **Reliability** | Uptime, error handling, fault tolerance | 99.9% uptime, < 0.1% errors |
| **Maintainability** | Code quality, test coverage, documentation | 80% coverage, 85+ quality score |

### Verdict System

| Verdict | Criteria | Icon |
|---------|----------|------|
| **PASS** | Evidence exists AND meets threshold | Checkmark |
| **CONCERNS** | Threshold UNKNOWN, evidence MISSING/INCOMPLETE, or close to threshold (within 10%) | Warning |
| **FAIL** | Evidence exists BUT does not meet threshold | X |

### Key Principle: Never Guess Thresholds

If a threshold is unknown, the NFR is marked **CONCERNS** (not assumed to pass or fail).

### Severity Classification

| Severity | Category Examples | Impact |
|----------|------------------|--------|
| **CRITICAL** | Security failures, reliability failures | Affects users immediately |
| **HIGH** | Performance failures, maintainability failures | Affects users soon |
| **MEDIUM** | Concerns without failures | May affect users eventually |
| **LOW** | Missing evidence for non-critical NFRs | Minimal impact |

---

## 5. Testarch-Test-Review Workflow (Test Quality Review)

**Location:** `_bmad/bmm/workflows/testarch/test-review/`

### Quality Score System

```
Starting Score: 100

Critical Violations: -10 points each
High Violations: -5 points each
Medium Violations: -2 points each
Low Violations: -1 point each

Bonus Points:
+ Excellent BDD structure: +5
+ Comprehensive fixtures: +5
+ Comprehensive data factories: +5
+ Network-first pattern: +5
+ Perfect isolation: +5
+ All test IDs present: +5

Quality Score: max(0, min(100, Starting Score - Violations + Bonus))
```

### Quality Grades

| Score Range | Grade | Meaning |
|-------------|-------|---------|
| 90-100 | A+ | Excellent |
| 80-89 | A | Good |
| 70-79 | B | Acceptable |
| 60-69 | C | Needs Improvement |
| < 60 | F | Critical Issues |

### Recommendation Outcomes

| Recommendation | Criteria |
|----------------|----------|
| **Approve** | Score 80+, no Critical issues |
| **Approve with comments** | Score 70-79 OR has High issues |
| **Request changes** | Score < 70 OR has Critical issues |

### Quality Criteria (13 checks)

| Criterion | PASS | WARN | FAIL |
|-----------|------|------|------|
| BDD Format | Given-When-Then present | Some structure | No structure |
| Test IDs | All tests have IDs | Some missing | No IDs |
| Priority Markers | All classified | Some missing | No classification |
| Hard Waits | No hard waits | Some justified | Hard waits present |
| Determinism | No conditionals/random | Some justified | Conditionals/random |
| Isolation | Clean up, no shared state | Some gaps | Shared state |
| Fixture Patterns | Pure fn -> Fixture | Some fixtures | No fixtures |
| Data Factories | Factory functions | Some factories | Hardcoded data |
| Network-First | Intercept before navigate | Some correct | Race conditions |
| Assertions | Explicit assertions | Some implicit | Missing assertions |
| Test Length | <= 300 lines | 301-500 lines | > 500 lines |
| Test Duration | <= 1.5 min | 1.5-3 min | > 3 min |
| Flakiness Patterns | No flaky patterns | Some potential | Multiple patterns |

---

## 6. Quick-Dev Adversarial Review

**Location:** `_bmad/bmm/workflows/bmad-quick-flow/quick-dev/steps/step-05-adversarial-review.md`

### Finding Severity Levels

| Severity | Description |
|----------|-------------|
| **Critical** | Security vulnerabilities, data loss risks, breaking changes |
| **High** | Performance issues, missing error handling, logic errors |
| **Medium** | Code quality issues, missing tests, documentation gaps |
| **Low** | Style issues, minor optimizations, suggestions |

### Finding Validity

| Validity | Meaning |
|----------|---------|
| **Real** | Confirmed issue that needs addressing |
| **Noise** | False positive, not actually an issue |
| **Undecided** | Requires further investigation |

### Key Rule: Zero Findings = Suspicious

If the adversarial review returns zero findings, **HALT** - this is suspicious and requires:
1. Re-analysis
2. User guidance request

### Processing Flow

1. Construct diff from baseline_commit
2. Invoke adversarial review task
3. Capture findings
4. **If zero findings: HALT**
5. Evaluate severity and validity
6. Order by severity
7. Number findings (F1, F2, F3, etc.)
8. Present as TODO list or table

---

## 7. Summary: All BMM Verdict Systems

### Outcome-Based Verdicts

| Workflow | Outcomes | Blocking Outcome |
|----------|----------|------------------|
| code-review | Approve / Changes Requested / Blocked | Blocked |
| check-implementation-readiness | READY / NEEDS WORK / NOT READY | NOT READY |
| testarch-trace | PASS / CONCERNS / FAIL / WAIVED | FAIL |
| testarch-nfr | PASS / CONCERNS / FAIL | FAIL |

### Score-Based Verdicts

| Workflow | Scoring | Critical Threshold |
|----------|---------|-------------------|
| testarch-test-review | 0-100 score, A+/A/B/C/F grade | Score < 60 = F |

### Finding-Based Verdicts

| Workflow | Finding Types | Suspicious Condition |
|----------|--------------|---------------------|
| quick-dev adversarial | Critical/High/Medium/Low | Zero findings |

---

## 8. Escalation Patterns

### When to Escalate to Human

| Condition | Escalation Path |
|-----------|-----------------|
| testarch-trace FAIL with P0 gaps | Block deployment, fix critical issues |
| testarch-nfr CRITICAL severity | Block release until resolved |
| code-review Blocked | Fundamental issues require human decision |
| check-implementation-readiness NOT READY | Critical blockers need human resolution |
| quick-dev zero findings | Suspicious - request user guidance |
| testarch-trace requires waiver | Business stakeholder approval needed |

### Escalation to Party Mode (BMAD Core)

Per the BMAD Automation Design, party mode auto-triggers for:
1. **Deadlock breaking** - Validation stalled (same issues repeating) + attempts >= 2
2. **Low confidence consultation** - AI confidence < 60% on decision (tier 2+)
3. **Mandatory pre-final review** - Required before final approval (tier 3-4)

---

## 9. Integration with Sprint Status

Several workflows update `sprint-status.yaml`:

| Workflow | Status Updates |
|----------|---------------|
| code-review | Updates story status (done/in-progress) |
| dev-story | Updates task completion |
| sprint-planning | Generates initial status file |
| sprint-status | Summarizes and routes |

Status values:
- `pending` - Not started
- `in-progress` - Work underway
- `review` - Ready for code review
- `done` - Completed

---

## 10. Key Observations

### Checklist vs. Adversarial

**code-review** is checklist-based despite workflow.yaml description mentioning "adversarial" and "find 3-10 issues". The actual implementation follows a structured checklist with Approve/Changes/Blocked outcomes.

**quick-dev adversarial** is truly adversarial - it expects findings and treats zero findings as suspicious.

### Deterministic vs. Judgment

**testarch-trace** and **testarch-nfr** use deterministic rules (specific thresholds trigger specific verdicts).

**check-implementation-readiness** uses more judgment-based assessment (evaluating document quality, alignment, best practices).

### Waiver System

Only **testarch-trace** has a formal waiver system (WAIVED verdict) with:
- Required approver
- Expiry date
- Remediation plan
- Evidence links

---

## References

- Memory: "BMAD Code Review Is Checklist-Based Not Adversarial" (ID: 29)
- Memory: "BMAD Automation Design v5 Complete" (ID: 27)
- Memory: "BMAD Automation: Validation Loop Specification" (ID: 23)
