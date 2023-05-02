import socket
import select

HOST = '10.135.156.144'  # set the host
PORT = 9999        # set the port

# with (socket.socket(socket.AF_INET, socket.SOCK_STREAM),socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as (s,t):
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
t.connect((HOST,9998))
s.setblocking(False)
t.setblocking(False)

inputs = [s,t]
outputs = []

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    # print(readable)
    # for i in writable:
    #     data = "hello my brother"
    #     sent = i.sendall(data.encode())

    for s in readable:
        data = s.recv(1024)
        if data:
            print('Received from', s.getpeername()[1], ':', data.decode())

    
    # message = input("Enter a message to send: ") + "\n" # add a new line character to the end of the message
    # t.sendall(message.encode())
    message = "hello my brother\n"
    s.send(message.encode())
    t.send("hello my sister\n".encode())
s.close()
t.close()