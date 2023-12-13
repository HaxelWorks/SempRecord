from queue import Queue
import threading
from time import sleep

import dxcam
import ffmpeg
import qoi

import util
from filename_generator import generate_filename
from settings import settings


CODEC = "hevc_nvenc" if util.nvenc_available() else "libx264"
CHANGE_THRESHOLD = 3000  # sub-pixels
FFPATH = r".\ffmpeg.exe"


def frameDiff(frame1, frame2):
    diff = frame1 != frame2
    # summ the whole frame into one value
    diff = diff.sum()
    return diff


class Recorder:
    """Allows for continuous writing to a video file"""

    def __init__(self, verbose=True):
        """Starts the recording process"""
        self.debug = verbose
        self.window_title = ""
        self.nframes = 0
        # generate a file name that looks like this: Wednesday 18 January 2023 HH;MM.mp4
        self.file_name = generate_filename()

        # create a metadata file we can append to with simple frame:window_title pairs
        self.metadata_file = settings.HOME_DIR / ".metadata" / f"{self.file_name}.tsv"
        self.metadata_file.touch()
        self.metadata_file = open(self.metadata_file, "a")
        
        #  make the qoi cache directory
        self.cache_dir = settings.HOME_DIR / ".cache" / f"{self.file_name}"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.write_queue = Queue(maxsize=10)
        
    
        self.paused = False
        self.stop = threading.Event()

        w, h = util.get_desktop_resolution()


        # launch threads
        
        self.record_thread = threading.Thread(
            target=self.recording_thread, name="Recording Thread"
        )
        self.record_thread.start()
        
        self.writer_thread = threading.Thread(
            target=self.writer_thread, name="QOI encoder"
        )
        self.writer_thread.start()
        
    def recording_thread(self):
        cam = dxcam.create()
        cam.start(target_fps=settings.FRAME_RATE)
        old_frame = cam.get_latest_frame()

        while not self.stop.is_set():
            new_frame = cam.get_latest_frame()
            if self.paused:
                old_frame = new_frame
                continue

            window_title = util.getForegroundWindowTitle()
            if window_title != self.window_title:
                self.window_title = window_title
                self.metadata_file.write(f"{self.nframes}\t{window_title}\n")

            if not util.isWhiteListed(window_title):
                continue
            if frameDiff(new_frame, old_frame) < CHANGE_THRESHOLD:
                continue
                        
            # write the frame as a qoi file
            self.write_queue.put(new_frame)
            

            old_frame = new_frame
            self.nframes += 1

        cam.stop()
        self.ffprocess.stdin.close()
        self.ffprocess.wait()

    def writer_thread(self):
        """Becomes a thread that listens to the queue and saves the frames to the qoi cache"""
        n = 0
        while (frame := self.write_queue.get()) is not None:
            path = self.cache_dir / f"{n}.qoi"
            qoi.write(path, frame)
            n += 1
            
            if n % 100 == 0:
                print(f"Saved {n} frames")
                print(f"Queue size: {self.write_queue.qsize()}")
            


    def end_recording(self):
        self.stop.set()
        self.metadata_file.close()
        # self.thumbnail_generator.render_webp_thumbnail()
        # join the recoding and status threads
        self.record_thread.join()


# ==========INTERFACE==========
RECORDER: Recorder = None


def is_recording():
    return RECORDER is not None


def start():
    global RECORDER
    if not is_recording():
        # Make a new recorder
        RECORDER = Recorder(verbose=False)
        print("Started recording")
        return RECORDER.file_name

    if RECORDER.paused:
        RECORDER.paused = False
        print("Resumed recording")


def stop():
    global RECORDER
    if not is_recording():
        return
    RECORDER.end_recording()
    filename = RECORDER.file_name
    RECORDER = None
    print("Stopped recording")
    return filename


def pause():
    global RECORDER
    if not is_recording():
        return
    RECORDER.paused = True
    print("Paused recording")


if __name__ == "__main__":
    RECORDER = Recorder("debug", verbose=True)
    input("Press enter to stop recording")
    RECORDER.end_recording()
