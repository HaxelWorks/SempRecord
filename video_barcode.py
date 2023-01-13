import numpy as np
class Bardcoder:
    def __init__(self,width:int,height:int,interval:int=4):
        self.width = width
        self.height = height
        self.interval = interval
        self.column_buffer = []
        self.finished_barcodes = []
        self.index = 0
    def process_frame(self, frame:np.ndarray) -> int:
        """ Process a single frame of video and if the barcode is complete, return the number of barcodes in the buffer. Otherwise, return 0."""
        # ------TUMBNAIL_BARCODE------
        # select a single column of pixels at self.index
        column = frame[:,self.index]
        # sample the column every 8 pixels
        column = column[::self.interval]
        
        self.column_buffer.append(column)
        # if the column buffer is full, merge it into the complete barcode
        
        if len(self.column_buffer) >= self.width//self.interval:
            # merge the column_buffer into the complete bars
            barcode = np.stack(self.column_buffer,axis=0)
            # clear the buffer
            self.column_buffer.clear()
            # add the barcode to the finished barcodes
            self.finished_barcodes.append(barcode)
            self.index = 0
            return len(self.finished_barcodes)
        else:
            self.index+=self.interval
            return 0
        
    def stack_barcodes(self):
        # concatenate the barcodes horizontally
        barcode = np.concatenate(self.finished_barcodes,axis=0)
        # rotate the barcode -90 degrees
        barcode = np.rot90(barcode,3)
        # mirror the barcode horizontally
        barcode = np.fliplr(barcode)
        return barcode