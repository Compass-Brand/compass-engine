# Security Rules

## Secrets and Credentials

- No hardcoded secrets, API keys, or credentials in code
- Use environment variables or secure vaults for sensitive data
- Never commit `.env` files or credential files to version control

## Dynamic Code Execution

- No `eval()`, `exec()`, or equivalent dynamic code execution
- Avoid `Function()` constructor in JavaScript
- No string-based SQL queries (use parameterized queries)

## Input Validation

- Validate and sanitize all external input (user input, API responses, file contents)
- Use allowlists over denylists when validating input
- Implement strict type checking on incoming data

## Dependency Security

- Run `npm audit` or equivalent before adding dependencies
- Review dependency licenses and security advisories
- Pin dependency versions to prevent supply chain attacks
- Prefer well-maintained packages with active security support

## Command Injection Prevention

- Never pass unsanitized input to shell commands
- Use subprocess libraries with array-based arguments (not shell strings)
- Escape or reject special characters in command arguments

## File Path Security

- Sanitize file paths to prevent directory traversal attacks
- Normalize paths: JS `path.resolve()`, Python `os.path.abspath()` or `pathlib.Path().resolve()`
- Validate that paths stay within expected directories
- Never use user input directly in file operations

## HTTPS / TLS Requirements

- Always use HTTPS for external communications
- Validate SSL/TLS certificates; do not disable certificate verification
- Use TLS 1.2+ for all encrypted connections
- Configure secure cipher suites

## Authentication / Authorization

- Implement defense in depth with authentication at multiple layers
- Use established libraries (e.g., passport.js, authlib) instead of rolling your own
- Enforce principle of least privilege for all access controls
- Session tokens must be cryptographically secure and properly invalidated on logout

## Logging Hygiene

- Never log passwords, tokens, API keys, or PII
- Sanitize user input before logging to prevent log injection
- Use structured logging with appropriate severity levels
- Ensure logs are stored securely with access controls

## Error Handling

- Do not expose stack traces or internal details in production error responses
- Use generic error messages for users; detailed errors only in logs
- Catch and handle exceptions gracefully; avoid crashes that leak information
- Configure error pages that do not reveal implementation details
