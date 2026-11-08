# Download the released APK from GitHub, decompile it, then overlay the patched files.
# Run: powershell -ExecutionPolicy Bypass -File prepare.ps1

$ErrorActionPreference = "Stop"
$Root  = "D:\myschedule"
$Tools = Join-Path $Root "tools"
$Java  = Join-Path $Tools "jdk\bin\java.exe"
$Apktool = Join-Path $Tools "apktool.jar"

if (-not (Test-Path $Java))    { throw "Run setup.ps1 first" }
if (-not (Test-Path $Apktool)) { throw "Run setup.ps1 first" }

$apk = Join-Path $Root "input\app-release.apk"
New-Item -ItemType Directory -Force -Path (Split-Path $apk) | Out-Null
if (-not (Test-Path $apk)) {
    Write-Host "[1/3] Downloading app-release.apk from GitHub ..."
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/xh-like/myscheduleapp-release/main/app-release.apk" -OutFile $apk
} else {
    Write-Host "[1/3] Using existing $apk"
}

Write-Host "[2/3] Decompiling to $Root\src ..."
& $Java -jar $Apktool d -f $apk -o (Join-Path $Root "src")
if ($LASTEXITCODE -ne 0) { throw "apktool decode failed" }

Write-Host "[3/3] Overlaying patched files ..."
$patch = Join-Path $PSScriptRoot "patches"
if (Test-Path $patch) {
    Get-ChildItem -Path $patch -Recurse -File | ForEach-Object {
        $rel  = $_.FullName.Substring($patch.Length + 1)
        $dest = Join-Path (Join-Path $Root "src") $rel
        New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
        Copy-Item $_.FullName $dest -Force
        Write-Host "  patched $rel"
    }
}

Write-Host ""
Write-Host "Source project ready: $Root\src"
Write-Host "Edit smali / xml there, then run build.ps1"
