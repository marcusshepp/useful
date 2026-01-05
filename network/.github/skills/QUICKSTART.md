# Quick Start Guide for This Workspace

When opening a new Copilot session in this directory, run these commands first:

## 1. Load Environment Variables

```powershell
# Load credentials from .env file
$env:AZURE_DEVOPS_PAT = (Get-Content .env | Select-String "AZURE_DEVOPS_PAT").ToString().Split('=')[1]
$env:AZURE_DEVOPS_ORG = "Legislative"
$env:AZURE_DEVOPS_PROJECT = "LegBone"
$env:AZURE_DEVOPS_USERNAME = "mshepherd"
$env:EVA_QA_PASSWORD = "eva4eva"
$env:M2_QA_PASSWORD = "ThisIsQA!"
```

## 2. Import Modules

```powershell
cd C:\Users\mshepherd\p\useful\network
Import-Module .\AzureDevOpsTools\AzureDevOpsTools.psd1 -Force
Import-Module .\EvaSql.psm1 -Force
```

## 3. Initialize Azure DevOps

```powershell
Initialize-AzureDevOps
```

## All-in-One Setup

```powershell
cd C:\Users\mshepherd\p\useful\network
$env:AZURE_DEVOPS_PAT = (Get-Content .env | Select-String "AZURE_DEVOPS_PAT").ToString().Split('=')[1]
$env:AZURE_DEVOPS_ORG = "Legislative"
$env:AZURE_DEVOPS_PROJECT = "LegBone"
$env:AZURE_DEVOPS_USERNAME = "mshepherd"
$env:EVA_QA_PASSWORD = "eva4eva"
$env:M2_QA_PASSWORD = "ThisIsQA!"
Import-Module .\AzureDevOpsTools\AzureDevOpsTools.psd1 -Force
Import-Module .\EvaSql.psm1 -Force
Initialize-AzureDevOps
```

---

## Common Tasks

### Azure DevOps Tickets

**Search for tickets:**
```powershell
Search-WorkItems -SearchText "eb sign report" -WorkItemType "User Story" -Top 10
```

**Get ticket details:**
```powershell
Get-WorkItem -Ids 5015
```

### Database Queries

**Eva QA Database (Sessions, Committee Reports):**
```powershell
Invoke-EvaSql -Environment QA -Query "SELECT TOP 5 * FROM sessions ORDER BY SessionID DESC"
```

**Legislature M2 Database (Committees, Members):**
```powershell
Invoke-EvaSql -Environment M2-QA -Query "SELECT TOP 5 CommitteeID, CommitteeName FROM Committee ORDER BY CommitteeID DESC"
```

---

## Important Notes

- **Azure DevOps Org:** Legislative
- **Azure DevOps Project:** LegBone
- **Eva DB:** Use `-Environment QA` (Eva_QA database)
- **Legislature DB:** Use `-Environment M2-QA` (Legislature database)
- **Committees are in M2-QA**, not Eva QA
- **Sessions are in Eva QA**, not M2-QA
