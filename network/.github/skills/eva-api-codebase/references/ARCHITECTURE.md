# EvaAPI Architecture Overview

## Technology Stack

-   **Framework**: ASP.NET Core 8.0
-   **ORM**: Entity Framework Core
-   **Database**: Microsoft SQL Server 2019
-   **Authentication**: JWT (JSON Web Tokens)
-   **API Style**: RESTful API

## Project Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│         Controllers (API)           │  ← HTTP Endpoints
├─────────────────────────────────────┤
│           Services (BLL)            │  ← Business Logic Layer
├─────────────────────────────────────┤
│      Data Access (EF Core)          │  ← Entity Framework DbContext
├─────────────────────────────────────┤
│         Database (SQL Server)       │  ← Eva_QA / Eva_DEMO / Eva_UAT
└─────────────────────────────────────┘
```

### Directory Responsibilities

#### `/Data`

**Purpose**: Database access layer

-   **EvaDbContext.cs**: Main DbContext with all DbSets
-   **Models/**: Entity classes that map to database tables
    -   Organized by domain (Committees, Calendar, Journal, Sessions)
    -   Each entity represents a database table
    -   Contains navigation properties for relationships
    -   May include `IEntityTypeConfiguration` for Fluent API configuration

#### `/Services`

**Purpose**: Business logic layer

-   Contains service classes that implement business rules
-   Services are injected into controllers
-   Organized by domain/feature area
-   **Pattern**: Each service typically handles one entity or feature area
-   **Naming**: `[Feature]Service.cs` (e.g., `CommitteeReportService.cs`)

#### `/Controllers`

**Purpose**: API endpoints (HTTP layer)

-   RESTful API controllers
-   Handle HTTP requests/responses
-   Validate input
-   Call services for business logic
-   Return DTOs (not entities)
-   **Naming**: `[Feature]Controller.cs`

#### `/Dtos`

**Purpose**: Data Transfer Objects

-   Objects returned by API endpoints
-   Prevent exposing internal entity structure
-   Can combine data from multiple entities
-   Can exclude sensitive properties

#### `/Interfaces`

**Purpose**: Service contracts

-   Defines service interfaces
-   Enables dependency injection
-   Makes testing easier
-   **Pattern**: `I[Feature]Service.cs`

#### `/Migrations`

**Purpose**: Database schema versioning

-   Entity Framework migrations
-   Track database schema changes over time
-   Can be applied or rolled back
-   **Pattern**: `{Timestamp}_{TicketNumber}__{Description}.cs`

#### `/Mapping`

**Purpose**: Object mapping configuration

-   AutoMapper profiles
-   Maps between entities and DTOs
-   Keeps mapping logic centralized

#### `/Utilities`

**Purpose**: Helper classes and extension methods

-   Shared utility functions
-   Common operations

## Common Patterns

### Entity Pattern

```csharp
// Data/Models/Committees/CommitteeReports/CommitteeReport.cs
public class CommitteeReport
{
    public int Id { get; set; }
    public int SessionId { get; set; }
    public int CommitteeId { get; set; }

    // Navigation properties
    public virtual Session Session { get; set; }
    public virtual ICollection<CommitteeReportAction> Actions { get; set; }
}
```

### Service Pattern

```csharp
// Interfaces/ICommitteeReportService.cs
public interface ICommitteeReportService
{
    CommitteeReportDto GetReport(int id);
    void CreateReport(CreateReportDto dto);
}

// Services/CommitteeManagement/CommitteeReportService.cs
public class CommitteeReportService : ICommitteeReportService
{
    private readonly EvaDbContext _context;

    public CommitteeReportService(EvaDbContext context)
    {
        _context = context;
    }

    public CommitteeReportDto GetReport(int id)
    {
        // Business logic here
    }
}
```

### Controller Pattern

```csharp
// Controllers/CommitteeReportsController.cs
[ApiController]
[Route("api/[controller]")]
public class CommitteeReportsController : ControllerBase
{
    private readonly ICommitteeReportService _service;

    public CommitteeReportsController(ICommitteeReportService service)
    {
        _service = service;
    }

    [HttpGet("{id}")]
    public ActionResult<CommitteeReportDto> GetReport(int id)
    {
        var report = _service.GetReport(id);
        return Ok(report);
    }
}
```

## Entity Framework Conventions

### DbSet Naming

-   **DbSet Property**: Plural (e.g., `CommitteeReports`)
-   **Entity Class**: Singular (e.g., `CommitteeReport`)
-   **Table Name**: Usually plural, matches DbSet name

### Navigation Properties

-   **One-to-Many**: Use `virtual ICollection<T>`
-   **Many-to-One**: Use `virtual T`
-   **Lazy Loading**: Enabled via `virtual` keyword

### Foreign Keys

-   **Convention**: `{NavigationPropertyName}Id`
-   **Example**: `SessionId` for navigation property `Session`

## Configuration Files

### appsettings.development.json

Contains development environment settings:

-   Database connection strings
-   Authentication settings
-   Email configuration
-   External service URLs

**Environments**:

-   **Local**: localhost databases
-   **QA**: tvmwsqls01 server
-   **DEMO**: uvmwsqls01 server
-   **UAT**: uvmwsqls01 server

### Connection String Pattern

```json
{
    "EvaDb": "Data Source={server},{port};Initial Catalog={database};User ID={user};Password={password};TrustServerCertificate=True"
}
```

## Authentication

### JWT Configuration

-   **Issuer**: Michigan Senate
-   **Audience**: EvaUsers
-   **Token Expiration**: 2 hours (configurable)
-   **Refresh Tokens**: 3 days

### Domain Authentication

-   **Domain**: misenate.org
-   **LDAP**: misenate

## Common Entity Properties

Most entities follow this pattern:

```csharp
public class BaseEntity
{
    public int Id { get; set; }
    public string CreatedBy { get; set; }
    public DateTime Created { get; set; }
    public string ModifiedBy { get; set; }
    public DateTime Modified { get; set; }
}
```

**Note**: Some older entities may have:

-   `DateAdded` instead of `Created`
-   `LastModified` instead of `Modified`
-   `LastModifiedBy` instead of `ModifiedBy`

## Table Types

### Transaction Tables

Store business data that changes frequently:

-   `CommitteeReports`
-   `CommitteeMeetingNotices`
-   `CalendarEntries`

### Lookup/Reference Tables

Store static or semi-static reference data:

-   `CommitteeReportCommitteeActions` (21 predefined actions)
-   `CommitteeTypes`
-   `MeetingTypes`

### Junction/Mapping Tables

Handle many-to-many relationships:

-   `CommitteeReportsAttendance`
-   `CommitteeMeetingToCommitteeClerks`

## Migration Naming Convention

**Pattern**: `{Timestamp}_{TicketNumber}__{Description}.cs`

**Examples**:

-   `20240607134553_2968__CommitteeReportsRewrite.cs`
-   `20240820204656_3881_committee-report-additional-actions.cs`

**Components**:

-   **Timestamp**: `yyyyMMddHHmmss` format
-   **Ticket Number**: Jira/Issue tracking number
-   **Description**: Brief description of changes (lowercase with hyphens)

## Dependency Injection

Services are registered in `Program.cs`:

```csharp
builder.Services.AddScoped<ICommitteeReportService, CommitteeReportService>();
```

**Lifetime Options**:

-   **Scoped**: Created once per HTTP request (most services)
-   **Transient**: Created each time requested
-   **Singleton**: Created once for application lifetime

## Key Relationships

### Committee Reports

```
CommitteeReport (1) ─→ (N) CommitteeReportActions
                  └─→ (N) CommitteeReportAgendaItems
                  └─→ (N) CommitteeReportsAttendance
                  └─→ (N) CommitteeReportRollCalls

CommitteeReportAction (N) ─→ (1) CommitteeReportCommitteeAction (lookup)
```

### Sessions

```
Session (1) ─→ (N) CommitteeReports
        └─→ (N) CommitteeMeetingNotices
        └─→ (N) CalendarEntries
```

## Best Practices

1. **Entity Models**: Keep them simple, focused on data structure
2. **Services**: Implement business logic, validation, orchestration
3. **Controllers**: Keep thin, delegate to services
4. **DTOs**: Never return entities directly from API
5. **Migrations**: One migration per feature/ticket
6. **Async/Await**: Use for database operations
7. **Dependency Injection**: Use interfaces for services
