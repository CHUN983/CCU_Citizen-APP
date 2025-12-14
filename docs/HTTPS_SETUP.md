# HTTPS 設定指南

## 📋 概述

本指南說明如何為 Citizen App 配置自簽名 HTTPS，適用於學校內部 VPN 環境。

## 🎯 為什麼使用 HTTPS？

1. ✅ **PWA 必要性**：Service Worker 需要 HTTPS 才能運作
2. ✅ **數據安全**：保護使用者帳號密碼和意見內容
3. ✅ **瀏覽器兼容**：避免瀏覽器「不安全」警告
4. ✅ **完整功能**：支援離線使用、推送通知等

## 🚀 快速部署（5 分鐘）

### 步驟 1：本地端推送更新

```bash
# 在本地開發機器上
cd /root/project/citizenApp

# 確認更改
git status

# 提交更改
git add -A
git commit -m "feat: 配置 HTTPS 支援"
git push origin claude
```

### 步驟 2：伺服器端部署

```bash
# SSH 連線到伺服器
ssh se_city@your_server_ip

# 進入專案目錄
cd ~/cityAPP

# 拉取最新代碼
git pull origin claude

# 1. 生成 SSL 證書
bash scripts/generate_ssl_cert.sh

# 2. 配置 HTTPS 服務
bash scripts/setup_https.sh

# 完成！服務現在運行在 HTTPS
```

### 步驟 3：驗證部署

```bash
# 測試 HTTPS 連接（-k 參數跳過證書驗證）
curl -k https://localhost:8443/health

# 應該返回：{"status":"healthy"}

# 查看服務狀態
systemctl --user status citizenapp

# 查看服務日誌
journalctl --user -u citizenapp -f
```

---

## 📱 手機端使用指南

### Android 手機（透過 VPN）

#### 首次使用步驟：

1. **連接學校 VPN** ✅
   ```
   連接到學校的 VPN
   確保可以訪問 140.123.105.199
   ```

2. **打開瀏覽器** 📱
   ```
   建議使用：Chrome、Firefox、Edge
   ```

3. **訪問 HTTPS 網址** 🌐
   ```
   https://140.123.105.199:8443
   ```

4. **信任自簽名證書** 🔒

   **Chrome/Edge**：
   ```
   1. 看到「您的連線不是私人連線」警告
   2. 點擊「進階」
   3. 點擊「繼續前往 140.123.105.199 (不安全)」
   4. 完成！
   ```

   **Firefox**：
   ```
   1. 看到「警告：潛在的安全性風險」
   2. 點擊「進階」
   3. 點擊「接受風險並繼續」
   4. 完成！
   ```

5. **安裝 PWA（可選）** 📲
   ```
   1. 網頁載入後，點擊瀏覽器選單
   2. 選擇「加到主畫面」或「安裝應用程式」
   3. 點擊「安裝」
   4. 現在可以像原生 App 一樣使用！
   ```

#### 重要提示：

- ✅ **只需信任一次**：每個裝置只需要在首次訪問時信任證書
- ✅ **安全性**：在 VPN 環境下，自簽名證書是安全的
- ✅ **完整功能**：信任證書後，所有 PWA 功能都可使用
- ⚠️ **證書警告是正常的**：這是自簽名證書的預期行為

---

## 🔧 技術細節

### SSL 證書資訊

- **類型**：自簽名 X.509 證書
- **演算法**：RSA 2048 位元
- **有效期**：365 天
- **位置**：
  - 證書：`~/cityAPP/ssl/selfsigned.crt`
  - 私鑰：`~/cityAPP/ssl/selfsigned.key`

### 服務配置

- **協議**：HTTPS
- **端口**：8443（從 8080 改為 8443）
- **證書**：自簽名證書
- **服務**：systemd --user

### 前端配置

- **API Base URL**：`https://140.123.105.199:8443/`
- **文件**：`src/main/js/citizen-portal/src/api/axios.js`

---

## 🔄 更新證書（一年後）

證書有效期為 365 天，到期前需要重新生成：

```bash
# 重新生成證書
bash ~/cityAPP/scripts/generate_ssl_cert.sh

# 重啟服務
systemctl --user restart citizenapp
```

---

## 🐛 常見問題

### Q1: 瀏覽器顯示「不安全」警告？

**A**: 這是正常的！自簽名證書會觸發此警告。
- 點擊「進階」→「繼續前往」即可
- 這不影響安全性（VPN 已加密）

### Q2: 無法連接到伺服器？

**A**: 檢查以下事項：
```bash
# 1. 確認服務運行中
systemctl --user status citizenapp

# 2. 確認端口正確（8443）
curl -k https://localhost:8443/health

# 3. 確認防火牆規則
# (如果有配置防火牆)
```

### Q3: PWA 仍然無法安裝？

**A**: 確保：
- ✅ 使用 HTTPS
- ✅ 已信任證書
- ✅ Service Worker 已註冊
- ✅ 使用支援 PWA 的瀏覽器（Chrome、Edge、Firefox）

### Q4: 想切換回 HTTP？

**A**: 修改 systemd 服務：
```bash
# 編輯服務文件
nano ~/.config/systemd/user/citizenapp.service

# 移除 --ssl-keyfile 和 --ssl-certfile 參數
# 將 8443 改回 8080

# 重新載入並重啟
systemctl --user daemon-reload
systemctl --user restart citizenapp
```

---

## 📞 需要幫助？

如果遇到問題：

1. **檢查服務日誌**：
   ```bash
   journalctl --user -u citizenapp -f
   ```

2. **檢查證書**：
   ```bash
   openssl x509 -in ~/cityAPP/ssl/selfsigned.crt -noout -text
   ```

3. **測試連接**：
   ```bash
   curl -k -v https://localhost:8443/health
   ```

---

## ✅ 部署檢查清單

- [ ] 本地端推送代碼到 GitHub
- [ ] 伺服器端拉取最新代碼
- [ ] 運行 `generate_ssl_cert.sh` 生成證書
- [ ] 運行 `setup_https.sh` 配置服務
- [ ] 驗證服務運行：`curl -k https://localhost:8443/health`
- [ ] 手機連接 VPN
- [ ] 手機訪問 `https://140.123.105.199:8443`
- [ ] 信任自簽名證書
- [ ] 安裝 PWA（可選）
- [ ] 測試所有功能

---

**配置完成！現在您可以在手機上享受完整的 PWA 體驗了！** 🎉
