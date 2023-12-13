import ctypes
import win32api
import win32con
import win32event
import win32gui
import tray
# Define the callback function for system shutdown events
def shutdown_handler(hwnd, msg, wparam, lparam):
    tray.exit_program()
    return True

# Register the callback function for system shutdown events
win32gui.InitCommonControls()
message_map = {win32con.WM_QUERYENDSESSION: shutdown_handler,
               win32con.WM_ENDSESSION: shutdown_handler}
wndclass = win32gui.WNDCLASS()
hinst = wndclass.hInstance = win32api.GetModuleHandle(None)
classname = 'MyAppShutdownHandler'
wndclass.lpszClassName = classname
atom = win32gui.RegisterClass(wndclass)
hwnd = win32gui.CreateWindow(classname, None, 0, 0, 0, 0, 0, 0, 0, hinst, None)

# Add the message map to the window
win32gui.PumpMessages()

