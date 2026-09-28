# Install Playwright Chromium (if needed) and run bridge e2e.
$ErrorActionPreference = "Stop"
$WebRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

Push-Location $WebRoot
try {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Error "npm not found - install Node.js 20+"
    }
    $nm = Join-Path $WebRoot "node_modules"
    if (-not (Test-Path $nm)) {
        npm install
    } else {
        npm install --prefer-offline
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    npx playwright install chromium
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    $env:CI = if ($env:CI) { $env:CI } else { "" }
    npm run test:e2e
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
