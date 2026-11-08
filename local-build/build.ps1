# Rebuild the patched project and sign it.
# Run: powershell -ExecutionPolicy Bypass -File build.ps1

$ErrorActionPreference = "Stop"
$Root  = "D:\myschedule"
$Tools = Join-Path $Root "tools"
$Java  = Join-Path $Tools "jdk\bin\java.exe"
$Keytool = Join-Path $Tools "jdk\bin\keytool.exe"
$Apktool = Join-Path $Tools "apktool.jar"
$Signer  = Join-Path $Tools "uber-apk-signer.jar"

if (-not (Test-Path $Java)) { throw "Run setup.ps1 first" }

$ks = Join-Path $Root "signing\release.jks"
if (-not (Test-Path $ks)) {
    Write-Host "[1/3] Creating signing key ..."
    New-Item -ItemType Directory -Force -Path (Split-Path $ks) | Out-Null
    & $Keytool -genkeypair -keystore $ks -alias schedule -keyalg RSA -keysize 2048 `
        -validity 10000 -storepass "Schedule@318" -keypass "Schedule@318" `
        -dname "CN=myschedule, OU=dev, O=myschedule, L=CN, ST=CN, C=CN"
} else {
    Write-Host "[1/3] Signing key already present"
}

Write-Host "[2/3] Building APK ..."
$unsigned = Join-Path $Root "out\app-unsigned.apk"
& $Java -jar $Apktool b (Join-Path $Root "src") -f -o $unsigned
if ($LASTEXITCODE -ne 0) { throw "apktool build failed" }

Write-Host "[3/3] Signing APK ..."
& $Java -jar $Signer -a $unsigned --ks $ks --ksAlias schedule `
    --ksPass "Schedule@318" --ksKeyPass "Schedule@318" -o (Join-Path $Root "out\signed")
if ($LASTEXITCODE -ne 0) { throw "signing failed" }

Get-ChildItem (Join-Path $Root "out\signed") -Filter *.apk | ForEach-Object {
    Write-Host ""
    Write-Host "Signed: $($_.FullName)"
    Get-FileHash $_.FullName -Algorithm SHA256 | ForEach-Object { Write-Host "SHA256: $($_.Hash)" }
}
