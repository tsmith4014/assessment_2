#!/bin/bash

# This script is used to stop and restart a systemd service. (check the backend api IP address to verify if the service is running)
# It takes the service name as an input and performs the following steps:
# 1. Stops the service using the systemctl stop command.
# 2. Waits for 1 minute using the sleep command.
# 3. Restarts the service using the systemctl start command.

SERVICE_NAME="todolist.service"  # Service name as per your provided systemd service file

# Stop the service
sudo systemctl stop $SERVICE_NAME
echo "Service $SERVICE_NAME stopped."

# Wait for 1 minute
sleep 60

# Restart the service
sudo systemctl start $SERVICE_NAME
echo "Service $SERVICE_NAME restarted."
