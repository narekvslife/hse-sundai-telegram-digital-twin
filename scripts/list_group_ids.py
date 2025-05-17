import os

from dotenv import load_dotenv

from telethon import TelegramClient

load_dotenv()

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')

async def get_GROUP_IDs():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Get all dialogs (conversations)
        dialogs = await client.get_dialogs()
        
        # Print all groups with their IDs
        print("Groups and their IDs:")
        for dialog in dialogs:
            if dialog.is_group:
                print(f"Group: {dialog.name}, ID: {dialog.id}")

# Run the async function
import asyncio
asyncio.run(get_GROUP_IDs())