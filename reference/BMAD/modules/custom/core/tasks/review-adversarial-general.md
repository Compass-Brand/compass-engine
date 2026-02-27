---
name: review-adversarial-general
description: "Perform an adversarial review and produce findings with skeptical, high-rigor analysis."
standalone: true
---

# Task: Adversarial Review (General)

## Objective
Perform a skeptical review of an artifact and produce a findings report with concrete issues.

## Inputs
- `content`: content to review (diff, doc, spec, story, branch summary, or similar artifact).
- `also_consider` (optional): additional focus areas.

## Mandatory Execution Rules
- Execute all steps in order.
- Assume problems exist and actively search for missing, weak, or risky elements.
- Maintain precise, professional language. No insults or profanity.
- If no findings are produced, re-check and explain why this is suspicious.

## Flow
### 1. Receive Content
- Load content from input or context.
- If empty or unreadable, ask for clarification and abort.
- Identify artifact type and constraints.

### 2. Adversarial Analysis
- Review with extreme skepticism.
- Identify at least ten findings to fix, improve, or clarify.
- Consider:
- missing requirements.
- hidden assumptions.
- unsafe defaults.
- ambiguous language.
- untested or unverifiable claims.

### 3. Present Findings
- Output findings as a markdown list of concise issue descriptions.

## Halt Conditions
- Content is empty or unreadable.
- Zero findings after analysis (requires re-analysis or explicit user guidance).
