# BMAD Workflow (Repo-Verified Canonical Order)

This is the top-to-bottom BMAD order for this repo if you want to run everything in sequence.
Optional steps are kept in-line and marked `Optional` so you can opt out without losing order.

Repo verification completed before this update:

- Source parity check across local copies:
  - `reference/BMAD/modules/bmm` == `BMAD-METHOD/src/bmm` (hash match)
  - `reference/BMAD/modules/core` == `BMAD-METHOD/src/core` (hash match)
  - `reference/BMAD/modules/test-architecture` == `bmad-method-test-architecture-enterprise/src` (hash match)
  - `reference/BMAD/modules/bmad-builder` == `bmad-builder/src` (hash match)
- Workflow ordering validated from module catalogs and workflow files (not docs-only).

## Legend

- `Required`: Required BMM progression gate.
- `Optional`: Valid in-order step you can skip.
- `TEA Insert`: TEA step insertion point.
- `Replace?`: Whether the TEA step replaces a BMM step.

## Full Product-Delivery Order (Run-All Default)

### Phase 0: Optional Pre-Work (Do First if Applicable)

| Run Order | Workflow                       | Command                              | Required | Notes                                                                 |
| --------- | ------------------------------ | ------------------------------------ | -------- | --------------------------------------------------------------------- |
| 1         | Initialize Docs                | `/bmad-bmm-init-docs`                | No       | Brownfield docs migration into Compass layout (`document-project` alias supported). |
| 2         | Generate Project Context       | `/bmad-bmm-generate-project-context` | No       | Brownfield context pack for agents.                                   |
| 3         | Teach Me Testing (TEA Academy) | `/bmad-tea-teach-me-testing`         | No       | TEA learning lane before delivery execution.                          |

### Phase 1: Analysis

| Run Order | Workflow           | Command                          | Required |
| --------- | ------------------ | -------------------------------- | -------- |
| 1         | Brainstorm Project | `/bmad-brainstorming`            | No       |
| 2         | Market Research    | `/bmad-bmm-market-research`      | No       |
| 3         | Domain Research    | `/bmad-bmm-domain-research`      | No       |
| 4         | Technical Research | `/bmad-bmm-technical-research`   | No       |
| 5         | Create Brief       | `/bmad-bmm-create-product-brief` | No       |

### Phase 2: Planning

| Run Order | Workflow               | Command                      | Required |
| --------- | ---------------------- | ---------------------------- | -------- |
| 1         | Create PRD             | `/bmad-bmm-create-prd`       | Yes      |
| 2         | Validate PRD           | `/bmad-bmm-validate-prd`     | No       |
| 3         | Edit PRD               | `/bmad-bmm-edit-prd`         | No       |
| 4         | Create UX Design       | `/bmad-bmm-create-ux-design` | No       |
| 5         | Update Docs (Planning) | `/bmad-bmm-update-docs`      | No       |

### Phase 3: Solutioning

| Run Order | Workflow                          | Command                                    | Required | TEA Insert | Replace? |
| --------- | --------------------------------- | ------------------------------------------ | -------- | ---------- | -------- |
| 1         | Create Architecture               | `/bmad-bmm-create-architecture`            | Yes      | No         | N/A      |
| 2         | Test Design (System-Level mode)   | `/bmad-tea-testarch-test-design`           | No       | Yes        | No       |
| 3         | Create Epics and Stories          | `/bmad-bmm-create-epics-and-stories`       | Yes      | No         | N/A      |
| 4         | Test Framework Setup              | `/bmad-tea-testarch-framework`             | No       | Yes        | No       |
| 5         | CI Setup                          | `/bmad-tea-testarch-ci`                    | No       | Yes        | No       |
| 6         | Update Docs (Solutioning)         | `/bmad-bmm-update-docs`                    | No       | No         | N/A      |
| 7         | Check Implementation Readiness    | `/bmad-bmm-check-implementation-readiness` | Yes      | No         | N/A      |

Notes:

- `test-design` is dual-mode:
  - Phase 3 uses **System-Level mode**.
  - Phase 4 uses **Epic-Level mode** (below).

### Phase 4: Implementation

Follow this phase from top to bottom.

#### 4A. Sprint Kickoff

| Run Order | Workflow        | Command                     | Required |
| --------- | --------------- | --------------------------- | -------- |
| 1         | Sprint Planning | `/bmad-bmm-sprint-planning` | Yes      |
| 2         | Sprint Status   | `/bmad-bmm-sprint-status`   | No       |

#### 4B. Epic Loop (Repeat for Every Epic)

| Run Order | Workflow                      | Command                          | Required | TEA Insert | Replace? |
| --------- | ----------------------------- | -------------------------------- | -------- | ---------- | -------- |
| 1         | Test Design (Epic-Level mode) | `/bmad-tea-testarch-test-design` | No       | Yes        | No       |

#### 4C. Story Loop (Repeat for Every Story in Current Epic)

| Run | ID  | Workflow        | Command                                  | Required |
| --- | --- | --------------- | ---------------------------------------- | -------- |
| 1   | CS  | Create Story    | `/bmad-bmm-create-story`                 | Yes      |
| 2   | VS  | Validate Story  | `/bmad-bmm-create-story` (Validate Mode) | No       |
| 3   | AT  | ATDD            | `/bmad-tea-testarch-atdd`                | No       |
| 4   | DS  | Dev Story       | `/bmad-bmm-dev-story`                    | Yes      |
| 5   | QA  | QA Automation   | `/bmad-bmm-qa-automate`                  | No       |
| 6   | TA  | Test Automation | `/bmad-tea-testarch-automate`            | No       |
| 7   | CR  | Code Review     | `/bmad-bmm-code-review`                  | No       |
| 8   | RV  | Test Review     | `/bmad-tea-testarch-test-review`         | No       |
| 9   | TR  | Traceability    | `/bmad-tea-testarch-trace`               | No       |
| 10  | SS  | Sprint Status   | `/bmad-bmm-sprint-status`                | No       |

- TEA insert points in this loop: `AT`, `TA`, `RV`, `TR`.
- Overlap note: `TA` partially overlaps `QA`; pick one primary automation lane to avoid duplicate generation.

Loop routing:

1. `CS` -> `VS` (optional) -> `AT` (optional) -> `DS`
2. `QA` (optional) -> `TA` (optional) -> `CR`
3. `RV` (optional) -> `TR` (optional) -> `SS` (optional)
4. If review/gate fails, route back to `DS` and repeat downstream steps.

#### 4D. Epic Wrap-Up (After Stories in Current Epic)

| Run Order | Workflow                             | Command                   | Required |
| --------- | ------------------------------------ | ------------------------- | -------- |
| 1         | Update Docs (Implementation)         | `/bmad-bmm-update-docs`   | No       |
| 2         | Retrospective                         | `/bmad-bmm-retrospective` | No       |
| 3         | Sprint Status                         | `/bmad-bmm-sprint-status` | No       |

#### 4E. Release Gate (After Final Epic, Before Release)

| Run Order | Workflow                          | Command                          | Required | Notes                                                   |
| --------- | --------------------------------- | -------------------------------- | -------- | ------------------------------------------------------- |
| 1         | NFR Assessment                    | `/bmad-tea-testarch-nfr`         | No       | Recommended before release.                             |
| 2         | Test Review (Final audit pass)    | `/bmad-tea-testarch-test-review` | No       | Optional final quality audit.                           |
| 3         | Traceability Gate (Release scope) | `/bmad-tea-testarch-trace`       | No       | Set gate scope to release (e.g., `gate_type=release`). |
| 4         | Validate Docs                     | `/bmad-bmm-validate-docs`        | No       | Docs gate for structure, policy sync, and navigation.  |
| 5         | Sprint Status                     | `/bmad-bmm-sprint-status`        | No       | Final status snapshot.                                  |

## TEA Insertion and Replacement Rules (Exact)

1. TEA does not replace required BMM progression gates:
   - `/bmad-bmm-create-prd`
   - `/bmad-bmm-create-architecture`
   - `/bmad-bmm-create-epics-and-stories`
   - `/bmad-bmm-check-implementation-readiness`
   - `/bmad-bmm-sprint-planning`
   - `/bmad-bmm-create-story`
   - `/bmad-bmm-dev-story`
2. `test-review` does not replace `code-review`.
3. `testarch-automate` partially overlaps `bmm-qa-automate`; pick one primary lane to avoid duplicate generation.
4. `nfr-assess` does not replace `trace` gate decisions; it complements gate evidence.
5. `test-design` appears twice by design:
   - Phase 3: System-Level mode (architecture/testability integration).
   - Phase 4: Epic-Level mode (per-epic risk/coverage planning).

## Required BMM Gate Chain (Quick Scan)

1. `/bmad-bmm-create-prd`
2. `/bmad-bmm-create-architecture`
3. `/bmad-bmm-create-epics-and-stories`
4. `/bmad-bmm-check-implementation-readiness`
5. `/bmad-bmm-sprint-planning`
6. Story progression: `/bmad-bmm-create-story` -> `/bmad-bmm-dev-story`

## Anytime Lanes (Outside Linear Gate Chain)

### Core

| Workflow                     | Command                            |
| ---------------------------- | ---------------------------------- |
| Brainstorming                | `/bmad-brainstorming`              |
| Party Mode                   | `/bmad-party-mode`                 |
| Help                         | `/bmad-help`                       |
| Index Docs                   | `/bmad-index-docs`                 |
| Shard Document               | `/bmad-shard-doc`                  |
| Editorial Review - Prose     | `/bmad-editorial-review-prose`     |
| Editorial Review - Structure | `/bmad-editorial-review-structure` |
| Adversarial Review           | `/bmad-review-adversarial-general` |

### BMM

| Workflow                 | Command / Invocation                 |
| ------------------------ | ------------------------------------ |
| Initialize Docs          | `/bmad-bmm-init-docs`                |
| Generate Project Context | `/bmad-bmm-generate-project-context` |
| Quick Spec               | `/bmad-bmm-quick-spec`               |
| Quick Dev                | `/bmad-bmm-quick-dev`                |
| Correct Course           | `/bmad-bmm-correct-course`           |
| Write Document           | Load `/tech-writer`, then `WD`       |
| Update Standards         | Load `/tech-writer`, then `US`       |
| Mermaid Generate         | Load `/tech-writer`, then `MG`       |
| Validate Document        | Load `/tech-writer`, then `VD`       |
| Update Docs              | `/bmad-bmm-update-docs`              |
| Validate Docs            | `/bmad-bmm-validate-docs`            |
| Explain Concept          | Load `/tech-writer`, then `EC`       |

### BMad Builder (Separate Lane; Not Part of Product Delivery Flow)

`bmad-builder` workflows are module/agent/workflow authoring tools and remain `anytime`.
They do not insert into the BMM product-delivery gate chain.

## Command Compatibility (TEA)

| Canonical Slash Alias            | Alternate Colon Form         |
| -------------------------------- | ---------------------------- |
| `/bmad-tea-teach-me-testing`     | `/bmad:tea:teach-me-testing` |
| `/bmad-tea-testarch-test-design` | `/bmad:tea:test-design`      |
| `/bmad-tea-testarch-framework`   | `/bmad:tea:framework`        |
| `/bmad-tea-testarch-ci`          | `/bmad:tea:ci`               |
| `/bmad-tea-testarch-atdd`        | `/bmad:tea:atdd`             |
| `/bmad-tea-testarch-automate`    | `/bmad:tea:automate`         |
| `/bmad-tea-testarch-test-review` | `/bmad:tea:test-review`      |
| `/bmad-tea-testarch-nfr`         | `/bmad:tea:nfr-assess`       |
| `/bmad-tea-testarch-trace`       | `/bmad:tea:trace`            |

## Source Files Audited

- `reference/BMAD/modules/bmm/module-help.csv`
- `reference/BMAD/modules/core/module-help.csv`
- `reference/BMAD/modules/test-architecture/module-help.csv`
- `reference/BMAD/modules/bmad-builder/module-help.csv`
- `reference/BMAD/modules/bmm/workflows/**`
- `reference/BMAD/modules/core/workflows/**`
- `reference/BMAD/modules/test-architecture/workflows/testarch/**`
- `reference/BMAD/modules/bmad-builder/workflows/**`
- `BMAD-METHOD/src/**`
- `bmad-method-test-architecture-enterprise/src/**`
- `bmad-builder/src/**`
