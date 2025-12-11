# 測試文檔中心 (Testing Documentation Hub)

> **citizenApp - 市民意見平台**
>
> 這裡是所有測試相關文檔的中央導覽頁面

---

## 🎯 快速導覽

### 📊 **想快速了解測試進度？**
👉 [**測試儀表板 (TESTING_DASHBOARD.md)**](TESTING_DASHBOARD.md) ⭐ **推薦！**
- 一目了然的測試進度
- 模組測試狀態
- 當前優先事項
- 快速指標與圖表

### 📋 **想看詳細測試結果？**
👉 [**測試執行報告 (TEST_EXECUTION_REPORT.md)**](TEST_EXECUTION_REPORT.md)
- 完整測試執行分析 (21 KB)
- 根本原因分析
- 優先修復清單
- 覆蓋率詳細數據

### 📘 **想了解完整測試規格？**
👉 [**綜合測試報告 (COMPREHENSIVE_TEST_REPORT.md)**](COMPREHENSIVE_TEST_REPORT.md)
- 測試計畫與策略 (1,627 行)
- V&V 測試案例詳細說明
- 測試環境與人員配置
- 結論與建議

---

## 📚 完整文檔清單

| 文檔 | 說明 | 大小 | 狀態 |
|------|------|------|------|
| 🎯 [TESTING_DASHBOARD.md](TESTING_DASHBOARD.md) | 測試儀表板 - 快速進度導覽 | 15 KB | ✅ 最新 |
| 📊 [TEST_EXECUTION_REPORT.md](TEST_EXECUTION_REPORT.md) | 測試執行報告 - 詳細結果分析 | 21 KB | ✅ 最新 |
| 📘 [COMPREHENSIVE_TEST_REPORT.md](COMPREHENSIVE_TEST_REPORT.md) | 綜合測試報告 - 完整測試規格 | 90 KB | ✅ 最新 |
| 📖 [../../src/test/README.md](../../src/test/README.md) | 測試框架使用說明 | 20 KB | ✅ 最新 |
| 📑 [TEST_PLAN.md](TEST_PLAN.md) | 測試計畫 - 策略與目標 | 15 KB | ✅ 最新 |
| 📝 [TEST_CASES.md](TEST_CASES.md) | 測試案例 - 詳細案例列表 | 80 KB | ✅ 最新 |
| 🔗 [TRACEABILITY_MATRIX.md](TRACEABILITY_MATRIX.md) | 追溯矩陣 - 需求追溯關係 | 40 KB | ✅ 最新 |

---

## 🎯 按需求查找

### 我想...

#### 📊 **快速了解測試狀態**
→ 查看 [測試儀表板](TESTING_DASHBOARD.md)
- 當前通過率、覆蓋率
- 各模組進度
- 優先修復事項

#### 🐛 **了解測試失敗原因**
→ 查看 [測試執行報告](TEST_EXECUTION_REPORT.md)
- 詳細錯誤分析
- 根本原因識別
- 修復建議

#### 📝 **查看特定測試案例**
→ 查看 [測試案例文檔](TEST_CASES.md)
- TC-AUTH-001 ~ TC-AUTH-010: 認證測試
- TC-OPIN-001 ~ TC-OPIN-015: 意見管理測試
- TC-MOD-001 ~ TC-MOD-010: 審核系統測試
- TC-MED-001 ~ TC-MED-016: 媒體管理測試
- TC-NOT-001 ~ TC-NOT-014: 通知系統測試

#### 🔗 **確認需求是否有測試覆蓋**
→ 查看 [追溯矩陣](TRACEABILITY_MATRIX.md)
- 需求 → 測試案例對應
- 測試覆蓋率統計
- 風險評估

#### 🧪 **執行測試**
→ 查看 [測試框架說明](../../src/test/README.md)
- 測試執行命令
- Fixtures 使用說明
- 常見問題排除

#### 📋 **了解測試計畫**
→ 查看 [測試計畫](TEST_PLAN.md)
- 測試策略
- 測試環境配置
- 時程安排

---

## 📊 當前測試狀態概覽

> 最後更新: 2025-12-12 00:30 ✨ **重大更新**

```
🎯 測試完成度: █████████████████░░░ 83.5% ⬆️ +55.9%

✅ 通過:  81 個測試 (83.5%) ⬆️ +73
❌ 失敗:  13 個測試 (13.4%)
⚠️ 錯誤:  1 個測試 (1.0%) ⬇️ -15
⏭️ 跳過:  2 個測試 (2.1%)

📈 程式碼覆蓋率: 43% (+2%)
⚡ 執行時間: 3m 34s (完整測試套件)
```

**✅ 關鍵修復完成**: 資料庫初始化、Mock 路徑、依賴套件

[👉 查看完整儀表板](TESTING_DASHBOARD.md) | [📋 修復成果總結](TESTING_DASHBOARD.md#修復成果總結)

---

## 🛠️ 快速命令

```bash
# 執行所有測試
pytest src/test/integration/ -v

# 執行特定模組測試
pytest src/test/integration/test_auth_api.py -v

# 生成覆蓋率報告
pytest src/test/ --cov=src/main/python --cov-report=html

# 查看覆蓋率報告
python -m http.server 8080 --directory htmlcov

# 生成 Allure 報告 (需安裝 allure CLI)
pytest src/test/integration/ --alluredir=allure-results
allure serve allure-results
```

---

## 📞 需要協助？

| 問題類型 | 解決方案 |
|---------|---------|
| ❓ 測試執行問題 | 查看 [測試框架說明](../../src/test/README.md) 的「常見問題」章節 |
| 🐛 測試失敗分析 | 查看 [測試執行報告](TEST_EXECUTION_REPORT.md) 的「關鍵發現」章節 |
| 📋 新增測試案例 | 參考 [測試案例文檔](TEST_CASES.md) 的格式 |
| 🔗 需求追溯 | 查看 [追溯矩陣](TRACEABILITY_MATRIX.md) |
| 💬 其他問題 | 聯絡 qa-team@citizenapp.example.com |

---

## 🔄 文檔更新記錄

| 日期 | 更新內容 | 文檔 |
|------|---------|------|
| 2025-12-12 | 新增測試儀表板 | TESTING_DASHBOARD.md |
| 2025-12-12 | 新增測試執行報告 | TEST_EXECUTION_REPORT.md |
| 2025-10-24 | 新增綜合測試報告 | COMPREHENSIVE_TEST_REPORT.md |
| 2025-10-24 | 初始測試文檔建立 | TEST_PLAN.md, TEST_CASES.md |

---

<div align="center">

**🎯 推薦從 [測試儀表板](TESTING_DASHBOARD.md) 開始！**

[📊 儀表板](TESTING_DASHBOARD.md) | [📋 執行報告](TEST_EXECUTION_REPORT.md) | [📘 綜合報告](COMPREHENSIVE_TEST_REPORT.md)

---

**citizenApp Testing Documentation** | v1.0 | 2025-12-12

</div>
