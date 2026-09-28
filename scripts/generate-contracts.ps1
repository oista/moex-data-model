# Generate DAMS Pydantic contracts into generated/contracts/moex-dams/0.1
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/generate-contracts.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $PSScriptRoot "lib.ps1")

$Python = Resolve-RepoPython -RepoRoot $RepoRoot
$env:PYTHONUTF8 = "1"
$Req = Join-Path $RepoRoot "requirements-linkml.txt"
& $Python -m pip install -q -r $Req
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location $RepoRoot
try {
    & $Python (Join-Path $RepoRoot "scripts/generate_contracts.py")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $Python -m pip install -q -e (Join-Path $RepoRoot "generated/contracts/moex-dams/0.1")
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
