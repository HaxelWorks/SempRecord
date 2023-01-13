import os
import yaml
import pathlib

# Load YAML config file
config: dict = yaml.safe_load(open("config.yaml"))


def get_recording_dir():
    user = os.path.expanduser("~")
    folder = os.path.join(user, "Video's", "Recordings")
    return folder

# convert to pathlib
def get_recording_dir():
    user = pathlib.Path.home()
    folder = user / "Video's" / "Recordings"
    return folder

def get_desktop_resolution():
    from ctypes import windll

    user32 = windll.user32
    user32.SetProcessDPIAware()
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize
