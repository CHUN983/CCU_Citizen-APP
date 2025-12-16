# 🔧 HTTPS 問題排查指南

## 📋 快速診斷清單

### 步驟 1️⃣：確認伺服器 HTTPS 狀態

在**伺服器**上執行：

```bash
# SSH 連線到伺服器
ssh se_city@your_server_ip

# 檢查服務狀態
systemctl --user status citizenapp

# 查看服務日誌（最後 50 行）
journalctl --user -u citizenapp -n 50

# 測試 HTTPS 是否運行
curl -k https://localhost:8443/health

# 測試 HTTP 是否已關閉（應該失敗）
curl http://localhost:8080/health
```

**預期結果**：
- ✅ HTTPS (8443)：`{"status":"healthy"}`
- ❌ HTTP (8080)：`curl: (7) Failed to connect`

### 步驟 2️⃣：如果服務未運行 HTTPS

```bash
# 進入專案目錄
cd ~/cityAPP

# 拉取最新代碼
git pull origin claude

# 生成 SSL 證書
bash scripts/generate_ssl_cert.sh

# 配置 HTTPS 服務
bash scripts/setup_https.sh

# 驗證服務
curl -k https://localhost:8443/health
```

---

## 🖥️ 問題 1：後台管理系統無法連接

### 錯誤訊息
```
Error: connect ECONNREFUSED 140.123.105.199:8080
```

### 原因
後台管理系統的 Vite 配置還在使用 HTTP 8080 端口。

### 解決方案

#### 在本地端：

```bash
# 1. 拉取最新代碼（已包含修復）
cd /root/project/citizenApp
git pull origin claude

# 2. 進入 admin-dashboard 目錄
cd src/main/js/admin-dashboard

# 3. 重新啟動開發伺服器
npm run dev
```

#### 驗證修復：

檢查 `vite.config.js` 是否已更新：
```javascript
proxy: {
  '/api': {
    target: 'https://140.123.105.199:8443/',  // ✅ HTTPS + 8443
    changeOrigin: true,
    secure: false, // ✅ 允許自簽名證書
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

---

## 📱 問題 2：手機 APP 載入意見失敗

### 可能原因與解決方案

#### 原因 A：伺服器未配置 HTTPS

**診斷**：
```bash
# 在伺服器上執行
curl -k https://localhost:8443/health
```

**如果失敗**：
```bash
# 配置 HTTPS
cd ~/cityAPP
bash scripts/generate_ssl_cert.sh
bash scripts/setup_https.sh
```

#### 原因 B：手機未信任證書

**症狀**：
- 瀏覽器顯示「連線不安全」
- 無法載入任何內容

**解決方案**：

1. **連接學校 VPN** ✅

2. **訪問 HTTPS 網址**：
   ```
   https://140.123.105.199:8443
   ```

3. **信任證書**（首次必須）：

   **Chrome/Edge**：
   ```
   1. 看到「您的連線不是私人連線」
   2. 點擊「進階」
   3. 點擊「繼續前往 140.123.105.199 (不安全)」
   ```

   **Firefox**：
   ```
   1. 看到「警告：潛在的安全性風險」
   2. 點擊「進階」
   3. 點擊「接受風險並繼續」
   ```

4. **驗證**：
   - 應該能看到登入頁面
   - 能正常載入意見列表

#### 原因 C：前端配置未更新

**診斷**：
檢查手機瀏覽器的開發者工具（如果可用）或檢查本地代碼。

**解決方案**：
```bash
# 確保前端使用 HTTPS
cd /root/project/citizenApp

# 檢查 citizen-portal 的 axios 配置
cat src/main/js/citizen-portal/src/api/axios.js | grep baseURL

# 應該看到：
# return 'https://140.123.105.199:8443/'
```

如果不是，拉取最新代碼：
```bash
git pull origin claude
```

---

## 🔍 詳細診斷步驟

### 檢查清單

#### ✅ 伺服器端

- [ ] 服務運行在 8443 端口
- [ ] HTTPS 健康檢查通過
- [ ] SSL 證書存在（`~/cityAPP/ssl/selfsigned.crt`）
- [ ] systemd 服務配置正確

**檢查指令**：
```bash
# 服務狀態
systemctl --user status citizenapp | grep Active

# 證書存在
ls -lh ~/cityAPP/ssl/

# HTTPS 測試
curl -k https://localhost:8443/health
```

#### ✅ 本地端（開發環境）

- [ ] 前端配置使用 HTTPS（axios.js）
- [ ] 後台配置使用 HTTPS（vite.config.js）
- [ ] 代碼已推送到 GitHub
- [ ] 本地開發服務器重啟

**檢查指令**：
```bash
# 檢查前端配置
grep "8443" src/main/js/citizen-portal/src/api/axios.js

# 檢查後台配置
grep "8443" src/main/js/admin-dashboard/vite.config.js

# Git 狀態
git log --oneline -3
```

#### ✅ 手機端

- [ ] 已連接學校 VPN
- [ ] 已信任自簽名證書
- [ ] 瀏覽器快取已清除（如果需要）
- [ ] 能訪問 `https://140.123.105.199:8443`

---

## 🚨 常見錯誤訊息

### 1. `ECONNREFUSED`
```
Error: connect ECONNREFUSED 140.123.105.199:8080
```
**原因**：嘗試連接 HTTP 8080，但服務運行在 HTTPS 8443
**解決**：更新配置為 HTTPS 8443

### 2. `SSL_ERROR_SELF_SIGNED_CERT`
```
SSL Error: Self-signed certificate
```
**原因**：瀏覽器不信任自簽名證書
**解決**：點擊「進階」→「繼續前往」

### 3. `ERR_CONNECTION_REFUSED`
```
ERR_CONNECTION_REFUSED
```
**原因**：服務未運行或端口錯誤
**解決**：檢查服務狀態，確認運行在 8443

### 4. `Service Worker registration failed`
```
Failed to register service worker
```
**原因**：未使用 HTTPS
**解決**：確認訪問 HTTPS 網址並信任證書

---

## 🔄 完整重置流程

如果以上都無效，執行完整重置：

### 伺服器端
```bash
# 1. 停止服務
systemctl --user stop citizenapp

# 2. 清理舊證書
rm -rf ~/cityAPP/ssl

# 3. 拉取最新代碼
cd ~/cityAPP
git pull origin claude

# 4. 重新生成證書
bash scripts/generate_ssl_cert.sh

# 5. 重新配置服務
bash scripts/setup_https.sh

# 6. 驗證
curl -k https://localhost:8443/health
```

### 本地端
```bash
# 1. 拉取最新代碼
cd /root/project/citizenApp
git pull origin claude

# 2. 重啟後台開發服務器
cd src/main/js/admin-dashboard
npm run dev

# 3. 重啟前端開發服務器（如果需要）
cd ../citizen-portal
npm run dev
```

### 手機端
```bash
# 1. 清除瀏覽器快取
設定 → 應用程式 → Chrome/Firefox → 清除資料

# 2. 重新連接 VPN

# 3. 重新訪問並信任證書
https://140.123.105.199:8443
```

---

## 📞 仍然無法解決？

### 收集診斷資訊

```bash
# 伺服器端
echo "=== 服務狀態 ==="
systemctl --user status citizenapp

echo "=== 服務日誌 ==="
journalctl --user -u citizenapp -n 100

echo "=== 證書資訊 ==="
ls -lh ~/cityAPP/ssl/
openssl x509 -in ~/cityAPP/ssl/selfsigned.crt -noout -text | head -20

echo "=== 端口監聽 ==="
ss -tlnp | grep -E "8080|8443"

echo "=== HTTPS 測試 ==="
curl -k -v https://localhost:8443/health 2>&1 | head -30
```

將輸出結果提供給技術支援。

---

## ✅ 驗證所有功能

完成修復後，依序測試：

### 伺服器
```bash
curl -k https://localhost:8443/health
# ✅ 預期：{"status":"healthy"}
```

### 後台管理系統
```bash
# 本地開發環境
npm run dev
# ✅ 預期：能正常登入和使用
```

### 手機端
```
1. 連接 VPN ✅
2. 訪問 https://140.123.105.199:8443 ✅
3. 信任證書 ✅
4. 能登入 ✅
5. 能載入意見列表 ✅
6. 能發表意見 ✅
```

---

**所有功能正常運作後，HTTPS 配置完成！** 🎉
