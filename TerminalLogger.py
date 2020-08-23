import sys
import datetime

OUTPUT_FILE = "logfile.log"

class Logger(object):
    def __init__(self, terminal, file):
        self.terminal = terminal
        self.log = open(file, "a")

    def write(self, message):
        self.terminal.write(f"{message}")
        self.log.write(f"{message}")
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger(sys.stdout, OUTPUT_FILE)
sys.stderr = Logger(sys.stderr, OUTPUT_FILE)

print(f" - Now logging to {OUTPUT_FILE} - ")