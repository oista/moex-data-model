# Validate DAMS RequirementCatalog instances (LinkML + semantic gate).
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-requirements.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $PSScriptRoot "lib.ps1")
$Schema = Join-Path $RepoRoot "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
$Catalog = Join-Path $RepoRoot "model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml"

if (-not (Test-Path $Schema)) { Write-Error "Missing schema: $Schema" }
if (-not (Test-Path $Catalog)) { Write-Error "Missing catalog: $Catalog" }

$Python = Resolve-RepoPython -RepoRoot $RepoRoot
Write-Host "Using Python: $Python"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$Req = Join-Path $RepoRoot "requirements-linkml.txt"
& $Python -m pip install -q -r $Req
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m pip install -q -e (Join-Path $RepoRoot "packages/modeling-kernel") -e (Join-Path $RepoRoot "packages/specification-dams")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location $RepoRoot
try {
    Write-Host "validate-requirements LinkML RequirementCatalog"
    & $Python -c @"
from pathlib import Path
import sys
import yaml
from linkml.validator import Validator

schema = Path(r'$Schema')
catalog = Path(r'$Catalog')
data = yaml.safe_load(catalog.read_text(encoding='utf-8'))
report = Validator(schema).validate(data, target_class='RequirementCatalog')
bad = []
for r in report.results:
    sev = str(getattr(r, 'severity', r))
    if 'ERROR' in sev.upper():
        bad.append(r)
if bad:
    for e in bad[:40]:
        print(e, file=sys.stderr)
    raise SystemExit(1)
print('LinkML RequirementCatalog OK')
"@
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "validate-requirements semantic gate"
    & $Python -m moex_dams.rules.catalog_validate $Catalog
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
