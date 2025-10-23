# CI/CD 使用指南

## 🎯 什麼是 CI/CD？

**CI (Continuous Integration - 持續整合)**：
- 每次程式碼提交時，自動執行測試和檢查
- 確保新程式碼不會破壞現有功能
- 及早發現問題

**CD (Continuous Deployment - 持續部署)**：
- 測試通過後，自動部署到測試或生產環境
- 加快發布速度
- 減少人為錯誤

---

## 🚀 我們的 CI/CD Pipeline

### 自動化流程圖：
```
git push → GitHub Actions 觸發
    ↓
1️⃣ 程式碼品質檢查 (Linting, Formatting)
    ↓
2️⃣ 單元測試 (Unit Tests)
    ↓
3️⃣ API 健康檢查 (Health Check)
    ↓
4️⃣ 安全性掃描 (Security Scan)
    ↓
5️⃣ 構建 Docker Image (Build)
    ↓
6️⃣ 部署到測試環境 (Deploy)
    ↓
7️⃣ 通知結果 (Notification)
```

---

## 📋 Pipeline 包含的檢查

### 1. **程式碼品質檢查** (Code Quality)
- ✅ Flake8：檢查 Python 程式碼規範
- ✅ Black：檢查程式碼格式化
- ✅ Pylint：深度程式碼分析

### 2. **後端單元測試** (Backend Tests)
- ✅ 自動啟動 MySQL 測試資料庫
- ✅ 執行所有測試案例
- ✅ 生成測試覆蓋率報告

### 3. **API 健康檢查** (API Health Check)
- ✅ 啟動 FastAPI 伺服器
- ✅ 檢查所有端點是否正常
- ✅ 驗證 API 文件完整性

### 4. **安全性掃描** (Security Scan)
- ✅ Bandit：檢查程式碼安全漏洞
- ✅ Safety：檢查依賴套件漏洞

### 5. **Docker 構建** (Build)
- ✅ 構建 Docker Image
- ✅ 準備部署套件

### 6. **自動部署** (Deploy)
- ✅ 部署到測試環境（僅 main 分支）

---

## 🎮 如何使用

### **方式 1：自動觸發（推薦）**

每次 push 到 GitHub 時自動執行：

```bash
# 正常開發流程
git add .
git commit -m "your message"
git push origin main  # 👈 會自動觸發 CI/CD
```

**觸發條件**：
- Push 到 `main` 或 `develop` 分支
- 對 `main` 分支發起 Pull Request

### **方式 2：查看執行結果**

1. 打開 GitHub 倉庫
2. 點擊上方 **"Actions"** 標籤
3. 查看最新的 Workflow 執行狀態

![GitHub Actions](https://docs.github.com/assets/cb-33488/images/help/actions/workflow-run-list.png)

---

## 📊 Pipeline 執行時間

| Job | 預計時間 |
|-----|---------|
| 程式碼品質檢查 | ~30 秒 |
| 單元測試 | ~1-2 分鐘 |
| API 健康檢查 | ~1 分鐘 |
| 安全性掃描 | ~30 秒 |
| Docker 構建 | ~2-3 分鐘 |
| **總計** | **~5-7 分鐘** |

---

## ✅ 成功標誌

當所有檢查通過時，你會看到：

```
✅ Code Quality Checks     - passed
✅ Backend Unit Tests      - passed
✅ API Health Check        - passed
✅ Security Scan          - passed
✅ Build Docker Image      - passed
```

你的 commit 旁邊會出現綠色 ✅ 勾勾！

---

## ❌ 失敗處理

如果檢查失敗：

### 1. **查看錯誤訊息**
```bash
# 在 GitHub Actions 頁面點擊失敗的 job
# 查看詳細的錯誤訊息
```

### 2. **常見問題**

#### **Lint 錯誤**：
```bash
# 本地執行檢查
pip install flake8 black
flake8 src/main/python
black src/main/python

# 自動修復格式問題
black src/main/python --line-length 127
```

#### **測試失敗**：
```bash
# 本地執行測試
pytest src/test -v

# 查看詳細錯誤
pytest src/test -vv --tb=long
```

#### **API 健康檢查失敗**：
```bash
# 本地啟動伺服器測試
./setup_and_run.sh

# 測試健康端點
curl http://localhost:8000/health
```

---

## 🐳 Docker 使用

### **本地測試 Docker 環境**：

```bash
# 啟動完整環境（MySQL + Backend）
docker-compose up -d

# 查看日誌
docker-compose logs -f backend

# 停止環境
docker-compose down

# 重新構建
docker-compose up -d --build
```

### **訪問應用**：
- API: http://localhost:8000
- API 文件: http://localhost:8000/api/docs
- MySQL: localhost:3306

---

## 🔧 自定義 CI/CD

### **修改 Pipeline**

編輯 `.github/workflows/ci-cd.yml`：

```yaml
# 例如：跳過某個 job
jobs:
  security-scan:
    if: false  # 👈 暫時停用這個 job
```

### **添加環境變數**

在 GitHub 倉庫設置：
1. Settings → Secrets and variables → Actions
2. New repository secret
3. 添加敏感資訊（如 API Keys）

使用方式：
```yaml
env:
  MY_SECRET: ${{ secrets.MY_SECRET }}
```

---

## 📈 進階功能

### **1. 自動生成 Release**

```yaml
- name: Create Release
  uses: actions/create-release@v1
  with:
    tag_name: v${{ github.run_number }}
    release_name: Release v${{ github.run_number }}
```

### **2. 部署到真實伺服器**

```yaml
- name: Deploy to production
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.SERVER_HOST }}
    username: ${{ secrets.SERVER_USER }}
    key: ${{ secrets.SSH_KEY }}
    script: |
      cd /app
      git pull
      docker-compose up -d --build
```

### **3. Slack/Discord 通知**

```yaml
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🎯 最佳實踐

### ✅ **DO 建議做的**：
1. 每次提交前在本地先執行測試
2. 寫清楚的 commit message
3. 小步提交，頻繁整合
4. 修復 CI 失敗後再提交新代碼
5. 使用分支進行功能開發

### ❌ **DON'T 不建議做的**：
1. 不要直接在 main 分支開發
2. 不要忽略 CI 失敗
3. 不要提交大量未測試的代碼
4. 不要跳過本地測試直接 push
5. 不要在 CI 配置中寫入敏感資訊

---

## 📚 學習資源

- [GitHub Actions 官方文檔](https://docs.github.com/en/actions)
- [Docker 官方教學](https://docs.docker.com/get-started/)
- [CI/CD 最佳實踐](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment)

---

## 🆘 常見問題

### Q: CI 跑太久怎麼辦？
A: 可以使用 cache 加速：
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

### Q: 如何只在特定條件下執行？
A: 使用 `if` 條件：
```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
```

### Q: 本地如何模擬 CI 環境？
A: 使用 `act` 工具：
```bash
# 安裝 act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# 本地執行 workflow
act push
```

---

## 🎉 總結

我們的 CI/CD Pipeline 提供：
- ✅ 自動化測試與部署
- ✅ 7 個檢查流程
- ✅ Docker 容器化支援
- ✅ 安全性掃描
- ✅ 自動通知

每次 push 都會自動執行，確保代碼品質！

---

**文件版本**: 1.0
**更新日期**: 2025-10-24
**維護者**: Claude Code Team
