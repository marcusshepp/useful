# Azure DevOps Tools Module

PowerShell module for managing Azure DevOps work items, designed to work seamlessly with GitHub Copilot CLI.

## 🚀 Quick Setup for New Copilot Sessions

**Run this before using any tools:**

```powershell
cd C:\Users\mshepherd\p\useful\network
$env:AZURE_DEVOPS_PAT = (Get-Content .env | Select-String "AZURE_DEVOPS_PAT").ToString().Split('=')[1]
$env:AZURE_DEVOPS_ORG = "Legislative"
$env:AZURE_DEVOPS_PROJECT = "LegBone"
$env:EVA_QA_PASSWORD = "eva4eva"
$env:M2_QA_PASSWORD = "ThisIsQA!"
Import-Module .\AzureDevOpsTools\AzureDevOpsTools.psd1 -Force
Import-Module .\EvaSql.psm1 -Force
Initialize-AzureDevOps
```

📚 **See [.github/skills/](/.github/skills/)** for detailed skills and workflows.

## Overview

This module provides natural language integration between GitHub Copilot and Azure DevOps. Instead of learning WIQL syntax or navigating the Azure DevOps UI, you can ask Copilot to find, update, and manage work items using plain English.

## Architecture

```
You (natural language)
    |
    v
GitHub Copilot CLI (reasoning)
    |
    v
AzureDevOpsTools Module (API calls)
    |
    v
Azure DevOps REST API
```

## Features

-   **Search**: Find work items by text, type, state, assignment, tags, area, or iteration
-   **Get Details**: Retrieve full work item details including comments and history
-   **Update**: Modify work item fields, add comments, create new items
-   **Export**: Generate markdown reports with acceptance criteria
-   **Relations**: Navigate parent/child/related work item hierarchies

## Installation

### 1. Install the Module

Copy the module to your PowerShell modules directory:

```powershell
# Windows
$modulePath = "$env:USERPROFILE\Documents\PowerShell\Modules\AzureDevOpsTools"
Copy-Item -Path ".\AzureDevOpsTools" -Destination $modulePath -Recurse -Force
```

Or use it directly from this directory:

```powershell
Import-Module .\AzureDevOpsTools\AzureDevOpsTools.psd1
```

### 2. Generate a Personal Access Token (PAT)

1. Go to your Azure DevOps organization
2. Click User Settings (gear icon) > Personal Access Tokens
3. Click "New Token"
4. Give it a name (e.g., "Copilot CLI")
5. Set scope to **Work Items: Read & Write**
6. Set expiration as desired
7. Click "Create" and **copy the token** (only shown once!)

### 3. Set Up Authentication

Store your PAT securely:

```powershell
# Option 1: Environment variable (recommended)
$env:AZURE_DEVOPS_PAT = "your-pat-token-here"

# Option 2: Add to PowerShell profile for persistence
# Edit your profile
notepad $PROFILE

# Add this line:
$env:AZURE_DEVOPS_PAT = "your-pat-token-here"
```

### 4. Initialize the Module

Add to your PowerShell profile (`$PROFILE`):

```powershell
Import-Module AzureDevOpsTools
Initialize-AzureDevOps -Organization "your-org" -Project "your-project"
```

Or initialize manually each session:

```powershell
Import-Module AzureDevOpsTools
Initialize-AzureDevOps -Organization "myorg" -Project "myproject"
```

## Quick Start

### Search for Work Items

```powershell
# Find all bugs related to authentication
Search-WorkItems -SearchText "authentication" -WorkItemType "Bug"

# Find active user stories
Search-WorkItems -WorkItemType "User Story" -State "Active"

# Find items assigned to you
Search-WorkItems -AssignedTo "your.email@company.com" -State "Active"
```

### Get Work Item Details

```powershell
# Get full details for a work item
Get-WorkItem -Ids 12345

# Get with related items
Get-WorkItem -Ids 12345 -ExpandRelations

# Get all comments
Get-WorkItemComments -Id 12345

# Get change history
Get-WorkItemHistory -Id 12345
```

### Update Work Items

```powershell
# Close a work item
Update-WorkItem -Id 12345 -State "Closed"

# Add a comment
Add-WorkItemComment -Id 12345 -Comment "Fixed in PR #789"

# Create a new bug
New-WorkItem -Type "Bug" -Title "Login fails on Safari" -Priority 1
```

### Export to Markdown

```powershell
# Export active stories with acceptance criteria
Search-WorkItems -WorkItemType "User Story" -State "Active" |
    Export-WorkItemsToMarkdown -OutputPath "active-stories.md" -IncludeAcceptanceCriteria

# Export a feature and all its children
Get-WorkItemsByFeature -SearchText "PDF export" |
    Export-WorkItemsToMarkdown -OutputPath "pdf-feature.md" -IncludeAcceptanceCriteria
```

## Using with GitHub Copilot CLI

Once the module is installed and initialized, you can use natural language with Copilot:

### Example Conversations

**You**: "Find all active bugs assigned to me"

**Copilot** will run:

```powershell
Search-WorkItems -AssignedTo "your.email@company.com" -WorkItemType "Bug" -State "Active"
```

**You**: "Tell me everything about ticket 12345"

**Copilot** will run:

```powershell
Get-WorkItem -Ids 12345 -ExpandRelations
Get-WorkItemComments -Id 12345
Get-WorkItemHistory -Id 12345
```

**You**: "Close ticket 12345 and add a comment that it was fixed in PR 789"

**Copilot** will run:

```powershell
Update-WorkItem -Id 12345 -State "Closed"
Add-WorkItemComment -Id 12345 -Comment "Fixed in PR 789"
```

**You**: "Give me a markdown file with all user stories under the authentication feature"

**Copilot** will run:

```powershell
Get-WorkItemsByFeature -SearchText "authentication" |
    Where-Object { $_.Type -eq "User Story" } |
    Export-WorkItemsToMarkdown -OutputPath "auth-stories.md" -IncludeAcceptanceCriteria
```

## Copilot Skills

The `.skills` directory contains skill documentation that helps Copilot understand when and how to use each function:

-   `initialize-azure-devops.skill.md` - Set up connection
-   `search-work-items.skill.md` - Search and filter work items
-   `get-work-item-details.skill.md` - Get full details, comments, history
-   `update-work-items.skill.md` - Modify, comment, create items
-   `export-work-items.skill.md` - Generate markdown reports
-   `find-feature-work.skill.md` - Find features and their children

## Functions Reference

### Core Functions

| Function                     | Purpose                                       |
| ---------------------------- | --------------------------------------------- |
| `Initialize-AzureDevOps`     | Set up connection to Azure DevOps             |
| `Search-WorkItems`           | Search with filters (text, type, state, etc.) |
| `Get-WorkItem`               | Get full details for specific IDs             |
| `Get-WorkItemsByFeature`     | Find feature and all children                 |
| `Get-RelatedWorkItems`       | Get parent/child/related items                |
| `Get-WorkItemComments`       | Get all comments on a work item               |
| `Get-WorkItemHistory`        | Get revision history                          |
| `Update-WorkItem`            | Modify work item fields                       |
| `Add-WorkItemComment`        | Add a comment                                 |
| `New-WorkItem`               | Create a new work item                        |
| `Export-WorkItemsToMarkdown` | Generate markdown report                      |

## Configuration

The module stores connection details in script-scoped variables. Each PowerShell session needs to call `Initialize-AzureDevOps` before using other functions.

### Multi-Organization Setup

If you work with multiple organizations or projects, reinitialize as needed:

```powershell
# Switch to different project
Initialize-AzureDevOps -Organization "other-org" -Project "other-project"
```

## Troubleshooting

### "Azure DevOps not initialized"

Run `Initialize-AzureDevOps` before other commands.

### "PAT not found"

Set the `AZURE_DEVOPS_PAT` environment variable or pass PAT to `Initialize-AzureDevOps`.

### "Failed to search work items"

Check:

-   PAT has Work Items Read scope
-   Organization and Project names are correct
-   Network connectivity to Azure DevOps

### No results found

-   Try broader search terms
-   Check filters (state, type, etc.)
-   Verify work items exist in the project

## Security Best Practices

1. **Never commit PAT to source control**
2. Use environment variables for PAT storage
3. Keep PAT scope minimal (Work Items only)
4. Rotate PAT tokens periodically
5. Use secure credential managers for automation
6. Don't share PAT tokens

## API Rate Limits

Azure DevOps has rate limits. For large queries:

-   Use specific filters to reduce result sets
-   Limit Top parameter in searches
-   Add delays between batch operations if needed

## Requirements

-   PowerShell 7.0 or later
-   Azure DevOps account with appropriate permissions
-   Personal Access Token with Work Items scope
-   Network access to dev.azure.com

## Contributing

Feel free to extend this module with additional functions:

-   Attachments handling
-   Custom field support
-   Board/Sprint queries
-   Advanced WIQL queries

## License

This module is provided as-is for use with GitHub Copilot CLI.

## Support

For issues with:

-   **The module**: Check function parameters and initialization
-   **Azure DevOps API**: Refer to [Azure DevOps REST API documentation](https://learn.microsoft.com/en-us/rest/api/azure/devops/)
-   **GitHub Copilot**: Refer to GitHub Copilot CLI documentation
