from openai import OpenAI
from config import get_settings
import logging
from typing import List, Dict
import json

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TagExtractor:
    def __init__(self):
        """
        タグ抽出器の初期化
        """
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.default_tags = [
            "taste", "service", "atmosphere", "price", "cleanliness",
            "location", "value", "quality", "staff", "food"
        ]

    def extract_tags(self, review_text: str) -> List[str]:
        """
        レビューからタグを抽出する

        Args:
            review_text (str): レビューテキスト

        Returns:
            List[str]: 抽出されたタグのリスト
        """
        try:
            prompt = f"""
            Analyze the following review and extract relevant tags from the predefined list.
            Return only the tags that are relevant to the review content.
            If no tags are relevant, return an empty list.

            Predefined tags: {', '.join(self.default_tags)}

            Review: {review_text}

            Return the tags in JSON format:
            {{
                "tags": ["tag1", "tag2", ...]
            }}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a review analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )

            # レスポンスをパース
            result = json.loads(response.choices[0].message.content)
            return result.get("tags", [])

        except Exception as e:
            logger.error(f"タグ抽出エラー: {str(e)}")
            return []

    def get_tag_statistics(self, reviews: List[Dict]) -> Dict[str, int]:
        """
        タグの統計情報を取得する

        Args:
            reviews (List[Dict]): レビューのリスト

        Returns:
            Dict[str, int]: タグごとの出現回数
        """
        tag_stats = {tag: 0 for tag in self.default_tags}
        
        for review in reviews:
            tags = self.extract_tags(review["text"])
            for tag in tags:
                if tag in tag_stats:
                    tag_stats[tag] += 1

        return tag_stats 