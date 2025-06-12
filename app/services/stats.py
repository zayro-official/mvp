from datetime import datetime, timedelta
from typing import Dict, List
import logging
from app.core.sheets import GoogleSheets
from app.core.tag_extractor import TagExtractor

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatisticsService:
    def __init__(self):
        """
        統計サービスの初期化
        """
        self.sheets = GoogleSheets()
        self.tag_extractor = TagExtractor()

    def get_review_stats(self, days: int = 30) -> Dict:
        """
        レビューの統計情報を取得

        Args:
            days (int): 集計期間（日数）

        Returns:
            Dict: 統計情報
        """
        try:
            reviews = self.sheets.get_reviews()
            if not reviews:
                return {
                    "total_reviews": 0,
                    "reviews_with_replies": 0,
                    "reply_rate": 0,
                    "daily_reviews": [],
                    "tag_distribution": {}
                }

            # 基本統計
            total_reviews = len(reviews)
            reviews_with_replies = len([r for r in reviews if r.get("reply")])
            reply_rate = (reviews_with_replies / total_reviews * 100) if total_reviews > 0 else 0

            # 日別レビュー数
            daily_reviews = self._get_daily_reviews(reviews, days)

            # タグ分布
            tag_distribution = self.tag_extractor.get_tag_statistics(reviews)

            return {
                "total_reviews": total_reviews,
                "reviews_with_replies": reviews_with_replies,
                "reply_rate": round(reply_rate, 2),
                "daily_reviews": daily_reviews,
                "tag_distribution": tag_distribution
            }

        except Exception as e:
            logger.error(f"統計情報取得エラー: {str(e)}")
            raise

    def _get_daily_reviews(self, reviews: List[Dict], days: int) -> List[Dict]:
        """
        日別レビュー数を取得

        Args:
            reviews (List[Dict]): レビューのリスト
            days (int): 集計期間（日数）

        Returns:
            List[Dict]: 日別レビュー数
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        daily_counts = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            daily_counts[date_str] = 0
            current_date += timedelta(days=1)

        for review in reviews:
            try:
                review_date = datetime.strptime(review.get("date", ""), "%Y-%m-%d %H:%M")
                date_str = review_date.strftime("%Y-%m-%d")
                if date_str in daily_counts:
                    daily_counts[date_str] += 1
            except (ValueError, TypeError):
                continue

        return [
            {"date": date, "count": count}
            for date, count in daily_counts.items()
        ] 