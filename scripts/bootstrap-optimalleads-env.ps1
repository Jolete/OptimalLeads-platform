$workspaceRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$serviceRoots = @(
        @{ Name = 'chat'; Path = Join-Path $workspaceRoot 'projects\optimalleads\chat' },
        @{ Name = 'leads'; Path = Join-Path $workspaceRoot 'projects\optimalleads\leads' },
        @{ Name = 'analytics'; Path = Join-Path $workspaceRoot 'projects\optimalleads\analytics' }
)

foreach ($service in $serviceRoots) {
        $examplePath = Join-Path $service.Path '.env.example'
        $envPath = Join-Path $service.Path '.env'

        if (-not (Test-Path $examplePath)) {
                continue
        }

        if (Test-Path $envPath) {
                continue
        }

        Copy-Item -Path $examplePath -Destination $envPath
        Write-Host "Created $envPath from .env.example"
}