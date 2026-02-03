# BMAD Upgrade

An upgrade to the standard BMAD (Breakthrough Method of Agile AI-Driven Development) methodology, customized for Compass Brand's workflows and automation needs.

## Overview

This project extends the BMAD-METHOD framework with:

- **Automated workflows** for common development tasks
- **Custom agents** tailored to Compass Brand's tech stack
- **Enhanced templates** for planning artifacts
- **Integration** with Compass Brand's MCP infrastructure

## Structure

```
bmad-engine/
├── BMAD-METHOD/          # Core BMAD framework (submodule)
├── _bmad-output/         # Generated artifacts and customizations
│   └── bmb-creations/    # Custom modules and workflows
├── docs/                 # Documentation
├── plans/                # Planning documents
├── reference/            # Reference materials
└── tests/                # Test files
```

## Getting Started

### Prerequisites

- Git
- Claude Code with MCP support
- Access to Compass Brand's MCP services

### Installation

1. Clone with the parent repository:
   ```bash
   git clone --recurse-submodules https://github.com/Compass-Brand/Compass-Brand.git
   ```

2. Or clone standalone:
   ```bash
   git clone https://github.com/Compass-Brand/bmad-engine.git
   cd bmad-engine
   git submodule update --init --recursive
   ```

### Usage

The BMAD workflows are available through Claude Code's skill system:

- `/bmad:bmm:workflows:create-prd` - Create a Product Requirements Document
- `/bmad:bmm:workflows:create-architecture` - Design system architecture
- `/bmad:bmm:workflows:sprint-planning` - Plan implementation sprints
- `/bmad:bmm:workflows:dev-story` - Execute story implementation

## BMAD Methodology

BMAD provides a structured approach to software development:

1. **Product Brief** - Define the vision and scope
2. **PRD** - Detail requirements and user stories
3. **Architecture** - Design technical solutions
4. **Epics & Stories** - Break down into implementable units
5. **Sprint Execution** - Build with TDD practices

## License

Private - Compass Brand © 2026
