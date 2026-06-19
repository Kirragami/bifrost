from bifrost.core.registry import plugin
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import sys
import os
import json
import time
import math

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return RGBColor(
        int(hex_str[0:2], 16),
        int(hex_str[2:4], 16),
        int(hex_str[4:6], 16)
    )

def flash(kb=None, mouse=None):
    devices = []
    if kb:
        devices.append(kb)
    if mouse:
        devices.append(mouse)
        
    if not devices:
        return

    print(devices)
    
    original_colors = {}
    led_counts = {}
    for dev in devices:
        dev.set_mode('direct')
        dev.update()
        original_colors[dev] = [RGBColor(c.red, c.green, c.blue) for c in dev.colors]
        led_counts[dev] = len(dev.colors)

    red = RGBColor(255, 255, 255)
    off = RGBColor(0, 0, 0)

    
    for _ in range(5):
        
        for dev in devices:
            dev.set_colors([red] * led_counts[dev])
        time.sleep(0.1)
        
        
        for dev in devices:
            dev.set_colors([off] * led_counts[dev])
        time.sleep(0.1)

    
    for dev in devices:
        dev.set_mode('direct')
        dev.set_colors(original_colors[dev])

@plugin
def notiflash(client, devices):
    kb = devices.get("keyboard")
    mouse = devices.get("mouse")

    flash(kb, mouse)
