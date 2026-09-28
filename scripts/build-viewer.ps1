# Build static Publication Viewer HTML (apps/viewer/dist/index.html).
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-viewer.ps1
# Optional: -Check  (pytest + moex_publication_viewer check)
# Optional: -Open   (open index.html after build)
# Env: VIEWER_PIP_VERBOSE=1  (pass -v to pip install)

param(
    [switch]$Check,
    [switch]$Open
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ViewerDir = Join-Path $RepoRoot "apps/viewer"
$ViewerVenvDir = Join-Path $ViewerDir ".venv"
$ViewerVenv = Join-Path $ViewerVenvDir "Scripts/python.exe"
$OutHtml = Join-Path $ViewerDir "dist/index.html"
$PythonVersionFile = Join-Path $RepoRoot ".python-version"

function Test-PythonAtLeast311 {
    param([Parameter(Mandatory = $true)][string]$Exe)
    & $Exe -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
    return ($LASTEXITCODE -eq 0)
}

function Find-Python311 {
    $preferred = @()
    if (Test-Path $PythonVersionFile) {
        $pin = (Get-Content $PythonVersionFile -Raw).Trim()
        if ($pin -match '^\d+\.\d+') { $preferred += $pin }
    }
    # Prefer CI pin (.python-version), then 3.12/3.11, then newer as fallback.
    foreach ($ver in ($preferred + @("3.12", "3.11", "3.13", "3.14") | Select-Object -Unique)) {
        try {
            $exe = & py "-$ver" -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $exe) {
                $path = $exe.Trim()
                if ((Test-Path $path) -and (Test-PythonAtLeast311 $path)) { return $path }
            }
        } catch { }
    }
    $fallback = Get-Command python -ErrorAction SilentlyContinue
    if ($fallback -and (Test-PythonAtLeast311 $fallback.Source)) {
        return $fallback.Source
    }
    return $null
}

function New-ViewerVenv {
    $hostPython = Find-Python311
    if (-not $hostPython) {
        Write-Error "Python 3.11+ not found (install 3.12 to match .python-version, or create apps/viewer/.venv)"
    }
    Write-Host "Creating apps/viewer/.venv with: $hostPython"
    if (Test-Path $ViewerVenvDir) {
        Remove-Item -Recurse -Force $ViewerVenvDir
    }
    & $hostPython -m venv $ViewerVenvDir
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if (-not (Test-Path $ViewerVenv)) {
        Write-Error "venv created but missing: $ViewerVenv"
    }
}

# Reuse .venv only if it is Python 3.11+; otherwise recreate.
if (Test-Path $ViewerVenv) {
    if (Test-PythonAtLeast311 $ViewerVenv) {
        $Python = $ViewerVenv
    } else {
        Write-Host "Existing apps/viewer/.venv is Python < 3.11; recreating"
        New-ViewerVenv
        $Python = $ViewerVenv
    }
} else {
    New-ViewerVenv
    $Python = $ViewerVenv
}

$pyVer = & $Python -c "import sys; print('{0}.{1}.{2}'.format(*sys.version_info[:3]))"
Write-Host "Using Python: $Python ($pyVer)"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Push-Location $RepoRoot
try {
    Write-Host "pip install -U pip setuptools wheel"
    & $Python -m pip install -U pip setuptools wheel
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    $pipVer = & $Python -m pip --version
    Write-Host "pip: $pipVer"

    Write-Host "pip install -e ./apps/viewer[dev]"
    $pipArgs = @("install", "-e", "${ViewerDir}[dev]")
    if ($env:VIEWER_PIP_VERBOSE -eq "1") {
        $pipArgs += "-v"
    }
    & $Python -m pip @pipArgs
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
