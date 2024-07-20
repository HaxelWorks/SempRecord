import threading as tr
from time import sleep

import dxcam
import ffmpeg

import bouncer
import util
from filename_generator import generate_filename
import settings
from thumbnailer import ThumbnailProcessor

CODEC = "hevc_nvenc" if util.nvenc_available() else "libx264"
CHANGE_THRESHOLD = 3000  # sub-pixels
FFPATH = r".\ffmpeg.exe"


def frameDiff(frame1, frame2):
    # sample the frame at 1/10th of the resolution
    # frame1 = frame1[::10, ::10]
    # frame2 = frame2[::10, ::10]
    
    diff = frame1 != frame2
    # summ the whole frame into one value
    return diff.sum()



class Recorder:
    """Allows for continuous writing to a video file"""

    def __init__(self):
        """Starts the recording process"""
        
        self.window_title = ""
        self.nframes = 0
        # generate a file name that looks like this: Wednesday 18 January 2023 HH;MM.mp4
        self.file_name = generate_filename()

        # create a metadata file we can append to with simple frame:window_title pairs
        self.metadata_file = settings.HOME_DIR / ".metadata" / f"{self.file_name}.tsv"
        self.metadata_file.touch()
        self.metadata_file = open(self.metadata_file, "a")
        self.thumbnail_generator = ThumbnailProcessor(self.file_name)

        self.path = settings.HOME_DIR / "Records" / f"{self.file_name}.mp4"
        self.paused = False
        self.cut = False
        # start ffmpeg
        w, h = util.get_desktop_resolution()
        self.ffprocess = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                r=settings.FRAME_RATE,
                pix_fmt="rgb24",
                s=f"{w}x{h}",
            )
            .output(
                str(self.path),
                r=settings.FRAME_RATE,
                vcodec=CODEC,
                cq=35,
                preset="p5",
                tune="hq",
                weighted_pred=1,
                pix_fmt="yuv420p",
                movflags="faststart",
            )
            .run_async(pipe_stdin=True, pipe_stderr=True)
        )

        # launch threads
        self.end_record_flag = tr.Event()
        self.record_thread = tr.Thread(
            target=self._record_thread, name="Recording Thread")

        self.end_status_flag = tr.Event()
        self.status_thread = tr.Thread(
            target=self._status_thread, name="Status Thread", daemon=True)

        self.record_thread.start()
        self.status_thread.start()

    def _record_thread(self):
        cam = dxcam.create()
        cam.start(target_fps=settings.FRAME_RATE)
        old_frame = cam.get_latest_frame()
        
        while not self.end_record_flag.is_set():

            new_frame = cam.get_latest_frame()
            if self.paused:
                old_frame = new_frame
                continue

            window_title = util.getForegroundWindowTitle()
            if window_title != self.window_title:
                self.window_title = window_title
                self.metadata_file.write(f"{self.nframes}\t{window_title}\n")

            if not bouncer.isWhiteListed(window_title):
                continue
            if bouncer.isBlackListed(window_title):
                continue
            if frameDiff(new_frame, old_frame) < CHANGE_THRESHOLD:
                continue
            # add the frame to the thumbnail generator
            self.thumbnail_generator.queue.put(new_frame)

            # Flush the frame to FFmpeg
            self.ffprocess.stdin.write(old_frame.tobytes())  # write to pipe
            old_frame = new_frame
            self.nframes += 1

        self.ffprocess.stdin.close()
        self.ffprocess.wait()
        cam.stop()
        print("FFmpeg process closed")
        
    def _status_thread(self):
        self.status = ""
        buffer = b""

        while not self.end_status_flag.is_set():
            new_stat = self.ffprocess.stderr.read1()
            
            # split the status into lines
            # we'd like to use readline but using \r as the delimiter
            new_stat = new_stat.split(b"\r")
            buffer += new_stat[0]
            if len(new_stat) > 1:
                # if there is more than one line, the last line is the current status
                self.status = buffer.decode("utf-8").strip()
                buffer = new_stat[-1]
    
        
    def get_status(self):
        if self.cut:
            return {}

        raw_stat = self.status.split(sep="=")
        raw_stat = [x.strip() for x in raw_stat]
        listed = []
        for s in raw_stat:
            listed.extend(s.split())
        # pair up the values
        status = {}
        for i in range(0, len(listed) - 1, 2):
            status[listed[i]] = listed[i + 1]
        return status

    def end_recording(self):
        self.cut = True
        
        # stop the status thread
        self.end_status_flag.set()
        self.end_record_flag.set()
        
        # process the thumbnail queue
        print("Processing thumbnail")
        self.thumbnail_generator.render_webp_thumbnail()
        self.metadata_file.close()

# ==========INTERFACE==========
RECORDER: Recorder = None


def is_recording():
    if RECORDER is None:
        return False
    if RECORDER.cut:
        return False
    return True
def start():
    global RECORDER
    if not is_recording():
        # Make a new recorder
        RECORDER = Recorder()
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
    print("Stopped recording")
    RECORDER = None
    return filename


def pause():
    global RECORDER
    if not is_recording():
        return
    RECORDER.paused = True
    print("Paused recording")


if __name__ == "__main__":
    RECORDER = Recorder()
    input("Press enter to stop recording")
    RECORDER.end_recording()
