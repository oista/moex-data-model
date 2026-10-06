# Lint DAMS schema, validate MDM solution instance, run architecture-check.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-schemas.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $PSScriptRoot "lib.ps1")
$Schema = Join-Path $RepoRoot "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
$Impl = Join-Path $RepoRoot "model-assets/implementations/solutions/mdm/mdm-solution-model.yaml"

if (-not (Test-Path $Schema)) { Write-Error "Missing schema: $Schema" }
if (-not (Test-Path $Impl)) { Write-Error "Missing implementation: $Impl" }

$Python = Resolve-RepoPython -RepoRoot $RepoRoot
Write-Host "Using Python: $Python"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$Req = Join-Path $RepoRoot "requirements-linkml.txt"
& $Python -m pip install -q -r $Req
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location $RepoRoot
try {
    Write-Host "schema load (SchemaView) + linkml-lint (.linkmllint.yaml)"
    & $Python -c @"
from pathlib import Path
import sys
import yaml
from linkml_runtime.utils.schemaview import SchemaView
from linkml.linter.config.datamodel.config import RuleLevel
from linkml.linter.linter import Linter

schema = Path(r'$Schema')
config_path = Path(r'$RepoRoot') / '.linkmllint.yaml'
sv = SchemaView(str(schema))
assert sv.get_class('MOEXModelRepository') is not None
print('SchemaView OK: classes=', len(sv.all_classes()))

config: dict = {}
if config_path.is_file():
    config = yaml.safe_load(config_path.read_text(encoding='utf-8')) or {}
    print('lint config:', config_path.as_posix())

errors = []
for r in Linter(config).lint(str(schema)):
    level = getattr(r, 'level', None)
    msg = getattr(r, 'message', str(r))
    rule = getattr(r, 'rule_name', '')
    print(f'{level}: {msg} ({rule})')
    if level == RuleLevel.error:
        errors.append(r)
if errors:
    raise SystemExit(1)
print('lint OK')
"@
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "DAMS ontology URI lint (MOEX-ONT-*)"
    $DamsSrc = (Join-Path $RepoRoot "packages/specification-dams/src") -replace '\\','/'
    $KernelSrc = (Join-Path $RepoRoot "packages/modeling-kernel/src") -replace '\\','/'
    $LinkmlSrc = (Join-Path $RepoRoot "packages/standard-linkml/src") -replace '\\','/'
    $ContractsSrc = (Join-Path $RepoRoot "generated/contracts/moex-dams/0.1") -replace '\\','/'
    $SchemaPosix = $Schema -replace '\\','/'
    & $Python -c @"
import sys
sys.path[:0] = [
    r'$DamsSrc',
    r'$KernelSrc',
    r'$LinkmlSrc',
    r'$ContractsSrc',
]
from pathlib import Path
from moex_dams.rules.ontology_uris import check_ontology_uris
diags = check_ontology_uris(Path(r'$SchemaPosix'))
for d in diags:
    print(f'{d.severity.value}\t{d.diagnostic_code}\t{d.diagnostic_message}')
if diags:
    raise SystemExit(1)
print('ontology URI lint OK')
"@
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "linkml validate ModelPackage"
    & $Python -c @"
from pathlib import Path
import sys
import yaml
from moex_standard_linkml.validation import error_results, make_linkml_validator

schema = Path(r'$Schema')
inst = Path(r'$Impl')
data = yaml.safe_load(inst.read_text(encoding='utf-8'))
bad = error_results(
    make_linkml_validator(schema).validate(data, target_class='ModelPackage')
)
if bad:
    for e in bad[:30]:
        print(e, file=sys.stderr)
    raise SystemExit(1)
print('validate OK')
"@
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "architecture-check"
    & $Python -m pip install -q -e (Join-Path $RepoRoot "tools/architecture-check[dev]")
    & $Python -m architecture_check.cli --root $RepoRoot
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
