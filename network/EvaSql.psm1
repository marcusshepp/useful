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

Export-ModuleMember -Function Invoke-EvaSql, Invoke-EvaSqlNonQuery
