Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$workspaceFolder = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $workspaceFolder '.venv\Scripts\python.exe'

& (Join-Path $workspaceFolder 'scripts\bootstrap-optimalleads-deps.ps1')

$pythonArgs = @('-NoExit', '-Command')

Start-Process -WindowStyle Normal -FilePath powershell -ArgumentList @($pythonArgs + @("Set-Location '$workspaceFolder'; & '$pythonExe' -m uvicorn bootstrap:app --reload --port 8080")) -WorkingDirectory $workspaceFolder
Start-Process -WindowStyle Normal -FilePath powershell -ArgumentList @($pythonArgs + @("Set-Location '$workspaceFolder'; & '$pythonExe' -m uvicorn projects.optimalleads.chat.main:create_app --factory --reload --port 8001")) -WorkingDirectory $workspaceFolder
Start-Process -WindowStyle Normal -FilePath powershell -ArgumentList @($pythonArgs + @("Set-Location '$workspaceFolder'; & '$pythonExe' -m uvicorn projects.optimalleads.leads.main:create_app --factory --reload --port 8002")) -WorkingDirectory $workspaceFolder
Start-Process -WindowStyle Normal -FilePath powershell -ArgumentList @($pythonArgs + @("Set-Location '$workspaceFolder'; & '$pythonExe' -m uvicorn projects.optimalleads.analytics.main:create_app --factory --reload --port 8003")) -WorkingDirectory $workspaceFolder
Start-Process 'http://127.0.0.1:8080/'