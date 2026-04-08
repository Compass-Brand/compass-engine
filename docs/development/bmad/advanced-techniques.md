# Advanced Elicitation and Adversarial Review

Last reviewed: 2026-04-08

Techniques for pushing artifacts beyond first-draft quality. These are "anytime" skills -- available at any point in the BMAD workflow -- that pressure-test ideas, surface blind spots, and iteratively refine content until it is genuinely robust.

## Advanced Elicitation

Advanced elicitation pushes the LLM to reconsider assumptions, find gaps, and deepen its analysis of a draft artifact. Instead of accepting the first reasonable output, you apply structured thinking methods that force re-examination from different angles.

### How It Works

The skill loads a registry of **50 elicitation methods** spanning 12 categories:

| Category | Example Methods | Best For |
| --- | --- | --- |
| core | First Principles Analysis, 5 Whys, Socratic Questioning | Foundational clarity |
| collaboration | Stakeholder Round Table, Debate Club Showdown | Multi-perspective alignment |
| advanced | Tree of Thoughts, Self-Consistency Validation | Complex reasoning paths |
| competitive | Red Team vs Blue Team, Shark Tank Pitch | Stress-testing viability |
| technical | Architecture Decision Records, Security Audit Personas | Engineering trade-offs |
| creative | SCAMPER Method, Reverse Engineering | Innovation and ideation |
| risk | Pre-mortem Analysis, Failure Mode Analysis | Risk mitigation |
| research | Thesis Defense Simulation, Comparative Analysis Matrix | Evidence-based decisions |
| learning | Feynman Technique, Active Recall Testing | Verifying understanding |
| philosophical | Occam's Razor Application | Simplification |
| retrospective | Hindsight Reflection, Lessons Learned Extraction | Continuous improvement |

### Interactive Flow

When invoked, the skill:

1. Analyzes the current content for type, complexity, stakeholder needs, risk level, and creative potential.
2. Selects 5 best-fit methods and presents them as a numbered menu.
3. The user picks a method (or multiple), and the skill applies it to the working content.
4. After each method, the user decides whether to accept (`y`), discard (`n`), or provide further direction.
5. The menu re-appears until the user selects `x` to finalize and return the enhanced content.

Additional menu options: `r` reshuffles with 5 new methods, `a` lists all 50 methods for manual selection, and entering multiple numbers chains methods in sequence.

### Party Mode Integration

If party mode is active when advanced elicitation is invoked, the loaded agent personas participate in the elicitation. For example, a Stakeholder Round Table would draw on the actual BMAD agent roster rather than hypothetical personas, making the discussion richer and more grounded in the project context.

## Adversarial Review

Adversarial review is a structured challenge of artifacts to find weaknesses. Where advanced elicitation refines and deepens, adversarial review attacks. Two complementary review skills cover different dimensions.

### General Adversarial Review (AR)

The reviewer adopts a skeptical, cynical stance and assumes problems exist. Given any content -- a diff, spec, story, or document -- it finds at least ten issues covering what is wrong, what is missing, and what is unclear. Output is a Markdown findings list.

Invoke via menu code `AR` or skill name `bmad-review-adversarial-general`.

### Edge Case Hunter Review (ECH)

Orthogonal to the general review, this skill is method-driven rather than attitude-driven. It mechanically walks every branching path and boundary condition in the content, reporting only unhandled edge cases. Output is a structured JSON array with location, trigger condition, guard snippet, and potential consequence for each gap.

Invoke via menu code `ECH` or skill name `bmad-review-edge-case-hunter`.

### When to Combine Them

Use both reviews together for maximum coverage. The adversarial review catches high-level issues (unclear requirements, missing stakeholder concerns, weak justifications), while the edge case hunter catches low-level path gaps (unguarded inputs, missing defaults, off-by-one conditions). Neither subsumes the other.

## The Autonomous Refinement Loop

The Autonomous Refinement Loop (ORL) combines party-mode collaboration and advanced elicitation into a fully automated iterative process. It runs without manual interaction until zero unresolved issues remain.

### How It Differs from Manual Use

| Aspect | Manual Elicitation | Autonomous Refinement Loop |
| --- | --- | --- |
| User interaction | Menu-driven, per-method confirmation | Fully autonomous, no prompts |
| Agent participation | Optional (if party mode active) | Always builds a review team |
| Termination | User selects `x` | Zero open issues after full re-scan |
| Scope | Single method at a time | 3-5 methods per iteration |
| Tracking | Implicit in conversation | Persistent issue ledger |

### The Iteration Cycle

Each iteration proceeds through these stages:

1. **Build team** -- Assemble a facilitator, 2+ domain reviewers, and an implementation-focused fixer. Reviewers rotate across iterations for diversity.
2. **Party critique** -- The team reviews the working content and raises issue candidates with severity ratings.
3. **Autonomous elicitation** -- 3-5 methods are auto-selected (with category diversity, no consecutive repeats) and applied without user prompts. New weaknesses become issue candidates.
4. **Merge into ledger** -- New issues get IDs and `open` status. Duplicates are deduped. Previously fixed issues that reappear are reopened.
5. **Auto-remediate** -- Open issues are processed in severity order (Critical to Low). Fixes are applied directly to the working content.
6. **Blocker gate** -- If any issue cannot be safely fixed, the loop halts and escalates with full context: what was attempted, why it failed, and what decision is needed.
7. **Full re-scan** -- Party critique and elicitation run again against the updated content. The ledger is reconciled.
8. **Stop or continue** -- If zero open issues remain after re-scan, the refined content is returned. Otherwise, the next iteration begins.

### The Issue Ledger

The loop maintains a persistent ledger tracking every issue across iterations:

| Field | Purpose |
| --- | --- |
| `id` | Unique identifier (I001, I002, ...) |
| `source` | Where it was found (`party` or `elicitation`) |
| `severity` | `Critical`, `High`, `Medium`, or `Low` |
| `status` | `open`, `fixed`, `blocked`, or `dismissed` |
| `issue` | Description of the problem |
| `proposed_fix` | How to resolve it |
| `rationale` | Why this fix was chosen |
| `first_seen_iteration` | When it first appeared |
| `last_updated_iteration` | When it was last touched |

Ledger rules: issues are never silently deleted, fixed issues reopen if they reappear, and dismissals require explicit rationale.

### Key Constraints

- The loop does not invoke adversarial review tasks (those remain separate, user-invoked skills).
- No iteration cap or timeout is applied -- it runs until clean or blocked.
- No separate report is generated; the target content itself is the output.

## When to Use These Techniques

### Advanced Elicitation

Use when you want to deepen or improve an artifact interactively:

- **PRD sections** that feel shallow or assumption-heavy
- **Architecture decisions** with unclear trade-offs
- **Epic and story definitions** that need stakeholder perspective
- After any workflow step where the first draft needs strengthening
- When exploring alternatives before committing to a direction

### Adversarial Review

Use when you need a structured quality gate:

- Before finalizing any deliverable
- After completing a PRD, architecture doc, or epic
- On code diffs before merge (the code review workflow runs this automatically)
- When you suspect gaps but cannot articulate them

### Autonomous Refinement Loop

Use when you want hands-off hardening of a specific artifact:

- High-stakes PRDs where thoroughness matters more than speed
- Architecture documents for complex systems
- Any content where iterative multi-perspective review would catch issues that a single pass misses
- When you want to walk away and let the system converge on quality

## Integration with the Main Workflow

All three techniques are registered as **anytime** skills in their respective modules. They do not belong to a specific BMAD phase and can be invoked at any point.

### Invocation

Each skill can be invoked by its slash command or menu code:

| Skill | Slash Command | Menu Code |
| --- | --- | --- |
| Advanced Elicitation | `/bmad-compass-advanced-elicitation` | `AE` |
| Autonomous Refinement Loop | `/bmad-compass-autonomous-refinement-loop` | `ORL` |
| Adversarial Review | `/bmad-review-adversarial-general` | `AR` |
| Edge Case Hunter | `/bmad-review-edge-case-hunter` | `ECH` |

### The `--content` Argument

Advanced Elicitation and the Autonomous Refinement Loop accept a `--content` argument. This tells the skill what artifact or section to operate on.

When invoked **standalone** (by the user directly), the skill uses the current conversation context or the content you point it to. When invoked **from another workflow** (e.g., a PRD creation workflow calls elicitation at a checkpoint), the calling workflow passes the current draft section as `--content`, and the skill returns the enhanced version when complete.

This pattern enables two usage modes:

- **Direct:** `/bmad-compass-advanced-elicitation --content planning/prd.md` -- apply elicitation to an existing artifact file.
- **Embedded:** A workflow step internally invokes the skill with the section it just generated, creating a natural refinement checkpoint without requiring the user to switch context.

The adversarial review skills use a `[path]` argument instead, accepting a file path to the content under review.

### Workflow Checkpoints

Several BMAD workflows include built-in elicitation checkpoints. At these points, the workflow pauses and invokes advanced elicitation on the section just completed. The user can apply methods, accept changes, and proceed -- or skip straight to `x` if the section is already satisfactory.

The Autonomous Refinement Loop is typically invoked explicitly rather than embedded, because its fully autonomous nature means it should be a deliberate choice.

## Related Documentation

- [BMAD Overview](./bmad-overview.md) -- Architecture and module system
- [Creating Skills](./creating-skills.md) -- How to build new skills
- [Custom Modules](./custom-modules.md) -- Compass-specific module structure
