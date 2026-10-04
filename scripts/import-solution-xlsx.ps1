# Import Object/ObjectAttribute xlsx → DAMS solution YAML (ADR-022).
# Usage (repo root):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/import-solution-xlsx.ps1 `
#     -Xlsx "F:\...\src_soluitions_model.xlsx" -System MDM -Force
#
# Optional: -All  imports MDM,UCD,CRM,ЕСЭД sequentially.

param(
    [Parameter(Mandatory = $false)]
    [string] $Xlsx,

    [Parameter(Mandatory = $false)]
    [string] $System,

    [string] $Profile,
    [string] $Out,
    [string] $ReportDir,
    [switch] $Force,
    [switch] $Strict,
    [switch] $SkipValidate,
    [switch] $SkipAssess,
    [switch] $SkipExport,
    [switch] $All
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$CliVenv = Join-Path $RepoRoot "apps/cli/.venv/Scripts/python.exe"
$PubVenv = Join-Path $RepoRoot "packages/publication/.venv/Scripts/python.exe"
$LinkmlVenv = Join-Path $RepoRoot "packages/standard-linkml/.venv/Scripts/python.exe"

function Find-Python {
    foreach ($candidate in @($CliVenv, $PubVenv, $LinkmlVenv)) {
        if (Test-Path $candidate) { return $candidate }
    }
    foreach ($ver in @("3.14", "3.13", "3.12", "3.11")) {
        try {
            $exe = & py "-$ver" -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
        } catch {}
    }
    throw "Python 3.11+ not found. Run packages/publication/scripts/check.ps1 or apps/cli/scripts/check.ps1 first."
}

$Python = Find-Python
# Ensure local src packages are importable without a full editable install of apps/cli.
$env:PYTHONPATH = @(
    (Join-Path $RepoRoot "apps/cli/src"),
    (Join-Path $RepoRoot "packages/standard-linkml/src"),
    (Join-Path $RepoRoot "packages/specification-dams/src"),
    (Join-Path $RepoRoot "packages/publication/src"),
    (Join-Path $RepoRoot "packages/modeling-kernel/src")
) -join ";"

Push-Location $RepoRoot
try {
    $systems = @()
    if ($All) {
        $systems = @("MDM", "UCD", "CRM", "ЕСЭД")
    } elseif ($System) {
        $systems = @($System)
    } else {
        throw "Specify -System <MDM|UCD|CRM|ЕСЭД> or -All"
    }
    if (-not $Xlsx) {
        throw "Specify -Xlsx path to workbook"
    }

    $exit = 0
    foreach ($sys in $systems) {
        $cliArgs = @(
            "-m", "moex_model_cli",
            "import-solution",
            "--xlsx", $Xlsx,
            "--system", $sys
        )
        if ($Profile) { $cliArgs += @("--profile", $Profile) }
        if ($Out -and -not $All) { $cliArgs += @("--out", $Out) }
        if ($ReportDir -and -not $All) { $cliArgs += @("--report-dir", $ReportDir) }
        if ($Force) { $cliArgs += "--force" }
        if ($Strict) { $cliArgs += "--strict" }
        if ($SkipValidate) { $cliArgs += "--skip-validate" }
        if ($SkipAssess) { $cliArgs += "--skip-assess" }
        if ($SkipExport) { $cliArgs += "--skip-export" }

        Write-Host "=== import-solution $sys ==="
        & $Python @cliArgs
        if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne 3) {
            $exit = $LASTEXITCODE
        } elseif ($LASTEXITCODE -eq 3 -and $exit -eq 0) {
            $exit = 3
        }
    }
    exit $exit
} finally {
    Pop-Location
}
