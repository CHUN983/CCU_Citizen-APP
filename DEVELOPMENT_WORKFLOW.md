# 🔄 Android APP 開發流程指南

## 📋 當前環境設定

### WSL2 環境
- **位置**: `/root/project/citizenApp/`
- **用途**: Vue.js 開發、程式碼編輯
- **工具**: Node.js, npm, Capacitor CLI

### Windows 環境
- **位置**: `C:\Users\user\AndroidProjects\citizenApp\`
- **用途**: Android 建置、測試、執行
- **工具**: Android Studio, JDK 21

---

## 🚀 日常開發流程

### 方案 A：完整自動化流程（推薦）

```bash
# 在 WSL2 中執行
/root/project/citizenApp/sync-to-windows.sh
```

**這個腳本會自動執行：**
1. 建置 Vue.js 應用程式
2. 同步到 Android 平台
3. 複製到 Windows 專案目錄

**完成後在 Windows Android Studio 中：**
1. `File` → `Sync Project with Gradle Files`
2. 點擊 ▶️ **Run** 按鈕

---

### 方案 B：手動分步流程

#### 步驟 1: 修改程式碼（WSL2）
```bash
cd /root/project/citizenApp/src/main/js/citizen-portal
# 使用你喜歡的編輯器修改 Vue 程式碼
code .  # 或 vim, nano 等
```

#### 步驟 2: 建置並同步（WSL2）
```bash
cd /root/project/citizenApp/src/main/js/citizen-portal

# 建置 Vue app
npm run build

# 同步到 Android
npx cap sync
```

#### 步驟 3: 複製到 Windows（WSL2）
```bash
# 同步 android 目錄
rsync -av --delete \
    /root/project/citizenApp/src/main/js/citizen-portal/android/ \
    /mnt/c/Users/user/AndroidProjects/citizenApp/src/main/js/citizen-portal/android/
```

#### 步驟 4: 執行 APP（Windows Android Studio）
1. `File` → `Sync Project with Gradle Files`
2. 點擊 ▶️ **Run** 按鈕

---

## 🎯 常用指令速查

### WSL2 指令

```bash
# 快速建置並同步
cd /root/project/citizenApp/src/main/js/citizen-portal
npm run build && npx cap sync

# 開發模式（Web 預覽）
npm run dev

# 完整同步到 Windows
/root/project/citizenApp/sync-to-windows.sh

# 只建置 Android（不開啟 Android Studio）
/root/project/citizenApp/build-android.sh
```

### Windows PowerShell 指令

```powershell
# 進入專案目錄
cd C:\Users\user\AndroidProjects\citizenApp\src\main\js\citizen-portal\android

# 建置 Debug APK
.\gradlew assembleDebug

# 建置 Release APK
.\gradlew assembleRelease

# 清理建置
.\gradlew clean
```

---

## 📱 測試方式

### 1. Web 測試（快速迭代）
```bash
# 在 WSL2 中
cd /root/project/citizenApp/src/main/js/citizen-portal
npm run dev

# 訪問 http://localhost:5173
```

### 2. Android 模擬器測試
- 在 Android Studio 中點擊 ▶️ **Run**
- 選擇已建立的模擬器
- 等待 APP 安裝並啟動

### 3. 真機測試
1. 手機開啟 USB 偵錯
2. USB 連接到電腦
3. 在 Android Studio 裝置列表中選擇你的手機
4. 點擊 ▶️ **Run**

---

## 🔧 常見開發任務

### 修改 UI 介面
```bash
# 1. 編輯 Vue 元件
vim /root/project/citizenApp/src/main/js/citizen-portal/src/components/YourComponent.vue

# 2. 先在瀏覽器測試
npm run dev

# 3. 確認無誤後同步到 Android
npm run build
npx cap sync
/root/project/citizenApp/sync-to-windows.sh
```

### 修改 Android 原生功能
```bash
# 直接在 Windows Android Studio 中編輯
# 位置: C:\Users\user\AndroidProjects\citizenApp\src\main\js\citizen-portal\android\app\src\main\java
```

### 新增 Capacitor 插件
```bash
# 在 WSL2 中
cd /root/project/citizenApp/src/main/js/citizen-portal
npm install @capacitor/camera  # 範例：安裝相機插件
npx cap sync
/root/project/citizenApp/sync-to-windows.sh
```

### 更新應用程式圖示和名稱
```bash
# 編輯配置檔
vim /root/project/citizenApp/src/main/js/citizen-portal/capacitor.config.ts

# 同步變更
npx cap sync
/root/project/citizenApp/sync-to-windows.sh
```

---

## 🐛 除錯技巧

### Chrome DevTools 除錯（推薦）
1. APP 在模擬器/真機上運行
2. Chrome 瀏覽器打開：`chrome://inspect`
3. 找到你的 APP 並點擊 **inspect**
4. 使用 Console、Network、Elements 等工具除錯

### Android Logcat 除錯
- 在 Android Studio 底部點擊 **Logcat** 標籤
- 過濾器輸入你的 APP 名稱
- 查看錯誤訊息和日誌

### VS Code 遠端除錯
```bash
# 在 VS Code 中安裝 Remote - WSL 擴充套件
# 然後在 WSL2 中開啟專案
code /root/project/citizenApp/src/main/js/citizen-portal
```

---

## 📊 效能最佳化建議

### 1. 只同步必要檔案
- 使用 `sync-to-windows.sh` 只同步 `android/` 目錄
- 避免複製整個專案（包含 `node_modules/`）

### 2. 使用增量建置
```bash
# 開發時使用 dev 模式
npm run dev  # 支援熱重載

# 只在需要測試 Android 功能時才建置
npm run build
```

### 3. 快取優化
```bash
# 清理 Capacitor 快取（如果遇到奇怪問題）
npx cap sync --force
```

---

## 🎓 學習資源

- [Capacitor 官方文件](https://capacitorjs.com/docs)
- [Vue.js 官方文件](https://vuejs.org/)
- [Android Studio 使用指南](https://developer.android.com/studio/intro)

---

## ✅ 快速檢查清單

開發前：
- [ ] WSL2 環境正常（`node -v` 可執行）
- [ ] Windows Android Studio 已開啟專案
- [ ] 模擬器或真機已準備就緒

每次修改後：
- [ ] Vue 程式碼已建置（`npm run build`）
- [ ] 已同步到 Android（`npx cap sync`）
- [ ] 已複製到 Windows（`sync-to-windows.sh` 或手動 `rsync`）
- [ ] Android Studio 已重新同步（Sync Project with Gradle Files）
- [ ] APP 已測試運行正常

---

**💡 提示**：將 `sync-to-windows.sh` 加入你的日常工作流程，可以大幅提升開發效率！
