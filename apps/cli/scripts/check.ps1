# Bootstrap venv, run vertical-slice + CLI tests, export preview JSON via moex-model.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File apps/cli/scripts/check.ps1

$ErrorActionPreference = "Stop"
$CliRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $CliRoot "../..")
. (Join-Path $RepoRoot "scripts/lib.ps1")

Push-Location $RepoRoot
try {
    $VenvPython = Resolve-VenvPython (Join-Path $CliRoot ".venv")
    if (-not $VenvPython) {
        $base = Find-Python311
        if (-not $base) {
            Write-Error "Python 3.11+ not found. Install Python 3.11+ or ensure 'py -3.14' / python3 works."
        }
        Write-Host "Creating venv with $base"
        & $base -m venv (Join-Path $CliRoot ".venv")
        $VenvPython = Resolve-VenvPython (Join-Path $CliRoot ".venv")
        if (-not $VenvPython) {
            Write-Error "venv created but python executable not found under apps/cli/.venv"
        }
    }

    $Kernel = Join-Path $RepoRoot "packages/modeling-kernel"
    $Linkml = Join-Path $RepoRoot "packages/standard-linkml"
    $Dams = Join-Path $RepoRoot "packages/specification-dams"
    $Pub = Join-Path $RepoRoot "packages/publication"
    $Git = Join-Path $RepoRoot "packages/git-adapter"

    $Contracts = Join-Path $RepoRoot "generated/contracts/moex-dams/0.1"
    Write-Host "Ensuring DAMS contracts package (Python: $VenvPython)"
    & $VenvPython -m pip install -U pip -q
    & $VenvPython -m pip install -q -r (Join-Path $RepoRoot "requirements-linkml.txt")
    & $VenvPython (Join-Path $RepoRoot "scripts/generate_contracts.py")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "Installing slice packages + moex-model-cli into .venv"
    & $VenvPython -m pip install `
        -e "$Contracts" `
        -e "$Kernel" `
        -e "$Linkml" `
        -e "$Dams" `
        -e "$Pub" `
        -e "$Git" `
        -e "$CliRoot[dev]" -q

    Write-Host "Running pytest (kernel, provider, dams, publication, git, cli, architecture)"
    & $VenvPython -m pytest `
        (Join-Path $Kernel "tests") `
        (Join-Path $Linkml "tests/test_provider.py") `
        (Join-Path $Dams "tests") `
        (Join-Path $Pub "tests") `
        (Join-Path $Git "tests") `
        (Join-Path $CliRoot "tests") `
        (Join-Path $RepoRoot "tests/architecture") `
        -q
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    $OutJson = Join-Path $RepoRoot "model-assets/implementations/solutions/trading-platform/publications/vertical_slice.json"
    Write-Host "Publishing slice projection via moex-model → $OutJson"
    & $VenvPython -m moex_model_cli publish `
        --root $RepoRoot `
        --implementation-id "moex:implementation:trading:1.0.0" `
        --out $OutJson
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
