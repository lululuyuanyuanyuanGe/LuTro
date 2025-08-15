#!/bin/bash

DOMAIN="{{DOMAIN}}"
EMAIL="admin@${DOMAIN}"
CERT_DIR="/root/trojan"
MAX_RETRIES=3
RETRY_COUNT=0

install_certificate() {
    mkdir -p "$CERT_DIR"
    
    if [ $? -eq 0 ]; then
        :
    else
        exit 1
    fi
    
    apt update
    apt install -y socat curl
    
    if [ -d "/root/.acme.sh" ]; then
        rm -rf /root/.acme.sh
    fi
    
    curl -s https://get.acme.sh | sh
    
    if [ $? -eq 0 ]; then
        :
    else
        return 1
    fi
    
    ln -sf /root/.acme.sh/acme.sh /usr/local/bin/acme.sh
    source ~/.bashrc
    export PATH="/root/.acme.sh:$PATH"
    
    /root/.acme.sh/acme.sh --register-account -m "$EMAIL"
    
    if [ $? -eq 0 ]; then
        :
    else
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
    
    if [ $? -eq 0 ]; then
        :
    else
        systemctl start nginx
        return 1
    fi
    
    if [ -f "$CERT_DIR/server.key" ] && [ -f "$CERT_DIR/server.crt" ]; then
        :
    else
        systemctl start nginx
        return 1
    fi
    
    chmod 600 "$CERT_DIR/server.key"
    chmod 644 "$CERT_DIR/server.crt"
    
    systemctl start nginx
    systemctl reload nginx
    
    return 0
}

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    install_certificate
    
    if [ $? -eq 0 ]; then
        exit 0
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        sleep 10
    fi
done

exit 1