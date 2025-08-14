#!/bin/bash

FOLDER_NAME="trojan"
DOWNLOAD_URL="https://raw.githubusercontent.com/lululuyuanyuanyuanGe/LuTro/main/trojan_linux_amd64/trojan-go-linux-amd64.zip"
ZIP_FILE="trojan-go-linux-amd64.zip"

apt update
apt install -y unzip wget
mkdir -p "/${FOLDER_NAME}"

if [ $? -eq 0 ]; then
    :
else
    exit 1
fi

cd "/${FOLDER_NAME}"
wget "${DOWNLOAD_URL}"

if [ $? -eq 0 ]; then
    :
else
    exit 1
fi

if [ -f "${ZIP_FILE}" ]; then
    :
else
    exit 1
fi

unzip "${ZIP_FILE}"

if [ $? -eq 0 ]; then
    rm "${ZIP_FILE}"
else
    exit 1
fi



# Create config.json with the VPS's own IP as remote_addr
cat > config.json << EOF
{
    "run_type": "server",
    "local_addr": "0.0.0.0",
    "local_port": 443,
    "remote_addr": "{{VPS_PUBLIC_IP}}",
    "remote_port": 80,
    "password": [
        "{{PASSWORD}}"
    ],
    "ssl": {
        "cert": "server.crt",
        "key": "server.key"
    }
}
EOF

echo "SUCCESS" > /tmp/setup_status.txt
