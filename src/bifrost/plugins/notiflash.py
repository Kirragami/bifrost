from bifrost.core.registry import plugin
from openrgb.utils import RGBColor
import time
import threading
import math

notifications_cleared = False
effect_already_active = False


K8_PRO_LED_MAP = {
    # Row 0 - Function Row & Esc
    "ESCAPE": 0, "F1": 1, "F2": 2, "F3": 3, "F4": 4, "F5": 5, "F6": 6, "F7": 7, "F8": 8, "F9": 9, "F10": 10, "F11": 11, "F12": 12, "PRINTSCREEN": 13, "MIC": 14, "RGB": 15,
    
    # Row 1 - Number Row
    "GRAVE": 16, "1": 17, "2": 18, "3": 19, "4": 20, "5": 21, "6": 22, "7": 23, "8": 24, "9": 25, "0": 26, "MINUS": 27, "EQUAL": 28, "BACKSPACE": 29, "INSERT": 30, "HOME": 31, "PAGEUP": 32,
    
    # Row 2 - QWERTY Row
    "TAB": 33, "Q": 34, "W": 35, "E": 36, "R": 37, "T": 38, "Y": 39, "U": 40, "I": 41, "O": 42, "P": 43, "LBRACKET": 44, "RBRACKET": 45, "BACKSLASH": 46, "DELETE": 47, "END": 48, "PAGEDOWN": 49,
    
    # Row 3 - Home Row
    "CAPSLOCK": 50, "A": 51, "S": 52, "D": 53, "F": 54, "G": 55, "H": 56, "J": 57, "K": 58, "L": 59, "SEMICOLON": 60, "QUOTE": 61, "ENTER": 62,
    
    # Row 4 - Bottom Alpha Row
    "LSHIFT": 63, "Z": 64, "X": 65, "C": 66, "V": 67, "B": 68, "N": 69, "M": 70, "COMMA": 71, "PERIOD": 72, "SLASH": 73, "RSHIFT": 74, "UP": 75,
    
    # Row 5 - Modifiers & Navigation
    "LCTRL": 76, "LWIN": 77, "LALT": 78, "SPACE": 79, "RALT": 80, "RWIN": 81, "FN": 82, "RCTRL": 83, "LEFT": 84, "DOWN": 85, "RIGHT": 86
}


KEY_COORDS = {
    # Row 0
    "ESCAPE": (0, 0), "F1": (1.5, 0), "F2": (2.5, 0), "F3": (3.5, 0), "F4": (4.5, 0), "F5": (6, 0), "F6": (7, 0), "F7": (8, 0), "F8": (9, 0), "F9": (10.5, 0), "F10": (11.5, 0), "F11": (12.5, 0), "F12": (13.5, 0), "PRINTSCREEN": (15, 0), "MIC": (16, 0), "RGB": (17, 0),
    # Row 1
    "GRAVE": (0, 1), "1": (1, 1), "2": (2, 1), "3": (3, 1), "4": (4, 1), "5": (5, 1), "6": (6, 1), "7": (7, 1), "8": (8, 1), "9": (9, 1), "0": (10, 1), "MINUS": (11, 1), "EQUAL": (12, 1), "BACKSPACE": (13.5, 1), "INSERT": (15, 1), "HOME": (16, 1), "PAGEUP": (17, 1),
    # Row 2
    "TAB": (0, 2), "Q": (1.25, 2), "W": (2.25, 2), "E": (3.25, 2), "R": (4.25, 2), "T": (5.25, 2), "Y": (6.25, 2), "U": (7.25, 2), "I": (8.25, 2), "O": (9.25, 2), "P": (10.25, 2), "LBRACKET": (11.25, 2), "RBRACKET": (12.25, 2), "BACKSLASH": (13.5, 2), "DELETE": (15, 2), "END": (16, 2), "PAGEDOWN": (17, 2),
    # Row 3
    "CAPSLOCK": (0, 3), "A": (1.5, 3), "S": (2.5, 3), "D": (3.5, 3), "F": (4.5, 3), "G": (5.5, 3), "H": (6.5, 3), "J": (7.5, 3), "K": (8.5, 3), "L": (9.5, 3), "SEMICOLON": (10.5, 3), "QUOTE": (11.5, 3), "ENTER": (13, 3),
    # Row 4
    "LSHIFT": (0, 4), "Z": (1.75, 4), "X": (2.75, 4), "C": (3.75, 4), "V": (4.75, 4), "B": (5.75, 4), "N": (6.75, 4), "M": (7.75, 4), "COMMA": (8.75, 4), "PERIOD": (9.75, 4), "SLASH": (10.75, 4), "RSHIFT": (12.5, 4), "UP": (16, 4),
    # Row 5
    "LCTRL": (0, 5), "LWIN": (1.25, 5), "LALT": (2.25, 5), "SPACE": (6.25, 5), "RALT": (10.25, 5), "RWIN": (11.25, 5), "FN": (12.25, 5), "RCTRL": (13.25, 5), "LEFT": (15, 5), "DOWN": (16, 5), "RIGHT": (17, 5)
}

CENTER = (8.5, 2.5) 

def ripple_worker(kb):
    global notifications_cleared
    global effect_already_active

    kb_original_colors = [RGBColor(c.red, c.green, c.blue) for c in kb.colors]
    ripple_color = RGBColor(255, 255, 255)
    
    drop_interval = 1.0 
    wave_speed = 15.0 
    
    try:
        effect_already_active = True
        while not notifications_cleared:
            start_time = time.time()
            
            while time.time() - start_time < drop_interval:
                if notifications_cleared: break
                
                t = time.time() - start_time
                new_colors = list(kb_original_colors)
                
                current_radius = t * wave_speed
                
                for key_name, idx in K8_PRO_LED_MAP.items():
                    if key_name in KEY_COORDS:
                        x, y = KEY_COORDS[key_name]
                        dist = math.sqrt((x - CENTER[0])**2 + (y - CENTER[1])**2)
                        
                        if abs(dist - current_radius) < 1.2:
                            new_colors[idx] = ripple_color
                
                kb.set_colors(new_colors)
                # time.sleep(0.02)
            
                
    finally:
        kb.set_colors(kb_original_colors)
        effect_already_active = False

@plugin
def notiflash(client, devices):
    global notifications_cleared
    global effect_already_active

    notifications_cleared = False
    kb = devices.get("keyboard")
    if kb and not effect_already_active:
        kb.set_mode('direct')
        thread = threading.Thread(target=ripple_worker, args=(kb,), daemon=True)
        thread.start()

@plugin
def noticleared(client, devices):
    global notifications_cleared
    notifications_cleared = True