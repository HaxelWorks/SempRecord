$dot = "."
$frontDir = "frontend/public/build"
$readme = "README.md"
$readmeDst = "."
$settings = "default_settings.yaml"
$ffmpeg = "ffmpeg.exe"
$license = "LICENSE.txt"
$icon = "icon.ico"
$pyInstallerArgs = @(
    "--onefile",
    "--icon=icon.ico",
    # Data files
    "--add-data=$icon;$dot",
    "--add-data=$license;$dot",
    "--add-data=$frontDir;$frontDir",
    "--add-data=$readme;$dot",
    "--add-data=$settings;$dot",
    # Binaries
    "--add-binary=$ffmpeg;$dot",
    "main.py"
)

pyinstaller @pyInstallerArgs
