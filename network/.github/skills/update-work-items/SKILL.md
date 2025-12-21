---
name: update-work-items
description: Modify work item fields, add comments, and create new items. Use when user wants to update, comment on, or create work items.
---

# Update Work Items

Modify work item fields, add comments, and create new items in Azure DevOps.

## When to Use

- User wants to update a work item
- Adding comments or notes to tickets
- Changing state, assignment, or other fields
- Creating new bugs or user stories

## Prerequisites

- Azure DevOps must be initialized with `Initialize-AzureDevOps`
- User must have write permissions in Azure DevOps

## Examples

### Update state

```powershell
Update-WorkItem -Id 12345 -State "Closed"
```

### Update assignment

```powershell
Update-WorkItem -Id 12345 -AssignedTo "john.doe@company.com"
```

### Update multiple fields

```powershell
Update-WorkItem -Id 12345 -State "Active" -Priority 1 -Tags "urgent,bug-fix"
```

### Add comment

```powershell
Add-WorkItemComment -Id 12345 -Comment "Fixed in PR #789"
```

### Create new bug

```powershell
New-WorkItem -Type "Bug" -Title "Login fails on Safari" -Priority 1
```

### Create user story with details

```powershell
New-WorkItem -Type "User Story" `
    -Title "Add export to PDF" `
    -Description "Users need to export reports as PDF" `
    -Priority 2 `
    -AreaPath "MyProject\Features"
```

## Functions

### Update-WorkItem

Updates fields on an existing work item.

**Parameters:**
- **Id**: Work item ID (required)
- **State**: New state value
- **AssignedTo**: User email to assign to
- **Priority**: Priority level (1-4)
- **Tags**: Comma-separated tags
- **Title**: New title
- **Description**: New description

### Add-WorkItemComment

Adds a comment to a work item.

**Parameters:**
- **Id**: Work item ID (required)
- **Comment**: Comment text (required)

### New-WorkItem

Creates a new work item.

**Parameters:**
- **Type**: Bug, User Story, Task, etc. (required)
- **Title**: Work item title (required)
- **Description**: Detailed description
- **Priority**: Priority level (1-4)
- **AssignedTo**: User email to assign to
- **AreaPath**: Area path
- **IterationPath**: Iteration/sprint path
- **Tags**: Comma-separated tags

## Output

All functions return the updated/created work item object with all current fields.

## Tips for Copilot

- Confirm changes with user before executing
- Use Add-WorkItemComment for audit trail
- Verify work item exists before updating
- Check valid state transitions in project
- Use specific, descriptive titles for new items
