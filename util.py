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
            enc_cap = pynvml.nvmlDeviceGetEncoderCapacity(handle, pynvml.NVML_ENCODER_QUERY_HEVC)
            if enc_cap > 0:
                return True
        return False
    except Exception as e:
        print("Error: {}".format(e))
        return False
    finally:
        pynvml.nvmlShutdown()
# ----------------------------------------------------------------------------- 
from settings import settings

def isWhiteListed(app_name: str) -> bool:
    """Returns True if the app is whitelisted or no focus is on an app."""	
    
    if not app_name:
        return False
    
    if settings.USE_BLACKLIST:
        for bl in settings.BLACKLISTED_APPS:
            if bl in app_name:
                return False
            
    if not settings.USE_WHITELIST:
        return True
    
    for wl in settings.WHITELISTED_APPS + settings.AUTOTRIGGER_APPS:
        if app_name.endswith(wl) or app_name.startswith(wl):
            return True
        
    return False 

def isTriggerlisted(app_name: str) -> bool:
    """Returns True if the app is whitelisted or no focus is on an app."""	
    if not app_name:
        return False
    for incl in settings.AUTOTRIGGER_APPS:
        if app_name.endswith(incl) or app_name.startswith(incl):
            return True
    return False




# ----------------------------------------------------------------------------- 
# GENERATED CONSTANTS
from ctypes import windll
def get_desktop_resolution():
    user32 = windll.user32
    user32.SetProcessDPIAware()
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize
def get_thumbnail_resolution():
    x, y = get_desktop_resolution()
    d = settings.THUMB_REDUCE_FACTOR
    return (x // d, y // d)
