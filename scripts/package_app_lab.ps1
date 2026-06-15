param(
    [string]$AppName = "braccio_web_agent"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path "$PSScriptRoot\.."
$AppDir = Join-Path $RepoRoot "app_lab\$AppName"
$DistDir = Join-Path $RepoRoot "dist"
$Date = Get-Date -Format yyyyMMdd
$ZipPath = Join-Path $DistDir "$AppName-app_lab-$Date.zip"
$TempParent = Join-Path $env:TEMP "unoq-braccio-applab-package"
$TempDir = Join-Path $TempParent $AppName

if (!(Test-Path $AppDir)) {
    throw "App Lab app not found: $AppDir"
}

Remove-Item -LiteralPath $TempParent -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

robocopy $AppDir $TempDir /E /XD __pycache__ /XF *.pyc | Out-Null
if ($LASTEXITCODE -ge 8) {
    throw "robocopy failed with exit code $LASTEXITCODE"
}

Compress-Archive -Path $TempDir -DestinationPath $ZipPath -Force
Remove-Item -LiteralPath $TempParent -Recurse -Force

Write-Output $ZipPath
