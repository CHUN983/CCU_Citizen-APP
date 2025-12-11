#!/bin/bash

# 複製 Android 專案到 Windows 的腳本
# 這樣可以避免 WSL2 路徑問題

echo "📦 Preparing to copy Android project to Windows..."
echo ""

# Windows 使用者目錄 (請根據實際情況修改)
WINDOWS_USER="your_username"  # 修改為您的 Windows 使用者名稱
WINDOWS_PROJECT_PATH="/mnt/c/Users/${WINDOWS_USER}/AndroidProjects/citizen-portal"

echo "Current settings:"
echo "  Source: /root/project/citizenApp/src/main/js/citizen-portal"
echo "  Target: ${WINDOWS_PROJECT_PATH}"
echo ""

# 詢問是否要修改目標路徑
read -p "Is this path correct? (y/n): " answer

if [ "$answer" != "y" ]; then
    echo ""
    echo "Please edit this script and set the correct WINDOWS_USER variable."
    echo "Example: WINDOWS_USER=\"YourName\""
    exit 1
fi

echo ""
echo "🔨 Building Vue app..."
cd /root/project/citizenApp/src/main/js/citizen-portal
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "🔄 Syncing to Capacitor..."
npx cap sync

if [ $? -ne 0 ]; then
    echo "❌ Sync failed!"
    exit 1
fi

echo ""
echo "📋 Creating Windows project directory..."
mkdir -p "${WINDOWS_PROJECT_PATH}"

echo "📂 Copying project files..."
rsync -av --progress \
    --exclude 'node_modules' \
    --exclude '.git' \
    --exclude 'dist' \
    /root/project/citizenApp/src/main/js/citizen-portal/ \
    "${WINDOWS_PROJECT_PATH}/"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Project copied successfully!"
    echo ""
    echo "📱 Next steps:"
    echo "1. Open Android Studio on Windows"
    echo "2. File → Open"
    echo "3. Navigate to: C:\\Users\\${WINDOWS_USER}\\AndroidProjects\\citizen-portal\\android"
    echo "4. Click OK and wait for Gradle sync"
    echo ""
    echo "💡 Tip: Add this path to your Windows path for easy access:"
    echo "   C:\\Users\\${WINDOWS_USER}\\AndroidProjects\\citizen-portal"
else
    echo "❌ Copy failed!"
    exit 1
fi
