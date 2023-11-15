import tray
import recorder
import threading
from settings import settings
from time import sleep
from util import getForegroundWindowTitle, isTriggerlisted


# ==========AUTO-TRIGGER==========
def trigger_thread(interval=10):
    """Automatically starts and stops recording based on the foreground window title."""
    sleep(interval)
    while settings.USE_AUTOTRIGGER:
        sleep(interval)
        window_title = getForegroundWindowTitle()
        if isTriggerlisted(window_title) and recorder.RECORDER is None:
            tray.start()

def enable():
    """start the recording trigger thread"""
    settings.USE_AUTOTRIGGER = True
    threading.Thread(target=trigger_thread, name="Auto Trigger Thread", daemon=True).start()

def disable():
    """stop the recording trigger thread"""
    settings.USE_AUTOTRIGGER = False

enable()