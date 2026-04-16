# 🇹🇼 台灣股市 7 日行情 Web API

這是一個基於 **FastAPI** 與 **yfinance** 實作的簡單 Web API。使用者只需輸入台灣股票代碼（如：2330），即可獲取該公司的中文/英文名稱以及最近 7 個交易日的股價與交易量數據。



## ✨ 功能特點
* **自動識別市場**：自動嘗試上市 (.TW) 或上櫃 (.TWO) 代碼，不需手動區分。
* **數據詳盡**：提供開盤、最高、最低、收盤價及交易量。
* **互動式文檔**：內建 Swagger UI，可直接在瀏覽器進行測試。

## 🚀 快速上手

### 1. 複製專案與安裝環境
```bash
# 複製專案
git clone <你的GitHub專案網址>
cd stock-webapi

# 建立並啟動虛擬環境 (Windows)
python -m venv venv
.\venv\Scripts\activate

# 安裝必要套件
pip install -r requirements.txt