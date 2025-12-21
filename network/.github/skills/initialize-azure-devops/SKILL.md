---
name: initialize-azure-devops
description: Set up connection to Azure DevOps organization and project. Required before using any Azure DevOps commands. Use when starting a new session.
---

# Initialize Azure DevOps Connection

Set up connection to Azure DevOps organization and project. This must be called before using any other Azure DevOps commands.

## When to Use

- At the start of any Azure DevOps work
- After importing the AzureDevOpsTools module
- When switching between organizations or projects
- When you get errors about Azure DevOps not being initialized

## Prerequisites

- AzureDevOpsTools module must be imported
- Personal Access Token (PAT) must be available via:
  - Parameter: `-PAT "your-token"`
  - Environment variable: `$env:AZURE_DEVOPS_PAT`

## Examples

### Initialize with environment variable

```powershell
# PAT is in $env:AZURE_DEVOPS_PAT
Initialize-AzureDevOps -Organization "myorg" -Project "myproject"
```

### Initialize with PAT parameter

```powershell
Initialize-AzureDevOps -Organization "myorg" -Project "myproject" -PAT "your-pat-token"
```

### Common setup in profile

```powershell
Import-Module AzureDevOpsTools
Initialize-AzureDevOps -Organization "Legislative" -Project "LegBone"
```

## Function

### Initialize-AzureDevOps

Configures the module with organization and project details and validates PAT.

## Parameters

- **Organization**: Azure DevOps organization name (required)
- **Project**: Project name within the organization (required)
- **PAT**: Personal Access Token (optional if set in environment)

## Output

Displays confirmation message when successfully initialized. Throws error if PAT is missing or invalid.

## Tips for Copilot

- Always call this first in a new session
- Organization and Project are usually consistent for a user
- PAT should come from environment variable for security
- Can be called multiple times to switch contexts
- Check for initialization errors before proceeding
