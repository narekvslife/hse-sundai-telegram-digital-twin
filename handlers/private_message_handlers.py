from telethon import events
from config import logger
from services.sticker_service import sticker_service
from utils.telegram_utils import (
    send_private_message,
    send_private_sticker,
    send_private_audio,
    send_private_video
)
import src.agent
import src.tts
import os



async def private_message_handler(event):
    try:
        # Пропускаем служебные сообщения
        if not event.message.text:
            return

        message_text = event.message.text

        # Обработка сообщения через агента
        message_type, agent_response = src.agent.process_message(message=message_text)

        logger.info(f"Received private message from {event.sender_id}: {message_text}")

        # Отправка ответа
        if message_type == "text":
            await send_private_message(event, agent_response)
        elif message_type == "sticker":
            await send_private_sticker(event, agent_response)
        elif message_type == "audio":
            audio_path = src.tts.synthesize_speech(text=agent_response)
            await send_private_audio(event, audio_path)
            os.remove(audio_path)
        elif message_type == "none":
            pass
        else:
            logger.warning(f"Unknown message type: {message_type}")

    except Exception as e:
        logger.error(f"Error processing private message: {e}")
        await event.reply("⚠️ Что-то пошло не так...")