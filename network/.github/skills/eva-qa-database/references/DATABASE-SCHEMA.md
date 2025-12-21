# Eva Database Schema Reference

## Core Tables

### sessions

Legislative session information.

**Key Columns:**

-   `Id` (int) - Primary key
-   `Name` (nvarchar) - Session name (e.g., "2025")
-   `StartDate` (datetime)
-   `EndDate` (datetime)
-   `IsRegularSession` (bit)
-   `IsCurrentSession` (bit)
-   `LsbId` (int) - LSB identifier
-   `VotingSessionCode` (nvarchar)
-   `Created` (datetime)
-   `CreatedBy` (nvarchar)
-   `Modified` (datetime)
-   `ModifiedBy` (nvarchar)

**Common Query:**

```sql
SELECT * FROM sessions WHERE IsCurrentSession = 1
```

## Committee-Related Tables

### CommitteeReports

Committee report records.

**Key Columns:**

-   `Id` (int) - Primary key
-   `Created` (datetime)
-   `CreatedBy` (nvarchar)
-   `Modified` (datetime)
-   `ModifiedBy` (nvarchar)

### CommitteeMeetingNotices

Meeting notice documents.

### CommitteeMeetingAgendaData

Agenda items for committee meetings.

### CommitteeClerks

Committee clerk assignments.

### CommitteeLetterhead

Letterhead templates for committees.

### CommitteeLocations

Meeting location information.

### CalendarCommitteeEdits

Calendar editing records.

## Finding Schema Information

### List All Tables

```sql
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME
```

### Get Column Information

```sql
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'sessions'
ORDER BY ORDINAL_POSITION
```

### Find Tables by Pattern

```sql
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE '%Committee%'
ORDER BY TABLE_NAME
```

## Notes

-   Most tables follow the pattern: `Id`, `Created`, `CreatedBy`, `Modified`, `ModifiedBy`
-   DateTime fields are stored in SQL Server datetime format
-   Use `TrustServerCertificate=True` in connection strings
-   Database uses SQL Server 2019
