import pystray
import os
import recorder
from icon_generator import ICONS


# Create a menu with a Start/Stop and pause option
# as well as the option to open a specific folder in the file explorer
# and one that opens the management page in the browser

def open_folder():
    os.startfile("C:\\Users\\Axel1\\Desktop\\SempRecord")
def open_browser():
    os.startfile("http://localhost:5000/")

MENU = pystray.Menu(
    pystray.MenuItem("Start", recorder.start),
    pystray.MenuItem("Stop", recorder.stop),
    pystray.MenuItem("Pause", recorder.pause),
    pystray.MenuItem("Open Folder", open_folder),
    pystray.MenuItem("Open Interface", open_browser),
)

# In order for the icon to be displayed, you must provide an icon
TRAY = pystray.Icon(
    "SempRecord",
    icon=ICONS.inactive,
    menu=MENU,
    action=lambda: print("Hello World!"),
)
    
TRAY.run_detached()



if __name__ == "__main__":
    # iterate through the various states of the recorder
    from time import sleep
    
    for icon in dir(ICONS):
        if icon.startswith("_"):
            continue
        TRAY.icon = getattr(ICONS, icon)
        sleep(2)
        
    
