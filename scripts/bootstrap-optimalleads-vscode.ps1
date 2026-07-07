Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$workspaceRoot = Split-Path -Parent $PSScriptRoot
$extensionsFile = Join-Path $workspaceRoot '.vscode\extensions.json'

function Get-CodeCommand {
        foreach ($candidate in @('code', 'code.cmd', 'code.exe')) {
                $command = Get-Command $candidate -ErrorAction SilentlyContinue
                if ($command) {
                        return $command.Source
                }
        }

        return $null
}

if (-not (Test-Path $extensionsFile)) {
        Write-Host 'No .vscode/extensions.json found, skipping extension bootstrap.'
        return
}

$codeCommand = Get-CodeCommand
if (-not $codeCommand) {
        Write-Host 'VS Code CLI was not found in PATH, skipping automatic extension install.'
        return
}

$recommendedExtensions = (Get-Content $extensionsFile -Raw | ConvertFrom-Json).recommendations
if (-not $recommendedExtensions) {
        Write-Host 'No recommended extensions listed, skipping extension bootstrap.'
        return
}

$installedExtensions = & $codeCommand --list-extensions
if (($global:LASTEXITCODE -as [int]) -ne 0) {
        throw 'Failed to query installed VS Code extensions.'
}

foreach ($extensionId in $recommendedExtensions) {
        if ($installedExtensions -contains $extensionId) {
                Write-Host "Extension already installed: $extensionId"
                continue
        }

        Write-Host "Installing VS Code extension: $extensionId"
        & $codeCommand --install-extension $extensionId --force
        if ($LASTEXITCODE -ne 0) {
                throw "Failed to install VS Code extension: $extensionId"
        }
}