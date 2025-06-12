from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.core.sheets import GoogleSheets
from app.core.tag_extractor import TagExtractor
from app.api import tags
import logging
from datetime import datetime

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ZAYRO Review Manager")

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# APIルーターの登録
app.include_router(tags.router, prefix="/api")

# Google Sheetsインスタンスの初期化
sheets = GoogleSheets()
tag_extractor = TagExtractor()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    メインページを表示
    """
    try:
        # レビューの取得
        reviews = sheets.get_reviews()
        
        # 各レビューにタグと返信を追加
        for review in reviews:
            # タグの抽出
            review["tags"] = tag_extractor.extract_tags(review["text"])
            
            # 返信の生成（既存の返信がない場合）
            if not review.get("reply"):
                review["reply"] = generate_reply(review["text"])
            
            # 日付のフォーマット
            review["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "reviews": reviews}
        )
    
    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tags", response_class=HTMLResponse)
async def tags_page(request: Request):
    """
    タグ管理ページを表示
    """
    try:
        tags = sheets.get_tags()
        return templates.TemplateResponse(
            "tags.html",
            {"request": request, "tags": tags}
        )
    except Exception as e:
        logger.error(f"タグページ表示エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/regenerate-reply/{row}")
async def regenerate_reply(row: int):
    """
    指定された行の返信を再生成
    """
    try:
        review = sheets.get_review_by_row(row)
        if not review:
            raise HTTPException(status_code=404, detail="レビューが見つかりません")
        
        reply = generate_reply(review["text"])
        return {"success": True, "reply": reply}
    
    except Exception as e:
        logger.error(f"返信再生成エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save-reply/{row}")
async def save_reply(row: int):
    """
    指定された行の返信を保存
    """
    try:
        review = sheets.get_review_by_row(row)
        if not review:
            raise HTTPException(status_code=404, detail="レビューが見つかりません")
        
        reply = generate_reply(review["text"])
        sheets.save_reply(row, reply)
        return {"success": True}
    
    except Exception as e:
        logger.error(f"返信保存エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 