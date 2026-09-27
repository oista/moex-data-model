# Bootstrap venv, run vertical-slice + CLI tests, export preview JSON via moex-model.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File apps/cli/scripts/check.ps1

$ErrorActionPreference = "Stop"
$CliRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $CliRoot "../..")
$VenvPython = Join-Path $CliRoot ".venv/Scripts/python.exe"

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

Push-Location $RepoRoot
try {
    if (-not (Test-Path $VenvPython)) {
        $base = Find-Python311
        if (-not $base) {
            Write-Error "Python 3.11+ not found. Install Python 3.11+ or ensure 'py -3.14' works."
        }
        Write-Host "Creating venv with $base"
        & $base -m venv (Join-Path $CliRoot ".venv")
    }

    $Kernel = Join-Path $RepoRoot "packages/modeling-kernel"
    $Linkml = Join-Path $RepoRoot "packages/standard-linkml"
    $Dams = Join-Path $RepoRoot "packages/specification-dams"
    $Pub = Join-Path $RepoRoot "packages/publication"
    $Git = Join-Path $RepoRoot "packages/git-adapter"

    $Contracts = Join-Path $RepoRoot "generated/contracts/moex-dams/0.1"
    Write-Host "Ensuring DAMS contracts package"
    & $VenvPython -m pip install -U pip -q
    & $VenvPython -m pip install -q "linkml>=1.8,<2"
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
