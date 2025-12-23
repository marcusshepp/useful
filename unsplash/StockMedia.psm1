$script:UnsplashAccessKey = $null
$script:PexelsApiKey = $null
$script:UnsplashBaseUrl = "https://api.unsplash.com"
$script:PexelsBaseUrl = "https://api.pexels.com"

function Initialize-StockMediaModule {
    [CmdletBinding()]
    param()

    [string]$envPath = Join-Path -Path $PSScriptRoot -ChildPath ".env"
    
    if (-not (Test-Path -Path $envPath)) {
        $errorDetails = @{
            StatusCode = 404
            Message = "Environment file not found at: $envPath"
            ErrorType = "FileNotFound"
        }
        return [PSCustomObject]$errorDetails
    }

    [hashtable]$envVars = @{}
    Get-Content -Path $envPath | ForEach-Object {
        [string]$line = $_
        if ($line -match "^\s*([^#][^=]+)=(.*)$") {
            $envVars[$matches[1].Trim()] = $matches[2].Trim()
        }
    }

    [System.Collections.ArrayList]$warnings = @()

    if ($envVars.ContainsKey("UNSPLASH_ACCESS_KEY")) {
        $script:UnsplashAccessKey = $envVars["UNSPLASH_ACCESS_KEY"]
    } else {
        $warnings.Add("UNSPLASH_ACCESS_KEY not found - Unsplash functions will not work") | Out-Null
    }

    if ($envVars.ContainsKey("PEXELS_API_KEY")) {
        $script:PexelsApiKey = $envVars["PEXELS_API_KEY"]
    } else {
        $warnings.Add("PEXELS_API_KEY not found - Pexels functions will not work") | Out-Null
    }

    if ($warnings.Count -eq 2) {
        $errorDetails = @{
            StatusCode = 400
            Message = "No API keys found in .env file"
            ErrorType = "MissingConfiguration"
        }
        return [PSCustomObject]$errorDetails
    }
    
    [PSCustomObject]@{
        Success = $true
        Message = "Stock media module initialized successfully"
        Warnings = $warnings
    }
}

function Search-UnsplashPhoto {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Query,

        [Parameter(Mandatory = $false)]
        [ValidateRange(1, 10)]
        [int]$Count = 3,

        [Parameter(Mandatory = $false)]
        [switch]$AsJson
    )

    if (-not $script:UnsplashAccessKey) {
        [PSCustomObject]$initResult = Initialize-StockMediaModule
        if ($initResult.PSObject.Properties.Name -contains "ErrorType") {
            if ($AsJson) { return $initResult | ConvertTo-Json -Depth 10 }
            return $initResult
        }
        if (-not $script:UnsplashAccessKey) {
            $errorDetails = @{
                StatusCode = 400
                Message = "UNSPLASH_ACCESS_KEY not configured"
                ErrorType = "MissingConfiguration"
            }
            if ($AsJson) { return [PSCustomObject]$errorDetails | ConvertTo-Json -Depth 10 }
            return [PSCustomObject]$errorDetails
        }
    }

    [string]$encodedQuery = [System.Web.HttpUtility]::UrlEncode($Query)
    [string]$url = "$script:UnsplashBaseUrl/search/photos?query=$encodedQuery&per_page=$Count"

    [hashtable]$headers = @{
        "Authorization" = "Client-ID $script:UnsplashAccessKey"
        "Accept-Version" = "v1"
    }

    try {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get

        [System.Collections.ArrayList]$photos = @()
        foreach ($result in $response.results) {
            [PSCustomObject]$photo = [PSCustomObject]@{
                Id = [string]$result.id
                Description = [string]($result.description ?? $result.alt_description ?? "No description")
                Urls = [PSCustomObject]@{
                    Raw = [string]$result.urls.raw
                    Full = [string]$result.urls.full
                    Regular = [string]$result.urls.regular
                    Small = [string]$result.urls.small
                    Thumb = [string]$result.urls.thumb
                }
                DownloadLocation = [string]$result.links.download_location
            }
            $photos.Add($photo) | Out-Null
        }

        if ($AsJson) { return $photos | ConvertTo-Json -Depth 10 }
        return $photos
    }
    catch {
        $errorDetails = @{
            StatusCode = [int]$_.Exception.Response.StatusCode.value__
            Message = [string]$_.Exception.Message
            ErrorType = "ApiError"
        }
        if ($AsJson) { return [PSCustomObject]$errorDetails | ConvertTo-Json -Depth 10 }
        return [PSCustomObject]$errorDetails
    }
}

function Save-UnsplashPhoto {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,

        [Parameter(Mandatory = $true)]
        [string]$DestinationPath,

        [Parameter(Mandatory = $false)]
        [ValidateSet("raw", "full", "regular", "small", "thumb")]
        [string]$Size = "regular"
    )

    if (-not $script:UnsplashAccessKey) {
        [PSCustomObject]$initResult = Initialize-StockMediaModule
        if ($initResult.PSObject.Properties.Name -contains "ErrorType") {
            return $initResult
        }
        if (-not $script:UnsplashAccessKey) {
            return [PSCustomObject]@{
                StatusCode = 400
                Message = "UNSPLASH_ACCESS_KEY not configured"
                ErrorType = "MissingConfiguration"
            }
        }
    }

    [hashtable]$headers = @{
        "Authorization" = "Client-ID $script:UnsplashAccessKey"
        "Accept-Version" = "v1"
    }

    [string]$downloadUrl = $Url
    [bool]$isDownloadLocation = $Url -like "*download_location*" -or $Url -like "*/download*"
    
    if ($isDownloadLocation) {
        try {
            $downloadResponse = Invoke-RestMethod -Uri $Url -Headers $headers -Method Get
            $downloadUrl = [string]$downloadResponse.url
        }
        catch {
            $errorDetails = @{
                StatusCode = [int]$_.Exception.Response.StatusCode.value__
                Message = "Failed to get download URL: $($_.Exception.Message)"
                ErrorType = "DownloadTrackingError"
            }
            return [PSCustomObject]$errorDetails
        }
    }

    if ($Url -like "*unsplash.com/photos/*" -or $Url -match "^[a-zA-Z0-9_-]{11}$") {
        [string]$photoId = $Url
        if ($Url -like "*unsplash.com/photos/*") {
            $photoId = ($Url -split "/photos/")[1] -split "[/?]" | Select-Object -First 1
        }
        
        try {
            [string]$trackingUrl = "$script:UnsplashBaseUrl/photos/$photoId/download"
            $downloadResponse = Invoke-RestMethod -Uri $trackingUrl -Headers $headers -Method Get
            $downloadUrl = [string]$downloadResponse.url
        }
        catch {
            $errorDetails = @{
                StatusCode = [int]$_.Exception.Response.StatusCode.value__
                Message = "Failed to track download: $($_.Exception.Message)"
                ErrorType = "DownloadTrackingError"
            }
            return [PSCustomObject]$errorDetails
        }
    }

    if ($Size -ne "regular" -and $downloadUrl -like "*images.unsplash.com*") {
        [hashtable]$sizeParams = @{
            "raw" = ""
            "full" = "q=85"
            "regular" = "w=1080"
            "small" = "w=400"
            "thumb" = "w=200"
        }
        
        if ($downloadUrl -match "\?") {
            $downloadUrl = $downloadUrl -replace "w=\d+", $sizeParams[$Size]
        }
    }

    [string]$directory = Split-Path -Path $DestinationPath -Parent
    if ($directory -and -not (Test-Path -Path $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }

    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $DestinationPath -Headers $headers

        [PSCustomObject]@{
            Success = $true
            Message = "Photo saved successfully"
            Path = [string](Resolve-Path -Path $DestinationPath)
            Size = $Size
        }
    }
    catch {
        $errorDetails = @{
            StatusCode = [int]$_.Exception.Response.StatusCode.value__
            Message = "Failed to download photo: $($_.Exception.Message)"
            ErrorType = "DownloadError"
        }
        return [PSCustomObject]$errorDetails
    }
}

function Search-PexelsPhoto {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Query,

        [Parameter(Mandatory = $false)]
        [ValidateRange(1, 80)]
        [int]$Count = 3,

        [Parameter(Mandatory = $false)]
        [ValidateSet("landscape", "portrait", "square")]
        [string]$Orientation,

        [Parameter(Mandatory = $false)]
        [switch]$AsJson
    )

    if (-not $script:PexelsApiKey) {
        [PSCustomObject]$initResult = Initialize-StockMediaModule
        if ($initResult.PSObject.Properties.Name -contains "ErrorType") {
            if ($AsJson) { return $initResult | ConvertTo-Json -Depth 10 }
            return $initResult
        }
        if (-not $script:PexelsApiKey) {
            $errorDetails = @{
                StatusCode = 400
                Message = "PEXELS_API_KEY not configured"
                ErrorType = "MissingConfiguration"
            }
            if ($AsJson) { return [PSCustomObject]$errorDetails | ConvertTo-Json -Depth 10 }
            return [PSCustomObject]$errorDetails
        }
    }

    [string]$encodedQuery = [System.Web.HttpUtility]::UrlEncode($Query)
    [string]$url = "$script:PexelsBaseUrl/v1/search?query=$encodedQuery&per_page=$Count"
    
    if ($Orientation) {
        $url += "&orientation=$Orientation"
    }

    [hashtable]$headers = @{
        "Authorization" = $script:PexelsApiKey
    }

    try {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get

        [System.Collections.ArrayList]$photos = @()
        foreach ($result in $response.photos) {
            [PSCustomObject]$photo = [PSCustomObject]@{
                Id = [int]$result.id
                Description = [string]($result.alt ?? "No description")
                Photographer = [string]$result.photographer
                PhotographerUrl = [string]$result.photographer_url
                Urls = [PSCustomObject]@{
                    Original = [string]$result.src.original
                    Large2x = [string]$result.src.large2x
                    Large = [string]$result.src.large
                    Medium = [string]$result.src.medium
                    Small = [string]$result.src.small
                    Tiny = [string]$result.src.tiny
                }
            }
            $photos.Add($photo) | Out-Null
        }

        if ($AsJson) { return $photos | ConvertTo-Json -Depth 10 }
        return $photos
    }
    catch {
        $errorDetails = @{
            StatusCode = [int]$_.Exception.Response.StatusCode.value__
            Message = [string]$_.Exception.Message
            ErrorType = "ApiError"
        }
        if ($AsJson) { return [PSCustomObject]$errorDetails | ConvertTo-Json -Depth 10 }
        return [PSCustomObject]$errorDetails
    }
}

function Search-PexelsVideo {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Query,

        [Parameter(Mandatory = $false)]
        [ValidateRange(1, 80)]
        [int]$Count = 3,

        [Parameter(Mandatory = $false)]
        [ValidateSet("landscape", "portrait", "square")]
        [string]$Orientation,

        [Parameter(Mandatory = $false)]
        [switch]$AsJson
    )

    if (-not $script:PexelsApiKey) {
        [PSCustomObject]$initResult = Initialize-StockMediaModule
        if ($initResult.PSObject.Properties.Name -contains "ErrorType") {
            if ($AsJson) { return $initResult | ConvertTo-Json -Depth 10 }
            return $initResult
        }
        if (-not $script:PexelsApiKey) {
            $errorDetails = @{
                StatusCode = 400
                Message = "PEXELS_API_KEY not configured"
                ErrorType = "MissingConfiguration"
            }
            if ($AsJson) { return [PSCustomObject]$errorDetails | ConvertTo-Json -Depth 10 }
            return [PSCustomObject]$errorDetails
        }
    }

    [string]$encodedQuery = [System.Web.HttpUtility]::UrlEncode($Query)
    [string]$url = "$script:PexelsBaseUrl/videos/search?query=$encodedQuery&per_page=$Count"
    
    if ($Orientation) {
        $url += "&orientation=$Orientation"
    }

    [hashtable]$headers = @{
        "Authorization" = $script:PexelsApiKey
    }

    try {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get

        [System.Collections.ArrayList]$videos = @()
        foreach ($result in $response.videos) {
            [System.Collections.ArrayList]$videoFiles = @()
            foreach ($file in $result.video_files) {
                [PSCustomObject]$videoFile = [PSCustomObject]@{
                    Id = [int]$file.id
                    Quality = [string]$file.quality
                    FileType = [string]$file.file_type
                    Width = [int]$file.width
                    Height = [int]$file.height
                    Link = [string]$file.link
                }
                $videoFiles.Add($videoFile) | Out-Null
            }

            [PSCustomObject]$video = [PSCustomObject]@{
                Id = [int]$result.id
                Duration = [int]$result.duration
                Width = [int]$result.width
                Height = [int]$result.height
                Thumbnail = [string]$result.image
                User = [PSCustomObject]@{
                    Name = [string]$result.user.name
                    Url = [string]$result.user.url
                }
                VideoFiles = $videoFiles
            }
            $videos.Add($video) | Out-Null
        }

        if ($AsJson) { return $videos | ConvertTo-Json -Depth 10 }
        return $videos
    }
    catch {
        $errorDetails = @{
            StatusCode = [int]$_.Exception.Response.StatusCode.value__
            Message = [string]$_.Exception.Message
            ErrorType = "ApiError"
        }
        if ($AsJson) { return [PSCustomObject]$errorDetails | ConvertTo-Json -Depth 10 }
        return [PSCustomObject]$errorDetails
    }
}

function Save-PexelsPhoto {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,

        [Parameter(Mandatory = $true)]
        [string]$DestinationPath,

        [Parameter(Mandatory = $false)]
        [ValidateSet("original", "large2x", "large", "medium", "small", "tiny")]
        [string]$Size = "large"
    )

    [string]$directory = Split-Path -Path $DestinationPath -Parent
    if ($directory -and -not (Test-Path -Path $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }

    try {
        Invoke-WebRequest -Uri $Url -OutFile $DestinationPath

        [PSCustomObject]@{
            Success = $true
            Message = "Photo saved successfully"
            Path = [string](Resolve-Path -Path $DestinationPath)
            Size = $Size
        }
    }
    catch {
        $errorDetails = @{
            StatusCode = [int]$_.Exception.Response.StatusCode.value__
            Message = "Failed to download photo: $($_.Exception.Message)"
            ErrorType = "DownloadError"
        }
        return [PSCustomObject]$errorDetails
    }
}

function Save-PexelsVideo {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,

        [Parameter(Mandatory = $true)]
        [string]$DestinationPath,

        [Parameter(Mandatory = $false)]
        [ValidateSet("uhd", "hd", "sd", "tiny")]
        [string]$Quality = "hd"
    )

    [string]$directory = Split-Path -Path $DestinationPath -Parent
    if ($directory -and -not (Test-Path -Path $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }

    try {
        Invoke-WebRequest -Uri $Url -OutFile $DestinationPath

        [PSCustomObject]@{
            Success = $true
            Message = "Video saved successfully"
            Path = [string](Resolve-Path -Path $DestinationPath)
            Quality = $Quality
        }
    }
    catch {
        $errorDetails = @{
            StatusCode = [int]$_.Exception.Response.StatusCode.value__
            Message = "Failed to download video: $($_.Exception.Message)"
            ErrorType = "DownloadError"
        }
        return [PSCustomObject]$errorDetails
    }
}

Export-ModuleMember -Function Initialize-StockMediaModule, Search-UnsplashPhoto, Save-UnsplashPhoto, Search-PexelsPhoto, Search-PexelsVideo, Save-PexelsPhoto, Save-PexelsVideo
