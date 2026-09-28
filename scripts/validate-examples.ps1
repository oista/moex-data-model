# Validate DAMS example YAML instances against moex-dams.yaml.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-examples.ps1
#
# registries.yaml is a bare YAML list of registry entries (not a single LinkML
# instance root) — skipped until wrapped as a ModelPackage / registry document.

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $PSScriptRoot "lib.ps1")
$Schema = Join-Path $RepoRoot "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
$ExamplesDir = Join-Path $RepoRoot "model-assets/specifications/moex-dams/0.1/examples"

if (-not (Test-Path $Schema)) { Write-Error "Missing schema: $Schema" }
if (-not (Test-Path $ExamplesDir)) { Write-Error "Missing examples: $ExamplesDir" }

$Python = Resolve-RepoPython -RepoRoot $RepoRoot
Write-Host "Using Python: $Python"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$Req = Join-Path $RepoRoot "requirements-linkml.txt"
& $Python -m pip install -q -r $Req
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location $RepoRoot
try {
    Write-Host "validate-examples"
    & $Python -c @"
from pathlib import Path
import sys
import yaml
from linkml.validator import Validator

repo = Path(r'$RepoRoot')
schema = Path(r'$Schema')
examples = Path(r'$ExamplesDir')

# Bare list document — not a LinkML instance root (see script header).
SKIP = {
    'registries.yaml': 'bare YAML list of registry entries, not a single class instance',
}

TARGETS = {
    'client-contract-binding.yaml': 'DataModelBinding',
    'client-data-flow.yaml': 'DataFlow',
}

validator = Validator(schema)
failed = 0
for path in sorted(examples.glob('*.yaml')):
    name = path.name
    if name in SKIP:
        print(f'skip {name}: {SKIP[name]}')
        continue
    target = TARGETS.get(name)
    if not target:
        print(f'error: no target_class mapping for {name}', file=sys.stderr)
        failed += 1
        continue
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    report = validator.validate(data, target_class=target)
    bad = []
    for r in report.results:
        sev = str(getattr(r, 'severity', r))
        if 'ERROR' in sev.upper():
            bad.append(r)
    if bad:
        failed += 1
        print(f'FAIL {name} target={target}', file=sys.stderr)
        for e in bad[:20]:
            print(e, file=sys.stderr)
    else:
        print(f'OK {name} target={target}')

if failed:
    raise SystemExit(1)
print('validate-examples OK')
"@
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
