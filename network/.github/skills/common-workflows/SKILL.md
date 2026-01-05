---
name: common-workflows
description: Common patterns and workflows for Azure DevOps and database queries. Use to avoid inefficient searches and tangents.
---

# Common Workflows

This skill documents the most efficient patterns for common tasks.

## Azure DevOps Workflows

### Finding Tickets by Topic

**Pattern:** Use Search-WorkItems with specific text and filters

```powershell
# Find stories about "eb sign report"
Search-WorkItems -SearchText "eb sign report" -WorkItemType "User Story" -Top 20

# Get the most recent one
$items = Search-WorkItems -SearchText "eb sign report" -WorkItemType "User Story" -Top 20
$latest = $items | Sort-Object ChangedDate -Descending | Select-Object -First 1
```

**Common pitfall:** Searching for multiple terms at once can cause timeouts. Keep searches specific.

### Getting Ticket Details

**Pattern:** Use Get-WorkItem once you have the ID

```powershell
# Get full details including acceptance criteria
$item = Get-WorkItem -Ids 5015
Write-Output $item.WebUrl
Write-Output $item.AcceptanceCriteria
```

### Searching with Date Sorting

**Pattern:** Search first, then sort by date in PowerShell (not in Azure DevOps query)

```powershell
# CORRECT - Sort after getting results
$items = Search-WorkItems -SearchText "committee" -WorkItemType "User Story" -Top 20
$sorted = $items | Sort-Object ChangedDate -Descending

# INCORRECT - Don't try to sort in the search parameters
# Search-WorkItems doesn't have -SortBy parameter
```

## Database Workflows

### Committee Queries

**Important:** Committees are in the **Legislature (M2-QA)** database, NOT Eva QA

```powershell
# CORRECT - Use M2-QA for committees
Invoke-EvaSql -Environment M2-QA -Query "SELECT TOP 5 CommitteeID, CommitteeName FROM Committee ORDER BY CommitteeID DESC"

# INCORRECT - Eva QA doesn't have a Committee table
# Invoke-EvaSql -Environment QA -Query "SELECT * FROM Committee"
```

**Note:** Committee table doesn't have CreatedDate. Use CommitteeID as proxy for creation order (higher ID = more recent).

### Session Queries

**Important:** Sessions are in the **Eva QA** database, NOT M2-QA

```powershell
# CORRECT - Use QA for sessions
Invoke-EvaSql -Environment QA -Query "SELECT TOP 5 * FROM sessions ORDER BY SessionID DESC"

# INCORRECT - M2-QA doesn't have sessions
# Invoke-EvaSql -Environment M2-QA -Query "SELECT * FROM sessions"
```

### Finding Table Names

**Pattern:** Use INFORMATION_SCHEMA when uncertain

```powershell
# Find tables with "Committee" in the name
Invoke-EvaSql -Environment M2-QA -Query "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%Committee%'"

# Find columns in a specific table
Invoke-EvaSql -Environment M2-QA -Query "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Committee'"
```

## Quick Reference

| Data Type | Environment | Database |
|-----------|-------------|----------|
| Committees | M2-QA | Legislature |
| Committee Meetings | M2-QA | Legislature |
| Sessions | QA | Eva_QA |
| Committee Reports | QA | Eva_QA |
| Meeting Notices | QA | Eva_QA |
| Work Items | Azure DevOps | Legislative/LegBone |

## Efficiency Tips

1. **Always load env vars first** - Saves authentication errors
2. **Check which database** - Eva vs M2-QA before querying
3. **Use TOP N** - Limit results to avoid timeouts
4. **Sort in PowerShell** - Don't rely on Azure DevOps query sorting
5. **Get IDs first** - Then use Get-WorkItem for full details
