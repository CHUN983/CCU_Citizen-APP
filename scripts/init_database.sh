#!/bin/bash
# Database initialization script

echo "🗄️  Initializing Database"
echo "========================"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

echo "📊 Creating database if not exists..."
mysql -h ${DB_HOST} -P ${DB_PORT} -u ${DB_USER} -p${DB_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo "📋 Running schema initialization (完整版)..."
mysql -h ${DB_HOST} -P ${DB_PORT} -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} < src/main/resources/config/schema_complete.sql

echo ""
echo "✅ Database initialized successfully!"
echo ""
echo "Default admin credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo "  ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!"
