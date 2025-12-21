# EvaAPI Codebase Exploration Script
# Run this to quickly explore the structure of the EvaAPI project

$evaApiPath = "C:\Users\mshepherd\p\leb\EvaAPI"
cd $evaApiPath

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "    EvaAPI Codebase Exploration" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

# ============================================================================
# Project Structure Overview
# ============================================================================

Write-Host "=== Project Directory Structure ===" -ForegroundColor Cyan
$directories = @(
    "Data",
    "Data\Models",
    "Services",
    "Controllers",
    "Dtos",
    "Interfaces",
    "Migrations",
    "Utilities"
)

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        $count = (Get-ChildItem -Path $dir -Filter *.cs -Recurse).Count
        Write-Host "$dir - $count C# files" -ForegroundColor White
    }
}

# ============================================================================
# Database Context Overview
# ============================================================================

Write-Host "`n=== DbSets in EvaDbContext ===" -ForegroundColor Cyan
Select-String -Path "Data\EvaDbContext.cs" -Pattern "public virtual DbSet<" | 
    ForEach-Object { $_.Line.Trim() } |
    Select-Object -First 20

# ============================================================================
# Entity Models by Domain
# ============================================================================

Write-Host "`n=== Entity Models by Domain ===" -ForegroundColor Cyan

$domains = Get-ChildItem -Path "Data\Models" -Directory

foreach ($domain in $domains) {
    $modelCount = (Get-ChildItem -Path $domain.FullName -Recurse -Filter *.cs).Count
    Write-Host "`n$($domain.Name): $modelCount models" -ForegroundColor Yellow
    
    Get-ChildItem -Path $domain.FullName -Recurse -Filter *.cs | 
        Select-Object -First 5 | 
        ForEach-Object { Write-Host "  - $($_.Name)" }
    
    if ($modelCount -gt 5) {
        Write-Host "  ... and $($modelCount - 5) more" -ForegroundColor Gray
    }
}

# ============================================================================
# Services Overview
# ============================================================================

Write-Host "`n=== Services by Feature ===" -ForegroundColor Cyan

if (Test-Path "Services") {
    $serviceFiles = Get-ChildItem -Path "Services" -Recurse -Filter *.cs -Exclude *Interface*
    Write-Host "Total Services: $($serviceFiles.Count)" -ForegroundColor White
    
    $servicesByDir = $serviceFiles | Group-Object { $_.Directory.Name }
    $servicesByDir | Select-Object -First 10 | ForEach-Object {
        Write-Host "  $($_.Name): $($_.Count) services" -ForegroundColor White
    }
}

# ============================================================================
# Controllers Overview
# ============================================================================

Write-Host "`n=== API Controllers ===" -ForegroundColor Cyan

if (Test-Path "Controllers") {
    $controllers = Get-ChildItem -Path "Controllers" -Filter *Controller.cs
    Write-Host "Total Controllers: $($controllers.Count)" -ForegroundColor White
    $controllers | Select-Object -First 15 | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor White
    }
    
    if ($controllers.Count -gt 15) {
        Write-Host "  ... and $($controllers.Count - 15) more" -ForegroundColor Gray
    }
}

# ============================================================================
# Recent Migrations
# ============================================================================

Write-Host "`n=== Recent Migrations (Last 10) ===" -ForegroundColor Cyan

Get-ChildItem -Path "Migrations" -Filter *.cs -Exclude *Designer*,*Snapshot* |
    Sort-Object Name -Descending |
    Select-Object -First 10 |
    ForEach-Object {
        $name = $_.Name -replace '^(\d{8})\d{6}_(.+)\.cs$', '$1 - $2'
        Write-Host "  $name" -ForegroundColor White
    }

# ============================================================================
# Project Configuration
# ============================================================================

Write-Host "`n=== Configuration Files ===" -ForegroundColor Cyan

@(
    "appsettings.json",
    "appsettings.development.json",
    "Program.cs",
    "EvaAPI.csproj"
) | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "  ✓ $_" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $_" -ForegroundColor Red
    }
}

# ============================================================================
# Find Specific Features (Example)
# ============================================================================

Write-Host "`n=== Example: CommitteeReport Feature Files ===" -ForegroundColor Cyan

Write-Host "`nEntity Models:" -ForegroundColor Yellow
Get-ChildItem -Path "Data\Models" -Recurse -Filter "*CommitteeReport*.cs" |
    Select-Object -First 5 |
    ForEach-Object { Write-Host "  - $($_.FullName.Replace($evaApiPath, '.'))" }

Write-Host "`nServices:" -ForegroundColor Yellow
Get-ChildItem -Path "Services" -Recurse -Filter "*CommitteeReport*.cs" |
    Select-Object -First 5 |
    ForEach-Object { Write-Host "  - $($_.FullName.Replace($evaApiPath, '.'))" }

Write-Host "`nControllers:" -ForegroundColor Yellow
Get-ChildItem -Path "Controllers" -Filter "*CommitteeReport*.cs" |
    ForEach-Object { Write-Host "  - $($_.FullName.Replace($evaApiPath, '.'))" }

# ============================================================================
# Quick Stats
# ============================================================================

Write-Host "`n=== Quick Stats ===" -ForegroundColor Cyan

$totalCs = (Get-ChildItem -Path . -Recurse -Filter *.cs -Exclude *Migration*,*Designer*).Count
$totalModels = (Get-ChildItem -Path "Data\Models" -Recurse -Filter *.cs).Count
$totalServices = (Get-ChildItem -Path "Services" -Recurse -Filter *.cs).Count
$totalControllers = (Get-ChildItem -Path "Controllers" -Filter *.cs).Count
$totalMigrations = (Get-ChildItem -Path "Migrations" -Filter *.cs -Exclude *Designer*,*Snapshot*).Count

Write-Host "  Total C# Files (excl migrations): $totalCs" -ForegroundColor White
Write-Host "  Entity Models: $totalModels" -ForegroundColor White
Write-Host "  Services: $totalServices" -ForegroundColor White
Write-Host "  Controllers: $totalControllers" -ForegroundColor White
Write-Host "  Migrations: $totalMigrations" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "    Exploration Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
