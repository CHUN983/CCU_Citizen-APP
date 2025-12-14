#!/bin/bash

# HTTPS Setup Script for Citizen App (Server-side)
# This script configures the systemd service to use HTTPS

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  HTTPS Setup Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
PROJECT_DIR="$HOME/cityAPP"
SSL_DIR="$PROJECT_DIR/ssl"
CERT_FILE="$SSL_DIR/selfsigned.crt"
KEY_FILE="$SSL_DIR/selfsigned.key"
SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_DIR/citizenapp.service"
BACKUP_FILE="$SERVICE_FILE.backup.$(date +%Y%m%d_%H%M%S)"

# Check if SSL certificates exist
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo -e "${RED}Error: SSL certificates not found!${NC}"
    echo -e "${YELLOW}Please run generate_ssl_cert.sh first${NC}"
    echo ""
    echo "Run: bash $PROJECT_DIR/scripts/generate_ssl_cert.sh"
    exit 1
fi

echo -e "${GREEN}✓ SSL certificates found${NC}"
echo ""

# Backup existing service file
if [ -f "$SERVICE_FILE" ]; then
    echo -e "${YELLOW}Backing up existing service file...${NC}"
    cp "$SERVICE_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✓ Backup created: $BACKUP_FILE${NC}"
else
    echo -e "${YELLOW}Warning: No existing service file found${NC}"
    echo -e "${YELLOW}Creating new service file...${NC}"
    mkdir -p "$SYSTEMD_DIR"
fi

# Create new systemd service file with HTTPS
echo ""
echo -e "${YELLOW}Creating HTTPS-enabled systemd service...${NC}"

cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=Citizen Urban Planning Participation System (HTTPS)
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/se_city/cityAPP
Environment="PATH=/home/se_city/anaconda3/envs/citizenapp/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/home/se_city/cityAPP/src/main/python"
EnvironmentFile=/home/se_city/cityAPP/.env
ExecStart=/home/se_city/anaconda3/envs/citizenapp/bin/python -m uvicorn src.main.python.core.app:app --host 0.0.0.0 --port 8443 --ssl-keyfile /home/se_city/cityAPP/ssl/selfsigned.key --ssl-certfile /home/se_city/cityAPP/ssl/selfsigned.crt
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

echo -e "${GREEN}✓ Service file created${NC}"
echo ""

# Reload systemd daemon
echo -e "${YELLOW}Reloading systemd daemon...${NC}"
systemctl --user daemon-reload
echo -e "${GREEN}✓ Systemd daemon reloaded${NC}"
echo ""

# Restart service
echo -e "${YELLOW}Restarting citizenapp service...${NC}"
systemctl --user restart citizenapp
echo ""

# Wait for service to start
echo -e "${YELLOW}Waiting for service to start...${NC}"
sleep 3

# Check service status
echo ""
echo -e "${YELLOW}Checking service status...${NC}"
if systemctl --user is-active --quiet citizenapp; then
    echo -e "${GREEN}✓ Service is running${NC}"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    echo ""
    echo -e "${YELLOW}Service logs:${NC}"
    systemctl --user status citizenapp --no-pager -l
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  HTTPS Setup Completed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Service Information:${NC}"
echo "  Status: Running"
echo "  Protocol: HTTPS"
echo "  Port: 8443"
echo "  Certificate: $CERT_FILE"
echo ""
echo -e "${GREEN}Access URLs:${NC}"
echo "  Local: https://localhost:8443"
echo "  Network: https://140.123.105.199:8443"
echo ""
echo -e "${YELLOW}Important Notes:${NC}"
echo "  1. This uses a self-signed certificate"
echo "  2. Browsers will show a security warning on first visit"
echo "  3. Click 'Advanced' → 'Proceed' to trust the certificate"
echo "  4. You only need to do this once per device"
echo ""
echo -e "${GREEN}Testing the service:${NC}"
echo "  curl -k https://localhost:8443/health"
echo ""
echo -e "${GREEN}View logs:${NC}"
echo "  journalctl --user -u citizenapp -f"
echo ""
