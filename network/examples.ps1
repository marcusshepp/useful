# Azure DevOps Tools - Example Usage Script
# This script demonstrates common workflows with the AzureDevOpsTools module

# Import the module
Import-Module .\AzureDevOpsTools\AzureDevOpsTools.psd1 -Force

# Initialize connection (replace with your org and project)
Write-Host "Initializing Azure DevOps connection..." -ForegroundColor Cyan
Initialize-AzureDevOps -Organization "your-org" -Project "your-project"

Write-Host "`nAzure DevOps Tools Module - Example Workflows`n" -ForegroundColor Green

# Example 1: Search for active bugs
Write-Host "Example 1: Finding active bugs" -ForegroundColor Yellow
$bugs = Search-WorkItems -WorkItemType "Bug" -State "Active" -Top 5
Write-Host "Found $($bugs.Count) active bugs"
$bugs | Format-Table Id, Title, AssignedTo, Priority -AutoSize

# Example 2: Search by text
Write-Host "`nExample 2: Searching for items related to 'authentication'" -ForegroundColor Yellow
$authItems = Search-WorkItems -SearchText "authentication" -Top 5
Write-Host "Found $($authItems.Count) items related to authentication"
$authItems | Format-Table Id, Type, Title, State -AutoSize

# Example 3: Get detailed information about a work item
Write-Host "`nExample 3: Getting details for a specific work item" -ForegroundColor Yellow
if ($bugs.Count -gt 0) {
    $itemId = $bugs[0].Id
    Write-Host "Getting details for work item $itemId..."
    
    $item = Get-WorkItem -Ids $itemId -ExpandRelations
    Write-Host "`nWork Item: [$($item.Id)] $($item.Title)"
    Write-Host "Type: $($item.Type)"
    Write-Host "State: $($item.State)"
    Write-Host "Assigned To: $($item.AssignedTo)"
    Write-Host "Created: $($item.CreatedDate)"
    
    # Get comments
    $comments = Get-WorkItemComments -Id $itemId
    Write-Host "`nComments: $($comments.Count)"
    $comments | Select-Object -First 3 | Format-Table CreatedBy, CreatedDate, Text -AutoSize
}

# Example 4: Find a feature and its children
Write-Host "`nExample 4: Finding a feature and all its work items" -ForegroundColor Yellow
Write-Host "Searching for features..." 
$features = Search-WorkItems -WorkItemType "Feature" -Top 1
if ($features.Count -gt 0) {
    $featureTitle = $features[0].Title
    Write-Host "Feature found: $featureTitle"
    
    $relatedWork = Get-RelatedWorkItems -Id $features[0].Id -RelationType "Child"
    Write-Host "Child items: $($relatedWork.Count)"
    $relatedWork | Format-Table Id, Type, Title, State -AutoSize
}

# Example 5: Search by assignment
Write-Host "`nExample 5: Finding work assigned to specific users" -ForegroundColor Yellow
$assignedItems = Search-WorkItems -State "Active" -Top 10
$byAssignee = $assignedItems | Group-Object AssignedTo | 
    Select-Object Name, Count | 
    Sort-Object Count -Descending
Write-Host "Active items by assignee:"
$byAssignee | Format-Table -AutoSize

# Example 6: Export to markdown
Write-Host "`nExample 6: Exporting work items to markdown" -ForegroundColor Yellow
$userStories = Search-WorkItems -WorkItemType "User Story" -State "Active" -Top 3
if ($userStories.Count -gt 0) {
    $exportPath = ".\active-user-stories.md"
    $result = $userStories | Export-WorkItemsToMarkdown -OutputPath $exportPath -IncludeAcceptanceCriteria
    Write-Host "Exported $($result.ItemCount) user stories to $($result.FilePath)"
}

# Example 7: Create a new work item (commented out to avoid creating test items)
Write-Host "`nExample 7: Creating a new work item (example - commented out)" -ForegroundColor Yellow
Write-Host "# To create a new bug:"
Write-Host "# New-WorkItem -Type 'Bug' -Title 'Example bug' -Description 'This is a test' -Priority 2"

# Example 8: Update a work item (commented out to avoid modifying items)
Write-Host "`nExample 8: Updating a work item (example - commented out)" -ForegroundColor Yellow
Write-Host "# To update a work item:"
Write-Host "# Update-WorkItem -Id 12345 -State 'Resolved' -Tags 'fixed,verified'"
Write-Host "# Add-WorkItemComment -Id 12345 -Comment 'Issue has been resolved'"

# Example 9: Complex search with multiple filters
Write-Host "`nExample 9: Complex search with filters" -ForegroundColor Yellow
$complexSearch = Search-WorkItems -WorkItemType "User Story" -State "Active" -Top 5
Write-Host "Active User Stories:"
$complexSearch | Select-Object Id, Title, State, AssignedTo, Effort | Format-Table -AutoSize

# Example 10: Summary statistics
Write-Host "`nExample 10: Project statistics" -ForegroundColor Yellow
$allItems = Search-WorkItems -Top 100

Write-Host "`nWork Items by Type:"
$allItems | Group-Object Type | 
    Select-Object Name, Count | 
    Sort-Object Count -Descending |
    Format-Table -AutoSize

Write-Host "Work Items by State:"
$allItems | Group-Object State | 
    Select-Object Name, Count | 
    Sort-Object Count -Descending |
    Format-Table -AutoSize

Write-Host "`n✓ Examples completed!" -ForegroundColor Green
Write-Host "`nNote: Update the Initialize-AzureDevOps parameters with your organization and project." -ForegroundColor Cyan
Write-Host "Set the AZURE_DEVOPS_PAT environment variable before running this script." -ForegroundColor Cyan
