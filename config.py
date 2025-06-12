from pydantic_settings import BaseSettings
from functools import lru_cache
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    アプリケーションの設定を管理するクラス
    """
    # OpenAI API設定
    openai_api_key: str

    # Google Sheets設定
    spreadsheet_id: str
    range_name: str = "Sheet1!A:C"
    credentials_path: str = "credentials.json"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    設定を取得する関数（キャッシュ付き）

    Returns:
        Settings: アプリケーションの設定
    """
    try:
        return Settings()
    except Exception as e:
        logger.error(f"設定の読み込みエラー: {str(e)}")
        raise 