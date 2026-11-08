# Capture the crash stack trace of the app.
# Run: powershell -ExecutionPolicy Bypass -File logcat.ps1

$ErrorActionPreference = "Continue"
$Root = "D:\myschedule"
$adb  = Join-Path $env:LOCALAPPDATA "Android\Sdk\platform-tools\adb.exe"
if (-not (Test-Path $adb)) { $adb = "adb" }

$out = Join-Path $Root "logcat-crash.txt"

Write-Host "Clearing log buffer ..."
& $adb logcat -c

Write-Host "Starting app ..."
& $adb shell am force-stop com.example.myschedule
& $adb shell am start -n com.example.myschedule/com.example.myschedule.LoginActivity
Start-Sleep -Seconds 4

Write-Host "Dumping crash buffer ..."
& $adb logcat -d -b crash | Out-File -FilePath $out -Encoding utf8
& $adb logcat -d *:E | Select-String -Pattern "FATAL EXCEPTION|AndroidRuntime" -Context 0,25 |
    Out-File -FilePath $out -Append -Encoding utf8

Write-Host ""
Write-Host "Saved to $out"
Write-Host "---- content ----"
Get-Content $out
