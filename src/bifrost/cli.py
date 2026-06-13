#!/usr/bin/env python3
import socket
import sys
import os

def cmd_help(args):
    print("""Bifrost Lighting Engine - CLI Tool
    
Usage: bifrost <command>

Commands:
  link                   Creates a dev environment directory with symlinks to settings and plugins
  reload                 Force daemon to re-import plugins
  call <plugin-name>     Send a direct request to daemon to run a plugin
""")

def cmd_call(args):
    if len(args) != 1:
        print("Usage: bifrost call <plugin-name>")
        return
    plugin_name = args[0]
    send_to_daemon(plugin_name)
    
def cmd_link(args):
    print("Linking logic goes here...")

def cmd_reload(args):
    send_to_daemon('reload')

def main():
    if len(sys.argv) < 2:
        cmd_help(1)
        sys.exit(1)

    commands = {
        'help': cmd_help,
        'link': cmd_link,
        'reload': cmd_reload,
        'call': cmd_call
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
            print(f"Sent: {command}")
    except (FileNotFoundError, ConnectionRefusedError):
        print("Error: Bifrost daemon is not running.")
    except socket.timeout:
        print("Error: Daemon did not respond in time.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()