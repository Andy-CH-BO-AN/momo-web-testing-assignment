# momo-web-testing-assignment

本專案以 momo 購物網搜尋功能為測試主題，使用 Python、pytest 與 Playwright 建立可重現的 Web E2E 自動化測試，涵蓋一般搜尋、邊界輸入、動態推薦與分頁結果一致性等情境。


## 測試範圍 (Test Scenarios)

目前搜尋功能涵蓋以下情境：

- 一般關鍵字搜尋：輸入一般關鍵字並透過搜尋按鈕送出，驗證搜尋結果與關鍵字一致性。
- 多關鍵字搜尋：透過 Enter 送出多關鍵字查詢，驗證至少有商品完整符合拆解後的搜尋詞。
- 無結果搜尋：使用不存在的關鍵字，驗證無結果訊息與商品數量。
- 分頁：驗證切換至第 2 頁後搜尋條件仍保留，且兩頁 organic product ID 不重複。
- 特殊字元：驗證包含特殊字元的搜尋詞可正確保留 query state 並取得相關結果。
- 空白輸入 + 搜尋按鈕：驗證網站使用當下動態 placeholder 作為搜尋詞。
- 僅空白字元輸入：驗證 whitespace-only query 進入明確的無結果狀態。
- 動態搜尋推薦：不 hardcode 推薦詞，從首頁「猜你想搜」取得第一個可見項目並驗證搜尋流程。
- 空白輸入 + Enter：驗證不觸發 navigation，並維持空白輸入狀態。

## 測試設計原則 (Test Design)

- **Page Object 職責分離**：Page Object 封裝 locator 與頁面操作；business assertions 保留於 testcase，讓測試意圖直接可讀。
- **State-based synchronization**：使用 Playwright auto-wait 與狀態 assertion，不使用固定時間的 `time.sleep`。
- **避免以 retry 掩蓋問題**：測試失敗直接反映實際狀態，不以 retry 隱藏 flaky behavior。
- **避免不必要的 hardcode**：例如首頁動態「猜你想搜」由 runtime 取得目前可見推薦詞，而非綁定固定文案。
- **驗證資料一致性**：分頁除了確認頁碼切換，也以 organic product ID 驗證單頁與跨頁結果不重複。

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

映像檔採用微軟官方 Playwright Python 環境（內建相容之 Chromium 瀏覽器與系統依賴）。Docker image 與 Python Playwright package 均固定於 `1.62.0`，避免瀏覽器、driver/runtime 與套件版本不一致造成環境差異：

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
├── conftest.py          # pytest 共用 fixture / hook 設定
├── README.md            # 專案環境建置與執行說明
├── pages/
│   ├── __init__.py      # pages package 初始化檔
│   └── search_page.py   # Search Page Object（封裝 Locator 與頁面動作）
├── pytest.ini           # pytest 設定檔（預設瀏覽器、除錯 artifacts 策略）
├── requirements.txt     # 專案相依套件定義
└── tests/
    └── test_search.py   # momo Search 功能自動化測試案例
```