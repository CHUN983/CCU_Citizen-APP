# 🐧 WSL2 環境下的 Android APP 開發指南

> **環境**: WSL2 (Windows Subsystem for Linux 2) + Ubuntu 22.04
> **目標**: 在 WSL2 環境中開發 Android APP

---

## 🎯 問題說明

您遇到的錯誤訊息:
```
[error] Unable to launch Android Studio. Is it installed?
        Attempted to open Android Studio at: /usr/local/android-studio/bin/studio.sh
```

**原因**: WSL2 是在 Windows 上執行的 Linux 子系統,沒有圖形介面,無法直接執行 Android Studio GUI。

---

## ✅ 推薦方案:Windows + WSL2 混合開發

### **開發流程:**
1. ✅ 在 WSL2 中開發 Vue 程式碼 (已完成)
2. ✅ 在 WSL2 中建置 Web 版本
3. ✅ 在 Windows 安裝 Android Studio
4. ✅ 從 Windows 開啟 WSL2 中的 Android 專案

---

## 📋 步驟 1: 在 Windows 安裝 Android Studio

### 1.1 下載安裝

```
下載頁面: https://developer.android.com/studio
檔案: android-studio-xxxx.exe
安裝位置: C:\Program Files\Android\Android Studio (預設)
```

### 1.2 安裝 SDK 元件

啟動 Android Studio 後:
1. 點擊 **More Actions** → **SDK Manager**
2. 安裝以下元件:
   - ✅ Android SDK Platform 33 (或更高)
   - ✅ Android SDK Build-Tools
   - ✅ Android Emulator
   - ✅ Android SDK Platform-Tools

### 1.3 設定環境變數 (Windows)

```powershell
# 開啟「系統」→「進階系統設定」→「環境變數」

# 新增使用者變數:
ANDROID_HOME = C:\Users\YourUsername\AppData\Local\Android\Sdk

# 編輯 Path,加入:
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\tools
```

### 1.4 驗證安裝 (在 Windows PowerShell)

```powershell
# 檢查 ADB
adb version

# 檢查 Java (Android Studio 內建)
java -version
```

---

## 📋 步驟 2: 從 Windows 開啟 WSL2 專案

### 方法 1: 使用 Windows 檔案總管

1. 開啟檔案總管
2. 在網址列輸入:
   ```
   \\wsl$\Ubuntu\root\project\citizenApp\src\main\js\citizen-portal\android
   ```
3. 右鍵點擊資料夾 → **Open Folder as Android Studio Project**

### 方法 2: 使用命令列 (PowerShell)

```powershell
# 切換到專案目錄
cd \\wsl$\Ubuntu\root\project\citizenApp\src\main\js\citizen-portal\android

# 使用 Android Studio 開啟
& "C:\Program Files\Android\Android Studio\bin\studio64.exe" .
```

### 方法 3: 在 Android Studio 中開啟

1. 啟動 Android Studio
2. File → Open
3. 瀏覽到:
   ```
   \\wsl$\Ubuntu\root\project\citizenApp\src\main\js\citizen-portal\android
   ```
4. 點擊 OK

---

## 📋 步驟 3: 建置並執行 APP

### 3.1 等待 Gradle 同步

首次開啟專案時:
- Android Studio 會自動開始 Gradle 同步
- 等待進度條完成 (可能需要 3-10 分鐘)
- 如有提示更新 Gradle 或插件,點擊 **Update**

### 3.2 建立模擬器 (如果沒有實體裝置)

1. 點擊工具列的 **Device Manager** (手機圖示)
2. 點擊 **Create Device**
3. 選擇 **Phone** → **Pixel 6** (或其他機型)
4. 選擇系統映像 (例: **Tiramisu** - API 33)
5. 下載系統映像 (首次需要下載)
6. 完成建立

### 3.3 執行 APP

1. 確認頂部工具列顯示正確的裝置
2. 點擊綠色的 ▶️ **Run** 按鈕
3. 等待 APP 安裝並啟動

---

## 🔄 開發工作流程

### 日常開發流程:

```bash
# 1. 在 WSL2 中修改 Vue 程式碼
cd /root/project/citizenApp/src/main/js/citizen-portal
code .  # 或使用任何編輯器

# 2. 在 WSL2 中測試 Web 版本
npm run dev
# 訪問 http://localhost:5173

# 3. 確認功能正常後,建置並同步
npm run build
npx cap sync

# 4. 在 Windows 的 Android Studio 中:
#    - 點擊 Build → Rebuild Project (如果需要)
#    - 點擊 Run 按鈕執行 APP
```

---

## 🚀 快速指令 (WSL2 端)

### 只建置 Web,不開啟 Android Studio

如果您只想建置並同步,不想開啟 Android Studio:

```bash
cd /root/project/citizenApp/src/main/js/citizen-portal

# 只建置和同步
npm run build
npx cap sync
```

然後手動在 Windows 開啟 Android Studio。

### 建立便利腳本

建立一個腳本來自動建置:

```bash
# 建立腳本
cat > /root/project/citizenApp/build-android.sh << 'EOF'
#!/bin/bash
cd /root/project/citizenApp/src/main/js/citizen-portal
echo "🔨 Building Vue app..."
npm run build
echo "🔄 Syncing to Android..."
npx cap sync
echo "✅ Build complete! Open Android Studio on Windows to run the app."
echo "📂 Project path: \\\\wsl\$\\Ubuntu\\root\\project\\citizenApp\\src\\main\\js\\citizen-portal\\android"
EOF

chmod +x /root/project/citizenApp/build-android.sh

# 使用方式:
/root/project/citizenApp/build-android.sh
```

---

## 🔧 替代方案:完全在 WSL2 中建置 (進階)

如果您想完全在 WSL2 中建置 APK,不使用 Android Studio:

### 安裝 Java 和 Android SDK

```bash
# 安裝 Java
sudo apt update
sudo apt install -y openjdk-17-jdk

# 驗證安裝
java -version
```

### 下載 Android SDK Command Line Tools

```bash
# 建立目錄
mkdir -p ~/android-sdk/cmdline-tools
cd ~/android-sdk/cmdline-tools

# 下載 Command Line Tools
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip

# 解壓縮
unzip commandlinetools-linux-9477386_latest.zip
mv cmdline-tools latest

# 設定環境變數
echo 'export ANDROID_HOME=~/android-sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc
```

### 安裝 SDK 元件

```bash
# 接受授權
yes | sdkmanager --licenses

# 安裝必要元件
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"
```

### 建置 APK

```bash
cd /root/project/citizenApp/src/main/js/citizen-portal/android

# 建置 Debug APK
./gradlew assembleDebug

# 輸出位置:
# android/app/build/outputs/apk/debug/app-debug.apk
```

### 安裝到實體裝置

```bash
# 連接 Android 裝置 (需要 USB 偵錯)
# 注意: WSL2 可能無法直接存取 USB,需要 usbipd 設定

# 如果能偵測到裝置:
adb devices
adb install app/build/outputs/apk/debug/app-debug.apk
```

---

## 🐛 常見問題

### Q1: WSL2 無法偵測到 USB 裝置

**解決方案 1: 使用 usbipd**

在 Windows PowerShell (管理員權限):
```powershell
# 安裝 usbipd
winget install usbipd

# 列出 USB 裝置
usbipd list

# 綁定 Android 裝置 (找到對應的 BUSID)
usbipd bind --busid 1-1

# 附加到 WSL
usbipd attach --wsl --busid 1-1
```

在 WSL2 中:
```bash
# 安裝 USB 工具
sudo apt install usbutils

# 檢查裝置
lsusb
adb devices
```

**解決方案 2: 使用 ADB over WiFi**

在 Android 裝置:
1. 開啟開發者選項
2. 啟用「USB 偵錯」和「無線偵錯」
3. 點擊「無線偵錯」,記下 IP 和 Port

在 WSL2:
```bash
adb connect 192.168.x.x:5555
adb devices
```

### Q2: Gradle 下載緩慢

設定 Gradle 使用阿里雲鏡像:

編輯 `android/build.gradle`:
```gradle
allprojects {
    repositories {
        maven { url 'https://maven.aliyun.com/repository/google' }
        maven { url 'https://maven.aliyun.com/repository/jcenter' }
        google()
        mavenCentral()
    }
}
```

### Q3: Windows 無法存取 WSL2 檔案

確保使用正確的路徑格式:
```
✅ 正確: \\wsl$\Ubuntu\root\project\...
❌ 錯誤: \\wsl.localhost\Ubuntu\root\...  (舊版 Windows)
```

如果無法存取:
```bash
# 在 WSL2 中啟動 explorer
explorer.exe .
```

---

## 📊 效能比較

| 方案 | 速度 | 簡易度 | 推薦度 |
|------|------|--------|--------|
| Windows Android Studio | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 推薦 |
| WSL2 命令列建置 | ⭐⭐⭐ | ⭐⭐ | ⚠️ 進階 |
| 混合開發 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 推薦 |

---

## 🎯 推薦配置

### 最佳開發環境設定:

```
開發工具:
- 📝 VSCode (Windows) + Remote WSL 擴充套件
- 🔨 Android Studio (Windows)
- 🐧 WSL2 (Ubuntu) 執行 Node.js 和 npm

工作流程:
1. 在 VSCode 中編輯程式碼 (透過 Remote WSL)
2. 在 WSL2 中執行 npm run build && npx cap sync
3. 在 Windows Android Studio 中執行 APP
```

---

## 📚 參考資源

- [WSL2 官方文件](https://docs.microsoft.com/zh-tw/windows/wsl/)
- [Android Studio 下載](https://developer.android.com/studio)
- [Capacitor 文件](https://capacitorjs.com/docs)
- [usbipd-win GitHub](https://github.com/dorssel/usbipd-win)

---

## ✅ 檢查清單

設定完成後,確認以下項目:

- [ ] Windows 上已安裝 Android Studio
- [ ] Android SDK 已安裝並設定環境變數
- [ ] 能夠從 Windows 存取 WSL2 檔案 (`\\wsl$\Ubuntu\...`)
- [ ] 能夠在 Android Studio 開啟專案
- [ ] Gradle 同步成功
- [ ] 能夠建立並執行模擬器
- [ ] APP 成功安裝並執行

---

**💡 小提示**: 大多數開發者在 WSL2 環境下都使用「混合開發」模式 - 在 WSL2 中寫程式碼和建置,在 Windows 中執行 Android Studio。這是最簡單且效率最高的方式!

**🎉 準備好了嗎?開始在 Windows 安裝 Android Studio 吧!**
