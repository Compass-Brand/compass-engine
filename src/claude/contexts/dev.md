# Development Context

You are operating in **development mode** with full edit capabilities.

## Mode Characteristics

- **Full edit access**: Create, modify, and delete files
- **TDD focus**: Write tests before implementation
- **Commit frequently**: Lock in working state every 15-20 minutes
- **Use all tools**: Serena, Forgetful, Context7, Bash, etc.

## Development Workflow

1. **Understand the task** - Query Forgetful for context, read relevant code
2. **Write failing tests** - TDD is mandatory for all functional code
3. **Implement** - Write minimal code to make tests pass
4. **Refactor** - Clean up while keeping tests green
5. **Commit** - Use conventional commit format

## Active Checks

- Run tests after each significant change
- Validate with `./scripts/validate-before-push.sh` before committing
- Check for security issues (no hardcoded secrets)
- Ensure type hints and documentation

## Reminders

- Query Forgetful memory at session start
- Save important decisions to Forgetful
- Use Serena for symbol analysis instead of grep
- Follow patterns in existing code
