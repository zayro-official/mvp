import schedule
import time
from datetime import datetime
import logging
from typing import List, Dict
from app.core.sheets import GoogleSheets
from app.core.tag_extractor import TagExtractor
from app.core.reply_gen import ReplyGenerator

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self):
        """
        バッチ処理の初期化
        """
        self.sheets = GoogleSheets()
        self.tag_extractor = TagExtractor()
        self.reply_generator = ReplyGenerator()

    def process_reviews(self):
        """
        レビューの一括処理
        """
        try:
            logger.info("バッチ処理を開始します...")
            
            # レビューの取得
            reviews = self.sheets.get_reviews()
            if not reviews:
                logger.info("処理するレビューがありません")
                return

            # 各レビューの処理
            for review in reviews:
                try:
                    # タグの抽出
                    tags = self.tag_extractor.extract_tags(review["text"])
                    
                    # 返信の生成
                    reply = self.reply_generator.generate_reply(
                        review["text"],
                        tags
                    )
                    
                    # 返信の保存
                    self.sheets.save_reply(review["row"], reply)
                    
                    logger.info(f"レビュー {review['row']} の処理が完了しました")
                    
                except Exception as e:
                    logger.error(f"レビュー {review['row']} の処理中にエラーが発生: {str(e)}")
                    continue

            logger.info("バッチ処理が完了しました")

        except Exception as e:
            logger.error(f"バッチ処理エラー: {str(e)}")
            raise

    def start_scheduler(self):
        """
        スケジューラーの開始
        """
        # 毎日午前0時に実行
        schedule.every().day.at("00:00").do(self.process_reviews)
        
        logger.info("スケジューラーを開始しました")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにチェック 