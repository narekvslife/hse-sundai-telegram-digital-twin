from telethon import events
from config import logger, GROUP_ID
from services.sticker_service import sticker_service
from utils.telegram_utils import send_group_message, send_group_sticker, send_group_audio, send_group_video
import src.agent2, src.tts
from src.tts import tts_engine
import uuid
import os


async def group_message_handler(event):
    message_text = event.message.text
    message_type, agent_response = src.agent.process_message(message_text)

    logger.info(f"Received message in group {GROUP_ID}: {message_text}")

    if message_type == "text":
        await send_group_message(event, agent_response)
    elif message_type == "sticker":
        await send_group_sticker(event, agent_response)
    elif message_type == "audio":
        res = tts_engine.synthesize_speech(text=agent_response)
        audio = res.get('audio', None)
        if audio:
            await send_group_audio(event, audio)
    elif message_type == "video":
        await send_group_video(event, agent_response)
    elif message_type == "none":
        pass
    else:
        logger.warning(f"Unknown message type: {message_type}")

    # except Exception as e:
    #     logger.error(f"Error processing group message: {e}")
    #     await event.reply("⚠️ Произошла ошибка при обработке сообщения")