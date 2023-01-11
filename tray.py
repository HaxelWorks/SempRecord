import pystray as tray
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

MENU = tray.Menu(
    tray.MenuItem("Start", recorder.start),
    tray.MenuItem("Stop", recorder.stop),
    tray.MenuItem("Pause", recorder.pause),
    tray.MenuItem("Open Folder", open_folder),
    tray.MenuItem("Open Interface", open_browser),
)

# In order for the icon to be displayed, you must provide an icon
icon = tray.Icon(
    "SempRecord",
    icon=ICONS.inactive,
    menu=MENU,
    action=lambda: print("Hello World!"),
)
    


# To finally show you icon, call run
icon.run_detached()
import time

time.sleep(4)
icon.notify("test", "test message")
icon.icon = ICONS.active
input("Press enter to stop recording")
