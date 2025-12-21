---
name: azure-devops-search
description: Search for Azure DevOps work items using text search and filters. Use when the user asks to find tickets, work items, issues, bugs, or user stories by keyword, state, assignment, tags, or area. PAT token in .env file at network/.env.
---

# Azure DevOps Work Items Search

Search for Azure DevOps work items using text search and various filters. This skill helps find bugs, user stories, tasks, and features across the Legislative project.

## Prerequisites Setup

### 1. Load PAT Token from .env file

```powershell
# Load the PAT from the .env file in network directory
$envFile = "c:\Users\mshepherd\p\useful\network\.env"
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^AZURE_DEVOPS_PAT=(.+)$') {
        $env:AZURE_DEVOPS_PAT = $matches[1]
    }
    if ($_ -match '^AZURE_DEVOPS_ORG=(.+)$') {
        $env:AZURE_DEVOPS_ORG = $matches[1]
    }
    if ($_ -match '^AZURE_DEVOPS_PROJECT=(.+)$') {
        $env:AZURE_DEVOPS_PROJECT = $matches[1]
    }
}
```

### 2. Import Module and Initialize

```powershell
Import-Module c:\Users\mshepherd\p\useful\network\AzureDevOpsTools\AzureDevOpsTools.psd1 -Force
Initialize-AzureDevOps -Organization $env:AZURE_DEVOPS_ORG -Project $env:AZURE_DEVOPS_PROJECT
```

### Complete One-Liner Setup

```powershell
Get-Content c:\Users\mshepherd\p\useful\network\.env | ForEach-Object { if ($_ -match '^(AZURE_DEVOPS_\w+)=(.+)$') { Set-Item "env:$($matches[1])" $matches[2] } }; Import-Module c:\Users\mshepherd\p\useful\network\AzureDevOpsTools\AzureDevOpsTools.psd1 -Force; Initialize-AzureDevOps -Organization $env:AZURE_DEVOPS_ORG -Project $env:AZURE_DEVOPS_PROJECT
```

## Usage Examples

### Basic text search

```powershell
$results = Search-WorkItems -SearchText "agenda"
Write-Host "Found $($results.Count) items"
$results | Format-Table Id, Type, Title, State -AutoSize
```

### Get first result with link

```powershell
$result = Search-WorkItems -SearchText "agenda" -Top 1
if ($result) {
    Write-Host "[$($result.Id)] $($result.Title)"
    Write-Host "https://dev.azure.com/$env:AZURE_DEVOPS_ORG/$env:AZURE_DEVOPS_PROJECT/_workitems/edit/$($result.Id)"
}
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
Search-WorkItems -AreaPath "LegBone\Backend" -WorkItemType "User Story"
```

### Search by tags

```powershell
Search-WorkItems -Tags "bug-fix" -State "Closed"
```

## Parameters

-   **SearchText**: Text to search in title and description
-   **WorkItemType**: Bug, User Story, Task, Feature, etc.
-   **State**: New, Active, Resolved, Closed, etc.
-   **AssignedTo**: User email or display name
-   **AreaPath**: Area path to search under
-   **IterationPath**: Iteration path to search under
-   **Tags**: Tags to filter by
-   **Top**: Maximum results (default 200)

## Output Format

Returns array of work item objects with:

-   `Id` - Work item ID number
-   `Type` - Bug, User Story, Task, Feature
-   `Title` - Work item title
-   `State` - New, Active, Resolved, Closed
-   `AssignedTo` - Assigned user
-   `CreatedBy` - Creator
-   `CreatedDate` - Creation date
-   `ChangedDate` - Last modified date
-   `Description` - Full description
-   `AcceptanceCriteria` - Acceptance criteria
-   `Priority` - Priority level
-   `Effort` - Effort estimate
-   `Tags` - Tags
-   `AreaPath` - Area path
-   `IterationPath` - Iteration path
-   `Url` - Web URL for viewing in Azure DevOps

## Tips for AI Assistants

-   Always load the .env file first to get credentials
-   When user mentions a feature or component, search for it
-   Try multiple related search terms if first search yields no results
-   Combine filters to narrow down results
-   Use State filter to focus on active work vs. completed items
-   Display results in a readable format with ID and link
-   The organization is "Legislative" and project is "LegBone"

## Common Patterns

### Pattern: Quick search and link

```powershell
Get-Content c:\Users\mshepherd\p\useful\network\.env | ForEach-Object { if ($_ -match '^(AZURE_DEVOPS_\w+)=(.+)$') { Set-Item "env:$($matches[1])" $matches[2] } }; Import-Module c:\Users\mshepherd\p\useful\network\AzureDevOpsTools\AzureDevOpsTools.psd1 -Force; Initialize-AzureDevOps -Organization $env:AZURE_DEVOPS_ORG -Project $env:AZURE_DEVOPS_PROJECT; $result = Search-WorkItems -SearchText "your-search" -Top 1; if ($result) { Write-Host "[$($result.Id)] $($result.Title)"; Write-Host "https://dev.azure.com/$env:AZURE_DEVOPS_ORG/$env:AZURE_DEVOPS_PROJECT/_workitems/edit/$($result.Id)" }
```

### Pattern: Search and format results

```powershell
$results = Search-WorkItems -SearchText "bug" -State "Active"
$results | Select-Object Id, Title, AssignedTo, Priority | Format-Table -AutoSize
```
