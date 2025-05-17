from telethon.tl.types import InputDocument
import os

async def send_group_message(event, text: str):
    await event.reply(text)

async def send_group_sticker(event, sticker_id: str):
    sticker_data = None
    if sticker_data:
        sticker = InputDocument(
            id=sticker_data['id'],
            access_hash=sticker_data['access_hash'],
            file_reference=sticker_data['file_reference']
        )
        await event.client.send_file(event.chat_id, sticker)
    else:
        await event.reply("Стикер не найден в коллекции")

async def send_group_audio(event, audio: bytes):
    await event.client.send_file(event.chat_id, audio, voice_note=True)

async def send_group_video(event, video_path: str):
    if os.path.exists(video_path):
        await event.client.send_file(event.chat_id, video_path, supports_streaming=True)
    else:
        await event.reply("Видеофайл не найден")

async def send_sticker(event, sticker_data):
    sticker = InputDocument(
        id=sticker_data['id'],
        access_hash=sticker_data['access_hash'],
        file_reference=sticker_data['file_reference']
    )
    await event.client.send_file(event.chat_id, sticker)