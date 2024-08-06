import socket
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

localUsers = []
telegramUsers = []

# TODO: сделать уведомление пользователю о том, что он подключился к чату

def update_from_file(query_var=None):
    '''Обновление динамических переменных. Работает через выполнение заданного кода'''

    with open('server.cfg', 'r', encoding='utf-8') as file:
        for line in file.readlines():
            if line.strip():
                name_var, value = line.split('=', 1)
                if name_var.strip() == query_var:
                    return value.strip()


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
                print(eval(update_from_file('disconnect_local_log')))
                break
            else:
                await broadcast(username, message, client)
    except Exception as e:
        print(e)
    finally:
        print(eval(update_from_file('disconnect_finally_log')))
        await send_leave_user(username, addr)
        localUsers.remove(client)
        client.close()


async def broadcast(username, message, sender=None):
    '''Непосредственная отправка сообщений'''

    if username != eval(update_from_file('system_msg_name')):
        print(eval(update_from_file('send_msg_log')))
    for user_id in telegramUsers:
        if user_id != sender:
            try:
                await bot.send_message(user_id, f'{username}: {message}')
            except Exception as e:
                print(eval(update_from_file('tg_msg_error_log')))
                localUsers.remove(user_id)

    for client in localUsers:
        if client != sender:
            try:
                client.send(f'{username}: {message}'.encode())
            except Exception as e:
                print(eval(update_from_file('local_msg_error_log')))
                client.close()
                localUsers.remove(client)


async def send_leave_user(username, addr, send_console=True):
    '''Отправка сообщений всем участникам чата, но не отключившемуся, об отключении участника'''

    await broadcast(eval(update_from_file('system_msg_name')), eval(update_from_file('disconnect_chat')))
    if send_console:
        print(eval(update_from_file('disconnect_chat_log')))


# TODO: cделать уведомление пользователю о том, что он успешно подключён к чату (отдельно сообщение юзеру)
async def send_connect_user(addr, send_console=True):
    '''Отправка сообщений всем участникам чата, в том числе и присоединившемуся, о присоединении участника'''

    await broadcast(eval(update_from_file('system_msg_name')), eval(update_from_file('connect_chat')))
    if send_console:
        print(eval(update_from_file('connect_log')))


bot = Bot(eval(update_from_file('token_tg')))
db = Dispatcher()


@db.message(Command("start"))
async def start(message: types.Message):
    '''Реакция телеграмм бота на команду /start.
    Обрабатывается приветствие для пользователя'''
    if message.from_user.id not in telegramUsers:
        await bot.send_message(message.from_user.id, eval(update_from_file('send_false_start_tg')))
    else:
        await bot.send_message(message.from_user.id, eval(update_from_file('send_true_start_tg')))


@db.message(Command("connect"))
async def start(message: types.Message):
    '''Реакция телеграмм бота на команду /connect.
    Обрабатывается подключения пользователя к чату через телеграмм'''

    if message.from_user.id not in telegramUsers:
        await message.answer(eval(update_from_file('send_connect_tg')))
        telegramUsers.append(message.from_user.id)
        await send_connect_user(message.from_user.id)
        print(eval(update_from_file('connect_success_tg_log')))
    else:
        await bot.send_message(message.from_user.id, eval(update_from_file('connect_error_tg')))


@db.message(Command("disconnect"))
async def start(message: types.Message):
    '''Реакция телеграмм бота на команду /disconnect.
    Обрабатывается отключение пользователя от чата через телеграмм'''

    if message.from_user.id in telegramUsers:
        username = message.from_user.first_name
        addr = message.from_user.id
        telegramUsers.remove(message.from_user.id)
        print(eval(update_from_file('disconnect_tg_log')))
        await broadcast(eval(update_from_file('system_msg_name')), eval(update_from_file('disconnect_all_tg')))
        await bot.send_message(addr, eval(update_from_file('disconnect_user_tg')))
        print(f"{eval(update_from_file('system_msg_name'))}:", eval(update_from_file('disconnect_chat')))
    else:
        await bot.send_message(message.from_user.id, eval(update_from_file('disconnect_error_tg')))


@db.message()
async def user_send_msg(message: types.Message):
    '''Отправка сообщения подключенным пользователем в общий чат через телеграмм'''
    if message.from_user.id in telegramUsers:
        await broadcast(message.from_user.first_name, message.text, message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, eval(update_from_file('connect_not_established')))


async def start_local_server():
    '''Создание сервера для локальных подключений'''

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with open('connect.cfg', 'r', encoding='utf-8') as connect_file:
        HOST, PORT = map(lambda var: var.split('=')[1].strip(), connect_file.readlines())
    server.bind((HOST, int(PORT)))
    server.listen()
    print(eval(update_from_file('wait_connect_log')))
    while True:
        client, addr = await asyncio.get_event_loop().run_in_executor(None, server.accept)
        print(eval(update_from_file('connect_success_local_log')))
        asyncio.create_task(handle_client(client, addr))


async def main():
    '''Включение локального сервера и активация бота для глобального'''

    await asyncio.gather(
        start_local_server(),
        db.start_polling(bot)
    )


if __name__ == "__main__":
    asyncio.run(main())
