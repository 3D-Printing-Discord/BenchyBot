import sys
import datetime

OUTPUT_FILE = "logfile.log"

class Logger(object):
    def __init__(self, *args):
        self.outputs = args

    def write(self, message):
        for o in self.outputs:
            o.write(f"{message}")
            o.flush()

    def flush(self):
        for o in self.outputs:
            o.flush()

sys.stdout = Logger(sys.stdout, open(OUTPUT_FILE, "a"))
sys.stderr = Logger(sys.stderr, open(OUTPUT_FILE, "a"), open("errorfile.log", "a"))

print(f" - Now logging to {OUTPUT_FILE} - ")