$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectRoot
New-Item -ItemType Directory -Force -Path "reports/locust" | Out-Null

$env:LOCUST_USE_SHAPE = "0"

uv run locust `
    -f performance/locustfile.py `
    AutomationExerciseAccountUser `
    -H https://automationexercise.com `
    --headless `
    --users 1 `
    --spawn-rate 1 `
    --run-time 30s `
    --csv reports/locust/account_smoke `
    --html reports/locust/account_smoke.html

if ($LASTEXITCODE -ne 0) {
    throw "Locust exited with code $LASTEXITCODE."
}
