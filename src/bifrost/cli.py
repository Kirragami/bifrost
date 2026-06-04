#!/usr/bin/env python3
import socket
import sys

def send_command(command):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/bifrost.sock")
        sock.sendall(command.encode())
        sock.close()
        print(f"Sent: {command}")
    except FileNotFoundError:
        print("Error: Bifrost daemon is not running.")
    except ConnectionRefusedError:
        print("Error: Could not connect to the socket.")

def main():
    if len(sys.argv) < 2:
        print("Usage: bifrost <command>")
    else:
        send_command(sys.argv[1])