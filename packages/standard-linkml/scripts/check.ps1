# Bootstrap package .venv (Python 3.11+) and run ingest tests.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File packages/standard-linkml/scripts/check.ps1
# Or from package dir:
#   powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/check.ps1

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
        $ok = & $fallback.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
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

    Write-Host "Installing moex-modeling-kernel + moex-standard-linkml[dev] into .venv"
    & $VenvPython -m pip install -U pip -q
    $KernelRoot = Join-Path $RepoRoot "packages/modeling-kernel"
    & $VenvPython -m pip install -e "$KernelRoot" -e "$PackageRoot[dev]" -q

    Write-Host "Running pytest"
    & $VenvPython -m pytest (Join-Path $PackageRoot "tests") -q
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
