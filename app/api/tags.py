from fastapi import APIRouter, HTTPException
from typing import List
from app.models.tag import Tag
from app.core.sheets import GoogleSheets
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
sheets = GoogleSheets()

@router.get("/tags", response_model=List[Tag])
async def get_tags():
    """
    タグ一覧を取得
    """
    try:
        return sheets.get_tags()
    except Exception as e:
        logger.error(f"タグ取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags/{tag_id}", response_model=Tag)
async def get_tag(tag_id: int):
    """
    特定のタグを取得
    """
    try:
        tag = sheets.get_tag(tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="タグが見つかりません")
        return tag
    except Exception as e:
        logger.error(f"タグ取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tags", response_model=Tag)
async def create_tag(tag: Tag):
    """
    新しいタグを作成
    """
    try:
        return sheets.create_tag(tag)
    except Exception as e:
        logger.error(f"タグ作成エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tags", response_model=Tag)
async def update_tag(tag: Tag):
    """
    タグを更新
    """
    try:
        updated_tag = sheets.update_tag(tag)
        if not updated_tag:
            raise HTTPException(status_code=404, detail="タグが見つかりません")
        return updated_tag
    except Exception as e:
        logger.error(f"タグ更新エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tags/{tag_id}")
async def delete_tag(tag_id: int):
    """
    タグを削除
    """
    try:
        if not sheets.delete_tag(tag_id):
            raise HTTPException(status_code=404, detail="タグが見つかりません")
        return {"message": "タグを削除しました"}
    except Exception as e:
        logger.error(f"タグ削除エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 