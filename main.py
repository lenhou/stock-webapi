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
    # 計算 20 日均線 (MA20)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    current_price = df['Close'].iloc[-1]
    current_ma20 = df['MA20'].iloc[-1]
    
    # 根據股價與均線關係判斷樂觀或悲觀
    if current_price > current_ma20: 
        return "樂觀 (多頭)", "#28a745"
    elif current_price < current_ma20: 
        return "悲觀 (空頭)", "#dc3545"
    else: 
        return "盤整中", "#ffc107"

@app.get("/api/stock/{symbol}")
async def get_stock(symbol: str):
    # 強制轉大寫並去除前後空白，確保代碼格式正確
    clean_symbol = symbol.strip().upper()
    
    # 循環嘗試上市(.TW)與上櫃(.TWO)後綴
    for suffix in [".TW", ".TWO"]:
        ticker_symbol = f"{clean_symbol}{suffix}"
        stock = yf.Ticker(ticker_symbol)
        
        try:
            # 抓取最近 3 個月的歷史數據
            df = stock.history(period="3mo", actions=True)
            
            if df is not None and not df.empty and len(df) >= 2:
                sentiment_text, color = get_sentiment(df)
                
                # 取得最新數據與計算漲跌幅
                latest = df.iloc[-1]
                prev_close = df['Close'].iloc[-2]
                change_pct = ((latest['Close'] - prev_close) / prev_close) * 100
                
                # 1. 格式化歷史數據時，加入 high 和 low
                history_list = []
                for date, row in df.tail(10).iterrows():
                    history_list.append({
                        "date": date.strftime('%Y-%m-%d'),
                        "open": round(row['Open'], 2),
                        "high": round(row['High'], 2),  # 加入這行
                        "low": round(row['Low'], 2),    # 加入這行
                        "close": round(row['Close'], 2),
                        "vol": int(row['Volume'])
                    })
                
                # 2. 最後 return 的字典，也要加入當日的 high_price 和 low_price
                return {
                    "symbol": ticker_symbol,
                    "current_price": round(latest['Close'], 2),
                    "open_price": round(latest['Open'], 2),
                    "high_price": round(latest['High'], 2),  # 加入這行
                    "low_price": round(latest['Low'], 2),   # 加入這行
                    "change_pct": f"{change_pct:+.2f}%",
                    "volume": f"{int(latest['Volume']):,}",
                    "sentiment": sentiment_text,
                    "sentiment_color": color,
                    "history": history_list
                }
        except Exception as e:
            print(f"查詢 {ticker_symbol} 時發生預期外錯誤: {e}")
            continue
            
    return {"error": f"找不到代碼 {clean_symbol}，請確認上市(.TW)或上櫃(.TWO)代碼是否正確"}

if __name__ == "__main__":
    import uvicorn
    # 綁定 0.0.0.0 以利雲端平台(如 Render)部署
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)