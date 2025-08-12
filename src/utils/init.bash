#!/bin/bash

FOLDER_NAME="trojan"
DOWNLOAD_URL="https://raw.githubusercontent.com/lululuyuanyuanyuanGe/LuTro/main/trojan_linux_amd64/trojan-go-linux-amd64.zip"
ZIP_FILE="trojan-go-linux-amd64.zip"

# Update package list and install required packages
apt update
apt install -y unzip wget

# Create folder under root directory
mkdir -p "/${FOLDER_NAME}"

if [ $? -eq 0 ]; then
    :
else
    exit 1
fi

# Change to the created directory
cd "/${FOLDER_NAME}"

# Download the file using wget
wget "${DOWNLOAD_URL}"

if [ $? -eq 0 ]; then
    :
else
    exit 1
fi

# Verify the file exists and has content
if [ -f "${ZIP_FILE}" ]; then
    :
else
    exit 1
fi

# Unzip the downloaded file
unzip "${ZIP_FILE}"

if [ $? -eq 0 ]; then
    # Remove the zip file after extraction to save space
    rm "${ZIP_FILE}"
else
    exit 1
fi

ls -la "/${FOLDER_NAME}/"
echo "SUCCESS" > /tmp/setup_status.txt
