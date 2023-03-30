import tray
from recorder import Recorder,RECORDER
import threading
import settings
from time import sleep
from util import getForegroundWindowTitle, isTriggerlisted


# ==========AUTO-TRIGGER==========
def trigger_thread(interval=15):
    """Automatically starts and stops recording based on the foreground window title."""
    global RECORDER
    sleep(interval)
    while settings.USE_AUTOTRIGGER:
        window_title = getForegroundWindowTitle()
        if isTriggerlisted(window_title) and RECORDER is None:
            tray.start()
        sleep(interval)
# start the recording trigger thread
threading.Thread(target=trigger_thread,name="Auto Trigger Thread",daemon=True).start()
