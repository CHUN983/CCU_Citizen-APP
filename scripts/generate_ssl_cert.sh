#!/bin/bash

# SSL Certificate Generation Script for Citizen App
# This script generates a self-signed SSL certificate for internal use

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SSL Certificate Generation Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
SSL_DIR="$HOME/cityAPP/ssl"
CERT_FILE="$SSL_DIR/selfsigned.crt"
KEY_FILE="$SSL_DIR/selfsigned.key"
DAYS_VALID=365

# Server information (adjust as needed)
COUNTRY="TW"
STATE="Chiayi"
CITY="Chiayi"
ORGANIZATION="CCU"
COMMON_NAME="140.123.105.199"  # Server IP or domain

# Subject Alternative Names (SAN) for multiple hostnames
# Includes both production IP and emulator IP for development
SAN="IP:140.123.105.199,IP:10.0.2.2,DNS:localhost"

echo -e "${YELLOW}Configuration:${NC}"
echo "  SSL Directory: $SSL_DIR"
echo "  Certificate: $CERT_FILE"
echo "  Private Key: $KEY_FILE"
echo "  Valid for: $DAYS_VALID days"
echo "  Common Name: $COMMON_NAME"
echo "  Subject Alternative Names: $SAN"
echo ""

# Create SSL directory if not exists
if [ ! -d "$SSL_DIR" ]; then
    echo -e "${YELLOW}Creating SSL directory...${NC}"
    mkdir -p "$SSL_DIR"
    chmod 700 "$SSL_DIR"
    echo -e "${GREEN}✓ SSL directory created${NC}"
else
    echo -e "${GREEN}✓ SSL directory already exists${NC}"
fi

# Check if certificate already exists
if [ -f "$CERT_FILE" ] || [ -f "$KEY_FILE" ]; then
    echo -e "${YELLOW}Warning: SSL certificate or key already exists${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Aborted. Existing certificate kept.${NC}"
        exit 0
    fi
    echo -e "${YELLOW}Removing old certificate...${NC}"
    rm -f "$CERT_FILE" "$KEY_FILE"
fi

# Generate self-signed certificate with SAN
echo ""
echo -e "${YELLOW}Generating self-signed SSL certificate with SAN...${NC}"
echo ""

# Create temporary OpenSSL config file with SAN
TEMP_CONFIG=$(mktemp)
cat > "$TEMP_CONFIG" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
C=$COUNTRY
ST=$STATE
L=$CITY
O=$ORGANIZATION
CN=$COMMON_NAME

[v3_req]
subjectAltName = $SAN
EOF

# Generate certificate using the config file
openssl req -x509 -nodes -days $DAYS_VALID -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -config "$TEMP_CONFIG" \
    2>/dev/null

# Clean up temporary config
rm -f "$TEMP_CONFIG"

# Set proper permissions
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SSL Certificate Generated Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Certificate Information:${NC}"
echo "  Certificate: $CERT_FILE"
echo "  Private Key: $KEY_FILE"
echo "  Valid for: $DAYS_VALID days"
echo ""

# Display certificate details
echo -e "${YELLOW}Certificate Details:${NC}"
openssl x509 -in "$CERT_FILE" -noout -text | grep -A 2 "Validity"
echo ""
openssl x509 -in "$CERT_FILE" -noout -text | grep -A 1 "Subject:"
echo ""
echo -e "${YELLOW}Subject Alternative Names:${NC}"
openssl x509 -in "$CERT_FILE" -noout -text | grep -A 1 "Subject Alternative Name"
echo ""

echo -e "${GREEN}Next Steps:${NC}"
echo "  1. Update systemd service to use HTTPS"
echo "  2. Restart the citizenapp service"
echo "  3. Access via: https://$COMMON_NAME:8443"
echo "  4. On first visit, trust the certificate in your browser/phone"
echo ""
echo -e "${YELLOW}Note: This is a self-signed certificate.${NC}"
echo -e "${YELLOW}Browsers will show a security warning on first visit.${NC}"
echo -e "${YELLOW}This is normal for self-signed certificates.${NC}"
echo ""
