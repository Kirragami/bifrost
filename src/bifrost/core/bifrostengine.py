import subprocess
import os
import atexit
import time
import socket
import signal
from config import settings
from pathlib import Path

class BifrostEngine:
    def __init__(self):
        # please please take this out to settings.py later :'))
        self.binary_path = (Path(__file__).resolve().parents[3] / "assets" / "OpenRGB.AppImage")
        self.host = '127.0.0.1'
        self.port = settings.PORT_RANGE_START
        self.process = None

        atexit.register(self.stop)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    
    def start(self):
        if self.is_running():
            return
        # Try until a port is available for instant startup
        while not self._attempt_start_on_current_port():
            if self.port == settings.PORT_RANGE_END:
                self.port = settings.PORT_RANGE_START
            else:
                self.port += 1
            print(f"[Engine] Port {self.port-1} failed, trying {self.port}...")        
        print((f"[Engine] Successfully started on port {self.port}"))

    def _attempt_start_on_current_port(self):
        self.process = subprocess.Popen(
            [str(self.binary_path), "--server", "--server-port", str(self.port)],
            start_new_session=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        start_poll = time.time()
        timeout = 2.0
        
        while time.time() - start_poll < timeout:
            if self.process.poll() is not None:
                output = self.process.stdout.read()
                if "Could not bind" in output:
                    return False
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', self.port)) == 0:
                    return True
            time.sleep(0.1)

        return False
    
    def restart(self):
        self.stop()
        self.start()

    def stop(self, *args):
        if self.process and self.process.poll() is None:
            try:
                pgid = os.getpgid(self.process.pid)
                os.killpg(pgid, signal.SIGKILL) 
                self.process.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    os.killpg(os.getpgid(self.process.pid), 9)
                    self.process.wait()
                except OSError:
                    pass
            finally:
                self.process = None

    def _signal_handler(self, signum, frame):
        self.stop()
        exit(0)
    
    def is_running(self):
        return self.process and self.process.poll() is None