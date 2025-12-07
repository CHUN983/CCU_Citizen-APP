# 🚀 Android Studio 首次執行指南

> **當前狀態**: 已在 Android Studio 開啟專案
> **專案路徑**: E:\code\AndroidStudioProjects\citizen-portal\android

---

## 📋 步驟 1: 等待 Gradle 同步 (3-10 分鐘)

### 您應該會看到:

在 Android Studio 底部會出現進度條:
```
Gradle sync in progress...
Building 'citizen-portal' Gradle project info...
```

### 這個過程中會:
- ✅ 下載 Gradle 8.11.1
- ✅ 下載 Android Gradle Plugin 8.7.2
- ✅ 下載專案依賴套件
- ✅ 索引專案檔案

### ⏱️ 預期時間:
- **首次同步**: 5-10 分鐘 (需下載依賴)
- **後續同步**: 1-2 分鐘

### 🔍 檢查同步狀態:

在 Android Studio 底部查看:
- ✅ **"BUILD SUCCESSFUL"** → 成功,繼續步驟 2
- ❌ **"BUILD FAILED"** → 查看錯誤訊息,跳到「疑難排解」

---

## 📋 步驟 2: 設定 Gradle JDK (如果同步失敗)

如果步驟 1 失敗,錯誤訊息顯示 JDK 相關問題:

### 2.1 開啟 Gradle 設定

```
File → Settings (或按 Ctrl+Alt+S)
→ Build, Execution, Deployment
→ Build Tools
→ Gradle
```

### 2.2 設定 Gradle JDK

在右側找到 **"Gradle JDK"** 下拉選單:

**選擇其中一個:**
- ✅ **jbr-17** (推薦)
- ✅ **Android Studio's embedded JDK**
- ✅ **17** (如果有顯示)

⚠️ **不要選擇:**
- ❌ 任何版本低於 17 的 JDK
- ❌ 包含 "WSL" 或 "Ubuntu" 的路徑

### 2.3 套用並重新同步

1. 點擊 **OK**
2. 點擊工具列的 🔄 **Sync Project with Gradle Files**
3. 等待同步完成

---

## 📋 步驟 3: 檢查專案結構

同步成功後,在左側 **Project** 視窗應該看到:

```
android/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/citizenapp/portal/
│   │       │   └── MainActivity.java
│   │       ├── res/
│   │       └── AndroidManifest.xml
│   └── build.gradle
├── gradle/
├── build.gradle
└── settings.gradle
```

如果看到這個結構 → ✅ 專案設定正確!

---

## 📋 步驟 4: 建立或選擇 Android 虛擬裝置 (AVD)

### 4.1 開啟 Device Manager

點擊工具列的 📱 **Device Manager** 圖示
(或 Tools → Device Manager)

### 4.2 檢查是否有裝置

**情況 A: 已有虛擬裝置**
- ✅ 直接跳到步驟 5

**情況 B: 沒有虛擬裝置**
- 繼續以下步驟建立

### 4.3 建立新的虛擬裝置

1. **點擊 "Create Device"**

2. **選擇硬體** (Category: Phone)
   - 推薦選項:
     - ✅ **Pixel 6** (現代裝置,效能好)
     - ✅ **Pixel 5** (較輕量)
     - ✅ **Medium Phone** (基本款)
   - 點擊 **Next**

3. **選擇系統映像**
   - 推薦選項:
     - ✅ **Tiramisu (API 33)** - Android 13
     - ✅ **UpsideDownCake (API 34)** - Android 14
   - 如果旁邊有 **Download** 連結,點擊下載
   - 下載完成後選擇該系統映像
   - 點擊 **Next**

4. **驗證設定**
   - AVD Name: 保持預設 (例: Pixel 6 API 33)
   - Startup orientation: Portrait
   - 點擊 **Finish**

### 4.4 等待虛擬裝置建立

- 首次建立需要 2-5 分鐘
- 會在 Device Manager 中看到新裝置

---

## 📋 步驟 5: 執行 APP

### 5.1 選擇執行裝置

在頂部工具列的裝置下拉選單中:
- 選擇剛建立的虛擬裝置
- 或選擇已連接的實體裝置 (如果有)

### 5.2 點擊 Run 按鈕

點擊綠色的 ▶️ **Run 'app'** 按鈕
(或按 Shift+F10)

### 5.3 等待 APP 啟動

**首次執行會經歷:**

1. **啟動虛擬裝置** (30-60 秒)
   ```
   Launching 'app' on Pixel 6 API 33
   Cold booting virtual device...
   ```

2. **安裝 APP** (10-30 秒)
   ```
   Installing APKs
   $ adb install-multiple ...
   Success
   ```

3. **啟動 APP**
   ```
   Launching activity...
   ```

### 5.4 成功畫面

**虛擬裝置應該會:**
- ✅ 開機並顯示 Android 桌面
- ✅ 自動啟動 Citizen Portal APP
- ✅ 顯示您的 Vue 3 應用程式

**Android Studio 底部顯示:**
```
App successfully installed
Activity launched
```

---

## 🎉 恭喜!您的第一個 APP 正在運行!

### 您現在應該看到:

- 📱 虛擬裝置運行中
- 🎨 Citizen Portal APP 已開啟
- 🌐 顯示您的 Vue 應用程式內容

### 可以測試的功能:

- ✅ 導航頁面
- ✅ 登入/註冊
- ✅ 查看議題列表
- ✅ **使用相機功能** (虛擬裝置會模擬相機)

---

## 🔧 常見問題疑難排解

### ❌ 問題 1: Gradle Sync 失敗

**錯誤訊息包含 "Unsupported class file" 或 "Java version"**

**解決方案:**
```
1. File → Settings → Build Tools → Gradle
2. Gradle JDK → 選擇 "jbr-17"
3. 點擊 OK
4. File → Sync Project with Gradle Files
```

---

### ❌ 問題 2: 下載依賴很慢

**症狀:** Gradle 同步卡在 "Resolving dependencies"

**解決方案 A: 使用國內鏡像**

編輯 `android/build.gradle`,在最上方加入:

```gradle
buildscript {
    repositories {
        maven { url 'https://maven.aliyun.com/repository/google' }
        maven { url 'https://maven.aliyun.com/repository/jcenter' }
        google()
        mavenCentral()
    }
    // ... rest
}

allprojects {
    repositories {
        maven { url 'https://maven.aliyun.com/repository/google' }
        maven { url 'https://maven.aliyun.com/repository/jcenter' }
        google()
        mavenCentral()
    }
}
```

**解決方案 B: 設定代理**
```
File → Settings → Appearance & Behavior → System Settings → HTTP Proxy
選擇適當的代理設定
```

---

### ❌ 問題 3: "SDK location not found"

**解決方案:**
```
1. File → Project Structure (Ctrl+Alt+Shift+S)
2. SDK Location → Android SDK location
3. 設定為: C:\Users\YourUsername\AppData\Local\Android\Sdk
   (或您實際的 SDK 路徑)
4. 點擊 OK
```

---

### ❌ 問題 4: 虛擬裝置啟動很慢

**優化方案:**

1. **確認 Hyper-V 或 HAXM 已啟用**
   ```
   Settings → Tools → Emulator
   勾選 "Launch in a tool window"
   ```

2. **使用較低規格的裝置**
   - 建立新 AVD 時選擇 "Medium Phone"
   - 選擇較低的 API Level (如 API 30)

3. **調整虛擬裝置設定**
   - Device Manager → 點擊裝置的 ⚙️
   - Graphics: Hardware - GLES 2.0
   - RAM: 2048 MB (如果電腦記憶體充足可提高)

---

### ❌ 問題 5: APP 閃退或白屏

**可能原因:** WebView 問題或 JavaScript 錯誤

**檢查方法:**
```
1. 在 Android Studio 底部點擊 "Logcat"
2. 選擇您的裝置
3. 過濾器輸入: "Capacitor" 或 "Console"
4. 查看錯誤訊息
```

**常見解決方案:**
```bash
# 在 WSL2 重新建置
cd /root/project/citizenApp/src/main/js/citizen-portal
npm run build
npx cap sync

# 複製更新的檔案到 Windows
# 在 Android Studio:
# File → Sync Project with Gradle Files
# Run → Run 'app'
```

---

### ❌ 問題 6: "Unable to locate adb"

**解決方案:**
```
1. 確認 Android SDK Platform-Tools 已安裝
   Tools → SDK Manager → SDK Tools
   勾選 "Android SDK Platform-Tools"
   點擊 Apply

2. 設定 ADB 路徑
   File → Settings → Appearance & Behavior → System Settings → Android SDK
   確認 "Android SDK Location" 正確
```

---

## 🔄 開發工作流程

### 修改程式碼後如何更新 APP?

**完整流程:**

1. **在 WSL2 修改 Vue 程式碼**
   ```bash
   cd /root/project/citizenApp/src/main/js/citizen-portal
   # 編輯 src/ 下的檔案
   ```

2. **建置並同步**
   ```bash
   npm run build
   npx cap sync
   ```

3. **複製 android 資料夾到 Windows**
   ```powershell
   # 在 Windows PowerShell
   robocopy "\\wsl$\Ubuntu\root\project\citizenApp\src\main\js\citizen-portal\android\app\src\main\assets" `
            "E:\code\AndroidStudioProjects\citizen-portal\android\app\src\main\assets" `
            /E /MIR
   ```

4. **在 Android Studio 重新執行**
   - 點擊 ▶️ Run 按鈕
   - 或按 Shift+F10

**快速流程 (只更新 Web 資源):**

如果只修改了 Vue 程式碼,可以只複製 assets:
```powershell
robocopy "\\wsl$\Ubuntu\root\project\citizenApp\src\main\js\citizen-portal\android\app\src\main\assets\public" `
         "E:\code\AndroidStudioProjects\citizen-portal\android\app\src\main\assets\public" `
         /E /MIR
```

---

## 🎯 測試相機功能

### 在虛擬裝置中測試相機:

1. **執行 APP**

2. **導航到相機功能頁面**
   - 例如: 建立新議題 → 上傳圖片

3. **點擊拍照按鈕**
   - 虛擬裝置會彈出相機選擇
   - 選擇 "Camera" 或 "Gallery"

4. **虛擬相機會提供測試圖片**
   - 虛擬裝置內建測試圖片
   - 可以選擇並上傳

### 在實體裝置中測試:

1. **啟用 USB 偵錯**
   - 設定 → 關於手機 → 連續點擊 "版本號碼" 7 次
   - 設定 → 開發人員選項 → 啟用 "USB 偵錯"

2. **連接手機到電腦**
   - 使用 USB 線連接
   - 手機會跳出授權提示 → 點選 "允許"

3. **在 Android Studio 選擇實體裝置**
   - 頂部裝置下拉選單會顯示您的手機
   - 選擇後點擊 Run

4. **測試真實相機**
   - APP 會使用手機的真實相機
   - 可以拍攝實際照片

---

## 📊 效能監控

### 查看 APP 效能:

**Logcat (日誌):**
```
View → Tool Windows → Logcat
過濾: Capacitor, Console, chromium
```

**Profiler (效能分析):**
```
View → Tool Windows → Profiler
可以監控 CPU, Memory, Network 使用情況
```

**Layout Inspector (佈局檢查):**
```
Tools → Layout Inspector
可以查看 WebView 渲染情況
```

---

## 🎓 進階功能

### 建置 Release APK:

1. **Build → Generate Signed Bundle / APK**
2. **選擇 APK**
3. **建立或選擇 Key Store**
4. **選擇 release build variant**
5. **完成後 APK 在 `android/app/release/app-release.apk`**

### 使用實體裝置無線偵錯:

```
1. 手機和電腦連接同一 Wi-Fi
2. 手機啟用 "無線偵錯"
3. 記下 IP 和 Port
4. 在 Android Studio Terminal:
   adb connect 192.168.x.x:5555
```

---

## ✅ 檢查清單

完成首次執行後,確認:

- [ ] Gradle sync 成功
- [ ] 能建立虛擬裝置
- [ ] APP 成功安裝到虛擬裝置
- [ ] APP 正常顯示內容
- [ ] 可以在 APP 中導航
- [ ] (可選) 測試相機功能

---

## 🎉 成功範例截圖

**Gradle Sync 成功:**
```
BUILD SUCCESSFUL in 1m 23s
```

**APP 安裝成功:**
```
Installing APKs
$ adb install-multiple ...
Success
Launching 'app'
Activity com.citizenapp.portal.MainActivity is launched
```

**虛擬裝置運行:**
- 顯示 Android 桌面
- Citizen Portal APP 圖示出現
- 點擊後進入應用程式

---

## 📞 需要幫助?

如果遇到問題:

1. **查看錯誤訊息**
   - Build 視窗底部
   - Logcat 視窗

2. **參考文件**
   - GRADLE_SYNC_FIX.md - Gradle 問題
   - WSL2_ANDROID_SETUP.md - WSL2 環境
   - MOBILE_APP_GUIDE.md - 完整指南

3. **提供資訊**
   - 完整錯誤訊息
   - Android Studio 版本
   - 當前步驟

---

**🚀 祝您開發順利!享受跨平台開發的樂趣!**
