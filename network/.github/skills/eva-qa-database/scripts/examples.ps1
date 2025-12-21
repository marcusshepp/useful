# Eva QA Database Examples
# These examples demonstrate common operations with the Eva database

# Import the module (should already be loaded from profile)
Import-Module C:\Users\mshepherd\p\network\EvaSql.psm1 -Force

# ============================================================================
# Basic Queries
# ============================================================================

# Get current session
Write-Host "`n=== Current Session ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT * FROM sessions WHERE IsCurrentSession = 1" -Environment QA

# List all sessions
Write-Host "`n=== All Sessions ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT Id, Name, StartDate, IsCurrentSession FROM sessions ORDER BY StartDate DESC" -Environment QA

# Get server info
Write-Host "`n=== Server Information ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT @@VERSION AS SQLVersion, DB_NAME() AS CurrentDatabase" -Environment QA

# ============================================================================
# Schema Discovery
# ============================================================================

# Find all committee-related tables
Write-Host "`n=== Committee Tables ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%Committee%' ORDER BY TABLE_NAME" -Environment QA

# Get schema for sessions table
Write-Host "`n=== Sessions Table Schema ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'sessions' ORDER BY ORDINAL_POSITION" -Environment QA

# ============================================================================
# Recent Activity
# ============================================================================

# Get recently created records (if CommitteeReports table exists)
Write-Host "`n=== Recent Committee Reports ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT TOP 5 * FROM CommitteeReports ORDER BY Created DESC" -Environment QA

# ============================================================================
# Data Analysis
# ============================================================================

# Count sessions by type
Write-Host "`n=== Session Count by Type ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT IsRegularSession, COUNT(*) AS SessionCount FROM sessions GROUP BY IsRegularSession" -Environment QA

# Get sessions created by user
Write-Host "`n=== Sessions by Creator ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT CreatedBy, COUNT(*) AS SessionCount FROM sessions GROUP BY CreatedBy ORDER BY SessionCount DESC" -Environment QA

# ============================================================================
# Advanced: Format Output
# ============================================================================

# Get sessions and format as table
Write-Host "`n=== Formatted Session List ===" -ForegroundColor Cyan
$sessions = Invoke-EvaSql -Query "SELECT Id, Name, StartDate, EndDate, IsCurrentSession FROM sessions" -Environment QA
$sessions | Format-Table -AutoSize

# Export to CSV
Write-Host "`n=== Exporting to CSV ===" -ForegroundColor Cyan
$sessions | Export-Csv -Path "C:\Users\mshepherd\p\network\sessions_export.csv" -NoTypeInformation
Write-Host "Exported to sessions_export.csv" -ForegroundColor Green

# ============================================================================
# Safe Update Example
# ============================================================================

Write-Host "`n=== Safe Update Example ===" -ForegroundColor Yellow
Write-Host "This demonstrates the safe pattern for updates:" -ForegroundColor Yellow

# 1. Check current value
Write-Host "`n1. Check current value:" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT Id, Name, IsCurrentSession FROM sessions WHERE Id = 3" -Environment QA

# 2. Perform update (commented out for safety)
# Write-Host "`n2. Perform update:" -ForegroundColor Cyan
# Invoke-EvaSqlNonQuery -Query "UPDATE sessions SET IsCurrentSession = 0 WHERE Id = 3" -Environment QA

# 3. Verify change
# Write-Host "`n3. Verify change:" -ForegroundColor Cyan
# Invoke-EvaSql -Query "SELECT Id, Name, IsCurrentSession FROM sessions WHERE Id = 3" -Environment QA

Write-Host "`nExamples complete!" -ForegroundColor Green
