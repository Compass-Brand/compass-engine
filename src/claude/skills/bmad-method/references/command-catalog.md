# BMAD Command Catalog

Generated from `dist/_bmad/_config/bmad-help.csv` (auto-generated at build time from per-module `module-help.csv` files).

Use this reference when selecting the right BMAD slash command for the current phase or when translating a BMAD workflow request into the shipped client command surface.

## learning

- `/bmad-tea-teach-me-testing` (Teach Me Testing): Teach testing fundamentals through 7 sessions (TEA Academy).

## analysis

- `/bmad-bmm-create-product-brief` (Create Brief): Create the high-level product brief that anchors the roadmap and later slice-level planning.
- `/bmad-bmm-domain-research` (Domain Research): Industry domain deep dive, subject matter expertise, and terminology.
- `/bmad-bmm-market-research` (Market Research): Market analysis, competitive landscape, customer needs, and trends.
- `/bmad-bmm-project-roadmap` (Project Roadmap): Create or update the approved roadmap summary and roadmap state from high-level analysis artifacts before phase activation.
- `/bmad-bmm-technical-research` (Technical Research): Technical feasibility, architecture options, and implementation approaches.
- `/bmad-brainstorming` (Brainstorm Project): Expert guided facilitation through a single or multiple techniques.
- `/bmad-cis-design-thinking` (Design Thinking): Run human-centered opportunity framing to sharpen product direction before the brief. Phase-scoped runs should redirect outputs to the current strategy lane.
- `/bmad-cis-innovation-strategy` (Innovation Strategy): Identify disruption opportunities and strategic bets that strengthen roadmap-level product direction. Phase-scoped runs should redirect outputs to the current strategy lane.

## planning

- `/bmad-bmm-create-prd` (Create PRD): Expert-led facilitation to produce the phase-scoped Product Requirements Document.
- `/bmad-bmm-create-ux-design` (Create UX): Realize the UX direction for the active slice, especially when UI behavior or interaction design matters.
- `/bmad-bmm-edit-prd` (Edit PRD): Revise an existing PRD when validation, WDS, or architecture work exposes requirement gaps.
- `/bmad-bmm-initiative-routing` (Initiative Routing): For workspace or parent repos, route the approved active phase into concurrent repo-targeted initiative workstreams without creating repo-local delivery artifacts.
- `/bmad-bmm-phase-sync` (Phase Sync): Select and frame the active roadmap slice, maintain the human phase brief, and keep the machine phase state aligned.
- `/bmad-bmm-update-docs` (Update Docs (Planning)): Checkpoint docs update after planning and experience-design artifacts are established.
- `/bmad-bmm-validate-prd` (Validate PRD): Validate the PRD for completeness, cohesion, and readiness for the WDS lane.
- `/bmad-wds-conceptual-specs` (Conceptual Specifications): Convert approved UX direction and scenario context into implementation-ready conceptual specifications for the active slice.
- `/bmad-wds-design-delivery` (Design Delivery): Package completed conceptual specs into design-delivery artifacts, test scenarios, and handoff notes for implementation.
- `/bmad-wds-outline-scenarios` (Outline Scenarios): ”Transform the active slice trigger map into scenario outlines that feed UX
- `/bmad-wds-trigger-mapping` (Trigger Mapping): ”Run the WDS trigger-mapping lane after PRD validation to connect business goals

## solutioning

- `/bmad-bmm-check-implementation-readiness` (Check Implementation Readiness): Ensure the PRD, UX, architecture, epics, and stories are aligned before implementation starts.
- `/bmad-bmm-create-architecture` (Create Architecture): Document the technical decisions for the active roadmap slice.
- `/bmad-bmm-create-epics-and-stories` (Create Epics and Stories): Create the epics and stories list for the active slice.
- `/bmad-bmm-update-docs` (Update Docs (Solutioning)): Checkpoint docs update after architecture, readiness, and security artifacts are refined.
- `/bmad-cybersec-secure-gates` (Secure Readiness Gate): Apply the conditional pre-implementation security gate and record the draft gate package before readiness approval.
- `/bmad-cybersec-security-architecture-review` (Security Architecture Review): Review the draft architecture with zero-trust and control-assessment lenses when the security lane is active.
- `/bmad-cybersec-threat-modeling` (Threat Modeling): Run STRIDE-based threat modeling against the current architecture and produce the threat model artifact for security-active slices.
- `/bmad-tea-testarch-ci` (CI/CD Alignment): TEA insert: align CI/CD quality automation with the current repo reality before readiness approval.
- `/bmad-tea-testarch-framework` (Test Framework): TEA insert: initialize or adapt the test framework after epics and stories are drafted.
- `/bmad-tea-testarch-test-design` (Test Design): TEA insert: system-level risk-based test design after architecture and before story decomposition.

## implementation

- `/bmad-bmm-code-review` (Code Review): If review finds issues, route back to Dev Story; if approved, continue through test review and traceability or advance to the next story.
- `/bmad-bmm-create-story` (Create Story): Story cycle start: prepare the next story in the sprint plan or a specifically requested story, then route through validation, ATDD, development, automation, and review.
- `/bmad-bmm-create-story` (Validate Story): Validate story readiness and completeness before development work begins.
- `/bmad-bmm-dev-story` (Dev Story): Execute story implementation tasks and tests, then hand off to automation and review.
- `/bmad-bmm-implementation-brainstorming` (Implementation Brainstorming): Implementation-focused ideation for the active phase and sprint execution.
- `/bmad-bmm-implementation-research` (Implementation Research): Implementation-focused research for active epics and stories plus delivery risk reduction.
- `/bmad-bmm-phase-closeout` (Phase Closeout): Close the active phase: archive the current snapshot, capture lessons, and refresh the next-phase scaffold.
- `/bmad-bmm-qa-automate` (QA Automation Test): Generate automated API and E2E tests for implemented code using the existing project test framework. Use after implementation to add coverage, not for code review or story validation.
- `/bmad-bmm-retrospective` (Retrospective): Optional at epic end: review completed work, lessons learned, and readiness for the next epic.
- `/bmad-bmm-sprint-planning` (Sprint Planning): Kick off implementation by producing the sprint plan the delivery agents will follow in sequence for the active stories.
- `/bmad-bmm-sprint-status` (Sprint Status): Anytime: summarize sprint status and route to the next workflow.
- `/bmad-bmm-update-docs` (Update Docs (Implementation)): Checkpoint docs update at epic boundaries or major implementation milestones.
- `/bmad-bmm-validate-docs` (Validate Docs): Validate docs structure, policy compliance, and navigation integrity before closeout.
- `/bmad-cybersec-secure-gates` (Secure Release Gate): Apply the conditional release security gate using available test, scan, and security evidence before final validation and closeout.
- `/bmad-tea-testarch-atdd` (ATDD): TEA insert: generate failing tests before implementation begins.
- `/bmad-tea-testarch-automate` (Test Automation): TEA insert: expand automated coverage after implementation. Pick the primary lane versus QA automation to avoid duplicates.
- `/bmad-tea-testarch-nfr` (NFR Assessment): TEA release gate: assess non-functional requirements before final release.
- `/bmad-tea-testarch-test-design` (Test Design (Epic Scope)): TEA insert: epic-level risk-based test design before the story loop for each epic.
- `/bmad-tea-testarch-test-review` (Test Review): TEA insert: quality audit for implemented tests at story level and, when needed, release level.
- `/bmad-tea-testarch-trace` (Traceability): TEA insert: coverage traceability and gate decision for story or release scope.

## anytime

- `/bmad-autonomous-refinement-loop` (Autonomous Refinement Loop): Run autonomous party-mode and auto-elicitation loops with agent teams until zero unresolved issues remain; manual Party Mode and Advanced Elicitation remain available separately. Escalates only on blocked fixes.
- `/bmad-bmm-correct-course` (Correct Course): Anytime: navigate significant changes. May recommend restart, PRD updates, architecture changes, sprint replanning, or story corrections.
- `/bmad-bmm-generate-project-context` (Generate Project Context): Generate or refresh the lean project-context artifact for the active roadmap slice or brownfield repo state.
- `/bmad-bmm-init-docs` (Initialize Docs): Migrate existing documentation into Compass opinionated docs structure while preserving legacy docs in dated migration snapshots.
- `/bmad-bmm-init-planning` (Initialize Planning): Normalize existing planning into the Compass roadmap-driven planning structure while preserving legacy planning in dated migration snapshots.
- `/bmad-bmm-quick-dev` (Quick Dev): Quick one-off tasks, small changes, simple apps, and utilities without extensive planning. Do not suggest for complex work unless requested or the user explicitly wants to skip the full BMAD method.
- `/bmad-bmm-quick-spec` (Quick Spec): Quick one-off specs for small changes, utilities, and brownfield additions to well-established patterns without extensive planning.
- `/bmad-bmm-sync-repositories` (Sync Repositories): Compare planning/repositories.yaml against the current repo topology and update the approved registry after explicit approval.
- `/bmad-bmm-workspace-bootstrap` (Workspace Bootstrap): Bootstrap selected repos from a workspace or orchestration root into the Compass BMAD planning and docs structure using safe migration rules.
- `/bmad-brainstorming` (Brainstorming): Generate diverse ideas through interactive techniques. Broad strategic brainstorming writes to roadmap lane by default.
- `/bmad-cis-problem-solving` (Problem Solving): Apply structured problem-solving methods to delivery blockers, design traps, or implementation challenges without forking the main BMAD pipeline.
- `/bmad-editorial-review-prose` (Editorial Review - Prose): Review prose for clarity, tone, and communication issues. Use after drafting to polish written content.
- `/bmad-editorial-review-structure` (Editorial Review - Structure): Propose cuts, reorganization, and simplification while preserving comprehension. Use when doc produced from multiple subprocesses or needs structural improvement.
- `/bmad-help` (bmad-help): Get unstuck by showing what workflow steps come next or answering BMad Method questions.
- `/bmad-index-docs` (Index Docs): Create lightweight index for quick LLM scanning. Use when LLM needs to understand available docs without loading everything.
- `/bmad-party-mode` (Party Mode): Orchestrate multi-agent discussions. Use when you need multiple agent perspectives or want agents to collaborate.
- `/bmad-review-adversarial-general` (Adversarial Review (General)): Review content critically to find issues and weaknesses. Use for quality assurance or before finalizing deliverables. Code Review in other modules run this automatically, but its useful also for document reviews
- `/bmad-shard-doc` (Shard Document): Split large documents into smaller files by sections. Use when doc becomes too large (>500 lines) to manage effectively.
