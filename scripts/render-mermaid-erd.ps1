# Render Mermaid erDiagram markdown to SVG via @mermaid-js/mermaid-cli@11.
# Usage: .\scripts\render-mermaid-erd.ps1 -InputMd path\to\logical.erd.md [-OutSvg path\to\logical.erd.svg]
param(
    [Parameter(Mandatory = $true)][string]$InputMd,
    [string]$OutSvg = ""
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib.ps1")

$md = Resolve-Path -LiteralPath $InputMd
if (-not $OutSvg) {
    $OutSvg = [System.IO.Path]::ChangeExtension($md.Path, ".svg")
}

$npx = Get-Command npx.cmd -ErrorAction SilentlyContinue
if (-not $npx) { $npx = Get-Command npx -ErrorAction SilentlyContinue }
if (-not $npx) {
    Write-Error "npx not found; install Node.js to render ERD SVG"
    exit 2
}

# Extract fenced mermaid body to a temp .mmd so mmdc writes the exact -o name
# (markdown input produces *-1.svg).
$text = Get-Content -LiteralPath $md.Path -Raw -Encoding UTF8
$mmdPath = [System.IO.Path]::ChangeExtension($OutSvg, ".mmd")
if ($text -match '(?s)```mermaid\s*(.*?)```') {
    Set-Content -LiteralPath $mmdPath -Value $Matches[1].Trim() -Encoding UTF8
} else {
    Copy-Item -LiteralPath $md.Path -Destination $mmdPath -Force
}

try {
    & npx.cmd --yes "@mermaid-js/mermaid-cli@11" `
        -i $mmdPath `
        -o $OutSvg `
        -t neutral `
        -b transparent
    if ($LASTEXITCODE -ne 0) {
        Write-Error "mmdc failed with exit $LASTEXITCODE"
        exit $LASTEXITCODE
    }
} finally {
    if (Test-Path -LiteralPath $mmdPath) { Remove-Item -LiteralPath $mmdPath -Force }
}
Write-Host "wrote $OutSvg"
exit 0
