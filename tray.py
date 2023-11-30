import os
from threading import Thread
from time import sleep
import atexit
import pystray
from windows_toasts import ToastButton, ToastText1, WindowsToaster

import recorder
import trigger
from icon_generator import ICONS
from settings import settings
import run_on_boot

def exit_program():
    print("Exiting safely...""")
    if recorder.is_recording():
        stop()
    # exit the program
    os._exit(0)
    
atexit.register(exit_program)

def open_folder():
    os.startfile(str(settings.HOME_DIR))


def open_browser():
    os.startfile("http://localhost:5000/")

def toast(message):
    wintoaster = WindowsToaster('SempRecord')
    newToast = ToastText1()
    newToast.SetBody(message)
    wintoaster.show_toast(newToast)
    
# Create a menu with a Start/Stop and pause option
# as well as the option to open a specific folder in the file explorer
# and one that opens the management page in the browser
def start():
    name = recorder.start()
    TRAY.icon = ICONS.active
    TRAY.menu = generate_menu(recording=True)
    TRAY.title = "SempRecord - Recording"
    toast('🔴 Record started | '+name)


def stop():
    TRAY.icon = ICONS.rendering
    name = recorder.stop()
    if settings.USE_AUTOTRIGGER:
        TRAY.icon = ICONS.standby
    else:
        TRAY.icon = ICONS.inactive
    
    TRAY.menu = generate_menu(recording=False)
    TRAY.title = "SempRecord - Stopped"
    toast('💾 Record saved | '+name)


def pause():
    recorder.pause()
    TRAY.icon = ICONS.paused
    TRAY.menu = generate_menu(recording=True, paused=True)
    TRAY.title = "SempRecord - Paused"
    toast('🟡 Recording paused')


def flip_auto_trigger(icon, item):
    state = not item.checked
    settings.USE_AUTOTRIGGER = state
    if state:
        TRAY.icon = ICONS.standby if not recorder.is_recording() else ICONS.active
        trigger.enable()
    else:
        TRAY.icon = ICONS.inactive if not recorder.is_recording() else ICONS.active
        trigger.disable()
 
def flip_run_on_boot(icon, item):
    state = not item.checked
    settings.RUN_ON_BOOT = state
    if state:
        run_on_boot.enable()
    else:
        run_on_boot.disable()


def generate_menu(recording=False, paused=False):
    menu_items = []
    if paused:
        menu_items.append(pystray.MenuItem("Resume", start, enabled=True))
    else:
        menu_items.extend([
            pystray.MenuItem("Start", start, enabled=not recording),
            pystray.MenuItem("Pause", pause, enabled=recording),
            pystray.MenuItem("Stop", stop, enabled=recording),
            ])
    
    menu_items.extend([
    pystray.MenuItem("Auto Trigger", flip_auto_trigger, checked=lambda _:settings.USE_AUTOTRIGGER),
    pystray.MenuItem("Run on boot", flip_run_on_boot, checked=lambda _:settings.RUN_ON_BOOT),
    pystray.MenuItem("Open Folder", open_folder),
    pystray.MenuItem("Open Interface", open_browser),
    pystray.MenuItem("Exit", exit_program)
    ])

    return pystray.Menu(*menu_items)


MENU = generate_menu()
icon = ICONS.standby if settings.USE_AUTOTRIGGER else ICONS.inactive
TRAY = pystray.Icon(
    icon=icon, menu=MENU, title="SempRecord", name="SempRecord"
)
TRAY.run_detached()


def tray_status_thread():
    """
    Continuously updates the title of the system tray icon with the current status of the recorder.

    The function retrieves the status of the recorder every 10 seconds and extracts the following keys:
    "frame", "size", "time", and "bitrate". If any of these keys are missing, the function skips the update.
    Otherwise, it constructs a string with the values of these keys separated by newlines and sets it as the
    title of the system tray icon.

    This function runs indefinitely until the program is terminated.
    """
    while True:
        sleep(10)
        if not recorder.is_recording():
            continue

        status = recorder.RECORDER.get_status()
        # try to collect the following the following keys: frame, size, time, bitrate
        try:
            frames = status["frame"]
            size = status["size"]
            time = status["time"]
            bitrate = status["bitrate"]
        except KeyError:
            continue
        # use newlines to separate the values
        title = f"Frames: {frames}\nSize: {size}\nTime: {time}\nBitrate: {bitrate}"
        TRAY.title = title


status_thread = Thread(
    target=tray_status_thread, daemon=True, name="Tray update status"
).start()


if __name__ == "__main__":
    # iterate through the various states of the recorder
    from time import sleep

    for icon in dir(ICONS):
        if icon.startswith("_"):
            continue
        TRAY.icon = getattr(ICONS, icon)
        sleep(2)
