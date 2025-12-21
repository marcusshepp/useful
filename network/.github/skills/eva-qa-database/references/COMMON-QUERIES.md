# Common Eva Database Queries

## Session Queries

### Get Current Session

```powershell
Invoke-EvaSql -Query "SELECT * FROM sessions WHERE IsCurrentSession = 1" -Environment QA
```

### Get All Sessions Ordered by Date

```powershell
Invoke-EvaSql -Query "SELECT Id, Name, StartDate, EndDate, IsCurrentSession FROM sessions ORDER BY StartDate DESC" -Environment QA
```

### Get Sessions for Specific Year

```powershell
Invoke-EvaSql -Query "SELECT * FROM sessions WHERE Name LIKE '%2025%'" -Environment QA
```

## Committee Reports

### Get Recent Reports

```powershell
Invoke-EvaSql -Query "SELECT TOP 10 * FROM CommitteeReports ORDER BY Created DESC" -Environment QA
```

### Get Reports by User

```powershell
Invoke-EvaSql -Query "SELECT * FROM CommitteeReports WHERE CreatedBy = 'username' ORDER BY Created DESC" -Environment QA
```

## Schema Discovery

### List All Tables

```powershell
Invoke-EvaSql -Query "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME" -Environment QA
```

### Find Tables by Keyword

```powershell
Invoke-EvaSql -Query "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%Committee%'" -Environment QA
```

### Get Table Schema

```powershell
Invoke-EvaSql -Query "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'sessions' ORDER BY ORDINAL_POSITION" -Environment QA
```

### Count Records in Table

```powershell
Invoke-EvaSql -Query "SELECT COUNT(*) AS RecordCount FROM sessions" -Environment QA
```

## Database Information

### Get SQL Server Version

```powershell
Invoke-EvaSql -Query "SELECT @@VERSION AS SQLVersion" -Environment QA
```

### Get Current Database Name

```powershell
Invoke-EvaSql -Query "SELECT DB_NAME() AS CurrentDatabase" -Environment QA
```

### List All Databases (if permissions allow)

```powershell
Invoke-EvaSql -Query "SELECT name FROM sys.databases ORDER BY name" -Environment QA
```

## Data Modification

### Update Record (Use with Caution)

```powershell
# First verify the current value
Invoke-EvaSql -Query "SELECT IsCurrentSession FROM sessions WHERE Id = 3" -Environment QA

# Then update
Invoke-EvaSqlNonQuery -Query "UPDATE sessions SET IsCurrentSession = 1 WHERE Id = 3" -Environment QA

# Verify the change
Invoke-EvaSql -Query "SELECT IsCurrentSession FROM sessions WHERE Id = 3" -Environment QA
```

## Tips

1. **Always use TOP when exploring** - Prevents accidentally returning thousands of rows
2. **Order results** - Makes data easier to understand
3. **Select specific columns** - Instead of `SELECT *` when you know what you need
4. **Use WHERE clauses** - Filter data at the database level
5. **Verify before updating** - Always SELECT first to see what you're changing
