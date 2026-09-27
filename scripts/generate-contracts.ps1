# Generate DAMS Pydantic contracts into generated/contracts/moex-dams/0.1
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/generate-contracts.ps1

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
    return $null
}

if (Test-Path $CliVenv) { $Python = $CliVenv }
else {
    $Python = Find-Python311
    if (-not $Python) { Write-Error "Python 3.11+ not found" }
}

$env:PYTHONUTF8 = "1"
& $Python -m pip install -q "linkml>=1.8,<2"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location $RepoRoot
try {
    & $Python (Join-Path $RepoRoot "scripts/generate_contracts.py")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $Python -m pip install -q -e (Join-Path $RepoRoot "generated/contracts/moex-dams/0.1")
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
