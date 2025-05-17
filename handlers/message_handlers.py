from telethon import events
from services.sticker_service import sticker_service
from utils.telegram_utils import send_sticker

async def button_handler(event):
    user_id = event.sender_id
    text = event.message.text

    if text == "Стикеры":
        await handle_stickers(event)
    elif text == "Добавить стикер":
        await event.reply("Отправьте стикер для добавления")
        sticker_service.user_states[user_id] = {'awaiting_sticker': True}
    elif text == "Показать все":
        await show_stickers(event)
    elif text == "Очистить":
        await clear_stickers(event)

async def show_stickers(event):
    if not sticker_service.demo_stickers:
        await event.reply("Коллекция стикеров пуста")
        return

    for i, sticker_data in enumerate(sticker_service.demo_stickers[:5], 1):
        await event.reply(f"Стикер {i}/{len(sticker_service.demo_stickers)}")
        await send_sticker(event, sticker_data)

async def clear_stickers(event):
    sticker_service.demo_stickers.clear()
    sticker_service.save_stickers()
    await event.reply("Коллекция стикеров очищена")