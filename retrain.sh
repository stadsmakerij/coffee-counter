#!/bin/bash

cd "$(dirname "$0")" || exit 1

echo "Training model..."
./coffee-counter/bin/python train_model.py

if [ $? -ne 0 ]; then
    echo "Training failed."
    exit 1
fi

echo "Restarting service..."
sudo systemctl restart coffee-counter.service

echo "Done. Model retrained and service restarted."
