# Install API deps and run FastAPI smoke tests (SQLite).
$ErrorActionPreference = "Stop"
$ApiRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $ApiRoot "../..")
$VenvPython = Join-Path $ApiRoot ".venv/Scripts/python.exe"

function Find-Python311 {
    foreach ($ver in @("3.14", "3.13", "3.12", "3.11")) {
        try {
            $exe = & py "-$ver" -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
        } catch { }
    }
    return $null
}

Push-Location $RepoRoot
try {
    if (-not (Test-Path $VenvPython)) {
        $base = Find-Python311
        if (-not $base) { Write-Error "Python 3.11+ not found" }
        & $base -m venv (Join-Path $ApiRoot ".venv")
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
        -e (Join-Path $RepoRoot "apps/cli") `
        -e "$ApiRoot[dev]" -q
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $VenvPython -m pytest (Join-Path $ApiRoot "tests") -q
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
