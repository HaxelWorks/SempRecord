import sys
import logging
from logging.handlers import RotatingFileHandler

import settings
log_path = settings.HOME_DIR / ".logs" / "log.txt"
class PrintLogger(logging.Logger):
    def write(self, msg):
        if msg.rstrip() != "":
            stripped = msg.rstrip()
            self.info(stripped)
            
            
    def flush(self):
        for handler in self.handlers:
            handler.flush()
            
            
# Create a logging object using the custom class
log = PrintLogger(__name__)
log.setLevel(logging.DEBUG)

# Create a RotatingFileHandler that rotates log files
# when they reach a certain size, and keep a maximum
# of 3 backup log files
file_handler = RotatingFileHandler(log_path, maxBytes=20_000, backupCount=3)
file_handler.setLevel(logging.DEBUG)
log.addHandler(file_handler)

# Redirect stdout and stderr to the logging object
sys.stdout = sys.stderr = log

# Create a formatter that formats messages in the log file
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Now, any print statements or error messages will be logged to the rotating log file
