import os
import threading as tr
from time import sleep

import dxcam
import ffmpeg

import bouncer
import util
from filename_generator import generate_filename
import settings
from thumbnailer import ThumbnailProcessor
import numpy as np
CODEC = "hevc_nvenc" if util.nvenc_available() else "libx265"
FFPATH = r".\ffmpeg.exe"

def mkv_encoder(width, height, path):
    return (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                r=settings.FRAME_RATE,
                pix_fmt="rgb24",
                s=f"{width}x{height}",
            )
            .output(
                str(path),
                r=settings.FRAME_RATE,
                vcodec=CODEC,
                cq=settings.QUALITY,
                preset="p5",
                tune="hq",
                weighted_pred=1,
                pix_fmt="yuv444p",
                movflags="faststart",
                color_primaries="bt709",  # sRGB uses BT.709 primaries
                color_trc="iec61966-2-1",  # sRGB transfer characteristics
                colorspace="bt709",  # sRGB uses BT.709 colorspace
                color_range="pc"  # Set color range to full
            )
            .run_async(pipe_stdin=True, pipe_stderr=True)
        )
    

def frameDiff(A:np.ndarray, B:np.ndarray):
    # sample the frame at half the resolution
    A = A[::2, ::2]
    B = B[::2, ::2]

    # summ the whole frame into one value
    diff = np.sum(A != B)
    return diff


class Recorder:
    """Allows for continuous writing to a video file"""

    def __init__(self):
        """Starts the recording process"""

        self.window_title = ""
        self.nframes = 0
        # generate a file name that looks like this: Wednesday 18 January 2023 HH;MM.mkv
        self.file_name = generate_filename()

        # create a metadata file we can append to with simple frame:window_title pairs
        self.metadata_file = settings.HOME_DIR / ".metadata" / f"{self.file_name}.tsv"
        self.metadata_file.touch()
        self.metadata_file = open(self.metadata_file, "a")
        self.thumbnail_generator = ThumbnailProcessor(self.file_name)

        self.path = settings.HOME_DIR / "Records" / f"{self.file_name}.mkv"
        self.paused = False
        self.cut = False
        # start ffmpeg
        w, h = util.get_desktop_resolution()
        self.ffprocess = mkv_encoder(w, h, self.path)

        # launch threads
        self.end_record_flag = tr.Event()
        self.record_thread = tr.Thread(
            target=self._record_thread, name="Recording Thread"
        )

        self.end_status_flag = tr.Event()
        self.status_thread = tr.Thread(
            target=self._status_thread, name="Status Thread", daemon=True
        )

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
            if frameDiff(new_frame, old_frame) < settings.CHANGE_THRESHOLD:
                continue
            # add the frame to the thumbnail generator
            self.thumbnail_generator.queue.put(new_frame)

            # Flush the frame to FFmpeg
            try:
                self.ffprocess.stdin.write(old_frame.tobytes())  # write to pipe
                old_frame = new_frame
                self.nframes += 1
            except os.error:
                break

        self.ffprocess.stdin.close()
        self.ffprocess.wait()
        cam.stop()
        print("FFmpeg process ended")

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
REC: Recorder = None


def is_recording() -> bool:
    """Check if recording is currently active."""
    if REC is None:
        return False
    if REC.cut:
        return False
    return True


def start() -> str:
    """Start or resume recording."""
    global REC
    if not is_recording():
        # Make a new recorder
        REC = Recorder()
        print("Started recording")
        return REC.file_name

    if REC.paused:
        REC.paused = False
        print("Resumed recording")


def stop() -> str:
    """Stop the recording if it is active."""
    global REC
    if not is_recording():
        return
    REC.end_recording()
    filename = REC.file_name
    print("Stopped recording")
    REC = None
    return filename


def pause() -> None:
    """Pause the recording if it is active."""
    global REC
    if not is_recording():
        return
    REC.paused = True
    print("Paused recording")


if __name__ == "__main__":
    REC = Recorder()
    input("Press enter to stop recording")
    REC.end_recording()
