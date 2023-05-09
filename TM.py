import socket
import select
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote, urlparse, parse_qs
from sys import argv
import random
import ast
import json

# Read the login database
with open('loginDB.txt', 'r') as loginFile:
    loginInfo = loginFile.read()

# Read the user questions database
with open('userQuestionsDB.txt', 'r') as questionFile:
    questionsInfo = questionFile.read()

# Convert login details to python dictionaries
loginDict = ast.literal_eval(loginInfo)

# # Convert user questions to python dictionaries
# questionsDict = ast.literal_eval(questionsInfo)

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
        javaQB.sendall(bytes("$REQ$"+str(numJavaQuestions) + "\n", "utf-8"))
        pythonQB.sendall(bytes("$REQ$"+str(numPythonQuestions) + "\n", "utf-8"))

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

    # Login page
    def login_page(self):
        content = "<html><head><title>login</title></head>"
        content += "<h1>Login</h1>"
        content += "<form action='/index' method='post'>"
        content += "<label for='username'>Username:</label><br>"
        content += "<input type='text' id='username' name='username'><br><br>"
        content += "<label for='password'>Password:</label><br>"
        content += "<input type='password' id='password' name='password'><br><br>"
        content += "<input type='submit' name='get-index-page' value='Login'>"
        content += '</form>'
        content += "</body></html>"

        return content
    
    # Starting page -> get questions
    def index_page(self, username):
        getQuestionsFromServer(randomiseQuestionNumbers()) # Request questions from the servers
        content = "<html><head><title>localhost</title></head>"
        content += "<body>"
        content += "<p>Click to get 5 random questions.</p>"
        content += "<form action='/questions' method='post'>"
        content += "<input type='submit' name='get-questions' value='Randomise'>"

        # Hidden username field to keep the username
        content += "<input type='hidden' id='username' name='username' value='{}'>".format(username)

        content += "</form>"
        content += "</body></html>"

        return content

    def multipleChoice(self, question, options, username):
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

        # Hidden username field to keep the username
        content += "<input type='hidden' id='username' name='username' value='{}'>".format(username)

        content += "</form>"

        return "$MC$" + content
    
    def shortAnswer(self, question, username):
        questionNumber = len(self.userQuestions) + 1
        # Question
        content = "<p>Q{})<br>{}</p>".format(questionNumber, question)
        content += "<form method='post'>"
        # Answer
        content += "<textarea name='message' style='width: 550px; height: 250px;', placeholder='Type here'></textarea>"
        content += "<br>"
        content += "<input type='submit' value='Submit'>"
        content += "</form>"

        # Back and next buttons
        content += "<form method='post'>"
        content += "<input type='submit' name='previous-question' value='Previous Question'>"
        content += "<input type='submit' name='next-question' value='Next Question'>"

        # Hidden username field to keep the username
        content += "<input type='hidden' id='username' name='username' value='{}'>".format(username)
        content += "</form>"

        return "$SA$" + content

    def _set_response(self, content):
        # Request the questions from the servers so that they are ready for the next POST request
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Check if multiple choice or short answer or index page
        if content.startswith("$MC$"):
            self.wfile.write(bytes(content[4:], "utf-8"))
        elif content.startswith("$SA$"):
            self.wfile.write(bytes(content[4:], "utf-8"))
        else:
            self.wfile.write(bytes(content, "utf-8"))

    def do_GET(self):
        if self.path == "/":
            # Request the login page
            content = self.login_page()
            self._set_response(content)
        elif self.path == "/questions":
            self._set_response(self.userQuestions[self.questionNumber])
        else:
            self.send_error(404, "File not found {}".format(self.path))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)

        username = ""
        password = ""
        answer = ""

        # Extract the username, password, and answer from the form data
        params = post_data.split('&')
        for param in params:
            key, value = param.split('=')
            # print(key + "and" + value)
            if key == 'username':
                username = value
            elif key == 'password':
                password = value
            elif key == 'message':
                answer = value

        print("Answer:", answer)
        print("Name:", username)

        # Perform the login validation (e.g., check against a database)     

        if self.path == '/questions':
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
                        self.userQuestions.append(self.multipleChoice(questionBody, options, username))
                    elif questionType == "SA":
                        questionBody = question
                        self.userQuestions.append(self.shortAnswer(questionBody, username))
                self._set_response(self.userQuestions[MyHTTPRequestHandler.questionNumber])
            elif 'next-question' in data:
                # Check that the question number is not the last question
                if MyHTTPRequestHandler.questionNumber < len(MyHTTPRequestHandler.userQuestions) - 1:
                    MyHTTPRequestHandler.questionNumber += 1
                else:
                    MyHTTPRequestHandler.questionNumber = 0
                
                self._set_response(self.userQuestions[MyHTTPRequestHandler.questionNumber])
            elif 'previous-question' in data:
                # Check that the question number is not the first question
                if MyHTTPRequestHandler.questionNumber > 0:
                    MyHTTPRequestHandler.questionNumber -= 1
                else:
                    MyHTTPRequestHandler.questionNumber = len(MyHTTPRequestHandler.userQuestions) - 1
                
                self._set_response(self.userQuestions[MyHTTPRequestHandler.questionNumber])
        elif username in loginDict and loginDict[username] == password:
            if 'get-index-page' in data:
                content = self.index_page(username)
                self._set_response(content)
        else:
            content = self.login_page() + "<p>Invalid username or password</p>"
            self._set_response(content)

    

def run(server_class=HTTPServer, handler_class=MyHTTPRequestHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd on port', port)
    httpd.serve_forever()

if __name__ == '__main__':
    run()