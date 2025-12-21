# Load environment variables from .env file
$envFile = Join-Path $PSScriptRoot ".env"

if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)\s*$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
} else {
    Write-Error ".env file not found at $envFile"
    exit 1
}

# Get credentials from environment variables
$username = $env:LOWER_ENV_USERNAME
$password = $env:LOWER_ENV_PASSWORD

if (-not $username -or -not $password) {
    Write-Error "Username or password not found in .env file"
    exit 1
}

# Network drive configuration
$driveLetter = "X:"
$networkPath = "\\tvmwapps01\d$"

# Remove existing mapping if it exists
$existingDrive = Get-PSDrive | Where-Object { $_.Name -eq $driveLetter.TrimEnd(':') -and $_.Provider.Name -eq 'FileSystem' }
if ($existingDrive) {
    Write-Host "Removing existing drive mapping for $driveLetter..."
    net use $driveLetter /delete
}

# Connect to the network drive
Write-Host "Connecting to $networkPath as $username..."
net use $driveLetter $networkPath /user:$username $password

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully connected to $driveLetter ($networkPath)" -ForegroundColor Green
} else {
    Write-Error "Failed to connect to network drive"
    exit 1
}
