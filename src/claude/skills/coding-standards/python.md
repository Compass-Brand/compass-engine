# Python Coding Standards

## Type Hints

- Use type hints for all function signatures
- Use `from __future__ import annotations` for forward refs
- Prefer `list[str]` over `List[str]` (requires Python 3.9+)
- Use `Optional[T]` for nullable types (Python 3.5+), or `T | None` (requires Python 3.10+)
- Use TypedDict for dictionary shapes

## Async Patterns

- Use asyncio for I/O-bound operations
- Prefer `async with` for context managers
- Use `asyncio.gather()` for parallel operations
- Don't mix sync and async code carelessly
- Use `await` consistently (no floating coroutines)

## Error Handling

- Create custom exceptions inheriting from Exception
- Use specific exceptions, not bare `except:`
- Include context with `raise ... from e`
- Use `contextlib.suppress()` only for truly expected and benign errors (e.g., `FileNotFoundError` when a file may legitimately not exist)
- Document exceptions in docstrings

## Import Organization

1. Standard library
2. Third-party packages
3. Local imports

- Blank line between groups
- Use absolute imports
- Avoid `from x import *`

## Naming Conventions

- `PascalCase`: Classes
- `snake_case`: Functions, variables, modules
- `SCREAMING_SNAKE_CASE`: Constants
- `_private`: Internal use (single underscore)
- `__dunder__`: Magic methods only
