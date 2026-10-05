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

$Contracts = Join-Path $RepoRoot "generated/contracts/moex-dams/0.1"
$Kernel = Join-Path $RepoRoot "packages/modeling-kernel"
$Linkml = Join-Path $RepoRoot "packages/standard-linkml"
$Dams = Join-Path $RepoRoot "packages/specification-dams"
$Pub = Join-Path $RepoRoot "packages/publication"
$Git = Join-Path $RepoRoot "packages/git-adapter"
$Sem = Join-Path $RepoRoot "packages/semantic-mappings"
$Tooling = Join-Path $RepoRoot "packages/linkml-tooling"
$ExtSrc = Join-Path $RepoRoot "packages/external-sources"
$Cli = Join-Path $RepoRoot "apps/cli"
$Req = Join-Path $RepoRoot "requirements-ontology.txt"

# Workspace packages are not on PyPI; install them in the same pip invocation as CLI.
Write-Host "Installing workspace packages + moex-model-cli[ontology]"
& $Python -m pip install -q `
    -e "$Contracts" `
    -e "$Kernel" `
    -e "$Linkml" `
    -e "$Dams" `
    -e "$Pub" `
    -e "$Git" `
    -e "$Sem" `
    -e "$Tooling" `
    -e "$ExtSrc" `
    -e "$Cli[ontology]"
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
