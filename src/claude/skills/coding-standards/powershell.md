# PowerShell Coding Standards

## Type Safety

- Use `[Parameter()]` attributes with types
- Use `[OutputType()]` for function returns
- Prefer strongly-typed parameters
- Use `[ValidateSet()]` for constrained values
- Use `[ValidatePattern()]` with `ErrorMessage` parameter for regex validation with clear error messages
- Cast to specific types when parsing input

## Error Handling

- Use `try/catch/finally` for structured handling
- Set `$ErrorActionPreference = 'Stop'` for scripts
- Use `-ErrorAction Stop` for critical commands
- Write errors with `Write-Error` not `throw` for non-terminating
- Use `throw` for terminating errors

## Cmdlet Design

- Follow Verb-Noun naming (Get-Item, Set-Config)
- Support `-WhatIf` and `-Confirm` for changes
- Use `[CmdletBinding()]` for advanced functions
- Accept pipeline input where appropriate
- Return objects, not formatted strings

## Import Organization

- Use `#Requires -Modules` for dependencies
- Import modules at script start
- Use `using namespace` for .NET types
- Avoid dot-sourcing when modules work

## Naming Conventions

- `PascalCase`: Functions, cmdlets, parameters
- `camelCase`: Local variables
- `SCREAMING_SNAKE_CASE`: Constants/readonly
- `$script:Variable`: Script-scoped
- `$global:Variable`: Avoid when possible

## Output Best Practices

- Return objects, format in calling code
- Use `Write-Verbose` for diagnostic output
- Use `Write-Information` for user messages
- Use `Write-Output` or implicit return for data
- Never use `Write-Host` for data (only UI)
