# Legislature (M2) Database Schema Reference

## Committee Tables

### Committee

Main committee table with committee definitions.

**Key Columns:**

-   `CommitteeID` (int) - Primary key
-   `CommitteeTypeID` (int) - Foreign key to CommitteeType
-   `CommitteeParentID` (int, nullable) - Parent committee for subcommittees
-   `SessionID` (int) - Legislative session (16 = current)
-   `ChamberID` (int) - 1 = House, 2 = Senate
-   `CommitteeName` (nvarchar) - Full committee name
-   `IntegrationName` (nvarchar) - Name for LSB integration
-   `NameCode` (nvarchar) - Short code
-   `MeetingDay` (nvarchar, nullable)
-   `MeetingTime` (nvarchar, nullable)
-   `LocationID` (int, nullable)
-   `ChairID` (int, nullable)
-   `ClerkID` (int, nullable)
-   `CommitteePhone` (nvarchar, nullable)
-   `ListServID` (int, nullable)
-   `Website` (nvarchar, nullable)
-   `IsPublic` (bit)
-   `IsAfterSession` (bit)
-   `IsActive` (bit)
-   `IsFiscal` (bit)
-   `DateAdded` (datetime)
-   `LastModified` (datetime)
-   `LastModifiedBy` (nvarchar)

**Example Record:**

```
CommitteeID: 466
CommitteeName: Marcus Committee Check Test
SessionID: 16
ChamberID: 2
IsActive: True
DateAdded: 2025-12-19 10:26:14
```

**Common Queries:**

```sql
-- Get active committees
SELECT * FROM Committee WHERE IsActive = 1

-- Get Senate committees for current session
SELECT * FROM Committee WHERE ChamberID = 2 AND SessionID = 16

-- Get latest committee
SELECT TOP 1 * FROM Committee ORDER BY CommitteeID DESC
```

### CommitteeMeeting

Committee meeting records.

**Key Columns:**

-   Meeting scheduling and location information
-   Links to Committee table

### CommitteeMember

Committee membership assignments.

**Key Columns:**

-   Links members to committees
-   Includes role assignments

### CommitteeMeetingAgendaItem

Individual agenda items for committee meetings.

### CommitteeMeetingAttendanceRecord

Tracks attendance at committee meetings.

### CommitteeRole

Lookup table for committee roles (Chair, Vice Chair, Member, etc.).

### CommitteeType

Lookup table for committee types (Standing, Select, Joint, etc.).

**Key Columns:**

-   `CommitteeTypeID` (int) - Primary key
-   Type classification information

### CommitteeMeetingAction

Actions taken during committee meetings.

### CommitteeMeetingActionType

Lookup table for action types.

### CommitteeMeetingCommittee

Junction table for committee meetings.

### CommitteeMeetingResource

Resources attached to committee meetings.

### CommitteeLocation

Lookup table for meeting locations.

## Finding Schema Information

### List All Committee Tables

```sql
SELECT TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE '%Committee%'
ORDER BY TABLE_NAME
```

### Get Committee Table Columns

```sql
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Committee'
ORDER BY ORDINAL_POSITION
```

### Find Foreign Key Relationships

```sql
SELECT
    OBJECT_NAME(fk.parent_object_id) AS TableName,
    COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS ColumnName,
    OBJECT_NAME(fk.referenced_object_id) AS ReferencedTable,
    COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS ReferencedColumn
FROM sys.foreign_keys fk
INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
WHERE OBJECT_NAME(fk.parent_object_id) = 'Committee'
```

## Important Notes

-   **Singular table names**: `Committee` not `Committees`
-   **ID suffix pattern**: Most tables use `TableNameID` for primary keys
-   **SessionID 16**: Current session in QA environment
-   **ChamberID**: 1 = House, 2 = Senate
-   **Date fields**: `DateAdded`, `LastModified` (not `Created`/`Modified`)
-   **Active records**: Use `IsActive = 1` to filter current records
-   Database uses SQL Server 2019
