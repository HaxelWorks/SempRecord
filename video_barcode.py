import numpy as np
import ffmpeg
import config

class Bardcoder:
    def __init__(self,):
        self.width, self.height = config.THUMBNAIL_RES
        self.interval = config.THUMBNAIL_REDUCTION
        
        self.column_buffer = []
        self.finished_barcodes = []
        self.hindex = 0

    def process_frame(self, frame: np.ndarray) -> int:
        """Process a single frame of video and if the barcode is complete, return the number of barcodes in the buffer. Otherwise, return 0."""
        # ------TUMBNAIL_BARCODE------

        # select a single column of pixels at self.index
        column = frame[:,self.hindex]
        # sample the column every 8 pixels
        column = column[::self.interval]
        
        self.column_buffer.append(column)
        # if the column buffer is full, merge it into the complete barcode

        if len(self.column_buffer) >= self.width:
            # merge the column_buffer into the complete bars
            barcode = np.stack(self.column_buffer, axis=1)

            # clear the buffer
            self.column_buffer.clear()
            # add the barcode to the finished barcodes
            self.finished_barcodes.append(barcode)
            self.hindex = 0
            return len(self.finished_barcodes)
        else:
            self.hindex += self.interval
            return 0


    def render_webp_thumbnail(self, filename: str):
        """Render the barcode as a webp animation using ffmpeg.

        """
        # ------WEBP_BARCODE------
        
        # convert the barcodes to webp (use direct file writing)
        process = (
            ffmpeg
            .input("pipe:", format="rawvideo", pix_fmt="rgb24", s=f"{self.width}x{self.height}",r=2)
            .output(filename, pix_fmt="yuv420p", vcodec="libwebp",r=2,preset="text",compression_level=6,loop=0)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
        # write the barcodes to the pipe
        for barcode in self.finished_barcodes:
            process.stdin.write(barcode.tobytes())
        # close the pipe
        process.stdin.close()
        process.wait()
