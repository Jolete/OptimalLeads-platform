param(
	[string[]] $Services = @('web', 'chat', 'leads', 'analytics', 'saga')
)

$workspaceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $workspaceRoot '.venv\Scripts\python.exe'

Get-CimInstance Win32_Process |
	Where-Object { $_.CommandLine -match 'bootstrap:app|projects\.optimalleads\.(chat|leads|analytics|saga)\.main|uvicorn' } |
	ForEach-Object {
		Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
	}

$logDir = Join-Path $workspaceRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

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

Stop-WorkspaceProcesses -Targets $Services

$serviceCommands = @(
	@{ Name = 'web'; Port = 8080; Command = "Set-Location '$workspaceRoot'; & '$pythonExe' -m uvicorn bootstrap:app --port 8080 *>> '$logDir\web.log'" },
	@{ Name = 'chat'; Port = 8001; Command = "Set-Location '$workspaceRoot'; & '$pythonExe' -m uvicorn projects.optimalleads.chat.main:create_app --factory --port 8001 *>> '$logDir\chat.log'" },
	@{ Name = 'leads'; Port = 8002; Command = "Set-Location '$workspaceRoot'; & '$pythonExe' -m uvicorn projects.optimalleads.leads.main:create_app --factory --port 8002 *>> '$logDir\leads.log'" },
	@{ Name = 'analytics'; Port = 8003; Command = "Set-Location '$workspaceRoot'; & '$pythonExe' -m uvicorn projects.optimalleads.analytics.main:create_app --factory --port 8003 *>> '$logDir\analytics.log'" },
	@{ Name = 'saga'; Port = $null; Command = "Set-Location '$workspaceRoot'; & '$pythonExe' -m projects.optimalleads.saga.main *>> '$logDir\saga.log'" }
)

$launchedServices = @()

foreach ($service in $serviceCommands) {
	if ($Services -notcontains $service.Name) {
		continue
	}
	$launchedServices += Start-Process -WindowStyle Normal -PassThru -FilePath powershell -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $service.Command) -WorkingDirectory $workspaceRoot
}

foreach ($service in $serviceCommands) {
	if ($Services -notcontains $service.Name -or $null -eq $service.Port) {
		continue
	}
	Wait-ForPort -Port $service.Port
}

Start-Process 'http://127.0.0.1:8080/'