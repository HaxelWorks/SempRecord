import os
import yaml
import pathlib
from ctypes import windll
import appdirs
import shutil
from typing import List

DEFAULT_SETTINGS_FILE = "default_settings.yaml"
THUMBNAIL_REDUCTION = 4
RECORDING_DIR = ''
data_dir = appdirs.site_data_dir("SempRecord", appauthor="HaxelWorks")
os.makedirs(data_dir, exist_ok=True) # Make sure the data directory exists
settings_path = os.path.join(data_dir, "settings.yaml")

if not os.path.isfile(settings_path):
   # If the settings file doesn't exist,
   # copy the default settings file to the data_dir and renamed as settings.yaml
   with open(DEFAULT_SETTINGS_FILE) as d:
    shutil.copyfile(DEFAULT_SETTINGS_FILE, settings_path)
 

# Load YAML config file
with open(settings_path) as f:
    _settings: dict = yaml.safe_load(f.read())
    # expose all config values as global variables
    globals().update(_settings)

# CONFIG TYPES
TYPES = [
    ('RECORDING_DIR', str),
    ('USE_BLACKLIST', bool),
    ('BLACKLISTED_APPS', List[str]),
    ('USE_AUTOSTART', bool),
    ('AUTOSTART_APPS', List[str]),
    ('INPUT_FPS', int),
    ('OUTPUT_FPS', int),
    ('THUMBNAIL_REDUCTION', int),
    ('THUMBNAIL_INTERVAL', int)
]
USER_VARS = [key for key, _ in TYPES]

def save_settings():
    """Save current settings to settings.yaml"""
    _settings = {k: globals()[k] for k in USER_VARS}
    with open(settings_path, 'w') as f:
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


