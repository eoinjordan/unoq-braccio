param(
    [string]$Port = "COM3",
    [string]$Fqbn = "arduino:zephyr:unoq"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path "$PSScriptRoot\.."
$SketchDir = Join-Path $RepoRoot "firmware\unoq_braccio_firmware"

arduino-cli lib install Braccio
arduino-cli core install arduino:zephyr
arduino-cli compile --fqbn $Fqbn $SketchDir
arduino-cli upload -p $Port --fqbn $Fqbn $SketchDir
