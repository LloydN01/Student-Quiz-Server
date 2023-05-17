import socket
import select
import random
import pdb
from utils import *

pythonQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pythonQB.bind((HOST, PPORT))
pythonQB.listen()
clients = [pythonQB]
aliases = []
requester = []
req_details = []
def receive():
    while True: 
        # qn = random.randint(0,10)
        # client.send(("r0," + str(qn)).encode())
        readable, writable, exceptional = select.select(clients, requester, clients)
        # pdb.set_trace()
        for recievedData in readable:
            # pdb.set_trace()
            if recievedData is pythonQB:
                client,address = pythonQB.accept()
                clients.append(client)
                # pdb.set_trace()
                print("Connected to"  + str(client.getpeername()[1]))
            else: 
                print("reading")
                req = recievedData.recv(1024)
                p = Packet(req.decode().split('$$$')[1],mode='r')
                if p.body.num: 
                    print("Got a request for " + req.decode() + " questions")
                    requester.append(recievedData)
                    req_details.append(p)
                else: 
                    clients.remove(recievedData)

        # Handle exceptional sockets
        for error in exceptional:
            print('Exceptional condition on', error.getpeername())
            clients.remove(error)
            error.close()
        
        for host in writable: 
            #pdb.set_trace()
            n = requester.index(host) 
            p = req_details[n]
            qn = p.body.num
            print(str(host.getpeername()[1]) + " requested " + qn + " questions." )
            host.send( ("Here are your " + qn + " questions!").encode())
            arr = readQ(qn)
            for i in range(int(qn)): 
                p = Packet(host.getsockname()[0],pythonQB.getsockname()[0],'q',1,Payload(qStr=arr[i],seq=i,mode='q'),mode='c')
                host.send(p.toSend())
            host.send(("All questions sent!").encode())
            requester.remove(host) 
            req_details.pop(n)
        # pdb.set_trace()
print("Listening on "+ str(PPORT))
receive()
# receive(pythonQB)