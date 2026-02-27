Overall Assessment: The file is very solid, short, structured, LLM-optimized, and focuses on non-obvious constraints—ideal for a context file.
Strengths (What the File Does Well):
Constraint-Oriented: Focuses on must happen, must never happen, and architectural separation (logic, pure/impure, persisted/transient). This reduces "AI drift."
Protects Architecture: Includes strong rules against breaking architecture (e.g., pure validation rules, centralized types, Zustand hygiene, no local interface definitions, immediate validation, transient API keys).
Clean Category Separation: Sections are structured for token efficiency and selective injection: Tech stack, Language rules, Framework rules, Testing rules, Code quality, Workflow rules, and Anti-patterns.
Areas for Improvement (Based on User's History/Preferences):
The file is missing meta-constraints the user strongly prefers: No assumptions, no silent fallbacks, no hidden coupling, SSOT enforcement, no architectural drift, no "AI slop," and an "Ask if uncertain" mandate.
Suggestion 1: Add "Uncertainty Protocol" Section:
STOP and ask if requirements are ambiguous.
Do not invent props, fields, or state slices.
Do not introduce fallback logic unless explicitly specified.
Do not silently widen scope.
Suggestion 2: Add "No Architectural Drift" Rule (Architectural Integrity):
Do not introduce new state management patterns.
Do not mix imperative and declarative state flows.
Do not bypass the validation lifecycle.
Do not create alternate persistence paths.
Suggestion 3: Add SSOT Declaration (Single Source of Truth):
Explicitly list SSOT locations (e.g., Domain models: src/lib/types.ts, Validation rules: src/lib/rules/, Persistence layer: Zustand store).
Rule: Do not duplicate schema definitions.
Suggestion 4: Explicit Anti-LLM Drift Section:
Do not add defensive guards unless required by the domain model.
Do not add optional chaining to bypass type issues.
Do not widen union types without updating validation rules.
Strategic Insight: The file achieves surgical, lightweight, and LLM-optimized governance, similar to a PAUL-style template, and is superior to typical GSD templates.