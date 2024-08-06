import socket
import threading

clients = []


def update_from_file(query_var=None):
    with open('server_cfg.cfg', 'r', encoding='utf-8') as file:
        for line in file.readlines():
            if line.strip():
                name_var, value = line.split('=', 1)
                if name_var.strip() == query_var:
                    return value.strip()


def handle_client(client, addr):
    clients.append(client)
    try:
        while True:
            input_data = client.recv(1024).decode()
            username = input_data.split(':')[0]
            message = str(input_data.split(':')[1]).lstrip()
            if message == 'disconnect':
                print(eval(update_from_file('disconnect_log')))
                break
            else:
                print(eval(update_from_file('send_msg_log')))
                broadcast(username, message, client)
    except Exception as e:
        print(e)
    finally:
        print(eval(update_from_file('disconnect_finally_log')))
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
    broadcast('SYSTEM', eval(update_from_file(('disconnect_chat'))))
    if send_console:
        print(eval(update_from_file('disconnect_chat_log')))


def send_connect_user(addr, send_console=True):
    broadcast('SYSTEM', eval(update_from_file('connect_chat')))
    if send_console:
        print(eval(update_from_file('connect_log')))


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = eval(update_from_file('HOST'))
    PORT = int(update_from_file('PORT'))
    server.bind((HOST, PORT))
    server.listen()
    print(eval(update_from_file('wait_connect_log')))

    while True:
        client, addr = server.accept()
        clients.append(client)
        send_connect_user(addr)
        print(eval(update_from_file('success_connect_log')))
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

start_server()