#!/bin/bash

set -e

# Global variables
FOLDER_NAME="trojan"
DOWNLOAD_URL="https://raw.githubusercontent.com/lululuyuanyuanyuanGe/LuTro/main/trojan_linux_amd64/trojan-go-linux-amd64.zip"
ZIP_FILE="trojan-go-linux-amd64.zip"
DOMAIN="{{DOMAIN}}"
EMAIL="admin@${DOMAIN}"
CERT_DIR="/trojan"
WEBPAGE_URL="https://raw.githubusercontent.com/lululuyuanyuanyuanGe/LuTro/main/resources/webpage.html"
WEBROOT="/var/www/html"
TEMP_FILE="/tmp/webpage.html"

# Step 1: Initialize Trojan
apt update
apt install -y unzip wget

if [ -d "/${FOLDER_NAME}" ]; then
    rm -rf "/${FOLDER_NAME}"
fi

mkdir -p "/${FOLDER_NAME}"
cd "/${FOLDER_NAME}"
wget "${DOWNLOAD_URL}"

if [ ! -f "${ZIP_FILE}" ]; then
    exit 1
fi

unzip "${ZIP_FILE}"
rm "${ZIP_FILE}"

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

# Step 2: Install SSL Certificate
install_certificate() {
    mkdir -p "$CERT_DIR"
    apt install -y socat curl
    
    if [ -d "/root/.acme.sh" ]; then
        rm -rf /root/.acme.sh
    fi
    
    curl -s https://get.acme.sh | sh
    
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    ln -sf /root/.acme.sh/acme.sh /usr/local/bin/acme.sh
    source ~/.bashrc
    export PATH="/root/.acme.sh:$PATH"
    
    /root/.acme.sh/acme.sh --register-account -m "$EMAIL"
    
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    ufw allow 80
    systemctl stop nginx
    
    /root/.acme.sh/acme.sh --issue -d "$DOMAIN" --standalone -k ec-256
    
    if [ $? -ne 0 ]; then
        /root/.acme.sh/acme.sh --set-default-ca --server letsencrypt
        /root/.acme.sh/acme.sh --issue -d "$DOMAIN" --standalone -k ec-256
        
        if [ $? -ne 0 ]; then
            /root/.acme.sh/acme.sh --set-default-ca --server zerossl
            /root/.acme.sh/acme.sh --issue -d "$DOMAIN" --standalone -k ec-256
            
            if [ $? -ne 0 ]; then
                /root/.acme.sh/acme.sh --set-default-ca --server buypass
                /root/.acme.sh/acme.sh --issue -d "$DOMAIN" --standalone -k ec-256
                
                if [ $? -ne 0 ]; then
                    systemctl start nginx
                    return 1
                fi
            fi
        fi
    fi
    
    /root/.acme.sh/acme.sh --installcert -d "$DOMAIN" --ecc \
        --key-file "$CERT_DIR/server.key" \
        --fullchain-file "$CERT_DIR/server.crt"
    
    if [ $? -ne 0 ]; then
        systemctl start nginx
        return 1
    fi
    
    if [ ! -f "$CERT_DIR/server.key" ] || [ ! -f "$CERT_DIR/server.crt" ]; then
        systemctl start nginx
        return 1
    fi
    
    chmod 600 "$CERT_DIR/server.key"
    chmod 644 "$CERT_DIR/server.crt"
    
    systemctl start nginx
    systemctl reload nginx
    
    return 0
}

MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    install_certificate
    
    if [ $? -eq 0 ]; then
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        sleep 10
    else
        exit 1
    fi
done

# Step 3: Host Webpage
apt-get install -y nginx ufw curl

curl -L "$WEBPAGE_URL" -o "$TEMP_FILE"

if [ $? -ne 0 ]; then
    exit 1
fi

mkdir -p "$WEBROOT"
cp "$TEMP_FILE" "$WEBROOT/index.html"
chmod 644 "$WEBROOT/index.html"

cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /var/www/html;
    index index.html index.htm index.nginx-debian.html;

    server_name _;

    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

nginx -t

if [ $? -ne 0 ]; then
    exit 1
fi

ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 'Nginx Full'

systemctl start nginx
systemctl enable nginx
systemctl restart nginx

rm -f "$TEMP_FILE"

# Step 4: Start Trojan Server
cd /trojan
chmod +x trojan-go
nohup ./trojan-go -config config.json > trojan.log 2>&1 &

TROJAN_PID=$!
sleep 2

if kill -0 $TROJAN_PID 2>/dev/null; then
    echo $TROJAN_PID > trojan.pid
    echo "SUCCESS" > /tmp/trojan_status.txt
else
    exit 1
fi