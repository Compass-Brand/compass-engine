# Git Workflow Rules

## Conventional Commits

- Use standard prefixes: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`
- Format: `<type>: <short description>`
- Include scope when relevant: `feat(auth): add login validation`
- Body should explain "why" not "what"

## Commit Frequency

- Maximum 15-20 minutes without committing
- Commit after each logical unit of work
- Commit before switching tasks or exploring new approaches
- Lock in working state after successful test runs

## Branch Naming

- Format: `type/description`
- Examples: `feat/add-auth`, `fix/login-error`, `refactor/database-layer`
- Use lowercase with hyphens
- Keep names short but descriptive

## Commit Quality

- Never commit broken or non-compiling code
- Remove debugging artifacts before committing
- Ensure all tests pass before committing
- One logical change per commit (avoid mixing unrelated changes)

## Co-Author Attribution

- Include co-author line when AI assists:
  ```
  Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
  ```
