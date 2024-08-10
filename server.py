import socket
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from server_cfg import *
from connect_cfg import *

localUsers = []
telegramUsers = []


async def handle_client(client, addr):
    '''Подключение локальных клиентов'''

    localUsers.append(client)
    await send_connect_user(addr)
    try:
        while True:
            input_data = await asyncio.get_event_loop().run_in_executor(None, client.recv, 1024)
            if not input_data:
                pass
            input_data = input_data.decode()
            username = input_data.split(':')[0]
            message = str(input_data.split(':')[1]).lstrip()
            if message == 'disconnect':
                print(disconnect_local_log.format(username))
                break
            else:
                await broadcast(username, message, client)
    except Exception as e:
        print(e)
    finally:
        print(disconnect_finally_log.format(addr))
        await send_leave_user(username, addr)
        localUsers.remove(client)
        client.close()


async def broadcast(username, message, sender=None):
    '''Непосредственная отправка сообщений'''

    if username != system_msg_name:
        print(send_msg_log.format(username, message))
    for user_id in telegramUsers:
        if user_id != sender:
            try:
                await bot.send_message(user_id, f'{username}: {message}')
            except Exception as e:
                print(tg_msg_error_log.format(user_id, e))
                localUsers.remove(user_id)

    for client in localUsers:
        if client != sender:
            try:
                client.send(f'{username}: {message}'.encode())
            except Exception as e:
                print(local_msg_error_log.format("addr", e))
                client.close()
                localUsers.remove(client)


async def send_leave_user(username, addr, send_console=True):
    '''Отправка сообщений всем участникам чата, но не отключившемуся, об отключении участника'''

    await broadcast(system_msg_name, disconnect_chat.format(username, addr))
    if send_console:
        print(disconnect_chat_log.format(username, addr))


# TODO: cделать уведомление пользователю о том, что он успешно подключён к чату (отдельноe сообщение юзеру)
async def send_connect_user(addr, send_console=True):
    '''Отправка сообщений всем участникам чата, в том числе и присоединившемуся, о присоединении участника'''

    await broadcast(system_msg_name, connect_chat.format(addr))
    if send_console:
        print(connect_log.format(addr))


bot = Bot(token_tg)
db = Dispatcher()


@db.message(Command("start"))
async def start(message: types.Message):
    '''Реакция телеграмм бота на команду /start.
    Обрабатывается приветствие для пользователя'''
    if message.from_user.id not in telegramUsers:
        await bot.send_message(message.from_user.id, send_false_start_tg.format(message.from_user.first_name))
    else:
        await bot.send_message(message.from_user.id, send_true_start_tg.format(message.from_user.first_name))


@db.message(Command("connect"))
async def start(message: types.Message):
    '''Реакция телеграмм бота на команду /connect.
    Обрабатывается подключения пользователя к чату через телеграмм'''

    if message.from_user.id not in telegramUsers:
        await message.answer(send_connect_tg)
        telegramUsers.append(message.from_user.id)
        await send_connect_user(message.from_user.id)
        print(connect_success_tg_log.format(message.from_user.id))
    else:
        await bot.send_message(message.from_user.id, connect_error_tg)


@db.message(Command("disconnect"))
async def start(message: types.Message):
    '''Реакция телеграмм бота на команду /disconnect.
    Обрабатывается отключение пользователя от чата через телеграмм'''

    if message.from_user.id in telegramUsers:
        username = message.from_user.first_name
        addr = message.from_user.id
        telegramUsers.remove(message.from_user.id)
        print(disconnect_tg_log.format(message.from_user.id))
        await broadcast(system_msg_name, disconnect_all_tg.format(message.from_user.first_name, message.from_user.id))
        await bot.send_message(addr, disconnect_user_tg)
        print(system_msg_name, disconnect_chat_log.format(username, addr))
    else:
        await bot.send_message(message.from_user.id, disconnect_error_tg)


@db.message()
async def user_send_msg(message: types.Message):
    '''Отправка сообщения подключенным пользователем в общий чат через телеграмм'''
    if message.from_user.id in telegramUsers:
        await broadcast(message.from_user.first_name, message.text, message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, connect_not_established)


async def start_local_server():
    '''Создание сервера для локальных подключений'''

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with open('connect.cfg', 'r', encoding='utf-8') as connect_file:
        HOST, PORT = map(lambda var: var.split('=')[1].strip(), connect_file.readlines())
    server.bind((HOST, int(PORT)))
    server.listen()
    print(wait_connect_log.format(HOST, PORT))
    while True:
        client, addr = await asyncio.get_event_loop().run_in_executor(None, server.accept)
        print(connect_success_local_log.format(addr))
        asyncio.create_task(handle_client(client, addr))


async def main():
    '''Включение локального сервера и активация бота для глобального'''

    await asyncio.gather(
        start_local_server(),
        db.start_polling(bot)
    )


if __name__ == "__main__":
    asyncio.run(main())