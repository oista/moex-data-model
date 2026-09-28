# Shared helpers for Stage 0 PowerShell scripts (Windows + Linux CI).
# Dot-source: . (Join-Path $PSScriptRoot "lib.ps1")  when in scripts/
# Or: . (Join-Path $RepoRoot "scripts/lib.ps1")

function Find-Python311 {
    foreach ($ver in @("3.14", "3.13", "3.12", "3.11")) {
        try {
            $exe = & py "-$ver" -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
        } catch { }
    }
    $fallback = Get-Command python3 -ErrorAction SilentlyContinue
    if (-not $fallback) {
        $fallback = Get-Command python -ErrorAction SilentlyContinue
    }
    if ($fallback) {
        & $fallback.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) { return $fallback.Source }
    }
    return $null
}

function Resolve-VenvPython {
    param(
        [Parameter(Mandatory = $true)][string]$VenvDir
    )
    $candidates = @(
        (Join-Path $VenvDir "Scripts/python.exe"),
        (Join-Path $VenvDir "bin/python"),
        (Join-Path $VenvDir "bin/python3")
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

function Resolve-RepoPython {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [string]$PreferredVenvRel = "apps/cli/.venv"
    )
    $venvPy = Resolve-VenvPython (Join-Path $RepoRoot $PreferredVenvRel)
    if ($venvPy) { return $venvPy }
    $found = Find-Python311
    if (-not $found) {
        Write-Error "Python 3.11+ not found (no venv at $PreferredVenvRel and no py/python3)"
    }
    return $found
}
