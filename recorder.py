import pprint
import threading
from ctypes import create_unicode_buffer, windll
from typing import Optional

import dxcam
import ffmpeg
import numpy as np
from time import sleep


# Config
EXCLUDED_APPS = ["Google Chrome","WhatsApp","Messenger","Discord",]
AUTO_START = ["Visual Studio Code"]
FPS_TARGET = 15
SPEED_MULTIPLIER = 4
CHANGE_THRESHOLD = 400  # pixels
VID_HEIGHT = 1440
VID_WIDTH = 2560
CODEC = "libx264"
CODEC = "h264_nvenc"

# Helper functions
def isBlacklisted(app_name: str) -> bool:
    """Returns True if the app is blacklisted or no focus is on an app."""	
    if not app_name:
        return True
    for excl in EXCLUDED_APPS:
        if app_name.endswith(excl):
            return True
    return False 

def getForegroundWindowTitle() -> Optional[str]:
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    return buf.value if buf.value else None

def frameDiff(frame1, frame2):
    diff = frame1 != frame2
    # summ the whole frame into one value
    diff = diff.sum()
    return diff

class Recorder:
    """Allows for continuous writing to a video file"""
    def __init__(self,file_name:str):
        """Starts the recording process"""
        FILE_FPS = FPS_TARGET * SPEED_MULTIPLIER
        # use ffmpeg pipe in
        self.paused = False
        self.stop = threading.Event()
        self.process = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
                s=f"{VID_WIDTH}x{VID_HEIGHT}",
            )
            
            .output(
                f"{file_name}.mp4",
                r=FILE_FPS,
                vcodec=CODEC,
                bitrate="1600k",
                minrate="400k",
                maxrate="4000k",
                bufsize="8m",
                preset="slow",
                temporal_aq=1,
                pix_fmt="yuv420p",
                movflags="faststart",  
            )
            .overwrite_output()
            .run_async(pipe_stdin=True,pipe_stderr=True)
        )
        self.record_thread = threading.Thread(target=self.recording_thread, name="Recording Thread", daemon=True)
        self.record_thread.start()
        self.status_thread = threading.Thread(target=self.status_thread, name="Status Thread", daemon=True)
        self.status_thread.start()
        
    def recording_thread(self):
        cam = dxcam.create()
        cam.start(target_fps=FPS_TARGET)
        last_frame = cam.get_latest_frame()
        
        while not self.stop.is_set():
            frame = cam.get_latest_frame()    
            window = getForegroundWindowTitle()
            
            if self.paused:
                last_frame = frame
                continue
            if isBlacklisted(window):
                continue
            if frameDiff(frame, last_frame) < CHANGE_THRESHOLD:
                continue
            
            self.process.stdin.write(frame.astype(np.uint8).tobytes()) # write to pipe
            last_frame = frame
        cam.stop()
        self.process.stdin.close()
        self.process.wait()
        
    def status_thread(self):
        self.status = ""
        buffer = b""
        while not self.stop.is_set():
            # we'd like to use readline but using \r as the delimiter
            new_stat = self.process.stderr.read1()
            # split the status into lines
            new_stat = new_stat.split(b"\r")
            buffer+= new_stat[0]
            if len(new_stat) > 1:
                # if there is more than one line, the last line is the current status
                self.status = buffer.decode("utf-8").strip()
                # print(self.status)
                buffer = new_stat[-1]
            sleep(0.5)
      
    def get_status(self):
        # the self.status comes out as a string
        # frame=  513 fps= 40 q=39.0 size=    1536kB time=00:00:08.50 bitrate=1480.4kbits/s dup=320 drop=0 speed=0.668x
        # we want this as a dictionary
        raw_stat = self.status.split(sep="=")
        raw_stat = [x.strip() for x in raw_stat]
        listed = []
        for s in raw_stat:
            listed.extend(s.split())
        # pair up the values
        status = {}
        for i in range(0,len(listed)-1,2):
            status[listed[i]] = listed[i+1]
        return status
              
    def stop_recording(self):
        self.stop.set()
        
if __name__	== "__main__":
    recorder = Recorder("test")
    input("Press enter to stop recording")
    recorder.stop_recording()
    
    