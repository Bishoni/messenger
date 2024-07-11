import socket
import threading

HOST = '192.168.0.99'
PORT = 12345
clients = []

# TODO: Сделать корректный вывод в консоль сервера о отправке сообщений. И от отключений пользователей
def handle_client(client, addr):
    clients.append(client)
    try:
        while True:
            message = client.recv(1024).decode()
            print(f'{addr} отправил сообщение {message}')
            if message == 'disconnect':
                print(f'Клиент {addr} разорвал настоящее соединение')
                break
            else:
                broadcast(message, client)
    except Exception as e:
        print(e)
    finally:
        # Вот в этой строке
        print(f"Соединение было разорвано с {addr}")
        clients.remove(client)
        client.close()


def broadcast(message, sender):
    for client in clients:
        if client != sender:
            try:
                client.send(message.encode())
            except Exception:
                print(f'Соединение с {client} потеряно. Сообщение этому клиенту не доставлено')
                client.close()
                clients.remove(client)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f'Сервер ожидает подключение по HOST: {HOST}; PORT: {PORT}')

    while True:
        client, addr = server.accept()
        clients.append(client)
        print(f"Соединение успешно установлено с {addr}")
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()


start_server()