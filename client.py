import socket
import threading
import tkinter
from tkinter import messagebox


def update_from_file(query_var=None):
    with open('client.cfg', 'r', encoding='utf-8') as file:
        for line in file.readlines():
            if line.strip():
                name_var, value = line.split('=', 1)
                if name_var.strip() == query_var:
                    return value.strip()


def receive():
    last_message = None
    while True:
        try:
            new_message = client.recv(1024).decode()
            if new_message:
                if new_message != last_message:
                    message_list.insert(tkinter.END, new_message)
                    last_message = new_message
            else:
                print("Соединение закрыто сервером.")
                break
        except Exception as e:
            print(f"Ошибка при получении сообщения: {e}")
            break


def send():
    message = my_message.get()
    my_message.set("")
    if message:
        message_list.insert(tkinter.END, "Me: " + message)
        try:
            client.send(f'{set_username()}: {message}'.encode())
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")


def disconnect():
    try:
        client.send(f'{set_username()}:disconnect'.encode())
    except Exception as e:
        print(f"Ошибка при отключении: {e}")
    finally:
        client.close()
        window.quit()


def set_username():
    username = set_name.get() if set_name.get() else eval(update_from_file('default_username'))
    return username


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
with open('connect.cfg', 'r', encoding='utf-8') as connect_file:
    HOST, PORT = map(lambda var: var.split('=')[1].strip(), connect_file.readlines())
    client.connect((HOST, int(PORT)))

window = tkinter.Tk()
window.title(eval(update_from_file('title_window_name')))
set_name = tkinter.StringVar()
set_name.set(set_username())
name_button = tkinter.Entry(window, textvariable=set_name)
name_button.pack()

message_list = tkinter.Listbox(window)
message_list.pack()

my_message = tkinter.StringVar()
my_message.set(eval(update_from_file('default_input_msg')))
message_entry = tkinter.Entry(window, textvariable=my_message)
message_entry.pack()
message_entry.bind("<Return>", lambda event: send())

send_button = tkinter.Button(window, text=eval(update_from_file('button_send_msg')), command=send)
send_button.pack()

disconnect_button = tkinter.Button(window, text=eval(update_from_file('button_disconnect')), command=disconnect)
disconnect_button.pack()

receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()

def on_closing():
    if messagebox.askokcancel(str(update_from_file('warning_disconnect')), eval(update_from_file('warning_button_disconnect'))):
        disconnect()

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()