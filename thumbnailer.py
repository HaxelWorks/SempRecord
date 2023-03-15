import PIL
import numpy as np
import ffmpeg
import settings
import qoi

from queue import Queue
from threading import Thread


class ThumbnailProcessor:
    def __init__(self, file_name: str):
        """Create a thumbnail for the given file name."""
        self.frames_to_skip = settings.INPUT_FPS * settings.THUMBNAIL_INTERVAL
        self.width, self.height = settings.THUMBNAIL_RES

        self.saved_frames = 0
        self.fragments = 0
        self.queue = Queue()
        self.qoi_cache_path = settings.RECORDING_DIR / ".cache"
        self.thumb_path = (
            settings.RECORDING_DIR / ".thumbnails" / f"{file_name}.webp"
        )

        
        self.writer_thread = Thread(target=self.writer, name="QOI encoder")
        self.writer_thread.start()

    def keep_or_discard(self):
        """returns a generator that yields True or False, True if the frame should be kept, False if it should be discarded"""
        while True:
            for i in range(settings.OUTPUT_FPS):
                yield True
            for i in range(self.frames_to_skip):
                yield False

    def save_frame(self, frame: np.ndarray) -> int:
        """Save a frame to the qoi cache."""
        frame = PIL.Image.fromarray(frame)
        # reduce the size of the frame by 1/4
        frame = frame.resize((self.width, self.height), PIL.Image.LANCZOS)
        frame = np.array(frame)
        path = self.qoi_cache_path / f"{self.saved_frames}.qoi"
        qoi.write(path, frame)
        self.saved_frames += 1

    def writer(self):
        """Becomes a thread that listens to the queue and saves the frames to the qoi cache"""
        kod = self.keep_or_discard()
        while (frame := self.queue.get()) is not None:
            if next(kod):
                self.save_frame(frame)

    def render_webp_thumbnail(self):
        """Save the qoi sequence as a webp animation."""
        #wait fort the queue to be empty
        self.queue.put(None)  # send a stop signal to the writer thread
        self.writer_thread.join()  # wait for the writer thread to stop
        
        # convert the fragments to webp (use direct file writing)
        process = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
                s=f"{self.width}x{self.height}",
            )
            .output(
                str(self.thumb_path),
                pix_fmt="yuv420p",
                vcodec="libwebp",
                r=settings.OUTPUT_FPS,
                preset="text",
                compression_level=6,
                loop=0,
            )
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
        # write the fragments to the pipe
        for i in range(self.saved_frames):
            f = self.qoi_cache_path / f"{i}.qoi"
            data = qoi.read(f)
            process.stdin.write(data.tobytes())
            f.unlink()  # delete the qoi file

        # close the pipe
        process.stdin.close()
        process.wait()
