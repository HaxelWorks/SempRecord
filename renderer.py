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
        for i in range(0, len(listed) - 1, 2):
            status[listed[i]] = listed[i + 1]
        return status