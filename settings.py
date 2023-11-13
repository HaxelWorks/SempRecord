from dataclasses import dataclass, asdict
from re import T

from typing import List
import yaml
from pathlib import Path


@dataclass()
class Settings:
    # LIST OF SETTINGS
    AUTOTRIGGER_APPS: List[str]
    WHITELISTED_APPS: List[str]
    BLACKLISTED_APPS: List[str]
    HOME_DIR: Path = Path.home() / "Videos" / "SempRecord"
    RUN_ON_BOOT: bool = False
    USE_AUTOTRIGGER: bool = True
    USE_WHITELIST: bool = True
    USE_BLACKLIST: bool = True
    FRAME_RATE: int = 20

    THUMB_REDUCE_FACTOR: int = 5
    THUMBNAIL_INTERVAL: int = 100  # in seconds

    def __init__(self):
        self.AUTOTRIGGER_APPS = [
            "Google Chrome",
            "Visual Studio Code",
            "Blender",
            "Cura",
            "Autodesk Inventor Professional 2023",
            "PotPlayer",
            "Plex"
        ]
        self.WHITELISTED_APPS = []
        self.BLACKLISTED_APPS = ["YouTube", "Porn", "Gmail","F1 TV"]

    def load(self, name="settings.yaml"):
        """Load settings from a yaml file"""
        path = self.HOME_DIR / name
        with open(path, "r") as f:
            settings = yaml.safe_load(f.read())
            [setattr(self, k, v) for k, v in settings.items()]
            
            self.HOME_DIR = Path(self.HOME_DIR) # special case for paths

    def save(self):
        """Save settings to a yaml file"""
        path = self.HOME_DIR / ".settings" / "settings.yaml"
        with open(path, "w") as f:
            settings = asdict(self)
            settings["HOME_DIR"] = str(settings["HOME_DIR"])  # convert to string
            yaml.dump(settings, f)

settings = Settings()