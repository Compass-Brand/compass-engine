# Extension Modules Reference

Compass BMAD ships four extension modules that add specialized capabilities to the core workflow. Each module is **conditional** -- it activates only when project characteristics warrant it or when explicitly chosen. None of them replace required core gates; they complement the main progression chain.

This page covers integration points and activation guidance. For detailed skill behavior, consult the individual SKILL.md files referenced in each section.

---

## TEA (Test Engineering and Automation)

### What TEA Is

TEA is a risk-based test strategy and automation framework. It provides structured workflows for test design, acceptance-test-driven development, test automation, CI/CD alignment, non-functional-requirements assessment, traceability, and test review. TEA scales testing depth with risk and impact rather than applying uniform coverage everywhere.

### Key Agent

**Murat** (`bmad-agent-tea`) -- Test Architect. Specializes in risk-based testing, fixture architecture, ATDD, API and UI automation, CI/CD governance, and scalable quality gates. Supports pytest, JUnit, Go test, xUnit, RSpec, Playwright, Cypress, and major CI platforms (GitHub Actions, GitLab CI, Jenkins, Azure DevOps, Harness).

### Workflows

| Code | Workflow | Command | Purpose |
|------|----------|---------|---------|
| TD | Test Design | `/bmad-tea-testarch-test-design` | Risk assessment and coverage strategy (system or epic scope) |
| TF | Test Framework | `/bmad-tea-testarch-framework` | Initialize production-ready test framework architecture |
| CI | CI/CD Alignment | `/bmad-tea-testarch-ci` | Recommend and scaffold CI/CD quality pipeline |
| AT | ATDD | `/bmad-tea-testarch-atdd` | Generate failing acceptance tests and implementation checklist before development |
| TA | Test Automation | `/bmad-tea-testarch-automate` | Generate prioritized API/E2E tests, fixtures, and DoD summary for a story |
| RV | Test Review | `/bmad-tea-testarch-test-review` | Quality check against written tests using knowledge base and best practices |
| NR | NFR Assessment | `/bmad-tea-testarch-nfr` | Assess non-functional requirements and recommend actions |
| TR | Traceability | `/bmad-tea-testarch-trace` | Map requirements to tests (Phase 1) and make quality gate decision (Phase 2) |
| TMT | Teach Me Testing | `/bmad-tea-teach-me-testing` | Interactive 7-session learning companion for testing fundamentals |

All TEA commands also accept a colon form (e.g., `/bmad:tea:test-design`). See the command compatibility table in `BMAD-workflow.md` for the full mapping.

### Dual Placement

Test Design appears **twice** in the workflow by design:

1. **Solutioning (Phase 7, step 4)** -- system-level mode. Produces the overall test strategy after the initial architecture draft, before epics and stories are created.
2. **Implementation (Phase 8B, step 2)** -- epic-level mode. Refines test design for each epic before the story loop begins.

### When to Activate TEA vs Built-In Code Review

TEA is **optional** at every insertion point. Use TEA when:

- The project has meaningful risk that benefits from structured test strategy beyond ad-hoc unit tests.
- You need traceable coverage evidence for compliance, audit, or release gates.
- The project spans multiple test levels (unit, integration, API, E2E) requiring coordinated automation.
- Non-functional requirements (performance, security, reliability) need formal assessment.

Built-in code review (`/bmad-bmm-code-review`) remains a separate lane. TEA's `test-review` complements but does **not** replace code review.

### TEA Insertion and Replacement Rules

1. TEA does not replace required framework control artifacts or required BMM progression gates.
2. `test-review` does not replace `code-review`.
3. `testarch-automate` is the preferred default post-dev automation lane; `bmm-qa-automate` is a secondary expansion lane.
4. `nfr-assess` complements gate evidence; it does not replace traceability gate decisions.

---

## CIS (Creative Intelligence Suite)

### What CIS Provides

CIS brings innovation strategy, design thinking, and systematic problem-solving into the BMAD workflow. It ensures that analysis phases include structured creative and strategic disciplines rather than relying on ad-hoc ideation.

### Key Agents

| Agent | Persona | Skill | Focus |
|-------|---------|-------|-------|
| **Victor** | Innovation Strategist | `bmad-agent-innovation-strategist` | Disruption opportunities and business model innovation (Jobs-to-be-Done, Blue Ocean Strategy) |
| **Maya** | Design Thinking Coach | `bmad-agent-design-thinking-coach` | Human-centered design, empathy mapping, prototyping, and user insights |
| **Dr. Quinn** | Creative Problem Solver | `bmad-agent-creative-problem-solver` | Systematic problem-solving (TRIZ, Theory of Constraints, Systems Thinking) |

### Workflows

| Code | Workflow | Command | Purpose |
|------|----------|---------|---------|
| IS | Innovation Strategy | `/bmad-cis-innovation-strategy` | Identify disruption opportunities and architect business model innovation |
| DT | Opportunity Framing | `/bmad-cis-design-thinking` | Guide human-centered design process using empathy-driven methodologies |
| PS | Problem Solving | `/bmad-cis-problem-solving` | Apply systematic problem-solving methodologies to complex challenges |

### Integration as Required Analysis Steps

Innovation Strategy and Opportunity Framing are **required** steps in the analysis phases:

- **High-Level Analysis (Phase 2, steps 5-6)** -- run at project level to inform the product brief.
- **Detailed Analysis (Phase 5, steps 6-7)** -- run scoped to the active roadmap slice.

Both enrich analysis and feed the brief; they do **not** replace the Product Brief step.

### Problem Solving as an Anytime Lane

Problem Solving is classified as an **anytime** lane. It should not be forced into every default run. Use it when encountering complex challenges, blockers, or system-level problems that benefit from structured methodologies (TRIZ, Theory of Constraints, root-cause analysis).

### Upstream vs Compass Customization

CIS agents and workflows are Compass customizations. The upstream BMAD-METHOD does not include CIS. Compass adds Victor, Maya, and Dr. Quinn as domain-specific personas that wrap structured innovation and design-thinking methodologies into BMAD-compatible workflow steps.

---

## WDS (Whiteport Design Studio)

### What WDS Is

WDS is a design-to-code pipeline for UX-heavy projects. It provides a structured handoff lane between planning (PRD) and solutioning (architecture), turning validated requirements into scenario-driven conceptual specifications and implementation-ready design-delivery packages.

### Sub-Workflows

| Step | Workflow | Command | Agent | Purpose |
|------|----------|---------|-------|---------|
| 1 | Trigger Mapping | `/bmad-wds-trigger-mapping` | Saga (WDS Analyst) | Connect business goals, personas, and driving forces for the active roadmap slice |
| 2 | Outline Scenarios | `/bmad-wds-outline-scenarios` | Saga (WDS Analyst) | Transform Trigger Maps into UX scenario outlines |
| 3 | Conceptual Specifications | `/bmad-wds-conceptual-specs` | Freya (WDS Designer) | Create implementation-ready page and flow specifications |
| 4 | Design Delivery | `/bmad-wds-design-delivery` | Freya (WDS Designer) | Package approved specs into delivery-ready handoff artifacts |

### Key Agents

| Agent | Persona | Skill | Focus |
|-------|---------|-------|-------|
| **Saga** | WDS Analyst | `bmad-agent-wds-analyst` | Strategic bridge from validated requirements into trigger mapping and scenario-ready planning artifacts |
| **Freya** | WDS Designer | `bmad-agent-wds-designer` | Implementation-ready conceptual specifications and design-delivery packages |

### Workflow Placement

WDS sits in **Phase 6 (Planning and Experience Design)**, after PRD creation and validation but before architecture:

1. Create PRD (required)
2. Validate PRD (required)
3. Edit PRD (conditional)
4. **Trigger Mapping** (conditional -- WDS)
5. **Outline Scenarios** (conditional -- WDS)
6. Create UX Design (conditional)
7. **Conceptual Specifications** (conditional -- WDS)
8. **Design Delivery** (conditional -- WDS)

### When to Activate

Activate the WDS lane when workflows, user journeys, UX complexity, or behavior design matter for the active slice. WDS is most valuable for projects with:

- Multi-step user flows that need scenario-level specification before development.
- Complex UX patterns requiring structured design handoff.
- Teams that need artifact continuity from business goals through to implementation specs.

### What WDS Does NOT Replace

- WDS does not replace `Create PRD` or `Create UX Design`. It deepens the handoff lane between planning and solutioning.
- If WDS exposes requirement gaps, route back to `Edit PRD` before proceeding to architecture.

---

## CYBERSEC

### What CYBERSEC Provides

CYBERSEC adds threat modeling, security architecture review, and conditional secure gates to the BMAD workflow. It ensures security is evaluated against real architecture evidence rather than hypothetical checklists.

### Key Agents

| Agent | Persona | Skill | Focus |
|-------|---------|-------|-------|
| **Cipher** | Threat Analyst | `bmad-agent-threat-analyst` | STRIDE-based threat modeling against real architecture, data flows, and trust boundaries |
| **Bastion** | Security Architect | `bmad-agent-security-architect` | Defense-in-depth, zero-trust, control assessment, and secure gate evaluation |

### Workflows

| Code | Workflow | Command | Purpose |
|------|----------|---------|---------|
| TH | Threat Modeling | `/bmad-cybersec-threat-modeling` | Run STRIDE against current architecture and capture mitigations |
| SAR | Security Architecture Review | `/bmad-cybersec-security-architecture-review` | Assess controls, attack surface, and zero-trust gaps |
| SG | Secure Gates | `/bmad-cybersec-secure-gates` | Apply conditional readiness or release security gate using current evidence |

### Compass-Only Extension

CYBERSEC is a **Compass-only** extension. It does not exist in the upstream BMAD-METHOD. Cipher and Bastion are Compass-specific agents that wrap STRIDE threat modeling and security architecture review into conditional BMAD workflow steps.

### When CYBERSEC Activates

CYBERSEC activates by **heuristic or explicit choice**. The heuristic gives extra weight to projects with:

- Legacy authentication or authorization systems.
- Significant data flows or sensitive data handling.
- Inherited attack surface from existing systems.
- Regulated work requiring compliance evidence.

Security remains conditional, not mandatory for every project.

### Dual Gate Design

Secure Gates appears **twice** in the workflow by design:

1. **Secure Readiness Gate (Phase 7, step 8)** -- evaluates security posture before implementation begins. Outputs land in `current/testing/gates/draft/security/` while pending, then `current/testing/gates/security/readiness/` once accepted.
2. **Secure Release Gate (Phase 9, step 4)** -- evaluates security posture before release. Outputs land in `current/testing/gates/security/release/`.

Both gates are conditional -- they run only when the security lane is active for the current phase.

### Ordering Rules

- Threat Modeling and Security Architecture Review run **after** an initial architecture draft, not before architecture exists.
- The security lane does not replace `create-architecture` or `check-implementation-readiness`; it adds conditional risk and gate checks around them.
- Secure Readiness Gate and Secure Release Gate are conditional gates, not default gates for every project.

---

## Activation Decision Guide

Use this table to decide which extension modules to activate for a given project or phase.

| Module | Activate When | Skip When |
|--------|---------------|-----------|
| **TEA** | Project needs structured test strategy, traceable coverage, multi-level automation, or NFR assessment | Simple projects where built-in TDD and code review provide sufficient quality assurance |
| **CIS** | Innovation Strategy and Opportunity Framing are required analysis steps (always run); Problem Solving is anytime as needed | Problem Solving should not be forced into every run |
| **WDS** | UX complexity, multi-step user flows, behavior design, or scenario-level specification matter | API-only services, CLI tools, or projects with no user-facing interface |
| **CYBERSEC** | Legacy auth, sensitive data flows, inherited attack surface, regulated work, or explicit security requirements | Low-risk internal tools with no sensitive data or external exposure |

---

## Related Documentation

- [BMAD Overview](bmad-overview.md) -- core BMAD concepts and workflow summary
- [Custom Modules](custom-modules.md) -- how Compass extends BMAD with custom modules
- `src/bmad/BMAD-workflow.md` -- canonical workflow ordering and all insertion rules
