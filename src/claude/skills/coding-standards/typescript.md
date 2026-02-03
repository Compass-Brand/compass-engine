# TypeScript Coding Standards

## Type Safety

- Enable strict mode in tsconfig.json
- Avoid `any` - use `unknown` if type truly unknown
- Use explicit return types for public functions
- Prefer type inference for local variables
- Use branded types for IDs (e.g., `type UserId = string & { _brand: 'UserId' }`)

## Async Patterns

- Always use async/await over raw Promises
- Handle errors with try/catch at boundaries
- Don't mix callbacks and promises
- Use Promise.all for parallel operations
- Avoid floating promises (always await or void)

## Error Handling

- Create custom error classes for domains
- Include context in error messages
- Don't swallow errors silently
- Use Result types for expected failures
- Throw only for exceptional cases

## Import Organization

1. External packages (node_modules)
2. Internal packages (workspace)
3. Relative imports (./local)

- Blank line between groups
- Alphabetize within groups

## Naming Conventions

- `PascalCase`: Types, interfaces, classes, enums
- `camelCase`: Variables, functions, methods
- `SCREAMING_SNAKE_CASE`: Constants
- `kebab-case`: File names
- Prefix interfaces with `I` only if needed for clarity
