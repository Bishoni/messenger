import socket
import threading
import tkinter


HOST = '192.168.0.30'
PORT = 12345


def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            window.after(0, message_list.insert, tkinter.END, message)
        except Exception as e:
            print(e)
            break


def send(event=None):
    message = my_message.get()
    my_message.set("")
    message_list.insert(tkinter.END, "Me: " + message)
    client.send(f'{set_username()}: {message}'.encode())



def disconnect():
    client.send('disconnect'.encode())
    client.close()
    window.quit()


def set_username():
    username = set_name.get()
    if not username:
        username = f'Введите имя пользователя'
    return username


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

window = tkinter.Tk()
window.title("Мессенджер")

set_name = tkinter.StringVar()
set_name.set(set_username())
message_entry = tkinter.Entry(window, textvariable=set_name)
message_entry.pack()

message_list = tkinter.Listbox(window)
message_list.pack()

my_message = tkinter.StringVar()
my_message.set("Введите сообщение")
message_entry = tkinter.Entry(window, textvariable=my_message)
message_entry.pack()
message_entry.bind("<Return>", send)


send_button = tkinter.Button(window, text="Отправить", command=send)
send_button.pack()

disconnect_button = tkinter.Button(window, text='Отключиться', command=disconnect)
disconnect_button.pack()

receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()

window.mainloop()