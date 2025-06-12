from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import json
from pathlib import Path
from typing import List, Dict
import logging

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="SUSHI REPUBLIC Review System")

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# レビューデータの読み込み
def load_reviews() -> List[Dict]:
    try:
        with open("data/reviews.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("reviews", [])
    except Exception as e:
        logger.error(f"Error loading reviews: {str(e)}")
        return []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """メインページの表示"""
    try:
        reviews = load_reviews()
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "reviews": reviews}
        )
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/reviews")
async def get_reviews():
    """レビュー一覧のAPIエンドポイント"""
    try:
        reviews = load_reviews()
        return {"reviews": reviews}
    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/reviews/{review_id}")
async def get_review(review_id: int):
    """個別レビューのAPIエンドポイント"""
    try:
        reviews = load_reviews()
        if 0 <= review_id < len(reviews):
            return reviews[review_id]
        raise HTTPException(status_code=404, detail="Review not found")
    except Exception as e:
        logger.error(f"Error fetching review {review_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)