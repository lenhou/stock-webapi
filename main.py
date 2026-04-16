import yfinance as yf
from fastapi import FastAPI, HTTPException
from datetime import datetime

app = FastAPI(title="Taiwan Stock API")

def fetch_stock_data(stock_id: str):
    # 自動嘗試上市(.TW)與上櫃(.TWO)後綴
    for suffix in [".TW", ".TWO"]:
        ticker = yf.Ticker(f"{stock_id}{suffix}")
        hist = ticker.history(period="7d")
        if not hist.empty:
            try:
                name = ticker.info.get('longName') or ticker.info.get('shortName') or f"Stock {stock_id}"
            except:
                name = f"Stock {stock_id}"
            
            # 格式化數據
            history_list = []
            for date, row in hist.sort_index(ascending=False).iterrows():
                history_list.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "open": round(row['Open'], 2),
                    "high": round(row['High'], 2),
                    "low": round(row['Low'], 2),
                    "close": round(row['Close'], 2),
                    "volume": int(row['Volume'])
                })
            return {"stock_id": stock_id, "company_name": name, "history": history_list}
    return None

@app.get("/api/stock/{stock_id}")
async def get_stock(stock_id: str):
    data = fetch_stock_data(stock_id)
    if not data:
        raise HTTPException(status_code=404, detail="找不到該股票資料")
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)