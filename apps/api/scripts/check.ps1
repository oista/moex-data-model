# Install API deps and run FastAPI smoke tests (SQLite).
$ErrorActionPreference = "Stop"
$ApiRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $ApiRoot "../..")
. (Join-Path $RepoRoot "scripts/lib.ps1")

Push-Location $RepoRoot
try {
    $VenvPython = Resolve-VenvPython (Join-Path $ApiRoot ".venv")
    if (-not $VenvPython) {
        $base = Find-Python311
        if (-not $base) { Write-Error "Python 3.11+ not found" }
        & $base -m venv (Join-Path $ApiRoot ".venv")
        $VenvPython = Resolve-VenvPython (Join-Path $ApiRoot ".venv")
        if (-not $VenvPython) {
            Write-Error "venv created but python executable not found under apps/api/.venv"
        }
    }
    $env:PYTHONUTF8 = "1"
    & $VenvPython -m pip install -U pip -q
    & $VenvPython -m pip install -q "linkml>=1.8,<2"
    & $VenvPython (Join-Path $RepoRoot "scripts/generate_contracts.py")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $VenvPython -m pip install `
        -e (Join-Path $RepoRoot "generated/contracts/moex-dams/0.1") `
        -e (Join-Path $RepoRoot "packages/modeling-kernel") `
        -e (Join-Path $RepoRoot "packages/standard-linkml") `
        -e (Join-Path $RepoRoot "packages/specification-dams") `
        -e (Join-Path $RepoRoot "packages/publication") `
        -e (Join-Path $RepoRoot "packages/git-adapter") `
        -e (Join-Path $RepoRoot "packages/semantic-mappings") `
        -e (Join-Path $RepoRoot "packages/drawdb-adapter") `
        -e (Join-Path $RepoRoot "packages/linkml-tooling") `
        -e (Join-Path $RepoRoot "apps/cli") `
        -e "$ApiRoot[dev]" -q
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $VenvPython -m pytest (Join-Path $ApiRoot "tests") -q
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
