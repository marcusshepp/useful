# Check Fizz Production Status

Give me a comprehensive status report of the Fizz production environment.

## What to Check

1. **Container Health**
   ```powershell
   Import-Module .\FizzAws.psm1
   Get-FizzContainers -All
   Get-FizzHealth
   ```

2. **Recent Errors**
   ```powershell
   Get-FizzErrors -Lines 20
   ```

3. **Resource Usage**
   ```powershell
   Get-FizzStats
   ```

4. **Database Status**
   ```powershell
   Test-FizzDatabase
   ```

Please run these commands and summarize:
- Which containers are running/stopped
- Any error patterns in the logs
- Current CPU/memory usage
- Disk space status
- Any immediate concerns
