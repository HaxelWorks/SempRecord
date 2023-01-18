import os
import yaml
import pathlib


def get_recording_dir():
    user = os.path.expanduser("~")
    folder = os.path.join(user, "Video's", "Recordings")
    return folder


# convert to pathlib
def get_recording_dir():
    user = pathlib.Path.home()
    folder = user / "Videos" / "Recordings"
    return folder


def get_desktop_resolution():
    from ctypes import windll

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


# GENERATED CONSTANTS
DISPLAY_RES = get_desktop_resolution()
THUMBNAIL_RES = (
    DISPLAY_RES[0] // THUMBNAIL_REDUCTION,
    DISPLAY_RES[1] // THUMBNAIL_REDUCTION,
)
