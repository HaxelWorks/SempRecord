from turtle import st
import yaml
from pathlib import Path
    
HOME_DIR: Path = Path.home() / "SempRecord"
RUN_ON_BOOT: bool = False
FRAME_RATE: int = 20
THUMBNAIL_RESOLUTION_REDUCTION: int = 5
THUMBNAIL_SECONDS_INTERVAL: int = 100  # in seconds
WL_ENABLE = True
BL_ENABLE = True


def gobals_as_dict():
    settings = {}
    for k, v in globals().items():
        if k.isupper():
            settings[k] = v
    return settings


def save_settings():
    settings = gobals_as_dict()
    settings["HOME_DIR"] = str(HOME_DIR)
    path = HOME_DIR / ".settings" / "settings.yaml"
    with open(path, "w") as f:
        yaml.dump(settings, f)
    

def load_settings():
    global HOME_DIR
    path = HOME_DIR / ".settings" / "settings.yaml"
    with open(path, "r") as f:
        settings = yaml.safe_load(f.read())
        if not settings:
            return
        for k, v in settings.items():
            globals()[k] = v
    
        HOME_DIR = Path(HOME_DIR)