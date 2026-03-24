# Coffee counter

Raspberry Pi script that detects coffee brews by monitoring power consumption from a Shelly Plug via MQTT. Uses a machine learning model trained on labeled power data.

## Install

```bash
bash install.sh
```

This sets up the virtual environment, installs dependencies, configures Mosquitto MQTT broker, and creates a systemd service.

## Usage

### 1. Collect data

After install, the service runs in data collection mode. It logs power data to `power_log.csv`.

### 2. Label coffee brews

When making coffee, mark the brew:

```bash
python label_coffee.py on    # start of brew
python label_coffee.py off   # end of brew
```

### 3. Train the model

After labeling ~10-20 brews:

```bash
bash retrain.sh
```

This trains the model and restarts the service. Coffee brews are now detected automatically and logged to `coffee_log.csv`.

## Commands

| Command                                         | Description |
|-------------------------------------------------|---|
| `bash install.sh`                               | Full install |
| `python label_coffee.py on`                     | Start labeling a brew |
| `python label_coffee.py off`                    | Stop labeling |
| `python label_coffee.py status`                 | Check if labeling is active |
| `bash retrain.sh`                               | Retrain model and restart service |
| `sudo journalctl -u coffee-counter.service -f`  | View live logs |
| `sudo systemctl restart coffee-counter.service` | Restart service |

## Configuration

The Shelly Plug must be configured to send MQTT data to the Pi's IP on port `1883`. The MQTT topic is set in `main.py`.
