---
name: find-feature-work
description: Search for features and automatically retrieve all child work items (stories, tasks, bugs) under that feature. Use when planning or reviewing feature scope.
---

# Find Feature and Related Work

Search for features and automatically retrieve all child work items (stories, tasks, bugs) under that feature.

## When to Use

- User asks about a specific feature
- Need to see all work under a feature
- Planning or reviewing feature scope
- Understanding feature dependencies

## Prerequisites

- Azure DevOps must be initialized with `Initialize-AzureDevOps`

## Examples

### Find feature and children

```powershell
Get-WorkItemsByFeature -SearchText "authentication"
```

### Find and export

```powershell
Get-WorkItemsByFeature -SearchText "PDF export" |
    Export-WorkItemsToMarkdown -OutputPath "pdf-feature.md" -IncludeAcceptanceCriteria
```

### Check feature status

```powershell
$items = Get-WorkItemsByFeature -SearchText "bill drafting"
$items | Group-Object State | Select-Object Name, Count
```

## Function

### Get-WorkItemsByFeature

Searches for feature by text and returns feature plus all child items.

## Parameters

- **SearchText**: Text to search in feature title (required)

## Output

Returns array of work item objects including:

- The feature itself
- All child user stories
- All child tasks
- All child bugs
- Complete hierarchy with relations

## Tips for Copilot

- Good starting point for feature planning
- Use with Export-WorkItemsToMarkdown for reports
- Check State distribution to see progress
- Useful for dependency analysis
