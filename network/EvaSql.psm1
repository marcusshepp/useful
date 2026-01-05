function Invoke-EvaSql {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Query,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet('Local', 'QA', 'DEMO', 'UAT', 'M2-Local', 'M2-QA', 'M2-DEMO', 'M2-UAT')]
        [string]$Environment = 'QA',
        
        [Parameter(Mandatory=$false)]
        [int]$Timeout = 30
    )
    
    # Connection strings for different environments
    # Passwords are loaded from environment variables for security
    $connectionStrings = @{
        'Local'    = "Data Source=localhost,1433;Initial Catalog=Eva;User ID=SA;Password=$($env:EVA_LOCAL_PASSWORD);TrustServerCertificate=True"
        'QA'       = "Data Source=tvmwsqls01,1433;Initial Catalog=Eva_QA;User ID=EvaQAUser;Password=$($env:EVA_QA_PASSWORD);TrustServerCertificate=True"
        'DEMO'     = "Data Source=uvmwsqls01,1433;Initial Catalog=Eva_DEMO;User ID=EvaDEMOUser;Password=$($env:EVA_DEMO_PASSWORD);TrustServerCertificate=True"
        'UAT'      = "Data Source=uvmwsqls01,1433;Initial Catalog=Eva_UAT;User ID=EvaUATUser;Password=$($env:EVA_UAT_PASSWORD);TrustServerCertificate=True"
        'M2-Local' = "Data Source=localhost,1433;Initial Catalog=Legislature;User=senate_dev_user;Password=$($env:M2_LOCAL_PASSWORD);TrustServerCertificate=True"
        'M2-QA'    = "Data Source=tvmwsqls01,1433;Initial Catalog=Legislature;User=senate_dev_user;Password=$($env:M2_QA_PASSWORD);TrustServerCertificate=True"
        'M2-DEMO'  = "Data Source=MLSQL-QA.lsb.legislature.mi.gov,1433;Initial Catalog=Legislature;User=senate_qa_user;Password=$($env:M2_DEMO_PASSWORD);TrustServerCertificate=True"
        'M2-UAT'   = "Data Source=MLSQL-SUP.lsb.legislature.mi.gov,1433;Initial Catalog=Legislature;User=senate_sup_user;Password=$($env:M2_UAT_PASSWORD);TrustServerCertificate=True"
    }
    
    $connectionString = $connectionStrings[$Environment]
    
    # Safety check: Only allow SELECT queries
    $queryUpper = $Query.Trim().ToUpper()
    if ($queryUpper -notmatch '^\s*SELECT\s') {
        Write-Error "Only SELECT queries are allowed in Invoke-EvaSql. Use Invoke-EvaSqlNonQuery for INSERT operations."
        return
    }
    
    # Additional safety: Block dangerous keywords
    $dangerousKeywords = @('DELETE', 'UPDATE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE', 'sp_executesql')
    foreach ($keyword in $dangerousKeywords) {
        if ($queryUpper -match "\b$keyword\b") {
            Write-Error "Dangerous keyword '$keyword' detected in query. Only SELECT statements are allowed."
            return
        }
    }
    
    try {
        $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
        $connection.Open()
        
        $command = $connection.CreateCommand()
        $command.CommandText = $Query
        $command.CommandTimeout = $Timeout
        
        $adapter = New-Object System.Data.SqlClient.SqlDataAdapter($command)
        $dataset = New-Object System.Data.DataSet
        $adapter.Fill($dataset) | Out-Null
        
        $connection.Close()
        
        return $dataset.Tables[0]
    }
    catch {
        Write-Error "SQL Error: $($_.Exception.Message)"
        if ($connection.State -eq 'Open') {
            $connection.Close()
        }
    }
}

function Invoke-EvaSqlNonQuery {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Query,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet('Local', 'QA', 'DEMO', 'UAT', 'M2-Local', 'M2-QA', 'M2-DEMO', 'M2-UAT')]
        [string]$Environment = 'QA',
        
        [Parameter(Mandatory=$false)]
        [int]$Timeout = 30
    )
    
    # Connection strings for different environments
    # Passwords are loaded from environment variables for security
    $connectionStrings = @{
        'Local'    = "Data Source=localhost,1433;Initial Catalog=Eva;User ID=SA;Password=$($env:EVA_LOCAL_PASSWORD);TrustServerCertificate=True"
        'QA'       = "Data Source=tvmwsqls01,1433;Initial Catalog=Eva_QA;User ID=EvaQAUser;Password=$($env:EVA_QA_PASSWORD);TrustServerCertificate=True"
        'DEMO'     = "Data Source=uvmwsqls01,1433;Initial Catalog=Eva_DEMO;User ID=EvaDEMOUser;Password=$($env:EVA_DEMO_PASSWORD);TrustServerCertificate=True"
        'UAT'      = "Data Source=uvmwsqls01,1433;Initial Catalog=Eva_UAT;User ID=EvaUATUser;Password=$($env:EVA_UAT_PASSWORD);TrustServerCertificate=True"
        'M2-Local' = "Data Source=localhost,1433;Initial Catalog=Legislature;User=senate_dev_user;Password=$($env:M2_LOCAL_PASSWORD);TrustServerCertificate=True"
        'M2-QA'    = "Data Source=tvmwsqls01,1433;Initial Catalog=Legislature;User=senate_dev_user;Password=$($env:M2_QA_PASSWORD);TrustServerCertificate=True"
        'M2-DEMO'  = "Data Source=MLSQL-QA.lsb.legislature.mi.gov,1433;Initial Catalog=Legislature;User=senate_qa_user;Password=$($env:M2_DEMO_PASSWORD);TrustServerCertificate=True"
        'M2-UAT'   = "Data Source=MLSQL-SUP.lsb.legislature.mi.gov,1433;Initial Catalog=Legislature;User=senate_sup_user;Password=$($env:M2_UAT_PASSWORD);TrustServerCertificate=True"
    }
    
    $connectionString = $connectionStrings[$Environment]
    
    # Safety check: Only allow INSERT queries
    $queryUpper = $Query.Trim().ToUpper()
    if ($queryUpper -notmatch '^\s*INSERT\s') {
        Write-Error "Only INSERT queries are allowed in Invoke-EvaSqlNonQuery. UPDATE and DELETE are blocked for safety."
        return
    }
    
    # Additional safety: Block dangerous keywords
    $dangerousKeywords = @('DELETE', 'UPDATE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE', 'sp_executesql')
    foreach ($keyword in $dangerousKeywords) {
        if ($queryUpper -match "\b$keyword\b") {
            Write-Error "Dangerous keyword '$keyword' detected in query. Only INSERT statements are allowed."
            return
        }
    }
    
    try {
        $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
        $connection.Open()
        
        $command = $connection.CreateCommand()
        $command.CommandText = $Query
        $command.CommandTimeout = $Timeout
        
        $rowsAffected = $command.ExecuteNonQuery()
        
        $connection.Close()
        
        Write-Host "Rows affected: $rowsAffected" -ForegroundColor Green
        return $rowsAffected
    }
    catch {
        Write-Error "SQL Error: $($_.Exception.Message)"
        if ($connection.State -eq 'Open') {
            $connection.Close()
        }
    }
}

function Copy-EvaDatabase {
    <#
    .SYNOPSIS
        Duplicates a database on the same SQL Server instance using backup/restore.
    
    .DESCRIPTION
        Creates a copy of an existing database with a new name. Uses SQL Server's 
        BACKUP and RESTORE commands. Only works on QA environments for safety.
    
    .PARAMETER SourceDatabase
        The name of the database to copy (e.g., 'Legislature', 'Eva_QA')
    
    .PARAMETER TargetDatabase
        The name for the new database copy (e.g., 'INT_Legislature')
    
    .PARAMETER Environment
        The environment to operate on. Only QA environments are allowed.
    
    .PARAMETER BackupPath
        Optional. The path for the temporary backup file. Defaults to SQL Server's default backup location.
    
    .PARAMETER Force
        Skip confirmation prompt.
    
    .EXAMPLE
        Copy-EvaDatabase -SourceDatabase "Legislature" -TargetDatabase "INT_Legislature" -Environment "M2-QA"
    
    .EXAMPLE
        Copy-EvaDatabase -SourceDatabase "Eva_QA" -TargetDatabase "Eva_INT" -Environment "QA" -Force
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$SourceDatabase,
        
        [Parameter(Mandatory=$true)]
        [string]$TargetDatabase,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet('QA', 'M2-QA')]
        [string]$Environment = 'M2-QA',
        
        [Parameter(Mandatory=$false)]
        [string]$BackupPath = $null,
        
        [Parameter(Mandatory=$false)]
        [switch]$Force,
        
        [Parameter(Mandatory=$false)]
        [int]$Timeout = 300  # 5 minutes default for large databases
    )
    
    # Server configuration for QA environments
    $serverConfig = @{
        'QA'    = @{
            Server = "tvmwsqls01,1433"
            User = "EvaQAUser"
            PasswordEnvVar = "EVA_QA_PASSWORD"
        }
        'M2-QA' = @{
            Server = "tvmwsqls01,1433"
            User = "senate_dev_user"
            PasswordEnvVar = "M2_QA_PASSWORD"
        }
    }
    
    $config = $serverConfig[$Environment]
    $password = [System.Environment]::GetEnvironmentVariable($config.PasswordEnvVar)
    
    if (-not $password) {
        Write-Error "Environment variable '$($config.PasswordEnvVar)' not set. Please load your .env file."
        return
    }
    
    # Confirmation prompt
    if (-not $Force) {
        Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
        Write-Host "║           DATABASE DUPLICATION WARNING                        ║" -ForegroundColor Yellow
        Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Yellow
        Write-Host "║  Source Database: $($SourceDatabase.PadRight(40))║" -ForegroundColor Cyan
        Write-Host "║  Target Database: $($TargetDatabase.PadRight(40))║" -ForegroundColor Cyan
        Write-Host "║  Server:          $($config.Server.PadRight(40))║" -ForegroundColor Cyan
        Write-Host "║  Environment:     $($Environment.PadRight(40))║" -ForegroundColor Cyan
        Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
        
        $confirmation = Read-Host "`nAre you sure you want to proceed? (yes/no)"
        if ($confirmation -ne 'yes') {
            Write-Host "Operation cancelled." -ForegroundColor Red
            return
        }
    }
    
    # Build connection string to master database (required for backup/restore operations)
    $connectionString = "Data Source=$($config.Server);Initial Catalog=master;User ID=$($config.User);Password=$password;TrustServerCertificate=True"
    
    try {
        $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
        $connection.Open()
        
        Write-Host "`n[1/5] Connected to server..." -ForegroundColor Green
        
        # Step 1: Check if source database exists
        $checkSourceQuery = "SELECT database_id FROM sys.databases WHERE name = '$SourceDatabase'"
        $cmd = $connection.CreateCommand()
        $cmd.CommandText = $checkSourceQuery
        $result = $cmd.ExecuteScalar()
        
        if (-not $result) {
            Write-Error "Source database '$SourceDatabase' does not exist."
            $connection.Close()
            return
        }
        
        Write-Host "[2/5] Source database '$SourceDatabase' verified..." -ForegroundColor Green
        
        # Step 2: Check if target database already exists
        $checkTargetQuery = "SELECT database_id FROM sys.databases WHERE name = '$TargetDatabase'"
        $cmd.CommandText = $checkTargetQuery
        $targetExists = $cmd.ExecuteScalar()
        
        if ($targetExists) {
            Write-Error "Target database '$TargetDatabase' already exists. Please drop it first or choose a different name."
            $connection.Close()
            return
        }
        
        Write-Host "[3/5] Target database name '$TargetDatabase' is available..." -ForegroundColor Green
        
        # Determine backup path first (needed for RESTORE FILELISTONLY)
        if (-not $BackupPath) {
            # Get SQL Server's default backup directory
            $backupDirQuery = "SELECT SERVERPROPERTY('InstanceDefaultBackupPath') AS BackupPath"
            $cmd.CommandText = $backupDirQuery
            $BackupPath = $cmd.ExecuteScalar()
            
            if (-not $BackupPath) {
                $BackupPath = "C:\Temp"  # Fallback
            }
        }
        
        $backupFile = Join-Path $BackupPath "$($SourceDatabase)_CopyBackup_$(Get-Date -Format 'yyyyMMdd_HHmmss').bak"
        
        Write-Host "[4/6] Creating backup at: $backupFile" -ForegroundColor Green
        
        # Step 4: Backup the source database
        $backupQuery = "BACKUP DATABASE [$SourceDatabase] TO DISK = '$backupFile' WITH FORMAT, COPY_ONLY, COMPRESSION"
        $cmd.CommandText = $backupQuery
        $cmd.CommandTimeout = $Timeout
        $cmd.ExecuteNonQuery() | Out-Null
        
        Write-Host "      Backup completed successfully!" -ForegroundColor Green
        
        # Step 5: Get file information from the backup (works without elevated permissions)
        Write-Host "[5/6] Reading file information from backup..." -ForegroundColor Green
        
        $fileListQuery = "RESTORE FILELISTONLY FROM DISK = '$backupFile'"
        $cmd.CommandText = $fileListQuery
        $adapter = New-Object System.Data.SqlClient.SqlDataAdapter($cmd)
        $fileTable = New-Object System.Data.DataTable
        $adapter.Fill($fileTable) | Out-Null
        
        if ($fileTable.Rows.Count -eq 0) {
            Write-Error "Could not retrieve file information from backup."
            $connection.Close()
            return
        }
        
        # Step 6: Build RESTORE command with MOVE options
        Write-Host "[6/6] Restoring as '$TargetDatabase'..." -ForegroundColor Green
        
        $moveStatements = @()
        foreach ($row in $fileTable.Rows) {
            # RESTORE FILELISTONLY returns: LogicalName, PhysicalName, Type (D=data, L=log)
            $logicalName = $row["LogicalName"]
            $physicalPath = $row["PhysicalName"]
            $fileType = $row["Type"]
            
            # Generate new physical path for target database
            $directory = [System.IO.Path]::GetDirectoryName($physicalPath)
            $extension = [System.IO.Path]::GetExtension($physicalPath)
            
            if ($fileType -eq "D") {
                $newFileName = "$TargetDatabase$extension"
            } else {
                $newFileName = "$($TargetDatabase)_log$extension"
            }
            
            $newPhysicalPath = Join-Path $directory $newFileName
            $moveStatements += "MOVE '$logicalName' TO '$newPhysicalPath'"
        }
        
        $moveClause = $moveStatements -join ", "
        
        $restoreQuery = @"
RESTORE DATABASE [$TargetDatabase] 
FROM DISK = '$backupFile' 
WITH $moveClause,
REPLACE,
RECOVERY
"@
        
        $cmd.CommandText = $restoreQuery
        $cmd.CommandTimeout = $Timeout
        $cmd.ExecuteNonQuery() | Out-Null
        
        Write-Host "      Restore completed successfully!" -ForegroundColor Green
        
        # Clean up backup file
        $cleanupQuery = "EXEC xp_delete_file 0, '$backupFile'"
        $cmd.CommandText = $cleanupQuery
        try {
            $cmd.ExecuteNonQuery() | Out-Null
            Write-Host "`n      Temporary backup file cleaned up." -ForegroundColor Gray
        } catch {
            Write-Host "`n      Note: Could not delete temporary backup file. Please delete manually: $backupFile" -ForegroundColor Yellow
        }
        
        $connection.Close()
        
        Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║           DATABASE DUPLICATION COMPLETE                       ║" -ForegroundColor Green
        Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Green
        Write-Host "║  New database '$TargetDatabase' created successfully!        " -ForegroundColor Green
        Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
        
        return @{
            Success = $true
            SourceDatabase = $SourceDatabase
            TargetDatabase = $TargetDatabase
            Server = $config.Server
        }
    }
    catch {
        Write-Error "Database copy failed: $($_.Exception.Message)"
        if ($connection.State -eq 'Open') {
            $connection.Close()
        }
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Remove-EvaDatabase {
    <#
    .SYNOPSIS
        Drops a database from a QA environment. USE WITH EXTREME CAUTION.
    
    .DESCRIPTION
        Permanently deletes a database. Only works on QA environments and requires
        explicit confirmation unless -Force is specified.
    
    .PARAMETER DatabaseName
        The name of the database to drop.
    
    .PARAMETER Environment
        The environment to operate on. Only QA environments are allowed.
    
    .PARAMETER Force
        Skip confirmation prompt. Still requires typing the database name.
    
    .EXAMPLE
        Remove-EvaDatabase -DatabaseName "INT_Legislature" -Environment "M2-QA"
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$DatabaseName,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet('QA', 'M2-QA')]
        [string]$Environment = 'M2-QA',
        
        [Parameter(Mandatory=$false)]
        [switch]$Force
    )
    
    # Protect critical databases
    $protectedDatabases = @('master', 'tempdb', 'model', 'msdb', 'Legislature', 'Eva_QA', 'Eva_DEMO', 'Eva_UAT')
    
    if ($protectedDatabases -contains $DatabaseName) {
        Write-Error "Cannot drop protected database '$DatabaseName'. This database is on the protected list."
        return
    }
    
    # Server configuration for QA environments
    $serverConfig = @{
        'QA'    = @{
            Server = "tvmwsqls01,1433"
            User = "EvaQAUser"
            PasswordEnvVar = "EVA_QA_PASSWORD"
        }
        'M2-QA' = @{
            Server = "tvmwsqls01,1433"
            User = "senate_dev_user"
            PasswordEnvVar = "M2_QA_PASSWORD"
        }
    }
    
    $config = $serverConfig[$Environment]
    $password = [System.Environment]::GetEnvironmentVariable($config.PasswordEnvVar)
    
    if (-not $password) {
        Write-Error "Environment variable '$($config.PasswordEnvVar)' not set. Please load your .env file."
        return
    }
    
    # Confirmation prompt - always require typing the database name
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║              DANGER: DATABASE DELETION                        ║" -ForegroundColor Red
    Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Red
    Write-Host "║  Database:    $($DatabaseName.PadRight(44))║" -ForegroundColor Yellow
    Write-Host "║  Server:      $($config.Server.PadRight(44))║" -ForegroundColor Yellow
    Write-Host "║  Environment: $($Environment.PadRight(44))║" -ForegroundColor Yellow
    Write-Host "║                                                              ║" -ForegroundColor Red
    Write-Host "║  THIS ACTION CANNOT BE UNDONE!                               ║" -ForegroundColor Red
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Red
    
    $confirmName = Read-Host "`nType the database name to confirm deletion"
    if ($confirmName -ne $DatabaseName) {
        Write-Host "Database name does not match. Operation cancelled." -ForegroundColor Red
        return
    }
    
    if (-not $Force) {
        $finalConfirm = Read-Host "Final confirmation - type 'DELETE' to proceed"
        if ($finalConfirm -ne 'DELETE') {
            Write-Host "Operation cancelled." -ForegroundColor Red
            return
        }
    }
    
    $connectionString = "Data Source=$($config.Server);Initial Catalog=master;User ID=$($config.User);Password=$password;TrustServerCertificate=True"
    
    try {
        $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
        $connection.Open()
        
        # Check if database exists
        $checkQuery = "SELECT database_id FROM sys.databases WHERE name = '$DatabaseName'"
        $cmd = $connection.CreateCommand()
        $cmd.CommandText = $checkQuery
        $result = $cmd.ExecuteScalar()
        
        if (-not $result) {
            Write-Error "Database '$DatabaseName' does not exist."
            $connection.Close()
            return
        }
        
        # Set to single user and drop
        $dropQuery = @"
ALTER DATABASE [$DatabaseName] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE [$DatabaseName];
"@
        $cmd.CommandText = $dropQuery
        $cmd.ExecuteNonQuery() | Out-Null
        
        $connection.Close()
        
        Write-Host "`nDatabase '$DatabaseName' has been deleted." -ForegroundColor Green
        
        return @{
            Success = $true
            DatabaseName = $DatabaseName
        }
    }
    catch {
        Write-Error "Failed to drop database: $($_.Exception.Message)"
        if ($connection.State -eq 'Open') {
            $connection.Close()
        }
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Get-EvaDatabases {
    <#
    .SYNOPSIS
        Lists all databases on a QA server.
    
    .PARAMETER Environment
        The environment to query.
    
    .EXAMPLE
        Get-EvaDatabases -Environment "M2-QA"
    #>
    param(
        [Parameter(Mandatory=$false)]
        [ValidateSet('QA', 'M2-QA')]
        [string]$Environment = 'M2-QA'
    )
    
    $serverConfig = @{
        'QA'    = @{
            Server = "tvmwsqls01,1433"
            User = "EvaQAUser"
            PasswordEnvVar = "EVA_QA_PASSWORD"
        }
        'M2-QA' = @{
            Server = "tvmwsqls01,1433"
            User = "senate_dev_user"
            PasswordEnvVar = "M2_QA_PASSWORD"
        }
    }
    
    $config = $serverConfig[$Environment]
    $password = [System.Environment]::GetEnvironmentVariable($config.PasswordEnvVar)
    
    if (-not $password) {
        Write-Error "Environment variable '$($config.PasswordEnvVar)' not set. Please load your .env file."
        return
    }
    
    $connectionString = "Data Source=$($config.Server);Initial Catalog=master;User ID=$($config.User);Password=$password;TrustServerCertificate=True"
    
    try {
        $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
        $connection.Open()
        
        $query = @"
SELECT 
    d.name AS DatabaseName,
    d.state_desc AS State,
    d.create_date AS Created,
    CAST(SUM(mf.size) * 8.0 / 1024 AS DECIMAL(10,2)) AS SizeMB
FROM sys.databases d
JOIN sys.master_files mf ON d.database_id = mf.database_id
GROUP BY d.name, d.state_desc, d.create_date
ORDER BY d.name
"@
        
        $cmd = $connection.CreateCommand()
        $cmd.CommandText = $query
        $adapter = New-Object System.Data.SqlClient.SqlDataAdapter($cmd)
        $table = New-Object System.Data.DataTable
        $adapter.Fill($table) | Out-Null
        
        $connection.Close()
        
        return $table
    }
    catch {
        Write-Error "Failed to list databases: $($_.Exception.Message)"
        if ($connection.State -eq 'Open') {
            $connection.Close()
        }
    }
}

Export-ModuleMember -Function Invoke-EvaSql, Invoke-EvaSqlNonQuery, Copy-EvaDatabase, Remove-EvaDatabase, Get-EvaDatabases
