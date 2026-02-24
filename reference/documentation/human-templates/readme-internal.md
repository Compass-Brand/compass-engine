<!-- Template from writing-documentation skill. Delete this line. -->
# [Service Name]

> [One-line description of what this service does]

**Team:** [Team name] | **On-call:** [Rotation link or contact]

## Overview

[2-3 sentences. What does this service do? Where does it fit in the system?]

**Depends on:** [upstream service(s)]
**Depended on by:** [downstream service(s)]

## Local Development Setup

### Prerequisites

- [Runtime] [version]+
- [Database/tool] [version]+
- [Other dependency]

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `[VAR_NAME]` | [What it configures] | [default or required] |
| `[VAR_NAME]` | [What it configures] | [default or required] |

### Run Locally

```bash
# Install dependencies
[install command]

# Set up local database (if applicable)
[db setup command]

# Start the service
[run command]
```

### Run Tests

```bash
# Unit tests
[unit test command]

# Integration tests
[integration test command]
```

## Architecture

[Brief description of how the service is structured. Include a diagram if helpful.]

### Key Files

| Path | Purpose |
|------|---------|
| `src/[file]` | [What it does] |
| `src/[file]` | [What it does] |
| `config/[file]` | [What it configures] |

## Deployment

| Environment | URL | Branch |
|-------------|-----|--------|
| Dev | [url] | `develop` |
| Staging | [url] | `staging` |
| Production | [url] | `main` |

[Deployment process notes, if any.]

## Runbooks

### [Common Task Name]

```bash
[Commands to perform the task]
```

### [Another Common Task]

```bash
[Commands to perform the task]
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| [What you see] | [Why it happens] | [How to fix it] |
| [What you see] | [Why it happens] | [How to fix it] |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and PR guidelines.

## Related Docs

- [Architecture overview](link)
- [API documentation](link)
- [Runbook collection](link)
