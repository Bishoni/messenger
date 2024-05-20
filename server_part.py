import socket
import threading

HOST = '192.168.0.99'
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []


def handle_client(client, addr):
    while True:
        try:
            message = client.recv(1024).decode()
            broadcast(message, client)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            break


def broadcast(message, sender):
    for client in clients:
        if client != sender:
            try:
                client.send(message.encode())
            except:
                client.close()
                clients.remove(client)

def start_server():
    while True:
        client, addr = server.accept()
        clients.append(client)
        print(f"Connection established with {addr}")
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

start_server()