<#
.SYNOPSIS
  Build application images (Full tar.gz) or an Overlay zip for air-gap transfer.

.DESCRIPTION
  Full (default):
    1. docker compose build model-api + model-web
    2. Tag moex-data-model-api:<version> and moex-data-model-web:<version>
    3. Smoke imports and the web root
    4. docker save | gzip -> reports/docker/
    5. Config bundle zip (compose + .env.example, no secrets)
    6. .sha256 + manifest.json (mode=full, deps_fingerprint)

  Overlay:
    1. Validate -ParentTag against moex-model-<ParentTag>.manifest.json (mode=full)
    2. Gate on deps_fingerprint
    3. Build apps/web via node:20-alpine
    4. Stage a zip context with scripts/airgap_overlay.py
    5. Zip + sha256 + manifest (mode=overlay)

  Contour (-Contour):
    1. Require a clean git tree (own version bump is allowed)
    2. Bump the patch in pyproject.toml
    3. Overlay when the fingerprint matches the parent Full; otherwise Full
    4. Assemble moex-model-<tag>-contour.zip

.EXAMPLE
  .\scripts\pack-docker-images.ps1
  .\scripts\pack-docker-images.ps1 -Mode Overlay -ParentTag 0.1.0
  .\scripts\pack-docker-images.ps1 -Contour -ParentTag 0.1.0
#>
[CmdletBinding()]
param(
    [ValidateSet('Full', 'Overlay')]
    [string]$Mode = 'Full',
    [string]$ParentTag = "",
    [string]$ParentManifest = "",
    [string]$OutDir = "",
    [switch]$SkipBuild,
    [switch]$SkipConfigBundle,
    [switch]$NoGzip,
    [switch]$Contour,
    [switch]$NoCache,
    [int]$KeepLast = 3
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

$ImageApi = "moex-data-model-api"
$ImageWeb = "moex-data-model-web"
$Prefix = "moex-model"

function Get-AppVersion {
    $pyproject = Join-Path $RepoRoot "pyproject.toml"
    $text = Get-Content $pyproject -Raw
    if ($text -match '(?m)^version\s*=\s*"([^"]+)"') { return $Matches[1] }
    throw "Cannot parse version from pyproject.toml"
}

function Get-GitSha {
    try {
        $sha = (& git rev-parse --short HEAD 2>$null)
        if ($LASTEXITCODE -eq 0 -and $sha) { return $sha.Trim() }
    } catch {}
    return "unknown"
}

function Ensure-Dir([string]$Path) {
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Invoke-Python {
    param([string[]]$PythonArgs)
    # Keep python's stdout off this function's pipeline. Otherwise a printed
    # path is returned together with the real result and the contour zip
    # stores that file twice.
    $output = & python @PythonArgs
    if ($LASTEXITCODE -ne 0) { throw "python $($PythonArgs -join ' ') failed" }
    if ($output) { $output | Out-Host }
}

function Get-DepsFingerprint {
    $out = & python scripts/airgap_overlay.py fingerprint
    if ($LASTEXITCODE -ne 0) { throw "deps_fingerprint failed" }
    return ($out | Select-Object -Last 1).ToString().Trim()
}

function Invoke-ComposeBuild {
    param(
        [string[]]$Services,
        [switch]$ForceNoCache
    )
    Write-Host "DEPS_FINGERPRINT=$($env:DEPS_FINGERPRINT)"
    Write-Host "MOEX_VERSION=$($env:MOEX_VERSION)"
    Write-Host "GIT_SHA=$($env:GIT_SHA)"
    Write-Host "MODEL_TAG=$($env:MODEL_TAG)"

    $composeArgs = @("compose", "-f", "docker-compose.yml", "build")
    if ($ForceNoCache -or $NoCache) {
        $composeArgs += "--no-cache"
    }
    $composeArgs += $Services
    Write-Host "docker $($composeArgs -join ' ')"
    & docker @composeArgs
    if ($LASTEXITCODE -ne 0) { throw "docker compose build failed" }
}

function Test-LocalTagNeedsNoCache {
    param([string]$ImageRef, [string]$ExpectedSha)
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $inspect = & docker image inspect $ImageRef --format '{{index .Config.Labels "moexmodel.git_sha"}}' 2>$null
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prevEap
    if ($code -ne 0) { return $false }
    $label = if ($inspect) { $inspect.ToString().Trim() } else { "" }
    if (-not $label) { return $true }
    $short = $ExpectedSha.Substring(0, [Math]::Min(7, $ExpectedSha.Length))
    $labelShort = $label.Substring(0, [Math]::Min(7, $label.Length))
    return ($labelShort -ne $short)
}

function New-ContourDropZip {
    param(
        [string]$Dir,
        [string]$Tag,
        [string]$DropMode,
        [string]$ParentTagValue,
        [string[]]$MemberPaths
    )
    $applyPath = Join-Path $env:TEMP "moex-APPLY-$Tag.md"
    $writeArgs = @(
        "scripts/airgap_overlay.py", "write-apply-md",
        "--mode", $DropMode,
        "--tag", $Tag,
        "--out", $applyPath
    )
    if ($ParentTagValue) {
        $writeArgs += @("--parent-tag", $ParentTagValue)
    }
    Invoke-Python $writeArgs

    $applySh = Join-Path $RepoRoot "scripts\apply-contour.sh"
    if (-not (Test-Path $applySh)) { throw "missing $applySh" }

    $zipPath = Join-Path $Dir "$Prefix-${Tag}-contour.zip"
    $asmArgs = @(
        "scripts/airgap_overlay.py", "assemble-contour",
        "--mode", $DropMode,
        "--dest", $zipPath,
        "--apply-md", $applyPath
    )
    foreach ($member in $MemberPaths) {
        $asmArgs += @("--member", $member)
    }
    $asmArgs += @("--member", $applySh)
    Invoke-Python $asmArgs
    Remove-Item $applyPath -Force -ErrorAction SilentlyContinue
    Write-Host "Contour drop: $zipPath"
    return $zipPath
}

function Write-LfFile([string]$Path, [string]$Text) {
    # sha256sum and the apply script run on Linux. Set-Content on Windows
    # writes CRLF, and the CR becomes part of the filename in the sum file.
    $normalized = ($Text -replace "`r`n", "`n" -replace "`r", "`n")
    if (-not $normalized.EndsWith("`n")) { $normalized += "`n" }
    [System.IO.File]::WriteAllText($Path, $normalized)
}

function Get-ComposeImageId([string]$Service) {
    # The tag compose just built. `docker compose images` follows containers
    # that are already running, and tagging that id back onto $MODEL_TAG
    # replaces the new image with the old one.
    $ref = switch ($Service) {
        "model-api" { "${ImageApi}:$($env:MODEL_TAG)" }
        "model-web" { "${ImageWeb}:$($env:MODEL_TAG)" }
        default { throw "unknown service $Service" }
    }
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $id = (& docker image inspect $ref --format "{{.Id}}" 2>$null)
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prevEap
    if ($code -ne 0 -or -not $id) {
        throw "No image id for $ref; run build first"
    }
    return $id.Trim()
}

function Invoke-Retention {
    param([string]$Dir, [int]$Keep, [string]$PrefixFilter, [string]$ModeFilter = "")
    if ($Keep -lt 1) { return }
    $archives = Get-ChildItem $Dir -Filter "${PrefixFilter}*" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Extension -in ".gz", ".tar", ".zip" -or $_.Name -match '\.(tar\.gz|manifest\.json|sha256)$'
        }
    if ($ModeFilter -eq "overlay") {
        $archives = $archives | Where-Object { $_.Name -match '-overlay' }
    } elseif ($ModeFilter -eq "full") {
        $archives = $archives | Where-Object { $_.Name -notmatch '-overlay' -and $_.Name -notmatch '-contour' }
    }
    $archives = $archives | Sort-Object LastWriteTime -Descending
    $groups = $archives | Group-Object {
        ($_.BaseName -replace '\.(tar|manifest)$', '') -replace '\.gz$', ''
    }
    $toRemove = $groups | Select-Object -Skip $Keep
    foreach ($group in $toRemove) {
        foreach ($file in $group.Group) {
            Write-Host "Retention: removing $($file.Name)"
            Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
        }
    }
}

function Compress-TarGzip {
    param([string]$Source, [string]$Destination)
    $inStream = [System.IO.File]::OpenRead($Source)
    try {
        $outStream = [System.IO.File]::Create($Destination)
        try {
            $gzip = New-Object System.IO.Compression.GZipStream(
                $outStream,
                [System.IO.Compression.CompressionLevel]::Optimal
            )
            try {
                $inStream.CopyTo($gzip)
            } finally {
                $gzip.Dispose()
            }
        } finally {
            $outStream.Dispose()
        }
    } finally {
        $inStream.Dispose()
    }
}

function Invoke-ConfigBundle {
    param([string]$Dir, [string]$Version)
    $bundleDir = Join-Path $env:TEMP "moex-release-bundle-$Version"
    if (Test-Path $bundleDir) { Remove-Item $bundleDir -Recurse -Force }
    New-Item -ItemType Directory -Path $bundleDir -Force | Out-Null

    $paths = @(
        "docker-compose.yml",
        "docker/docker-compose.prod.yml",
        ".env.example"
    )
    foreach ($rel in $paths) {
        $src = Join-Path $RepoRoot $rel
        if (-not (Test-Path -LiteralPath $src)) {
            Write-Warning "Config bundle: skip missing $rel"
            continue
        }
        $dest = Join-Path $bundleDir $rel
        Ensure-Dir (Split-Path $dest -Parent)
        Copy-Item -LiteralPath $src -Destination $dest -Force
    }

    $zipPath = Join-Path $Dir "release-bundle-${Version}.zip"
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
    Invoke-Python @(
        "scripts/airgap_overlay.py", "zip-tree",
        "--src", $bundleDir,
        "--dest", $zipPath
    )
    Remove-Item $bundleDir -Recurse -Force
    Write-Host "Config bundle: $zipPath"
    return $zipPath
}

function Get-ParentFullManifest {
    param([string]$Tag, [string]$Dir, [string]$ExplicitPath)
    if ($ExplicitPath) {
        if (-not (Test-Path -LiteralPath $ExplicitPath)) {
            throw "ParentManifest not found: $ExplicitPath"
        }
        return (Resolve-Path $ExplicitPath).Path
    }
    $candidate = Join-Path $Dir "$Prefix-${Tag}.manifest.json"
    if (-not (Test-Path -LiteralPath $candidate)) {
        throw "Parent Full manifest missing: $candidate (pass -ParentManifest or pack Full into -OutDir first)"
    }
    return $candidate
}

function Invoke-FrontendBuildInDocker {
    Write-Host "Frontend build via node:20-alpine ..."
    $frontendAbs = Join-Path $RepoRoot "apps\web"
    if (-not (Test-Path $frontendAbs)) { throw "frontend dir missing: $frontendAbs" }
    $winMount = $RepoRoot.Path
    if ($winMount -match '^[A-Za-z]:') {
        $winMount = $winMount -replace '\\', '/'
    }
    $cmd = @(
        "run", "--rm",
        "-v", "${winMount}:/app",
        "-w", "/app/apps/web",
        "node:20-alpine",
        "sh", "-c",
        "npm ci && npm run build && test -f dist/index.html"
    )
    Write-Host "docker $($cmd -join ' ')"
    & docker @cmd
    if ($LASTEXITCODE -ne 0) { throw "frontend docker build failed" }
}

function Invoke-OverlayPack {
    param(
        [string]$Dir,
        [string]$Version,
        [string]$GitSha,
        [string]$Fingerprint
    )
    if (-not $ParentTag) {
        throw "Overlay requires -ParentTag (Full version tag, e.g. 0.1.0)"
    }

    $manifestPath = Get-ParentFullManifest -Tag $ParentTag -Dir $Dir -ExplicitPath $ParentManifest
    $parentFullMeta = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($parentFullMeta.mode -and $parentFullMeta.mode -ne "full") {
        throw "Parent manifest mode must be 'full' (got '$($parentFullMeta.mode)'): $manifestPath"
    }
    $parentFp = [string]$parentFullMeta.deps_fingerprint
    if ([string]::IsNullOrWhiteSpace($parentFp)) {
        throw "Parent Full manifest lacks deps_fingerprint: $manifestPath (re-pack Full)"
    }
    if ($parentFp -ne $Fingerprint) {
        throw "deps_fingerprint mismatch vs parent Full — Overlay not allowed; run Full pack."
    }

    Invoke-FrontendBuildInDocker

    $stageDir = Join-Path $env:TEMP "moex-overlay-stage-$Version-$GitSha"
    if (Test-Path $stageDir) { Remove-Item $stageDir -Recurse -Force }

    Write-Host "Staging overlay context ..."
    Invoke-Python @(
        "scripts/airgap_overlay.py", "stage",
        "--dest", $stageDir,
        "--parent-tag", $ParentTag,
        "--version", $Version,
        "--git-sha", $GitSha,
        "--parent-fingerprint", $Fingerprint
    )

    $overlayManifest = Get-Content (Join-Path $stageDir "overlay.manifest.json") -Raw | ConvertFrom-Json
    $newTag = $overlayManifest.new_tag

    $zipName = "$Prefix-${newTag}-overlay.zip"
    $zipPath = Join-Path $Dir $zipName
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
    Invoke-Python @(
        "scripts/airgap_overlay.py", "zip-tree",
        "--src", $stageDir,
        "--dest", $zipPath
    )
    Remove-Item $stageDir -Recurse -Force

    $hash = (Get-FileHash -Algorithm SHA256 -Path $zipPath).Hash.ToLowerInvariant()
    $shaFile = "$zipPath.sha256"
    Write-LfFile $shaFile "$hash  $zipName"
    $sizeBytes = (Get-Item $zipPath).Length

    $bundlePath = $null
    if (-not $SkipConfigBundle) {
        $bundlePath = Invoke-ConfigBundle -Dir $Dir -Version $newTag
    }

    $outManifest = [ordered]@{
        mode             = "overlay"
        parent_tag       = $ParentTag
        new_tag          = $newTag
        version          = $Version
        git_sha          = $GitSha
        git_commit_unix  = $overlayManifest.git_commit_unix
        deps_fingerprint = $Fingerprint
        images           = $overlayManifest.images
        created_utc      = (Get-Date).ToUniversalTime().ToString("o")
        file             = $zipName
        sha256           = $hash
        size_bytes       = $sizeBytes
    }
    if ($bundlePath) {
        $outManifest.config_bundle = (Split-Path $bundlePath -Leaf)
    }
    $manifestFile = Join-Path $Dir "$Prefix-${newTag}-overlay.manifest.json"
    Write-LfFile $manifestFile ($outManifest | ConvertTo-Json -Depth 6)

    Invoke-Retention -Dir $Dir -Keep $KeepLast -PrefixFilter "$Prefix-" -ModeFilter "overlay"
    if ($bundlePath) {
        Invoke-Retention -Dir $Dir -Keep $KeepLast -PrefixFilter "release-bundle-"
    }

    Write-Host ""
    Write-Host "Packed overlay: $zipPath"
    Write-Host "SHA256: $hash"
    Write-Host "Size:   $([math]::Round($sizeBytes / 1MB, 1)) MB"
    Write-Host "Manifest: $manifestFile"
    Write-Host ""
    Write-Host "On the closed host:"
    Write-Host "  unzip $zipName -d /tmp/moex-overlay"
    Write-Host "  cd /tmp/moex-overlay && bash apply-overlay.sh"
    Write-Host "  export MODEL_TAG=${newTag}"
    Write-Host "  docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d"

    return [pscustomobject]@{
        newTag       = $newTag
        zipPath      = $zipPath
        shaFile      = $shaFile
        manifestFile = $manifestFile
        bundlePath   = $bundlePath
    }
}

if (-not $OutDir) {
    $OutDir = Join-Path $RepoRoot "reports\docker"
}
Ensure-Dir $OutDir

$script:ContourActive = [bool]$Contour
$script:ContourParentTag = $ParentTag

if ($Contour) {
    Write-Host "Contour: require a clean git tree (a version bump may stay uncommitted) ..."
    Invoke-Python @("scripts/airgap_overlay.py", "gate-clean", "--allow-pyproject-version")

    $porcelain = (& git status --porcelain 2>$null)
    $needsBump = -not ($porcelain | Where-Object { $_ -match 'pyproject\.toml' })
    if ($needsBump) {
        Write-Host "Contour: bump patch in pyproject.toml ..."
        $bumpJson = & python scripts/airgap_overlay.py bump-patch
        if ($LASTEXITCODE -ne 0) { throw "Contour bump-patch failed" }
        $bumpObj = ($bumpJson | Select-Object -Last 1) | ConvertFrom-Json
        Write-Host "Version $($bumpObj.old) -> $($bumpObj.new)"
        $prevEap = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & uv lock 2>&1 | Out-Null
        $ErrorActionPreference = $prevEap
        if ($LASTEXITCODE -ne 0) { throw "uv lock failed after version bump" }
    } else {
        Write-Host "Contour: pyproject.toml already bumped — skip bump-patch"
    }

    $GitSha = Get-GitSha
    Invoke-Python @("scripts/airgap_overlay.py", "gate-clean", "--allow-pyproject-version")

    $Version = Get-AppVersion
    $Fingerprint = Get-DepsFingerprint
    Write-Host "deps_fingerprint=$Fingerprint"

    if (-not $ParentTag) {
        throw "Contour requires -ParentTag (last Full tag on the closed host, e.g. 0.1.0)"
    }
    $parentManifestPath = Get-ParentFullManifest -Tag $ParentTag -Dir $OutDir -ExplicitPath $ParentManifest
    $parentFullMeta = Get-Content -LiteralPath $parentManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $parentFp = [string]$parentFullMeta.deps_fingerprint
    if ($parentFullMeta.mode -and $parentFullMeta.mode -ne "full") {
        throw "Parent manifest mode must be 'full': $parentManifestPath"
    }
    if ([string]::IsNullOrWhiteSpace($parentFp)) {
        throw "Parent Full manifest lacks deps_fingerprint: $parentManifestPath"
    }

    Invoke-Python @(
        "scripts/airgap_overlay.py", "gate-version",
        "--out-dir", $OutDir,
        "--version", $Version,
        "--git-sha", $GitSha
    )

    if ($parentFp -eq $Fingerprint) {
        Write-Host "Contour: fingerprint matches parent Full -> Overlay"
        $Mode = "Overlay"
    } else {
        $parentShort = $parentFp.Substring(0, [Math]::Min(12, $parentFp.Length))
        $currentShort = $Fingerprint.Substring(0, [Math]::Min(12, $Fingerprint.Length))
        Write-Host "Contour: fingerprint mismatch -> Full pack (parent=$parentShort... current=$currentShort...)"
        $Mode = "Full"
        $ParentTag = ""
    }
} else {
    $Version = Get-AppVersion
    $GitSha = Get-GitSha
    Write-Host "MOEX_VERSION=$Version  GIT_SHA=$GitSha  Mode=$Mode  OutDir=$OutDir"
    $Fingerprint = Get-DepsFingerprint
    Write-Host "deps_fingerprint=$Fingerprint"
}

if ($Mode -eq 'Overlay') {
    $overlay = Invoke-OverlayPack -Dir $OutDir -Version $Version -GitSha $GitSha -Fingerprint $Fingerprint
    if ($script:ContourActive) {
        $members = @($overlay.zipPath, $overlay.shaFile, $overlay.manifestFile)
        if ($overlay.bundlePath) { $members += $overlay.bundlePath }
        New-ContourDropZip -Dir $OutDir -Tag $overlay.newTag -DropMode "overlay" `
            -ParentTagValue $script:ContourParentTag -MemberPaths $members | Out-Null
        Write-Host "Commit the pyproject.toml bump ($Version) separately after pack."
    }
    return
}

$Tag = "${ImageApi}:${Version}"
$TagWeb = "${ImageWeb}:${Version}"
$imageRefs = @($Tag, $TagWeb)

$env:DEPS_FINGERPRINT = $Fingerprint
$env:MOEX_VERSION = $Version
$env:GIT_SHA = $GitSha
$env:MODEL_TAG = $Version

if (-not $SkipBuild) {
    $services = @("model-api", "model-web")
    $needNoCache = $NoCache
    if (-not $needNoCache) {
        if (Test-LocalTagNeedsNoCache -ImageRef $Tag -ExpectedSha $GitSha) {
            Write-Host "Local $Tag has a different or missing moexmodel.git_sha -> --no-cache"
            $needNoCache = $true
        } elseif (Test-LocalTagNeedsNoCache -ImageRef $TagWeb -ExpectedSha $GitSha) {
            Write-Host "Local $TagWeb has a different or missing moexmodel.git_sha -> --no-cache"
            $needNoCache = $true
        }
    }
    if ($needNoCache) {
        Invoke-ComposeBuild -Services $services -ForceNoCache
    } else {
        Invoke-ComposeBuild -Services $services
    }

    $apiId = Get-ComposeImageId "model-api"
    $webId = Get-ComposeImageId "model-web"
    Write-Host "Tagging $Tag ..."
    & docker tag $apiId $Tag
    if ($LASTEXITCODE -ne 0) { throw "docker tag api failed" }
    Write-Host "Tagging $TagWeb ..."
    & docker tag $webId $TagWeb
    if ($LASTEXITCODE -ne 0) { throw "docker tag web failed" }

    Write-Host "Smoke: api imports ..."
    & docker run --rm --entrypoint python $Tag -c "import moex_model_api, moex_publication_viewer; print('ok')"
    if ($LASTEXITCODE -ne 0) { throw "Smoke api failed" }

    Write-Host "Smoke: web root ..."
    & docker run --rm --add-host model-api:127.0.0.1 --entrypoint sh $TagWeb -c "touch /etc/nginx/conf.d/auth.inc && nginx -t && test -f /usr/share/nginx/html/index.html && test -f /etc/nginx/conf.d/default.conf"
    if ($LASTEXITCODE -ne 0) { throw "Smoke web failed" }
} else {
    Write-Host "SkipBuild: using existing tags $Tag / $TagWeb"
}

$ext = if ($NoGzip) { "tar" } else { "tar.gz" }
$OutFile = Join-Path $OutDir "$Prefix-${Version}.${ext}"
$ShaFile = "$OutFile.sha256"
$ManifestFile = Join-Path $OutDir "$Prefix-${Version}.manifest.json"

Write-Host "docker save -> $OutFile ..."
if ($NoGzip) {
    & docker save @imageRefs -o $OutFile
    if ($LASTEXITCODE -ne 0) { throw "docker save failed" }
} else {
    $tmpTar = Join-Path $OutDir "$Prefix-${Version}.tar"
    & docker save @imageRefs -o $tmpTar
    if ($LASTEXITCODE -ne 0) { throw "docker save failed" }
    Compress-TarGzip -Source $tmpTar -Destination $OutFile
    if (-not (Test-Path $OutFile)) { throw "gzip failed" }
    Remove-Item $tmpTar -Force
}

$hash = (Get-FileHash -Algorithm SHA256 -Path $OutFile).Hash.ToLowerInvariant()
Write-LfFile $ShaFile "$hash  $(Split-Path $OutFile -Leaf)"
$sizeBytes = (Get-Item $OutFile).Length

$bundlePath = $null
if (-not $SkipConfigBundle) {
    $bundlePath = Invoke-ConfigBundle -Dir $OutDir -Version $Version
}

$manifest = [ordered]@{
    mode             = "full"
    images           = $imageRefs
    version          = $Version
    git_sha          = $GitSha
    deps_fingerprint = $Fingerprint
    created_utc      = (Get-Date).ToUniversalTime().ToString("o")
    file             = (Split-Path $OutFile -Leaf)
    sha256           = $hash
    size_bytes       = $sizeBytes
}
if ($bundlePath) {
    $manifest.config_bundle = (Split-Path $bundlePath -Leaf)
}
Write-LfFile $ManifestFile ($manifest | ConvertTo-Json -Depth 4)

Invoke-Retention -Dir $OutDir -Keep $KeepLast -PrefixFilter "$Prefix-" -ModeFilter "full"
Invoke-Retention -Dir $OutDir -Keep $KeepLast -PrefixFilter "release-bundle-"

if ($script:ContourActive) {
    $members = @($OutFile, $ShaFile, $ManifestFile)
    if ($bundlePath) { $members += $bundlePath }
    New-ContourDropZip -Dir $OutDir -Tag $Version -DropMode "full" `
        -ParentTagValue "" -MemberPaths $members | Out-Null
    Write-Host "Commit the pyproject.toml bump ($Version) separately after pack."
}

Write-Host ""
Write-Host "Packed: $OutFile"
Write-Host "SHA256: $hash"
Write-Host "Size:   $([math]::Round($sizeBytes / 1MB, 1)) MB"
Write-Host "Manifest: $ManifestFile"
if ($bundlePath) { Write-Host "Config bundle: $bundlePath" }
Write-Host ""
Write-Host "On the closed host:"
Write-Host "  sha256sum -c $(Split-Path $OutFile -Leaf).sha256"
Write-Host "  gunzip -c $(Split-Path $OutFile -Leaf) | docker load"
Write-Host "  unzip release-bundle-${Version}.zip -d /opt/moex-data-model"
Write-Host "  export MODEL_TAG=${Version}"
Write-Host "  docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d"
