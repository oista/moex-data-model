# Thin wrapper around scripts/check_all.py (Windows / pwsh).
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_all.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_all.ps1 -- --only compare-golden

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $PSScriptRoot "lib.ps1")

$Python = Resolve-RepoPython -RepoRoot $RepoRoot
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Push-Location $RepoRoot
try {
    & $Python (Join-Path $RepoRoot "scripts/check_all.py") @args
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
