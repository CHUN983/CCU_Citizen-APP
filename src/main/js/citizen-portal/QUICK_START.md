# 🚀 Citizen Portal APP 快速開始

> **5 分鐘上手指南** - 從安裝到執行第一個 APP

## 📱 方案選擇

您選擇了: **Vue 3 + Capacitor** ✅

**為什麼選擇這個方案?**
- 🎯 **程式碼複用 95%+** - 直接使用現有 Vue 程式碼
- 🚀 **最快上線** - 不需要學習新框架
- 💰 **成本最低** - 一份程式碼,三個平台
- 🔧 **維護簡單** - Web/iOS/Android 統一更新

---

## ⚡ 立即開始 (3 步驟)

### 步驟 1: 安裝 Android Studio

```bash
# 1. 下載 Android Studio
# https://developer.android.com/studio

# 2. 安裝完成後,開啟 SDK Manager 並安裝:
# ✅ Android SDK Platform 33
# ✅ Android SDK Build-Tools
# ✅ Android Emulator

# 3. 設定環境變數 (Linux/macOS)
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools

# 4. 驗證安裝
java -version
adb version
```

### 步驟 2: 建置並執行 Android APP

```bash
# 切換到專案目錄
cd /root/project/citizenApp/src/main/js/citizen-portal

# 開啟 Android Studio
npm run android

# 首次啟動會自動:
# ✅ 建置 Vue 專案
# ✅ 同步到 Android 平台
# ✅ 開啟 Android Studio
```

### 步驟 3: 在模擬器或實體裝置執行

```
在 Android Studio 中:
1. 等待 Gradle 同步完成 (首次需 3-5 分鐘)
2. 點擊頂部工具列的 ▶️ Run 按鈕
3. 選擇模擬器或連接的實體裝置
4. 等待安裝並啟動 APP

🎉 完成!您的第一個 APP 正在執行!
```

---

## 📖 使用相機功能範例

### 方法 1: 使用現成元件 (推薦)

```vue
<template>
  <div class="page">
    <h2>拍照上傳</h2>

    <!-- 直接使用 CameraUpload 元件 -->
    <CameraUpload
      :allow-multiple="true"
      :max-images="5"
      @update:images="handleImages"
    />

    <el-button
      type="primary"
      @click="uploadImages"
      :disabled="images.length === 0"
    >
      上傳圖片 ({{ images.length }})
    </el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import CameraUpload from '@/components/CameraUpload.vue';
import { ElMessage } from 'element-plus';

const images = ref([]);

function handleImages(newImages) {
  images.value = newImages;
  console.log('已選擇圖片:', newImages);
}

async function uploadImages() {
  try {
    // TODO: 呼叫您的後端 API
    // await api.uploadImages(images.value);

    ElMessage.success(`成功上傳 ${images.value.length} 張圖片`);
  } catch (error) {
    ElMessage.error('上傳失敗: ' + error.message);
  }
}
</script>
```

### 方法 2: 直接使用工具函式

```vue
<template>
  <div>
    <el-button @click="takePhoto">拍照</el-button>
    <img v-if="photo" :src="photo.dataUrl" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { takePicture } from '@/utils/camera';

const photo = ref(null);

async function takePhoto() {
  try {
    photo.value = await takePicture({
      source: 'camera',
      quality: 80
    });
  } catch (error) {
    console.error('拍照失敗:', error);
  }
}
</script>
```

---

## 🔧 日常開發流程

### Web 開發 (推薦先在 Web 測試)

```bash
# 1. 啟動開發伺服器
npm run dev

# 2. 瀏覽器開啟 http://localhost:5173

# 3. 修改程式碼 (即時 Hot Reload)

# 4. 測試功能
```

### 同步到 Android APP

```bash
# 當 Web 功能完成後,同步到 APP
npm run cap:sync

# 或者直接建置並開啟 Android Studio
npm run android
```

### 測試相機功能

**注意:** 相機功能需要在實體裝置或支援相機的模擬器上測試

```bash
# 1. 連接 Android 手機 (開啟 USB 偵錯)
adb devices

# 2. 在 Android Studio 選擇實體裝置
# 3. 點擊 Run
# 4. APP 安裝後,測試拍照功能
```

---

## 📊 專案結構說明

```
citizen-portal/
├── 📱 android/              # Android 原生專案 (自動產生)
├── 🍎 ios/                  # iOS 原生專案 (自動產生)
├── 🌐 src/                  # Vue 3 程式碼 (您主要開發的地方)
│   ├── components/
│   │   └── CameraUpload.vue  # 📸 相機元件 (已建立)
│   ├── utils/
│   │   └── camera.js         # 📷 相機工具 (已建立)
│   ├── views/               # 頁面元件 (您的程式碼)
│   ├── api/                 # API 呼叫
│   └── store/               # 狀態管理
├── 📦 dist/                 # 建置輸出 (自動產生)
└── ⚙️ capacitor.config.json # Capacitor 設定
```

**開發重點:**
- ✏️ 主要在 `src/` 目錄開發 Vue 元件
- 🚫 不要直接修改 `android/` 和 `ios/` (自動產生)
- 🔄 每次修改後執行 `npm run cap:sync` 同步

---

## 🎨 客製化 APP

### 1. 修改 APP 名稱和圖示

#### APP 名稱

編輯 `capacitor.config.json`:

```json
{
  "appName": "市民服務平台",  // ← 修改這裡
  "appId": "com.citizenapp.portal"
}
```

#### APP 圖示

```bash
# 準備 1024x1024 的 PNG 圖示
# 使用線上工具產生各尺寸: https://icon.kitchen

# 替換圖示檔案:
# Android: android/app/src/main/res/mipmap-*/ic_launcher.png
# iOS: ios/App/App/Assets.xcassets/AppIcon.appiconset/
```

### 2. 修改啟動畫面 (Splash Screen)

編輯 `capacitor.config.json`:

```json
{
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 2000,
      "backgroundColor": "#409EFF",  // ← 您的品牌色
      "showSpinner": false
    }
  }
}
```

### 3. 設定 APP 版本

Android: 編輯 `android/app/build.gradle`

```gradle
defaultConfig {
    versionCode 1          // ← 每次發布 +1
    versionName "1.0.0"    // ← 顯示給使用者看的版本
}
```

---

## 🐛 常見問題速查

### ❓ 找不到 Android SDK

```bash
# 設定環境變數
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools

# 加入到 ~/.bashrc 或 ~/.zshrc
echo 'export ANDROID_HOME=$HOME/Android/Sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc
```

### ❓ Gradle 同步失敗

```bash
cd android
./gradlew clean
cd ..
npm run cap:sync
```

### ❓ 相機權限被拒絕

確認 `android/app/src/main/AndroidManifest.xml` 有加入:

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
```

### ❓ 無法連接實體裝置

```bash
# 1. 手機開啟「開發者選項」和「USB 偵錯」
# 2. 連接 USB 後執行:
adb devices

# 如果顯示 unauthorized:
# - 手機會跳出授權提示,點選「允許」
# - 重新執行 adb devices
```

---

## 📈 下一步

### 完成基礎設定後,您可以:

1. **新增更多功能**
   - GPS 定位: `npm install @capacitor/geolocation`
   - 推播通知: `npm install @capacitor/push-notifications`
   - 分享功能: `npm install @capacitor/share`

2. **優化 APP 效能**
   - 圖片壓縮 (已整合在 CameraUpload)
   - 快取策略
   - 離線支援

3. **準備上架**
   - 產生簽署金鑰
   - 建置 Release 版本
   - 準備商店素材

4. **iOS 開發** (需要 macOS)
   - 安裝 Xcode
   - 執行 `npm run ios`
   - 測試 iOS 版本

---

## 🎯 重要指令速記卡

```bash
# 🌐 Web 開發
npm run dev                # 啟動開發伺服器
npm run build              # 建置 Web 版本

# 📱 APP 開發
npm run android            # 開啟 Android Studio
npm run cap:sync           # 同步到原生平台

# 🔍 偵錯
adb devices                # 查看連接的裝置
adb logcat                 # 查看 Android 日誌

# 🧹 清理
rm -rf node_modules dist   # 清理暫存
npm install                # 重新安裝
```

---

## 💡 開發技巧

### 1. 平台偵測

```javascript
import { Capacitor } from '@capacitor/core';

const isAndroid = Capacitor.getPlatform() === 'android';
const isIOS = Capacitor.getPlatform() === 'ios';
const isNative = Capacitor.isNativePlatform();

if (isNative) {
  // 只在 APP 執行
}
```

### 2. 在瀏覽器測試 APP 功能

某些功能(如相機)在瀏覽器會自動降級為網頁版:
- 拍照 → 使用 `<input type="file" capture="camera">`
- 相簿 → 使用 `<input type="file" accept="image/*">`

### 3. 即時預覽

```bash
# 1. 確保手機和電腦在同一網路
npm run dev

# 2. 查看電腦 IP (例如: 192.168.1.100)
ifconfig  # macOS/Linux
ipconfig  # Windows

# 3. 手機瀏覽器開啟: http://192.168.1.100:5173
```

---

## 🎓 學習資源

- 📘 [完整開發指南](./MOBILE_APP_GUIDE.md)
- 🌐 [Capacitor 官方文件](https://capacitorjs.com/docs)
- 🎥 [Capacitor 教學影片](https://www.youtube.com/c/capacitorjs)
- 💬 [Capacitor 社群論壇](https://forum.ionicframework.com/c/capacitor)

---

**🚀 準備好了嗎?開始您的第一個 APP 開發之旅!**

```bash
cd /root/project/citizenApp/src/main/js/citizen-portal
npm run android
```

如有任何問題,請參考 [完整開發指南](./MOBILE_APP_GUIDE.md) 或搜尋官方文件。
