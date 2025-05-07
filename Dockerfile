# 使用 Python 基礎映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製專案檔案
COPY . .

# 安裝必要的系統套件
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    apt-get clean

# 安裝 Chromium 依賴
RUN apt-get install -y libnss3 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm-dev libgtk-3-0 libasound2 libpangocairo-1.0-0 \
    fonts-liberation libappindicator3-1 xdg-utils

# 安裝 Playwright 和瀏覽器
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install chromium

# 開放 Port
EXPOSE 8080

# 啟動服務
CMD ["waitress-serve", "--listen=0.0.0.0:8080", "app:app"]