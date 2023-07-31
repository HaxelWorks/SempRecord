import sys
import os
from random import randint
import yaml
import pathlib
from ctypes import windll
import appdirs
import shutil
import win32api
import win32con
from typing import List

# LIST OF SETTINGS
RECORDING_DIR: str
USE_BLACKLIST: bool
BLACKLISTED_APPS: List[str]
USE_AUTOSTART: bool
USE_AUTOSTOP: bool
AUTOSTART_APPS: List[str]
AUTOSTART_OVERRIDES_BLACKLIST: bool
INPUT_FPS: int
OUTPUT_FPS: int
THUMBNAIL_REDUCTION: int
THUMBNAIL_INTERVAL: int



# check if _MEIPASS exists, if so we are running this in a pyinstaller's onefile mode
if hasattr(sys, '_MEIPASS'):
    meipass_root = pathlib.Path(sys._MEIPASS)
    DEFAULT_SETTINGS_FILE = meipass_root / "default_settings.yaml"
else:
    DEFAULT_SETTINGS_FILE = "default_settings.yaml"
    
THUMBNAIL_REDUCTION = 4
RECORDING_DIR = ''
data_dir = appdirs.site_data_dir("SempRecord", appauthor="HaxelWerks")
data_dir = pathlib.Path(data_dir)
os.makedirs(data_dir, exist_ok=True) # Make sure the data directory exists
SETTINGS_PATH = data_dir / "settings.yaml"


if not os.path.isfile(SETTINGS_PATH):
   # If the settings file doesn't exist,
   # copy the default settings file to the data_dir and renamed as settings.yaml
   with open(DEFAULT_SETTINGS_FILE) as d:
    shutil.copyfile(DEFAULT_SETTINGS_FILE, SETTINGS_PATH)
 

# Load YAML config file
with open(SETTINGS_PATH) as f:
    _settings: dict = yaml.safe_load(f.read())
    # expose all config values as global variables
    globals().update(_settings)

RECORDING_DIR = pathlib.Path(os.path.expanduser('~')) / "Videos" / "Records"
# create the recording directory if it doesn't exists
RECORDING_DIR.mkdir(exist_ok=True)


# CONFIG TYPES
TYPES = [
    ('RECORDING_DIR', str),
    ('USE_BLACKLIST', bool),
    ('BLACKLISTED_APPS', List[str]),
    ('USE_AUTOSTART', bool),
    ('USE_AUTOSTOP', bool),
    ('AUTOSTART_APPS', List[str]),
    ('INPUT_FPS', int),
    ('OUTPUT_FPS', int),
    ('THUMBNAIL_REDUCTION', int),
    ('THUMBNAIL_INTERVAL', int),
    ('AUTOSTART_OVERRIDES_BLACKLIST', bool)
]
USER_VARS = [key for key, _ in TYPES]

def save_settings():
    """Save current settings to settings.yaml"""
    _settings = {k: globals()[k] for k in USER_VARS}
    with open(SETTINGS_PATH, 'w') as f:
        f.write(yaml.safe_dump(_settings))


# make sure the following folders exist
# .cache - saves thumbnails frames as qoi files
# .metadata - saves changes in window focus as a tsv files
# .thumbnails - saves thumbnails as webp animations
RECORDING_DIR = pathlib.Path(RECORDING_DIR)
RECORDING_DIR.mkdir(exist_ok=True)
(RECORDING_DIR / ".cache").mkdir(exist_ok=True)
(RECORDING_DIR / ".metadata").mkdir(exist_ok=True)
(RECORDING_DIR / ".thumbnails").mkdir(exist_ok=True)


# Set the folders starting with . to hidden
for f in RECORDING_DIR.iterdir():
    if f.name.startswith("."):
        win32api.SetFileAttributes(str(f), win32con.FILE_ATTRIBUTE_HIDDEN)

# GENERATED CONSTANTS
def get_desktop_resolution():
    user32 = windll.user32
    user32.SetProcessDPIAware()
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize

DISPLAY_RES = get_desktop_resolution()
THUMBNAIL_RES = (
    DISPLAY_RES[0] // THUMBNAIL_REDUCTION,
    DISPLAY_RES[1] // THUMBNAIL_REDUCTION,
)


