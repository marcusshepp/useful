#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Eva Migration Manager

.DESCRIPTION
    This script manages Entity Framework migrations for the Eva project. It provides functionality to:
    1. Update the database to a specific migration
    2. Remove existing migrations
    3. Checkout the model snapshot from develop branch
    4. Add new migrations

.PARAMETER Update
    Update database to a specific migration. If no name provided, will detect previous migration.

.PARAMETER Add
    Add a new migration with the specified name.

.PARAMETER Remove
    Remove specified number of migrations (default: 1).

.PARAMETER Checkout
    Checkout model snapshot from develop branch.

.PARAMETER St
    Show git status after operation.

.EXAMPLE
    .\migrate.ps1
    Runs interactive workflow.

.EXAMPLE
    .\migrate.ps1 -Update "PreviousMigrationName"
    Updates database to specified migration.

.EXAMPLE
    .\migrate.ps1 -Remove 2
    Removes the last 2 migrations.

.AUTHOR
    Marcus Shepherd

.DATE
    January 13, 2025
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [AllowEmptyString()]
    [string]$Update,

    [Parameter(Mandatory = $false)]
    [string]$Add,

    [Parameter(Mandatory = $false)]
    [int]$Remove = 0,

    [Parameter(Mandatory = $false)]
    [switch]$Checkout,

    [Parameter(Mandatory = $false)]
    [switch]$St
)

[string]$script:PathToWorkingDirectory = "~/p/leb/EvaAPI"

[string]$script:EvaAscii = @"

███████╗██╗   ██╗ █████╗ 
██╔════╝██║   ██║██╔══██╗
█████╗  ██║   ██║███████║
██╔══╝  ╚██╗ ██╔╝██╔══██║
███████╗ ╚████╔╝ ██║  ██║
╚══════╝  ╚═══╝  ╚═╝  ╚═╝

"@

enum CommandType {
    Update
    Remove
    Checkout
    Add
}

class MigrationCommand {
    [string]$Description
    [string]$CommandTemplate
    [string]$SuccessMessage
    [string]$InputKey
    [string]$InputPrompt
    [bool]$RequiresConfirmation

    MigrationCommand(
        [string]$description,
        [string]$commandTemplate,
        [string]$successMessage,
        [string]$inputKey,
        [string]$inputPrompt,
        [bool]$requiresConfirmation
    ) {
        $this.Description = $description
        $this.CommandTemplate = $commandTemplate
        $this.SuccessMessage = $successMessage
        $this.InputKey = $inputKey
        $this.InputPrompt = $inputPrompt
        $this.RequiresConfirmation = $requiresConfirmation
    }
}

class MigrationManager {
    [string]$WorkingDirectory
    [string]$MigrationsDirectory
    [hashtable]$Commands

    MigrationManager([string]$workingDirectory) {
        $this.WorkingDirectory = [System.IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($workingDirectory.Replace("~", $env:USERPROFILE)))
        $this.MigrationsDirectory = Join-Path $this.WorkingDirectory "Migrations"
        $this.Commands = @{
            [CommandType]::Update = [MigrationCommand]::new(
                "Update database to previous migration",
                "dotnet ef database update {previous_migration} --context evadbcontext",
                "Database Successfully Updated to Previous Migration! 🎉",
                "previous_migration",
                "Enter the name of the previous migration: ",
                $true
            )
            [CommandType]::Remove = [MigrationCommand]::new(
                "Remove last migration(s)",
                "dotnet ef migrations remove --context evadbcontext",
                "Migration Successfully Removed! 🗑️",
                $null,
                $null,
                $true
            )
            [CommandType]::Checkout = [MigrationCommand]::new(
                "Git checkout develop for the migration snapshot",
                "git checkout develop -- .\Migrations\EvaDbContextModelSnapshot.cs",
                "Model Snapshot Successfully Checked Out! 📥",
                $null,
                $null,
                $true
            )
            [CommandType]::Add = [MigrationCommand]::new(
                "Add a new migration with a unique name",
                "dotnet ef migrations add {new_migration} --context evadbcontext",
                "New Migration Successfully Added! 🚀",
                "new_migration",
                "Enter the name for the new migration: ",
                $true
            )
        }
    }

    [string] GetPreviousMigration() {
        try {
            [System.IO.FileInfo[]]$migrationFiles = Get-ChildItem -Path $this.MigrationsDirectory -Filter "*.cs" -File | 
                Where-Object { 
                    $_.BaseName -ne "EvaDbContextModelSnapshot" -and 
                    -not $_.BaseName.EndsWith(".Designer") 
                }

            if ($migrationFiles.Count -lt 2) {
                return $null
            }

            [System.IO.FileInfo[]]$sortedFiles = $migrationFiles | Sort-Object -Property BaseName
            [string]$previousMigration = $sortedFiles[-2].BaseName

            return $previousMigration
        }
        catch {
            Write-Host "Failed to get previous migration: $_" -ForegroundColor Red
            return $null
        }
    }

    [bool] UpdateDatabaseInteractive([string]$migrationName) {
        [string]$previousMigration = $this.GetPreviousMigration()

        if ([string]::IsNullOrEmpty($migrationName) -and -not [string]::IsNullOrEmpty($previousMigration)) {
            Write-Host "Previous migration detected: $previousMigration" -ForegroundColor Cyan
            [string]$response = Read-Host "Update to this migration? (y/n)"
            if ($response.Trim().ToLower() -eq 'y') {
                $migrationName = $previousMigration
            }
            else {
                $migrationName = Read-Host $this.Commands[[CommandType]::Update].InputPrompt
            }
        }
        elseif ([string]::IsNullOrEmpty($migrationName)) {
            $migrationName = Read-Host $this.Commands[[CommandType]::Update].InputPrompt
        }

        [hashtable]$inputs = @{ "previous_migration" = $migrationName.Trim() }
        return $this.ExecuteCommand($this.Commands[[CommandType]::Update].CommandTemplate, [CommandType]::Update, $inputs)
    }

    [bool] SetupWorkingDirectory() {
        try {
            if (-not (Test-Path $this.WorkingDirectory)) {
                Write-Host "Directory not found: $($this.WorkingDirectory)" -ForegroundColor Red
                return $false
            }

            Set-Location $this.WorkingDirectory
            return $true
        }
        catch {
            Write-Host "Failed to set working directory: $_" -ForegroundColor Red
            return $false
        }
    }

    [bool] ExecuteCommand([string]$command, [CommandType]$commandType, [hashtable]$inputs) {
        try {
            foreach ($key in $inputs.Keys) {
                $command = $command.Replace("{$key}", $inputs[$key])
            }

            Write-Host "Executing: $command" -ForegroundColor Yellow
            
            [string]$output = Invoke-Expression $command 2>&1

            if ($LASTEXITCODE -ne 0) {
                Write-Host "Command failed with exit code: $LASTEXITCODE" -ForegroundColor Red
                Write-Host $output -ForegroundColor Red
                return $false
            }

            if (-not [string]::IsNullOrEmpty($output)) {
                Write-Host $output
            }

            Write-Host ""
            Write-Host ("=" * 50) -ForegroundColor Green
            Write-Host "✅ $($this.Commands[$commandType].SuccessMessage)" -ForegroundColor Green
            Write-Host ("=" * 50) -ForegroundColor Green
            Write-Host ""

            return $true
        }
        catch {
            Write-Host "Unexpected error: $_" -ForegroundColor Red
            return $false
        }
    }

    [void] ShowGitStatus() {
        try {
            Write-Host "`nGit Status:" -ForegroundColor Cyan
            [string]$status = git status 2>&1
            Write-Host $status
        }
        catch {
            Write-Host "Failed to get git status: $_" -ForegroundColor Red
        }
    }

    [void] LogWorkflowSuccess() {
        Write-Host ""
        Write-Host ("=" * 50) -ForegroundColor Green
        Write-Host "✅ Workflow Completed Successfully! 🎉" -ForegroundColor Green
        Write-Host ("=" * 50) -ForegroundColor Green
        Write-Host ""
    }

    [void] RunInteractiveWorkflow() {
        [bool]$success = $true
        [CommandType[]]$commandTypes = [CommandType]::Update, [CommandType]::Remove, [CommandType]::Checkout, [CommandType]::Add

        foreach ($commandType in $commandTypes) {
            [MigrationCommand]$command = $this.Commands[$commandType]
            Write-Host "`nStep: $($command.Description)" -ForegroundColor Cyan
            [string]$response = Read-Host "Do you want to proceed? (y/n)"

            if ($response.Trim().ToLower() -eq 'y') {
                if ($commandType -eq [CommandType]::Update) {
                    if (-not $this.UpdateDatabaseInteractive($null)) {
                        Write-Host "Failed at step: $($command.Description)" -ForegroundColor Red
                        $success = $false
                        break
                    }
                }
                else {
                    [hashtable]$inputs = @{}
                    if (-not [string]::IsNullOrEmpty($command.InputKey) -and -not [string]::IsNullOrEmpty($command.InputPrompt)) {
                        [string]$inputValue = Read-Host $command.InputPrompt
                        $inputs[$command.InputKey] = $inputValue.Trim()
                    }

                    if (-not $this.ExecuteCommand($command.CommandTemplate, $commandType, $inputs)) {
                        Write-Host "Failed at step: $($command.Description)" -ForegroundColor Red
                        $success = $false
                        break
                    }
                }
            }
        }

        if ($success) {
            $this.ShowGitStatus()
            $this.LogWorkflowSuccess()
        }
    }

    [bool] UpdateDatabase([string]$migrationName) {
        return $this.UpdateDatabaseInteractive($migrationName)
    }

    [bool] RemoveMigrations([int]$count) {
        for ([int]$i = 0; $i -lt $count; $i++) {
            if (-not $this.ExecuteCommand($this.Commands[[CommandType]::Remove].CommandTemplate, [CommandType]::Remove, @{})) {
                return $false
            }
        }
        return $true
    }

    [bool] AddMigration([string]$name) {
        [hashtable]$inputs = @{ "new_migration" = $name }
        return $this.ExecuteCommand($this.Commands[[CommandType]::Add].CommandTemplate, [CommandType]::Add, $inputs)
    }

    [bool] CheckoutSnapshot() {
        return $this.ExecuteCommand($this.Commands[[CommandType]::Checkout].CommandTemplate, [CommandType]::Checkout, @{})
    }
}

function Main {
    Write-Host $script:EvaAscii -ForegroundColor Cyan
    Write-Host "Welcome to the Eva Migration Manager! 🦴" -ForegroundColor Green
    Write-Host "Working Directory: $script:PathToWorkingDirectory" -ForegroundColor Gray

    [string]$expandedPath = [Environment]::ExpandEnvironmentVariables($script:PathToWorkingDirectory.Replace("~", $env:USERPROFILE))
    [MigrationManager]$manager = [MigrationManager]::new($expandedPath)

    if (-not $manager.SetupWorkingDirectory()) {
        return
    }

    [bool]$hasUpdateParam = $PSBoundParameters.ContainsKey('Update')
    [bool]$hasAnyCommand = $hasUpdateParam -or 
                           (-not [string]::IsNullOrEmpty($Add)) -or 
                           ($Remove -gt 0) -or 
                           $Checkout

    if (-not $hasAnyCommand) {
        $manager.RunInteractiveWorkflow()
        return
    }

    [bool]$success = $true

    if ($hasUpdateParam) {
        if (-not $manager.UpdateDatabase($Update)) {
            Write-Host "Failed to update database" -ForegroundColor Red
            $success = $false
        }
    }

    if (-not [string]::IsNullOrEmpty($Add)) {
        if (-not $manager.AddMigration($Add)) {
            Write-Host "Failed to add migration" -ForegroundColor Red
            $success = $false
        }
    }

    if ($Remove -gt 0) {
        if (-not $manager.RemoveMigrations($Remove)) {
            Write-Host "Failed to remove migrations" -ForegroundColor Red
            $success = $false
        }
    }

    if ($Checkout) {
        if (-not $manager.CheckoutSnapshot()) {
            Write-Host "Failed to checkout snapshot" -ForegroundColor Red
            $success = $false
        }
    }

    if ($success -and $St) {
        $manager.ShowGitStatus()
    }

    if ($success) {
        $manager.LogWorkflowSuccess()
    }
}

Main
