# SSH and Execute Custom Command

I need to run a custom command on the Fizz production server.

## Quick Reference

```powershell
Import-Module .\FizzAws.psm1

# Interactive SSH session
Connect-FizzServer

# Run a single command
Invoke-FizzSsh "docker ps"
Invoke-FizzSsh "df -h"
Invoke-FizzSsh "free -m"
Invoke-FizzSsh "uptime"

# Docker commands
Invoke-FizzSsh "docker logs fizz-app --tail 50"
Invoke-FizzSsh "docker stats --no-stream"
Invoke-FizzSsh "docker system prune -f"

# Check app directory
Invoke-FizzSsh "ls -la /home/ubuntu/fizz"
Invoke-FizzSsh "cat /home/ubuntu/fizz/.env"

# System logs
Invoke-FizzSsh "sudo journalctl -u docker --since '1 hour ago'"
```

## Command I Need to Run
[Specify the command or what you're trying to accomplish]
