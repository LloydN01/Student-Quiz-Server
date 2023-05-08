import socket
import select
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote, urlparse, parse_qs
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

def convertToMultipleChoice(question):
    # Split the question into the question and the answer
    question, answer = question.split("$")
    options = answer.split("/") # Split the answer into the options
    
    return (question, options)

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    
    userQuestions = [] # Stores the question in html format
    questionNumber = 0 # Stores the current question number

    # Starting page -> Later replce with login page
    def index_page(self):
        getQuestionsFromServer(randomiseQuestionNumbers())
        content = "<html><head><title>localhost</title></head>"
        content += "<body>"
        content += "<p>Click to get 5 random questions.</p>"
        content += "<form action='/questions' method='post'>"
        content += "<input type='submit' name='get-questions' value='Randomise'>"
        content += "</form>"
        content += "</body></html>"

        return content

    def multipleChoice(self, question, options):
        questionNumber = len(self.userQuestions) + 1
        # Question
        content = "<p>Q{})<br>{}</p>".format(questionNumber, question)
        content += "<form method='post'>"
        # Options
        for option in options:
            content += "<input type='radio' id='{}' name='message' value='{}'>".format(option, option)
            content += "<label for='{}'>{}</label><br>".format(option, option)
        content += "<input type='submit' value='Submit'>"
        content += "</form>"

        # Back and next buttons
        content += "<form method='post'>"
        content += "<input type='submit' name='previous-question' value='Previous Question'>"
        content += "<input type='submit' name='next-question' value='Next Question'>"
        content += "</form>"

        return content

    def _set_response(self, content):
        # Request the questions from the servers so that they are ready for the next POST request
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))

    def do_GET(self):
        if self.path == "/":
            # Request the starting page
            content = self.index_page()
            self._set_response(content)
        elif self.path == "/questions":
            self._set_response(self.userQuestions[self.questionNumber])
        else:
            self.send_error(404, "File not found {}".format(self.path))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)

        print("data: " + str(data))

        if 'get-questions' in data:
            # First time logging in, request the questions from the servers
            # Wait for the questions to be received
            readable, _ , _ = select.select(inputs, outputs, inputs)
            listOfQuestions = []
            for receivedData in readable:
                receivedQuestion = receivedData.recv(1024)
                if receivedQuestion:
                    # print('Received from', receivedData.getpeername()[1], ':\n', receivedQuestion.decode())
                    listOfQuestions += (receivedQuestion.decode().strip().split("$$")) # Using $$ as a delimiter between questions
            
            # Remove ""s from the list created due to split function
            listOfQuestions = list(filter(None, listOfQuestions))

            for question in listOfQuestions:
                questionType, question = question.split("$", 1)
                if questionType == "MC":
                    questionBody, options = convertToMultipleChoice(question)
                    self.userQuestions.append(self.multipleChoice(questionBody, options))
                elif questionType == "SA":
                    # Have code to handle short answer questions
                    pass # For now
        elif 'next-question' in data:
            # Check that the question number is not the last question
            if MyHTTPRequestHandler.questionNumber < len(MyHTTPRequestHandler.userQuestions) - 1:
                MyHTTPRequestHandler.questionNumber += 1
            else:
                MyHTTPRequestHandler.questionNumber = 0
        elif 'previous-question' in data:
            # Check that the question number is not the first question
            if MyHTTPRequestHandler.questionNumber > 0:
                MyHTTPRequestHandler.questionNumber -= 1
            else:
                MyHTTPRequestHandler.questionNumber = len(MyHTTPRequestHandler.userQuestions) - 1
        
        print("Question number: " + str(MyHTTPRequestHandler.questionNumber))
        self._set_response(self.userQuestions[MyHTTPRequestHandler.questionNumber])

def run(server_class=HTTPServer, handler_class=MyHTTPRequestHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd on port', port)
    httpd.serve_forever()

if __name__ == '__main__':
    run()