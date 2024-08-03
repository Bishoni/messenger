import socket
import threading

HOST = '192.168.0.99'
PORT = 12345
clients = []


def handle_client(client, addr):
    clients.append(client)
    try:
        while True:
            input_data = client.recv(1024).decode()
            username = input_data.split(':')[0]
            message = str(input_data.split(':')[1]).lstrip()
            if message == 'disconnect':
                print(f'LOG: Клиент \'{username}\' разорвал настоящее соединение')
                break
            else:
                print(f'Участник \'{username}\' отправил сообщение: \'{message}\' ')
                broadcast(username, message, client)
    except Exception as e:
        print(e)
    finally:
        print(f"LOG: Соединение было разорвано с {addr}")
        send_leave_user(username, addr)
        clients.remove(client)
        client.close()


def broadcast(username, message, sender=None):
    for client in clients:
        if client != sender:
            try:
                client.send(f'{username}: {message}'.encode())
            except Exception:
                client.close()
                clients.remove(client)


def send_leave_user(username, addr, send_console=True):
    broadcast('SYSTEM', f'Участник \'{username}\' отключился {addr}')
    if send_console:
        print('SYSTEM:', f'Участник \'{username}\' отключился {addr}')


def send_connect_user(addr, send_console=True):
    broadcast('SYSTEM', f'Подключился новый участник {addr}')
    if send_console:
        print('SYSTEM:', f'Подключился новый участник {addr}')


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f'LOG: Сервер ожидает подключение по IP: {HOST}; PORT: {PORT}')

    while True:
        client, addr = server.accept()
        clients.append(client)
        send_connect_user(addr)
        print(f"LOG: Соединение успешно установлено с {addr}")
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

start_server()