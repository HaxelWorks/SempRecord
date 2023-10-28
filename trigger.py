import tray
import recorder
import threading
from settings import settings
from time import sleep
from util import getForegroundWindowTitle, isTriggerlisted


# ==========AUTO-TRIGGER==========
trigger_enabled = threading.Event()
def trigger_thread(interval=10):
    """Automatically starts and stops recording based on the foreground window title."""

    while True:
        sleep(interval)    
        trigger_enabled.wait()
        window_title = getForegroundWindowTitle()
        if isTriggerlisted(window_title) and recorder.RECORDER is None:
            tray.start()




# start the recording trigger thread
threading.Thread(target=trigger_thread,name="Auto Trigger Thread",daemon=True).start()
