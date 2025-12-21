---
name: search-work-items
description: Search for Azure DevOps work items using text search and filters. IMPORTANT - Only use Bug or User Story types by default, exclude Enabler and other types.
---

# Search Azure DevOps Work Items

Search for Azure DevOps work items using text search and various filters. This skill helps find bugs and user stories across the project.

## When to Use

- User asks to find tickets, work items, or issues
- Searching for items by keyword, feature name, or topic
- Filtering by state, type, assignment, or tags
- Finding all items in an area or iteration

## Prerequisites

- Azure DevOps must be initialized with `Initialize-AzureDevOps`
- PAT token must be set (via parameter or AZURE_DEVOPS_PAT environment variable)

## Examples

### Basic text search

```powershell
Search-WorkItems -SearchText "PDF export"
```

### Search with filters

```powershell
Search-WorkItems -SearchText "authentication" -WorkItemType "Bug" -State "Active"
```

### Search by assignment

```powershell
Search-WorkItems -AssignedTo "john.doe@company.com" -State "Active"
```

### Search by area path

```powershell
Search-WorkItems -AreaPath "MyProject\Backend" -WorkItemType "User Story"
```

### Search by tags

```powershell
Search-WorkItems -Tags "bug-fix" -State "Closed"
```

## Parameters

- **SearchText**: Text to search in title and description
- **WorkItemType**: Bug, User Story, Task, Feature, etc. **NOTE: Only use "Bug" or "User Story" - exclude Enabler and other types**
- **State**: New, Active, Resolved, Closed, etc.
- **AssignedTo**: User email or display name
- **AreaPath**: Area path to search under
- **IterationPath**: Iteration path to search under
- **Tags**: Tags to filter by
- **Top**: Maximum results (default 200)

## Output

Returns array of work item objects with:

- Id, Type, Title, State
- AssignedTo, CreatedBy, Created/Changed dates
- Description, Acceptance Criteria
- Priority, Effort, Tags
- Area/Iteration paths
- Web URL for viewing in Azure DevOps

## Tips for Copilot

- **IMPORTANT: Default to Bug or User Story types only - do not include Enabler or other work item types unless explicitly requested**
- When user mentions a feature or component, search for it
- Try multiple related search terms if first search yields no results
- Combine filters to narrow down results
- Use State filter to focus on active work vs. completed items
- When filtering results, exclude Enabler type by default
