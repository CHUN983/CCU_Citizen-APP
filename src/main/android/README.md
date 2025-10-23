# Android 專案目錄

此目錄包含 Android APP 的原始碼和配置。

## 快速開始

### 1. 開啟專案
```bash
# 使用 Android Studio 開啟此目錄
File → Open → 選擇 src/main/android
```

### 2. 同步 Gradle
```bash
# Android Studio 會自動提示同步
# 或手動執行：Build → Rebuild Project
```

### 3. 執行 APP
```bash
# 連接模擬器或實機
# 點擊綠色 ▶️ 按鈕
```

## 專案結構

```
android/
├── app/                          # 主要 APP 模組
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/citizenapp/
│   │   │   │   ├── data/        # 數據層
│   │   │   │   ├── domain/      # 業務邏輯層
│   │   │   │   ├── ui/          # UI 層
│   │   │   │   ├── di/          # 依賴注入
│   │   │   │   └── utils/       # 工具類
│   │   │   ├── res/             # 資源文件
│   │   │   └── AndroidManifest.xml
│   │   └── test/                # 測試
│   └── build.gradle.kts         # APP 級別配置
├── build.gradle.kts             # 專案級別配置
└── settings.gradle.kts          # 設定檔
```

## 配置文件

### build.gradle.kts (Project)
專案級別的 Gradle 配置，定義插件和倉庫。

### build.gradle.kts (App)
APP 級別的配置，包含：
- 依賴套件
- 編譯選項
- 版本配置

### local.properties
本地配置（不提交到 Git）：
```properties
sdk.dir=/Users/yourname/Library/Android/sdk
```

## API 配置

### 開發環境
```kotlin
BASE_URL = "http://10.0.2.2:8000/"  // 模擬器
```

### 真機測試
```kotlin
BASE_URL = "http://192.168.x.x:8000/"  // 改為電腦 IP
```

## 常見問題

### Q: Gradle 同步失敗？
A: 檢查網路連接，或使用 VPN

### Q: 模擬器很慢？
A: 增加 RAM 配置或使用真機

### Q: 無法連接 API？
A: 檢查 BASE_URL 配置

## 參考資源

- [開發規劃](../../docs/dev/ANDROID_DEVELOPMENT_PLAN.md)
- [API 文件](http://localhost:8000/api/docs)
- [後端文件](../../BACKEND_ENHANCEMENTS.md)
