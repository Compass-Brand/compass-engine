# Instincts Data Model

## Storage Location

Instincts are stored in Forgetful MCP as memories with specific structure.

## Memory Format

```json
{
  "title": "[INSTINCT] Pattern description",
  "content": "Detailed pattern with examples and context",
  "tags": ["instinct", "confidence-high"],
  "metadata": {
    "type": "instinct",
    "pattern": "When X happens, do Y",
    "trigger": "Description of trigger condition",
    "action": "Description of action to take",
    "confidence": 0.75,
    "invocations": 5,
    "last_used": "YYYY-MM-DDTHH:mm:ssZ",
    "created": "YYYY-MM-DDTHH:mm:ssZ",
    "source": "user_correction|observed_pattern|explicit_instruction"
  }
}
```

## Confidence Levels

| Level  | Range    | Tag               | Meaning                      |
| ------ | -------- | ----------------- | ---------------------------- |
| Low    | 0.0-0.5  | confidence-low    | Tentative, needs validation  |
| Medium | 0.5-0.75 | confidence-medium | Promising, moderate evidence |
| High   | 0.75-0.9 | confidence-high   | Well-established pattern     |
| Ready  | 0.9-0.95 | confidence-ready  | Ready for skill graduation   |

> **Note:** Confidence is capped at 0.95 for instincts. Full 1.0 confidence is only achieved after graduation to a skill, representing complete trust in the pattern.

## Confidence Adjustments

- Positive outcome: +0.05 (capped at 0.95)
- User correction: -0.15 (floored at 0.1)
- Contradiction found: -0.25

> **Note:** Adjustments are applied sequentially and clamped to [0.0, 1.0] after each adjustment. For example, if confidence is 0.1 and a contradiction is found (-0.25), the result is clamped to 0.0, not -0.15.

## Query Examples

```python
# Find all instincts
mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "instinct patterns",
  "tags": ["instinct"]
})

# Find ready-to-graduate
mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "high confidence instincts",
  "tags": ["instinct", "confidence-ready"]
})
```
