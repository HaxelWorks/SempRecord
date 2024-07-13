# SEMPRECORD BUILD SCRIPT FOR WINDOWS (POWERSHELL)

# Check if the virtual environment exists
if (!(Test-Path -Path ".\venv")) {
    # Create the virtual environment
    python -m venv venv
    # Activate the virtual environment
    & ".\venv\Scripts\activate"
    # and install the requirements
    pip install -r requirements.txt
}


# Set the variables
$dot = "."
$icon = "icon.ico"
$corpus = "corpus.pkl"
$readme = "README.md"
$license = "LICENSE.txt"
$frontDir = "frontend/public"
$ffmpeg = "ffmpeg.exe"

# activate and use the virtual environment
& ".\venv\Scripts\activate"


# Run icon_generator.py if icon.ico does not already exist
if (!(Test-Path -Path ".\icon.ico")) {
    & ".\icon_generator.py"
}

Remove-Item -Path ".\dist" -Recurse -Force

$pyInstallerArgs = @(
    "--noconsole",
    "--icon=icon.ico",

    # Data files
    "--add-data=$icon;$dot",
    "--add-data=$corpus;$dot",
    "--add-data=$readme;$dot",
    "--add-data=$license;$dot",
    "--add-data=$frontDir;$frontDir",
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

# Install the executable
& ".\dist\SempRecordInstaller.exe"

