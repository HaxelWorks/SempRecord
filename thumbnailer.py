import PIL
import numpy as np
import ffmpeg
import config
import qoi

from queue import Queue
from threading import Thread, Event


class ThumbnailProcessor:
    def __init__(self, file_name: str):
        """Create a thumbnail for the given file name."""
        self.frames_to_skip = config.INPUT_FPS * config.THUMBNAIL_INTERVAL
        self.width, self.height = config.THUMBNAIL_RES

        self.saved_frames = 0
        self.fragments = 0
        self.queue = Queue()
        self.qoi_cache_path = config.get_recording_dir() / ".cache"
        self.thumb_path = (
            config.get_recording_dir() / ".thumbnails" / f"{file_name}.webp"
        )

        self.stop = Event()
        self.writer_thread = Thread(
            target=self.writer, name="Thumbnail Writer Thread", daemon=True
        )
        self.writer_thread.start()

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
        """Retrieve frames from the queue and save them to the qoi cache, discarding specified number of frames."""
        while not self.stop.is_set():
            # Record 1 second of frames
            for i in range(config.OUTPUT_FPS):
                frame = self.queue.get()
                frame = self.save_frame(frame)
            # Discard the next n seconds of frames
            for i in range(self.frames_to_skip):
                self.queue.get()  # discard frames
            self.fragments += 1

    def render_webp_thumbnail(self):
        """Save the qoi sequence as a webp animation."""
        self.stop.set()

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
                r=config.OUTPUT_FPS,
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
