# Build DAMS release bundle index (+ staged directory).
$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$env:PYTHONUTF8 = "1"

Push-Location $RepoRoot
try {
    $python = "python"
    if (Test-Path "apps/cli/.venv/Scripts/python.exe") {
        $python = "apps/cli/.venv/Scripts/python.exe"
    }
    & $python -m pip install -q -r requirements-linkml.txt
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $python scripts/build_release_bundle.py @args
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
