import os
import winshell
import sys


def startup_folder():
    """Returns the startup folder for the current user"""
    return os.path.join(
        os.getenv("APPDATA"),
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup",
    )


def main_folder():
    """Returns the main folder where the program is installed"""
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def enable():
    """Creates a shortcut in the startup folder to the main folder"""
    path = os.path.join(startup_folder(), "SempRecord.lnk")
    target = os.path.join(main_folder(), "main.exe")
    winshell.CreateShortcut(
        Path=path,
        Target=target,
    )


def disable():
    """Removes the shortcut in the startup folder"""
    path = os.path.join(startup_folder(), "SempRecord.lnk")
    os.remove(path)


if __name__ == "__main__":
    print(startup_folder())
    print(main_folder())
