# 📱 Citizen Portal 行動 APP 開發指南

> **建立日期**: 2025-11-27
> **版本**: 1.0.0
> **技術**: Vue 3 + Capacitor 7 + Element Plus

## 📋 目錄

1. [專案概述](#專案概述)
2. [技術架構](#技術架構)
3. [環境準備](#環境準備)
4. [開發指南](#開發指南)
5. [建置與部署](#建置與部署)
6. [功能模組](#功能模組)
7. [疑難排解](#疑難排解)

---

## 🎯 專案概述

Citizen Portal 是一個跨平台的市民服務應用程式,使用 Vue 3 + Capacitor 技術實現:

- ✅ **一份程式碼,三個平台**: Web / iOS / Android
- ✅ **原生功能支援**: 相機、檔案系統、推播通知
- ✅ **高度複用**: 95%+ Web 程式碼直接用於 APP
- ✅ **響應式設計**: 自適應不同螢幕尺寸

---

## 🏗️ 技術架構

```
┌─────────────────────────────────────┐
│         Vue 3 Application           │
│  (Vite + Vue Router + Pinia)        │
└─────────────┬───────────────────────┘
              │
      ┌───────┴───────┐
      │  Capacitor 7   │
      └───────┬───────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐        ┌────▼───┐
│  iOS   │        │ Android│
│  App   │        │  App   │
└────────┘        └────────┘
```

### 核心技術棧

| 技術 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5.22 | 前端框架 |
| Vite | 7.1.7 | 建置工具 |
| Capacitor | 7.4.4 | 原生橋接 |
| Element Plus | 2.11.5 | UI 元件庫 |
| Pinia | 3.0.3 | 狀態管理 |
| Vue Router | 4.6.3 | 路由管理 |

---

## 🛠️ 環境準備

### 1️⃣ 基礎環境

```bash
# Node.js 18+ (已安裝)
node --version

# 確認 npm
npm --version
```

### 2️⃣ Android 開發環境

#### 安裝 Android Studio

1. 下載 Android Studio: https://developer.android.com/studio
2. 安裝完成後,開啟 SDK Manager
3. 安裝以下元件:
   - Android SDK Platform 33 (或更高)
   - Android SDK Build-Tools
   - Android Emulator
   - Android SDK Platform-Tools

#### 設定環境變數

```bash
# Linux/macOS - 加入到 ~/.bashrc 或 ~/.zshrc
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin

# 重新載入
source ~/.bashrc  # or source ~/.zshrc
```

```cmd
REM Windows - 設定系統環境變數
ANDROID_HOME=C:\Users\YourUsername\AppData\Local\Android\Sdk
Path=%Path%;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools
```

#### 驗證安裝

```bash
# 檢查 Java (需要 JDK 17+)
java -version

# 檢查 Android SDK
sdkmanager --list

# 檢查 ADB
adb version
```

### 3️⃣ iOS 開發環境 (僅限 macOS)

#### 安裝 Xcode

```bash
# 從 App Store 安裝 Xcode 15+
# 安裝完成後安裝命令列工具
xcode-select --install

# 安裝 CocoaPods
sudo gem install cocoapods

# 驗證
pod --version
```

---

## 💻 開發指南

### 專案結構

```
citizen-portal/
├── src/
│   ├── components/
│   │   └── CameraUpload.vue    # 📸 相機上傳元件
│   ├── utils/
│   │   └── camera.js           # 📷 相機工具函式
│   ├── views/                  # 頁面元件
│   ├── router/                 # 路由設定
│   ├── store/                  # 狀態管理
│   ├── api/                    # API 介接
│   └── main.js                 # 入口檔案
├── android/                    # 🤖 Android 原生專案
├── ios/                        # 🍎 iOS 原生專案
├── dist/                       # 建置輸出
├── capacitor.config.json       # Capacitor 設定
├── vite.config.js              # Vite 設定
└── package.json                # 專案設定
```

### 開發流程

#### 1. Web 開發模式

```bash
cd /root/project/citizenApp/src/main/js/citizen-portal

# 啟動開發伺服器
npm run dev

# 訪問 http://localhost:5173
```

#### 2. Android 開發模式

```bash
# 同步 Web 變更到 Android
npm run cap:sync

# 或者直接建置並開啟 Android Studio
npm run android

# Android Studio 開啟後:
# 1. 等待 Gradle 同步完成
# 2. 點擊 Run 按鈕 (綠色播放圖示)
# 3. 選擇模擬器或實體裝置
```

#### 3. iOS 開發模式 (macOS)

```bash
# 同步 Web 變更到 iOS
npm run cap:sync

# 開啟 Xcode
npm run ios

# Xcode 開啟後:
# 1. 選擇模擬器 (iPhone 14 Pro 等)
# 2. 點擊 Run 按鈕 (▶️)
```

---

## 🔧 功能模組

### 📸 相機與相片上傳

#### 使用相機工具函式

```javascript
// src/utils/camera.js
import { takePicture, pickImages, compressImage } from '@/utils/camera';

// 拍照
const photo = await takePicture({ source: 'camera' });

// 從相簿選擇
const photo = await takePicture({ source: 'gallery' });

// 選擇多張圖片
const photos = await pickImages({ multiple: true });

// 壓縮圖片
const compressed = await compressImage(base64, 1920, 1920, 0.8);
```

#### 使用相機元件

```vue
<template>
  <CameraUpload
    :allow-multiple="true"
    :max-images="5"
    :compress="true"
    @update:images="handleImagesUpdate"
  />
</template>

<script setup>
import CameraUpload from '@/components/CameraUpload.vue';

function handleImagesUpdate(images) {
  console.log('選擇的圖片:', images);
  // images: [{ dataUrl, base64, format, size }, ...]
}
</script>
```

#### 相機權限處理

Android 需要在 `AndroidManifest.xml` 加入權限:

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

iOS 需要在 `Info.plist` 加入說明:

```xml
<!-- ios/App/App/Info.plist -->
<key>NSCameraUsageDescription</key>
<string>我們需要使用相機來拍攝照片</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>我們需要存取相簿來選擇照片</string>
```

### 🔔 其他 Capacitor 插件

```bash
# 安裝更多插件
npm install @capacitor/geolocation        # GPS 定位
npm install @capacitor/push-notifications # 推播通知
npm install @capacitor/network           # 網路狀態
npm install @capacitor/share             # 分享功能
npm install @capacitor/haptics           # 震動回饋

# 同步到原生平台
npm run cap:sync
```

---

## 🚀 建置與部署

### Android APK 建置

#### 1. Debug 版本 (測試用)

```bash
# 同步最新程式碼
npm run build
npx cap sync android

# 開啟 Android Studio
npx cap open android

# 在 Android Studio:
# Build > Build Bundle(s) / APK(s) > Build APK(s)
# 輸出位置: android/app/build/outputs/apk/debug/app-debug.apk
```

#### 2. Release 版本 (正式發布)

##### 產生簽署金鑰

```bash
# 產生 keystore (首次)
keytool -genkey -v -keystore citizen-portal.keystore \
  -alias citizen-portal -keyalg RSA -keysize 2048 -validity 10000

# 記住以下資訊:
# - Keystore 密碼
# - Key 密碼
# - Alias 名稱
```

##### 設定簽署

建立 `android/key.properties`:

```properties
storePassword=你的keystore密碼
keyPassword=你的key密碼
keyAlias=citizen-portal
storeFile=/path/to/citizen-portal.keystore
```

修改 `android/app/build.gradle`:

```gradle
// 在 android {} 區塊內加入

def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

signingConfigs {
    release {
        keyAlias keystoreProperties['keyAlias']
        keyPassword keystoreProperties['keyPassword']
        storeFile file(keystoreProperties['storeFile'])
        storePassword keystoreProperties['storePassword']
    }
}

buildTypes {
    release {
        signingConfig signingConfigs.release
        minifyEnabled false
        proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
    }
}
```

##### 建置 Release APK

```bash
# 使用 Gradle 指令
cd android
./gradlew assembleRelease

# 輸出位置: android/app/build/outputs/apk/release/app-release.apk
```

##### 建置 AAB (Google Play)

```bash
cd android
./gradlew bundleRelease

# 輸出位置: android/app/build/outputs/bundle/release/app-release.aab
```

### iOS IPA 建置 (macOS)

#### 1. Debug 版本

```bash
# 同步程式碼
npm run build
npx cap sync ios

# 開啟 Xcode
npx cap open ios

# 在 Xcode:
# 1. 選擇實體裝置或模擬器
# 2. Product > Run (⌘R)
```

#### 2. Release 版本 (App Store)

```bash
# 在 Xcode:
# 1. 設定 Bundle Identifier (com.citizenapp.portal)
# 2. 設定團隊簽署憑證
# 3. Product > Archive
# 4. 上傳到 App Store Connect
```

---

## 🎨 響應式設計建議

### 偵測平台

```javascript
import { Capacitor } from '@capacitor/core';

// 檢查平台
const platform = Capacitor.getPlatform(); // 'web', 'ios', 'android'
const isNative = Capacitor.isNativePlatform();
const isIOS = platform === 'ios';
const isAndroid = platform === 'android';

// 在 Vue 元件中
if (isNative) {
  // 原生 APP 專屬邏輯
}
```

### CSS 媒體查詢

```css
/* 手機版 */
@media (max-width: 768px) {
  .container {
    padding: 12px;
  }
}

/* 平板版 */
@media (min-width: 769px) and (max-width: 1024px) {
  .container {
    padding: 20px;
  }
}

/* 桌面版 */
@media (min-width: 1025px) {
  .container {
    padding: 32px;
  }
}
```

---

## 🐛 疑難排解

### Android 常見問題

#### 問題: Gradle 同步失敗

```bash
# 清理 Gradle 快取
cd android
./gradlew clean

# 重新同步
npm run cap:sync
```

#### 問題: SDK 版本錯誤

檢查 `android/app/build.gradle`:

```gradle
android {
    compileSdkVersion 33
    defaultConfig {
        minSdkVersion 22
        targetSdkVersion 33
    }
}
```

#### 問題: 無法存取相機

確認已加入權限到 `AndroidManifest.xml`,並在執行時請求權限。

### iOS 常見問題

#### 問題: CocoaPods 安裝失敗

```bash
# 更新 CocoaPods
sudo gem install cocoapods

# 重新安裝 pods
cd ios/App
pod install
```

#### 問題: 簽署錯誤

在 Xcode 的 Signing & Capabilities 分頁:
1. 選擇正確的開發團隊
2. 確認 Bundle Identifier 唯一
3. 選擇適當的 Provisioning Profile

### 一般問題

#### 問題: Hot Reload 不工作

```bash
# 停止開發伺服器
# 刪除快取
rm -rf node_modules .vite dist

# 重新安裝
npm install
npm run dev
```

#### 問題: Capacitor 插件未同步

```bash
# 完整重新同步
npm run build
npx cap sync
```

---

## 📚 參考資源

- [Capacitor 官方文件](https://capacitorjs.com/docs)
- [Vue 3 官方文件](https://vuejs.org/)
- [Element Plus 文件](https://element-plus.org/)
- [Android 開發者文件](https://developer.android.com/)
- [iOS 開發者文件](https://developer.apple.com/)

---

## 🎯 NPM 指令快速參考

```bash
# Web 開發
npm run dev              # 啟動開發伺服器
npm run build            # 建置 Web 版本
npm run preview          # 預覽建置結果

# Capacitor 同步
npm run cap:sync         # 建置並同步到原生平台

# 開啟原生 IDE
npm run android          # 建置並開啟 Android Studio
npm run ios              # 建置並開啟 Xcode (macOS only)
```

---

## ✅ 檢查清單

### 開發前
- [ ] Node.js 18+ 已安裝
- [ ] Android Studio 已安裝並設定好 SDK
- [ ] (macOS) Xcode 和 CocoaPods 已安裝
- [ ] 環境變數已設定

### 建置前
- [ ] 所有功能在 Web 版測試通過
- [ ] 已測試響應式佈局
- [ ] 已處理所有平台特定邏輯
- [ ] 權限說明已加入 AndroidManifest.xml 和 Info.plist

### 發布前
- [ ] App 圖示和啟動畫面已設定
- [ ] 版本號已更新
- [ ] 已建置並測試 Release 版本
- [ ] 已檢查 App 大小和效能
- [ ] 已準備好應用商店素材

---

**🎉 恭喜!您已準備好開發 Citizen Portal 行動 APP!**

如有問題,請參考官方文件或社群論壇。
