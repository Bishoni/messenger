import socket
import threading

HOST = '192.168.0.30'
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
    except IndexError as e:
        leave_user(str(username), send_console=True)
    finally:
        print(f"LOG: Соединение было разорвано с {addr}")
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


def leave_user(username, send_console):
    broadcast('SYSTEM', f'Участник \'{username}\' отключился')
    if send_console:
        print('SYSTEM:', f'Участник \'{username}\' отключился')


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f'LOG: Сервер ожидает подключение по IP: {HOST}; PORT: {PORT}')

    while True:
        client, addr = server.accept()
        clients.append(client)
        print(f"LOG: Соединение успешно установлено с {addr}")
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()


start_server()
