import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Настройка логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация Telegram
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')

# Пути
STICKERS_FILE = Path("stickers.json")