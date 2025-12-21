# Common Legislature Database Queries

## Committee Queries

### Get All Active Committees

```powershell
Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName, SessionID, ChamberID FROM Committee WHERE IsActive = 1 ORDER BY CommitteeName" -Environment M2-QA
```

### Get Latest Created Committee

```powershell
Invoke-EvaSql -Query "SELECT TOP 1 CommitteeID, CommitteeName, DateAdded, LastModifiedBy FROM Committee ORDER BY DateAdded DESC" -Environment M2-QA
```

### Get Committee by ID

```powershell
Invoke-EvaSql -Query "SELECT * FROM Committee WHERE CommitteeID = 466" -Environment M2-QA
```

### Find Committee by Name

```powershell
Invoke-EvaSql -Query "SELECT * FROM Committee WHERE CommitteeName LIKE '%Finance%'" -Environment M2-QA
```

### Get Senate Committees for Current Session

```powershell
Invoke-EvaSql -Query "SELECT * FROM Committee WHERE ChamberID = 2 AND SessionID = 16 AND IsActive = 1" -Environment M2-QA
```

### Get All Committees by Type

```powershell
Invoke-EvaSql -Query "
SELECT c.CommitteeID, c.CommitteeName, ct.CommitteeTypeID
FROM Committee c
LEFT JOIN CommitteeType ct ON c.CommitteeTypeID = ct.CommitteeTypeID
WHERE c.IsActive = 1
ORDER BY c.CommitteeName
" -Environment M2-QA
```

## Committee Meeting Queries

### Get Recent Committee Meetings

```powershell
Invoke-EvaSql -Query "SELECT TOP 10 * FROM CommitteeMeeting ORDER BY MeetingID DESC" -Environment M2-QA
```

### Get Meetings for Specific Committee

```powershell
Invoke-EvaSql -Query "SELECT * FROM CommitteeMeeting WHERE CommitteeID = 466" -Environment M2-QA
```

## Committee Membership Queries

### Get Members of a Committee

```powershell
Invoke-EvaSql -Query "SELECT * FROM CommitteeMember WHERE CommitteeID = 466" -Environment M2-QA
```

## Lookup Table Queries

### Get All Committee Types

```powershell
Invoke-EvaSql -Query "SELECT * FROM CommitteeType ORDER BY CommitteeTypeID" -Environment M2-QA
```

### Get All Committee Roles

```powershell
Invoke-EvaSql -Query "SELECT * FROM CommitteeRole ORDER BY CommitteeRoleID" -Environment M2-QA
```

## Schema Discovery

### List All Tables

```powershell
Invoke-EvaSql -Query "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME" -Environment M2-QA
```

### Find All Committee-Related Tables

```powershell
Invoke-EvaSql -Query "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%Committee%' ORDER BY TABLE_SCHEMA, TABLE_NAME" -Environment M2-QA
```

### Get Committee Table Schema

```powershell
Invoke-EvaSql -Query "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Committee' ORDER BY ORDINAL_POSITION" -Environment M2-QA
```

### Count Records in Committee Table

```powershell
Invoke-EvaSql -Query "SELECT COUNT(*) AS TotalCommittees FROM Committee" -Environment M2-QA
```

### Count Active vs Inactive Committees

```powershell
Invoke-EvaSql -Query "SELECT IsActive, COUNT(*) AS CommitteeCount FROM Committee GROUP BY IsActive" -Environment M2-QA
```

## Database Information

### Get SQL Server Version

```powershell
Invoke-EvaSql -Query "SELECT @@VERSION AS SQLVersion" -Environment M2-QA
```

### Get Current Database Name

```powershell
Invoke-EvaSql -Query "SELECT DB_NAME() AS CurrentDatabase" -Environment M2-QA
```

## Data Analysis

### Committees by Chamber

```powershell
Invoke-EvaSql -Query "
SELECT
    ChamberID,
    CASE ChamberID
        WHEN 1 THEN 'House'
        WHEN 2 THEN 'Senate'
        ELSE 'Unknown'
    END AS Chamber,
    COUNT(*) AS CommitteeCount
FROM Committee
WHERE IsActive = 1
GROUP BY ChamberID
" -Environment M2-QA
```

### Committees by Session

```powershell
Invoke-EvaSql -Query "SELECT SessionID, COUNT(*) AS CommitteeCount FROM Committee GROUP BY SessionID ORDER BY SessionID DESC" -Environment M2-QA
```

### Recently Modified Committees

```powershell
Invoke-EvaSql -Query "SELECT TOP 10 CommitteeID, CommitteeName, LastModified, LastModifiedBy FROM Committee ORDER BY LastModified DESC" -Environment M2-QA
```

## Safe Update Example

### Update Committee (Use with Caution)

```powershell
# 1. Check current value
Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName, IsActive FROM Committee WHERE CommitteeID = 466" -Environment M2-QA

# 2. Update
Invoke-EvaSqlNonQuery -Query "UPDATE Committee SET IsActive = 1 WHERE CommitteeID = 466" -Environment M2-QA

# 3. Verify change
Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName, IsActive FROM Committee WHERE CommitteeID = 466" -Environment M2-QA
```

## Tips

1. **Always filter by IsActive = 1** for current records
2. **SessionID 16** is the current session in QA
3. **ChamberID 2** is Senate, **1** is House
4. **Use CommitteeID** not just "ID" for queries
5. **Table names are singular** - Committee, not Committees
6. **Date columns** use DateAdded and LastModified
