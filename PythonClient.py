import socket
import select

HOST = '10.135.156.144'  # set the host
PORT = 9999
PORT2 = 9998

# with (socket.socket(socket.AF_INET, socket.SOCK_STREAM),socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as (s,t):
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST, PORT))
server2.connect((HOST, PORT2))

server.setblocking(False)
server2.setblocking(False)
 
inputs = [server, server2]
outputs = []

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    # print(readable)
    # for i in writable:
    #     data = "hello my brother"
    #     sent = i.sendall(data.encode())

    for recievedData in readable:
        recievedMsg = recievedData.recv(1024)
        if recievedMsg:
            print('Received from', recievedData.getpeername()[1], ':', recievedMsg.decode())
    
    # message = input("Enter a message to send: ") + "\n" # add a new line character to the end of the message
    # t.sendall(message.encode())
    server.send("//JAVA//hello my brother\n".encode())
    server2.send("//PYTHON//hello my sister\n".encode())
server.close()
server2.close()