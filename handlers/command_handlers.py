from telethon import events, Button
from config import logger
from services.sticker_service import sticker_service
from utils.telegram_utils import send_sticker

async def handle_start(event):
    buttons = [
        [Button.text("Стикеры", resize=True)],
        [Button.text("Помощь", resize=True)]
    ]
    await event.reply("Добро пожаловать! Выберите действие:", buttons=buttons)

async def handle_stickers(event):
    buttons = [
        [Button.text("Добавить стикер", resize=True)],
        [Button.text("Показать все", resize=True)],
        [Button.text("Очистить", resize=True)],
        [Button.text("Назад", resize=True)]
    ]
    await event.reply("Управление стикерами:", buttons=buttons)