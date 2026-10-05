# Bootstrap venv and run vertical-slice package tests + export preview JSON.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File packages/publication/scripts/check.ps1

$ErrorActionPreference = "Stop"
$PackageRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $PackageRoot "../..")
$VenvPython = Join-Path $PackageRoot ".venv/Scripts/python.exe"

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
        & $base -m venv (Join-Path $PackageRoot ".venv")
    }

    $Kernel = Join-Path $RepoRoot "packages/modeling-kernel"
    $Linkml = Join-Path $RepoRoot "packages/standard-linkml"
    $Dams = Join-Path $RepoRoot "packages/specification-dams"

    $Contracts = Join-Path $RepoRoot "generated/contracts/moex-dams/0.1"
    Write-Host "Ensuring DAMS contracts package"
    & $VenvPython -m pip install -U pip -q
    & $VenvPython -m pip install -q "linkml>=1.8,<2"
    & $VenvPython (Join-Path $RepoRoot "scripts/generate_contracts.py")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "Installing vertical-slice packages into .venv"
    & $VenvPython -m pip install `
        -e "$Contracts" `
        -e "$Kernel" `
        -e "$Linkml" `
        -e "$Dams" `
        -e "$PackageRoot[dev]" -q

    Write-Host "Running pytest (kernel, linkml provider, dams, publication, architecture)"
    & $VenvPython -m pytest `
        (Join-Path $Kernel "tests") `
        (Join-Path $Linkml "tests/test_provider.py") `
        (Join-Path $Dams "tests") `
        (Join-Path $PackageRoot "tests") `
        (Join-Path $RepoRoot "tests/architecture") `
        -q
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    $OutJson = Join-Path $RepoRoot "model-assets/implementations/solutions/mdm/publications/vertical_slice.json"
    Write-Host "Exporting slice projection → $OutJson"
    & $VenvPython -m moex_publication.cli export-slice `
        --schema (Join-Path $RepoRoot "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml") `
        --implementation (Join-Path $RepoRoot "model-assets/implementations/solutions/mdm/mdm-solution-model.yaml") `
        --implementation-id "moex:implementation:mdm:0.1.0" `
        --out $OutJson
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
