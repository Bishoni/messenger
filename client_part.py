import socket


HOST = '192.168.0.99'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f'Попытка установления соединения с {HOST}')
    s.connect((HOST, PORT))
    print(f'Соединение с {HOST} установлено')
    while True:
        request = input('Введите запрос для сервера: ')
        s.sendall(request.encode())
        print(f'Успешно отправлен!')
        data = s.recv(1024)
        print(f'Получен ответ от сервера: {data.decode()}')