#!/usr/bin/env python3
import socket
import sys
import os
import subprocess
import re

def cmd_help(args):
    print("""Bifrost Lighting Engine - CLI Tool
    
Usage: bifrost <command>

Commands:
  link                   Creates a dev environment directory with symlinks to settings and plugins
  reload                 Force daemon to re-import plugins
  call <plugin-name>     Send a direct request to daemon to run a plugin
  setudev                Let's you choose devices and writes udev rules for them. (This requires sudo password)
""")

def cmd_call(args):
    if len(args) != 1:
        print("Usage: bifrost call <plugin-name>")
        return
    plugin_name = args[0]
    send_to_daemon(plugin_name)
    
def cmd_link(args):
    target_dir = "bifrost"
    # Just let this one slide, I don't wanna deal with path problems currently :'))
    app_dir = os.path.expanduser("~/.local/share/bifrost/src/bifrost")
    src_settings = os.path.join(app_dir, "config/settings.py")
    src_plugins = os.path.join(app_dir, "plugins")

    if not os.path.exists(src_settings) or not os.path.exists(src_plugins):
        print(f"Error: Could not find settings.py or plugins/ in {app_dir}")
        return
    
    if os.path.exists(target_dir):
        print(f"Error: Directory {target_dir} already exists.")

    try:
        os.makedirs(target_dir)

        os.symlink(src_settings, os.path.join(target_dir, "settings.py"))
        os.symlink(src_plugins, os.path.join(target_dir, "plugins"))

        print(f"Bifrost workplace initialized in ./{target_dir}")
    except OSError as e:
        print("Failed to create workspace")

def cmd_reload(args):
    if len(args) != 0:
        print("Usage: bifrost reload")
        return 
    send_to_daemon('reload')

def cmd_setudev(args):
    try:
        lsusb_out = subprocess.run(["lsusb"], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        print(f"Error listing USB devices: {e}")
        return

    pattern = re.compile(r"ID ([0-9a-fA-F]{4}:[0-9a-fA-F]{4}) (.*)")
    devices = [
        {"id": m.group(1), "desc": m.group(2)} 
        for m in (pattern.search(line) for line in lsusb_out.splitlines()) if m
    ]

    if not devices:
        print("No USB devices found.")
        return

    print("Detected USB devices:")
    for i, dev in enumerate(devices):
        print(f"[{i}] {dev['desc']} ({dev['id']})")
    

    user_input = input("\nEnter the numbers of devices to setup (comma separated, e.g., 0, 2): ")
    try:
        indices = [int(x.strip()) for x in user_input.split(',')]
        selected = [devices[i] for i in indices]
    except (ValueError, IndexError):
        print("Invalid selection. Please use the bracketed numbers.")
        return


    rules = []
    for d in selected:
        vid, pid = d['id'].split(':')
        rules.append(f'SUBSYSTEM=="usb", ATTR{{idVendor}}=="{vid}", ATTR{{idProduct}}=="{pid}", MODE="0666"')
    
    rule_content = "\n".join(rules)
    rule_path = "/etc/udev/rules.d/99-bifrost.rules"

    
    print(f"\nApplying permissions for selected devices...")

    # massive security issues here, fix in later versions
    cmd = f"echo '{rule_content}' | sudo tee {rule_path} && sudo udevadm control --reload-rules && sudo udevadm trigger"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"\nUdev rules written to {rule_path}.")
    except subprocess.CalledProcessError:
        print("\nSetup failed. Ensure you have sudo privileges and try again.")

def main():
    if len(sys.argv) < 2:
        cmd_help(1)
        sys.exit(1)

    commands = {
        'help': cmd_help,
        'link': cmd_link,
        'reload': cmd_reload,
        'call': cmd_call,
        'setudev': cmd_setudev
    }

    cmd_name = sys.argv[1]
    cmd_args = sys.argv[2:]

    handler = commands.get(cmd_name)

    if handler:
        try:
            handler(cmd_args)
        except Exception as e:
            print(f"Error executing '{cmd_name}': {e}")
    else:
        print(f"Unknown command: {cmd_name}")
        sys.exit(1)

def send_to_daemon(command):
    if not command:
        return
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(2.0)
            sock.connect('/tmp/bifrost.sock')
            sock.sendall(command.encode())
    except (FileNotFoundError, ConnectionRefusedError):
        print("Error: Bifrost daemon is not running.")
    except socket.timeout:
        print("Error: Daemon did not respond in time.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()