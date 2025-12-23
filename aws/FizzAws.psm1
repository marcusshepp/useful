<#
.SYNOPSIS
    Fizz AWS Management Module - SSH and Docker operations for the Fizz production app.

.DESCRIPTION
    This module provides functions to:
    - SSH into the EC2 instance running Fizz
    - Execute Docker commands on the remote server
    - View and tail container logs
    - Manage container lifecycle (start, stop, restart)
    - Debug production issues

.NOTES
    Requires: SSH client, .env file with EC2_HOST, EC2_USER, SSH_KEY_PATH
#>

# Load environment variables from .env file
function Import-FizzEnv {
    [CmdletBinding()]
    param(
        [string]$EnvPath = "$PSScriptRoot\.env"
    )
    
    if (-not (Test-Path $EnvPath)) {
        Write-Error "Environment file not found: $EnvPath"
        Write-Host "Copy .env.example to .env and fill in your values" -ForegroundColor Yellow
        return $false
    }
    
    Get-Content $EnvPath | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($value) {
                Set-Item -Path "env:$name" -Value $value
            }
        }
    }
    return $true
}

# Validate required environment variables
function Test-FizzConfig {
    [CmdletBinding()]
    param()
    
    $required = @('EC2_HOST', 'EC2_USER', 'SSH_KEY_PATH')
    $missing = @()
    
    foreach ($var in $required) {
        if (-not (Get-Item -Path "env:$var" -ErrorAction SilentlyContinue) -or 
            [string]::IsNullOrWhiteSpace((Get-Item -Path "env:$var").Value)) {
            $missing += $var
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Error "Missing required environment variables: $($missing -join ', ')"
        Write-Host "Edit .env file and set these values" -ForegroundColor Yellow
        return $false
    }
    
    if (-not (Test-Path $env:SSH_KEY_PATH)) {
        Write-Error "SSH key not found: $env:SSH_KEY_PATH"
        return $false
    }
    
    return $true
}

# Build SSH command base
function Get-SshCommand {
    [CmdletBinding()]
    param(
        [string]$Command = ""
    )
    
    $sshArgs = @(
        "-i", $env:SSH_KEY_PATH,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "$($env:EC2_USER)@$($env:EC2_HOST)"
    )
    
    if ($Command) {
        $sshArgs += $Command
    }
    
    return $sshArgs
}

#region SSH Functions

<#
.SYNOPSIS
    Opens an interactive SSH session to the Fizz EC2 instance.
#>
function Connect-FizzServer {
    [CmdletBinding()]
    param()
    
    if (-not (Test-FizzConfig)) { return }
    
    Write-Host "Connecting to Fizz server at $env:EC2_HOST..." -ForegroundColor Cyan
    $args = Get-SshCommand
    & ssh @args
}

<#
.SYNOPSIS
    Executes a command on the Fizz EC2 instance via SSH.
#>
function Invoke-FizzSsh {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, Position = 0)]
        [string]$Command
    )
    
    if (-not (Test-FizzConfig)) { return }
    
    $args = Get-SshCommand -Command $Command
    & ssh @args
}

#endregion

#region Docker Functions

<#
.SYNOPSIS
    Lists all Docker containers on the Fizz server.
#>
function Get-FizzContainers {
    [CmdletBinding()]
    param(
        [switch]$All
    )
    
    $cmd = if ($All) { "docker ps -a" } else { "docker ps" }
    Invoke-FizzSsh $cmd
}

<#
.SYNOPSIS
    Gets logs from a Fizz Docker container.
#>
function Get-FizzLogs {
    [CmdletBinding()]
    param(
        [Parameter(Position = 0)]
        [ValidateSet('app', 'postgres', 'redis', 'worker-discovery', 'worker-screenshots', 
                     'worker-lighthouse', 'worker-vision', 'worker-sections', 'worker-email', 
                     'worker-followup', 'migrate', 'caddy')]
        [string]$Container = 'app',
        
        [int]$Tail = 100,
        [switch]$Follow,
        [string]$Since
    )
    
    $containerName = "fizz-$Container"
    $cmd = "docker logs $containerName --tail $Tail"
    
    if ($Since) {
        $cmd += " --since $Since"
    }
    
    if ($Follow) {
        $cmd += " -f"
        Write-Host "Following logs for $containerName (Ctrl+C to stop)..." -ForegroundColor Yellow
    }
    
    Invoke-FizzSsh $cmd
}

<#
.SYNOPSIS
    Tails logs from all Fizz containers using docker-compose.
#>
function Watch-FizzLogs {
    [CmdletBinding()]
    param(
        [int]$Tail = 50
    )
    
    $cmd = "cd $env:FIZZ_APP_DIR && docker compose logs -f --tail $Tail"
    Write-Host "Following all container logs (Ctrl+C to stop)..." -ForegroundColor Yellow
    Invoke-FizzSsh $cmd
}

<#
.SYNOPSIS
    Restarts a Fizz Docker container.
#>
function Restart-FizzContainer {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, Position = 0)]
        [ValidateSet('app', 'postgres', 'redis', 'worker-discovery', 'worker-screenshots', 
                     'worker-lighthouse', 'worker-vision', 'worker-sections', 'worker-email', 
                     'worker-followup', 'caddy')]
        [string]$Container
    )
    
    $containerName = "fizz-$Container"
    Write-Host "Restarting $containerName..." -ForegroundColor Yellow
    Invoke-FizzSsh "docker restart $containerName"
    Write-Host "Container restarted." -ForegroundColor Green
}

<#
.SYNOPSIS
    Executes a command inside a Fizz container.
#>
function Invoke-FizzDocker {
    [CmdletBinding()]
    param(
        [Parameter(Position = 0)]
        [ValidateSet('app', 'postgres', 'redis', 'worker-discovery', 'worker-screenshots', 
                     'worker-lighthouse', 'worker-vision', 'worker-sections', 'worker-email', 
                     'worker-followup', 'caddy')]
        [string]$Container = 'app',
        
        [Parameter(Mandatory, Position = 1)]
        [string]$Command,
        
        [switch]$Interactive
    )
    
    $containerName = "fizz-$Container"
    $flags = if ($Interactive) { "-it" } else { "-i" }
    Invoke-FizzSsh "docker exec $flags $containerName $Command"
}

<#
.SYNOPSIS
    Opens an interactive shell inside a Fizz container.
#>
function Enter-FizzContainer {
    [CmdletBinding()]
    param(
        [Parameter(Position = 0)]
        [ValidateSet('app', 'postgres', 'redis', 'worker-discovery', 'worker-screenshots', 
                     'worker-lighthouse', 'worker-vision', 'worker-sections', 'worker-email', 
                     'worker-followup', 'caddy')]
        [string]$Container = 'app',
        
        [string]$Shell = '/bin/sh'
    )
    
    $containerName = "fizz-$Container"
    Write-Host "Entering $containerName shell..." -ForegroundColor Cyan
    
    # For interactive shell, we need to allocate a TTY
    $sshArgs = @(
        "-i", $env:SSH_KEY_PATH,
        "-o", "StrictHostKeyChecking=no", 
        "-o", "UserKnownHostsFile=/dev/null",
        "-t",  # Force TTY allocation
        "$($env:EC2_USER)@$($env:EC2_HOST)",
        "docker exec -it $containerName $Shell"
    )
    & ssh @sshArgs
}

<#
.SYNOPSIS
    Runs docker-compose commands on the Fizz server.
#>
function Invoke-FizzCompose {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, Position = 0)]
        [ValidateSet('up', 'down', 'restart', 'ps', 'pull', 'build', 'logs')]
        [string]$Action,
        
        [string]$Service,
        [switch]$Detach,
        [switch]$Build
    )
    
    $cmd = "cd $env:FIZZ_APP_DIR && docker compose $Action"
    
    if ($Action -eq 'up' -and $Detach) {
        $cmd += " -d"
    }
    if ($Action -eq 'up' -and $Build) {
        $cmd += " --build"
    }
    if ($Service) {
        $cmd += " $Service"
    }
    
    Write-Host "Running: docker compose $Action $Service" -ForegroundColor Cyan
    Invoke-FizzSsh $cmd
}

#endregion

#region Debugging Functions

<#
.SYNOPSIS
    Gets the health status of all Fizz containers.
#>
function Get-FizzHealth {
    [CmdletBinding()]
    param()
    
    Write-Host "`n=== Fizz Container Health ===" -ForegroundColor Cyan
    Invoke-FizzSsh "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep fizz"
    
    Write-Host "`n=== Disk Usage ===" -ForegroundColor Cyan
    Invoke-FizzSsh "df -h / | tail -1"
    
    Write-Host "`n=== Memory Usage ===" -ForegroundColor Cyan
    Invoke-FizzSsh "free -h | head -2"
    
    Write-Host "`n=== Docker Disk Usage ===" -ForegroundColor Cyan
    Invoke-FizzSsh "docker system df"
}

<#
.SYNOPSIS
    Gets recent error logs from all workers.
#>
function Get-FizzErrors {
    [CmdletBinding()]
    param(
        [int]$Lines = 50
    )
    
    $workers = @('app', 'worker-discovery', 'worker-screenshots', 'worker-lighthouse', 
                 'worker-vision', 'worker-sections', 'worker-email', 'worker-followup')
    
    foreach ($worker in $workers) {
        Write-Host "`n=== Errors in fizz-$worker ===" -ForegroundColor Yellow
        Invoke-FizzSsh "docker logs fizz-$worker --tail $Lines 2>&1 | grep -i -E 'error|exception|failed|fatal' | tail -10"
    }
}

<#
.SYNOPSIS
    Checks database connectivity from the app container.
#>
function Test-FizzDatabase {
    [CmdletBinding()]
    param()
    
    Write-Host "Testing database connection..." -ForegroundColor Cyan
    Invoke-FizzSsh "docker exec fizz-app npx prisma db execute --stdin <<< 'SELECT 1'"
}

<#
.SYNOPSIS
    Shows resource usage for all Fizz containers.
#>
function Get-FizzStats {
    [CmdletBinding()]
    param()
    
    Write-Host "Container resource usage (Ctrl+C to stop)..." -ForegroundColor Cyan
    Invoke-FizzSsh "docker stats --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}' \$(docker ps -q --filter 'name=fizz')"
}

#endregion

#region Initialization

# Auto-load environment on module import
$script:envLoaded = Import-FizzEnv

# Export functions
Export-ModuleMember -Function @(
    'Import-FizzEnv',
    'Test-FizzConfig',
    'Connect-FizzServer',
    'Invoke-FizzSsh',
    'Get-FizzContainers',
    'Get-FizzLogs',
    'Watch-FizzLogs',
    'Restart-FizzContainer',
    'Invoke-FizzDocker',
    'Enter-FizzContainer',
    'Invoke-FizzCompose',
    'Get-FizzHealth',
    'Get-FizzErrors',
    'Test-FizzDatabase',
    'Get-FizzStats'
)

#endregion
