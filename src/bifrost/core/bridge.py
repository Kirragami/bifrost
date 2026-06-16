import subprocess
import os
import time
from pathlib import Path
from openrgb import OpenRGBClient
from config import settings
from .bifrostengine import BifrostEngine

class Bridge:
    def __init__(self):
        self.engine = BifrostEngine()
        self.engine.start()

        self.client = OpenRGBClient()
        self.devices = self._map_devices()

    def _map_devices(self):
        active = {}
        for device_type, name in settings.DEVICES.items():
            device = self.client.get_devices_by_name(name, exact=False)[0]
            
            if device:
                active[device_type] = device
            else:
                 print(f"[Bridge] Hardware not found: {name}")
        return active