# Fetch pinned drawdb-io/drawdb into apps/drawdb/upstream (gitignored).
$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ShaFile = Join-Path $Root "UPSTREAM_SHA"
$Sha = (Get-Content $ShaFile -Raw).Trim()
if (-not $Sha) { Write-Error "UPSTREAM_SHA empty" }
$Dest = Join-Path $Root "upstream"
if (Test-Path $Dest) {
    Remove-Item -Recurse -Force $Dest
}
Write-Host "Cloning drawdb-io/drawdb @$Sha → $Dest"
git clone --depth 1 https://github.com/drawdb-io/drawdb.git $Dest
Push-Location $Dest
try {
    git fetch --depth 1 origin $Sha
    git checkout $Sha
} finally {
    Pop-Location
}
Write-Host "Done. Build image: docker build -t moex-drawdb $Root"
