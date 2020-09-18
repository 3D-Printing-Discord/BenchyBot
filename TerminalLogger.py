import sys


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


def start(OUTPUT_FILE='logfile.log', ERROR_FILE='errorfile.log'):
    sys.stdout = Logger(
        sys.stdout,
        open(OUTPUT_FILE, "a")
        )

    sys.stderr = Logger(
        sys.stderr,
        open(OUTPUT_FILE, "a"),
        open(ERROR_FILE, "a")
        )

    print(f"[!] Now logging to {OUTPUT_FILE}, errors ")
