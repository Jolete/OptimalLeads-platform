$workspaceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $workspaceRoot '.venv\Scripts\python.exe'

$logDir = Join-Path $workspaceRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$jobs = @(
	@{ Name = 'optimalleads-web'; Args = @('-m', 'uvicorn', 'bootstrap:app', '--port', '8080'); Log = Join-Path $logDir 'web.log' },
	@{ Name = 'optimalleads-chat'; Args = @('-m', 'uvicorn', 'projects.optimalleads.chat.main:create_app', '--factory', '--port', '8001'); Log = Join-Path $logDir 'chat.log' },
	@{ Name = 'optimalleads-leads'; Args = @('-m', 'uvicorn', 'projects.optimalleads.leads.main:create_app', '--factory', '--port', '8002'); Log = Join-Path $logDir 'leads.log' },
	@{ Name = 'optimalleads-analytics'; Args = @('-m', 'uvicorn', 'projects.optimalleads.analytics.main:create_app', '--factory', '--port', '8003'); Log = Join-Path $logDir 'analytics.log' }
)

foreach ($job in $jobs) {
	Start-Job -Name $job.Name -ScriptBlock {
		param($pythonPath, $workingDir, $arguments, $logPath)
		Set-Location $workingDir
		& $pythonPath @arguments *>> $logPath
	} -ArgumentList $pythonExe, $workspaceRoot, $job.Args, $job.Log | Out-Null
}

Start-Process 'http://127.0.0.1:8080/'