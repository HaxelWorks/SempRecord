import os
import pathlib

import win32api
import win32con

from settings import settings

# Create the HOME_DIR if it doesn't exist
if not settings.HOME_DIR:
    user_dir = os.path.expanduser("~")
    path = pathlib.Path(user_dir) / "Videos" / "SempRecord"
    path.mkdir(exist_ok=True)
    settings.HOME_DIR = path
    settings.save()


# make sure the following folders exist
# .cache - saves thumbnails frames as qoi files
# .metadata - saves changes in window focus as a tsv files
# .thumbnails - saves thumbnails as webp animations
HOME_DIR = settings.HOME_DIR
HOME_DIR = pathlib.Path(HOME_DIR)
HOME_DIR.mkdir(exist_ok=True)
(HOME_DIR / ".logs").mkdir(exist_ok=True)
(HOME_DIR / ".cache").mkdir(exist_ok=True)
(HOME_DIR / ".metadata").mkdir(exist_ok=True)
(HOME_DIR / ".thumbnails").mkdir(exist_ok=True)
(HOME_DIR / "Records").mkdir(exist_ok=True)


# Set the folders starting with . to hidden
for f in HOME_DIR.iterdir():
    if f.name.startswith("."):
        win32api.SetFileAttributes(str(f), win32con.FILE_ATTRIBUTE_HIDDEN)
