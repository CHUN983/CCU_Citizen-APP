# 📱 使用真實手機測試 APP 指南

## 🎯 準備工作

### 1. 手機端設定

#### Step 1: 開啟開發者選項

**Android 手機（大多數品牌）：**
```
1. 設定 → 關於手機
2. 連續點擊「版本號碼」或「Build number」7 次
3. 會看到提示：「您已成為開發人員」
```

**不同品牌位置：**
```
Samsung: 設定 → 關於手機 → 軟體資訊 → 版本號碼
Xiaomi: 設定 → 我的裝置 → 全部參數 → MIUI 版本
OPPO/Realme: 設定 → 關於手機 → 版本號碼
Huawei: 設定 → 關於手機 → 版本號碼
```

#### Step 2: 開啟 USB 偵錯

```
1. 設定 → 系統 → 開發人員選項
2. 開啟「USB 偵錯」
3. 開啟「安裝透過 USB 的應用程式」（如果有）
```

#### Step 3: 連接電腦

```
1. 使用 USB 線連接手機到電腦
2. 手機會彈出提示：「允許 USB 偵錯？」
3. 勾選「一律允許這台電腦」
4. 點擊「確定」
```

---

## 🖥️ WSL2 環境下的真機連接

### ⚠️ 重要：WSL2 預設無法直接存取 USB

WSL2 在虛擬環境中運行，無法直接存取 Windows 的 USB 裝置。有兩個解決方案：

### 解決方案 A：在 Windows Android Studio 中使用（推薦）

**優點：** 簡單、可靠、不需額外設定

```
1. 確保手機已連接到 Windows（USB 偵錯已開啟）
2. 在 Windows 的 Android Studio 中開啟專案：
   C:\Users\user\AndroidProjects\citizenApp\src\main\js\citizen-portal\android
3. 在裝置選單中選擇你的手機
4. 點擊 ▶️ Run
```

### 解決方案 B：使用 ADB over WiFi（無線連接）

**優點：** 不需要 USB 線、WSL2 可以直接使用

#### Step 1: 在 Windows 建立 WiFi 連接

```powershell
# 在 Windows PowerShell 中

# 1. 確認手機已透過 USB 連接
adb devices

# 2. 設定手機監聽 WiFi 連接
adb tcpip 5555

# 3. 查看手機 IP 位址
# 在手機上：設定 → 關於手機 → 狀態 → IP 位址
# 例如：192.168.1.100

# 4. 透過 WiFi 連接
adb connect 192.168.1.100:5555

# 5. 可以拔掉 USB 線了
# 驗證連接
adb devices
# 應該看到：192.168.1.100:5555    device
```

#### Step 2: 在 WSL2 中使用

```bash
# 在 WSL2 中

# 安裝 ADB（如果還沒安裝）
sudo apt update
sudo apt install -y android-tools-adb

# 連接到手機（使用相同的 IP）
adb connect 192.168.1.100:5555

# 驗證連接
adb devices

# 現在可以在 WSL2 中安裝 APP
cd /root/project/citizenApp/src/main/js/citizen-portal/android
./gradlew installDebug
```

### 解決方案 C：使用 usbipd（進階）

**優點：** 完整的 USB 支援

#### Windows 端設定：

```powershell
# 在 Windows PowerShell（管理員權限）中

# 1. 安裝 usbipd
winget install usbipd

# 2. 列出 USB 裝置
usbipd list

# 3. 找到你的 Android 裝置（通常顯示品牌名稱）
# 記下 BUSID（例如：1-4）

# 4. 綁定裝置
usbipd bind --busid 1-4

# 5. 附加到 WSL
usbipd attach --wsl --busid 1-4
```

#### WSL2 端設定：

```bash
# 在 WSL2 中

# 1. 安裝 USB 工具
sudo apt install -y usbutils android-tools-adb

# 2. 檢查 USB 裝置
lsusb
# 應該能看到你的手機

# 3. 驗證 ADB 連接
adb devices
```

---

## 🚀 在真機上執行 APP

### 方法 1：Windows Android Studio

```
1. 確保手機已連接（USB 或 WiFi）
2. 在 Android Studio 裝置選單中選擇你的手機
3. 點擊 ▶️ Run
4. APP 會自動安裝並啟動
```

### 方法 2：WSL2 命令列

```bash
cd /root/project/citizenApp/src/main/js/citizen-portal/android

# 建置並安裝
./gradlew installDebug

# 手動在手機上啟動 APP
# 或使用 adb 啟動
adb shell monkey -p your.app.package.name -c android.intent.category.LAUNCHER 1
```

---

## 🔍 查看 APP 在真機上的表現

### 1. 直接在手機上操作

- APP 安裝後會出現在應用程式清單
- 圖示和名稱根據你的 `capacitor.config.ts` 設定
- 可以像一般 APP 一樣使用

### 2. 除錯 APP

#### Chrome DevTools（推薦）

```
1. 手機連接到電腦（USB 或 WiFi）
2. 在手機上開啟 APP
3. 在電腦的 Chrome 瀏覽器訪問：chrome://inspect
4. 找到你的裝置和 APP
5. 點擊 "inspect"
6. 使用 DevTools 除錯
```

#### Android Studio Logcat

```
1. 在 Android Studio 中點擊 "Logcat" 標籤
2. 選擇你的真機裝置
3. 查看即時日誌
```

---

## 📊 真機 vs 模擬器比較

| 功能 | 模擬器 | 真機 |
|------|--------|------|
| 設定難度 | ⭐⭐⭐⭐⭐ 簡單 | ⭐⭐⭐ 中等 |
| 執行速度 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 快速 |
| 硬體功能 | ⭐⭐ 模擬 | ⭐⭐⭐⭐⭐ 完整 |
| 真實體驗 | ⭐⭐⭐ 接近 | ⭐⭐⭐⭐⭐ 真實 |
| WSL2 支援 | ⭐⭐⭐⭐⭐ 完整 | ⭐⭐ 需額外設定 |

---

## 🎯 推薦使用時機

### 使用模擬器：
- ✅ 初期開發和 UI 調整
- ✅ 快速迭代測試
- ✅ 測試不同 Android 版本
- ✅ 不需要硬體功能時

### 使用真機：
- ✅ 測試相機、GPS、感應器
- ✅ 效能測試
- ✅ 最終發布前測試
- ✅ 真實使用者體驗測試

---

## ❓ 常見問題

### Q: 手機無法被偵測到？

**檢查清單：**
```
1. USB 偵錯是否已開啟？
2. USB 線是否支援資料傳輸？（有些線只能充電）
3. 是否已允許這台電腦的 USB 偵錯？
4. 嘗試更換 USB 埠
5. Windows 是否已安裝手機驅動？（通常會自動安裝）
```

**驗證連接：**
```powershell
# 在 Windows PowerShell 中
adb devices

# 應該看到：
# List of devices attached
# XXXXXXXXXXXXXX    device

# 如果看到 unauthorized，檢查手機上的授權提示
```

### Q: ADB over WiFi 一直斷線？

**解決方案：**
```
1. 確保手機和電腦在同一個 WiFi 網路
2. 手機設定中關閉「省電模式」
3. 手機設定中關閉「WiFi 最佳化」
4. 保持手機螢幕開啟（測試期間）
```

### Q: APP 安裝失敗？

**常見原因：**
```
1. 手機已安裝舊版本（簽章不同）
   → 先解除安裝舊版本

2. 儲存空間不足
   → 清理手機空間

3. 安全設定阻擋
   → 設定 → 安全性 → 允許安裝未知應用程式
```

---

## 🔄 完整開發流程（使用真機）

```bash
# 1. 在 WSL2 中開發
cd /root/project/citizenApp/src/main/js/citizen-portal
vim src/App.vue

# 2. 建置並同步
npm run build
npx cap sync

# 3. 同步到 Windows
/root/project/citizenApp/sync-to-windows.sh

# 4. 在 Windows Android Studio 中
# - 選擇你的真機
# - 點擊 ▶️ Run

# 5. 在手機上測試
# - APP 會自動安裝並啟動
# - 在真實裝置上操作測試

# 6. 除錯（如果需要）
# - Chrome 訪問 chrome://inspect
# - 使用 DevTools 查看問題
```

---

**💡 建議**：初期使用模擬器開發，功能完成後再用真機做最終測試！
