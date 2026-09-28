# Regenerate contracts (temp) and compare digests to committed golden.
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/compare-golden.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$CliVenv = Join-Path $RepoRoot "apps/cli/.venv/Scripts/python.exe"

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

if (Test-Path $CliVenv) { $Python = $CliVenv }
else {
    $Python = Find-Python311
    if (-not $Python) { Write-Error "Python 3.11+ not found" }
}

Write-Host "Using Python: $Python"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$Req = Join-Path $RepoRoot "requirements-linkml.txt"
& $Python -m pip install -q -r $Req
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location $RepoRoot
try {
    & $Python (Join-Path $RepoRoot "scripts/compare_golden.py")
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
