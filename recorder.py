import pprint
import threading
from ctypes import create_unicode_buffer, windll
from typing import Optional

import dxcam
import ffmpeg
import numpy as np
from time import sleep
from config import *


# Helper functions
def isBlacklisted(app_name: str) -> bool:
    """Returns True if the app is blacklisted or no focus is on an app."""	
    if not app_name:
        return True
    for excl in BLACKLISTED_APPS:
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
                bitrate="2000k",
                minrate="400k",
                maxrate="4000k",
                bufsize="4m",
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
        if self.stop.is_set():
            return {}

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



def start():
    global active_recorder
    active_recorder = Recorder("test")
    
def stop():
    global active_recorder
    active_recorder.stop_recording()
 
def pause():
    global active_recorder
    active_recorder.paused = True
  
def unpause():
    active_recorder = Recorder("test")

if __name__	== "__main__":
    input("Press enter to stop recording")
    active_recorder.stop_recording()
    
    