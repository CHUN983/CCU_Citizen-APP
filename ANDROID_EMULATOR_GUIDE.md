# 📱 Android 模擬器完整使用指南

## 🎯 第一次使用：建立虛擬裝置

### 1. 開啟 Device Manager
在 Android Studio 中：
- 點擊右上角的 **Device Manager** 圖示（手機圖示）
- 或：`Tools` → `Device Manager`

### 2. 建立新裝置
1. 點擊 **Create Device** 按鈕
2. 選擇裝置類型：
   ```
   Category: Phone
   Device: Pixel 6 或 Pixel 7（推薦）
   ```
3. 點擊 **Next**

### 3. 選擇系統映像
1. 選擇 Android 版本：
   ```
   Release Name: Tiramisu (API Level 33) ⭐推薦
   或
   Release Name: UpsideDownCake (API Level 34)
   ```
2. 如果旁邊顯示 **Download**，點擊下載（第一次需要下載，約 800MB-1.5GB）
3. 等待下載完成
4. 點擊 **Next**

### 4. 完成設定
1. 給模擬器一個名稱（例如：`Pixel 6 API 33`）
2. 進階設定（可選）：
   ```
   RAM: 2048 MB（建議至少 2GB）
   Internal Storage: 2048 MB
   ```
3. 點擊 **Finish**

---

## ▶️ 執行你的 APP

### 方法 A：使用 Run 按鈕（最簡單）

1. **確認專案已同步**
   - 如果看到提示，點擊 `Sync Now`
   - 或：`File` → `Sync Project with Gradle Files`

2. **選擇執行裝置**
   - 在上方工具列，找到裝置下拉選單
   - 選擇你剛建立的模擬器（例如：`Pixel 6 API 33`）

3. **執行 APP**
   - 點擊綠色的 ▶️ **Run** 按鈕
   - 或按快捷鍵：`Shift + F10`

4. **等待啟動**
   ```
   第一次啟動流程：
   1. 模擬器開機（約 30-60 秒）
   2. Gradle 建置 APP（約 10-30 秒）
   3. 安裝 APP 到模擬器（約 5-10 秒）
   4. 自動啟動 APP
   ```

### 方法 B：先啟動模擬器，再執行

1. **手動啟動模擬器**
   - 在 Device Manager 中
   - 點擊你的模擬器旁邊的 ▶️ 按鈕

2. **等待模擬器完全啟動**
   - 看到 Android 主畫面表示已啟動

3. **執行 APP**
   - 點擊 Android Studio 的 ▶️ **Run** 按鈕

---

## 👀 如何看到你的 APP

### APP 啟動後你會看到：

1. **自動開啟**
   - APP 會自動在模擬器中開啟
   - 顯示你的 Vue.js 設計的介面

2. **手動開啟**（如果關閉了）
   - 在模擬器主畫面
   - 點擊應用程式清單（圓形圖示，底部中間）
   - 找到你的 APP 圖示並點擊

### APP 名稱和圖示位置：

你的 APP 預設資訊可以在這裡查看：
```bash
# 在 WSL2 中查看
cat /root/project/citizenApp/src/main/js/citizen-portal/capacitor.config.ts
```

---

## 🔍 查看 APP 內容

### 你設計的內容在哪裡？

你的 Vue.js 程式碼會顯示在 APP 中：

1. **主頁面**
   - 位置：`src/main/js/citizen-portal/src/views/`
   - 這些 Vue 元件會渲染成 APP 的頁面

2. **元件**
   - 位置：`src/main/js/citizen-portal/src/components/`
   - UI 元素、按鈕、卡片等

3. **路由**
   - 位置：`src/main/js/citizen-portal/src/router/`
   - 控制頁面導航

### 範例：修改主頁面

```bash
# 1. 在 WSL2 中修改 Vue 檔案
vim /root/project/citizenApp/src/main/js/citizen-portal/src/App.vue

# 2. 建置並同步
/root/project/citizenApp/sync-to-windows.sh

# 3. 在 Android Studio 中重新執行
# 點擊停止按鈕（■）然後再點擊執行按鈕（▶️）
```

---

## 🎨 模擬器控制

### 基本操作：

```
返回：模擬器右側面板的 ◀ 按鈕
主畫面：模擬器右側面板的 ⭘ 按鈕
最近使用的 APP：模擬器右側面板的 ▭ 按鈕
音量：模擬器右側面板的 🔊 按鈕
旋轉螢幕：模擬器右側面板的 🔄 按鈕
```

### 進階功能（點擊 ... 更多按鈕）：

```
Location：模擬 GPS 位置
Camera：使用電腦攝影機
Phone：模擬電話
Cellular：模擬網路狀態
Battery：模擬電池狀態
```

---

## 🐛 除錯你的 APP

### 1. Chrome DevTools（最強大）

```bash
# APP 在模擬器運行時：
1. 開啟 Chrome 瀏覽器
2. 訪問：chrome://inspect
3. 找到你的 APP 名稱
4. 點擊 "inspect"
5. 使用 Console、Network、Elements 標籤除錯
```

### 2. Android Studio Logcat

```
1. 在 Android Studio 底部點擊 "Logcat" 標籤
2. 可以看到所有系統日誌
3. 在過濾器中輸入你的 APP 名稱
4. 查看錯誤訊息和 console.log 輸出
```

### 3. Vue DevTools（開發模式）

```bash
# 在瀏覽器中測試時使用
npm run dev
# 訪問 http://localhost:5173
# 使用 Vue DevTools 瀏覽器擴充套件
```

---

## 📊 效能監控

### 在模擬器中：

1. 點擊模擬器的 **...** （更多選項）
2. 選擇 **Settings** → **Advanced** → **Performance**
3. 調整：
   ```
   Graphics: Hardware - GLES 2.0 （最快）
   Boot option: Quick boot （快速啟動）
   ```

---

## 🔄 重新整理 APP

### 方法 1：重新執行（完全重新安裝）
```
1. 點擊停止按鈕（■）
2. 點擊執行按鈕（▶️）
```

### 方法 2：熱重載（如果支援）
```
在模擬器中：
1. 搖動裝置（Ctrl + M）
2. 或在 APP 中下拉重新整理
```

### 方法 3：清除資料重新開始
```
在模擬器中：
1. 長按 APP 圖示
2. App info → Storage → Clear Data
3. 重新開啟 APP
```

---

## 🎯 快速測試流程

### 完整測試（推薦）：

```bash
# 1. 在 WSL2 中修改程式碼
vim /root/project/citizenApp/src/main/js/citizen-portal/src/App.vue

# 2. 同步到 Windows
/root/project/citizenApp/sync-to-windows.sh

# 3. 在 Android Studio 中
# - File → Sync Project with Gradle Files
# - 點擊 ▶️ Run（會自動重新安裝）
```

### 快速迭代（Web 測試）：

```bash
# 在瀏覽器中快速測試 UI 變更
npm run dev
# 訪問 http://localhost:5173
# 修改程式碼立即看到效果（熱重載）

# 確認無誤後再同步到 Android
```

---

## 🎓 第一次使用建議流程

### Day 1：熟悉環境
1. ✅ 建立一個模擬器
2. ✅ 成功啟動你的 APP
3. ✅ 嘗試在 APP 中導航

### Day 2：簡單修改
1. ✅ 修改一個文字
2. ✅ 執行 sync-to-windows.sh
3. ✅ 在模擬器中看到變更

### Day 3：進階開發
1. ✅ 使用 Chrome DevTools 除錯
2. ✅ 查看 Logcat 日誌
3. ✅ 了解元件結構

---

## ❓ 常見問題

### Q: 模擬器很慢怎麼辦？
A: 
1. 確保電腦已啟用硬體虛擬化（BIOS 中的 VT-x/AMD-V）
2. 增加模擬器的 RAM 配置
3. 選擇較舊的 Android 版本（API 30 比 API 34 快）

### Q: 找不到我的 APP？
A: 
1. 確認 APP 已成功安裝（查看 Run 面板的輸出）
2. 在模擬器中打開應用程式清單
3. 搜尋你的 APP 名稱

### Q: APP 一片空白？
A: 
1. 確認 `npm run build` 已執行
2. 確認 `npx cap sync` 已執行
3. 查看 Chrome DevTools Console 是否有錯誤
4. 檢查 API 連接設定

---

**💡 小技巧**：第一次使用建議先用模擬器熟悉流程，之後再嘗試真機測試！
