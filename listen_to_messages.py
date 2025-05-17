import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

# Your API credentials from https://my.telegram.org/
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
group_id = os.getenv('TELEGRAM_GROUP_ID')

# Try to convert group_id to integer if it's numeric
try:
    group_id_int = int(group_id)
    group_id = group_id_int
except (ValueError, TypeError):
    # Keep as string if it's a username (e.g., '@groupname')
    pass

# Create the client
client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(chats=group_id))
async def message_handler(event):
    # Access the message content
    message_text = event.message.text
    
    # Print the message
    print(f"New message: {message_text}")
    
    # You can access other attributes like:
    sender = await event.get_sender()
    print(f"Sender: {sender.username}")
    
    # Access media, if any
    if event.message.media:
        print("This message contains media")

# Start the client
async def main():
    await client.start()
    print("Client started. Listening for messages...")
    
    # Verify the group ID is valid
    try:
        entity = await client.get_entity(group_id)
        print(f"Successfully found group: {entity.title if hasattr(entity, 'title') else entity.username}")
    except ValueError as e:
        print(f"Error: Could not find the group with ID {group_id}")
        print(f"Make sure the group ID is correct and the account has access to this group")
        print(f"Error details: {e}")
        return
    
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())