# Quick Setup Guide for Azure DevOps Tools

## Prerequisites

-   PowerShell 7.0 or later
-   Azure DevOps account
-   Access to a project with work items

## Setup Steps

### Step 1: Generate Personal Access Token (PAT)

1. Go to your Azure DevOps organization: `https://dev.azure.com/YOUR-ORG`
2. Click your profile icon (top right) → **Personal Access Tokens**
3. Click **+ New Token**
4. Configure:
    - **Name**: "Copilot CLI Tool" (or any name)
    - **Organization**: Select your organization
    - **Expiration**: Choose duration (30-90 days recommended)
    - **Scopes**: Click "Show all scopes"
        - Expand **Work Items**
        - Check ✓ **Read, Write, & Manage**
5. Click **Create**
6. **IMPORTANT**: Copy the token immediately (it won't be shown again!)

### Step 2: Set Environment Variable

Choose one of these methods:

#### Option A: Temporary (Current Session Only)

```powershell
$env:AZURE_DEVOPS_PAT = "paste-your-token-here"
```

#### Option B: PowerShell Profile (Persistent)

```powershell
# Edit your profile
notepad $PROFILE

# Add this line (replace with your token):
$env:AZURE_DEVOPS_PAT = "your-token-here"

# Save and reload
. $PROFILE
```

#### Option C: Windows Environment Variable

```powershell
# Run PowerShell as Administrator
[Environment]::SetEnvironmentVariable("AZURE_DEVOPS_PAT", "your-token-here", "User")

# Restart PowerShell to load the variable
```

### Step 3: Import and Initialize Module

```powershell
# Import the module
Import-Module .\AzureDevOpsTools\AzureDevOpsTools.psd1

# Initialize with your organization and project
Initialize-AzureDevOps -Organization "your-org-name" -Project "your-project-name"
```

**To find your organization and project names:**

-   Look at your Azure DevOps URL: `https://dev.azure.com/{organization}/{project}`
-   Example: `https://dev.azure.com/contoso/MyApp`
    -   Organization: `contoso`
    -   Project: `MyApp`

### Step 4: Test the Connection

```powershell
# Try a simple search
Search-WorkItems -Top 5

# If this returns work items, you're all set!
```

## Adding to Your PowerShell Profile

For automatic loading every time you open PowerShell:

```powershell
# Edit your profile
notepad $PROFILE

# Add these lines:
Import-Module c:\Users\mshepherd\p\network\AzureDevOpsTools\AzureDevOpsTools.psd1
Initialize-AzureDevOps -Organization "your-org" -Project "your-project"
$env:AZURE_DEVOPS_PAT = "your-pat-token"

# Save and reload
. $PROFILE
```

## Verification Checklist

-   [ ] PowerShell 7+ installed (`$PSVersionTable.PSVersion`)
-   [ ] PAT generated with Work Items scope
-   [ ] AZURE_DEVOPS_PAT environment variable set
-   [ ] Module imported successfully
-   [ ] Connection initialized
-   [ ] Test search returns results

## Common Issues

### "PAT not found"

**Solution**: Set the AZURE_DEVOPS_PAT environment variable

### "Azure DevOps not initialized"

**Solution**: Run `Initialize-AzureDevOps -Organization "org" -Project "project"`

### "Failed to search work items: 401 Unauthorized"

**Solution**:

-   Verify PAT is correct
-   Ensure PAT has Work Items Read/Write scope
-   Check PAT hasn't expired

### "Failed to search work items: 404 Not Found"

**Solution**:

-   Verify organization name is correct
-   Verify project name is correct
-   Ensure you have access to the project

## Usage Examples

### Search for bugs

```powershell
Search-WorkItems -WorkItemType "Bug" -State "Active"
```

### Get details about a specific work item

```powershell
Get-WorkItem -Ids 12345
Get-WorkItemComments -Id 12345
```

### Update a work item

```powershell
Update-WorkItem -Id 12345 -State "Closed"
Add-WorkItemComment -Id 12345 -Comment "Fixed in latest release"
```

### Export to markdown

```powershell
Search-WorkItems -SearchText "feature-name" |
    Export-WorkItemsToMarkdown -OutputPath "report.md" -IncludeAcceptanceCriteria
```

## Security Best Practices

✓ **DO:**

-   Store PAT in environment variables
-   Use minimal required scopes (Work Items only)
-   Set expiration dates on PATs
-   Rotate PATs regularly

✗ **DON'T:**

-   Commit PAT to source control
-   Share PATs with others
-   Use overly broad scopes (like "Full Access")
-   Store PAT in plain text files

## Getting Help

Each function has detailed help:

```powershell
Get-Help Search-WorkItems -Full
Get-Help Update-WorkItem -Examples
Get-Help Export-WorkItemsToMarkdown -Detailed
```

## Next Steps

1. Run the examples script: `.\examples.ps1`
2. Review the skills in `.skills\` directory
3. Try using with GitHub Copilot CLI
4. Customize searches for your workflow

## Support

-   Azure DevOps API Docs: https://learn.microsoft.com/en-us/rest/api/azure/devops/
-   PowerShell Docs: https://learn.microsoft.com/en-us/powershell/
-   GitHub Copilot CLI: https://githubnext.com/projects/copilot-cli
