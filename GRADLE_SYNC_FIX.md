# 🔧 Android Studio Gradle Sync 問題解決方案

> **問題**: Gradle sync 失敗,JVM 路徑錯誤
> **環境**: WSL2 + Windows Android Studio

---

## ❌ 錯誤的做法

**千萬不要將 JDK 路徑指向 WSL2 (`\\wsl$\Ubuntu\...`)**

這會導致:
- ❌ Android Studio 無法正確執行 Gradle
- ❌ 路徑相容性問題
- ❌ 更多編譯錯誤

---

## ✅ 正確的解決方案

### **方案 1: 修正 Android Studio 的 JDK 設定 (快速)**

#### 步驟 1: 檢查錯誤訊息

在 Android Studio 的 Build 輸出視窗,找到具體的錯誤訊息。通常是:
```
Unsupported Java version
Could not determine Java version
JDK version mismatch
```

#### 步驟 2: 設定正確的 JDK

1. **開啟設定**
   ```
   File → Settings (Ctrl+Alt+S)
   或 File → Project Structure (Ctrl+Alt+Shift+S)
   ```

2. **設定 Gradle JDK**
   ```
   Build, Execution, Deployment → Build Tools → Gradle

   Gradle JDK: 選擇 "jbr-17" 或 "Android Studio's embedded JDK"
   ```

   > **重要**: 不要選擇 WSL 路徑!

3. **設定專案 JDK (如果需要)**
   ```
   File → Project Structure → SDK Location

   JDK location: E:\program_file\Android\Android Studio\jbr
   (或其他 Windows 本機路徑)
   ```

4. **重新同步**
   ```
   File → Sync Project with Gradle Files
   或點擊工具列的 🔄 Sync 按鈕
   ```

#### 步驟 3: 清理並重建 (如果仍失敗)

1. **清理 Gradle 快取**
   ```
   Build → Clean Project
   ```

2. **使 Gradle 快取失效**
   ```
   File → Invalidate Caches... → Invalidate and Restart
   ```

3. **重新同步**
   - 等待 Android Studio 重啟
   - 自動開始 Gradle sync

---

### **方案 2: 將專案複製到 Windows (推薦,更穩定)**

由於 WSL2 檔案系統的效能和相容性限制,建議將專案複製到 Windows:

#### 使用手動方式:

**步驟 1: 在 WSL2 建置專案**

```bash
cd /root/project/citizenApp/src/main/js/citizen-portal
npm run build
npx cap sync
```

**步驟 2: 在 Windows 建立專案目錄**

在 Windows PowerShell:
```powershell
# 建立目錄
New-Item -ItemType Directory -Path "C:\AndroidProjects\citizen-portal" -Force

# 開啟檔案總管
explorer C:\AndroidProjects\citizen-portal
```

**步驟 3: 複製專案檔案**

1. 開啟 Windows 檔案總管
2. 在網址列輸入:
   ```
   \\wsl$\Ubuntu\root\project\citizenApp\src\main\js\citizen-portal
   ```
3. 複製整個 `citizen-portal` 資料夾
4. 貼到 `C:\AndroidProjects\`

**步驟 4: 在 Android Studio 開啟 Windows 版本**

1. File → Open
2. 瀏覽到: `C:\AndroidProjects\citizen-portal\android`
3. 點擊 OK

這樣 JDK 路徑就完全在 Windows 系統中,不會有相容性問題。

---

### **方案 3: 使用提供的腳本 (自動化)**

我已經為您建立了自動複製腳本:

```bash
# 編輯腳本,設定您的 Windows 使用者名稱
nano /root/project/citizenApp/copy-to-windows.sh

# 修改這一行:
WINDOWS_USER="your_username"  # 改為您的 Windows 使用者名

# 儲存後執行
/root/project/citizenApp/copy-to-windows.sh
```

---

## 🔍 診斷步驟

### 檢查 Android Studio 的 JDK 版本

在 Android Studio:
```
Help → About

在彈出視窗中查看:
Runtime version: 17.x.x (應該是 17 或更高)
```

### 檢查 Gradle 需求

您的專案使用:
- **Gradle 8.11.1**
- **Android Gradle Plugin 8.7.2**
- **需要 JDK 17 或更高**

Android Studio 內建的 JBR (JetBrains Runtime) 17 完全符合需求。

---

## 🐛 常見錯誤排查

### 錯誤 1: "Unsupported class file major version"

**原因**: JDK 版本太舊

**解決**:
```
Settings → Build Tools → Gradle → Gradle JDK
選擇 JDK 17 或 "jbr-17"
```

### 錯誤 2: "Could not resolve all dependencies"

**原因**: 網路問題或 Maven 倉庫連線失敗

**解決**:
編輯 `android/build.gradle`,在最上方加入:

```gradle
buildscript {
    repositories {
        maven { url 'https://maven.aliyun.com/repository/google' }
        maven { url 'https://maven.aliyun.com/repository/jcenter' }
        google()
        mavenCentral()
    }
    // ... rest of buildscript
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

### 錯誤 3: "Gradle sync failed: permission denied"

**原因**: WSL2 檔案權限問題

**解決**: 使用方案 2,將專案複製到 Windows

---

## 📊 方案比較

| 方案 | 難度 | 速度 | 穩定性 | 推薦度 |
|------|------|------|--------|--------|
| 修正 JDK 設定 | ⭐ 簡單 | ⭐⭐⭐ 快 | ⭐⭐ 中等 | ⚠️ 可試試 |
| 複製到 Windows | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 很快 | ⭐⭐⭐⭐⭐ 很穩定 | ✅ 強烈推薦 |

---

## 🎯 推薦工作流程

### 開發流程 (使用 Windows 專案):

```bash
# 1. 在 WSL2 中開發和測試 Web 版本
cd /root/project/citizenApp/src/main/js/citizen-portal
npm run dev

# 2. 確認功能正常後,建置
npm run build
npx cap sync

# 3. 複製 android 和 ios 資料夾到 Windows
# (只需複製這兩個資料夾,不需要整個專案)
```

在 Windows PowerShell:
```powershell
# 從 WSL 複製 android 資料夾
robocopy \\wsl$\Ubuntu\root\project\citizenApp\src\main\js\citizen-portal\android `
         C:\AndroidProjects\citizen-portal\android `
         /MIR /XD node_modules .gradle build

# 在 Android Studio 開啟並執行
```

---

## 💡 長期建議

### 選項 A: 完全在 Windows 開發

```
優點:
✅ 沒有 WSL2 相容性問題
✅ Android Studio 效能最佳
✅ 所有工具都在同一系統

缺點:
❌ 需要在 Windows 安裝 Node.js
❌ 失去 WSL2 的 Linux 環境優勢
```

### 選項 B: 混合開發 (推薦)

```
優點:
✅ 在 WSL2 開發 Web 版本 (Linux 環境優勢)
✅ 在 Windows 建置 Android (效能和相容性最佳)
✅ 兩者優點兼具

開發流程:
1. WSL2: 寫程式碼 + npm run dev
2. WSL2: npm run build && npx cap sync
3. 複製 android 資料夾到 Windows
4. Windows: Android Studio 建置執行
```

---

## ✅ 快速檢查清單

完成 Gradle sync 前,確認:

- [ ] Android Studio 已安裝在 Windows
- [ ] JDK 設定指向 Windows 本機路徑 (不是 WSL2)
- [ ] Gradle JDK 設為 "jbr-17" 或 "Android Studio's embedded JDK"
- [ ] 專案路徑在 Windows 本機 (不是 `\\wsl$\...`)
- [ ] 網路連線正常 (Gradle 需要下載依賴)

---

## 🆘 仍然失敗?

請提供以下資訊:

1. **完整的錯誤訊息**
   - Build → Build Output 視窗的內容

2. **Android Studio 版本**
   - Help → About

3. **JDK 設定**
   - Settings → Build Tools → Gradle → Gradle JDK

4. **專案路徑**
   - 是在 WSL (`\\wsl$\...`) 還是 Windows (`C:\...`)

---

**💡 最佳實踐**: 將專案複製到 Windows 本機,可以避免 90% 的 WSL2 相關問題!

**🎯 推薦**: 先試試方案 1 (修正 JDK),如果不行就用方案 2 (複製到 Windows)。
