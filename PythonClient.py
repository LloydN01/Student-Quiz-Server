import socket
import select
import random
from sys import argv

HOST = str(argv[1])  # set the host
javaPort = 9999
pythonPort = 9998

javaQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pythonQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

javaQB.connect((HOST, javaPort))
pythonQB.connect((HOST, pythonPort))

if javaQB.fileno() != -1 and pythonQB.fileno() != -1:
    print("Connected to both servers")

javaQB.setblocking(False)
pythonQB.setblocking(False)
 
inputs = [javaQB, pythonQB]
outputs = []
counter = 0

try:
    while inputs:
        answer = input("type here: ") + '\n'
        print(answer[3:])
        if("$J$" in answer):
            javaQB.sendall(answer[3:].encode())
        else:
            pythonQB.sendall(answer[3:].encode())

        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for recievedData in readable:
            recievedQuestion = recievedData.recv(1024)
            if recievedQuestion:
                print('Received from', recievedData.getpeername()[1], ':', recievedQuestion.decode())
                counter+=1

        # Handle exceptional sockets
        for error in exceptional:
            print('Exceptional condition on', error.getpeername())
            inputs.remove(error)
            if error in outputs:
                outputs.remove(error)
            error.close()
        
except:
    print("Connection closed")

javaQB.close()
pythonQB.close()