#!/usr/bin/env python3
import sys
import os
import time

MARKER_FILE = 'coffee_marker.txt'

def on():
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(MARKER_FILE, 'w') as f:
        f.write(timestamp)
    print(f"Labeling started at {timestamp}. Run 'off' when done.")

def off():
    if not os.path.exists(MARKER_FILE):
        print("No active session. Run 'on' first.")
        return
    os.remove(MARKER_FILE)
    print(f"Labeling stopped at {time.strftime('%Y-%m-%d %H:%M:%S')}.")

def status():
    if os.path.exists(MARKER_FILE):
        with open(MARKER_FILE, 'r') as f:
            print(f"Labeling active since {f.read().strip()}")
    else:
        print("No active labeling session.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python label_coffee.py <on|off|status>")
        sys.exit(1)

    command = sys.argv[1]
    if command == 'on':
        on()
    elif command == 'off':
        off()
    elif command == 'status':
        status()
    else:
        print("Usage: python label_coffee.py <on|off|status>")
        sys.exit(1)
