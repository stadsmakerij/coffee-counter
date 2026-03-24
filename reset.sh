#!/bin/bash

echo "Resetting coffee counter..."

rm -f power_log.csv coffee_log.csv coffee_model.pkl coffee_marker.txt session_marker.txt

sudo systemctl restart coffee-counter.service

echo "Done. All data, model, and markers removed. Service restarted."
