# 測試文檔 (Testing Documentation)

> **專案**: citizenApp - 市民意見平台
> **測試框架**: pytest, FastAPI TestClient
> **覆蓋範圍**: 後端 API 整合測試

---

## 📑 目錄

1. [測試概述](#測試概述)
2. [測試架構](#測試架構)
3. [快速開始](#快速開始)
4. [測試執行](#測試執行)
5. [測試模組說明](#測試模組說明)
6. [Fixtures 說明](#fixtures-說明)
7. [測試報告](#測試報告)
8. [常見問題](#常見問題)

---

## 測試概述

本專案採用自動化測試策略，涵蓋：

- **整合測試 (Integration Tests)**: 測試 API 端點的完整功能
- **單元測試 (Unit Tests)**: 測試獨立功能模組
- **認證測試**: 用戶註冊、登入、Token 驗證
- **意見管理測試**: CRUD、投票、留言、收藏功能
- **審核系統測試**: 核准、拒絕、合併、刪除操作

### 測試覆蓋率目標

| 模組 | 目標覆蓋率 | 優先級 |
|------|-----------|--------|
| 認證系統 | 95%+ | Critical |
| 意見管理 | 90%+ | Critical |
| 審核系統 | 90%+ | High |
| 媒體管理 | 85%+ | Medium |
| 通知系統 | 80%+ | Low |

---

## 測試架構

```
src/test/
├── conftest.py              # 共用 fixtures 和配置
├── README.md                # 本文件
├── unit/                    # 單元測試
│   └── (待實作)
└── integration/             # 整合測試
    ├── test_auth_api.py          # 認證 API 測試 (10+ 測試案例)
    ├── test_opinion_api.py       # 意見管理 API 測試 (15+ 測試案例)
    └── test_moderation_api.py    # 審核模組 API 測試 (10+ 測試案例)
```

### 配置文件

- `pytest.ini`: Pytest 全域配置
- `conftest.py`: 共用 fixtures (資料庫、認證、測試資料)
- `requirements.txt`: 測試依賴套件

---

## 快速開始

### 1. 安裝測試依賴

```bash
# 啟動虛擬環境
source venv/bin/activate

# 安裝測試套件
pip install pytest pytest-asyncio pytest-cov pytest-html httpx
```

### 2. 執行第一個測試

```bash
# 執行所有測試
pytest src/test/ -v

# 執行特定模組測試
pytest src/test/integration/test_auth_api.py -v
```

### 3. 查看測試覆蓋率

```bash
pytest src/test/ --cov=src/main/python --cov-report=html
# 開啟 htmlcov/index.html 查看報告
```

---

## 測試執行

### 使用測試腳本（推薦）

```bash
# 執行互動式測試腳本
./run_tests.sh

# 腳本提供以下選項:
# 1. 執行所有測試
# 2. 執行單元測試
# 3. 執行整合測試
# 4. 執行認證模組測試
# 5. 執行意見管理模組測試
# 6. 執行審核模組測試
# 7. 執行測試並生成 HTML 報告
# 8. 執行測試並生成覆蓋率報告
# 9. 執行快速測試 (排除 slow 標記)
# 10. 執行冒煙測試
```

### 使用 pytest 命令

#### 基本執行

```bash
# 執行所有測試
pytest

# 詳細輸出
pytest -v

# 顯示打印輸出
pytest -s

# 執行特定文件
pytest src/test/integration/test_auth_api.py

# 執行特定測試類別
pytest src/test/integration/test_auth_api.py::TestUserRegistration

# 執行特定測試函數
pytest src/test/integration/test_auth_api.py::TestUserRegistration::test_register_success
```

#### 使用標記 (Markers)

```bash
# 只執行整合測試
pytest -m integration

# 只執行認證相關測試
pytest -m auth

# 執行意見系統測試
pytest -m opinion

# 執行審核系統測試
pytest -m moderation

# 排除慢速測試
pytest -m "not slow"

# 只執行冒煙測試
pytest -m smoke
```

#### 測試覆蓋率

```bash
# 生成終端覆蓋率報告
pytest --cov=src/main/python --cov-report=term-missing

# 生成 HTML 覆蓋率報告
pytest --cov=src/main/python --cov-report=html

# 同時生成多種報告
pytest --cov=src/main/python --cov-report=html --cov-report=term-missing --cov-report=xml
```

#### 並行執行

```bash
# 安裝 pytest-xdist
pip install pytest-xdist

# 使用 4 個 CPU 核心並行執行
pytest -n 4

# 自動使用所有可用核心
pytest -n auto
```

#### 失敗重試

```bash
# 安裝 pytest-rerunfailures
pip install pytest-rerunfailures

# 失敗測試重試 2 次
pytest --reruns 2

# 失敗測試重試，間隔 1 秒
pytest --reruns 2 --reruns-delay 1
```

---

## 測試模組說明

### 1. 認證 API 測試 (`test_auth_api.py`)

**測試類別**:
- `TestUserRegistration`: 用戶註冊功能測試
- `TestUserLogin`: 用戶登入功能測試
- `TestUserAuthentication`: Token 認證測試
- `TestTokenValidation`: Token 驗證測試
- `TestRoleBasedAccess`: 角色權限測試

**測試案例對應**: TC-AUTH-001 ~ TC-AUTH-010
**需求對應**: REQ-001 (用戶認證系統)

**關鍵測試**:
- ✅ 成功註冊/登入流程
- ✅ 重複用戶名/郵箱驗證
- ✅ JWT Token 生成與驗證
- ✅ 無效 Token 拒絕
- ✅ 角色權限檢查

### 2. 意見管理 API 測試 (`test_opinion_api.py`)

**測試類別**:
- `TestOpinionCreation`: 意見建立測試
- `TestOpinionRetrieval`: 意見查詢測試
- `TestOpinionComments`: 留言功能測試
- `TestOpinionVoting`: 投票功能測試
- `TestOpinionCollection`: 收藏功能測試

**測試案例對應**: TC-OPIN-001 ~ TC-OPIN-015
**需求對應**: REQ-002 ~ REQ-005

**關鍵測試**:
- ✅ CRUD 操作完整性
- ✅ 分頁與篩選功能
- ✅ 投票與留言邏輯
- ✅ 收藏功能正確性
- ✅ 權限控制驗證

### 3. 審核模組 API 測試 (`test_moderation_api.py`)

**測試類別**:
- `TestOpinionApproval`: 意見核准測試
- `TestOpinionRejection`: 意見拒絕測試
- `TestOpinionMerge`: 意見合併測試
- `TestCommentDeletion`: 留言刪除測試
- `TestCategoryUpdate`: 分類更新測試

**測試案例對應**: TC-MOD-001 ~ TC-MOD-010
**需求對應**: REQ-008, REQ-009

**關鍵測試**:
- ✅ 管理員審核權限
- ✅ 審核狀態轉換
- ✅ 意見合併邏輯
- ✅ 留言管理功能
- ✅ 角色權限驗證

---

## Fixtures 說明

### 資料庫 Fixtures

| Fixture | 作用域 | 說明 |
|---------|--------|------|
| `test_db_engine` | session | SQLite 記憶體資料庫引擎 |
| `test_db_session` | function | 每個測試獨立的資料庫 session |
| `cleanup_db` | function | 測試後清理資料庫 |

### 應用 Fixtures

| Fixture | 作用域 | 說明 |
|---------|--------|------|
| `test_app` | module | FastAPI 應用實例 |
| `test_client` | function | TestClient 實例 |

### 認證 Fixtures

| Fixture | 說明 |
|---------|------|
| `test_user_data` | 測試用戶資料字典 |
| `test_admin_data` | 測試管理員資料字典 |
| `test_moderator_data` | 測試審核員資料字典 |
| `create_test_user` | 建立測試用戶並返回用戶物件 |
| `create_test_admin` | 建立測試管理員並返回用戶物件 |
| `auth_headers_user` | 普通用戶的認證標頭 |
| `auth_headers_admin` | 管理員的認證標頭 |

### 意見系統 Fixtures

| Fixture | 說明 |
|---------|------|
| `test_opinion_data` | 測試意見資料字典 |
| `create_test_opinion` | 建立單個測試意見 |
| `create_multiple_opinions` | 建立多個不同狀態的測試意見 |

---

## 測試報告

### HTML 測試報告

```bash
# 生成 HTML 測試報告
pytest src/test/ --html=test_report.html --self-contained-html

# 開啟報告
# 報告位置: test_report.html
```

### 覆蓋率報告

```bash
# 生成 HTML 覆蓋率報告
pytest src/test/ --cov=src/main/python --cov-report=html

# 開啟報告
# 報告位置: htmlcov/index.html
```

### JUnit XML 報告 (CI/CD 集成)

```bash
# 生成 JUnit XML 報告 (用於 CI/CD)
pytest src/test/ --junit-xml=test-results.xml
```

### 終端報告

```bash
# 詳細終端輸出
pytest -v

# 顯示最慢的 10 個測試
pytest --durations=10

# 顯示測試摘要
pytest --tb=short
```

---

## 常見問題

### Q1: 測試失敗，提示找不到模組

**問題**: `ModuleNotFoundError: No module named 'models'`

**解決方案**:
```bash
# 確保 PYTHONPATH 包含專案根目錄
export PYTHONPATH=/root/project/citizenApp:$PYTHONPATH

# 或在 pytest.ini 中配置 pythonpath
# pythonpath = . src/main/python
```

### Q2: 資料庫連線錯誤

**問題**: `sqlalchemy.exc.OperationalError: unable to open database file`

**解決方案**:
- 測試使用記憶體資料庫，不需要實際資料庫
- 確保 `test_db_engine` fixture 正確配置
- 檢查 `conftest.py` 中的資料庫設定

### Q3: Token 驗證失敗

**問題**: `401 Unauthorized` 在需要認證的測試中

**解決方案**:
- 確保使用正確的 fixtures: `auth_headers_user` 或 `auth_headers_admin`
- 檢查 JWT Token 生成邏輯
- 驗證 `utils/security.py` 中的 Token 配置

### Q4: 測試執行緩慢

**解決方案**:
```bash
# 使用並行執行
pip install pytest-xdist
pytest -n auto

# 排除慢速測試
pytest -m "not slow"

# 只執行失敗的測試
pytest --lf  # last failed
pytest --ff  # failed first
```

### Q5: 如何調試失敗的測試

**解決方案**:
```bash
# 顯示打印輸出
pytest -s

# 在失敗時進入 pdb 調試器
pytest --pdb

# 顯示詳細回溯
pytest --tb=long

# 只執行失敗的測試
pytest --lf -v
```

### Q6: 如何跳過特定測試

**方法 1: 使用 skip 裝飾器**
```python
import pytest

@pytest.mark.skip(reason="功能尚未實作")
def test_future_feature():
    pass
```

**方法 2: 條件跳過**
```python
@pytest.mark.skipif(condition, reason="原因")
def test_something():
    pass
```

**方法 3: 命令列排除**
```bash
# 排除特定標記
pytest -m "not slow"

# 排除特定文件
pytest --ignore=src/test/integration/test_future.py
```

---

## 測試最佳實踐

### 1. 測試命名規範

- **文件**: `test_*.py` 或 `*_test.py`
- **類別**: `Test*` 或 `*Tests`
- **函數**: `test_*`
- **描述性命名**: `test_create_opinion_success`

### 2. 測試結構 (AAA 模式)

```python
def test_example():
    # Arrange - 準備測試資料
    user_data = {...}

    # Act - 執行操作
    response = client.post("/endpoint", json=user_data)

    # Assert - 驗證結果
    assert response.status_code == 200
    assert response.json()["id"] is not None
```

### 3. 使用 Fixtures

```python
def test_with_fixtures(test_client, auth_headers_user):
    # 使用預先準備的 fixtures
    response = test_client.get("/endpoint", headers=auth_headers_user)
    assert response.status_code == 200
```

### 4. 測試獨立性

- 每個測試應該獨立運行
- 不依賴其他測試的執行結果
- 使用 fixtures 準備測試環境

### 5. 清理資源

```python
@pytest.fixture
def resource():
    # 準備
    r = setup_resource()
    yield r
    # 清理
    cleanup_resource(r)
```

---

## CI/CD 集成

### GitHub Actions 範例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10

    - name: Install dependencies
      run: |
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt

    - name: Run tests
      run: |
        source venv/bin/activate
        pytest src/test/ --cov=src/main/python --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 聯絡與支援

- **測試文檔**: `/docs/testing/`
- **測試案例**: `/docs/testing/TEST_CASES.md`
- **追蹤矩陣**: `/docs/testing/TRACEABILITY_MATRIX.md`

---

**最後更新**: 2025-10-24
**維護者**: V&V Team
