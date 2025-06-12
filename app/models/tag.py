from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Tag(BaseModel):
    """
    タグモデル
    """
    id: Optional[int] = None
    name: str
    color: str = "#3B82F6"  # デフォルトは青色
    description: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        from_attributes = True 