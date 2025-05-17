from telethon import events
from telethon.tl.types import InputDocument
from config import logger
from services.sticker_service import sticker_service
from utils.telegram_utils import send_sticker


async def handle_sticker(event):
    try:
        user_id = event.sender_id
        sticker = event.message.sticker

        if sticker_service.user_states.get(user_id, {}).get('awaiting_sticker'):
            new_sticker = {
                'id': sticker.id,
                'access_hash': sticker.access_hash,
                'file_reference': sticker.file_reference
            }

            if not any(s['id'] == new_sticker['id'] for s in sticker_service.demo_stickers):
                sticker_service.demo_stickers.append(new_sticker)
                sticker_service.save_stickers()
                await event.reply(f"✅ Стикер добавлен! Всего стикеров: {len(sticker_service.demo_stickers)}")
            else:
                await event.reply("Этот стикер уже есть в коллекции")

            sticker_service.user_states[user_id] = {'awaiting_sticker': False}
    except Exception as e:
        logger.error(f"Ошибка обработки стикера: {e}")
        await event.reply("⚠️ Произошла ошибка при обработке стикера")