# Azure DevOps Tools Module
# For use with GitHub Copilot CLI to manage work items

#region Module State
$Script:AzureDevOpsConfig = @{
    Organization = $null
    Project = $null
    PAT = $null
    BaseUrl = $null
    Headers = $null
}
#endregion

#region Authentication

<#
.SYNOPSIS
    Initialize Azure DevOps connection settings.
.DESCRIPTION
    Sets up the organization, project, and authentication for Azure DevOps API calls.
.PARAMETER Organization
    The Azure DevOps organization name.
.PARAMETER Project
    The Azure DevOps project name.
.PARAMETER PAT
    Personal Access Token. If not provided, will use AZURE_DEVOPS_PAT environment variable.
.EXAMPLE
    Initialize-AzureDevOps -Organization "myorg" -Project "myproject"
#>
function Initialize-AzureDevOps {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$Organization,
        
        [Parameter(Mandatory = $false)]
        [string]$Project,
        
        [Parameter(Mandatory = $false)]
        [string]$PAT
    )
    
    # Use env vars as defaults
    if (-not $Organization) {
        $Organization = $env:AZURE_DEVOPS_ORG
        if (-not $Organization) {
            throw "Organization not provided and AZURE_DEVOPS_ORG environment variable not set"
        }
    }
    
    if (-not $Project) {
        $Project = $env:AZURE_DEVOPS_PROJECT
        if (-not $Project) {
            throw "Project not provided and AZURE_DEVOPS_PROJECT environment variable not set"
        }
    }
    
    if (-not $PAT) {
        $PAT = $env:AZURE_DEVOPS_PAT
        if (-not $PAT) {
            throw "PAT not provided and AZURE_DEVOPS_PAT environment variable not set"
        }
    }
    
    $Script:AzureDevOpsConfig.Organization = $Organization
    $Script:AzureDevOpsConfig.Project = $Project
    $Script:AzureDevOpsConfig.PAT = $PAT
    $Script:AzureDevOpsConfig.BaseUrl = "https://dev.azure.com/$Organization/$Project/_apis"
    
    # Create auth header
    $base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$PAT"))
    $Script:AzureDevOpsConfig.Headers = @{
        Authorization = "Basic $base64AuthInfo"
        'Content-Type' = 'application/json'
    }
    
    Write-Verbose "Initialized Azure DevOps connection to $Organization/$Project"
}

function Test-AzureDevOpsInitialized {
    if (-not $Script:AzureDevOpsConfig.BaseUrl) {
        throw "Azure DevOps not initialized. Call Initialize-AzureDevOps first."
    }
}

#endregion

#region Search Functions

<#
.SYNOPSIS
    Search for work items using text search and filters.
.DESCRIPTION
    Searches Azure DevOps work items across title and description fields with optional filters.
.PARAMETER SearchText
    Text to search for in title and description fields.
.PARAMETER WorkItemType
    Filter by work item type (Bug, User Story, Task, Feature, etc.).
.PARAMETER State
    Filter by state (New, Active, Resolved, Closed, etc.).
.PARAMETER AssignedTo
    Filter by assigned user (display name or email).
.PARAMETER AreaPath
    Filter by area path.
.PARAMETER IterationPath
    Filter by iteration path.
.PARAMETER Tags
    Filter by tags (comma-separated).
.PARAMETER Top
    Maximum number of results to return (default 200).
.EXAMPLE
    Search-WorkItems -SearchText "PDF export" -WorkItemType "Bug" -State "Active"
#>
function Search-WorkItems {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$SearchText,
        
        [Parameter(Mandatory = $false)]
        [string]$WorkItemType,
        
        [Parameter(Mandatory = $false)]
        [string]$State,
        
        [Parameter(Mandatory = $false)]
        [string]$AssignedTo,
        
        [Parameter(Mandatory = $false)]
        [string]$AreaPath,
        
        [Parameter(Mandatory = $false)]
        [string]$IterationPath,
        
        [Parameter(Mandatory = $false)]
        [string]$Tags,
        
        [Parameter(Mandatory = $false)]
        [int]$Top = 200
    )
    
    Test-AzureDevOpsInitialized
    
    # Build WIQL query
    $whereConditions = @()
    $whereConditions += "[System.TeamProject] = '$($Script:AzureDevOpsConfig.Project)'"
    
    if ($SearchText) {
        $whereConditions += "([System.Title] CONTAINS '$SearchText' OR [System.Description] CONTAINS '$SearchText')"
    }
    
    if ($WorkItemType) {
        $whereConditions += "[System.WorkItemType] = '$WorkItemType'"
    }
    
    if ($State) {
        $whereConditions += "[System.State] = '$State'"
    }
    
    if ($AssignedTo) {
        $whereConditions += "[System.AssignedTo] = '$AssignedTo'"
    }
    
    if ($AreaPath) {
        $whereConditions += "[System.AreaPath] UNDER '$AreaPath'"
    }
    
    if ($IterationPath) {
        $whereConditions += "[System.IterationPath] UNDER '$IterationPath'"
    }
    
    if ($Tags) {
        $whereConditions += "[System.Tags] CONTAINS '$Tags'"
    }
    
    $whereClause = $whereConditions -join " AND "
    $wiql = "SELECT [System.Id] FROM WorkItems WHERE $whereClause ORDER BY [System.ChangedDate] DESC"
    
    $body = @{
        query = $wiql
    } | ConvertTo-Json
    
    $url = "$($Script:AzureDevOpsConfig.BaseUrl)/wit/wiql?api-version=7.1"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers $Script:AzureDevOpsConfig.Headers -Body $body
        
        if ($response.workItems.Count -eq 0) {
            Write-Verbose "No work items found matching criteria"
            return @()
        }
        
        # Get full details for all work items
        $ids = $response.workItems.id | Select-Object -First $Top
        return Get-WorkItem -Ids $ids -ExpandRelations
    }
    catch {
        Write-Error "Failed to search work items: $_"
        throw
    }
}

<#
.SYNOPSIS
    Get full details for one or more work items by ID.
.DESCRIPTION
    Fetches complete work item details including fields, comments, and relations.
.PARAMETER Ids
    Array of work item IDs to fetch.
.PARAMETER ExpandRelations
    Include related work items information.
.EXAMPLE
    Get-WorkItem -Ids 12345,67890 -ExpandRelations
#>
function Get-WorkItem {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [int[]]$Ids,
        
        [Parameter(Mandatory = $false)]
        [switch]$ExpandRelations
    )
    
    begin {
        Test-AzureDevOpsInitialized
        $allIds = @()
    }
    
    process {
        $allIds += $Ids
    }
    
    end {
        if ($allIds.Count -eq 0) {
            return @()
        }
        
        $idsParam = $allIds -join ','
        $expand = if ($ExpandRelations) { '&$expand=relations' } else { '' }
        $url = "$($Script:AzureDevOpsConfig.BaseUrl)/wit/workitems?ids=$idsParam&api-version=7.1$expand"
        
        try {
            $response = Invoke-RestMethod -Uri $url -Method Get -Headers $Script:AzureDevOpsConfig.Headers
            
            # Transform to more user-friendly format
            $workItems = $response.value | ForEach-Object {
                $fields = $_.fields
                
                [PSCustomObject]@{
                    Id = $_.id
                    Type = $fields.'System.WorkItemType'
                    Title = $fields.'System.Title'
                    State = $fields.'System.State'
                    AssignedTo = $fields.'System.AssignedTo'.displayName
                    CreatedBy = $fields.'System.CreatedBy'.displayName
                    CreatedDate = $fields.'System.CreatedDate'
                    ChangedDate = $fields.'System.ChangedDate'
                    Description = $fields.'System.Description'
                    AcceptanceCriteria = $fields.'Microsoft.VSTS.Common.AcceptanceCriteria'
                    Priority = $fields.'Microsoft.VSTS.Common.Priority'
                    Effort = $fields.'Microsoft.VSTS.Scheduling.Effort'
                    Tags = $fields.'System.Tags'
                    AreaPath = $fields.'System.AreaPath'
                    IterationPath = $fields.'System.IterationPath'
                    Url = $_.url
                    WebUrl = $fields.'System.TeamProject' ? "https://dev.azure.com/$($Script:AzureDevOpsConfig.Organization)/$($fields.'System.TeamProject')/_workitems/edit/$($_.id)" : $null
                    Relations = $_.relations
                    AllFields = $fields
                }
            }
            
            return $workItems
        }
        catch {
            Write-Error "Failed to get work items: $_"
            throw
        }
    }
}

<#
.SYNOPSIS
    Find a feature and all its child work items.
.DESCRIPTION
    Searches for a feature by text and returns it along with all child items.
.PARAMETER SearchText
    Text to search for in feature title.
.EXAMPLE
    Get-WorkItemsByFeature -SearchText "authentication"
#>
function Get-WorkItemsByFeature {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$SearchText
    )
    
    Test-AzureDevOpsInitialized
    
    # Find the feature
    $features = Search-WorkItems -SearchText $SearchText -WorkItemType "Feature"
    
    if ($features.Count -eq 0) {
        Write-Warning "No feature found matching '$SearchText'"
        return @()
    }
    
    $results = @()
    foreach ($feature in $features) {
        $results += $feature
        
        # Get all children
        $children = Get-RelatedWorkItems -Id $feature.Id -RelationType "Child"
        $results += $children
    }
    
    return $results
}

<#
.SYNOPSIS
    Get work items related to a specific work item.
.DESCRIPTION
    Retrieves parent, child, or related work items for a given work item ID.
.PARAMETER Id
    The work item ID.
.PARAMETER RelationType
    Type of relation: Parent, Child, Related, All (default: All).
.EXAMPLE
    Get-RelatedWorkItems -Id 12345 -RelationType "Child"
#>
function Get-RelatedWorkItems {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [int]$Id,
        
        [Parameter(Mandatory = $false)]
        [ValidateSet('Parent', 'Child', 'Related', 'All')]
        [string]$RelationType = 'All'
    )
    
    Test-AzureDevOpsInitialized
    
    # Get the work item with relations
    $workItem = Get-WorkItem -Ids $Id -ExpandRelations
    
    if (-not $workItem.Relations) {
        return @()
    }
    
    # Filter relations based on type
    $relations = $workItem.Relations | Where-Object {
        if ($RelationType -eq 'All') { return $true }
        
        $relType = $_.rel
        switch ($RelationType) {
            'Parent' { $relType -eq 'System.LinkTypes.Hierarchy-Reverse' }
            'Child' { $relType -eq 'System.LinkTypes.Hierarchy-Forward' }
            'Related' { $relType -eq 'System.LinkTypes.Related' }
        }
    }
    
    # Extract work item IDs from relation URLs
    $relatedIds = $relations | Where-Object { $_.url -match '/workitems/(\d+)' } | ForEach-Object {
        if ($_.url -match '/workitems/(\d+)') {
            [int]$Matches[1]
        }
    }
    
    if ($relatedIds.Count -eq 0) {
        return @()
    }
    
    return Get-WorkItem -Ids $relatedIds -ExpandRelations
}

#endregion

#region Details Functions

<#
.SYNOPSIS
    Get all comments for a work item.
.DESCRIPTION
    Retrieves all comments/discussions for a specific work item.
.PARAMETER Id
    The work item ID.
.EXAMPLE
    Get-WorkItemComments -Id 12345
#>
function Get-WorkItemComments {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [int]$Id
    )
    
    Test-AzureDevOpsInitialized
    
    $url = "$($Script:AzureDevOpsConfig.BaseUrl)/wit/workitems/$Id/comments?api-version=7.1"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers $Script:AzureDevOpsConfig.Headers
        
        return $response.comments | ForEach-Object {
            [PSCustomObject]@{
                Id = $_.id
                Text = $_.text
                CreatedBy = $_.createdBy.displayName
                CreatedDate = $_.createdDate
                ModifiedBy = $_.modifiedBy.displayName
                ModifiedDate = $_.modifiedDate
            }
        }
    }
    catch {
        Write-Error "Failed to get comments for work item $Id : $_"
        throw
    }
}

<#
.SYNOPSIS
    Get revision history for a work item.
.DESCRIPTION
    Retrieves all changes made to a work item over time.
.PARAMETER Id
    The work item ID.
.EXAMPLE
    Get-WorkItemHistory -Id 12345
#>
function Get-WorkItemHistory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [int]$Id
    )
    
    Test-AzureDevOpsInitialized
    
    $url = "$($Script:AzureDevOpsConfig.BaseUrl)/wit/workitems/$Id/updates?api-version=7.1"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers $Script:AzureDevOpsConfig.Headers
        
        return $response.value | ForEach-Object {
            [PSCustomObject]@{
                Revision = $_.rev
                RevisedBy = $_.revisedBy.displayName
                RevisedDate = $_.revisedDate
                Fields = $_.fields
            }
        }
    }
    catch {
        Write-Error "Failed to get history for work item $Id : $_"
        throw
    }
}

#endregion

#region Update Functions

<#
.SYNOPSIS
    Update a work item's fields.
.DESCRIPTION
    Modifies one or more fields of an existing work item.
.PARAMETER Id
    The work item ID.
.PARAMETER Title
    New title for the work item.
.PARAMETER State
    New state (New, Active, Resolved, Closed, etc.).
.PARAMETER AssignedTo
    Assign to user (email or display name).
.PARAMETER Description
    New description.
.PARAMETER AcceptanceCriteria
    New acceptance criteria.
.PARAMETER Tags
    Tags to set (comma-separated).
.PARAMETER Priority
    Priority value.
.PARAMETER Effort
    Effort/story points.
.EXAMPLE
    Update-WorkItem -Id 12345 -State "Closed" -Tags "bug-fix,completed"
#>
function Update-WorkItem {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [int]$Id,
        
        [Parameter(Mandatory = $false)]
        [string]$Title,
        
        [Parameter(Mandatory = $false)]
        [string]$State,
        
        [Parameter(Mandatory = $false)]
        [string]$AssignedTo,
        
        [Parameter(Mandatory = $false)]
        [string]$Description,
        
        [Parameter(Mandatory = $false)]
        [string]$AcceptanceCriteria,
        
        [Parameter(Mandatory = $false)]
        [string]$Tags,
        
        [Parameter(Mandatory = $false)]
        [int]$Priority,
        
        [Parameter(Mandatory = $false)]
        [int]$Effort
    )
    
    Test-AzureDevOpsInitialized
    
    # Build JSON Patch document
    $patchOps = @()
    
    if ($Title) {
        $patchOps += @{
            op = "add"
            path = "/fields/System.Title"
            value = $Title
        }
    }
    
    if ($State) {
        $patchOps += @{
            op = "add"
            path = "/fields/System.State"
            value = $State
        }
    }
    
    if ($AssignedTo) {
        $patchOps += @{
            op = "add"
            path = "/fields/System.AssignedTo"
            value = $AssignedTo
        }
    }
    
    if ($Description) {
        $patchOps += @{
            op = "add"
            path = "/fields/System.Description"
            value = $Description
        }
    }
    
    if ($AcceptanceCriteria) {
        $patchOps += @{
            op = "add"
            path = "/fields/Microsoft.VSTS.Common.AcceptanceCriteria"
            value = $AcceptanceCriteria
        }
    }
    
    if ($Tags) {
        $patchOps += @{
            op = "add"
            path = "/fields/System.Tags"
            value = $Tags
        }
    }
    
    if ($PSBoundParameters.ContainsKey('Priority')) {
        $patchOps += @{
            op = "add"
            path = "/fields/Microsoft.VSTS.Common.Priority"
            value = $Priority
        }
    }
    
    if ($PSBoundParameters.ContainsKey('Effort')) {
        $patchOps += @{
            op = "add"
            path = "/fields/Microsoft.VSTS.Scheduling.Effort"
            value = $Effort
        }
    }
    
    if ($patchOps.Count -eq 0) {
        Write-Warning "No fields to update specified"
        return
    }
    
    $body = $patchOps | ConvertTo-Json -Depth 10
    $url = "$($Script:AzureDevOpsConfig.BaseUrl)/wit/workitems/$Id`?api-version=7.1"
    
    $headers = $Script:AzureDevOpsConfig.Headers.Clone()
    $headers.'Content-Type' = 'application/json-patch+json'
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Patch -Headers $headers -Body $body
        Write-Verbose "Updated work item $Id"
        return Get-WorkItem -Ids $Id
    }
    catch {
        Write-Error "Failed to update work item $Id : $_"
        throw
    }
}

<#
.SYNOPSIS
    Add a comment to a work item.
.DESCRIPTION
    Adds a new comment/discussion to a work item.
.PARAMETER Id
    The work item ID.
.PARAMETER Comment
    The comment text.
.EXAMPLE
    Add-WorkItemComment -Id 12345 -Comment "Fixed in PR #789"
#>
function Add-WorkItemComment {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [int]$Id,
        
        [Parameter(Mandatory = $true)]
        [string]$Comment
    )
    
    Test-AzureDevOpsInitialized
    
    $body = @{
        text = $Comment
    } | ConvertTo-Json
    
    $url = "$($Script:AzureDevOpsConfig.BaseUrl)/wit/workitems/$Id/comments?api-version=7.1"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers $Script:AzureDevOpsConfig.Headers -Body $body
        Write-Verbose "Added comment to work item $Id"
        return $response
    }
    catch {
        Write-Error "Failed to add comment to work item $Id : $_"
        throw
    }
}

<#
.SYNOPSIS
    Create a new work item.
.DESCRIPTION
    Creates a new work item with specified fields.
.PARAMETER Type
    Work item type (Bug, User Story, Task, Feature, etc.).
.PARAMETER Title
    Title for the work item.
.PARAMETER Description
    Description text.
.PARAMETER AssignedTo
    Assign to user (email or display name).
.PARAMETER ParentId
    ID of parent work item to link to.
.PARAMETER Tags
    Tags (comma-separated).
.PARAMETER Priority
    Priority value.
.PARAMETER Effort
    Effort/story points.
.EXAMPLE
    New-WorkItem -Type "Bug" -Title "Login fails" -Priority 1 -AssignedTo "user@example.com"
#>
function New-WorkItem {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Type,
        
        [Parameter(Mandatory = $true)]
        [string]$Title,
        
        [Parameter(Mandatory = $false)]
        [string]$Description,
        
        [Parameter(Mandatory = $false)]
        [string]$AssignedTo,
        
        [Parameter(Mandatory = $false)]
        [int]$ParentId,
        
        [Parameter(Mandatory = $false)]
        [string]$Tags,
        
        [Parameter(Mandatory = $false)]
        [int]$Priority,
        
        [Parameter(Mandatory = $false)]
        [int]$Effort
    )
    
    Test-AzureDevOpsInitialized
    
    # Build JSON Patch document
    $patchOps = @(
        @{
            op = "add"
            path = "/fields/System.Title"
            value = $Title
        }
    )
    
    if ($Description) {
        $patchOps += @{
            op = "add"
            path = "/fields/System.Description"
            value = $Description
        }
    }
    
    if ($AssignedTo) {
        $patchOps += @{
            op = "add"
            path = "/fields/System.AssignedTo"
            value = $AssignedTo
        }
    }
    
    if ($Tags) {
        $patchOps += @{
            op = "add"
            path = "/fields/System.Tags"
            value = $Tags
        }
    }
    
    if ($PSBoundParameters.ContainsKey('Priority')) {
        $patchOps += @{
            op = "add"
            path = "/fields/Microsoft.VSTS.Common.Priority"
            value = $Priority
        }
    }
    
    if ($PSBoundParameters.ContainsKey('Effort')) {
        $patchOps += @{
            op = "add"
            path = "/fields/Microsoft.VSTS.Scheduling.Effort"
            value = $Effort
        }
    }
    
    # Add parent link if specified
    if ($ParentId) {
        $patchOps += @{
            op = "add"
            path = "/relations/-"
            value = @{
                rel = "System.LinkTypes.Hierarchy-Reverse"
                url = "https://dev.azure.com/$($Script:AzureDevOpsConfig.Organization)/_apis/wit/workitems/$ParentId"
            }
        }
    }
    
    $body = $patchOps | ConvertTo-Json -Depth 10
    $url = "$($Script:AzureDevOpsConfig.BaseUrl)/wit/workitems/`$$Type`?api-version=7.1"
    
    $headers = $Script:AzureDevOpsConfig.Headers.Clone()
    $headers.'Content-Type' = 'application/json-patch+json'
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
        Write-Verbose "Created work item $($response.id)"
        return Get-WorkItem -Ids $response.id
    }
    catch {
        Write-Error "Failed to create work item: $_"
        throw
    }
}

#endregion

#region Export Functions

<#
.SYNOPSIS
    Export work items to a markdown file.
.DESCRIPTION
    Generates a markdown report of work items with optional acceptance criteria.
.PARAMETER WorkItems
    Array of work items to export (from pipeline).
.PARAMETER OutputPath
    Path to save the markdown file.
.PARAMETER IncludeAcceptanceCriteria
    Include acceptance criteria in the export.
.PARAMETER IncludeDescription
    Include description in the export.
.PARAMETER IncludeComments
    Include comments in the export.
.EXAMPLE
    Search-WorkItems -SearchText "auth" | Export-WorkItemsToMarkdown -OutputPath "auth-items.md" -IncludeAcceptanceCriteria
#>
function Export-WorkItemsToMarkdown {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [object[]]$WorkItems,
        
        [Parameter(Mandatory = $true)]
        [string]$OutputPath,
        
        [Parameter(Mandatory = $false)]
        [switch]$IncludeAcceptanceCriteria,
        
        [Parameter(Mandatory = $false)]
        [switch]$IncludeDescription,
        
        [Parameter(Mandatory = $false)]
        [switch]$IncludeComments
    )
    
    begin {
        Test-AzureDevOpsInitialized
        $allWorkItems = @()
    }
    
    process {
        $allWorkItems += $WorkItems
    }
    
    end {
        $markdown = @()
        $markdown += "# Work Items Export"
        $markdown += ""
        $markdown += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        $markdown += ""
        $markdown += "---"
        $markdown += ""
        
        foreach ($item in $allWorkItems) {
            $markdown += "## [$($item.Id)] $($item.Title)"
            $markdown += ""
            $markdown += "**Type:** $($item.Type) | **State:** $($item.State)"
            $markdown += ""
            $markdown += "**Assigned To:** $($item.AssignedTo ?? 'Unassigned')"
            $markdown += ""
            
            if ($item.Tags) {
                $markdown += "**Tags:** $($item.Tags)"
                $markdown += ""
            }
            
            if ($item.WebUrl) {
                $markdown += "[View in Azure DevOps]($($item.WebUrl))"
                $markdown += ""
            }
            
            if ($IncludeDescription -and $item.Description) {
                $markdown += "### Description"
                $markdown += ""
                # Strip HTML tags for cleaner markdown
                $cleanDesc = $item.Description -replace '<[^>]+>', ''
                $markdown += $cleanDesc
                $markdown += ""
            }
            
            if ($IncludeAcceptanceCriteria -and $item.AcceptanceCriteria) {
                $markdown += "### Acceptance Criteria"
                $markdown += ""
                # Strip HTML tags for cleaner markdown
                $cleanAC = $item.AcceptanceCriteria -replace '<[^>]+>', ''
                $markdown += $cleanAC
                $markdown += ""
            }
            
            if ($IncludeComments) {
                $comments = Get-WorkItemComments -Id $item.Id
                if ($comments.Count -gt 0) {
                    $markdown += "### Comments"
                    $markdown += ""
                    foreach ($comment in $comments) {
                        $markdown += "**$($comment.CreatedBy)** ($($comment.CreatedDate)):"
                        $markdown += ""
                        $markdown += $comment.Text
                        $markdown += ""
                    }
                }
            }
            
            $markdown += "---"
            $markdown += ""
        }
        
        $markdown | Out-File -FilePath $OutputPath -Encoding utf8
        Write-Verbose "Exported $($allWorkItems.Count) work items to $OutputPath"
        
        return [PSCustomObject]@{
            FilePath = $OutputPath
            ItemCount = $allWorkItems.Count
        }
    }
}

#endregion

#region Pull Request Functions

<#
.SYNOPSIS
    Get pull requests from Azure DevOps.
.DESCRIPTION
    Retrieves pull requests with various filter options.
.PARAMETER Status
    Filter by PR status: Active, Completed, Abandoned, All. Default is Active.
.PARAMETER CreatedBy
    Filter by creator username or email.
.PARAMETER SourceBranch
    Filter by source branch name.
.PARAMETER TargetBranch
    Filter by target branch name (default is main/master).
.PARAMETER RepositoryName
    Repository name. If not provided, searches all repos in the project.
.PARAMETER Top
    Maximum number of results to return. Default is 100.
.EXAMPLE
    Get-PullRequests -Status Active
.EXAMPLE
    Get-PullRequests -CreatedBy "mshepherd" -Status Active
.EXAMPLE
    Get-PullRequests -Status All -Top 50
#>
function Get-PullRequests {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [ValidateSet('Active', 'Completed', 'Abandoned', 'All')]
        [string]$Status = 'Active',
        
        [Parameter(Mandatory = $false)]
        [string]$CreatedBy,
        
        [Parameter(Mandatory = $false)]
        [string]$SourceBranch,
        
        [Parameter(Mandatory = $false)]
        [string]$TargetBranch,
        
        [Parameter(Mandatory = $false)]
        [string]$RepositoryName,
        
        [Parameter(Mandatory = $false)]
        [int]$Top = 100
    )
    
    Test-AzureDevOpsInitialized
    
    try {
        # Build the API URL
        $org = $Script:AzureDevOpsConfig.Organization
        $project = $Script:AzureDevOpsConfig.Project
        
        if ($RepositoryName) {
            $apiUrl = "https://dev.azure.com/$org/$project/_apis/git/repositories/$RepositoryName/pullrequests?api-version=7.0"
        } else {
            $apiUrl = "https://dev.azure.com/$org/$project/_apis/git/pullrequests?api-version=7.0"
        }
        
        # Add search criteria
        $criteria = @()
        
        if ($Status -ne 'All') {
            $criteria += "searchCriteria.status=$Status"
        }
        
        if ($CreatedBy) {
            $criteria += "searchCriteria.creatorId=$CreatedBy"
        }
        
        if ($SourceBranch) {
            $criteria += "searchCriteria.sourceRefName=refs/heads/$SourceBranch"
        }
        
        if ($TargetBranch) {
            $criteria += "searchCriteria.targetRefName=refs/heads/$TargetBranch"
        }
        
        $criteria += "`$top=$Top"
        
        if ($criteria.Count -gt 0) {
            $apiUrl += "&" + ($criteria -join "&")
        }
        
        Write-Verbose "Getting pull requests from: $apiUrl"
        
        $response = Invoke-RestMethod -Uri $apiUrl -Headers $Script:AzureDevOpsConfig.Headers -Method Get
        
        $prs = $response.value | ForEach-Object {
            [PSCustomObject]@{
                PullRequestId = $_.pullRequestId
                Title = $_.title
                Description = $_.description
                Status = $_.status
                CreatedBy = $_.createdBy.displayName
                CreatedByEmail = $_.createdBy.uniqueName
                CreatedDate = $_.creationDate
                SourceBranch = $_.sourceRefName -replace '^refs/heads/', ''
                TargetBranch = $_.targetRefName -replace '^refs/heads/', ''
                Repository = $_.repository.name
                IsDraft = $_.isDraft
                MergeStatus = $_.mergeStatus
                Url = $_.url
                WebUrl = "https://dev.azure.com/$org/$project/_git/$($_.repository.name)/pullrequest/$($_.pullRequestId)"
            }
        }
        
        # Apply CreatedBy filter if specified (filter by display name or email)
        if ($CreatedBy) {
            $prs = $prs | Where-Object { 
                $_.CreatedBy -like "*$CreatedBy*" -or 
                $_.CreatedByEmail -like "*$CreatedBy*" 
            }
        }
        
        Write-Verbose "Found $($prs.Count) pull requests"
        return $prs
        
    } catch {
        Write-Error "Failed to get pull requests: $($_.Exception.Message)"
    }
}

<#
.SYNOPSIS
    Get detailed information about a specific pull request.
.DESCRIPTION
    Retrieves full details of a pull request including reviewers, work items, and commits.
.PARAMETER PullRequestId
    The ID of the pull request.
.PARAMETER RepositoryName
    The name of the repository containing the pull request.
.EXAMPLE
    Get-PullRequestDetails -PullRequestId 1234 -RepositoryName "eva-api"
#>
function Get-PullRequestDetails {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [int]$PullRequestId,
        
        [Parameter(Mandatory = $true)]
        [string]$RepositoryName
    )
    
    Test-AzureDevOpsInitialized
    
    try {
        $org = $Script:AzureDevOpsConfig.Organization
        $project = $Script:AzureDevOpsConfig.Project
        
        $apiUrl = "https://dev.azure.com/$org/$project/_apis/git/repositories/$RepositoryName/pullrequests/$PullRequestId`?api-version=7.0"
        
        Write-Verbose "Getting PR details from: $apiUrl"
        
        $pr = Invoke-RestMethod -Uri $apiUrl -Headers $Script:AzureDevOpsConfig.Headers -Method Get
        
        # Get reviewers
        $reviewers = $pr.reviewers | ForEach-Object {
            [PSCustomObject]@{
                DisplayName = $_.displayName
                Vote = switch ($_.vote) {
                    10 { "Approved" }
                    5 { "Approved with suggestions" }
                    0 { "No vote" }
                    -5 { "Waiting for author" }
                    -10 { "Rejected" }
                    default { $_.vote }
                }
                IsRequired = $_.isRequired
            }
        }
        
        # Get work item references
        $workItemRefs = $pr.workItemRefs | ForEach-Object {
            $id = $_.id
            [PSCustomObject]@{
                Id = $id
                Url = $_.url
            }
        }
        
        $details = [PSCustomObject]@{
            PullRequestId = $pr.pullRequestId
            Title = $pr.title
            Description = $pr.description
            Status = $pr.status
            CreatedBy = $pr.createdBy.displayName
            CreatedByEmail = $pr.createdBy.uniqueName
            CreatedDate = $pr.creationDate
            ClosedDate = $pr.closedDate
            SourceBranch = $pr.sourceRefName -replace '^refs/heads/', ''
            TargetBranch = $pr.targetRefName -replace '^refs/heads/', ''
            Repository = $pr.repository.name
            IsDraft = $pr.isDraft
            MergeStatus = $pr.mergeStatus
            Reviewers = $reviewers
            WorkItems = $workItemRefs
            WebUrl = "https://dev.azure.com/$org/$project/_git/$($pr.repository.name)/pullrequest/$($pr.pullRequestId)"
            CompletionOptions = $pr.completionOptions
        }
        
        return $details
        
    } catch {
        Write-Error "Failed to get pull request details: $($_.Exception.Message)"
    }
}

<#
.SYNOPSIS
    Get comments/threads from a pull request.
.DESCRIPTION
    Retrieves all comment threads from a pull request.
.PARAMETER PullRequestId
    The ID of the pull request.
.PARAMETER RepositoryName
    The name of the repository containing the pull request.
.EXAMPLE
    Get-PullRequestComments -PullRequestId 1234 -RepositoryName "eva-api"
#>
function Get-PullRequestComments {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [int]$PullRequestId,
        
        [Parameter(Mandatory = $true)]
        [string]$RepositoryName
    )
    
    Test-AzureDevOpsInitialized
    
    try {
        $org = $Script:AzureDevOpsConfig.Organization
        $project = $Script:AzureDevOpsConfig.Project
        
        $apiUrl = "https://dev.azure.com/$org/$project/_apis/git/repositories/$RepositoryName/pullrequests/$PullRequestId/threads?api-version=7.0"
        
        Write-Verbose "Getting PR comments from: $apiUrl"
        
        $response = Invoke-RestMethod -Uri $apiUrl -Headers $Script:AzureDevOpsConfig.Headers -Method Get
        
        $threads = $response.value | ForEach-Object {
            $comments = $_.comments | ForEach-Object {
                [PSCustomObject]@{
                    Id = $_.id
                    Author = $_.author.displayName
                    Content = $_.content
                    PublishedDate = $_.publishedDate
                    CommentType = $_.commentType
                }
            }
            
            [PSCustomObject]@{
                ThreadId = $_.id
                Status = $_.status
                ThreadContext = $_.threadContext
                Comments = $comments
                IsDeleted = $_.isDeleted
            }
        }
        
        return $threads
        
    } catch {
        Write-Error "Failed to get pull request comments: $($_.Exception.Message)"
    }
}

<#
.SYNOPSIS
    Get unresolved comments from your active pull requests.
.DESCRIPTION
    Retrieves all unresolved comment threads from active pull requests created by you.
.PARAMETER Username
    Username to filter PRs by. If not provided, uses AZURE_DEVOPS_USERNAME environment variable.
.PARAMETER RepositoryName
    Optional. Filter to a specific repository.
.EXAMPLE
    Get-MyUnresolvedPRComments
.EXAMPLE
    Get-MyUnresolvedPRComments -RepositoryName "LegBone"
#>
function Get-MyUnresolvedPRComments {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$Username,
        
        [Parameter(Mandatory = $false)]
        [string]$RepositoryName
    )
    
    Test-AzureDevOpsInitialized
    
    # Use environment variable if username not provided
    if (-not $Username) {
        $Username = $env:AZURE_DEVOPS_USERNAME
        if (-not $Username) {
            Write-Error "Username not provided and AZURE_DEVOPS_USERNAME environment variable not set"
            return
        }
    }
    
    try {
        # Get active PRs by user
        $prs = Get-PullRequests -Status Active -CreatedBy $Username
        
        if ($RepositoryName) {
            $prs = $prs | Where-Object { $_.Repository -eq $RepositoryName }
        }
        
        if (-not $prs) {
            Write-Host "No active pull requests found for user: $Username" -ForegroundColor Yellow
            return
        }
        
        Write-Verbose "Found $($prs.Count) active PR(s) for $Username"
        
        $allUnresolvedComments = @()
        
        foreach ($pr in $prs) {
            Write-Verbose "Checking PR #$($pr.PullRequestId): $($pr.Title)"
            
            $comments = Get-PullRequestComments -PullRequestId $pr.PullRequestId -RepositoryName $pr.Repository
            
            $unresolved = $comments | Where-Object { 
                $_.Status -eq "active" -or $_.Status -eq "pending"
            }
            
            foreach ($thread in $unresolved) {
                $allUnresolvedComments += [PSCustomObject]@{
                    PullRequestId = $pr.PullRequestId
                    PullRequestTitle = $pr.Title
                    Repository = $pr.Repository
                    ThreadId = $thread.ThreadId
                    Status = $thread.Status
                    Comments = $thread.Comments
                    FilePath = $thread.ThreadContext.filePath
                    LineStart = $thread.ThreadContext.rightFileStart.line
                    LineEnd = $thread.ThreadContext.rightFileEnd.line
                    WebUrl = $pr.WebUrl
                }
            }
        }
        
        if ($allUnresolvedComments.Count -eq 0) {
            Write-Host "No unresolved comments found! 🎉" -ForegroundColor Green
            return
        }
        
        Write-Host "`nFound $($allUnresolvedComments.Count) unresolved comment thread(s):`n" -ForegroundColor Cyan
        
        foreach ($item in $allUnresolvedComments) {
            Write-Host "PR #$($item.PullRequestId) - $($item.PullRequestTitle) [$($item.Repository)]" -ForegroundColor Yellow
            Write-Host "  Thread $($item.ThreadId) - Status: $($item.Status)" -ForegroundColor Gray
            
            if ($item.FilePath) {
                $fileInfo = "$($item.FilePath)"
                if ($item.LineStart) {
                    $fileInfo += " (Line $($item.LineStart)"
                    if ($item.LineEnd -and $item.LineEnd -ne $item.LineStart) {
                        $fileInfo += "-$($item.LineEnd)"
                    }
                    $fileInfo += ")"
                }
                Write-Host "  File: $fileInfo" -ForegroundColor Cyan
            }
            
            Write-Host "  Link: $($item.WebUrl)" -ForegroundColor Gray
            
            foreach ($comment in $item.Comments) {
                Write-Host "    [$($comment.Author)] $($comment.Content)" -ForegroundColor White
            }
            Write-Host ""
        }
        
        return $allUnresolvedComments
        
    } catch {
        Write-Error "Failed to get unresolved PR comments: $($_.Exception.Message)"
    }
}

#endregion

# Export module members
Export-ModuleMember -Function @(
    'Initialize-AzureDevOps',
    'Search-WorkItems',
    'Get-WorkItem',
    'Get-WorkItemsByFeature',
    'Get-RelatedWorkItems',
    'Get-WorkItemComments',
    'Get-WorkItemHistory',
    'Update-WorkItem',
    'Add-WorkItemComment',
    'New-WorkItem',
    'Export-WorkItemsToMarkdown',
    'Get-PullRequests',
    'Get-PullRequestDetails',
    'Get-PullRequestComments',
    'Get-MyUnresolvedPRComments'
)

# Auto-initialize if all environment variables are set
if ($env:AZURE_DEVOPS_ORG -and $env:AZURE_DEVOPS_PROJECT -and $env:AZURE_DEVOPS_PAT) {
    try {
        Initialize-AzureDevOps
        Write-Host "Azure DevOps Tools initialized from environment variables: $env:AZURE_DEVOPS_ORG/$env:AZURE_DEVOPS_PROJECT" -ForegroundColor Green
    } catch {
        Write-Warning "Failed to auto-initialize Azure DevOps: $_"
    }
}
