import subprocess
import os
import atexit
import time
import socket
from pathlib import Path

class BifrostEngine:
    def __init__(self):
        # please please take this out to settings.py later :'))
        self.binary_path = (Path(__file__).resolve().parents[3] / "assets" / "OpenRGB.AppImage")
        self.process = None
        atexit.register(self.stop)

    
    def start(self):
        if self.is_running():
            return
        # make the port it runs on configurable in next patches
        self.process = subprocess.Popen([str(self.binary_path), "--server"], start_new_session=True)
        self._wait_for_server()
        print(f"[Engine] Started at {self.binary_path}")

    def _wait_for_server(self, host='127.0.0.1', port=6742, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex((host, port)) == 0:
                    return True
            time.sleep(0.5)
        raise TimeoutError("[Engine] OpenRGB server failed to start in time.")
    
    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), 15) 
                self.process.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    os.killpg(os.getpgid(self.process.pid), 9)
                    self.process.wait()
                except OSError:
                    pass
            finally:
                self.process = None
    
    def is_running(self):
        return self.process and self.process.poll() is None