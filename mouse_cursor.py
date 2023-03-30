import ctypes

# Define the POINT structure from the Windows API
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def cursor_pos_generator():
    """ A generator function which returns the cursor position """
    cursor_pos = POINT()
    while True:
        # Call the GetCursorPos function to get the mouse cursor position
        ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor_pos))
        yield cursor_pos

if __name__  == "__main__":
    # Initialize the cursor_pos_generator	
    import time
    cursor_pos = cursor_pos_generator()
    while True:
        pos = next(cursor_pos)
        print(pos.x, pos.y)
        time.sleep(0.05)