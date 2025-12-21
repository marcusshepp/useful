# Azure DevOps + Copilot CLI Integration

## Goal

Use GitHub Copilot CLI to reason about and manage Azure DevOps work items through natural language. Copilot decides what to search for, the PowerShell module handles the API calls.

---

## Architecture

```
You (natural language)
    |
    v
Copilot CLI (reasoning layer)
    |
    v
PowerShell Module (API plumbing)
    |
    v
Azure DevOps REST API
```

Copilot handles the hard part: understanding "find tickets related to the PDF export feature" means searching for "PDF", "export", "document generation", etc. The module just executes those searches and returns data.

---

## Module Capabilities

### Search

| Function | Purpose |
|----------|---------|
| Search-WorkItems | Text search across title/description with optional filters |
| Get-WorkItem | Fetch full details for one or more IDs |
| Get-WorkItemsByFeature | Find a feature and all its children |
| Get-RelatedWorkItems | Get linked items (parent, children, related) |

Search supports combining:
- Free text (searches title and description)
- Work item type (Bug, User Story, Task, Feature)
- State (New, Active, Resolved, Closed)
- Assigned to
- Area path
- Iteration path
- Tags

### Full Details Returned

For each work item:
- Title, description, acceptance criteria
- State, assigned to, priority, effort
- Tags, area path, iteration path
- All comments
- Attachment URLs
- Revision history (who changed what, when)
- Relations (parent, children, linked items, PRs)

### Update

| Function | Purpose |
|----------|---------|
| Update-WorkItem | Modify fields (state, title, AC, assigned to, tags) |
| Add-WorkItemComment | Add a comment to a ticket |
| New-WorkItem | Create a new work item with optional parent link |

### Export

| Function | Purpose |
|----------|---------|
| Export-WorkItemsToMarkdown | Generate markdown report with links and ACs |

---

## Authentication

Uses a Personal Access Token (PAT) with Work Items read/write scope.

Storage options:
- Environment variable: AZURE_DEVOPS_PAT
- Pass directly to Initialize-AzureDevOps

---

## Example Workflows

### Find Related Tickets

You: "Find all tickets related to the bill drafting workflow"

Copilot runs:
```powershell
Search-WorkItems -SearchText "bill drafting"
Search-WorkItems -SearchText "draft workflow"
Search-WorkItems -SearchText "legislation draft"
Search-WorkItems -AreaPath "ProjectName\BillDrafting"
```

Copilot combines results, reads through them, summarizes what it found.

### Export Acceptance Criteria

You: "Give me a markdown file with the ACs for active user stories under the authentication feature"

Copilot runs:
```powershell
$items = Search-WorkItems -SearchText "authentication" -WorkItemType "User Story" -State "Active"
$items | Export-WorkItemsToMarkdown -IncludeAcceptanceCriteria -OutputPath "auth-acs.md"
```

### Update Ticket State

You: "Close ticket 12345 and add a comment saying it was fixed in PR 789"

Copilot runs:
```powershell
Update-WorkItem -Id 12345 -State "Closed"
Add-WorkItemComment -Id 12345 -Comment "Fixed in PR 789"
```

### Get Full Context on a Ticket

You: "Tell me everything about ticket 5678 including who worked on it"

Copilot runs:
```powershell
Get-WorkItem -Ids 5678 -ExpandRelations
Get-WorkItemComments -Id 5678
Get-WorkItemHistory -Id 5678
```

Copilot reads the results and gives you a summary.

---

## Module Structure

```
AzureDevOpsTools/
    AzureDevOpsTools.psd1       # Module manifest
    AzureDevOpsTools.psm1       # Main module file
```

Single file module. No external dependencies beyond PowerShell 7.

---

## Setup

1. Generate PAT in Azure DevOps with Work Items read/write scope
2. Set environment variable or store securely
3. Copy module to PowerShell modules path
4. Add to profile:
   ```powershell
   Import-Module AzureDevOpsTools
   Initialize-AzureDevOps -Organization "your-org" -Project "your-project"
   ```
5. Use with Copilot CLI

---

## API Reference

Base URL: `https://dev.azure.com/{org}/{project}/_apis`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| wit/wiql | POST | Run WIQL query |
| wit/workitems?ids=1,2,3 | GET | Batch fetch work items |
| wit/workitems/{id} | PATCH | Update work item |
| wit/workitems/${type} | POST | Create work item |
| wit/workitems/{id}/comments | GET/POST | Read/add comments |
| wit/workitems/{id}/updates | GET | Revision history |

Auth: Basic header with base64 encoded ":{PAT}"

API Version: 7.1

---

## Limitations

- Azure DevOps search is text-based, not semantic
- Copilot must reason about what terms to search
- Large result sets may need multiple queries
- Rate limits apply to API calls

---

## Next Steps

1. Generate PAT with appropriate scopes
2. Build module with core search and get functions
3. Test search coverage on actual ticket data
4. Add update functions
5. Add markdown export
6. Test end-to-end with Copilot CLI
