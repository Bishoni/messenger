import socket
import threading

HOST = '192.168.0.99'
PORT = 12345
clients = []


def handle_client(client, addr):
    global clients
    clients.append(client)
    try:
        while True:
            message = client.recv(1024).decode()
            if message == 'client_count':
                client.send(str(len(clients)).encode())
            elif message == 'disconnect':
                print(f'Клиент {addr} разорвал настоящее соединение')
            else:
                broadcast(message, client)
    except Exception as e:
        print(e)
    finally:
        print(f"Соединение было разорвано с {addr}")
        clients.remove(client)
        client.close()
        broadcast_client_count()


def broadcast_client_count():
    global clients
    for client in clients:
        try:
            client.send(f"client_count:{len(clients)}".encode())
        except Exception as e:
            print(e)


def broadcast(message, sender):
    for client in clients:
        if client != sender:
            try:
                client.send(message.encode())
            except Exception:
                print(f'Клиент {client} был отключён!')
                client.close()
                clients.remove(client)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    while True:
        client, addr = server.accept()
        clients.append(client)
        print(f"Соединение установлено с {addr}")
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()


start_server()

