import socket

HOST = '192.168.0.99'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f'Создание сервера на хосте: {HOST}')
    s.bind((HOST, PORT))
    s.listen()
    print('Успешно!')
    conn, addr = s.accept()

    with conn:
        print(f'Соединение установлено: IP: {addr[0]}, PORT: {addr[1]}\nОжидание запроса от {addr[0]}')

        while True:
            data = conn.recv(1024)
            print(f'Получен запрос: {data.decode()}')
            if not data:
                print('Соединение разорвано!')
                break
            response = input('Введите ответ: ')
            conn.sendall(response.encode())
            print(f'Успешно отправлен!')
            