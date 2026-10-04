# Build static Publication Viewer HTML (apps/viewer/dist/index.html).
# Usage from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-viewer.ps1
# Optional: -Check     (pytest + moex_publication_viewer check)
# Optional: -Open      (open index.html after build)
# Optional: -SkipPip   (skip pip; use existing apps/viewer/.venv)
# Optional: -ForcePip  (always run pip even if deps already import)
# Env: VIEWER_PIP_VERBOSE=1  (pass -v to pip install)
# Env: VIEWER_SKIP_PIP=1 / VIEWER_FORCE_PIP=1  (same as switches)

param(
    [switch]$Check,
    [switch]$Open,
    [switch]$SkipPip,
    [switch]$ForcePip
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

function Test-ViewerDepsImportable {
    param([Parameter(Mandatory = $true)][string]$Exe)
    & $Exe -c "import moex_publication_viewer, jinja2, yaml, markdown, click, pytest" 2>$null
    return ($LASTEXITCODE -eq 0)
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

$doSkipPip = $SkipPip -or ($env:VIEWER_SKIP_PIP -eq "1")
$doForcePip = $ForcePip -or ($env:VIEWER_FORCE_PIP -eq "1")
$depsOk = Test-ViewerDepsImportable $Python

Push-Location $RepoRoot
try {
    $env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
    if (-not $env:PIP_DEFAULT_TIMEOUT) { $env:PIP_DEFAULT_TIMEOUT = "15" }

    if ($doSkipPip) {
        if (-not $depsOk) {
            Write-Error "SkipPip set but viewer deps are not importable in $Python"
        }
        Write-Host "Skipping pip (SkipPip / VIEWER_SKIP_PIP); using existing venv"
    } elseif ($depsOk -and -not $doForcePip) {
        # Refresh editable link without contacting PyPI for dependencies.
        Write-Host "deps present; pip install -e ./apps/viewer --no-deps (offline-friendly)"
        & $Python -m pip install -e $ViewerDir --no-deps --disable-pip-version-check
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARNING: offline editable refresh failed; continuing with existing install"
        }
    } else {
        Write-Host "pip install -U pip setuptools wheel"
        & $Python -m pip install -U pip setuptools wheel --disable-pip-version-check
        if ($LASTEXITCODE -ne 0) {
            if (Test-ViewerDepsImportable $Python) {
                Write-Host "WARNING: pip bootstrap failed (network?); continuing with existing packages"
            } else {
                exit $LASTEXITCODE
            }
        }

        $pipVer = & $Python -m pip --version
        Write-Host "pip: $pipVer"

        Write-Host "pip install -e ./apps/viewer[dev]"
        $pipArgs = @("install", "-e", "${ViewerDir}[dev]", "--disable-pip-version-check")
        if ($env:VIEWER_PIP_VERBOSE -eq "1") {
            $pipArgs += "-v"
        }
        & $Python -m pip @pipArgs
        if ($LASTEXITCODE -ne 0) {
            if (Test-ViewerDepsImportable $Python) {
                Write-Host "WARNING: pip install failed (network?); continuing with existing packages"
            } else {
                exit $LASTEXITCODE
            }
        }
    }

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
