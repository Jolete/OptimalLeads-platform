$workspaceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $workspaceRoot '.venv\Scripts\python.exe'

$logDir = Join-Path $workspaceRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$jobs = @(
	@{ Name = 'optimalleads-web'; Args = @('-m', 'uvicorn', 'bootstrap:app', '--port', '8080'); Log = Join-Path $logDir 'web.log' },
	@{ Name = 'optimalleads-chat'; Args = @('-m', 'uvicorn', 'projects.optimalleads.chat.main:create_app', '--factory', '--port', '8001'); Log = Join-Path $logDir 'chat.log' },
	@{ Name = 'optimalleads-leads'; Args = @('-m', 'uvicorn', 'projects.optimalleads.leads.main:create_app', '--factory', '--port', '8002'); Log = Join-Path $logDir 'leads.log' },
	@{ Name = 'optimalleads-analytics'; Args = @('-m', 'uvicorn', 'projects.optimalleads.analytics.main:create_app', '--factory', '--port', '8003'); Log = Join-Path $logDir 'analytics.log' },
	@{ Name = 'optimalleads-saga'; Args = @('-m', 'projects.optimalleads.saga.main'); Log = Join-Path $logDir 'saga.log' }
)

foreach ($job in $jobs) {
	$argumentList = @(
		'-NoProfile',
		'-ExecutionPolicy',
		'Bypass',
		'-Command',
		"Set-Location '$workspaceRoot'; & '$pythonExe' $($job.Args -join ' ') *>> '$($job.Log)'")
	Start-Process -WindowStyle Normal -FilePath powershell -ArgumentList $argumentList -WorkingDirectory $workspaceRoot | Out-Null
}

Start-Process 'http://127.0.0.1:8080/'