---
name: security-review
description: Systematic security analysis using OWASP Top 10, dependency auditing, and secret scanning
---

# Security Review Skill

## Purpose

Provide systematic security analysis using OWASP Top 10, dependency auditing, and secret scanning.

## OWASP Top 10 Checklist (2021)

### A01: Broken Access Control

- [ ] Authorization checks on all protected routes
- [ ] No direct object references without validation
- [ ] Deny by default principle
- [ ] Rate limiting on sensitive operations

### A02: Cryptographic Failures

- [ ] No hardcoded secrets/keys
- [ ] TLS for data in transit
- [ ] Strong encryption for sensitive data at rest
- [ ] Secure random number generation

### A03: Injection

- [ ] Parameterized queries (no string concatenation)
- [ ] Input validation and sanitization
- [ ] No eval() or dynamic code execution
- [ ] Shell command escaping

### A04: Insecure Design

- [ ] Threat modeling performed
- [ ] Security requirements documented
- [ ] Defense in depth applied
- [ ] Secure defaults

### A05: Security Misconfiguration

- [ ] Unnecessary features disabled
- [ ] Default credentials changed
- [ ] Error messages don't leak details
- [ ] Security headers configured

### A06: Vulnerable Components

- [ ] Dependencies up to date
- [ ] No known CVEs in dependencies
- [ ] Minimal dependency footprint
- [ ] Regular dependency audits

### A07: Authentication Failures

- [ ] Strong password requirements
- [ ] Multi-factor authentication available
- [ ] Session management secure
- [ ] Brute force protection

### A08: Integrity Failures

- [ ] Input validation on all external data
- [ ] Integrity verification on downloads
- [ ] CI/CD pipeline secured
- [ ] Signed commits/releases

### A09: Logging & Monitoring Failures

- [ ] Security events logged
- [ ] No sensitive data in logs
- [ ] Log integrity protected
- [ ] Alerting on suspicious activity

### A10: SSRF (Server-Side Request Forgery)

- [ ] URL validation on user-provided URLs
- [ ] Allowlisting for external requests
- [ ] No internal network exposure
- [ ] Metadata endpoint protection

## Dependency Audit Commands

### JavaScript/npm

```bash
npm audit                    # Check vulnerabilities
npm audit fix               # Auto-fix where possible
npm audit --json            # JSON output for processing
```

### Python/pip

```bash
pip-audit                   # Requires: pip install pip-audit
pip-audit --fix            # Attempt fixes
pip-audit -f json          # JSON output
```

### Go

```bash
govulncheck ./...          # Requires: go install golang.org/x/vuln/cmd/govulncheck@latest
```

### Ruby

```bash
bundle-audit check         # Requires: gem install bundler-audit
```

## Secret Scanning Patterns

### Patterns to Detect

```regex
# API Keys
(?i)(api[_\-]?key|apikey)['":\s]*['"]?[a-zA-Z0-9]{20,}

# AWS Keys
(AKIA|A3T|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}

# Private Keys
-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----

# JWT Tokens
eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*

# Generic Secrets
(?i)(password|secret|token|credential)['":\s]*['"]?[^\s'"]{8,}
```

### Tools

- `gitleaks` - Git history scanning
- `trufflehog` - Secret detection
- `detect-secrets` - Pre-commit hook

## CVSS Scoring Guidelines

| Score    | Severity | Action Required        |
| -------- | -------- | ---------------------- |
| 9.0-10.0 | Critical | Immediate fix required |
| 7.0-8.9  | High     | Fix within 24-48 hours |
| 4.0-6.9  | Medium   | Fix within 1 week      |
| 0.1-3.9  | Low      | Fix in next release    |

## Output Format

```markdown
## Security Review: [Component/File]

### Findings Summary

| ID  | Severity | Category | Finding                        |
| --- | -------- | -------- | ------------------------------ |
| S1  | Critical | A03      | SQL injection in query builder |

### Details

#### S1: SQL injection in query builder

- **Location**: src/db/query.ts:45
- **CVSS**: 9.8 (Critical)
- **Issue**: User input concatenated directly into SQL
- **Remediation**: Use parameterized queries
- **Reference**: https://owasp.org/Top10/A03_2021-Injection/
```
