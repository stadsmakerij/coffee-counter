#!/usr/bin/env python3
import sys
import os
import time

MARKER_FILE = 'coffee_marker.txt'
SESSION_FILE = 'session_marker.txt'

def start():
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(SESSION_FILE, 'w') as f:
        f.write(timestamp)
    print(f"Monitoring session started at {timestamp}.")

def stop():
    if not os.path.exists(SESSION_FILE):
        print("No active session.")
        return
    if os.path.exists(MARKER_FILE):
        os.remove(MARKER_FILE)
    os.remove(SESSION_FILE)
    print(f"Monitoring session stopped at {time.strftime('%Y-%m-%d %H:%M:%S')}.")

def on():
    if not os.path.exists(SESSION_FILE):
        print("No active session. Run 'start' first.")
        return
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(MARKER_FILE, 'w') as f:
        f.write(timestamp)
    print(f"Coffee label ON at {timestamp}.")

def off():
    if not os.path.exists(MARKER_FILE):
        print("Coffee label is not active.")
        return
    os.remove(MARKER_FILE)
    print(f"Coffee label OFF at {time.strftime('%Y-%m-%d %H:%M:%S')}.")

def status():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            print(f"Session active since {f.read().strip()}")
        if os.path.exists(MARKER_FILE):
            with open(MARKER_FILE, 'r') as f:
                print(f"Coffee label ON since {f.read().strip()}")
        else:
            print("Coffee label OFF")
    else:
        print("No active session (data logged as unlabeled).")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python label_coffee.py <start|stop|on|off|status>")
        sys.exit(1)

    command = sys.argv[1]
    commands = {'start': start, 'stop': stop, 'on': on, 'off': off, 'status': status}
    if command in commands:
        commands[command]()
    else:
        print("Usage: python label_coffee.py <start|stop|on|off|status>")
        sys.exit(1)
