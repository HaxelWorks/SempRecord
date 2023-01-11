import os
import yaml

# Load YAML config file
config = yaml.safe_load(open("config.yaml"))

def get_recording_dir():
    user = os.path.expanduser("~")
    folder = os.path.join(user, "Video's", "Recordings")
    return folder
   
def get_desktop_resolution():
    from ctypes import windll
    user32 = windll.user32
    user32.SetProcessDPIAware()
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize



# USER CHANGEABLE 
RECORDING_FOLDER = get_recording_dir()
VID_WIDTH = 2560
VID_HEIGHT = 1440
CODEC = "libx264" 
CODEC = "h264_nvenc"
FPS_TARGET = 15
SPEED_MULTIPLIER = 4

# DO NOT CHANGE
CHANGE_THRESHOLD = 400  #sub-pixels
THUMBNAIL_WIDTH = 320
THUMBNAIL_HEIGHT = 180
