# Debug Production Issue

I need to debug an issue on the Fizz production server (fyzz.dev).

## Current Symptoms
[Describe what's happening - errors, slow performance, features not working, etc.]

## Steps to Investigate

1. First, import the FizzAws module and check overall health:
   ```powershell
   Import-Module .\FizzAws.psm1
   Get-FizzHealth
   ```

2. Check for errors across all containers:
   ```powershell
   Get-FizzErrors
   ```

3. Look at specific container logs based on the issue:
   - App issues: `Get-FizzLogs -Container app -Tail 200`
   - Worker issues: `Get-FizzLogs -Container worker-<name> -Tail 200`
   - Database issues: `Get-FizzLogs -Container postgres -Tail 100`

4. Test database connectivity:
   ```powershell
   Test-FizzDatabase
   ```

5. Check resource usage:
   ```powershell
   Get-FizzStats
   ```

Please help me investigate and fix this issue.
