import socket
import select
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, urlparse, parse_qs
from sys import argv
import random
import ast
import json

# Read the login database
with open('loginDB.txt', 'r') as loginFile:
    loginInfo = loginFile.read()

# Read the user questions database
questionsDict = {}
with open('userQuestionsDB.txt', 'r') as questionFile:
     if questionFile.readable() and questionFile.read().strip() != "":
        # Reposition file pointer to beginning of file
        questionFile.seek(0)
        # Load the data as a dictionary
        questionsDict = json.load(questionFile)

# Convert login details to python dictionaries
loginDict = ast.literal_eval(loginInfo)

# Get the host from the command line
HOST = str(argv[1])

# Set the ports
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

    # Send the number of questions to each server -> "$REQ$<numQuestions>\n is the format"
    javaQB.sendall(bytes("$REQ$"+str(numJavaQuestions) + "\n", "utf-8"))
    pythonQB.sendall(bytes("$REQ$"+str(numPythonQuestions) + "\n", "utf-8"))

    print("Asked for", numJavaQuestions, "questions to Java server")
    print("Asked for", numPythonQuestions, "questions to Python server")

def convertToMultipleChoice(question):
    # Split the question into the question and the answer
    question, answer = question.split("$")
    options = answer.split("/") # Split the answer into the options
    
    return (question, options)

# Creates the HTML for the login page
def login_page():
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
def index_page(username):
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

# Creates the HTML for the multiple choice question
def multipleChoice(question, options, username):
    questionNumber = len(questionsDict[username]["questions"]) + 1
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
    content += "<form action='/questions' method='post'>"
    content += "<input type='submit' name='previous-question' value='Previous Question'>"
    content += "<input type='submit' name='next-question' value='Next Question'>"

    # Hidden username field to keep the username
    content += "<input type='hidden' id='username' name='username' value='{}'>".format(username)

    content += "</form>"

    return "$MC$" + content

# Creates the HTML for the short answer question
def shortAnswer(question, username):
    questionNumber = len(questionsDict[username]["questions"]) + 1
    # Question
    content = "<p>Q{})<br>{}</p>".format(questionNumber, question)
    content += "<form method='post'>"
    # Answer
    content += "<textarea name='message' style='width: 550px; height: 250px;', placeholder='Type here'></textarea>"
    content += "<br>"
    content += "<input type='submit' value='Submit'>"
    content += "</form>"

    # Back and next buttons
    content += "<form action='/questions' method='post'>"
    content += "<input type='submit' name='previous-question' value='Previous Question'>"
    content += "<input type='submit' name='next-question' value='Next Question'>"

    # Hidden username field to keep the username
    content += "<input type='hidden' id='username' name='username' value='{}'>".format(username)
    content += "</form>"

    return "$SA$" + content

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    # In the userQuestionsDB.txt -> {'username':{
    #                                   completed: <Bool>, 
    #                                   questionNum: <Int>, 
    #                                   questions: [<List of questions>], 
    #                                   questionKeys: [<List of question keys>], 
    #                                   marks: [<List of marks>],
    #                                   attempts: [<List of attempts>]}}

    def _set_response(self, content):
        # Everytime a request is made, the userQuestionsDB.txt file is updated
        with open("userQuestionsDB.txt", "w") as questionsDB:
            questionsDB.write(json.dumps(questionsDict))
        
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
            content = login_page()
            self._set_response(content)
        else:
            self.send_error(404, "File not found {}".format(self.path))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)

        username = ""
        password = ""

        # Extract the username and password from the form data
        params = post_data.split('&')
        for param in params:
            key, value = param.split('=')
            # print(key + "and" + value)
            if key == 'username':
                username = value
            elif key == 'password':
                password = value

        print("Name:", username) 

        if self.path == '/questions':
            if 'get-questions' in data:
                # 'get-questions' is the name of the submit button in the index page. Users will only get access to this page if they are new and have not previously attempted the test
                # First time logging in, request the questions from the servers
                getQuestionsFromServer(randomiseQuestionNumbers()) # Request questions from the servers
                
                readable = []
                # Wait for the questions to be received from both JavaQB and PythonQB
                while(True):
                    readable, _ , _ = select.select(inputs, outputs, inputs)
                    if len(readable) == len(inputs):
                        # Only breaks out of the while loop when questions from both the Java and Python QB have been read
                        break
                
                listOfQuestions = []
                for receivedData in readable:
                    receivedQuestion = receivedData.recv(2048)
                    if receivedQuestion:
                        listOfQuestions += (receivedQuestion.decode().strip().split("$$")) # Using $$ as a delimiter between questions
                
                # Remove ""s from the list created due to split function
                listOfQuestions = list(filter(None, listOfQuestions))

                # Intialise the new user's dictionary entries
                # In the userQuestionsDB.txt -> {'username':{
                #                                   completed: <Bool>, 
                #                                   questionNum: <Int>, 
                #                                   questions: [<List of questions>], 
                #                                   questionKeys: [<List of question keys>], 
                #                                   marks: [<List of marks>],
                #                                   attempts: [<List of attempts>]}}
                
                questionsDict[username] = {"completed": False,
                                           "questionNum": 0,
                                           "questions": [],
                                           "questionKeys": [],
                                           "marks": [],
                                           "attempts": []} # Create new entry for the user in Questions dictionary
                currUser = questionsDict[username]

                for questionPacket in listOfQuestions:
                    questionNum, questionLang, questionType, question = questionPacket.split("$", 3)
                    if questionType == "MC":
                        # If question is multiple choice
                        questionBody, options = convertToMultipleChoice(question)
                        currUser["questionKeys"].append(questionLang + questionNum)
                        currUser["questions"].append(multipleChoice(questionBody, options, username))
                    elif questionType == "SA":
                        # If question is short answer
                        questionBody = question
                        currUser["questionKeys"].append(questionLang + questionNum)
                        currUser["questions"].append(shortAnswer(questionBody, username))

                currUser["marks"] = [0] * len(currUser["questions"]) # Initialise the marks to 0
                currUser["attempts"] = [1] * len(currUser["questions"]) # Initialise the attempt number to 1

                self._set_response(currUser["questions"][0]) # Send the first question to the user
            elif 'next-question' in data:
                # Check that the question number is not the last question
                oldQuestionNumber = questionsDict[username]["questionNum"]
                userQuestions = questionsDict[username]["questions"]

                if oldQuestionNumber < len(userQuestions) - 1:
                    questionsDict[username]["questionNum"] += 1
                else:
                    questionsDict[username]["questionNum"] = 0

                newQuestionNumber = questionsDict[username]["questionNum"]
                
                self._set_response(userQuestions[newQuestionNumber])
            elif 'previous-question' in data:
                # Check that the question number is not the first question
                oldQuestionNumber = questionsDict[username]["questionNum"]
                userQuestions = questionsDict[username]["questions"]

                if oldQuestionNumber > 0:
                    questionsDict[username]["questionNum"] -= 1
                else:
                    questionsDict[username]["questionNum"] = len(userQuestions) - 1
                
                newQuestionNumber = questionsDict[username]["questionNum"]
                
                self._set_response(userQuestions[newQuestionNumber])
        elif username in loginDict and loginDict[username] == password:
            # Perform the login validation (e.g., check against a database)    
            if 'get-index-page' in data:
                if username not in questionsDict:
                    # If user does not exist in the Questions dictionary, redirect them to the index page
                    # These users have not received their questions yet
                    print("New user {} has been added".format(username))
                    content = index_page(username)
                    self._set_response(content)
                else:
                    # If user has received their questions already, redirect them to the questions page where they last left off
                    currQuestionNum = questionsDict[username]["questionNum"] # The question number that the user is currently on
                    currQuestionContent = questionsDict[username]["questions"][currQuestionNum] # The question that the user is currently on
                    print("User {} has returned".format(username))
                    self._set_response(currQuestionContent)
        else:
            content = login_page() + "<p>Invalid username or password</p>"
            self._set_response(content)


if __name__ == '__main__':
    port = 5000
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, MyHTTPRequestHandler) # Use ThreadingHTTPServer to allow multiple users to connect to the server
    print('Starting httpd on port', port)
    httpd.serve_forever()