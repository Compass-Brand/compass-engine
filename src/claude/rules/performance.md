# Performance and Context Efficiency Rules

## Tool Call Optimization

- Batch independent tool calls in single message blocks
- Prefer parallel execution for non-dependent operations
- Avoid sequential calls when parallel calls work

## MCP Tool Preference

- Prefer MCP tools (Serena, Forgetful, Context7) over raw Bash commands
- Use Serena for symbol analysis instead of grep for code navigation
- Use Context7 for library documentation lookup

## Memory and Context

- Query Forgetful memory before starting work on any project
- Save important decisions and patterns to memory
- Use project IDs to scope memory queries appropriately

## Search Strategies

- Use Task tool for open-ended searches requiring multiple rounds
- Use Glob for file pattern matching
- Use Grep for content searching
- Avoid reading entire files when symbol analysis suffices

## Resource Efficiency

- Prefer targeted file reads over full file reads
- Use line offsets when only part of a file is needed
- Clean up temporary resources after use
- Avoid redundant operations (check if action needed first)

## MCP Context Budget

- **CRITICAL:** Each MCP server consumes ~10-30k tokens of context
- Keep under 10 MCPs enabled simultaneously
- Monitor token usage; compact proactively at ~45k tokens
- Use Serena for code navigation instead of grep to reduce context
- Prefer targeted symbol lookups over full file reads
