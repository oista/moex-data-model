# Stage 8 ontology extras: pySHACL fixtures + optional linkml-owl smoke.
# Not part of Stage 0 make check.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ontology-check.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $PSScriptRoot "lib.ps1")

$Python = Resolve-RepoPython -RepoRoot $RepoRoot
Write-Host "Using Python: $Python"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$Cli = Join-Path $RepoRoot "apps/cli"
$Req = Join-Path $RepoRoot "requirements-ontology.txt"
& $Python -m pip install -q -e "$Cli[ontology]"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (Test-Path $Req) {
    & $Python -m pip install -q -r $Req
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Push-Location $RepoRoot
try {
    Write-Host "pySHACL instance fixtures"
    & $Python -m pytest packages/specification-dams/tests/test_pyshacl_instances.py -v
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "linkml-owl smoke (export_owl_instances.py)"
    & $Python scripts/export_owl_instances.py --out (Join-Path $RepoRoot "tmp/owl-instances.ttl")
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
