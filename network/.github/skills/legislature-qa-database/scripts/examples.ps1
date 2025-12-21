# Legislature (M2) QA Database Examples
# These examples demonstrate common operations with the Legislature database

# Import the module (should already be loaded from profile)
Import-Module C:\Users\mshepherd\p\network\EvaSql.psm1 -Force

# ============================================================================
# Basic Committee Queries
# ============================================================================

# Get latest committee
Write-Host "`n=== Latest Committee ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT TOP 1 CommitteeID, CommitteeName, DateAdded, LastModifiedBy FROM Committee ORDER BY CommitteeID DESC" -Environment M2-QA

# Get all active committees
Write-Host "`n=== Active Committees ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName, ChamberID FROM Committee WHERE IsActive = 1 ORDER BY CommitteeName" -Environment M2-QA

# Get Senate committees for current session
Write-Host "`n=== Senate Committees (Session 16) ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName FROM Committee WHERE ChamberID = 2 AND SessionID = 16 AND IsActive = 1" -Environment M2-QA

# Get server info
Write-Host "`n=== Server Information ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT @@VERSION AS SQLVersion, DB_NAME() AS CurrentDatabase" -Environment M2-QA

# ============================================================================
# Schema Discovery
# ============================================================================

# Find all committee-related tables
Write-Host "`n=== Committee Tables ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%Committee%' ORDER BY TABLE_SCHEMA, TABLE_NAME" -Environment M2-QA

# Get schema for Committee table
Write-Host "`n=== Committee Table Schema ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Committee' ORDER BY ORDINAL_POSITION" -Environment M2-QA

# ============================================================================
# Lookup Tables
# ============================================================================

# Get committee types
Write-Host "`n=== Committee Types ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT * FROM CommitteeType ORDER BY CommitteeTypeID" -Environment M2-QA

# Get committee roles
Write-Host "`n=== Committee Roles ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT * FROM CommitteeRole ORDER BY CommitteeRoleID" -Environment M2-QA

# ============================================================================
# Data Analysis
# ============================================================================

# Count committees by chamber
Write-Host "`n=== Committees by Chamber ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "
SELECT 
    ChamberID,
    CASE ChamberID 
        WHEN 1 THEN 'House'
        WHEN 2 THEN 'Senate'
        ELSE 'Unknown'
    END AS Chamber,
    COUNT(*) AS CommitteeCount
FROM Committee
WHERE IsActive = 1
GROUP BY ChamberID
" -Environment M2-QA

# Count active vs inactive committees
Write-Host "`n=== Active vs Inactive Committees ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT IsActive, COUNT(*) AS CommitteeCount FROM Committee GROUP BY IsActive" -Environment M2-QA

# Get recently modified committees
Write-Host "`n=== Recently Modified Committees ===" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT TOP 10 CommitteeID, CommitteeName, LastModified, LastModifiedBy FROM Committee ORDER BY LastModified DESC" -Environment M2-QA

# ============================================================================
# Advanced: Format Output
# ============================================================================

# Get committees and format as table
Write-Host "`n=== Formatted Committee List ===" -ForegroundColor Cyan
$committees = Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName, ChamberID, IsActive FROM Committee WHERE SessionID = 16" -Environment M2-QA
$committees | Format-Table -AutoSize

# Export to CSV
Write-Host "`n=== Exporting to CSV ===" -ForegroundColor Cyan
$committees | Export-Csv -Path "C:\Users\mshepherd\p\network\committees_export.csv" -NoTypeInformation
Write-Host "Exported to committees_export.csv" -ForegroundColor Green

# ============================================================================
# Safe Update Example
# ============================================================================

Write-Host "`n=== Safe Update Example ===" -ForegroundColor Yellow
Write-Host "This demonstrates the safe pattern for updates:" -ForegroundColor Yellow

# 1. Check current value
Write-Host "`n1. Check current value:" -ForegroundColor Cyan
Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName, IsActive FROM Committee WHERE CommitteeID = 466" -Environment M2-QA

# 2. Perform update (commented out for safety)
# Write-Host "`n2. Perform update:" -ForegroundColor Cyan
# Invoke-EvaSqlNonQuery -Query "UPDATE Committee SET IsActive = 1 WHERE CommitteeID = 466" -Environment M2-QA

# 3. Verify change
# Write-Host "`n3. Verify change:" -ForegroundColor Cyan
# Invoke-EvaSql -Query "SELECT CommitteeID, CommitteeName, IsActive FROM Committee WHERE CommitteeID = 466" -Environment M2-QA

Write-Host "`nExamples complete!" -ForegroundColor Green
