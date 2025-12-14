# 🔐 Android 模擬器 SSL 連接問題解決心路歷程

> **專案**：市民意見平台 (Citizen App)
> **問題**：Android 模擬器無法連接 HTTPS API
> **解決日期**：2025-12-14
> **耗時**：約 3 小時
> **難度**：⭐⭐⭐⭐⭐

---

## 📋 目錄

1. [問題發現](#問題發現)
2. [技術背景](#技術背景)
3. [解決歷程](#解決歷程)
4. [最終方案](#最終方案)
5. [經驗教訓](#經驗教訓)
6. [參考資源](#參考資源)

---

## 🔍 問題發現

### 初始症狀

在完成 HTTPS 配置後，發現 Android 模擬器無法載入任何資料：

```
[ERROR:net/socket/ssl_client_socket_impl.cc:916]
handshake failed; returned -1, SSL error code 1, net_error -202

File: http://localhost/assets/List-DZSNat-P.js - Line 1 - Msg:
Failed to fetch categories: [object Object]
```

**關鍵觀察：**
- ✅ 後台管理系統（網頁版）運行正常
- ✅ 伺服器 HTTPS 服務正常運行
- ✅ SSH 隧道成功建立
- ❌ Android 模擬器無法連接 API

---

## 🏗️ 技術背景

### 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                    開發環境 (WSL2 + Windows)                 │
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  Android     │         │  開發主機     │                  │
│  │  模擬器      │◄───────►│  localhost   │                  │
│  │  (Pixel 7)   │ 虛擬網路 │              │                  │
│  └──────────────┘         └──────┬───────┘                  │
│         │                        │                           │
│         │                        │ SSH 隧道                  │
│         │ 10.0.2.2:8443         │ (加密)                    │
│         │                        │                           │
└─────────┼────────────────────────┼───────────────────────────┘
          │                        │
          │                        ▼
          │              ┌──────────────────┐
          │              │   遠端伺服器      │
          └─────────────►│ 140.123.105.199  │
            (透過主機)    │   Port: 8443     │
                         │   (HTTPS)        │
                         └──────────────────┘
```

### 關鍵技術點

1. **Android 模擬器網路**
   - 使用 NAT 模式，無法直接訪問主機的 VPN 網路
   - 特殊 IP `10.0.2.2` 代表主機（host machine）

2. **SSH 隧道**
   - 作用：將本地端口轉發到遠端伺服器
   - 指令：`ssh -N -L 8443:140.123.105.199:8443 user@server`
   - 特性：僅做 TCP 封包轉發，不做協議轉換

3. **自簽名 SSL 證書**
   - 伺服器使用自簽名證書（非公信 CA 簽發）
   - 瀏覽器/應用程式預設不信任
   - 需要手動配置信任

---

## 🚀 解決歷程

### 第一階段：環境變數誤判 ❌

**問題發現：**
```javascript
const isDevelopment = import.meta.env.DEV || import.meta.env.MODE === 'development'

if (isDevelopment) {
  return 'https://10.0.2.2:8443/'  // 模擬器
}
return 'https://140.123.105.199:8443/'  // 生產環境
```

**錯誤原因：**
- Capacitor 建置 Android 應用時使用**生產模式**
- `import.meta.env.DEV` 為 `false`
- 應用程式錯誤地使用了生產環境 URL (140.123.105.199)
- Android 模擬器無法透過 VPN 訪問該 IP

**Logcat 證據：**
```
Environment: {mode: 'production', dev: false, prod: true}
```

**修復方案：**
```javascript
if (Capacitor.isNativePlatform()) {
  const platform = Capacitor.getPlatform()

  if (platform === 'android') {
    return 'https://10.0.2.2:8443/'  // 直接使用模擬器 IP
  }
}
```

**結果：**
- ✅ 應用程式開始嘗試連接 `10.0.2.2:8443`
- ❌ 但仍然出現 SSL 握手錯誤
- 錯誤碼從 `-202` 變為 `-200`

---

### 第二階段：證書信任問題 ⚠️

**新錯誤：**
```
net_error -200 (ERR_CERT_COMMON_NAME_INVALID)
```

**進展分析：**
- `-202` = `ERR_CERT_AUTHORITY_INVALID` → 不信任證書頒發機構
- `-200` = `ERR_CERT_COMMON_NAME_INVALID` → 證書主機名稱不匹配

這表示我們解決了第一個問題（應用程式現在連接到正確的 IP），但遇到了新問題！

**根本原因：**
```
應用程式連接：10.0.2.2
證書簽發給：   140.123.105.199
結果：         主機名稱不匹配 ❌
```

**嘗試方案 1：加入應用程式內建證書**

```xml
<!-- network_security_config.xml -->
<domain-config cleartextTrafficPermitted="false">
    <domain includeSubdomains="true">10.0.2.2</domain>
    <trust-anchors>
        <certificates src="@raw/server_cert" />
        <certificates src="system" />
        <certificates src="user" />
    </trust-anchors>
</domain-config>
```

**結果：**
- ✅ Android 開始信任證書頒發機構
- ❌ 但主機名稱驗證仍然失敗
- 仍然出現 `-200` 錯誤

**為什麼這樣不行？**

Android 的 Network Security Config 無法停用主機名稱驗證。即使信任了證書，但當：
- 連接 IP 是 `10.0.2.2`
- 證書 CN (Common Name) 是 `140.123.105.199`

系統仍然會拒絕連接！

---

### 第三階段：考慮使用 HTTP ❌

**想法：**
既然 SSH 隧道已經提供加密，是否可以在模擬器到主機之間使用 HTTP？

```javascript
return 'http://10.0.2.2:8443/'  // 使用 HTTP
```

**為什麼這樣不行？**

SSH 隧道只做 **TCP 封包轉發**，不做協議轉換：

```
Android App → HTTP 請求 → 10.0.2.2:8443
                ↓
          SSH 隧道（轉發 TCP）
                ↓
         140.123.105.199:8443 → 期待 HTTPS 握手
                ↓
            協議不匹配！❌
```

如果應用程式發送 HTTP 請求，伺服器會期待 TLS 握手，導致連接失敗。

---

### 第四階段：重新生成證書（包含 SAN） ✅

**最終方案：**

重新生成 SSL 證書，在 **Subject Alternative Names (SAN)** 中包含所有可能的主機名稱：

```bash
# 使用 OpenSSL 配置檔案
[v3_req]
subjectAltName = IP:140.123.105.199,IP:10.0.2.2,DNS:localhost
```

**腳本更新：**

```bash
# 建立臨時 OpenSSL 配置檔案
TEMP_CONFIG=$(mktemp)
cat > "$TEMP_CONFIG" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
C=TW
ST=Chiayi
L=Chiayi
O=CCU
CN=140.123.105.199

[v3_req]
subjectAltName = IP:140.123.105.199,IP:10.0.2.2,DNS:localhost
EOF

# 生成證書
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout selfsigned.key \
    -out selfsigned.crt \
    -config "$TEMP_CONFIG"
```

**驗證 SAN：**

```bash
$ openssl x509 -in selfsigned.crt -noout -text | grep -A 2 "Subject Alternative Name"

X509v3 Subject Alternative Name:
    IP Address:140.123.105.199, IP Address:10.0.2.2, DNS:localhost
```

✅ **成功！**

---

## ✅ 最終方案

### 完整配置清單

#### 1. 伺服器端 (140.123.105.199)

```bash
# 生成包含 SAN 的證書
cd ~/cityAPP
bash scripts/generate_ssl_cert.sh

# 重啟 HTTPS 服務
systemctl --user restart citizenapp
```

#### 2. 前端配置 (axios.js)

```javascript
const getBaseURL = () => {
  if (Capacitor.isNativePlatform()) {
    const platform = Capacitor.getPlatform()

    if (platform === 'android') {
      // Android 模擬器：透過 SSH 隧道
      return 'https://10.0.2.2:8443/'
    }

    // 真實裝置：透過 VPN
    return 'https://140.123.105.199:8443/'
  }

  // 網頁瀏覽器：直接訪問
  return 'https://140.123.105.199:8443/'
}
```

#### 3. Android 配置 (network_security_config.xml)

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- 基礎配置 -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>

    <!-- 開發環境覆寫 -->
    <debug-overrides>
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>

    <!-- 生產伺服器配置 -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">140.123.105.199</domain>
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </domain-config>

    <!-- 模擬器開發配置 -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">10.0.2.2</domain>
        <domain includeSubdomains="true">localhost</domain>
        <trust-anchors>
            <!-- 信任應用程式內建的證書 -->
            <certificates src="@raw/server_cert" />
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </domain-config>
</network-security-config>
```

#### 4. 證書檔案配置

```
android/app/src/main/res/raw/server_cert.crt  ← 伺服器證書（包含 SAN）
```

#### 5. SSH 隧道

```powershell
ssh -o KexAlgorithms=curve25519-sha256 `
    -o HostKeyAlgorithms=ssh-ed25519,ecdsa-sha2-nistp256,rsa-sha2-512 `
    -N -L 8443:140.123.105.199:8443 `
    se_city@140.123.105.199
```

#### 6. .gitignore 配置

```gitignore
# SSL/TLS Certificates (NEVER commit!)
*.crt
*.key
*.pem
*.p12
*.pfx
selfsigned.*
```

---

## 📊 問題演進時間線

```
19:00  發現 Android 模擬器無法載入資料
       錯誤：net_error -202 (ERR_CERT_AUTHORITY_INVALID)

19:10  分析 Logcat，發現 Environment: {mode: 'production'}
       ├─ 修復：改用 Capacitor.getPlatform() 檢測
       └─ 結果：錯誤變為 -200 (ERR_CERT_COMMON_NAME_INVALID)

19:20  理解問題：證書主機名稱不匹配
       ├─ 嘗試：加入應用程式內建證書
       └─ 結果：仍然失敗，主機名稱驗證無法繞過

19:30  考慮使用 HTTP
       ├─ 理解：SSH 隧道只做 TCP 轉發，不能改協議
       └─ 結果：放棄此方案

19:40  決定：重新生成證書，加入 SAN
       ├─ 更新證書生成腳本
       ├─ 在伺服器生成新證書
       ├─ 下載並更新 Android 應用程式
       └─ 結果：✅ 成功！

19:50  驗證所有功能正常運作
```

---

## 💡 經驗教訓

### 技術要點

#### 1. Android 模擬器網路特性

**關鍵認知：**
- Android 模擬器使用 **NAT 網路模式**
- 無法直接訪問主機的 VPN 連線
- 必須使用 `10.0.2.2` 訪問主機

**錯誤示範：**
```javascript
// ❌ 模擬器無法訪問 VPN 網路
return 'https://140.123.105.199:8443/'
```

**正確做法：**
```javascript
// ✅ 透過主機轉發
return 'https://10.0.2.2:8443/'
```

#### 2. SSL/TLS 證書驗證機制

**兩個層次的驗證：**

1. **證書頒發機構驗證** (Certificate Authority)
   - 檢查證書是否由受信任的 CA 簽發
   - 自簽名證書需要手動加入信任清單

2. **主機名稱驗證** (Hostname Verification)
   - 檢查證書的 CN 或 SAN 是否與訪問的主機名稱匹配
   - **無法在 Android Network Security Config 中停用**

**關鍵概念：SAN (Subject Alternative Names)**

```
傳統證書：只有一個 Common Name (CN)
現代證書：可以有多個 SAN 條目

範例：
CN: 140.123.105.199
SAN:
  - IP:140.123.105.199  (生產環境)
  - IP:10.0.2.2         (開發環境)
  - DNS:localhost       (本地測試)
```

#### 3. SSH 隧道工作原理

**常見誤解：**
> "SSH 隧道加密了，所以可以在兩端使用不同協議"

**實際情況：**
```
SSH 隧道 = TCP 封包轉發 + 加密

應用程式 → HTTPS 請求 → SSH 隧道 → 伺服器
           (TLS 握手)     (轉發)     (期待 TLS)

應用程式 → HTTP 請求  → SSH 隧道 → 伺服器
           (普通 HTTP)    (轉發)     (期待 TLS) ❌
```

SSH 隧道不會改變應用層協議！

#### 4. Vite/Vue 環境變數陷阱

**問題：**
```javascript
// ❌ 這在 Capacitor 建置時不可靠
if (import.meta.env.DEV) { ... }
```

**原因：**
- Capacitor 建置流程：`npm run build` → 生產模式
- `import.meta.env.DEV` 會是 `false`
- 即使在開發環境也是如此！

**解決方案：**
```javascript
// ✅ 使用執行時檢測
if (Capacitor.isNativePlatform()) {
  const platform = Capacitor.getPlatform()
  // 根據平台決定 URL
}
```

#### 5. Android Network Security Config 限制

**可以做的：**
- ✅ 信任自訂 CA
- ✅ 信任使用者安裝的證書
- ✅ 信任應用程式內建的證書
- ✅ 允許/禁止明文流量

**不能做的：**
- ❌ 停用主機名稱驗證
- ❌ 接受任何證書（trustAll）
- ❌ 自訂 SSL/TLS 驗證邏輯

---

### 最佳實踐

#### 1. 開發環境證書配置

**推薦方案：**

```bash
# 生成包含所有環境的 SAN 證書
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout server.key \
    -out server.crt \
    -config <(cat <<EOF
[req]
distinguished_name = dn
x509_extensions = v3_req

[dn]
CN = production.server.ip

[v3_req]
subjectAltName = IP:production.ip,IP:10.0.2.2,DNS:localhost,DNS:*.dev.local
EOF
)
```

**優點：**
- 一個證書支援多個環境
- 不需要為不同環境生成不同證書
- 簡化部署流程

#### 2. 證書管理策略

**安全考量：**

```gitignore
# .gitignore - 絕對不要提交證書！
*.crt
*.key
*.pem
*.p12
*.pfx
```

**部署策略：**

1. **開發環境：** 使用自簽名證書，包含開發用 IP/域名
2. **測試環境：** 使用自簽名證書或內部 CA
3. **生產環境：** 使用公信 CA 簽發的證書

#### 3. 多平台 URL 配置模式

**推薦架構：**

```javascript
// api/config.js
export const getBaseURL = () => {
  // 1. 檢測平台
  if (Capacitor.isNativePlatform()) {
    const platform = Capacitor.getPlatform()

    // 2. Android 特殊處理
    if (platform === 'android') {
      // 檢測是否為模擬器（可選）
      // 目前直接假設是模擬器
      return 'https://10.0.2.2:8443/'
    }

    // 3. iOS 或其他平台
    return 'https://production.server.ip:8443/'
  }

  // 4. 網頁瀏覽器
  return 'https://production.server.ip:8443/'
}
```

**進階版本：**

```javascript
// 支援環境變數覆寫
export const getBaseURL = () => {
  // 開發時可以透過環境變數覆寫
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }

  if (Capacitor.isNativePlatform()) {
    const platform = Capacitor.getPlatform()

    if (platform === 'android') {
      // 可以透過 Android 特定的配置覆寫
      return 'https://10.0.2.2:8443/'
    }

    return 'https://production.server.ip:8443/'
  }

  return 'https://production.server.ip:8443/'
}
```

#### 4. 除錯技巧

**有效的除錯方法：**

1. **檢查實際使用的 URL**
```javascript
// 在 axios.js 中加入 console.log
console.log('Axios baseURL:', instance.defaults.baseURL)
```

2. **分析錯誤碼**
```
-200: ERR_CERT_COMMON_NAME_INVALID (主機名稱不匹配)
-201: ERR_CERT_DATE_INVALID (證書過期)
-202: ERR_CERT_AUTHORITY_INVALID (不信任的 CA)
-203: ERR_CERT_CONTAINS_ERRORS (證書有錯誤)
```

3. **驗證證書內容**
```bash
# 檢查 CN 和 SAN
openssl x509 -in cert.crt -noout -text | grep -A 2 "Subject Alternative Name"

# 檢查有效期
openssl x509 -in cert.crt -noout -dates

# 完整資訊
openssl x509 -in cert.crt -noout -text
```

4. **測試 SSH 隧道**
```powershell
# Windows 測試隧道是否運作
curl.exe -k https://localhost:8443/health
```

5. **查看 Android Logcat**
```bash
# 過濾 SSL 相關錯誤
adb logcat | grep -i "ssl\|certificate\|handshake"

# 過濾應用程式日誌
adb logcat | grep "com.citizenapp"
```

---

### 常見陷阱

#### 陷阱 1：誤以為 SSH 隧道會處理 SSL

**錯誤想法：**
> "SSH 已經加密了，我可以用 HTTP 連接 SSH 隧道"

**正確認知：**
- SSH 隧道只負責加密**傳輸通道**
- 應用層協議（HTTP/HTTPS）不受影響
- 必須端到端使用相同協議

#### 陷阱 2：依賴建置時環境變數

**錯誤做法：**
```javascript
// ❌ Capacitor 建置時這永遠是 false
if (import.meta.env.DEV) { ... }
```

**正確做法：**
```javascript
// ✅ 執行時檢測
if (Capacitor.isNativePlatform()) { ... }
```

#### 陷阱 3：忽略證書主機名稱驗證

**錯誤想法：**
> "我已經把證書加入信任了，為什麼還是失敗？"

**正確認知：**
- 信任 CA ≠ 通過主機名稱驗證
- 必須確保證書的 CN 或 SAN 包含訪問的主機名稱

#### 陷阱 4：在 Git 提交證書

**危險做法：**
```bash
git add *.crt  # ❌ 絕對不要！
```

**後果：**
- 證書暴露在公開倉庫
- 安全風險
- 難以撤銷（Git 歷史記錄）

**正確做法：**
```gitignore
# .gitignore
*.crt
*.key
*.pem
```

---

## 🎯 檢查清單

### 開發環境設置檢查

- [ ] SSH 隧道正確配置
  ```bash
  ssh -N -L 8443:server:8443 user@server
  ```

- [ ] 證書包含所有必要的 SAN
  ```bash
  openssl x509 -in cert.crt -noout -text | grep "Subject Alternative Name"
  ```

- [ ] Android 應用程式使用正確的 URL
  ```javascript
  return 'https://10.0.2.2:8443/'  // 模擬器
  ```

- [ ] Network Security Config 正確配置
  ```xml
  <certificates src="@raw/server_cert" />
  ```

- [ ] 證書檔案已加入 .gitignore
  ```gitignore
  *.crt
  *.key
  ```

### 部署前檢查

- [ ] 切換到生產環境 URL
  ```javascript
  return 'https://140.123.105.199:8443/'
  ```

- [ ] 移除除錯用的 console.log

- [ ] 確認使用生產環境證書

- [ ] 測試真實裝置 + VPN 連線

### 除錯檢查

- [ ] 檢查 Logcat 中的 baseURL 輸出
- [ ] 確認 SSH 隧道正在運行
- [ ] 測試證書有效期
- [ ] 驗證網路連通性

---

## 📚 參考資源

### 官方文檔

1. **Android Network Security Configuration**
   - https://developer.android.com/training/articles/security-config

2. **Capacitor Platform Detection**
   - https://capacitorjs.com/docs/core-apis/device

3. **OpenSSL SAN 證書生成**
   - https://www.openssl.org/docs/man1.1.1/man5/x509v3_config.html

### 相關錯誤碼

| 錯誤碼 | 常數名稱 | 意義 | 解決方案 |
|--------|----------|------|----------|
| -200 | ERR_CERT_COMMON_NAME_INVALID | 主機名稱不匹配 | 在證書 SAN 中加入訪問的 IP/域名 |
| -201 | ERR_CERT_DATE_INVALID | 證書過期或未生效 | 重新生成證書 |
| -202 | ERR_CERT_AUTHORITY_INVALID | 不信任的 CA | 將證書加入信任清單 |
| -203 | ERR_CERT_CONTAINS_ERRORS | 證書格式錯誤 | 檢查證書是否正確生成 |

### 有用的指令

```bash
# 檢查證書詳細資訊
openssl x509 -in cert.crt -noout -text

# 檢查證書 SAN
openssl x509 -in cert.crt -noout -text | grep -A 3 "Subject Alternative Name"

# 檢查證書有效期
openssl x509 -in cert.crt -noout -dates

# 測試 HTTPS 連線（忽略證書驗證）
curl -k https://localhost:8443/health

# Android Logcat 即時監控
adb logcat | grep -i "ssl\|certificate"

# 檢查 SSH 隧道狀態（Linux/Mac）
lsof -i :8443

# 檢查 SSH 隧道狀態（Windows）
netstat -ano | findstr :8443
```

---

## 🎓 總結

### 核心問題

Android 模擬器透過 SSH 隧道訪問 HTTPS 伺服器時，會遇到兩個主要問題：

1. **環境檢測問題**：Capacitor 建置的應用程式在生產模式下運行
2. **證書驗證問題**：證書主機名稱與訪問 IP 不匹配

### 解決方案

1. **使用執行時平台檢測**，而非建置時環境變數
2. **生成包含多個 SAN 的證書**，涵蓋所有訪問路徑
3. **將證書加入 Android 應用程式資源**，並配置 Network Security Config

### 關鍵學習

- 🔑 理解 Android 模擬器的網路架構
- 🔑 掌握 SSL/TLS 證書驗證機制
- 🔑 了解 SSH 隧道的工作原理
- 🔑 學會使用正確的除錯工具和方法

### 未來優化

1. **生產環境部署**
   - 使用公信 CA 簽發的證書
   - 配置 CDN 和負載平衡

2. **開發環境改進**
   - 實現模擬器自動檢測
   - 支援環境變數覆寫

3. **安全性增強**
   - 實施證書 Pinning
   - 加入證書輪換機制

---

**文件版本：** 1.0
**最後更新：** 2025-12-14
**作者：** Claude Code + 開發團隊
**專案：** 市民意見平台 (Citizen App)

---

> 💡 **經驗分享**
>
> 這次問題解決過程雖然耗時，但讓我們深入理解了 Android 網路安全配置、SSL/TLS 證書機制，以及行動應用開發的諸多細節。
>
> 記住：**除錯不是失敗，而是學習的過程**。每一個錯誤都是通往正確方案的墊腳石。
>
> 希望這份文件能幫助遇到類似問題的開發者！🚀
