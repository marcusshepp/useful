# View Worker Logs

I need to check the logs for the Fizz background workers to understand what's being processed.

## Available Workers

- `worker-discovery` - Discovers leads from search results
- `worker-screenshots` - Captures website screenshots
- `worker-lighthouse` - Runs performance audits
- `worker-vision` - AI analysis of screenshots
- `worker-sections` - Extracts page sections
- `worker-email` - Generates outreach emails
- `worker-followup` - Handles follow-up sequences

## Commands

```powershell
Import-Module .\FizzAws.psm1

# View specific worker logs
Get-FizzLogs -Container worker-discovery -Tail 100
Get-FizzLogs -Container worker-screenshots -Tail 100
Get-FizzLogs -Container worker-vision -Tail 100

# Follow logs in real-time
Get-FizzLogs -Container worker-discovery -Follow

# View all logs together
Watch-FizzLogs -Tail 50
```

## What I'm Looking For
[Describe what you're investigating - stuck jobs, errors, processing speed, etc.]
