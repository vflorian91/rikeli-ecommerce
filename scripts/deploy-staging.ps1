param([Parameter(Mandatory=$true)][string]$ImagePrefix)
$ErrorActionPreference = 'Stop'
$env:STAGING_IMAGE_PREFIX = $ImagePrefix
$env:POSTGRES_DB = 'rikeli_staging'
$env:POSTGRES_USER = 'rikeli_staging'
$secretDirectory = Join-Path $env:LOCALAPPDATA 'Rikeli\staging'
$secretFile = Join-Path $secretDirectory 'postgres.credential.xml'
if (!(Test-Path $secretFile)) {
    $existingVolume = docker volume ls --filter name=rikeli-staging_postgres_data --format '{{.Name}}'
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo consultar Docker' }
    if ($existingVolume -contains 'rikeli-staging_postgres_data') { throw 'Existe una base staging sin su credencial. Recuperar la credencial antes de desplegar.' }
    New-Item -ItemType Directory -Force $secretDirectory | Out-Null
    $secret = ConvertTo-SecureString ([guid]::NewGuid().ToString('N')) -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential('rikeli_staging', $secret)
    $credential | Export-Clixml $secretFile
}
$credential = Import-Clixml $secretFile
$env:POSTGRES_PASSWORD = $credential.GetNetworkCredential().Password
$composeArgs = @('compose','-f','docker-compose.yml','-f','docker-compose.staging.yml','-p','rikeli-staging')
$reportDirectory = Join-Path (Get-Location).Path 'test-results/staging'
New-Item -ItemType Directory -Force $reportDirectory | Out-Null
try {
    docker @composeArgs up -d --no-build --wait --wait-timeout 240
    if ($LASTEXITCODE -ne 0) { throw 'Staging no alcanzo estado saludable' }
    $services = @('auth','catalogo','pedidos','pagos')
    $report = foreach ($index in 0..3) {
        $port = 8101 + $index
        $url = "http://127.0.0.1:$port/health"
        $response = Invoke-RestMethod -Uri $url -TimeoutSec 15
        if ($response.service -ne $services[$index] -or $response.status -ne 'ok' -or $response.dependencies.postgres -ne 'ok' -or $response.dependencies.redis -ne 'ok') {
            throw "Comprobacion fallida: $url"
        }
        [pscustomobject]@{service=$services[$index]; url=$url; status=$response.status; imagePrefix=$ImagePrefix; checkedAt=(Get-Date).ToUniversalTime().ToString('o')}
    }
    $report | ConvertTo-Json | Set-Content (Join-Path $reportDirectory 'health.json')
    $report | Format-Table
}
catch {
    docker @composeArgs ps -a | Out-File (Join-Path $reportDirectory 'containers.txt')
    docker @composeArgs logs --no-color --tail 100 2>&1 | Out-File (Join-Path $reportDirectory 'services.log')
    throw
}
finally {
    Remove-Item Env:POSTGRES_PASSWORD -ErrorAction SilentlyContinue
}
