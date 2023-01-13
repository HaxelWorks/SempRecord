import os
import threading
from collections import Counter
from ctypes import create_unicode_buffer, windll
from time import sleep
from typing import Optional
import pathlib
from shutil import move
import PIL

import dxcam
import ffmpeg
import numpy as np

from config import config, get_recording_dir
from video_barcode import Bardcoder
# USER CHANGEABLE 
RECORDING_FOLDER = get_recording_dir()
VID_WIDTH = 2560
VID_HEIGHT = 1440
CODEC = "libx264" 
CODEC = "h264_nvenc"
FPS_TARGET = 15
SPEED_MULTIPLIER = 4

# DO NOT CHANGE
CHANGE_THRESHOLD = 3000  #sub-pixels
THUMB_W = 320
THUMB_H = VID_HEIGHT//8


# Helper functions
def isBlacklisted(app_name: str) -> bool:
    """Returns True if the app is blacklisted or no focus is on an app."""	
    if not app_name:
        return True
    for excl in config.get("BLACKLISTED_APPS"):
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
    def __init__(self,file_name="temp",debug=False):
        """Starts the recording process"""
        FILE_FPS = FPS_TARGET * SPEED_MULTIPLIER
        # use ffmpeg pipe in
        self.file_name = file_name
        self.path = RECORDING_FOLDER / f"{file_name}.mp4"
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
                self.file_name+".mp4",
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
        
        self.debug = debug
        self.bardcoder = Bardcoder(2560,1440)

       
    def recording_thread(self):
        cam = dxcam.create()
        cam.start(target_fps=FPS_TARGET)
        last_frame = cam.get_latest_frame()
        
        while not self.stop.is_set():
            frame = cam.get_latest_frame()    
            if self.paused:
                last_frame = frame
                continue
            
            window_title = getForegroundWindowTitle()
            if isBlacklisted(window_title):
                continue
            if frameDiff(frame, last_frame) < CHANGE_THRESHOLD:
                continue
           
            i = self.bardcoder.process_frame(frame)
            if i:
                print(i)
            
        
            # Flush the frame to FFmpeg       
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
                if self.debug:
                    print(self.status)
                
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
              
    def end_recording(self):
        self.stop.set()
        
        # ------TUMBNAIL_BARCODE------
        array = self.bardcoder.stack_barcodes()
        # save the image using PIL
        img = PIL.Image.fromarray(array)
        # save the image to the current directory
        img.save(self.file_name+".png")
        
        
        self.status_thread.join()   
        self.record_thread.join()


# ==========INTERFACE==========
RECORDER:Recorder = None
def start():
    global RECORDER
    if RECORDER is None: 
        RECORDER = Recorder(debug=True)
    if RECORDER.paused:
        RECORDER.paused = False
    
def stop():
    global RECORDER
    if RECORDER is None:
        return
    RECORDER.end_recording()
    RECORDER = None
def pause():
    global RECORDER
    if RECORDER is None:
        return
    RECORDER.paused = True
  
if __name__	== "__main__":
    RECORDER = Recorder("debug",debug=True)
    input("Press enter to stop recording")
    RECORDER.end_recording()