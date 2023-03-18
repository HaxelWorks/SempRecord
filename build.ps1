$dot = "."
$frontDir = "frontend/public/build"
$readme = "README.md"
$readmeDst = "."
$settings = "default_settings.yaml"
$ffmpeg = "ffmpeg.exe"
$license = "LICENSE.txt"
$icon = "icon.ico"
$pyInstallerArgs = @(
    "--noconsole",
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

# Build the executable
pyinstaller @pyInstallerArgs

# Build the installer
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "InnoSetup.iss"

# Move the installer to the dist directory and rename it, replace if necessary
Move-Item -Path ".\Output\mysetup.exe" -Destination ".\dist\SempRecordInstaller.exe" -Force

# Remove the Output folder
Remove-Item -Path ".\Output" -Recurse