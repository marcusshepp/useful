# Fizz AWS Management

PowerShell module and Copilot skills for managing the Fizz production environment on AWS EC2.

## Setup

1. Copy `.env.example` to `.env` and fill in your values:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` with your EC2 details:
   - `EC2_HOST`: Your EC2 public IP or Elastic IP
   - `SSH_KEY_PATH`: Path to your SSH private key (.pem file)

3. Import the module:
   ```powershell
   Import-Module .\FizzAws.psm1
   ```

## Quick Start

```powershell
# Connect to server
Connect-FizzServer

# Check health
Get-FizzHealth

# View logs
Get-FizzLogs -Container app -Tail 100
Watch-FizzLogs

# Debug errors
Get-FizzErrors

# Restart services
Restart-FizzContainer -Container app
```

## Available Commands

| Command | Description |
|---------|-------------|
| `Connect-FizzServer` | Open interactive SSH session |
| `Invoke-FizzSsh <cmd>` | Run command via SSH |
| `Get-FizzContainers` | List Docker containers |
| `Get-FizzLogs` | View container logs |
| `Watch-FizzLogs` | Tail all container logs |
| `Restart-FizzContainer` | Restart a container |
| `Enter-FizzContainer` | Open shell in container |
| `Invoke-FizzDocker` | Run command in container |
| `Invoke-FizzCompose` | Run docker-compose commands |
| `Get-FizzHealth` | Health check all services |
| `Get-FizzErrors` | Find errors in logs |
| `Get-FizzStats` | View resource usage |
| `Test-FizzDatabase` | Test DB connectivity |

## Copilot Skills

The `.github/skills/fizz-production/SKILL.md` file teaches Copilot how to manage the Fizz production environment. When you open Copilot in this directory, it will understand:
- The architecture and containers
- How to use the PowerShell module
- Debugging workflows
- Common operations

## Prompts

The `prompts/` directory contains reusable prompts:
- `debug-production.md` - Investigate production issues
- `check-status.md` - Get status report
- `view-worker-logs.md` - Check worker processing
- `restart-services.md` - Restart containers
- `database-ops.md` - Database queries and operations
- `ssh-command.md` - Run custom SSH commands

## Infrastructure

- **Domain**: fyzz.dev
- **EC2**: Ubuntu 22.04
- **Database**: PostgreSQL (RDS)
- **Containers**: Next.js app, Redis, Caddy, 7 workers
