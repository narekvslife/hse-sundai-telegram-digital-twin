import json
import base64
from pathlib import Path
from config import logger, STICKERS_FILE

class StickerService:
    def __init__(self):
        self.demo_stickers = []
        self.user_states = {}
        self.load_stickers()

    def load_stickers(self):
        try:
            if STICKERS_FILE.exists():
                with open(STICKERS_FILE, "r") as f:
                    content = f.read()
                    if content.strip():
                        stickers_data = json.loads(content)
                        self.demo_stickers = [{
                            'id': s['id'],
                            'access_hash': s['access_hash'],
                            'file_reference': base64.b64decode(s['file_reference'])
                        } for s in stickers_data]
        except Exception as e:
            logger.error(f"Ошибка загрузки стикеров: {e}")

    def save_stickers(self):
        try:
            stickers_to_save = [{
                'id': s['id'],
                'access_hash': s['access_hash'],
                'file_reference': base64.b64encode(s['file_reference']).decode('utf-8')
            } for s in self.demo_stickers]

            with open(STICKERS_FILE, "w") as f:
                json.dump(stickers_to_save, f, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения стикеров: {e}")

sticker_service = StickerService()