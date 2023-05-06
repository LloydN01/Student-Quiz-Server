import socket
import select
import random

HOST = '192.168.0.19'  # set the host
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

try:
    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)

        # answer = input("Message ('$P' = Python, '$J' = Java): ") + "\n"
        
        answer = random.choice(["$P$Hello, Python!", "$J$Hello, Java!"]) + "\n"
        print(answer)
        if("$J$" in answer):
            javaQB.sendall(answer.encode())
        else:
            pythonQB.sendall(answer.encode())

        for recievedData in readable:
            recievedQuestion = recievedData.recv(1024)
            if recievedQuestion:
                print('Received from', recievedData.getpeername()[1], ':', recievedQuestion.decode())

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