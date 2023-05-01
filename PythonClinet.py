import socket

HOST = '192.168.56.1'  # set the host
PORT = 9999        # set the port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        data = s.recv(1024).decode()[:-1] # remove the new line character at the end of the message
        print("Received message from server: ", data)
        message = input("Enter a message to send: ") + "\n" # add a new line character to the end of the message
        s.sendall(message.encode())