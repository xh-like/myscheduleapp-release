# Install the freshly built APK (uninstall first, because the signature differs from the original).
# Run: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"
$Root = "D:\myschedule"
$adb  = Join-Path $env:LOCALAPPDATA "Android\Sdk\platform-tools\adb.exe"
if (-not (Test-Path $adb)) { $adb = "adb" }

$apk = Get-ChildItem (Join-Path $Root "out\signed") -Filter *.apk |
       Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $apk) { throw "No signed apk in $Root\out\signed, run build.ps1 first" }

Write-Host "Uninstalling old package ..."
& $adb uninstall com.example.myschedule

Write-Host "Installing $($apk.Name) ..."
& $adb install "$($apk.FullName)"

Write-Host "Installed version:"
& $adb shell dumpsys package com.example.myschedule | Select-String "versionName|versionCode"
