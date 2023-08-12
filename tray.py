import os
from threading import Thread
from time import sleep

import pystray
from windows_toasts import ToastText1, WindowsToaster

import recorder
import run_on_boot
import settings
from icon_generator import ICONS


def toast(message):
    wintoaster = WindowsToaster('SempRecord')
    newToast = ToastText1()
    newToast.SetBody(message)
    newToast.on_activated = lambda _: print('Toast clicked!')
    wintoaster.show_toast(newToast)
    
# Create a menu with a Start/Stop and pause option
# as well as the option to open a specific folder in the file explorer
# and one that opens the management page in the browser
def start():
    recorder.start()
    TRAY.icon = ICONS.active
    TRAY.menu = generate_menu(recording=True)
    TRAY.title = "SempRecord - Recording"
    toast('🔴 Recording started')


def stop():
    TRAY.icon = ICONS.rendering
    recorder.stop()
    TRAY.icon = ICONS.standby if trigger_state else ICONS.inactive
    TRAY.menu = generate_menu(recording=False)
    TRAY.title = "SempRecord - Stopped"
    toast('🎬 Recording ended')


def pause():
    recorder.pause()
    TRAY.icon = ICONS.paused
    TRAY.menu = generate_menu(recording=True, paused=True)
    TRAY.title = "SempRecord - Paused"
    toast('🟡 Recording paused')
def exit_program():
    stop()
    TRAY.stop()
    # exit the program
    os._exit(0)
    

def open_folder():
    os.startfile(str(settings.RECORDING_DIR))


def open_browser():
    os.startfile("http://localhost:5000/")

trigger_state = False
def trigger_clicked(icon, item):
    global trigger_state
    trigger_state = not item.checked
    if trigger_state:
        TRAY.icon = ICONS.standby
    else:
        TRAY.icon = ICONS.inactive
 
def generate_menu(recording=False, paused=False):
    items = []
    if paused:
        items.append(pystray.MenuItem("Resume", start, enabled=True))
    else:
        controls = [
            pystray.MenuItem("Start", start, enabled=not recording),
            pystray.MenuItem("Pause", pause, enabled=recording),
            pystray.MenuItem("Stop", stop, enabled=recording),
            
        ]
        items.extend(controls)

    items.append(pystray.MenuItem("Auto Trigger", trigger_clicked, checked=lambda _:trigger_state))
    items.append(pystray.MenuItem("Open Folder", open_folder))
    items.append(pystray.MenuItem("Open Interface", open_browser))
    items.append(pystray.MenuItem("Exit", exit_program))
    # add a menu entry that shows a radio button if the program is set to autotrigger or not
    # when checked it should run run_on_boot.enable() and when unchecked it should run run_on_boot.disable()
    # the menu entry should be called "Autotrigger"
    return pystray.Menu(*items)


MENU = generate_menu()
TRAY = pystray.Icon(
    icon=ICONS.inactive, menu=MENU, title="SempRecord", name="SempRecord"
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
        if recorder.RECORDER is None:
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
