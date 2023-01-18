import numpy as np

import ffmpeg
import config
import qoi
class Bardcoder:
    def __init__(self):
        self.width, self.height = config.THUMBNAIL_RES
        self.interval = config.THUMBNAIL_REDUCTION
        
        self.column_buffer = []
        self.finished_barcodes = 0
        self.hindex = 0

        self.qoicache = config.get_recording_dir() / ".cache"
        
        
    def process_frame(self, frame: np.ndarray) -> int:
        """Process a single frame of video and if the barcode is complete, return the number of barcodes in the buffer. Otherwise, return 0."""
        # ------TUMBNAIL_BARCODE------

        # select a single column of pixels at self.index
        column = frame[:,self.hindex]
        # sample the column every 8 pixels
        column = column[::self.interval]
        self.column_buffer.append(column)
        # sets the index for the next column
    
        # if the column buffer is full, merge it into the complete barcode
        if len(self.column_buffer) >= self.width:
            self.hindex = 0 # prepare for the next barcode
            # merge the column_buffer into the complete bars
            barcode = np.stack(self.column_buffer, axis=1)
            # clear the buffer
            self.column_buffer.clear()
            # save the barcode as a qoi file
            filename = f"{self.finished_barcodes}.qoi"
            path = self.qoicache / filename
            qoi.write(path, barcode)
            self.finished_barcodes += 1
            print(f"Thumbnail frame {self.finished_barcodes} saved")
            return self.finished_barcodes

        self.hindex += self.interval
    

    def render_webp_thumbnail(self, filename: str):
        """Save the qoi sequence as a webp animation."""

        # convert the barcodes to webp (use direct file writing)
        process = (
            ffmpeg
            .input("pipe:", format="rawvideo", pix_fmt="rgb24", s=f"{self.width}x{self.height}",r=3)
            .output(filename, pix_fmt="yuv420p", vcodec="libwebp",r=3,preset="text",compression_level=6,loop=0)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
        # write the barcodes to the pipe
        for i in range(self.finished_barcodes):
            f = self.qoicache / f"{i}.qoi"
            data = qoi.read(f)
            process.stdin.write(data.tobytes())
            f.unlink() # delete the qoi file
            
        # close the pipe
        process.stdin.close()
        process.wait()
