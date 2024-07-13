from ctypes import create_unicode_buffer, windll
from typing import Optional

import pynvml

import settings


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


def nvenc_available() -> bool:
    try:
        pynvml.nvmlInit()
        deviceCount = pynvml.nvmlDeviceGetCount()
        for i in range(deviceCount):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            enc_cap = pynvml.nvmlDeviceGetEncoderCapacity(
                handle, pynvml.NVML_ENCODER_QUERY_HEVC
            )
            if enc_cap > 0:
                return True
        return False
    except Exception as e:
        print("Error: {}".format(e))
        return False
    finally:
        pynvml.nvmlShutdown()


def get_desktop_resolution():
    user32 = windll.user32
    user32.SetProcessDPIAware()
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize


def get_thumbnail_resolution():
    x, y = get_desktop_resolution()
    d = settings.THUMBNAIL_RESOLUTION_REDUCTION
    return (x // d, y // d)
