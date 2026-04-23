import yfinance as yf
import pandas as pd
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

@app.get("/")
async def read_index():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "找不到 static/index.html"}

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

def get_sentiment(df):
    if len(df) < 20: return "資料不足", "gray"
    df['MA20'] = df['Close'].rolling(window=20).mean()
    current_price = df['Close'].iloc[-1]
    current_ma20 = df['MA20'].iloc[-1]
    if current_price > current_ma20: return "樂觀 (多頭)", "#28a745"
    elif current_price < current_ma20: return "悲觀 (空頭)", "#dc3545"
    else: return "盤整中", "#ffc107"

@app.get("/api/stock/{symbol}")
async def get_stock(symbol: str):
    symbol = symbol.upper()
    for suffix in [".TW", ".TWO"]:
        ticker_symbol = f"{symbol}{suffix}"
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period="3mo")
        
        if not df.empty:
            sentiment_text, color = get_sentiment(df)
            
            # 取得最新一筆與前一筆數據來計算漲跌
            latest = df.iloc[-1]
            prev_close = df['Close'].iloc[-2]
            change_pct = ((latest['Close'] - prev_close) / prev_close) * 100
            
            # 格式化歷史數據用於 Textbox
            history_list = []
            for date, row in df.tail(10).iterrows():
                history_list.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "open": round(row['Open'], 2),
                    "close": round(row['Close'], 2),
                    "vol": int(row['Volume'])
                })
            
            return {
                "symbol": symbol,
                "current_price": round(latest['Close'], 2),
                "open_price": round(latest['Open'], 2),
                "change_pct": f"{change_pct:+.2f}%",
                "volume": f"{int(latest['Volume']):,}",
                "sentiment": sentiment_text,
                "sentiment_color": color,
                "history": history_list
            }
    return {"error": f"找不到代碼 {symbol}"}