from ctypes import create_unicode_buffer, windll
from typing import Optional

def getForegroundWindowTitle() -> Optional[str]:
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    if buf.value:
        # strip the string of any non-ascii characters
        text = buf.value.encode("ascii", "ignore").decode()
        return text
    else:
        return None
# ----------------------------------------------------------------------------- 
import pynvml

def nvenc_available() -> bool:
    try:
        pynvml.nvmlInit()
        deviceCount = pynvml.nvmlDeviceGetCount()
        for i in range(deviceCount):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            enc_cap = pynvml.nvmlDeviceGetEncoderCapacity(handle, pynvml.NVML_ENCODER_QUERY_H264)
            if enc_cap > 0:
                return True
        return False
    except Exception as e:
        print("Error: {}".format(e))
        return False
    finally:
        pynvml.nvmlShutdown()
# ----------------------------------------------------------------------------- 
import settings  

def isBlacklisted(app_name: str) -> bool:
    """Returns True if the app is blacklisted or no focus is on an app."""	
    if not app_name:
        return True
    for excl in settings.BLACKLISTED_APPS:
        if app_name.endswith(excl):
            return True
    return False 

def isTriggerlisted(app_name: str) -> bool:
    """Returns True if the app is blacklisted or no focus is on an app."""	
    if not app_name:
        return False
    for incl in settings.AUTOTRIGGER_APPS:
        if app_name.endswith(incl):
            return True
    return False
# ----------------------------------------------------------------------------- 

