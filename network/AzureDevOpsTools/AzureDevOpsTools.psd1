@{
    ModuleVersion = '1.0.0'
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    Author = 'GitHub Copilot'
    CompanyName = 'Unknown'
    Copyright = '(c) 2025. All rights reserved.'
    Description = 'Azure DevOps work items management module for use with GitHub Copilot CLI'
    PowerShellVersion = '7.0'
    RootModule = 'AzureDevOpsTools.psm1'
    FunctionsToExport = @(
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
        'Export-WorkItemsToMarkdown'
    )
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
