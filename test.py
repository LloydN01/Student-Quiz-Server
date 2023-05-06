import socket
import select
from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import argv

HOST = str(argv[1])
PORT = 5000
JAVA_PORT = 9999
PYTHON_PORT = 9998

javaQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pythonQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

javaQB.connect((HOST, JAVA_PORT))
pythonQB.connect((HOST, PYTHON_PORT))

if javaQB.fileno() != -1 and pythonQB.fileno() != -1:
    print("Connected to both servers")

javaQB.setblocking(False)
pythonQB.setblocking(False)

inputs = [javaQB, pythonQB]
outputs = []

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>localhost</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("<form method='post'>", "utf-8"))
        self.wfile.write(bytes("<label for='textbox'>Enter a message:</label><br>", "utf-8"))
        self.wfile.write(bytes("<input type='text' id='textbox' name='message'><br><br>", "utf-8"))
        self.wfile.write(bytes("<input type='submit' value='Submit'>", "utf-8"))
        self.wfile.write(bytes('</form>',"utf-8"))
        self.wfile.write(bytes("<button onclick=\"fetch('/activate').then(response => console.log(response.text()))\">GET</button>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_GET(self):
        if self.path == '/activate':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes('Button was clicked!', 'utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><head><title>localhost</title></head>")
            self.wfile.write(b"<body><p>This is an example web server.</p>")
            self.wfile.write(b"<form method='post'>")
            self.wfile.write(b"<label for='textbox'>Enter a message:</label><br>")
            self.wfile.write(b"<input type='text' id='textbox' name='message'><br><br>")
            self.wfile.write(b"<input type='submit' value='Submit'>")
            self.wfile.write(b"</form>")
            self.wfile.write(b"<button onclick=\"fetch('/activate').then(response => console.log(response.text()))\">GET</button>")
            self.wfile.write(b"</body></html>")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        answer = post_data.decode() + '\n'
        print(answer[3:])
        if "$J$" in answer:
            javaQB.sendall(answer[3:].encode())
        else:
            pythonQB.sendall(answer[3:].encode())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

with HTTPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print("serving at port", PORT)
    try:
        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            for receivedData in readable:
                receivedQuestion = receivedData.recv(1024)
                if receivedQuestion:
                    print('Received from', receivedData.getpeername()[1], ':', receivedQuestion.decode())

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
