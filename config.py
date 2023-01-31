import os
import yaml
import pathlib
from ctypes import windll

# convert to pathlib
def get_recording_dir():
    user = pathlib.Path.home()
    folder = user / "Videos" / "Recordings"
    return folder

# make sure the following folders exist
# .cache - saves thumbnails frames as qoi files
# .metadata - saves changes in window focus as a tsv files
# .thumbnails - saves thumbnails as webp animations
recdir = get_recording_dir()
recdir.mkdir(exist_ok=True)
(recdir / ".cache").mkdir(exist_ok=True)
(recdir / ".metadata").mkdir(exist_ok=True)
(recdir / ".thumbnails").mkdir(exist_ok=True)

def get_desktop_resolution():
    user32 = windll.user32
    user32.SetProcessDPIAware()
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize

# Load YAML config file
yaml_config: dict = yaml.safe_load(open("config.yaml"))
# expose all config values as global variables
globals().update(yaml_config)

# CONFIG TYPES
USE_BLACKLIST: bool
BLACKLISTED_APPS: list[str]
USE_AUTOSTART: bool
AUTOSTART_APPS: list[str]
INPUT_FPS: int
OUTPUT_FPS: int
THUMBNAIL_REDUCTION: int
THUMBNAIL_INTERVAL: int


# GENERATED CONSTANTS
DISPLAY_RES = get_desktop_resolution()
THUMBNAIL_RES = (
    DISPLAY_RES[0] // THUMBNAIL_REDUCTION,
    DISPLAY_RES[1] // THUMBNAIL_REDUCTION,
)
