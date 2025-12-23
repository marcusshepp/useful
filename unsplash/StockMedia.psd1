@{
    RootModule = 'StockMedia.psm1'
    ModuleVersion = '2.0.0'
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    Author = 'Marcus'
    Description = 'PowerShell module for querying Unsplash and Pexels APIs for photos and videos'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Initialize-StockMediaModule',
        'Search-UnsplashPhoto',
        'Save-UnsplashPhoto',
        'Search-PexelsPhoto',
        'Search-PexelsVideo',
        'Save-PexelsPhoto',
        'Save-PexelsVideo'
    )
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
    PrivateData = @{
        PSData = @{
            Tags = @('Unsplash', 'Pexels', 'API', 'Photos', 'Videos', 'Images', 'StockMedia')
            ProjectUri = ''
            LicenseUri = ''
        }
    }
}
