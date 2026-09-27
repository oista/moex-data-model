# Build static Publication Viewer HTML (apps/viewer/dist/index.html).
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-viewer.ps1
# Optional: -Check  (pytest + moex_publication_viewer check)
# Optional: -Open   (open index.html after build)

param(
    [switch]$Check,
    [switch]$Open
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ViewerDir = Join-Path $RepoRoot "apps/viewer"
$ViewerVenv = Join-Path $ViewerDir ".venv/Scripts/python.exe"
$OutHtml = Join-Path $ViewerDir "dist/index.html"

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

if (Test-Path $ViewerVenv) {
    $Python = $ViewerVenv
} else {
    $Python = Find-Python311
    if (-not $Python) { Write-Error "Python 3.11+ not found (install or create apps/viewer/.venv)" }
}

Write-Host "Using Python: $Python"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Push-Location $RepoRoot
try {
    Write-Host "pip install -e ./apps/viewer[dev]"
    & $Python -m pip install -q -e "${ViewerDir}[dev]"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    if ($Check) {
        Write-Host "pytest apps/viewer/tests"
        & $Python -m pytest (Join-Path $ViewerDir "tests") -q
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        Write-Host "moex_publication_viewer check"
        & $Python -m moex_publication_viewer.cli check --root .
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }

    Write-Host "moex_publication_viewer build"
    & $Python -m moex_publication_viewer.cli build --root .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    if (-not (Test-Path $OutHtml)) {
        Write-Error "Build finished but missing output: $OutHtml"
    }
    Write-Host "OK: $OutHtml"

    if ($Open) {
        Start-Process $OutHtml
    }
} finally {
    Pop-Location
}
