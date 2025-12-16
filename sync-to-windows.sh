#!/bin/bash

echo "🚀 開始 WSL2 → Windows 同步流程..."
echo ""

# 1. 建置 Vue app
echo "📦 步驟 1/3: 建置 Vue app..."
cd /root/project/citizenApp/src/main/js/citizen-portal
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Vue 建置失敗！"
    exit 1
fi

# 2. 同步到 Android
echo ""
echo "🔄 步驟 2/3: 同步到 Android 平台..."
npx cap sync

if [ $? -ne 0 ]; then
    echo "❌ Capacitor 同步失敗！"
    exit 1
fi

# 3. 複製 android 目錄到 Windows
echo ""
echo "📁 步驟 3/3: 同步到 Windows 專案..."
WINDOWS_PROJECT="/mnt/c/Users/user/AndroidProjects/citizenApp/src/main/js/citizen-portal"

# 只複製 android 目錄（避免複製整個專案造成時間浪費）
rsync -av --delete \
    /root/project/citizenApp/src/main/js/citizen-portal/android/ \
    $WINDOWS_PROJECT/android/

if [ $? -ne 0 ]; then
    echo "❌ 複製到 Windows 失敗！"
    exit 1
fi

echo ""
echo "✅ 同步完成！"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 下一步操作："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "方案 1: 使用 Android Studio (推薦)"
echo "  1. 在 Android Studio 中點擊 File → Sync Project with Gradle Files"
echo "  2. 等待同步完成"
echo "  3. 點擊 Run 按鈕 (▶️)"
echo ""
echo "方案 2: 使用命令列建置"
echo "  在 Windows PowerShell 中執行："
echo "  cd C:\\Users\\user\\AndroidProjects\\citizenApp\\src\\main\\js\\citizen-portal\\android"
echo "  .\\gradlew assembleDebug"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
