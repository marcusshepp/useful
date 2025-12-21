---
name: get-work-item-details
description: Retrieve full details of work items including comments, history, and related items. Use when user wants complete information about specific work items.
---

# Get Work Item Details

Retrieve full details of work items including comments, history, and related items.

## When to Use

- User asks about a specific ticket number
- Need complete work item information
- Investigating work item history or changes
- Understanding work item relationships

## Prerequisites

- Azure DevOps must be initialized with `Initialize-AzureDevOps`

## Examples

### Get basic details

```powershell
Get-WorkItem -Ids 12345
```

### Get multiple items

```powershell
Get-WorkItem -Ids 12345,67890,11111
```

### Get with relationships

```powershell
Get-WorkItem -Ids 12345 -ExpandRelations
```

### Get comments

```powershell
Get-WorkItemComments -Id 12345
```

### Get full history

```powershell
Get-WorkItemHistory -Id 12345
```

### Get everything

```powershell
$details = Get-WorkItem -Ids 12345 -ExpandRelations
$comments = Get-WorkItemComments -Id 12345
$history = Get-WorkItemHistory -Id 12345
```

## Functions

### Get-WorkItem

Retrieves work item details.

**Parameters:**
- **Ids**: One or more work item IDs (required)
- **ExpandRelations**: Include parent/child/related items

**Returns:** Work item object(s) with all fields

### Get-WorkItemComments

Retrieves all comments on a work item.

**Parameters:**
- **Id**: Work item ID (required)

**Returns:** Array of comment objects with text, author, date

### Get-WorkItemHistory

Retrieves change history for a work item.

**Parameters:**
- **Id**: Work item ID (required)

**Returns:** Array of history entries showing field changes

## Output Fields

Work items include:

- Id, Type, Title, State
- AssignedTo, CreatedBy, ChangedBy
- Created, Changed dates
- Description, AcceptanceCriteria
- Priority, Effort, StoryPoints
- Tags, AreaPath, IterationPath
- WebUrl (link to Azure DevOps)
- Relations (if expanded)

## Tips for Copilot

- Start with basic Get-WorkItem, add details as needed
- Use ExpandRelations to see related items
- Comments often have important context
- History helps understand decision-making
- Combine with other commands for analysis
