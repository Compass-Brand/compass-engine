---
name: instincts
description: Capture patterns and corrections during sessions, store in Forgetful memory, and graduate proven instincts to skills
---

# Instincts - Continuous Learning System

## Purpose

Capture patterns and corrections during sessions, store in Forgetful memory, and graduate proven instincts to skills.

## What Are Instincts?

Instincts are learned patterns from:

- User corrections ("No, do it this way...")
- Repeated preferences observed across sessions
- Successful approaches to recurring problems
- Workflow optimizations discovered during work

## How Instincts Work

### Capture

When a pattern is identified:

1. Extract the trigger condition ("When X happens...")
2. Extract the action ("...do Y")
3. Assign initial confidence based on source:
   - **User explicit correction**: Medium-High (0.7) - user directly stated preference
   - **Observed repeated behavior**: Medium-Low (0.55) - inferred from patterns
   - **Successful approach**: Medium (0.6) - worked but not explicitly requested
4. Store in Forgetful with instinct tags

### Reinforcement

Each time an instinct is used:

- **Positive outcome**: Confidence increases by +0.05 (capped at 0.95 to require graduation for full confidence). Upon graduation to a skill, confidence is set to 1.0 (full confidence)
- **User correction**: Confidence decreases by -0.15 (floored at 0.1 to preserve learning)
- Invocation count increments

### Graduation

Instincts can evolve to skills when:

- Confidence > 0.9
- Invocations > 10
- No contradictions with existing patterns

## Commands

- [/instinct-status](../../commands/instinct-status.md) - List all instincts with confidence/invocations
- [/instinct-export](../../commands/instinct-export.md) - Export instincts to JSON file
- [/instinct-import](../../commands/instinct-import.md) - Import instincts from JSON file
- [/evolve](../../commands/evolve.md) - Graduate qualifying instincts to skills

## Integration with Forgetful

Instincts are stored as Forgetful memories with special tagging for retrieval and analysis.
