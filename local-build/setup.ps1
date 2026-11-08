# Download all tools from GitHub into D:\myschedule\tools
# Run: powershell -ExecutionPolicy Bypass -File setup.ps1

$ErrorActionPreference = "Stop"
$Root  = "D:\myschedule"
$Tools = Join-Path $Root "tools"

New-Item -ItemType Directory -Force -Path $Tools, "$Root\src", "$Root\out", "$Root\input", "$Root\signing" | Out-Null

function Get-LatestAssetUrl([string]$Repo, [string]$Pattern) {
    $rel = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" `
        -Headers @{ "User-Agent" = "myschedule-local" }
    $asset = $rel.assets | Where-Object { $_.name -match $Pattern } | Select-Object -First 1
    if (-not $asset) { throw "Asset not found: $Repo / $Pattern" }
    return $asset.browser_download_url
}

# ---- JDK 17 (Temurin, GitHub releases) ----
$jdkDir = Join-Path $Tools "jdk"
if (-not (Test-Path (Join-Path $jdkDir "bin\java.exe"))) {
    Write-Host "[1/3] Downloading JDK 17 ..."
    $url = Get-LatestAssetUrl "adoptium/temurin17-binaries" "OpenJDK17U-jdk_x64_windows_hotspot_.*\.zip$"
    $zip = Join-Path $Tools "jdk.zip"
    Invoke-WebRequest -Uri $url -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath $Tools -Force
    $inner = Get-ChildItem $Tools -Directory | Where-Object { $_.Name -like "jdk-17*" } | Select-Object -First 1
    if (-not $inner) { throw "JDK folder not found after unzip" }
    Move-Item $inner.FullName $jdkDir -Force
    Remove-Item $zip -Force
} else {
    Write-Host "[1/3] JDK 17 already present"
}

# ---- apktool (GitHub releases) ----
$apktool = Join-Path $Tools "apktool.jar"
if (-not (Test-Path $apktool)) {
    Write-Host "[2/3] Downloading apktool ..."
    $url = Get-LatestAssetUrl "iBotPeaches/Apktool" "apktool_.*\.jar$"
    Invoke-WebRequest -Uri $url -OutFile $apktool
} else {
    Write-Host "[2/3] apktool already present"
}

# ---- uber-apk-signer (GitHub releases) ----
$signer = Join-Path $Tools "uber-apk-signer.jar"
if (-not (Test-Path $signer)) {
    Write-Host "[3/3] Downloading uber-apk-signer ..."
    $url = Get-LatestAssetUrl "patrickfav/uber-apk-signer" "uber-apk-signer-.*\.jar$"
    Invoke-WebRequest -Uri $url -OutFile $signer
} else {
    Write-Host "[3/3] uber-apk-signer already present"
}

Write-Host ""
Write-Host "Done. Tools are in $Tools"
& "$jdkDir\bin\java.exe" -version
