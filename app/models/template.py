from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Template(BaseModel):
    """
    返信テンプレートモデル
    """
    id: Optional[int] = None
    name: str
    content: str
    tags: List[str]  # 関連するタグのリスト
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        from_attributes = True 