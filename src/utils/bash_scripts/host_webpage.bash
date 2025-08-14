#!/bin/bash

WEBPAGE_URL="https://raw.githubusercontent.com/lululuyuanyuanyuanGe/LuTro/main/resources/webpage.html"
WEBROOT="/var/www/html"
TEMP_FILE="/tmp/webpage.html"

echo "Starting webpage hosting setup..."

# Update system packages
apt-get update -y

# Install nginx and ufw if not already installed
apt-get install -y nginx ufw curl

# Download the webpage
echo "Downloading webpage from: $WEBPAGE_URL"
curl -L "$WEBPAGE_URL" -o "$TEMP_FILE"

if [ $? -ne 0 ]; then
    echo "Failed to download webpage from $WEBPAGE_URL"
    exit 1
fi

# Create webroot directory if it doesn't exist
mkdir -p "$WEBROOT"

# Copy downloaded webpage to webroot
cp "$TEMP_FILE" "$WEBROOT/index.html"
chmod 644 "$WEBROOT/index.html"

# Configure nginx to serve on port 80
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

# Test nginx configuration
nginx -t

if [ $? -ne 0 ]; then
    echo "Nginx configuration test failed"
    exit 1
fi

# Configure firewall
echo "Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 'Nginx Full'

# Start and enable nginx
systemctl start nginx
systemctl enable nginx

# Restart nginx to apply configuration
systemctl restart nginx

# Clean up temporary file
rm -f "$TEMP_FILE"

echo "Webpage hosting setup complete!"
echo "Webpage is now accessible on port 80"
echo "Firewall configured to allow HTTP traffic"

# Display status
systemctl status nginx --no-pager -l
ufw status