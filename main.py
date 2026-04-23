import yfinance as yf
import pandas as pd
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse # 新增：用於回傳 HTML 檔案
import os

app = FastAPI()

# 1. 優先處理根目錄路徑，避免出現 Not Found
@app.get("/")
async def read_index():
    # 確保 index.html 放在 static 資料夾內
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "找不到 static/index.html，請檢查檔案位置"}

# 2. 掛載靜態資源 (CSS, JS, 圖片等)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

def get_sentiment(df):
    """計算趨勢指標"""
    if len(df) < 20:
        return "資料不足", "gray"
    
    df['MA20'] = df['Close'].rolling(window=20).mean()
    current_price = df['Close'].iloc[-1]
    current_ma20 = df['MA20'].iloc[-1]
    
    if current_price > current_ma20:
        return "樂觀 (多頭)", "green"
    elif current_price < current_ma20:
        return "悲觀 (空頭)", "red"
    else:
        return "盤整中", "orange"

# 3. 確保 API 路徑正確
@app.get("/api/stock/{symbol}")
async def get_stock(symbol: str):
    symbol = symbol.upper()
    # 嘗試 台灣證交所(.TW) 與 櫃買中心(.TWO)
    for suffix in [".TW", ".TWO"]:
        ticker_symbol = f"{symbol}{suffix}"
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period="3mo")
        
        if not df.empty:
            sentiment_text, color = get_sentiment(df)
            history_data = []
            for date, row in df.tail(10).iterrows():
                history_data.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "close": round(row['Close'], 2)
                })
            
            return {
                "symbol": symbol,
                "current_price": round(df['Close'].iloc[-1], 2),
                "sentiment": sentiment_text,
                "sentiment_color": color,
                "history": history_data
            }
            
    return {"error": f"找不到股票代碼 {symbol}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)