---
name: legislature-qa-database
description: Query and analyze the Legislature (M2) QA database using PowerShell functions. Use when working with committees, committee meetings, bills, legislators, or any Legislature/M2 application data in the QA environment.
metadata:
    author: michigan-senate
    version: "1.0"
    environments: "M2-QA, M2-DEMO, M2-UAT, M2-Local"
---

# Legislature (M2) QA Database Skill

This skill provides access to the Legislature database (also called M2) in the QA environment using PowerShell functions.

## Available Functions

### Query Data (SELECT)

Use `Invoke-EvaSql` with M2 environments for SELECT queries:

```powershell
Invoke-EvaSql -Query "SELECT * FROM Committee" -Environment M2-QA
```

**Security Note:** `Invoke-EvaSql` is restricted to SELECT queries only. UPDATE, DELETE, DROP, and other dangerous operations are blocked for safety.

### Insert Data (INSERT)

Use `Invoke-EvaSqlNonQuery` for inserting new records:

```powershell
Invoke-EvaSqlNonQuery -Query "INSERT INTO Committee (CommitteeName, SessionID) VALUES ('Test Committee', 16)" -Environment M2-QA
```

**Security Note:** `Invoke-EvaSqlNonQuery` is restricted to INSERT queries only. UPDATE and DELETE operations are blocked to prevent accidental data modification.

## Environment Options

-   `M2-QA` - Legislature database on tvmwsqls01 (most common)
-   `M2-DEMO` - Legislature database on MLSQL-QA.lsb.legislature.mi.gov
-   `M2-UAT` - Legislature database on MLSQL-SUP.lsb.legislature.mi.gov
-   `M2-Local` - Local development Legislature database

## Common Tables

See [DATABASE-SCHEMA.md](references/DATABASE-SCHEMA.md) for complete schema information.

### Core Tables

-   `Committee` - Committee definitions
-   `CommitteeMeeting` - Committee meeting records
-   `CommitteeMember` - Committee membership
-   `CommitteeMeetingAgendaItem` - Agenda items
-   `CommitteeMeetingAttendanceRecord` - Attendance tracking
-   `CommitteeRole` - Committee role definitions
-   `CommitteeType` - Committee type classifications

## Usage Examples

See [COMMON-QUERIES.md](references/COMMON-QUERIES.md) for frequently used queries.

### Get Active Committees

```powershell
Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName, SessionID FROM Committee WHERE IsActive = 1" -Environment M2-QA
```

### Get Latest Committee

```powershell
Invoke-EvaSql -Query "SELECT TOP 1 * FROM Committee ORDER BY CommitteeID DESC" -Environment M2-QA
```

### Find Committee by Name

```powershell
Invoke-EvaSql -Query "SELECT * FROM Committee WHERE CommitteeName LIKE '%Finance%'" -Environment M2-QA
```

## Best Practices

1. **Use M2-QA environment** - This is the QA environment for Legislature data
2. **Committee vs Committees** - Table is singular "Committee" not "Committees"
3. **SessionID is important** - Many tables link to SessionID (16 = current)
4. **ChamberID** - 1 = House, 2 = Senate
5. **Check IsActive** - Many tables have IsActive flag for filtering

## Connection Details

Connection strings are managed in the EvaSql.psm1 module. See [CONNECTION-STRINGS.md](references/CONNECTION-STRINGS.md) for details.

## Key Differences from Eva Database

-   Legislature database has **Committee** (singular) not "Committees"
-   Uses **CommitteeID** as primary key (not just "Id")
-   Has more normalized structure with lookup tables
-   Contains LSB (Legislative Service Bureau) integration data
-   SessionID and ChamberID are critical foreign keys

## Troubleshooting

**Error: "Invalid object name 'Committees'"**

-   Table name is singular: use `Committee` not `Committees`

**Error: "Invalid column name 'Name'"**

-   Column is `CommitteeName` not `Name`

**Error: "Invalid column name 'CreatedDate'"**

-   Column is `DateAdded` not `CreatedDate`
