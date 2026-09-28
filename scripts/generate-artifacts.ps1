# Generate DAMS OWL / SHACL / DBML / Mermaid into generated/artifacts/moex-dams/0.1
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/generate-artifacts.ps1

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
    & $Python (Join-Path $RepoRoot "scripts/generate_artifacts.py") @args
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
