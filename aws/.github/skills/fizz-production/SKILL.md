---
name: fizz-production
description: Enables Copilot to SSH into the Fizz EC2 instance and manage Docker containers for the fyzz.dev production app.
---

# Fizz Production Management Skill

This skill enables you to manage the Fizz lead generation application running on AWS EC2.

## Architecture Overview

Fizz is a Next.js application deployed on EC2 with the following components:
- **fizz-app**: Main Next.js web application (port 3000)
- **fizz-postgres**: PostgreSQL 16 database
- **fizz-redis**: Redis for rate limiting and caching
- **fizz-caddy**: Caddy reverse proxy with automatic HTTPS
- **Workers**: Background job processors
  - `fizz-worker-discovery`: Lead discovery
  - `fizz-worker-screenshots`: Website screenshots
  - `fizz-worker-lighthouse`: Performance analysis
  - `fizz-worker-vision`: AI vision analysis
  - `fizz-worker-sections`: Section extraction
  - `fizz-worker-email`: Email generation
  - `fizz-worker-followup`: Follow-up email handling

## Using the FizzAws PowerShell Module

First, import the module:
```powershell
Import-Module .\FizzAws.psm1
```

### Common Operations

**Connect to the server:**
```powershell
Connect-FizzServer
```

**View container status:**
```powershell
Get-FizzContainers
Get-FizzHealth
```

**View logs:**
```powershell
Get-FizzLogs -Container app -Tail 100
Get-FizzLogs -Container worker-discovery -Follow
Watch-FizzLogs  # All containers
```

**Debug errors:**
```powershell
Get-FizzErrors
Get-FizzStats
```

**Restart containers:**
```powershell
Restart-FizzContainer -Container app
Invoke-FizzCompose -Action restart
```

**Enter container shell:**
```powershell
Enter-FizzContainer -Container app
Enter-FizzContainer -Container postgres -Shell /bin/bash
```

**Run commands in containers:**
```powershell
Invoke-FizzDocker -Container app -Command "npx prisma studio"
Invoke-FizzDocker -Container postgres -Command "psql -U fizz -d fizz"
```

## Infrastructure Details

- **Domain**: fyzz.dev (Route53 managed)
- **EC2**: Ubuntu 22.04, t3.small
- **RDS**: PostgreSQL on db.t4g.micro
- **Region**: us-east-1
- **SSH User**: ubuntu

## Debugging Checklist

When investigating production issues:

1. Check container health: `Get-FizzHealth`
2. Look for errors: `Get-FizzErrors`
3. Check specific container logs: `Get-FizzLogs -Container <name>`
4. Verify database connectivity: `Test-FizzDatabase`
5. Check resource usage: `Get-FizzStats`
6. Review recent deployments in the fizz repository

## Environment Variables

The app uses these key environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ANTHROPIC_API_KEY`: For AI features
- `SERPAPI_API_KEY`: For search functionality
- `PAGESPEED_API_KEY`: For Lighthouse analysis
- `AUTH_SECRET`: Authentication secret
- `SMARTLEAD_API_KEY`: For email campaigns
