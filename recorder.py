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
import datetime

import config
from thumbnailer import ThumbnailProcessor
 
CODEC = "libx264" 
CODEC = "h264_nvenc"
CHANGE_THRESHOLD = 4000  #sub-pixels

# Helper functions
def isBlacklisted(app_name: str) -> bool:
    """Returns True if the app is blacklisted or no focus is on an app."""	
    if not app_name:
        return True
    for excl in config.BLACKLISTED_APPS:
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
    def __init__(self,tag='',verbose=False):
        """Starts the recording process"""
        self.debug = verbose
        
        # generate a file name that looks like this: Wednesday 18 January 2023 HH;MM.mp4 
        self.file_name = datetime.datetime.now().strftime("%A %d %B %Y %H;%M")
        if tag: self.file_name = f"{tag} - {self.file_name}"
        
        self.thumbnail_generator = ThumbnailProcessor(self.file_name)
        
        self.path = config.get_recording_dir() / f"{self.file_name}.mp4"
        self.paused = False
        self.stop = threading.Event()
        
        # start ffmpeg
        w,h = config.DISPLAY_RES
        self.ffprocess = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
                s=f"{w}x{h}",
            )
            .output(
                str(self.path),
                r=config.OUTPUT_FPS,
                vcodec=CODEC,
                bitrate="1500k",
                minrate="500k",
                maxrate="3000k",
                bufsize="1500k",
                preset="slow",
                temporal_aq=1,
                pix_fmt="yuv420p",
                movflags="faststart",  
            )
            .overwrite_output()
            .run_async(pipe_stdin=True,pipe_stderr=True)
        )
        # launch threads
        self.record_thread = threading.Thread(target=self.recording_thread, name="Recording Thread", daemon=True)
        self.status_thread = threading.Thread(target=self.status_thread, name="Status Thread", daemon=True)
        self.record_thread.start()
        self.status_thread.start()
        

    def recording_thread(self):
        cam = dxcam.create()
        cam.start(target_fps=config.INPUT_FPS)
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
            # add the frame to the thumbnail generator
            self.thumbnail_generator.queue.put(frame)
            
            # Flush the frame to FFmpeg       
            self.ffprocess.stdin.write(frame.tobytes()) # write to pipe
            last_frame = frame
              
        cam.stop()
        self.ffprocess.stdin.close()
        self.ffprocess.wait()
         
    def status_thread(self):
        self.status = ""
        buffer = b""
        while not self.stop.is_set():
            # we'd like to use readline but using \r as the delimiter
            new_stat = self.ffprocess.stderr.read1()
            # split the status into lines
            new_stat = new_stat.split(b"\r")
            buffer += new_stat[0]
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
        self.status_thread.join()   
        self.record_thread.join()
        self.thumbnail_generator.render_webp_thumbnail()


# ==========INTERFACE==========
RECORDER:Recorder = None
def start():
    global RECORDER
    if RECORDER is None: 
        RECORDER = Recorder(verbose=True)
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
    RECORDER = Recorder("debug",verbose=True)
    input("Press enter to stop recording")
    RECORDER.end_recording()