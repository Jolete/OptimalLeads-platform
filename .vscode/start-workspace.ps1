param(
	[string[]] $Services = @('web', 'chat', 'leads', 'analytics', 'saga')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$workspaceFolder = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $workspaceFolder '.venv\Scripts\python.exe'

Get-CimInstance Win32_Process |
	Where-Object { $_.CommandLine -match 'bootstrap:app|projects\.optimalleads\.(chat|leads|analytics|saga)\.main|uvicorn' } |
	ForEach-Object {
		Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
	}

& (Join-Path $workspaceFolder 'scripts\bootstrap-optimalleads-deps.ps1')

function Wait-ForPort {
	param(
		[int] $Port,
		[int] $TimeoutSeconds = 90
	)

	$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
	while ((Get-Date) -lt $deadline) {
		if (Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue) {
			return
		}
		Start-Sleep -Seconds 1
	}

	throw "Timed out waiting for port $Port"
}

function Stop-WorkspaceProcesses {
	param(
		[string[]] $Targets
	)

	$patterns = switch ($Targets) {
		'web' { @('bootstrap:app') }
		'chat' { @('projects\.optimalleads\.chat\.main', 'uvicorn.*8001') }
		'leads' { @('projects\.optimalleads\.leads\.main', 'uvicorn.*8002') }
		'analytics' { @('projects\.optimalleads\.analytics\.main', 'uvicorn.*8003') }
		'saga' { @('projects\.optimalleads\.saga\.main') }
		default { @('bootstrap:app', 'projects\.optimalleads\.(chat|leads|analytics|saga)\.main', 'uvicorn') }
	}

	Get-CimInstance Win32_Process |
		Where-Object {
			$commandLine = $_.CommandLine
			$null -ne $commandLine -and ($patterns | Where-Object { $commandLine -match $_ })
		} |
		ForEach-Object {
			Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
		}
}

function Stop-ListenerOnPort {
	param(
		[int] $Port
	)

	Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
		Select-Object -ExpandProperty OwningProcess -Unique |
		ForEach-Object {
			Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
		}

	Get-CimInstance Win32_Process |
		Where-Object { $_.CommandLine -match "--port $Port\b|:${Port}\b" } |
		ForEach-Object {
			Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
		}
}

function Wait-ForPortFree {
	param(
		[int] $Port,
		[int] $TimeoutSeconds = 30
	)

	$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
	while ((Get-Date) -lt $deadline) {
		if (-not (Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)) {
			return
		}
		Start-Sleep -Seconds 1
	}

	throw "Timed out waiting for port $Port to become free"
}

Stop-WorkspaceProcesses -Targets $Services

$serviceCommands = @(
	@{ Name = 'web'; Port = 8080; Args = @('-m', 'uvicorn', 'bootstrap:app', '--port', '8080'); StdOut = Join-Path $workspaceFolder 'logs\web.out.log'; StdErr = Join-Path $workspaceFolder 'logs\web.err.log' },
	@{ Name = 'chat'; Port = 8001; Args = @('-m', 'uvicorn', 'projects.optimalleads.chat.main:create_app', '--factory', '--port', '8001'); StdOut = Join-Path $workspaceFolder 'logs\chat.out.log'; StdErr = Join-Path $workspaceFolder 'logs\chat.err.log' },
	@{ Name = 'leads'; Port = 8002; Args = @('-m', 'uvicorn', 'projects.optimalleads.leads.main:create_app', '--factory', '--port', '8002'); StdOut = Join-Path $workspaceFolder 'logs\leads.out.log'; StdErr = Join-Path $workspaceFolder 'logs\leads.err.log' },
	@{ Name = 'analytics'; Port = 8003; Args = @('-m', 'uvicorn', 'projects.optimalleads.analytics.main:create_app', '--factory', '--port', '8003'); StdOut = Join-Path $workspaceFolder 'logs\analytics.out.log'; StdErr = Join-Path $workspaceFolder 'logs\analytics.err.log' },
	@{ Name = 'saga'; Port = $null; Args = @('-m', 'projects.optimalleads.saga.main'); StdOut = Join-Path $workspaceFolder 'logs\saga.out.log'; StdErr = Join-Path $workspaceFolder 'logs\saga.err.log' }
)

$launchedServices = @()

foreach ($service in $serviceCommands) {
	if ($Services -notcontains $service.Name) {
		continue
	}
	if ($null -ne $service.Port) {
		Stop-ListenerOnPort -Port $service.Port
		Wait-ForPortFree -Port $service.Port
	}
	$launchedServices += Start-Process -WindowStyle Normal -PassThru -FilePath $pythonExe -ArgumentList $service.Args -WorkingDirectory $workspaceFolder -RedirectStandardOutput $service.StdOut -RedirectStandardError $service.StdErr
}

foreach ($service in $serviceCommands) {
	if ($Services -notcontains $service.Name -or $null -eq $service.Port) {
		continue
	}
	Wait-ForPort -Port $service.Port
}
Start-Process 'http://127.0.0.1:8080/'