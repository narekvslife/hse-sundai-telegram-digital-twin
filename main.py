from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN
from handlers import (
    command_handlers,
    sticker_handlers,
    message_handlers,
    group_handlers,
    private_message_handlers
)
from services.sticker_service import sticker_service

client = TelegramClient('session_name', API_ID, API_HASH)


def register_handlers():
    # Регистрация обработчиков команд
    client.add_event_handler(command_handlers.handle_start, events.NewMessage(pattern='/start'))
    client.add_event_handler(command_handlers.handle_stickers, events.NewMessage(pattern='/stickers'))

    # Регистрация обработчиков стикеров
    client.add_event_handler(sticker_handlers.handle_sticker, events.NewMessage(func=lambda e: e.message.sticker))

    # Регистрация других обработчиков
    client.add_event_handler(
        message_handlers.button_handler,
        events.NewMessage(func=lambda e: e.message.text in ["Стикеры", "Добавить стикер", "Показать все", "Очистить"])
    )

    group_handlers.register_group_handlers(client)
    private_message_handlers.register_private_handlers(client)


async def main():
    await client.start()
    register_handlers()
    print("Бот запущен и работает...")
    await client.run_until_disconnected()


if __name__ == '__main__':
    client.loop.run_until_complete(main())
