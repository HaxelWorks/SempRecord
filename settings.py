from dataclasses import dataclass, asdict, astuple
from typing import List
import yaml
import pathlib
from pathlib import Path

@dataclass()
class Settings:
    # LIST OF SETTINGS
    AUTOTRIGGER_APPS: List[str]
    WHITELISTED_APPS: List[str]
    HOME_DIR: Path = Path.home() / "Videos" / "SempRecord"
    USE_AUTOTRIGGER: bool = False
    USE_WHITELIST: bool = False

    INPUT_FPS: int = 10
    OUTPUT_FPS: int = 60

    THUMB_REDUCE_FACTOR: int = 5
    THUMBNAIL_INTERVAL: int = 150 # in seconds
    
    def __init__(self):
        self.AUTOTRIGGER_APPS = ["Google Chrome","Visual Studio Code"]
        self.WHITELISTED_APPS = []

    def load(self, path):
        """ Load settings from a yaml file """
        with open(path, "r") as f:
            settings = yaml.safe_load(f.read())
            for key, value in settings.items():
                setattr(self, key, value)
        # special case for paths
        self.HOME_DIR = Path(self.HOME_DIR)            

    def save(self, path = "settings.yaml"):
        """ Save settings to a yaml file """
        with open(path, "w") as f:
            settings = asdict(self)
            settings["HOME_DIR"] = str(settings["HOME_DIR"]) # convert to string
            yaml.dump(settings, f)
            
            
settings = Settings()
settings.save("settings.yaml")
settings.load("settings.yaml")


