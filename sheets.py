from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config import get_settings
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheets:
    def __init__(self):
        """
        Google Sheets APIの初期化
        """
        settings = get_settings()
        self.spreadsheet_id = settings.spreadsheet_id
        self.range_name = settings.range_name

        # 認証情報の設定
        creds = Credentials.from_service_account_file(
            settings.credentials_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )

        # APIサービスの構築
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet = self.service.spreadsheets()

    def get_reviews(self):
        """
        スプレッドシートからレビューを取得する

        Returns:
            list: レビューのリスト（各レビューは辞書形式で、rowとtextを含む）
        """
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name,
            ).execute()

            values = result.get("values", [])
            if not values:
                logger.warning("データが見つかりません")
                return []

            reviews = []
            for i, row in enumerate(values, start=2):  # 2から開始（ヘッダー行を考慮）
                if len(row) >= 2 and row[1]:  # レビューテキストが存在する場合
                    review = {
                        "row": i,
                        "text": row[1]
                    }
                    # 返信が存在する場合は追加
                    if len(row) >= 3 and row[2]:
                        review["reply"] = row[2]
                    reviews.append(review)

            return reviews

        except Exception as e:
            logger.error(f"レビュー取得エラー: {str(e)}")
            raise

    def get_review_by_row(self, row: int):
        """
        指定された行のレビューを取得する

        Args:
            row (int): 取得する行番号

        Returns:
            dict: レビュー情報（見つからない場合はNone）
        """
        try:
            range_name = f"{self.range_name.split('!')[0]}!A{row}:C{row}"
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
            ).execute()

            values = result.get("values", [[]])
            if not values or not values[0]:
                return None

            review = {
                "row": row,
                "text": values[0][1] if len(values[0]) > 1 else ""
            }
            if len(values[0]) > 2:
                review["reply"] = values[0][2]

            return review

        except Exception as e:
            logger.error(f"レビュー取得エラー: {str(e)}")
            raise

    def save_reply(self, row: int, reply: str):
        """
        返信をスプレッドシートに保存する

        Args:
            row (int): 保存する行番号
            reply (str): 保存する返信テキスト
        """
        try:
            range_name = f"{self.range_name.split('!')[0]}!C{row}"
            body = {
                "values": [[reply]]
            }

            self.sheet.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()

            logger.info(f"返信を保存しました: 行 {row}")

        except Exception as e:
            logger.error(f"返信保存エラー: {str(e)}")
            raise 