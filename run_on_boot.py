import os
import appdirs
import winshell
import sys
def startup_folder():
    startup_folder = os.path.join(appdirs.user_data_dir(), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
def enable():
    # Get the path to the PyInstaller executable
    executable_path = os.path.abspath(sys.executable)

    # Get the path to the Startup folder for the current user
    startup_folder = os.path.join(appdirs.user_data_dir(), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

    # Create the Startup folder if it doesn't already exist
    os.makedirs(startup_folder, exist_ok=True)

    # Construct the path to the shortcut file in the Startup folder
    shortcut_path = os.path.join(startup_folder, "SempRecord.lnk")

    # Create the shortcut using the `winshell` library
    with winshell.shortcut(shortcut_path) as shortcut:
        shortcut.path = executable_path
        shortcut.description = "SempRecord"
        shortcut.write()
        
def disable():
    # Get the path to the PyInstaller executable
    executable_path = os.path.abspath(sys.executable)

    # Get the path to the Startup folder for the current user
    startup_folder = os.path.join(appdirs.user_data_dir(), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

    # Construct the path to the shortcut file in the Startup folder
    shortcut_path = os.path.join(startup_folder, "SempRecord.lnk")
    os.remove(shortcut_path)
    
    

if __name__ == "__main__":
    enable()