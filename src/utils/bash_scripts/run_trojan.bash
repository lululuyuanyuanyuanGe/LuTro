#!/bin/bash

# Navigate to trojan directory
cd /trojan

# Make sure the trojan binary is executable
chmod +x trojan-go

# Start trojan server in the background
nohup ./trojan-go -config config.json > trojan.log 2>&1 &

# Get the process ID
TROJAN_PID=$!

# Wait a moment for the process to start
sleep 2

# Check if the process is still running
if kill -0 $TROJAN_PID 2>/dev/null; then
    echo "Trojan server started successfully with PID: $TROJAN_PID"
    echo $TROJAN_PID > trojan.pid
    echo "SUCCESS" > /tmp/trojan_status.txt
else
    exit 1
fi

# Show the log for verification
tail -n 10 trojan.log