import yfinance as yf
from fastapi import FastAPI, HTTPException
from datetime import datetime
from fastapi.staticfiles import StaticFiles  # 新增
from fastapi.responses import FileResponse   # 新增

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

# 將 static 資料夾掛載到 /static 路徑
app.mount("/static", StaticFiles(directory="static"), name="static")

# 新增一個首頁路由，讓使用者打開 127.0.0.1:8000 就能看到網頁
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse('static/index.html')

@app.get("/api/stock/{stock_id}")
async def get_stock(stock_id: str):
    # 強制轉大寫再查詢
    data = fetch_stock_data(stock_id.upper())
    if not data:
        raise HTTPException(status_code=404, detail="找不到該股票資料")
    return data

if __name__ == "__main__":
    import uvicorn
    import os
    # 這樣寫能同時相容「本機電腦」與「任何雲端平台」
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)