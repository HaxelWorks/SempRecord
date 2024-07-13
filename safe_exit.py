import win32api
import win32con
import os
import tray
def wndProc(hWnd, message, wParam, lParam):
    if message == win32con.WM_QUERYENDSESSION:
        print('\a System shutdown or user logoff detected!')
        tray.exit_program()
    return True

win32api.SetConsoleCtrlHandler(wndProc, True)