import json
import paho.mqtt.client as mqtt
import time
import csv
import os
import sys
import joblib
import numpy as np
import pandas as pd
from collections import deque

MQTT_BROKER_ADDRESS = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "shellyplusplugs-c82e1806b8a0/status/switch:0"
LOG_FILE_PATH = 'power_log.csv'
COFFEE_LOG_PATH = 'coffee_log.csv'
MARKER_FILE_PATH = 'coffee_marker.txt'

model = None
if os.path.exists('coffee_model.pkl'):
    try:
        model = joblib.load('coffee_model.pkl')
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Warning: Failed to load model: {e}")
else:
    print("No model found. Running in data collection mode only.")

event_buffer = deque(maxlen=15)
prediction_buffer = []

coffee_count = 0
last_detection_time = 0

def print_log(message):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def initialize_log_file():
    write_header = False
    if not os.path.exists(LOG_FILE_PATH):
        write_header = True
    else:
        with open(LOG_FILE_PATH, 'r') as file:
            first_line = file.readline().strip()
            if first_line != 'timestamp,power,coffee_brewed':
                write_header = True
    if write_header:
        with open(LOG_FILE_PATH, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'power', 'coffee_brewed'])
        print_log(f"Log file {LOG_FILE_PATH} headers written.")

def initialize_coffee_log():
    global coffee_count
    if not os.path.exists(COFFEE_LOG_PATH):
        with open(COFFEE_LOG_PATH, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp'])
        coffee_count = 0
    else:
        with open(COFFEE_LOG_PATH, 'r') as file:
            coffee_count = sum(1 for _ in file) - 1
    print_log(f"Coffee count initialized: {coffee_count}")

def log_coffee():
    global coffee_count
    coffee_count += 1
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(COFFEE_LOG_PATH, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp])
    print_log(f"Coffee logged. Total: {coffee_count}")

SESSION_FILE_PATH = 'session_marker.txt'

def is_session_active():
    return os.path.exists(SESSION_FILE_PATH)

def is_brewing():
    return os.path.exists(MARKER_FILE_PATH)

def log_power_data(timestamp, power):
    if not is_session_active():
        label = 'unlabeled'
    elif is_brewing():
        label = 'yes'
    else:
        label = 'no'
    with open(LOG_FILE_PATH, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, power, label])

def predict_coffee():
    global coffee_count, prediction_buffer, last_detection_time

    if model is None:
        return

    if len(event_buffer) == 15:
        mean_last_15 = np.mean(event_buffer)
        max_last_15 = np.max(event_buffer)
        min_last_15 = np.min(event_buffer)

        X = pd.DataFrame([[event_buffer[-1], mean_last_15, max_last_15, min_last_15]],
                         columns=['power', 'mean_last_15', 'max_last_15', 'min_last_15'])

        prediction = model.predict(X)
        probability = model.predict_proba(X)[:, 1].mean()

        current_time = time.time()
        if probability > 0.5:
            print_log(f"Predicted: Coffee is being brewed with probability {probability:.2f}")
            if last_detection_time == 0:
                last_detection_time = current_time
                print_log("Timer started.")
            prediction_buffer.append((current_time, probability))
        else:
            print_log(f"Predicted: No coffee brewing detected with probability {probability:.2f}")
            if last_detection_time > 0:
                elapsed_time = current_time - last_detection_time
                mean_probability = np.mean([p[1] for p in prediction_buffer])

                if mean_probability >= 0.5:
                    print_log("Timer still active due to sufficient average probability.")
                    prediction_buffer.append((current_time, probability))
                else:
                    print_log("Timer stopped due to low average probability.")
                    last_detection_time = 0
                    prediction_buffer.clear()

        if last_detection_time > 0 and (current_time - last_detection_time >= 15):
            mean_probability = np.mean([p[1] for p in prediction_buffer])
            if mean_probability > 0.5:
                log_coffee()

                last_detection_time = time.time()
                prediction_buffer = [(last_detection_time, probability)]
                print_log("Timer restarted with current time and last event.")
            else:
                print_log("Timer stopped due to insufficient average probability at 15 seconds.")
                last_detection_time = 0
                prediction_buffer.clear()

def on_mqtt_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))

        if isinstance(payload, dict) and 'apower' in payload:
            power = float(payload['apower'])
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print_log(f"Received power: {power} W")

            log_power_data(timestamp, power)

            event_buffer.append(power)

            predict_coffee()

    except json.JSONDecodeError:
        print_log("Invalid JSON message received")

initialize_log_file()
initialize_coffee_log()

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_message = on_mqtt_message

print_log("Connecting to MQTT broker...")
mqtt_client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT)

mqtt_client.subscribe(MQTT_TOPIC)
print_log(f"Subscribed to topic {MQTT_TOPIC}")

mqtt_client.loop_forever()
