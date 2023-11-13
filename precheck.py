import os
import pathlib

import win32api
import win32con

from settings import settings


# Create the HOME_DIR if it doesn't exist
if not settings.HOME_DIR:
    user_dir = os.path.expanduser("~")
    homepath = pathlib.Path(user_dir) / "Videos" / "SempRecord"
    homepath.mkdir(exist_ok=True)
    settings.HOME_DIR = homepath

HOME_DIR = settings.HOME_DIR
HOME_DIR = pathlib.Path(HOME_DIR)
HOME_DIR.mkdir(exist_ok=True)

# Create the following folders if they don't exist
for folder in [".logs", ".cache", ".metadata", ".settings", ".thumbnails", "Records"]:
    (HOME_DIR / folder).mkdir(exist_ok=True)

# Set the folders starting with . to hidden
for f in HOME_DIR.iterdir():
    if f.name.startswith("."):
        win32api.SetFileAttributes(str(f), win32con.FILE_ATTRIBUTE_HIDDEN)



# Description of the folders:
# .cache - saves thumbnails frames as qoi files
# .metadata - saves changes in window focus as a tsv files
# .thumbnails - saves thumbnails as webp animations
# .settings - saves multiple setting profiles as yaml files
# Records - saves the actual recordings as mp4 files


