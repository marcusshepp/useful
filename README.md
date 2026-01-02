# Useful Tools

A collection of tools and scripts to make life easier. Each directory contains focused utilities for specific tasks with documentation on how to use them.

## Available Tools

### AWS Management (`aws/`)
PowerShell module and Copilot skills for managing AWS EC2 production environments.
- SSH connection management
- Docker container operations
- Health checks and log monitoring
- See [aws/README.md](aws/README.md) for setup and usage

### Azure DevOps Integration (`network/`)
PowerShell module for managing Azure DevOps work items with natural language support.
- Search and filter work items
- Update tickets and add comments
- Export to markdown reports
- See [network/README.md](network/README.md) for setup and usage

### Azure Sprint Analysis (`azure/`)
Python tool for generating sprint performance reports and visualizations.
- Velocity tracking
- Commitment vs completion analysis
- Bug metrics
- See [azure/README.md](azure/README.md) for setup and usage

### Eva Tools (`eva/`)
Database migration and management scripts for Eva project.
- Database switching utilities (PowerShell and Python)
- Migration scripts for database changes
- Committee reports refactoring tools
- Contains: `migrations.py`, `migrations.ps1`, `switch-db.py`, `switch-db.ps1`, and subdirectories for specific tasks

### Stock Media (`unsplash/`)
PowerShell module for querying Unsplash and Pexels APIs.
- Search photos and videos
- Download media assets
- See [unsplash/README.md](unsplash/README.md) for setup and usage

### CentOS Server Setup (`centos/`)
Shell scripts for CentOS 7 server configuration on Linode.
- SSH key generation
- Docker installation and updates
- Git installation
- See [centos/README.md](centos/README.md) for details

### Playwright Testing (`playwrite/`)
Automated UI testing framework for index builder functionality.
- Python-based Playwright tests
- Index verification utilities
- See [playwrite/README.md](playwrite/README.md) for setup and usage

### Angular Analysis (`delta/`)
Python tool for analyzing Angular component dependencies and impact.
- Track component changes between commits
- Identify service dependencies
- Generate regression testing recommendations
- Usage: `python delta/main.py -p <project-path> --from-commit <hash> --to-commit <hash>`

### Lab Scripts (`labs/`)
Miscellaneous utility scripts for various environments.
- Alpine VM setup script

## Requirements

Different tools have different requirements. Check each tool's README for specific dependencies:
- **PowerShell tools**: PowerShell 7.0+
- **Python tools**: Python 3.8+
- **Node.js tools**: Node.js 16+

## Contributing

Feel free to add new tools or improve existing ones. Keep each tool:
- Self-contained in its own directory
- Well-documented with a README
- Focused on solving specific problems
