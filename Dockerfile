# 使用 Playwright 官方 Python 映像檔（包含預編譯之瀏覽器與系統相依庫）
FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

# 設定工作目錄
WORKDIR /app

# 安裝 Python 相依套件（利用 Layer Cache 避免程式碼修改時重新安裝）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製測試程式碼與設定檔
COPY . .

# 預設執行 pytest
CMD ["pytest"]
