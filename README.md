# momo-web-testing-assignment

本專案為 momo 購物網 Web 自動化測試專案，使用 Python、pytest 與 Playwright 建立。

## 環境需求 (Prerequisites)

- Python 3.12+ (本環境使用 Python 3.13)

## 環境建置步驟 (Setup)

### 1. 建立並啟用虛擬環境 (Virtual Environment)

```bash
# 建立虛擬環境
python3 -m venv .venv

# 啟用虛擬環境
# macOS / Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

### 2. 安裝相依套件 (Install Dependencies)

```bash
pip install -r requirements.txt
```

### 3. 安裝 Playwright 瀏覽器 (Install Chromium)

本專案測試預設使用 Chromium：

```bash
playwright install chromium
```

## 執行測試 (Run Tests)

確保已啟用虛擬環境後，可直接透過 `pytest` 執行測試：

```bash
# 預設以 Headless 模式執行
pytest

# 以 Headed 模式（顯示瀏覽器視窗）執行
pytest --headed
```

## 專案結構 (Project Structure)

```text
.
├── AGENTS.md            # 開發與測試撰寫規範
├── README.md            # 專案環境建置與執行說明
├── pytest.ini           # pytest 設定檔
├── requirements.txt     # 專案相依套件定義
└── tests/
    └── test_smoke.py    # 基本 Smoke Test（驗證瀏覽器啟動與首頁連線）
```