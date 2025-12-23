# Restart Fizz Services

I need to restart services on the Fizz production server.

## Quick Commands

```powershell
Import-Module .\FizzAws.psm1

# Restart a single container
Restart-FizzContainer -Container app
Restart-FizzContainer -Container worker-discovery

# Restart all services via docker-compose
Invoke-FizzCompose -Action restart

# Full restart (down then up)
Invoke-FizzCompose -Action down
Invoke-FizzCompose -Action up -Detach

# Rebuild and restart (after code changes)
Invoke-FizzCompose -Action up -Detach -Build
```

## Available Containers
- `app` - Main Next.js application
- `postgres` - Database
- `redis` - Cache/rate limiting
- `caddy` - Reverse proxy
- `worker-discovery`, `worker-screenshots`, `worker-lighthouse`, `worker-vision`, `worker-sections`, `worker-email`, `worker-followup`

## What I Need to Restart
[Specify which service and why - after deploy, memory leak, stuck process, etc.]
