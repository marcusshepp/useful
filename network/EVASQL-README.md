# EvaSql PowerShell Module

PowerShell module for querying Eva and Legislature (M2) databases across multiple environments.

## Quick Start

```powershell
# 1. Load environment variables (contains database passwords)
. c:\Users\mshepherd\p\useful\env-vars.ps1

# 2. Set M2 password (for Legislature database)
$env:M2_QA_PASSWORD = $env:SHARED_QA_PASSWORD

# 3. Import the module
Import-Module c:\Users\mshepherd\p\useful\network\EvaSql.psm1 -Force

# 4. Run a query
Invoke-EvaSql -Query "SELECT * FROM Committee" -Environment M2-QA
```

## Overview

This module provides two main functions for database operations:

-   `Invoke-EvaSql` - For SELECT queries that return data
-   `Invoke-EvaSqlNonQuery` - For INSERT, UPDATE, DELETE operations

## Environments

### Eva Database Environments

-   `Local` - Local Docker SQL Server (Eva database)
-   `QA` - Eva_QA database on tvmwsqls01
-   `DEMO` - Eva_DEMO database on uvmwsqls01
-   `UAT` - Eva_UAT database on uvmwsqls01

### Legislature (M2) Database Environments

-   `M2-Local` - Local Docker SQL Server (Legislature database)
-   `M2-QA` - Legislature database on tvmwsqls01 (shared data)
-   `M2-DEMO` - Legislature database on MLSQL-QA.lsb.legislature.mi.gov
-   `M2-UAT` - Legislature database on MLSQL-SUP.lsb.legislature.mi.gov

**Important**: M2 environments access the **shared Legislature database** which contains:

-   Committee data
-   Member data
-   Session data
-   Other shared legislative data

## Environment Variables Required

The module expects these environment variables to be set:

```powershell
# Eva Database Passwords
$env:EVA_LOCAL_PASSWORD    # For Local Eva
$env:EVA_QA_PASSWORD       # For QA Eva
$env:EVA_DEMO_PASSWORD     # For DEMO Eva
$env:EVA_UAT_PASSWORD      # For UAT Eva

# M2/Legislature Database Passwords
$env:M2_LOCAL_PASSWORD     # For Local Legislature
$env:M2_QA_PASSWORD        # For QA Legislature (use $env:SHARED_QA_PASSWORD)
$env:M2_DEMO_PASSWORD      # For DEMO Legislature
$env:M2_UAT_PASSWORD       # For UAT Legislature
```

These are typically set by sourcing `env-vars.ps1`:

```powershell
. c:\Users\mshepherd\p\useful\env-vars.ps1
$env:M2_QA_PASSWORD = $env:SHARED_QA_PASSWORD  # Set M2 password from shared password
```

## Usage Examples

### Querying Eva Database

```powershell
# Get all sessions from Eva QA
Invoke-EvaSql -Query "SELECT * FROM sessions" -Environment QA

# Get current session
Invoke-EvaSql -Query "SELECT * FROM sessions WHERE IsCurrentSession = 1" -Environment QA

# Get recent committee reports
Invoke-EvaSql -Query "SELECT TOP 10 * FROM CommitteeReports ORDER BY Created DESC" -Environment QA
```

### Querying Legislature (M2) Database

```powershell
# Get all committees from shared database in QA
Invoke-EvaSql -Query "SELECT * FROM Committee" -Environment M2-QA

# Get active committees
Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName, ChamberID FROM Committee WHERE IsActive = 1" -Environment M2-QA

# Get Senate committees only (ChamberID = 2)
Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName FROM Committee WHERE ChamberID = 2 AND IsActive = 1" -Environment M2-QA

# Get committee details
Invoke-EvaSql -Query "SELECT * FROM Committee WHERE CommitteeID = 466" -Environment M2-QA
```

### Modifying Data (NonQuery)

```powershell
# Update a record (returns number of rows affected)
Invoke-EvaSqlNonQuery -Query "UPDATE sessions SET IsCurrentSession = 0 WHERE Id = 1" -Environment QA

# Insert a record
Invoke-EvaSqlNonQuery -Query "INSERT INTO sessions (Name, StartDate) VALUES ('Test Session', GETDATE())" -Environment QA
```

### Working with Results

```powershell
# Store results in a variable
$committees = Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName FROM Committee WHERE IsActive = 1" -Environment M2-QA

# Display as table
$committees | Format-Table -AutoSize

# Filter results
$committees | Where-Object { $_.CommitteeName -like "*Finance*" }

# Export to CSV
$committees | Export-Csv -Path "committees.csv" -NoTypeInformation
```

### Database Exploration

```powershell
# Check connection and database version
Invoke-EvaSql -Query "SELECT @@VERSION AS SQLVersion, DB_NAME() AS CurrentDatabase" -Environment M2-QA

# List all tables
Invoke-EvaSql -Query "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES ORDER BY TABLE_NAME" -Environment M2-QA

# Find tables by name pattern
Invoke-EvaSql -Query "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%Committee%'" -Environment M2-QA

# Get table schema
Invoke-EvaSql -Query "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Committee' ORDER BY ORDINAL_POSITION" -Environment M2-QA
```

## Common Patterns for AI Assistants

### Pattern 1: Quick Committee Query

```powershell
. c:\Users\mshepherd\p\useful\env-vars.ps1
$env:M2_QA_PASSWORD = $env:SHARED_QA_PASSWORD
Import-Module c:\Users\mshepherd\p\useful\network\EvaSql.psm1 -Force
Invoke-EvaSql -Query "SELECT * FROM Committee WHERE CommitteeID = 466" -Environment M2-QA
```

### Pattern 2: Quick Eva Query

```powershell
. c:\Users\mshepherd\p\useful\env-vars.ps1
Import-Module c:\Users\mshepherd\p\useful\network\EvaSql.psm1 -Force
Invoke-EvaSql -Query "SELECT * FROM sessions WHERE IsCurrentSession = 1" -Environment QA
```

### Pattern 3: Explore Database Schema

```powershell
. c:\Users\mshepherd\p\useful\env-vars.ps1
$env:M2_QA_PASSWORD = $env:SHARED_QA_PASSWORD
Import-Module c:\Users\mshepherd\p\useful\network\EvaSql.psm1 -Force
Invoke-EvaSql -Query "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME" -Environment M2-QA
```

## Parameters

### Invoke-EvaSql Parameters

-   `Query` (required) - SQL SELECT statement
-   `Environment` (optional) - Default is 'QA'
-   `Timeout` (optional) - Query timeout in seconds, default is 30

### Invoke-EvaSqlNonQuery Parameters

-   `Query` (required) - SQL INSERT/UPDATE/DELETE statement
-   `Environment` (optional) - Default is 'QA'
-   `Timeout` (optional) - Query timeout in seconds, default is 30

## Key Differences: Eva vs M2 Databases

| Aspect       | Eva Database                     | M2/Legislature Database                     |
| ------------ | -------------------------------- | ------------------------------------------- |
| Purpose      | Application-specific data        | Shared legislative data                     |
| Environments | QA, DEMO, UAT, Local             | M2-QA, M2-DEMO, M2-UAT, M2-Local            |
| Tables       | Sessions, CommitteeReports, etc. | Committee, Member, Session, etc.            |
| Password Var | `EVA_QA_PASSWORD`                | `M2_QA_PASSWORD` (use `SHARED_QA_PASSWORD`) |

## Troubleshooting

### "Login failed for user" Error

-   Make sure you've sourced `env-vars.ps1`
-   For M2 environments, ensure `$env:M2_QA_PASSWORD` is set to `$env:SHARED_QA_PASSWORD`
-   Check that the environment variable name matches the environment you're using

### "Cannot open database" Error

-   Verify you're using the correct environment name
-   Check that you have network access to the database server
-   Confirm VPN is connected if accessing remote servers

### Module Not Found

-   Use the full path: `Import-Module c:\Users\mshepherd\p\useful\network\EvaSql.psm1 -Force`
-   The `-Force` flag ensures the module is reloaded even if already imported

## Module Location

The module file is located at:

```
c:\Users\mshepherd\p\useful\network\EvaSql.psm1
```

Environment variables are defined in:

```
c:\Users\mshepherd\p\useful\env-vars.ps1
```

## Additional Resources

-   See `.skills/eva-qa-database/` for Eva-specific examples
-   See `.skills/legislature-qa-database/` for Legislature/M2-specific examples
-   See `examples.ps1` in each skills folder for more query patterns
