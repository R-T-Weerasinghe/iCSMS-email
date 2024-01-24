from threading import Timer
from backend.Email.new_emails import identify_new_emails

# https://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds
class RepeatedTimer(object):
    """
    Timer class that executes a function every N seconds. Call start() to start and stop() to stop.
    """
    def __init__(self, intervalInSeconds, function, *args, **kwargs):
        self._timer = None
        self.interval = intervalInSeconds
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self._timer:
            self._timer.cancel()
        self.is_running = False


def polling():
    """Polls the email server for new emails."""
    print("Polling started.")
    rt = RepeatedTimer(60, identify_new_emails)
    try:
        while(True):
            pass
    finally:
        rt.stop()

if __name__ == "__main__":
    print("Run main.py")