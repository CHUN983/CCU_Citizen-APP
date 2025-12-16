#!/bin/bash

# 安全地將專案同步到 Windows 的腳本
# 排除問題檔案和不必要的目錄

echo "🔧 WSL2 → Windows 專案同步工具"
echo "================================"
echo ""

# 設定路徑
WSL_PROJECT="/root/project/citizenApp/src/main/js/citizen-portal"
WINDOWS_TARGET="/mnt/c/AndroidProjects/citizen-portal"

# 顯示設定
echo "📂 來源: ${WSL_PROJECT}"
echo "📂 目標: ${WINDOWS_TARGET}"
echo ""

# 詢問是否繼續
read -p "是否繼續? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ 取消操作"
    exit 0
fi

echo ""
echo "🔨 步驟 1/4: 建置 Vue 專案..."
cd "${WSL_PROJECT}"
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 建置失敗!"
    exit 1
fi

echo ""
echo "🔄 步驟 2/4: 同步 Capacitor..."
npx cap sync

if [ $? -ne 0 ]; then
    echo "❌ 同步失敗!"
    exit 1
fi

echo ""
echo "📁 步驟 3/4: 建立 Windows 目錄..."
mkdir -p "${WINDOWS_TARGET}"

echo ""
echo "📋 步驟 4/4: 複製檔案到 Windows..."
echo "   (排除不必要的檔案,避免相容性問題)"
echo ""

# 使用 rsync 複製,排除問題檔案
rsync -av --progress \
    --exclude 'node_modules/' \
    --exclude '.git/' \
    --exclude 'dist/' \
    --exclude '.vite/' \
    --exclude '.gradle/' \
    --exclude 'build/' \
    --exclude 'android/.gradle/' \
    --exclude 'android/app/build/' \
    --exclude 'android/build/' \
    --exclude 'ios/App/Pods/' \
    --exclude 'ios/App/build/' \
    --exclude '.DS_Store' \
    --exclude '*.log' \
    --exclude '*~' \
    "${WSL_PROJECT}/" \
    "${WINDOWS_TARGET}/"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 複製完成!"
    echo ""
    echo "📱 下一步:"
    echo "1. 開啟 Android Studio (在 Windows)"
    echo "2. File → Open"
    echo "3. 選擇: C:\\AndroidProjects\\citizen-portal\\android"
    echo "4. 等待 Gradle 同步完成"
    echo "5. 點擊 Run (▶️) 執行 APP"
    echo ""
    echo "💡 提示: 如果 Gradle 同步失敗,請執行:"
    echo "   Build → Clean Project"
    echo "   File → Invalidate Caches... → Invalidate and Restart"
else
    echo ""
    echo "❌ 複製失敗!"
    exit 1
fi
