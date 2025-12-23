# Stock Media PowerShell Module

PowerShell module for querying Unsplash and Pexels APIs for photos and videos.

## Setup

1. Create a `.env` file in the module directory:
```
UNSPLASH_ACCESS_KEY=your_access_key
UNSPLASH_SECRET_KEY=your_secret_key
PEXELS_API_KEY=your_pexels_key
```

2. Import the module:
```powershell
Import-Module .\StockMedia.psd1
```

## Functions

### Initialize-StockMediaModule
Loads the `.env` file and sets API keys. Called automatically by other functions if needed.

```powershell
Initialize-StockMediaModule
```

---

## Unsplash Functions

### Search-UnsplashPhoto

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| Query | string | Yes | - | Search terms |
| Count | int | No | 3 | Number of results (1-10) |
| AsJson | switch | No | false | Return JSON string |

```powershell
Search-UnsplashPhoto -Query "modern office" -Count 3
```

**Returns:** `Id`, `Description`, `Urls`, `DownloadLocation`

### Save-UnsplashPhoto

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| Url | string | Yes | - | DownloadLocation from search results |
| DestinationPath | string | Yes | - | File path to save |
| Size | string | No | regular | raw, full, regular, small, thumb |

```powershell
$photos = Search-UnsplashPhoto -Query "restaurant" -Count 1
Save-UnsplashPhoto -Url $photos[0].DownloadLocation -DestinationPath ".\public\images\hero.jpg"
```

---

## Pexels Functions

### Search-PexelsPhoto

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| Query | string | Yes | - | Search terms |
| Count | int | No | 3 | Number of results (1-80) |
| Orientation | string | No | - | landscape, portrait, square |
| AsJson | switch | No | false | Return JSON string |

```powershell
Search-PexelsPhoto -Query "coffee shop" -Count 5 -Orientation landscape
```

**Returns:** `Id`, `Description`, `Photographer`, `PhotographerUrl`, `Urls`

### Search-PexelsVideo

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| Query | string | Yes | - | Search terms |
| Count | int | No | 3 | Number of results (1-80) |
| Orientation | string | No | - | landscape, portrait, square |
| AsJson | switch | No | false | Return JSON string |

```powershell
Search-PexelsVideo -Query "nature" -Count 2
```

**Returns:** `Id`, `Duration`, `Width`, `Height`, `Thumbnail`, `User`, `VideoFiles`

### Save-PexelsPhoto

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| Url | string | Yes | - | URL from search results (e.g., Urls.Large) |
| DestinationPath | string | Yes | - | File path to save |
| Size | string | No | large | original, large2x, large, medium, small, tiny |

```powershell
$photos = Search-PexelsPhoto -Query "office" -Count 1
Save-PexelsPhoto -Url $photos[0].Urls.Large -DestinationPath ".\public\images\hero.jpg"
```

### Save-PexelsVideo

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| Url | string | Yes | - | Video file link from VideoFiles array |
| DestinationPath | string | Yes | - | File path to save |
| Quality | string | No | hd | uhd, hd, sd, tiny |

```powershell
$videos = Search-PexelsVideo -Query "ocean" -Count 1
$hdFile = $videos[0].VideoFiles | Where-Object { $_.Quality -eq "hd" } | Select-Object -First 1
Save-PexelsVideo -Url $hdFile.Link -DestinationPath ".\public\videos\background.mp4"
```

---

## Example: Vite Project Workflow

```powershell
Import-Module C:\path\to\StockMedia.psd1

# Unsplash photos
$unsplashPhotos = Search-UnsplashPhoto -Query "tech startup" -Count 2
Save-UnsplashPhoto -Url $unsplashPhotos[0].DownloadLocation -DestinationPath ".\my-vite-app\public\images\hero.jpg"

# Pexels photos
$pexelsPhotos = Search-PexelsPhoto -Query "team meeting" -Count 2 -Orientation landscape
Save-PexelsPhoto -Url $pexelsPhotos[0].Urls.Large -DestinationPath ".\my-vite-app\public\images\about.jpg"

# Pexels video for background
$videos = Search-PexelsVideo -Query "abstract" -Count 1
$hdVideo = $videos[0].VideoFiles | Where-Object { $_.Quality -eq "hd" } | Select-Object -First 1
Save-PexelsVideo -Url $hdVideo.Link -DestinationPath ".\my-vite-app\public\videos\bg.mp4"
```

## Error Handling

Functions return error objects with `StatusCode`, `Message`, and `ErrorType` properties on failure.

```powershell
$result = Search-PexelsPhoto -Query "test"
if ($result.ErrorType) {
    Write-Error "Failed: $($result.Message)"
}
```
