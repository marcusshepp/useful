---
name: export-work-items
description: Generate markdown reports of work items with optional details like acceptance criteria, descriptions, and comments. Use when creating sprint summaries, feature overviews, or documenting requirements.
---

# Export Work Items to Markdown

Generate markdown reports of work items with optional details like acceptance criteria, descriptions, and comments.

## When to Use

- User wants a report or documentation of work items
- Need to share work item details outside Azure DevOps
- Creating sprint summaries or feature overviews
- Documenting requirements or acceptance criteria

## Prerequisites

- Azure DevOps must be initialized with `Initialize-AzureDevOps`

## Examples

### Export search results

```powershell
Search-WorkItems -SearchText "authentication" | Export-WorkItemsToMarkdown -OutputPath "auth-items.md"
```

### Export with acceptance criteria

```powershell
Search-WorkItems -WorkItemType "User Story" -State "Active" |
    Export-WorkItemsToMarkdown -OutputPath "active-stories.md" -IncludeAcceptanceCriteria
```

### Export with full details

```powershell
Get-WorkItem -Ids 12345,67890 |
    Export-WorkItemsToMarkdown -OutputPath "feature-details.md" `
        -IncludeDescription `
        -IncludeAcceptanceCriteria `
        -IncludeComments
```

### Export feature with children

```powershell
Get-WorkItemsByFeature -SearchText "authentication" |
    Export-WorkItemsToMarkdown -OutputPath "auth-feature.md" -IncludeAcceptanceCriteria
```

## Function

### Export-WorkItemsToMarkdown

Accepts work items from pipeline and generates markdown report.

## Parameters

- **WorkItems**: Array of work items (from pipeline)
- **OutputPath**: File path to save markdown (required)
- **IncludeAcceptanceCriteria**: Include AC in export
- **IncludeDescription**: Include descriptions
- **IncludeComments**: Include all comments

## Output

Returns object with:

- **FilePath**: Path to generated file
- **ItemCount**: Number of items exported

Markdown includes:

- Work item ID and title as headers
- Type, state, assignment
- Tags and links to Azure DevOps
- Optional: description, acceptance criteria, comments
- Formatted for easy reading

## Tips for Copilot

- Pipe search results directly to export
- Use IncludeAcceptanceCriteria for requirements docs
- Use IncludeComments for full context
- Good for sprint planning documents
- Helpful for sharing with non-Azure DevOps users
