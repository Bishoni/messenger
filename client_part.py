import socket
import threading
import tkinter

def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            message_list.insert(tkinter.END, 'Response: ' + message)
        except:
            break

def send():
    message = my_message.get()
    my_message.set("")
    message_list.insert(tkinter.END, "Request: " + message)
    client.send(message.encode())
    if message == "exit":
        client.close()
        window.quit()

HOST = '192.168.0.99'
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

window = tkinter.Tk()
window.title("Мессенджер")

message_list = tkinter.Listbox(window)
message_list.pack()

my_message = tkinter.StringVar()
my_message.set("Введите сообщение")
message_entry = tkinter.Entry(window, textvariable=my_message)
message_entry.pack()
message_entry.bind("<Return>", send)

send_button = tkinter.Button(window, text="Отправить", command=send)
send_button.pack()

receive_thread = threading.Thread(target=receive)
receive_thread.start()

tkinter.mainloop()
