# TypeScript Coding Standards

## Type Safety

- Enable strict mode in tsconfig.json
- Avoid `any` - use `unknown` if type truly unknown
- Use explicit return types for public functions
- Prefer type inference for local variables
- Use branded types for IDs (e.g., `type UserId = string & { _brand: 'UserId' }`) - the `_brand` property is phantom/compile-time only and adds no runtime overhead

## Async Patterns

- Prefer async/await over raw Promises, but raw Promises are acceptable for Promise.race, Promise.any, deferred patterns, and APIs that require them
- Handle errors with try/catch at boundaries
- Don't mix callbacks and promises
- Use Promise.all for parallel operations
- Avoid floating promises (always await or void)

## Error Handling

- Create custom error classes for domains
- Include context in error messages
- Don't swallow errors silently
- Use Result types for expected failures (e.g., `Result<T, E>` discriminated union with `{ ok: true, value: T } | { ok: false, error: E }`; consider libraries like neverthrow or ts-results)
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
