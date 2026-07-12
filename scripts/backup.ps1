param([string]$Output = ".\backups")
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
docker compose exec -T postgres pg_dump -U rentscout -d rentscout -Fc > (Join-Path $Output "rentwise-$stamp.dump")
Write-Host "Backup created: rentwise-$stamp.dump"
