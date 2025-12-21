---
name: eva-api-codebase
description: Navigate and understand the EvaAPI codebase structure. Use when searching for models, services, controllers, migrations, or any code related to Eva database entities. Helps locate where specific features are implemented.
metadata:
    author: michigan-senate
    version: "1.0"
    codebase: "C:/Users/mshepherd/p/leb/EvaAPI"
---

# EvaAPI Codebase Navigation Skill

This skill helps you navigate the EvaAPI .NET Core application codebase located at `C:\Users\mshepherd\p\leb\EvaAPI`.

## Project Structure

### Core Directories

```
C:\Users\mshepherd\p\leb\EvaAPI\
├── Data\                           # Database context and entity models
│   ├── EvaDbContext.cs            # Main DbContext with all DbSets
│   └── Models\                    # Entity models organized by domain
│       ├── Committees\            # Committee-related entities
│       │   └── CommitteeReports\  # Committee report entities
│       ├── Calendar\              # Calendar entities
│       ├── Journal\               # Journal entities
│       └── Sessions\              # Session entities
│
├── Services\                      # Business logic services
│   ├── CommitteeManagement\       # Committee-related services
│   │   └── CommitteeReports\      # Committee report services
│   ├── CalendarManagement\        # Calendar services
│   └── JournalManagement\         # Journal services
│
├── Controllers\                   # API endpoints
│   ├── CommitteeReportsController.cs
│   ├── SessionsController.cs
│   └── CalendarController.cs
│
├── Dtos\                          # Data Transfer Objects
│   ├── CommitteeReports\          # DTOs for committee reports
│   └── Calendar\                  # DTOs for calendar
│
├── Migrations\                    # EF Core database migrations
│   └── EvaDbContextModelSnapshot.cs  # Current DB schema snapshot
│
├── Interfaces\                    # Service interfaces
├── Utilities\                     # Helper classes
├── Extensions\                    # Extension methods
├── Filters\                       # API filters
├── Mapping\                       # AutoMapper profiles
└── Settings\                      # Configuration classes
```

## Finding Code by Feature

### Database Entities (Models)

**Location**: `Data\Models\[Domain]\`

**Examples**:

-   `Data\Models\Committees\CommitteeReports\CommitteeReport.cs`
-   `Data\Models\Committees\CommitteeReports\CommitteeReportCommitteeAction.cs`
-   `Data\Models\Sessions\Session.cs`

**How to find**:

```powershell
# Find entity by name
cd C:\Users\mshepherd\p\leb\EvaAPI
Get-ChildItem -Path Data\Models -Recurse -Filter "*CommitteeReport*.cs"

# Find all models in a domain
Get-ChildItem -Path Data\Models\Committees -Recurse -Filter *.cs
```

### Database Context

**Location**: `Data\EvaDbContext.cs`

Contains all `DbSet<T>` declarations that map to database tables.

**Example DbSets**:

-   `DbSet<CommitteeReport> CommitteeReports`
-   `DbSet<CommitteeReportCommitteeAction> CommitteeReportCommitteeActions`
-   `DbSet<Session> Sessions`

### Services (Business Logic)

**Location**: `Services\[Domain]\`

**Examples**:

-   `Services\CommitteeManagement\CommitteeReports\CommitteeReportAgendaItemService.cs`
-   `Services\CommitteeManagement\CommitteeReports\CommitteeReportService.cs`
-   `Services\SessionManagement\SessionService.cs`

**How to find**:

```powershell
# Find service by feature
Get-ChildItem -Path Services -Recurse -Filter "*CommitteeReport*.cs"

# Search for specific method usage
Select-String -Path Services\**\*.cs -Pattern "GetAvailableActions"
```

### Controllers (API Endpoints)

**Location**: `Controllers\`

**Examples**:

-   `Controllers\CommitteeReportsController.cs`
-   `Controllers\SessionsController.cs`

**How to find**:

```powershell
# List all controllers
Get-ChildItem -Path Controllers -Filter *.cs

# Find controller by feature
Get-ChildItem -Path Controllers -Filter "*CommitteeReport*.cs"
```

### Migrations

**Location**: `Migrations\`

**Pattern**: `{Timestamp}_{Description}.cs`

**Examples**:

-   `Migrations\20240607134553_2968__CommitteeReportsRewrite.cs`
-   `Migrations\20240820204656_3881_committee-report-additional-actions.cs`

**Current Schema**: `Migrations\EvaDbContextModelSnapshot.cs`

**How to find migrations for a table**:

```powershell
# Find migrations that reference a specific table
Select-String -Path Migrations\*.cs -Pattern "CommitteeReportCommitteeActions" | Select-Object -First 5
```

## Common Search Patterns

### Find where a table is used

```powershell
cd C:\Users\mshepherd\p\leb\EvaAPI

# Search all C# files (excluding migrations)
Get-ChildItem -Recurse -Filter *.cs -Exclude *Migration*,*Designer* |
    Select-String -Pattern "CommitteeReportCommitteeActions" -SimpleMatch
```

### Find entity model and its usage

```powershell
# 1. Find the entity model
Get-ChildItem -Path Data\Models -Recurse -Filter "*CommitteeReport*.cs"

# 2. Find services using it
Get-ChildItem -Path Services -Recurse -Filter *.cs |
    Select-String -Pattern "CommitteeReport"

# 3. Find controllers using it
Get-ChildItem -Path Controllers -Filter *.cs |
    Select-String -Pattern "CommitteeReport"
```

### Find DTOs for a feature

```powershell
Get-ChildItem -Path Dtos -Recurse -Filter "*CommitteeReport*.cs"
```

### Search for specific code patterns

```powershell
# Find all DbSet declarations
Select-String -Path Data\EvaDbContext.cs -Pattern "DbSet<"

# Find all API endpoints for a feature
Select-String -Path Controllers\CommitteeReportsController.cs -Pattern "\[Http"
```

## Entity Naming Conventions

### Database Tables

-   Plural: `CommitteeReports`, `CommitteeReportActions`, `Sessions`
-   Snake_case in old tables, PascalCase in newer tables

### C# Entities

-   Singular class name: `CommitteeReport`, `CommitteeReportAction`, `Session`
-   File matches class name: `CommitteeReport.cs`

### DbSet Properties

-   Plural: `CommitteeReports`, `CommitteeReportActions`
-   Declared in `EvaDbContext.cs`

## Key Files

### Main Entry Points

-   `Program.cs` - Application startup and configuration
-   `appsettings.json` - Production configuration
-   `appsettings.development.json` - Development configuration (has connection strings)

### Database

-   `Data\EvaDbContext.cs` - Database context with all tables
-   `Migrations\EvaDbContextModelSnapshot.cs` - Current complete schema

### Configuration

-   `Settings\JwtSettings.cs` - JWT authentication settings
-   `Settings\EmailSettings.cs` - Email configuration

## Tips for Code Navigation

1. **Start with the entity model** - Find in `Data\Models\` to understand the structure
2. **Check EvaDbContext.cs** - Verify the DbSet exists and see navigation properties
3. **Find the service** - Look in `Services\` for business logic
4. **Find the controller** - Look in `Controllers\` for API endpoints
5. **Check migrations** - See how the table evolved over time

## Common File Locations by Feature

### Committee Reports

-   **Models**: `Data\Models\Committees\CommitteeReports\`
-   **Services**: `Services\CommitteeManagement\CommitteeReports\`
-   **Controllers**: `Controllers\CommitteeReportsController.cs`
-   **DTOs**: `Dtos\CommitteeReports\`

### Sessions

-   **Models**: `Data\Models\Sessions\`
-   **Services**: `Services\SessionManagement\`
-   **Controllers**: `Controllers\SessionsController.cs`

### Calendar

-   **Models**: `Data\Models\Calendar\`
-   **Services**: `Services\CalendarManagement\`
-   **Controllers**: `Controllers\CalendarController.cs`

## Useful PowerShell Commands

See [SEARCH-COMMANDS.md](references/SEARCH-COMMANDS.md) for comprehensive search examples.
