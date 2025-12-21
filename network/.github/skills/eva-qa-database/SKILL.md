---
name: eva-qa-database
description: Query and analyze the Eva QA database using PowerShell functions. Use when working with Eva sessions, committee reports, meeting notices, or any Eva application data in the QA environment.
metadata:
    author: michigan-senate
    version: "1.0"
    environments: "QA, DEMO, UAT, Local"
---

# Eva QA Database Skill

This skill provides access to the Eva application database in the QA environment using PowerShell functions.

## Available Functions

### Query Data (SELECT)

Use `Invoke-EvaSql` for SELECT queries that return data:

```powershell
Invoke-EvaSql -Query "SELECT * FROM sessions" -Environment QA
```

**Security Note:** `Invoke-EvaSql` is restricted to SELECT queries only. UPDATE, DELETE, DROP, and other dangerous operations are blocked for safety.

### Insert Data (INSERT)

Use `Invoke-EvaSqlNonQuery` for inserting new records:

```powershell
Invoke-EvaSqlNonQuery -Query "INSERT INTO sessions (Name, StartDate) VALUES ('Test Session', GETDATE())" -Environment QA
```

**Security Note:** `Invoke-EvaSqlNonQuery` is restricted to INSERT queries only. UPDATE and DELETE operations are blocked to prevent accidental data modification.

## Environment Options

-   `QA` (default) - Eva_QA database on tvmwsqls01
-   `DEMO` - Eva_DEMO database on uvmwsqls01
-   `UAT` - Eva_UAT database on uvmwsqls01
-   `Local` - Local development database

## Common Tables

See [DATABASE-SCHEMA.md](references/DATABASE-SCHEMA.md) for complete schema information.

### Core Tables

-   `sessions` - Legislative sessions
-   `CommitteeReports` - Committee report data
-   `CommitteeMeetingNotices` - Meeting notices
-   `CommitteeMeetingAgendaData` - Agenda items
-   `CalendarCommitteeEdits` - Calendar edits

## Usage Examples

See [COMMON-QUERIES.md](references/COMMON-QUERIES.md) for frequently used queries.

### Get Current Session

```powershell
Invoke-EvaSql -Query "SELECT * FROM sessions WHERE IsCurrentSession = 1" -Environment QA
```

### Get Recent Committee Reports

```powershell
Invoke-EvaSql -Query "SELECT TOP 10 * FROM CommitteeReports ORDER BY Created DESC" -Environment QA
```

### Find Tables by Pattern

```powershell
Invoke-EvaSql -Query "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%pattern%'" -Environment QA
```

## Best Practices

1. **Always specify the environment** - Even though QA is default, be explicit
2. **Use TOP for exploration** - Limit results when exploring tables
3. **Check schema first** - Query INFORMATION_SCHEMA to understand table structure
4. **Handle errors** - The functions automatically display SQL errors
5. **Use transactions carefully** - For updates, verify with SELECT first

## Connection Details

Connection strings are managed in the EvaSql.psm1 module. See [CONNECTION-STRINGS.md](references/CONNECTION-STRINGS.md) for details.

## Troubleshooting

**Error: "Invalid object name"**

-   Table name might be wrong or not exist
-   Query INFORMATION_SCHEMA.TABLES to find correct name

**Error: "Invalid column name"**

-   Column doesn't exist in table
-   Query INFORMATION_SCHEMA.COLUMNS to see available columns

**Connection timeout**

-   VPN connection might be down
-   Server might be unreachable
