import yfinance as yf
import pandas as pd
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # 修改這裡
import os

app = FastAPI()

# 修正後的掛載方式
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

def get_sentiment(df):
    """根據股價與 MA20 的關係判斷走勢 [cite: 34]"""
    if len(df) < 20:
        return "資料不足", "gray"
    
    # 計算 20日移動平均線 [cite: 29]
    df['MA20'] = df['Close'].rolling(window=20).mean()
    current_price = df['Close'].iloc[-1]
    current_ma20 = df['MA20'].iloc[-1]
    
    if current_price > current_ma20:
        return "樂觀 (多頭趨勢)", "green"
    elif current_price < current_ma20:
        return "悲觀 (空頭趨勢)", "red"
    else:
        return "盤整中", "orange"

@app.get("/api/stock/{symbol}")
async def get_stock(symbol: str):
    # 強制轉大寫以支援 00981A 等代碼 [cite: 26]
    symbol = symbol.upper()
    tickers = [f"{symbol}.TW", f"{symbol}.TWO"]
    
    for t in tickers:
        stock = yf.Ticker(t)
        df = stock.history(period="3mo") # 抓取三個月資料以計算均線
        
        if not df.empty:
            sentiment_text, color = get_sentiment(df)
            # 格式化資料回傳給前端 [cite: 22]
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
            
    return {"error": "找不到股票代碼或抓取失敗"}

if __name__ == "__main__":
    import uvicorn
    # 統一使用 0.0.0.0 配合環境變數，確保本機與雲端皆可連線 [cite: 6, 8, 21]
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)