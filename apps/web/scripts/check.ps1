# Install, test, and build the Workbench web app.
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
    npm test
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    npm run build
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
