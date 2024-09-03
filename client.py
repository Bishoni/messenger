import socket
import threading
import tkinter
from tkinter import messagebox, scrolledtext


from client_cfg import *
from connect_cfg import HOST, PORT


def receive():
    last_message = None
    while True:
        try:
            new_message = client.recv(1024).decode()
            if new_message:
                if new_message.startswith("SYSTEM:"):
                    message_display.insert(tkinter.END, new_message + '\n', 'system')
                else:
                    if new_message != last_message:
                        message_display.insert(tkinter.END, new_message + '\n', 'user')
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
        message_display.insert(tkinter.END, "Me: " + message + '\n', 'me')
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


def open_color_window():
    color_window = tkinter.Toplevel(window)
    color_window.title("Выбор цвета")
    color_window.geometry("200x200")

    pink_button = tkinter.Button(color_window, text="Розовый", command=lambda: window.configure(bg='pink'), width=10, height=2)
    pink_button.pack(pady=5)

    green_button = tkinter.Button(color_window, text="Зеленый", command=lambda: window.configure(bg='lightgreen'), width=10, height=2)
    green_button.pack(pady=5)

    grey_button = tkinter.Button(color_window, text="Голубой", command=lambda: window.configure(bg='lightblue'), width=10, height=2)
    grey_button.pack(pady=5)

    blue_button = tkinter.Button(color_window, text="Серый", command=lambda: window.configure(bg='gray'), width=10, height=2)
    blue_button.pack(pady=5)


def change_color(color):
    window.configure(bg=color)
    message_display.configure(bg=color, fg='black')


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
window = tkinter.Tk()
window.title(title_window_name)
window.geometry("400x500")
window.configure(bg='light blue')

set_name = tkinter.StringVar()
set_name.set(set_username())
name_button = tkinter.Entry(window, textvariable=set_name, bg='white', width=30)
name_button.pack(pady=5)

message_display = scrolledtext.ScrolledText(window, height=15, width=50, bg='white', fg='black')
message_display.pack(pady=5, fill=tkinter.BOTH, expand=True)
message_display.tag_config('me', foreground='blue')
message_display.tag_config('user', foreground='green')
message_display.tag_config('system', foreground='red')

my_message = tkinter.StringVar()
my_message.set(default_input_msg)
message_entry = tkinter.Entry(window, textvariable=my_message, bg='white', width=40)
message_entry.pack(pady=5)
message_entry.bind("<Return>", lambda event: send())

send_button = tkinter.Button(window, text=button_send_msg, command=send, width=20, height=2)
send_button.pack(pady=5)

disconnect_button = tkinter.Button(window, text=button_disconnect, command=disconnect, width=20, height=2)
disconnect_button.pack(pady=5)

color_button = tkinter.Button(window, text="Изменить цвет", command=open_color_window, width=20, height=2)
color_button.pack(pady=5)

receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()


def on_closing():
    if messagebox.askokcancel(warning_disconnect, warning_button_disconnect):
        disconnect()


window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()