import pyudev
import threading
import time

class DeviceMonitor(threading.Thread):
    def __init__(self, bridge):
        super().__init__(daemon=True)
        self.bridge = bridge
        self.restart_func = self.bridge.refresh_devices
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='usb')
        self.is_restarting = False

        self.debounce_seconds = 3.0
        self.timer = None

    def run(self):
        for device in iter(self.monitor.poll, None):
            if device.action in ('add', 'remove'):
                print(f"[Monitor] USB event detected: {device.action}")
                self._debounce_event()

    def _debounce_event(self):
        if self.is_restarting:
            return
            
        if self.timer:
            self.timer.cancel()
        
        self.timer = threading.Timer(self.debounce_seconds, self._trigger_callback)
        self.timer.start()

    def _trigger_callback(self):
        self.is_restarting = True
        try:
            self.restart_func()
        finally:
            self.is_restarting = False