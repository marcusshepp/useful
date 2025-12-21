# Agent Skills for Eva & Legislature Databases

This directory contains Agent Skills that teach GitHub Copilot how to work with the Michigan Senate's database systems.

## What are Agent Skills?

Agent Skills are a new feature in GitHub Copilot that allows you to teach specialized capabilities through folders containing instructions, scripts, and resources. They follow the [Agent Skills open standard](https://agentskills.io/).

## Available Skills

### 1. eva-qa-database

Query and analyze the Eva application database (sessions, committee reports, meeting notices, etc.)

**Use this skill when:**

-   Working with Eva sessions
-   Querying committee reports
-   Accessing meeting notices or agendas
-   Exploring Eva application data

**Environment:** QA, DEMO, UAT, Local

**Security:** Read-only SELECT queries and INSERT only. UPDATE/DELETE blocked for safety.

### 2. legislature-qa-database

Query and analyze the Legislature (M2) database (committees, meetings, members, etc.)

**Use this skill when:**

-   Working with committee definitions
-   Querying committee meetings
-   Accessing committee membership
-   Exploring Legislature/M2 data

**Environment:** M2-QA, M2-DEMO, M2-UAT, M2-Local

**Security:** Read-only SELECT queries and INSERT only. UPDATE/DELETE blocked for safety.

### 3. azure-devops-search

Search for Azure DevOps work items using text search and filters.

**Use this skill when:**

-   User asks to find tickets, work items, or issues
-   Searching by keyword, state, assignment, or tags
-   Need to find bugs, user stories, or features

**Authentication:** PAT token stored in `network/.env` file

### 4. azure-devops-details

Get complete details for specific Azure DevOps work items by ID.

**Use this skill when:**

-   User mentions a specific ticket number
-   Need full work item context including comments
-   Want to see change history or related items

**Authentication:** PAT token stored in `network/.env` file

## How to Use

Copilot will automatically discover and use these skills when you ask questions about the databases. For example:

```
"Show me all active committees in the QA database"
"What's the current session in Eva?"
"Get the schema for the Committee table"
"Find committees with 'Finance' in the name"
```

You can also explicitly reference skills:

```
"Using the eva-qa-database skill, show me recent committee reports"
```

## PowerShell Functions

Database skills use the PowerShell functions from `EvaSql.psm1`:

### Query Data (SELECT)

```powershell
Invoke-EvaSql -Query "SELECT * FROM TableName" -Environment QA
```

**Security:** Only SELECT queries are allowed. UPDATE, DELETE, DROP, and other dangerous operations are automatically blocked.

### Insert Data (INSERT)

```powershell
Invoke-EvaSqlNonQuery -Query "INSERT INTO TableName (Column) VALUES ('Value')" -Environment QA
```

**Security:** Only INSERT queries are allowed. UPDATE and DELETE operations are automatically blocked to prevent accidental data modification.

## Structure

Each skill contains:

-   `SKILL.md` - Main instructions and usage guide
-   `references/` - Detailed documentation
    -   `DATABASE-SCHEMA.md` - Table structures and relationships
    -   `COMMON-QUERIES.md` - Frequently used queries
    -   `CONNECTION-STRINGS.md` - Environment connection details
-   `scripts/` - Example PowerShell scripts

## Key Differences: Eva vs Legislature

| Aspect           | Eva Database                        | Legislature Database          |
| ---------------- | ----------------------------------- | ----------------------------- |
| Environment Flag | `QA`, `DEMO`, `UAT`                 | `M2-QA`, `M2-DEMO`, `M2-UAT`  |
| Database Name    | Eva_QA, Eva_DEMO, Eva_UAT           | Legislature (same for all)    |
| Table Names      | Plural (sessions, CommitteeReports) | Singular (Committee, Session) |
| Primary Keys     | Usually just `Id`                   | TableNameID (CommitteeID)     |
| Date Columns     | Created, Modified                   | DateAdded, LastModified       |
| Current Session  | SessionID = 3                       | SessionID = 16                |

## Examples

See the `scripts/examples.ps1` file in each skill directory for comprehensive usage examples.

## Updating Skills

To update these skills:

1. Edit the relevant `.md` or `.ps1` files
2. Copilot will automatically pick up changes
3. Skills are version controlled with the repository

## Support

For issues or questions:

-   Check the reference documentation in each skill's `references/` folder
-   Run the example scripts in `scripts/examples.ps1`
-   Ask Copilot for help using the skill

## Learn More

-   [Agent Skills Specification](https://agentskills.io/specification)
-   [VS Code Copilot Customization](https://code.visualstudio.com/docs/copilot/copilot-customization)
-   [GitHub Copilot Agent Skills Announcement](https://github.blog/changelog/2025-12-18-github-copilot-now-supports-agent-skills)
