import subprocess
import os
import time
from pathlib import Path
from openrgb import OpenRGBClient
from config import settings
from .bifrostengine import BifrostEngine
from .monitor import DeviceMonitor

class Bridge:
    def __init__(self):
        self.engine = BifrostEngine()
        self.engine.start()

        self.startup_tasks = []
        self.client = OpenRGBClient(self.engine.host, self.engine.port, 'Bifrost')
        self.devices = self._map_devices()
        self.monitor = DeviceMonitor(self)
        self.monitor.start()

    def _map_devices(self):
        active = {}
        for device_type, name in settings.DEVICES.items():
            try:
                active[device_type] = self.client.get_devices_by_name(name, exact=False)[0]
            except:
                 print(f"[Bridge] Hardware not found: {name}")
        return active

    def refresh_devices(self):
        print("[Bridge] Re-scanning devices...")
        self.engine.restart()
        self.client = OpenRGBClient(self.engine.host, self.engine.port, 'Bifrost')
        self.devices = self._map_devices()
        self.run_all_startups()

    def run_all_startups(self):
        for task in self.startup_tasks:
            task(self.client, self.devices)