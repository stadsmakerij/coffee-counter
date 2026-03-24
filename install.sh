#!/bin/bash

cd "$(dirname "$0")" || exit 1

echo "Starting installation..."

echo "Updating package list and installing required system packages..."
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip mosquitto mosquitto-clients

if [ $? -ne 0 ]; then
    echo "Failed to install system packages. Exiting..."
    exit 1
fi

echo "System packages installed successfully."

if [ -d "coffee-counter" ]; then
    echo "Removing existing virtual environment..."
    rm -rf coffee-counter
fi

echo "Creating virtual environment (might take a while)..."
python3 -m venv coffee-counter

if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment. Exiting..."
    exit 1
fi
echo "Virtual environment 'coffee-counter' created."

echo "Activating virtual environment..."
source coffee-counter/bin/activate

if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment. Exiting..."
    exit 1
fi

echo "Virtual environment activated."

echo "Upgrading pip and installing necessary Python libraries..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install Python libraries. Exiting..."
    deactivate
    exit 1
fi

echo "All Python libraries installed successfully."

CONFIG_FILE="/etc/mosquitto/conf.d/custom_port.conf"
echo "Configuring Mosquitto to use custom port and allow anonymous connections..."
if ! grep -q "listener 1883" "$CONFIG_FILE" || ! grep -q "allow_anonymous true" "$CONFIG_FILE"; then
    echo -e "listener 1883\nallow_anonymous true" | sudo tee "$CONFIG_FILE" > /dev/null
else
    echo "Mosquitto configuration already set."
fi

echo "Starting Mosquitto MQTT broker service..."
sudo systemctl enable mosquitto
sudo systemctl restart mosquitto

if [ $? -ne 0 ]; then
    echo "Failed to start Mosquitto service. Exiting..."
    deactivate
    exit 1
fi

echo "Mosquitto MQTT broker service started successfully."

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Training model with scikit-learn version on this system..."
$INSTALL_DIR/coffee-counter/bin/python $INSTALL_DIR/train_model.py

if [ $? -ne 0 ]; then
    echo "Failed to train model. Exiting..."
    deactivate
    exit 1
fi

echo "Model trained successfully."

echo "Creating systemd service for coffee-counter..."
SERVICE_FILE="/etc/systemd/system/coffee-counter.service"
sudo bash -c "cat > $SERVICE_FILE" << EOL
[Unit]
Description=Coffee Counter Python Service
After=network.target mosquitto.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/coffee-counter/bin/python -u $INSTALL_DIR/main.py
Environment=PYTHONUNBUFFERED=1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

echo "Enabling and starting coffee-counter service..."
sudo systemctl daemon-reload
sudo systemctl enable coffee-counter.service
sudo systemctl restart coffee-counter.service

if [ $? -ne 0 ]; then
    echo "Failed to start coffee-counter service. Exiting..."
    deactivate
    exit 1
fi

echo "Coffee-counter service started successfully."

echo "Installation complete. The environment is ready for use."

deactivate
