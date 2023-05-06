import socket
import select

HOST = '172.20.10.3'  # set the host
javaPort = 9999
pythonPort = 9998

javaQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pythonQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

javaQB.connect((HOST, javaPort))
pythonQB.connect((HOST, pythonPort))

javaQB.setblocking(False)
pythonQB.setblocking(False)
 
inputs = [javaQB, pythonQB]
outputs = []

try:
    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

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
        
        answer = "Hello, World!" + "\n" # TODO: This variable will need to be updated when the user submits an answer
        isJava = True # TODO: Need a way to keep track of this variable and change it according to the question
        if(isJava):
            javaQB.sendall(answer.encode())
        else:
            pythonQB.sendall(answer.encode())
except:
    print("Connection closed")

javaQB.close()
pythonQB.close()