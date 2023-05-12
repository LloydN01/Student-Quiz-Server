import socket
import select
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, urlparse, parse_qs
from sys import argv
import random
import ast
import json

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

# Creates the HTML that displays the current user mark (if question is completed) or the attempt number (if question is incomplete)
def generateCurrentStatus(mark, attempt):
    print(mark, attempt)
    content = "<p>Current Status: "
    if attempt > 3:
        content += "FAILED <br> You have failed this question 3 times. Please move on to the next question. </p>"
    elif mark > 0:
        content += "PASSED</p>"
    else:
        content += "INCOMPLETE</p>"

    content += "<p>Attempt Number: "
    if attempt > 3:
        content += "3 </p>"
    else:
        content += str(attempt) + "</p>"
    
    content += "<p> Current Mark: " + str(mark) + "</p>"

    return content

# Creates the HTML for the multiple choice question
def multipleChoice(questionNumber, question, options, username, questionKey):
    # Question
    content = "<p>Q{} for {})<br>{}</p>".format(questionNumber + 1, username, question)
    content += "<form action='/questions' method='post'>"
    # Options
    for option in options:
        content += "<input type='radio' id='{}' name='answer' value='{}'>".format(option, option)
        content += "<label for='{}'>{}</label><br>".format(option, option)
    content += "<input type='submit' name='submit-answer' value='Submit'>"
    # Hidden input for question ID 
    content += "<input type='hidden' id='questionKey' name='questionKey' value='{}'>".format("$MCQ$" + questionKey)

    # Back and next buttons
    content += "<input type='submit' name='previous-question' value='Previous Question'>"
    content += "<input type='submit' name='next-question' value='Next Question'>"

    # Hidden username field to keep the username
    content += "<input type='hidden' id='username' name='username' value='{}'>".format(username)
    content += "</form>"

    # Display the current question status (attempt number and mark)
    content += generateCurrentStatus(questionsDict[username]["marks"][questionNumber], questionsDict[username]["attempts"][questionNumber])

    return content

# Creates the HTML for the short answer question
def shortAnswer(questionNumber, question, username, questionKey):
    # Question
    content = "<p>Q{} for {})<br>{}</p>".format(questionNumber + 1, username, question)
    content += "<form action='/questions' method='post'>"
    # Answer
    content += "<textarea name='answer' style='width: 550px; height: 250px;', placeholder='Type here'></textarea>"
    content += "<br>"
    content += "<input type='submit' name='submit-answer' value='Submit'>"
    # Hidden input for question ID 
    content += "<input type='hidden' id='questionKey' name='questionKey' value='{}'>".format("$SAQ$" + questionKey)

    # Back and next buttons
    content += "<input type='submit' name='previous-question' value='Previous Question'>"
    content += "<input type='submit' name='next-question' value='Next Question'>"

    # Hidden username field to keep the username
    content += "<input type='hidden' id='username' name='username' value='{}'>".format(username)
    content += "</form>"

    # Display the current question status (attempt number and mark)
    content += generateCurrentStatus(questionsDict[username]["marks"][questionNumber], questionsDict[username]["attempts"][questionNumber])

    return content

# Creates the HTML that displays the current question using the packet received from the QBs
def generateQuestionsHTML(questionPacket, username):
    index = questionsDict[username]["questions"].index(questionPacket) # Get the index of the current question for the user eg -> Qx) where x is index
    questionNum, questionLang, questionType, question = questionPacket.split("$", 3)
    content = ""
    if questionType == "MC":
        # If question is multiple choice
        questionBody, options = convertToMultipleChoice(question)
        content += multipleChoice(index, questionBody, options, username, questionLang + questionNum)
    elif questionType == "SA":
        # If question is short answer
        questionBody = question
        content += shortAnswer(index, questionBody, username, questionLang + questionNum)

    return content

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

        username = "" # Stoes the username of the current user
        password = "" # Stores the password of the current user (only relevant when logging in)
        HTMLContent = "" # Stores the HTML content that will be sent back to the user via _set_response()

        # Extract the username and password from the form data
        params = post_data.split('&')
        for param in params:
            key, value = param.split('=')
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
                    currUser["questions"].append(questionPacket)

                    questionNum, questionLang, questionType, question = questionPacket.split("$", 3)
                    if questionType == "MC":
                        # If question is multiple choice
                        currUser["questionKeys"].append(questionLang + questionNum)
                    elif questionType == "SA":
                        # If question is short answer
                        currUser["questionKeys"].append(questionLang + questionNum)

                currUser["marks"] = [0] * len(currUser["questions"]) # Initialise the marks to 0
                currUser["attempts"] = [0] * len(currUser["questions"]) # Initialise the attempt number to 0

                HTMLContent = (generateQuestionsHTML(currUser["questions"][0], username)) # Send the first question to the user
            elif 'next-question' in data:
                # Check that the question number is not the last question
                oldQuestionNumber = questionsDict[username]["questionNum"]
                userQuestions = questionsDict[username]["questions"]

                if oldQuestionNumber < len(userQuestions) - 1:
                    questionsDict[username]["questionNum"] += 1
                else:
                    questionsDict[username]["questionNum"] = 0

                newQuestionNumber = questionsDict[username]["questionNum"]
                
                HTMLContent = (generateQuestionsHTML(userQuestions[newQuestionNumber], username))
            elif 'previous-question' in data:
                # Check that the question number is not the first question
                oldQuestionNumber = questionsDict[username]["questionNum"]
                userQuestions = questionsDict[username]["questions"]

                if oldQuestionNumber > 0:
                    questionsDict[username]["questionNum"] -= 1
                else:
                    questionsDict[username]["questionNum"] = len(userQuestions) - 1
                
                newQuestionNumber = questionsDict[username]["questionNum"]
                
                HTMLContent = (generateQuestionsHTML(userQuestions[newQuestionNumber], username))
            elif 'submit-answer' in data:
                # Send user submitted answer to the correct QB
                # If questionKey contains Java -> JavaQB if Python -> PythonQB
                # Answer will comeback as either "correct" or "wrong"

                questionKey = str(data["questionKey"][0])
                userAnswer = str(data["answer"][0])
                isJavaQB = False # Either true if sending to JavaQB or false if sending to PythonQB
                id = ""
                if "Java" in questionKey:
                    isJavaQB = True
                    id = questionKey.replace('Java',"",1)
                elif "Python" in questionKey:
                    id = questionKey.replace('Python',"",1)

                answerToQB = id + "$" + userAnswer

                if isJavaQB:
                    javaQB.sendall(bytes(answerToQB + "\n", "utf-8"))
                else:
                    pythonQB.sendall(bytes(answerToQB + "\n", "utf-8"))

                # Wait for the answer to be received from the QB
                marked = []
                marked, _ , _ = select.select(inputs, outputs, inputs)
                receivedMark = marked[0].recv(1024).decode().strip() # Either "correct" or "wrong"

                currentMark = questionsDict[username]["marks"][questionsDict[username]["questionNum"]]
                currentAttempt = questionsDict[username]["attempts"][questionsDict[username]["questionNum"]]
                
                if receivedMark == "correct":
                    # If the answer is correct, increment the marks
                    questionsDict[username]["marks"][questionsDict[username]["questionNum"]] = 3 - currentAttempt
                    questionsDict[username]["attempts"][questionsDict[username]["questionNum"]] += 1
                elif receivedMark == "wrong":
                    # If the answer is wrong, increment the attempts
                    questionsDict[username]["attempts"][questionsDict[username]["questionNum"]] += 1
                
                newMark = questionsDict[username]["marks"][questionsDict[username]["questionNum"]]
                newAttempt = questionsDict[username]["attempts"][questionsDict[username]["questionNum"]]

                userQuestions = questionsDict[username]["questions"]
                currQuestionNum = questionsDict[username]["questionNum"]

                HTMLContent = (generateQuestionsHTML(userQuestions[currQuestionNum], username)) # After submitting their answer, the page should stay on the same question

        elif username in loginDict and loginDict[username] == password:
            # Perform the login validation (e.g., check against a database)    
            if 'get-index-page' in data:
                if username not in questionsDict:
                    # If user does not exist in the Questions dictionary, redirect them to the index page
                    # These users have not received their questions yet
                    print("New user {} has been added".format(username))
                    content = index_page(username)
                    HTMLContent = (content)
                else:
                    # If user has received their questions already, redirect them to the questions page where they last left off
                    currQuestionNum = questionsDict[username]["questionNum"] # The question number that the user is currently on
                    currQuestionContent = questionsDict[username]["questions"][currQuestionNum] # The question that the user is currently on
                    print("User {} has returned".format(username))
                    HTMLContent = (generateQuestionsHTML(currQuestionContent, username))
        else:
            content = login_page() + "<p>Invalid username or password</p>"
            HTMLContent = (content)

        # Send the HTML content to the client
        self._set_response(HTMLContent)

if __name__ == '__main__':
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

    HOST1 = "" # IP for device running Java QB
    HOST2 = "" # IP for device running Python QB

    # Get the host from the command line
    if len(argv) == 3:
        HOST1 = str(argv[1])
        HOST2 = str(argv[2])
        print("Connected to two different QBs on different machines")
    elif len(argv) == 2:
        HOST1 = HOST2 = str(argv[1])
        print("Connected to two dfferent QBs running on same machine")
    else:
        print("Need at least one IP for QB")
        quit()

    # Set the ports
    JAVA_PORT = 9999
    PYTHON_PORT = 9998

    # Create the sockets
    javaQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pythonQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the servers
    javaQB.connect((HOST1, JAVA_PORT))
    pythonQB.connect((HOST2, PYTHON_PORT))

    # Check that both servers are connected
    if javaQB.fileno() != -1 and pythonQB.fileno() != -1:
        print("Connected to both servers")

    # Set the sockets to non-blocking
    javaQB.setblocking(False)
    pythonQB.setblocking(False)

    # Add the sockets to the inputs list
    inputs = [javaQB, pythonQB]
    outputs = []

    port = 5000
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, MyHTTPRequestHandler) # Use ThreadingHTTPServer to allow multiple users to connect to the server
    print('Starting httpd on port', port)
    httpd.serve_forever()