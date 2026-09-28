# Regenerate contracts (temp) and compare digests to committed golden.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/compare-golden.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $PSScriptRoot "lib.ps1")

$Python = Resolve-RepoPython -RepoRoot $RepoRoot
Write-Host "Using Python: $Python"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$Req = Join-Path $RepoRoot "requirements-linkml.txt"
& $Python -m pip install -q -r $Req
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location $RepoRoot
try {
    & $Python (Join-Path $RepoRoot "scripts/compare_golden.py")
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
