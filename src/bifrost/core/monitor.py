import pyudev
import threading

class DeviceMonitor(threading.Thread):
    def __init__(self, bridge):
        super().__init__(daemon=True)
        self.bridge = bridge
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='usb')

    def run(self):
        for device in iter(self.monitor.poll, None):
            if device.action in ('add', 'remove'):
                print(f"[Monitor] USB event detected: {device.action}")
                self.bridge.refresh_devices()