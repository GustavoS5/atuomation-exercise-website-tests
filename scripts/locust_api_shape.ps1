$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectRoot
New-Item -ItemType Directory -Force -Path "reports/locust" | Out-Null

$env:LOCUST_USE_SHAPE = "1"

uv run locust `
    -f performance/locustfile.py `
    AutomationExerciseApiUser `
    -H https://automationexercise.com `
    --headless `
    --csv reports/locust/api_shape `
    --html reports/locust/api_shape.html

if ($LASTEXITCODE -ne 0) {
    throw "Locust exited with code $LASTEXITCODE."
}
