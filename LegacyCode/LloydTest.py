# import socket
# import select


# HOST = '10.135.156.144'  # set the host
# javaPort = 9999
# pythonPort = 9998

# javaQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# pythonQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# javaQB.connect((HOST, javaPort))
# pythonQB.connect((HOST, pythonPort))

# javaQB.setblocking(False)
# pythonQB.setblocking(False)
 
# inputs = [javaQB, pythonQB]
# outputs = []

# try:
#     while inputs:
#         readable, writable, exceptional = select.select(inputs, outputs, inputs)

#         for recievedData in readable:
#             recievedQuestion = recievedData.recv(1024)
#             if recievedQuestion:
#                 print('Received from', recievedData.getpeername()[1], ':', recievedQuestion.decode())

#         # Handle exceptional sockets
#         for error in exceptional:
#             print('Exceptional condition on', error.getpeername())
#             inputs.remove(error)
#             if error in outputs:
#                 outputs.remove(error)
#             error.close()
        
#         answer = "Hello, World!" + "\n" # TODO: This variable will need to be updated when the user submits an answer
#         isJava = True # TODO: Need a way to keep track of this variable and change it according to the question
#         if(isJava):
#             javaQB.sendall(answer.encode())
#         else:
#             pythonQB.sendall(answer.encode())
# except:
#     print("Connection closed")

# javaQB.close()
# pythonQB.close()

# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import time

hostName = "localhost"
serverPort = 8080

class MyTCPHandler(socketserver.BaseRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def handle(self):
        # Handle incoming request
        pass

with socketserver.TCPServer(("localhost", 8000), MyTCPHandler) as server:
    server.server_activate()

    while True:
        # Wait for a single request and handle it
        server.handle_request()

        # Do some other work
        print("Server is still running!")

# class MyServer(BaseHTTPRequestHandler):
#     def do_GET(self):
#         self.send_response(200)
#         self.send_header("Content-type", "text/html")
#         self.end_headers()
#         self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
#         self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
#         self.wfile.write(bytes("<body>", "utf-8"))
#         self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
#         self.wfile.write(bytes("</body></html>", "utf-8"))

# if __name__ == "__main__":        
#     webServer = HTTPServer((hostName, serverPort), MyServer)
#     print("Server started http://%s:%s" % (hostName, serverPort))

#     while(True):
#         try:
#             webServer.
#             webServer.server_activate()
#         except KeyboardInterrupt:
#             pass