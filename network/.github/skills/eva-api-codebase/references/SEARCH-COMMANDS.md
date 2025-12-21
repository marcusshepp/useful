# EvaAPI Codebase Search Commands

## Basic Navigation

### List All Files in a Directory

```powershell
cd C:\Users\mshepherd\p\leb\EvaAPI

# List all C# files in Data\Models
Get-ChildItem -Path Data\Models -Recurse -Filter *.cs

# List just the names
Get-ChildItem -Path Data\Models -Recurse -Filter *.cs | Select-Object Name

# List with full paths
Get-ChildItem -Path Data\Models -Recurse -Filter *.cs | Select-Object FullName
```

## Finding Entity Models

### Find Model by Name

```powershell
cd C:\Users\mshepherd\p\leb\EvaAPI

# Find specific model
Get-ChildItem -Path Data\Models -Recurse -Filter "CommitteeReport.cs"

# Find all models matching pattern
Get-ChildItem -Path Data\Models -Recurse -Filter "*CommitteeReport*.cs"

# Find all models in a domain
Get-ChildItem -Path Data\Models\Committees -Recurse -Filter *.cs
```

### List All Entity Models

```powershell
# Get all model files organized by folder
Get-ChildItem -Path Data\Models -Recurse -Filter *.cs |
    Select-Object Name, Directory |
    Format-Table -AutoSize
```

## Searching Code Content

### Search for Text in Files

```powershell
cd C:\Users\mshepherd\p\leb\EvaAPI

# Find all files containing specific text
Select-String -Path **\*.cs -Pattern "CommitteeReportCommitteeActions"

# Search in specific directory
Select-String -Path Services\**\*.cs -Pattern "GetAvailableActions"

# Search excluding migrations
Get-ChildItem -Recurse -Filter *.cs -Exclude *Migration*,*Designer* |
    Select-String -Pattern "CommitteeReportCommitteeActions" -SimpleMatch
```

### Find DbSet Declarations

```powershell
# Find all DbSets in EvaDbContext
Select-String -Path Data\EvaDbContext.cs -Pattern "DbSet<"

# Show with line numbers
Select-String -Path Data\EvaDbContext.cs -Pattern "DbSet<" |
    Select-Object LineNumber, Line
```

### Find Class Definitions

```powershell
# Find where a class is defined
Select-String -Path Data\Models\**\*.cs -Pattern "class CommitteeReport "

# Find all classes in a file
Select-String -Path Data\Models\Committees\CommitteeReports\CommitteeReport.cs -Pattern "class "
```

## Finding Services

### Find Service by Name

```powershell
cd C:\Users\mshepherd\p\leb\EvaAPI

# Find specific service
Get-ChildItem -Path Services -Recurse -Filter "*CommitteeReportService.cs"

# Find all services in a domain
Get-ChildItem -Path Services\CommitteeManagement -Recurse -Filter *.cs
```

### Find Where Service is Used

```powershell
# Find service interface implementations
Select-String -Path Services\**\*.cs -Pattern "ICommitteeReportService"

# Find service constructor injections
Select-String -Path **\*.cs -Pattern "ICommitteeReportService" -Exclude *Migration*
```

## Finding Controllers

### List All Controllers

```powershell
Get-ChildItem -Path Controllers -Filter *.cs
```

### Find Specific Controller

```powershell
Get-ChildItem -Path Controllers -Filter "*CommitteeReport*.cs"
```

### Find API Endpoints in Controller

```powershell
# Find all HTTP method attributes
Select-String -Path Controllers\CommitteeReportsController.cs -Pattern "\[Http"

# Find GET endpoints
Select-String -Path Controllers\CommitteeReportsController.cs -Pattern "\[HttpGet"

# Find POST endpoints
Select-String -Path Controllers\CommitteeReportsController.cs -Pattern "\[HttpPost"
```

## Finding Migrations

### List All Migrations

```powershell
Get-ChildItem -Path Migrations -Filter *.cs -Exclude *Designer*,*Snapshot* |
    Sort-Object Name |
    Select-Object Name
```

### Find Migrations by Date

```powershell
# Migrations from 2024
Get-ChildItem -Path Migrations -Filter "2024*.cs" -Exclude *Designer*

# Recent migrations (2025)
Get-ChildItem -Path Migrations -Filter "2025*.cs" -Exclude *Designer*
```

### Find Migrations for a Table

```powershell
# Find migrations that reference a table
Select-String -Path Migrations\*.cs -Pattern "CommitteeReportCommitteeActions" |
    Select-Object Filename, LineNumber, Line
```

### Find Migration by Ticket Number

```powershell
# Find migration for ticket 2968
Get-ChildItem -Path Migrations -Filter "*2968*.cs" -Exclude *Designer*
```

## Finding DTOs

### Find DTOs by Feature

```powershell
cd C:\Users\mshepherd\p\leb\EvaAPI

# Find all CommitteeReport DTOs
Get-ChildItem -Path Dtos -Recurse -Filter "*CommitteeReport*.cs"

# Find DTOs in specific domain
Get-ChildItem -Path Dtos\CommitteeReports -Filter *.cs
```

## Advanced Searches

### Find References to a Class

```powershell
# Find all files using CommitteeReport class
Get-ChildItem -Recurse -Filter *.cs -Exclude *Migration*,*Designer* |
    Select-String -Pattern "CommitteeReport" |
    Group-Object Filename |
    Select-Object Name, Count |
    Sort-Object Count -Descending
```

### Find Enum Definitions

```powershell
# Find all enums
Select-String -Path Data\Models\**\*.cs -Pattern "enum "

# Find specific enum
Select-String -Path **\*.cs -Pattern "enum COMMITTEE_ACTION_IDS"
```

### Find Configuration Classes

```powershell
# Find EntityTypeConfiguration classes
Select-String -Path Data\Models\**\*.cs -Pattern "IEntityTypeConfiguration"
```

### Find Interfaces

```powershell
# Find all interfaces
Get-ChildItem -Path Interfaces -Filter *.cs

# Find interface definitions
Select-String -Path Interfaces\*.cs -Pattern "interface "
```

## Reading File Contents

### Read Specific File

```powershell
cd C:\Users\mshepherd\p\leb\EvaAPI

# Read entire file
Get-Content "Data\Models\Committees\CommitteeReports\CommitteeReport.cs"

# Read first 20 lines
Get-Content "Data\Models\Committees\CommitteeReports\CommitteeReport.cs" |
    Select-Object -First 20

# Read specific line range
Get-Content "Data\Models\Committees\CommitteeReports\CommitteeReport.cs" |
    Select-Object -Skip 10 -First 20
```

### Read with Line Numbers

```powershell
Get-Content "Data\EvaDbContext.cs" |
    ForEach-Object { $i = 1 } { "$i`: $_"; $i++ } |
    Select-Object -First 50
```

## Combining Searches

### Find Entity, Service, and Controller

```powershell
cd C:\Users\mshepherd\p\leb\EvaAPI

Write-Host "=== Entity Model ===" -ForegroundColor Cyan
Get-ChildItem -Path Data\Models -Recurse -Filter "*CommitteeReport.cs"

Write-Host "`n=== Services ===" -ForegroundColor Cyan
Get-ChildItem -Path Services -Recurse -Filter "*CommitteeReport*.cs"

Write-Host "`n=== Controllers ===" -ForegroundColor Cyan
Get-ChildItem -Path Controllers -Filter "*CommitteeReport*.cs"

Write-Host "`n=== DTOs ===" -ForegroundColor Cyan
Get-ChildItem -Path Dtos -Recurse -Filter "*CommitteeReport*.cs"
```

### Map Entity to Database Table

```powershell
# Find entity
$entityFile = Get-ChildItem -Path Data\Models -Recurse -Filter "CommitteeReport.cs" |
    Select-Object -First 1

# Find DbSet in context
Select-String -Path Data\EvaDbContext.cs -Pattern "DbSet<CommitteeReport>"

# Find in migrations
Select-String -Path Migrations\*.cs -Pattern "CommitteeReports" |
    Select-Object -First 5
```

## Export Results

### Export File List to CSV

```powershell
Get-ChildItem -Path Data\Models -Recurse -Filter *.cs |
    Select-Object Name, Directory, Length, LastWriteTime |
    Export-Csv -Path "C:\Users\mshepherd\p\network\model_files.csv" -NoTypeInformation
```

### Export Search Results

```powershell
Select-String -Path Services\**\*.cs -Pattern "CommitteeReport" |
    Select-Object Filename, LineNumber, Line |
    Export-Csv -Path "C:\Users\mshepherd\p\network\committee_report_usage.csv" -NoTypeInformation
```

## Tips

1. **Use -Recurse** for searching subdirectories
2. **Use -Filter** for file patterns (faster than -Include)
3. **Use Select-String** for content search
4. **Use -Exclude** to skip migrations and designers
5. **Pipe to Select-Object** to format output
6. **Use Get-Content** to read file contents
7. **Combine commands** with pipelines for complex searches
