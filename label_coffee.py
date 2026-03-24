#!/usr/bin/env python3
import sys
import os
import csv
import time
from datetime import datetime

MARKER_FILE = 'coffee_marker.txt'
LOG_FILE = 'power_log.csv'

def start():
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(MARKER_FILE, 'w') as f:
        f.write(timestamp)
    print(f"Brewing started at {timestamp}. Run 'stop' when done.")

def stop():
    if not os.path.exists(MARKER_FILE):
        print("No active brewing session. Run 'on' first.")
        return

    with open(MARKER_FILE, 'r') as f:
        start_time = f.read().strip()

    stop_time = time.strftime('%Y-%m-%d %H:%M:%S')
    os.remove(MARKER_FILE)

    rows = []
    labeled = 0
    with open(LOG_FILE, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)
        for row in reader:
            if len(row) >= 3 and row[2] == 'undefined':
                if start_time <= row[0] <= stop_time:
                    row[2] = 'yes'
                    labeled += 1
                else:
                    row[2] = 'no'
            rows.append(row)

    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Labeled {labeled} rows as 'yes' between {start_time} and {stop_time}.")
    print(f"All other unlabeled rows set to 'no'.")

def status():
    if os.path.exists(MARKER_FILE):
        with open(MARKER_FILE, 'r') as f:
            print(f"Brewing in progress since {f.read().strip()}")
    else:
        print("No active brewing session.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python label_coffee.py <on|off|status>")
        sys.exit(1)

    command = sys.argv[1]
    if command == 'on':
        start()
    elif command == 'off':
        stop()
    elif command == 'status':
        status()
    else:
        print("Usage: python label_coffee.py <on|off|status>")
        sys.exit(1)
