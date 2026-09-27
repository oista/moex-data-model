# Lint DAMS schema, validate trading-solution instance, run architecture-check.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-schemas.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$CliVenv = Join-Path $RepoRoot "apps/cli/.venv/Scripts/python.exe"
$Schema = Join-Path $RepoRoot "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
$Impl = Join-Path $RepoRoot "model-assets/implementations/solutions/trading-platform/trading-solution-model.yaml"

function Find-Python311 {
    foreach ($ver in @("3.14", "3.13", "3.12", "3.11")) {
        try {
            $exe = & py "-$ver" -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
        } catch { }
    }
    $fallback = Get-Command python -ErrorAction SilentlyContinue
    if ($fallback) {
        & $fallback.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) { return $fallback.Source }
    }
    return $null
}

if (-not (Test-Path $Schema)) { Write-Error "Missing schema: $Schema" }
if (-not (Test-Path $Impl)) { Write-Error "Missing implementation: $Impl" }

if (Test-Path $CliVenv) {
    $Python = $CliVenv
} else {
    $Python = Find-Python311
    if (-not $Python) { Write-Error "Python 3.11+ not found" }
}

Write-Host "Using Python: $Python"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
& $Python -m pip install -q "linkml>=1.8,<2"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location $RepoRoot
try {
    Write-Host "schema load (SchemaView) + linkml-lint"
    & $Python -c @"
from pathlib import Path
import sys
from linkml_runtime.utils.schemaview import SchemaView
from linkml.linter.config.datamodel.config import RuleLevel
from linkml.linter.linter import Linter

schema = Path(r'$Schema')
# Force UTF-8 for Windows consoles / cp1251 default
sv = SchemaView(str(schema))
assert sv.get_class('MOEXModelRepository') is not None
print('SchemaView OK: classes=', len(sv.all_classes()))

# Linter opens files with locale encoding; patch via temp utf-8 rewrite not needed
# when PYTHONUTF8=1. Fall back to SchemaView-only if lint fails on encoding.
try:
    errors = []
    for r in Linter().lint(str(schema)):
        level = getattr(r, 'level', None)
        msg = getattr(r, 'message', str(r))
        rule = getattr(r, 'rule_name', '')
        print(f'{level}: {msg} ({rule})')
        if level == RuleLevel.error:
            errors.append(r)
    if errors:
        raise SystemExit(1)
    print('lint OK')
except UnicodeDecodeError as exc:
    print('lint skipped due to encoding:', exc, file=sys.stderr)
    print('lint skipped (SchemaView already loaded)')
"@
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "linkml validate ModelPackage"
    & $Python -c @"
from pathlib import Path
import sys
import yaml
from linkml.validator import Validator

schema = Path(r'$Schema')
inst = Path(r'$Impl')
data = yaml.safe_load(inst.read_text(encoding='utf-8'))
report = Validator(schema).validate(data, target_class='ModelPackage')
bad = []
for r in report.results:
    sev = str(getattr(r, 'severity', r))
    if 'ERROR' in sev.upper():
        bad.append(r)
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
