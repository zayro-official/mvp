from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import json
from pathlib import Path
from typing import List, Dict
import logging
import openai
from datetime import datetime

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

# レビューデータの保存
def save_reviews(reviews: List[Dict]):
    try:
        with open("data/reviews.json", "w", encoding="utf-8") as f:
            json.dump({"reviews": reviews}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving reviews")

# タグ抽出
def extract_tags(text: str) -> List[str]:
    tags = []
    tag_patterns = {
        "味": ["美味しい", "おいしい", "うまい", "まずい", "味が良い", "味が悪い"],
        "サービス": ["サービス", "接客", "対応", "スタッフ", "店員", "態度"],
        "価格": ["値段", "価格", "安い", "高い", "コスパ", "コストパフォーマンス"],
        "雰囲気": ["雰囲気", "内装", "外装", "清潔", "汚い", "落ち着く"],
        "メニュー": ["メニュー", "品揃え", "種類", "選択肢", "豊富", "少ない"]
    }
    
    for category, patterns in tag_patterns.items():
        for pattern in patterns:
            if pattern in text:
                tags.append(f"{category}:{pattern}")
                break
    
    return list(set(tags))

# 返信生成
def generate_reply(review: Dict) -> str:
    try:
        prompt = f"""
        以下のレビューに対する返信を生成してください：
        
        レビュー: {review['text']}
        タグ: {', '.join(review.get('tags', []))}
        
        返信は以下の条件を満たしてください：
        1. 丁寧で誠実な口調
        2. 具体的な改善点への言及
        3. 感謝の意を示す
        4. 200文字以内
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは寿司店のマネージャーです。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating reply: {str(e)}")
        return "申し訳ありません。返信の生成中にエラーが発生しました。"

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

@app.post("/api/reviews/{review_id}/reply")
async def create_reply(review_id: int):
    """返信生成のAPIエンドポイント"""
    try:
        reviews = load_reviews()
        if 0 <= review_id < len(reviews):
            review = reviews[review_id]
            
            # タグの抽出
            if "tags" not in review:
                review["tags"] = extract_tags(review["text"])
            
            # 返信の生成
            reply = generate_reply(review)
            review["reply"] = reply
            review["reply_date"] = datetime.now().isoformat()
            
            # レビューデータの保存
            save_reviews(reviews)
            
            return {"message": "Reply generated successfully", "reply": reply}
        raise HTTPException(status_code=404, detail="Review not found")
    except Exception as e:
        logger.error(f"Error generating reply for review {review_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)