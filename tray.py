import pystray
import os
import recorder
from icon_generator import ICONS
from threading import Thread
from time import sleep

# Create a menu with a Start/Stop and pause option
# as well as the option to open a specific folder in the file explorer
# and one that opens the management page in the browser
def start():
    recorder.start()
    TRAY.icon = ICONS.active
    TRAY.menu = generate_menu(recording=True)
    TRAY.title = "SempRecord - Recording"


def stop():
    recorder.stop()
    TRAY.icon = ICONS.inactive
    TRAY.menu = generate_menu(recording=False)
    TRAY.title = "SempRecord - Stopped"


def pause():
    recorder.pause()
    TRAY.icon = ICONS.paused
    TRAY.menu = generate_menu(recording=True, paused=True)

def exit_program():
    stop()
    TRAY.stop()
    # exit the program
    os._exit(0)
    

def open_folder():
    os.startfile("C:\\Users\\Axel1\\Desktop\\SempRecord")  # TODO: make this dynamic


def open_browser():
    os.startfile("http://localhost:5000/")


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

    items.append(pystray.MenuItem("Open Folder", open_folder))
    items.append(pystray.MenuItem("Open Interface", open_browser))
    items.append(pystray.MenuItem("Exit", exit_program))

    return pystray.Menu(*items)


MENU = generate_menu()
TRAY = pystray.Icon(
    icon=ICONS.inactive, menu=MENU, title="SempRecord", name="SempRecord"
)
TRAY.run_detached()


def tray_status_thread():
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
