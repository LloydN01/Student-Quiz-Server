import socket
import select
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote # To stop the http encoding messing with the message (ie. %24 -> $)
from sys import argv
import random

# Get the host from the command line
HOST = str(argv[1])

# Set the ports
PORT = 5000
JAVA_PORT = 9999
PYTHON_PORT = 9998

# Create the sockets
javaQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pythonQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the servers
javaQB.connect((HOST, JAVA_PORT))
pythonQB.connect((HOST, PYTHON_PORT))

# Check that both servers are connected
if javaQB.fileno() != -1 and pythonQB.fileno() != -1:
    print("Connected to both servers")

# Set the sockets to non-blocking
javaQB.setblocking(False)
pythonQB.setblocking(False)

# Add the sockets to the list of inputs
inputs = [javaQB, pythonQB]
outputs = []

# Randomly choose the number of questions requested to each server
def randomiseQuestionNumbers():
    # choose a random number between 0 and 5
    numFromJava = random.randint(0,5)
    numFromPython = 5 - numFromJava

    return (numFromJava, numFromPython)

# Send the request for questions to each server
def getQuestionsFromServer(numQuestions):
    # Get the number of questions from each server
        numJavaQuestions, numPythonQuestions = numQuestions

        # Send the number of questions to each server
        javaQB.sendall(bytes(str(numJavaQuestions) + "\n", "utf-8"))
        pythonQB.sendall(bytes(str(numPythonQuestions) + "\n", "utf-8"))

        print("Asked for", numJavaQuestions, "questions to Java server")
        print("Asked for", numPythonQuestions, "questions to Python server")

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, message):
        getQuestionsFromServer(randomiseQuestionNumbers())
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>localhost</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>Click to get 5 random questions.</p>", "utf-8"))
        self.wfile.write(bytes("<form method='post'>", "utf-8"))
        self.wfile.write(bytes("<input type='submit' value='Randomise'>", "utf-8"))
        self.wfile.write(bytes('</form>',"utf-8"))

        self.wfile.write(bytes("<p>Questions Received: <br> {}</p>".format(message), "utf-8"))

        self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_GET(self):
        self._set_response("")

    def do_POST(self):
        # Wait for the questions to be received
        readable, _ , _ = select.select(inputs, outputs, inputs)
        renderQuestions = ""
        for receivedData in readable:
            receivedQuestion = receivedData.recv(1024)
            if receivedQuestion:
                print('Received from', receivedData.getpeername()[1], ':\n', receivedQuestion.decode())

                renderQuestions += receivedQuestion.decode().replace("\n", "<br>")
            
        self._set_response(renderQuestions)

with HTTPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
    javaQB.close()
    pythonQB.close()
