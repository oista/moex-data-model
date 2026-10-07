# Validate DAMS example YAML instances against moex-dams.yaml.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-examples.ps1
#
# registries.yaml is a bare YAML list of registry entries (not a single LinkML
# instance root) — skipped until wrapped as a ModelPackage / registry document.
#
# PR-C2: examples/invariants/manifest.yaml — valid fixtures must pass; invalid
# must fail (negative mode) via make_linkml_validator.

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $PSScriptRoot "lib.ps1")
$Schema = Join-Path $RepoRoot "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
$ExamplesDir = Join-Path $RepoRoot "model-assets/specifications/moex-dams/0.1/examples"
$InvManifest = Join-Path $ExamplesDir "invariants/manifest.yaml"

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
from moex_standard_linkml.validation import error_results, make_linkml_validator

repo = Path(r'$RepoRoot')
schema = Path(r'$Schema')
examples = Path(r'$ExamplesDir')
inv_manifest = Path(r'$InvManifest')

# Bare list document — not a LinkML instance root (see script header).
SKIP = {
    'registries.yaml': 'bare YAML list of registry entries, not a single class instance',
}

TARGETS = {
    'client-contract-binding.yaml': 'DataModelBinding',
    'client-data-flow.yaml': 'DataFlow',
}

validator = make_linkml_validator(schema)
failed = 0

# --- positive: top-level examples ---
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
    bad = error_results(validator.validate(data, target_class=target))
    if bad:
        failed += 1
        print(f'FAIL {name} target={target}', file=sys.stderr)
        for e in bad[:20]:
            print(e, file=sys.stderr)
    else:
        print(f'OK {name} target={target}')

# --- L1 invariants: valid must pass, invalid must fail (PR-C2) ---
if inv_manifest.is_file():
    man = yaml.safe_load(inv_manifest.read_text(encoding='utf-8')) or {}
    inv_dir = inv_manifest.parent
    for case in man.get('cases') or []:
        iid = case['id']
        target = case['target_class']
        valid_path = inv_dir / case['valid']
        invalid_path = inv_dir / case['invalid']
        if not valid_path.is_file() or not invalid_path.is_file():
            failed += 1
            print(f'FAIL {iid}: missing fixture file', file=sys.stderr)
            continue
        vdata = yaml.safe_load(valid_path.read_text(encoding='utf-8'))
        idata = yaml.safe_load(invalid_path.read_text(encoding='utf-8'))
        vbad = error_results(validator.validate(vdata, target_class=target))
        ibad = error_results(validator.validate(idata, target_class=target))
        if vbad:
            failed += 1
            print(f'FAIL {iid} valid must pass target={target}', file=sys.stderr)
            for e in vbad[:10]:
                print(e, file=sys.stderr)
        else:
            print(f'OK {iid} valid target={target}')
        if not ibad:
            failed += 1
            print(f'FAIL {iid} invalid must be rejected target={target}', file=sys.stderr)
        else:
            print(f'OK {iid} invalid rejected target={target} ({len(ibad)} errors)')
else:
    print('skip invariants: no manifest.yaml')

if failed:
    raise SystemExit(1)
print('validate-examples OK')
"@
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
