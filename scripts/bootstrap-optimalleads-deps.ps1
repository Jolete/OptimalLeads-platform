Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$workspaceRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $workspaceRoot '.venv\Scripts\python.exe'

function Get-BasePythonCommand {
        if (Get-Command py -ErrorAction SilentlyContinue) {
                return @{ Command = 'py'; Arguments = @('-3') }
        }

        if (Get-Command python -ErrorAction SilentlyContinue) {
                return @{ Command = 'python'; Arguments = @() }
        }

        throw 'Python is required but neither py nor python was found in PATH.'
}

function Invoke-PythonCommand {
        param(
                [Parameter(Mandatory = $true)]
                [string]$PythonPath,
                [Parameter(Mandatory = $true)]
                [string[]]$Arguments
        )

        & $PythonPath @Arguments
        if ($LASTEXITCODE -ne 0) {
                throw "Python command failed: $PythonPath $($Arguments -join ' ')"
        }
}

$basePython = Get-BasePythonCommand

if (-not (Test-Path $venvPython)) {
        Write-Host 'Creating .venv...'
        & $basePython.Command @($basePython.Arguments + @('-m', 'venv', '.venv'))
        if ($LASTEXITCODE -ne 0) {
                throw 'Failed to create the workspace virtual environment.'
        }
}

$needsInstall = $true
try {
        Invoke-PythonCommand -PythonPath $venvPython -Arguments @('-c', 'import uvicorn')
        $needsInstall = $false
} catch {
        $needsInstall = $true
}

if ($needsInstall) {
        Write-Host 'Installing workspace dependencies...'
        Invoke-PythonCommand -PythonPath $venvPython -Arguments @('-m', 'pip', 'install', '--upgrade', 'pip')
        Invoke-PythonCommand -PythonPath $venvPython -Arguments @('-m', 'pip', 'install', '-e', '.[dev]')
}