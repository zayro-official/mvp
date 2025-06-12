from openai import OpenAI
from config import get_settings
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_reply(review: str) -> str:
    """
    レビューに対して返信を生成する

    Args:
        review (str): レビューテキスト

    Returns:
        str: 生成された返信
    """
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    
    prompt = f"""
    以下のレビューに対して、丁寧で親切な返信を生成してください：
    
    レビュー: {review}
    
    返信:
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切で丁寧なカスタマーサポート担当者です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"返信生成エラー: {str(e)}")
        raise 