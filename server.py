import socket
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from server_cfg import *
from connect_cfg import *

local_users = []
telegram_users = []


async def handle_client(client, addr):
    """Обработка подключения локальных клиентов."""
    local_users.append(client)
    await send_connect_user(addr)
    try:
        while True:
            input_data = await asyncio.get_event_loop().run_in_executor(None, client.recv, 1024)
            if not input_data:
                break
            input_data = input_data.decode()
            username, message = input_data.split(':', 1)
            message = message.lstrip()
            if message == 'disconnect':
                print(disconnect_local_log.format(username))
                break
            await broadcast(username, message, client)
    except Exception as e:
        print(f"Ошибка при обработке клиента {addr}: {e}")
    finally:
        await handle_client_disconnect(username, addr, client)


async def handle_client_disconnect(username, addr, client):
    """Обработка отключения клиента."""
    print(disconnect_finally_log.format(addr))
    await send_leave_user(username, addr)
    local_users.remove(client)
    client.close()


async def broadcast(username, message, sender=None):
    """Отправка сообщений всем пользователям."""
    if username != system_msg_name:
        print(send_msg_log.format(username, message))

    for user_id in telegram_users:
        if user_id != sender:
            await send_message_to_user(user_id, f'{username}: {message}')

    for client in local_users:
        if client != sender:
            await send_message_to_client(client, f'{username}: {message}')


async def send_message_to_user(user_id, message):
    """Отправка сообщения пользователю Telegram."""
    try:
        await bot.send_message(user_id, message)
    except Exception as e:
        print(tg_msg_error_log.format(user_id, e))
        telegram_users.remove(user_id)


async def send_message_to_client(client, message):
    """Отправка сообщения локальному клиенту."""
    try:
        client.send(message.encode())
    except Exception as e:
        print(local_msg_error_log.format("addr", e))
        client.close()
        local_users.remove(client)


async def send_leave_user(username, addr, send_console=True):
    """Уведомление участников о отключении пользователя."""
    await broadcast(system_msg_name, disconnect_chat.format(username, addr))
    if send_console:
        print(disconnect_chat_log.format(username, addr))


async def send_connect_user(addr):
    """Уведомление участников о подключении нового пользователя."""
    await broadcast(system_msg_name, connect_chat.format(addr))
    print(connect_log.format(addr))


bot = Bot(token_tg)
db = Dispatcher()


@db.message(Command("start"))
async def start(message: types.Message):
    """Обработка команды /start."""
    if message.from_user.id not in telegram_users:
        await bot.send_message(message.from_user.id, send_false_start_tg.format(message.from_user.first_name))
    else:
        await bot.send_message(message.from_user.id, send_true_start_tg.format(message.from_user.first_name))


@db.message(Command("connect"))
async def connect(message: types.Message):
    """Обработка команды /connect."""
    if message.from_user.id not in telegram_users:
        await message.answer(send_connect_tg)
        telegram_users.append(message.from_user.id)
        await send_connect_user(message.from_user.id)
        print(connect_success_tg_log.format(message.from_user.id))
    else:
        await bot.send_message(message.from_user.id, connect_error_tg)


@db.message(Command("disconnect"))
async def disconnect(message: types.Message):
    """Обработка команды /disconnect."""
    if message.from_user.id in telegram_users:
        username = message.from_user.first_name
        addr = message.from_user.id
        telegram_users.remove(message.from_user.id)
        print(disconnect_tg_log.format(message.from_user.id))
        await broadcast(system_msg_name, disconnect_all_tg.format(username, addr))
        await bot.send_message(addr, disconnect_user_tg)
        print(disconnect_chat_log.format(username, addr))
    else:
        await bot.send_message(message.from_user.id, disconnect_error_tg)


@db.message()
async def user_send_msg(message: types.Message):
    """Обработка текстовых сообщений от пользователей."""
    if message.from_user.id in telegram_users:
        await broadcast(message.from_user.first_name, message.text, message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, connect_not_established)


async def start_local_server():
    """Создание локального сервера."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(wait_connect_log.format(HOST, PORT))
    while True:
        client, addr = await asyncio.get_event_loop().run_in_executor(None, server.accept)
        print(connect_success_local_log.format(addr))
        asyncio.create_task(handle_client(client, addr))


async def main():
    """Запуск локального сервера и бота."""
    await asyncio.gather(
        start_local_server(),
        db.start_polling(bot)
    )


if __name__ == "__main__":
    asyncio.run(main())