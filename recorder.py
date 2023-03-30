import os
import threading
from collections import Counter
from time import sleep
import pathlib
from shutil import move
import PIL
import dxcam
import ffmpeg
import numpy as np
import datetime
import settings
from thumbnailer import ThumbnailProcessor
import subprocess
from util import nvenc_available, getForegroundWindowTitle, isTriggerlisted, isBlacklisted

CODEC = "h264_nvenc" if nvenc_available() else "libx264"
CHANGE_THRESHOLD = 10_000  #sub-pixels
FFPATH = r".\ffmpeg.exe"

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
        self.window_title = ''
        self.nframes = 0
        # generate a file name that looks like this: Wednesday 18 January 2023 HH;MM.mp4 
        self.file_name = datetime.datetime.now().strftime("%A %d %B %Y %H;%M")
        if tag: self.file_name = f"{tag} - {self.file_name}"
        
        # create a metadata file we can append to with simple frame:window_title pairs
        self.metadata_file = settings.RECORDING_DIR / ".metadata" / f"{self.file_name}.tsv"
        self.metadata_file.touch()
        self.metadata_file = open(self.metadata_file,'a')
        self.thumbnail_generator = ThumbnailProcessor(self.file_name)
        
        self.path = settings.RECORDING_DIR / f"{self.file_name}.mp4"
        self.paused = False
        self.stop = threading.Event()
        
        # start ffmpeg
        w,h = settings.DISPLAY_RES
        self.ffprocess =(
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
                s=f"{w}x{h}",
            )
            .output(
                str(self.path),
                r=settings.OUTPUT_FPS,
                vcodec=CODEC,
                bitrate="2000k",
                minrate="750k",
                maxrate="2500k",
                bufsize="2000k",
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
        self.status_thread = threading.Thread(target=self._status_thread, name="Status Thread", daemon=True)
        self.record_thread.start()
        self.status_thread.start()

    def recording_thread(self):
        cam = dxcam.create()
        cam.start(target_fps=settings.INPUT_FPS)
        last_frame = cam.get_latest_frame()
        
        while not self.stop.is_set():
            frame = cam.get_latest_frame()    
            if self.paused:
                last_frame = frame
                continue
            
            window_title = getForegroundWindowTitle()
            if window_title != self.window_title:
                self.window_title = window_title
                self.metadata_file.write(f"{self.nframes}\t{window_title}\n")
            
            
            if isBlacklisted(window_title):
                continue
            if frameDiff(frame, last_frame) < CHANGE_THRESHOLD:
                continue
            # add the frame to the thumbnail generator
            self.thumbnail_generator.queue.put(frame)
            
            # Flush the frame to FFmpeg       
            self.ffprocess.stdin.write(frame.tobytes()) # write to pipe
            last_frame = frame
            self.nframes +=1  
        cam.stop()
        self.ffprocess.stdin.close()
        self.ffprocess.wait()
         
    def _status_thread(self):
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
        self.metadata_file.close()
        self.thumbnail_generator.render_webp_thumbnail()

# ==========INTERFACE==========
RECORDER:Recorder = None
def start():
    global RECORDER
    if RECORDER is None: 
        RECORDER = Recorder(verbose=False)
        print("Started recording")
    if RECORDER.paused:
        RECORDER.paused = False
        print("Resumed recording")
    
def stop():
    global RECORDER
    if RECORDER is None:
        return
    RECORDER.end_recording()
    RECORDER = None
    print("Stopped recording")
def pause():
    global RECORDER
    if RECORDER is None:
        return
    RECORDER.paused = True
    print("Paused recording")
  
if __name__	== "__main__":
    RECORDER = Recorder("debug",verbose=True)
    input("Press enter to stop recording")
    RECORDER.end_recording()