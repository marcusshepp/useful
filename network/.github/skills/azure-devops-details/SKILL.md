---
name: azure-devops-details
description: Retrieve complete details for specific Azure DevOps work items by ID, including all fields, comments, change history, and related items. Use when the user asks about a specific ticket number or needs full context on a work item. PAT token in .env file at network/.env.
---

# Azure DevOps Work Item Details

Retrieve complete details for specific work items by ID, including all fields, comments, history, and related items.

## Prerequisites Setup

### Complete One-Liner Setup

```powershell
Get-Content c:\Users\mshepherd\p\useful\network\.env | ForEach-Object { if ($_ -match '^(AZURE_DEVOPS_\w+)=(.+)$') { Set-Item "env:$($matches[1])" $matches[2] } }; Import-Module c:\Users\mshepherd\p\useful\network\AzureDevOpsTools\AzureDevOpsTools.psd1 -Force; Initialize-AzureDevOps -Organization $env:AZURE_DEVOPS_ORG -Project $env:AZURE_DEVOPS_PROJECT
```

## Usage Examples

### Get single work item

```powershell
$item = Get-WorkItem -Ids 6673
Write-Host "[$($item.Id)] $($item.Title)"
Write-Host "State: $($item.State)"
Write-Host "Assigned To: $($item.AssignedTo)"
Write-Host "Description: $($item.Description)"
```

### Get multiple work items

```powershell
$items = Get-WorkItem -Ids 6673,6674,6675
$items | Format-Table Id, Title, State, AssignedTo -AutoSize
```

### Get with relations (parent/child items)

```powershell
$item = Get-WorkItem -Ids 6673 -ExpandRelations
# This will include related work items in the response
```

### Get all comments

```powershell
$comments = Get-WorkItemComments -Id 6673
Write-Host "Total comments: $($comments.Count)"
$comments | ForEach-Object {
    Write-Host "[$($_.CreatedBy)] $($_.CreatedDate)"
    Write-Host $_.Text
    Write-Host ""
}
```

### Get change history

```powershell
$history = Get-WorkItemHistory -Id 6673
$history | Format-Table Rev, RevisedBy, RevisedDate, ChangedFields -AutoSize
```

### Get related items

```powershell
# Get all related items
$related = Get-RelatedWorkItems -Id 6673
Write-Host "Found $($related.Count) related items"

# Get only child items
$children = Get-RelatedWorkItems -Id 6673 -RelationType Child

# Get parent item
$parent = Get-RelatedWorkItems -Id 6673 -RelationType Parent
```

## Available Functions

### Get-WorkItem

Returns full work item details including all fields.

**Parameters:**

-   `Ids` - Work item IDs (single or comma-separated)
-   `ExpandRelations` - Include related work items

### Get-WorkItemComments

Returns all comments/discussions on the work item.

**Parameters:**

-   `Id` - Work item ID

### Get-WorkItemHistory

Returns revision history showing who changed what and when.

**Parameters:**

-   `Id` - Work item ID

### Get-RelatedWorkItems

Returns parent, child, or related work items.

**Parameters:**

-   `Id` - Work item ID
-   `RelationType` - Parent, Child, Related, or All (default)

## Output Format

Work items include:

-   `Id` - Work item ID
-   `Type` - Bug, User Story, Task, Feature
-   `Title` - Work item title
-   `State` - Current state
-   `AssignedTo` - Assigned user
-   `Description` - Full description
-   `AcceptanceCriteria` - Acceptance criteria
-   `Priority` - Priority level
-   `Effort` - Effort estimate
-   `Tags` - Tags
-   `CreatedBy`, `CreatedDate` - Creator info
-   `ChangedBy`, `ChangedDate` - Last modified info
-   `AreaPath`, `IterationPath` - Paths
-   `Url` - Web URL for Azure DevOps
-   All custom fields

Comments include:

-   `Text` - Comment text
-   `CreatedBy` - Author
-   `CreatedDate` - When posted

## Tips for AI Assistants

-   Always load .env file first to get credentials
-   Use this when user mentions a specific ticket number
-   Get comments to understand discussion context
-   Check history to see who worked on it and what changed
-   Use ExpandRelations to see linked parent/child items
-   Display results in a readable format
-   Organization is "Legislative" and project is "LegBone"

## Common Patterns

### Pattern: Get ticket with full context

```powershell
Get-Content c:\Users\mshepherd\p\useful\network\.env | ForEach-Object { if ($_ -match '^(AZURE_DEVOPS_\w+)=(.+)$') { Set-Item "env:$($matches[1])" $matches[2] } }; Import-Module c:\Users\mshepherd\p\useful\network\AzureDevOpsTools\AzureDevOpsTools.psd1 -Force; Initialize-AzureDevOps -Organization $env:AZURE_DEVOPS_ORG -Project $env:AZURE_DEVOPS_PROJECT; $item = Get-WorkItem -Ids 6673; Write-Host "[$($item.Id)] $($item.Title)"; Write-Host "State: $($item.State) | Assigned: $($item.AssignedTo)"; Write-Host "Link: https://dev.azure.com/$env:AZURE_DEVOPS_ORG/$env:AZURE_DEVOPS_PROJECT/_workitems/edit/$($item.Id)"
```

### Pattern: Get ticket with comments

```powershell
$item = Get-WorkItem -Ids 6673
$comments = Get-WorkItemComments -Id 6673
Write-Host "Work Item: [$($item.Id)] $($item.Title)"
Write-Host "`nComments ($($comments.Count)):"
$comments | ForEach-Object { Write-Host "- [$($_.CreatedBy)] $($_.Text)" }
```
