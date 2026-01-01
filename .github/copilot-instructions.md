# GitHub Copilot Instructions for Useful Scripts Repository

This repository contains miscellaneous utility scripts for automation tasks across various domains (AWS, Azure, database management, web automation, etc.).

## Code Style

### Python
- Use Python 3 with type hints where appropriate
- Follow PEP 8 style guidelines
- Include docstrings for modules, classes, and functions
- Use descriptive variable names
- Example format from repository:
```python
#!/usr/bin/env python3

"""
Module Description
------------------

Brief description of what the module does.

Usage:
    python script.py [options]

Environment Variables Required:
    VAR_NAME: Description

Author: Marcus Shepherd
Date: [Date]
"""
```

### PowerShell
- Use approved verbs (Get-, Set-, Invoke-, etc.)
- Include comment-based help for functions
- Use CamelCase for function names
- Use verbose parameter descriptions
- Follow module structure as seen in `FizzAws.psm1`

### JavaScript/TypeScript
- Use modern ES6+ syntax
- Prefer const over let, avoid var
- Use async/await for asynchronous operations
- Follow existing code patterns in the repository

### Shell Scripts
- Use `#!/bin/bash` or appropriate shebang
- Include comments explaining complex operations
- Use descriptive variable names in UPPER_CASE for environment variables

## Security Practices

### Environment Variables and Secrets
- **NEVER** commit secrets, API keys, passwords, or sensitive data to the repository
- Always use environment variables for sensitive data
- Store credentials in `.env` files (already gitignored)
- Use patterns like `.env.example` for documenting required variables
- Reference environment variables like: `$ENV:VAR_NAME` (PowerShell) or `os.getenv('VAR_NAME')` (Python)

### Database Operations
- Use parameterized queries to prevent SQL injection
- Prefer read-only operations (SELECT) when possible
- Block dangerous operations (UPDATE, DELETE, DROP) in utility scripts as seen in `EvaSql.psm1`
- Always validate and sanitize user inputs

## Directory Structure

This repository is organized by domain/technology:
- `aws/` - AWS EC2 and infrastructure management (PowerShell modules, Copilot skills)
- `azure/` - Azure DevOps utilities
- `network/` - Database query tools and Azure DevOps skills
- `eva/` - Eva application database utilities
- `playwrite/` - Playwright-based web automation testing
- `delta/` - Delta-related utilities
- `anth/` - Anthropic/AI-related scripts
- `llama/` - LLM-related tools
- `labs/` - Experimental scripts
- `media/` - Media processing utilities
- `unsplash/` - Unsplash API utilities
- `notes/` - Documentation and notes

## Agent Skills

### Using Agent Skills
- Agent Skills are located in `.github/skills/` directories within subdirectories
- Skills follow the [Agent Skills open standard](https://agentskills.io/)
- Each skill has a `SKILL.md` file with instructions and usage documentation
- Skills include reference documentation in `references/` subdirectories
- Copilot will automatically discover and use these skills when relevant

### Existing Skills
- `aws/.github/skills/fizz-production/` - Manages Fizz production environment on AWS EC2
- `network/.github/skills/` - Multiple skills for Eva and Legislature databases, Azure DevOps

When creating new skills:
- Follow the existing structure with `SKILL.md` and `references/` subdirectories
- Include clear usage examples
- Document all required environment variables
- Provide schema documentation for database-related skills

## Testing

- Write tests that match existing test patterns in the repository
- For Python: Use standard test frameworks (pytest, unittest)
- For JavaScript: Use frameworks like Jest when applicable
- Test scripts should be self-contained and documented

## Documentation

### README Files
- Each major directory should have a README.md explaining its purpose
- Include setup instructions, prerequisites, and usage examples
- Document required environment variables
- Provide quick start guides

### Inline Documentation
- Use comments to explain non-obvious logic
- Document parameters, return values, and side effects
- Include usage examples in function/module docstrings

## Common Patterns

### Connection Management
- Use connection pooling where appropriate
- Close connections properly in finally blocks or context managers
- Handle connection failures gracefully with clear error messages

### Error Handling
- Use try/except blocks for operations that may fail
- Provide meaningful error messages
- Log errors appropriately
- Fail fast for configuration errors

### Script Entry Points
- Check for required environment variables at startup
- Validate command-line arguments
- Provide usage information for incorrect invocations
- Use `if __name__ == "__main__":` pattern for Python scripts

## Dependencies

- Keep dependencies minimal and well-documented
- Document dependencies in:
  - `requirements.txt` for Python
  - `package.json` for Node.js
  - README files for PowerShell modules
- Avoid adding unnecessary dependencies

## Git Practices

### Files to Ignore
These patterns are already in `.gitignore`:
- `.env` and environment variable files
- `key.txt` and sensitive files
- `*.log` files
- `__pycache__/` and Python bytecode
- `node_modules/` and `dist/`
- IDE settings (`.vscode/`, `.idea/`)
- Data directories (`*_data/`, `backups/`)

### Commit Messages
- Use clear, descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused on single changes

## Repository Purpose

This is a personal collection of automation scripts that:
- Automate repetitive tasks
- Provide utilities for infrastructure management
- Offer database query and management tools
- Support web automation testing
- Include AI/ML integration utilities

When suggesting changes or additions:
- Maintain the miscellaneous, utility-focused nature
- Keep scripts independent and self-contained where possible
- Prioritize simplicity and practicality over complex architectures
- Document thoroughly for future reference
