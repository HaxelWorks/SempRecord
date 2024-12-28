import sys
import time
import ctypes
import logging
import tkinter as tk
from tkinter import ttk

import win32con
import win32gui
import win32api


# NOTE: this is used in the root.mainloop() replacement at the bottom.
exit_requested = False
def quit():
    global exit_requested
    exit_requested = True


# Received when the user tries to close the window via X in the top right corner.
def close_window(*args, **kwargs):
    logging.info("WM_CLOSE received")
    quit()
    # 0 tells Windows the message has been handled
    return 0


# Received when the system is shutting down.
def end_session(*args, **kwargs):
    logging.info("WM_ENDSESSION received")
    quit()
    # Returning immediately lets Windows proceed with the shutdown.
    # You can run some shutdown code here, but there's a 5 seconds maximum timeout,
    # before your application is killed by Windows.
    return 0


# Received when the system is about to shutdown, but the user can
# cancel this action. Return 0 to tell the system to wait until
# the application exits first. No timeout.
def query_end_session(*args, **kwargs):
    logging.info("WM_QUERYENDSESSION received")
    quit()
    # 1 means you're ready to exit, and you'll receive a WM_ENDSESSION immediately afterwards.
    # 0 tells Windows to wait before proceeding with the shutdown.
    return 0


# Simple logging setup to catch all logging messages into a file.
file_handler = logging.FileHandler("shutdown_test.log", encoding="utf8")
file_handler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
logging.info("starting shutdown test")

# Start of your application code
root = tk.Tk()
root.title("Shutdown test")
main_frame = ttk.Frame(root, padding=20)
main_frame.grid(column=0, row=0)
ttk.Label(
    main_frame, text="Shutdown test in progress...", padding=50
).grid(column=0, row=0, sticky="nsew")
# End of your application code

# This is crucial - a root.update() after all application setup is done,
# is very needed here, otherwise Tk won't properly set itself up internally,
# leading to not being able to catch any messages later.
root.update()

# NOTE: These two lines below can be used for basic message handling instead.
# Return value from WM_SAVE_YOURSELF is ignored, so you're expected to
# finish all of the closing sequence before returning. Note that Windows will wait
# for you up to 5 seconds, and then proceed with the shutdown anyway.

# root.protocol("WM_DELETE_WINDOW", close_window)
# root.protocol("WM_SAVE_YOURSELF", query_end_session)

root_handle = int(root.wm_frame(), 16)
message_map = {
    win32con.WM_CLOSE: close_window,
    win32con.WM_ENDSESSION: end_session,
    win32con.WM_QUERYENDSESSION: query_end_session,
}


def wnd_proc(hwnd, msg, w_param, l_param):
    """
    This function serves as a message processor for all messages sent to your
    application by Windows.
    """
    if msg == win32con.WM_DESTROY:
        win32api.SetWindowLong(root_handle, win32con.GWL_WNDPROC, old_wnd_proc)
    if msg in message_map:
        return message_map[msg](w_param, l_param)
    return win32gui.CallWindowProc(old_wnd_proc, hwnd, msg, w_param, l_param)


# This hooks up the wnd_proc function as the message processor for the root window.
old_wnd_proc = win32gui.SetWindowLong(root_handle, win32con.GWL_WNDPROC, wnd_proc)
if old_wnd_proc == 0:
    raise NameError("wndProc override failed!")

# This works together with WM_QUERYENDSESSION to provide feedback to the user
# in terms of what's preventing the shutdown from proceeding.
# NOTE: It's sort-of optional. If you don't include it, Windows will use
# a generic message instead. However, your application can fail to receive
# a WM_QUERYENDSESSION if it's window is minimized (via iconify/withdraw)
# when the message happens - if you also need to be able to handle that case,
# then you'll need it.
retval = ctypes.windll.user32.ShutdownBlockReasonCreate(
    root_handle, ctypes.c_wchar_p("I'm still saving data!")
)
if retval == 0:
    raise NameError("shutdownBlockReasonCreate failed!")

# NOTE: this replaces root.mainloop() to allow for a loop exit
# without closing any windows - root.quit() apparently does so.
while not exit_requested:
    root.update()
    time.sleep(0.05)

# Your shutdown sequence goes here.
logging.info("shutdown start")
time.sleep(10)
logging.info("shutdown finished")
root.destroy()
sys.exit(0)