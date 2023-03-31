import tray
import recorder
import threading
import settings
from time import sleep
from util import getForegroundWindowTitle, isTriggerlisted


# ==========AUTO-TRIGGER==========
def trigger_thread(interval=15):
    """Automatically starts and stops recording based on the foreground window title."""
   
    sleep(interval)
    while settings.USE_AUTOSTART:
        window_title = getForegroundWindowTitle()
        if isTriggerlisted(window_title) and recorder.RECORDER is None:
            tray.start()
        sleep(interval)
# start the recording trigger thread
threading.Thread(target=trigger_thread,name="Auto Trigger Thread",daemon=True).start()
