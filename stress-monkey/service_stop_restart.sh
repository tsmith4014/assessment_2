#!/bin/bash

SERVICE_NAME="todolist"  # Service name as per your provided systemd service file

# Stop the service
sudo systemctl stop $SERVICE_NAME
echo "Service $SERVICE_NAME stopped."

# Wait for 1 minute
sleep 60

# Restart the service
sudo systemctl start $SERVICE_NAME
echo "Service $SERVICE_NAME restarted."
