import socket
import threading
import tkinter
from tkinter import messagebox
from client_cfg import *


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
                print(server_close_connect)
                break
        except Exception as e:
            print(client_error_receive.format(e))
            break


def send():
    message = my_message.get()
    my_message.set("")
    if message:
        message_list.insert(tkinter.END, "Me: " + message)
        try:
            client.send(f'{set_username()}: {message}'.encode())
        except Exception as e:
            print(client_error_send.format(e))


def disconnect():
    try:
        client.send(f'{set_username()}:disconnect'.encode())
    except Exception as e:
        print(client_error_disconnect.format(e))
    finally:
        client.close()
        window.quit()


def set_username():
    username = set_name.get() if set_name.get() else default_username
    return username


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
with open('connect.cfg', 'r', encoding='utf-8') as connect_file:
    HOST, PORT = map(lambda var: var.split('=')[1].strip(), connect_file.readlines())
    client.connect((HOST, int(PORT)))

window = tkinter.Tk()
window.title(title_window_name)
set_name = tkinter.StringVar()
set_name.set(set_username())
name_button = tkinter.Entry(window, textvariable=set_name)
name_button.pack()

message_list = tkinter.Listbox(window)
message_list.pack()

my_message = tkinter.StringVar()
my_message.set(default_input_msg)
message_entry = tkinter.Entry(window, textvariable=my_message)
message_entry.pack()
message_entry.bind("<Return>", lambda event: send())

send_button = tkinter.Button(window, button_send_msg, command=send)
send_button.pack()

disconnect_button = tkinter.Button(window, button_disconnect, command=disconnect)
disconnect_button.pack()

receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()


def on_closing():
    if messagebox.askokcancel(warning_disconnect, warning_button_disconnect):
        disconnect()


window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()