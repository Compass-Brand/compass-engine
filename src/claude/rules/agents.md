# Agent Delegation Rules

## When to Delegate

- Complex multi-step tasks that benefit from focused context
- Parallel workstreams that can run independently
- Specialized tasks requiring specific tool configurations
- Tasks that would exceed main agent context limits

## Model Selection

- **Opus**: Complex reasoning, architectural decisions, nuanced analysis
- **Sonnet**: Standard development tasks, code generation, documentation
- **Haiku**: Quick operations, simple queries, validation checks

## Tool Restrictions

- Read-only agents should not have write access
- Limit tool access to what the task requires
- Explicitly deny sensitive operations for research agents
- Document tool restrictions in agent configuration

## Prompt Guidelines

- Provide clear, specific instructions with defined outcomes
- Include relevant context and constraints
- Specify expected output format
- Set explicit boundaries on scope
- Include success criteria for task completion
