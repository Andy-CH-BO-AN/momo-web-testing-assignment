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

### 1. 正常執行測試

```bash
# 預設以 Headless 模式執行（自動帶入 pytest.ini 中的配置）
pytest

# 以 Headed 模式（顯示瀏覽器視窗）執行
pytest --headed
```

### 2. 產生 HTML 測試報告

本專案採用 `pytest-html` 產生自包含（Self-contained）的 HTML 測試報告：

```bash
# 執行測試並產生自包含 report.html
pytest --html=report.html --self-contained-html
```

產生的 `report.html` 可直接以任何瀏覽器開啟檢視，無外部資源相依。

## 測試失敗除錯機制 (Failure Debugging)

專案已於 `pytest.ini` 設定 `pytest-playwright` 原生功能，**僅在測試失敗時自動收集除錯產物**：

- **失敗截圖**：`--screenshot only-on-failure`
- **執行軌跡**：`--tracing retain-on-failure`
- **產出位置**：統一儲存於 `test-results/` 目錄

### 除錯產物位置 (Artifacts Location)

若測試發生失敗，除錯產物會依測試案例放置於 `test-results/` 下：

```text
test-results/
└── <test-identifier>/
    ├── test-failed-1.png   # 失敗當下的頁面截圖
    └── trace.zip           # 包含 DOM Snapshot、Console、網路請求之 Playwright Trace
```

### 如何開啟與檢視 Trace

透過 Playwright CLI 的 `show-trace` 指令開啟視覺化 Trace Viewer：

```bash
# 檢視指定測試案例的 trace.zip
playwright show-trace test-results/<test-directory>/trace.zip
```

## Docker 執行環境 (Docker Environment)

為降低本機 Python、Chromium 或作業系統環境差異造成無法執行的風險，本專案提供 Docker 執行方式作為**可重現的替代執行選項**（不取代原本的 virtualenv + pip 本機開發流程）。

### 1. 建置 Docker 映像檔

映像檔採用微軟官方 Playwright Python 環境（內建相容之 Chromium 瀏覽器與系統依賴）：

```bash
docker build -t momo-tests .
```

### 2. 執行測試

```bash
# 預設執行 Headless 測試（容器預設指令即為 pytest）
docker run --rm --init --ipc=host momo-tests

# 執行測試並將 HTML 測試報告輸出至本機 test-results 目錄
docker run --rm --init --ipc=host -v $(pwd)/test-results:/app/test-results momo-tests pytest --html=test-results/report.html --self-contained-html
```

## 專案結構 (Project Structure)

```text
.
├── .dockerignore        # Docker build context 排除規則
├── AGENTS.md            # 開發與測試撰寫規範
├── Dockerfile           # Playwright 官方 Python 測試容器定義
├── README.md            # 專案環境建置與執行說明
├── pytest.ini           # pytest 設定檔（預設瀏覽器、除錯 artifacts 策略）
├── requirements.txt     # 專案相依套件定義
└── tests/
    └── test_smoke.py    # 基本 Smoke Test（驗證瀏覽器啟動與首頁連線）
```