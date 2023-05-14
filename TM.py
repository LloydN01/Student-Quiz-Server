import socket
import select
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler # TODO: Maybe we dont need threads. We could just use HTTPServer
from urllib.parse import unquote, urlparse, parse_qs
from sys import argv
import random
import ast
import json


############################################################################################
# Functions relating to requesting, receiving, manipulating, and keeping track of questions
############################################################################################

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
    java_conn.sendall(bytes("$REQ$"+str(numJavaQuestions) + "\n", "utf-8"))
    python_conn.sendall(bytes("$REQ$"+str(numPythonQuestions) + "\n", "utf-8"))

    print("Asked for", numJavaQuestions, "questions to Java server")
    print("Asked for", numPythonQuestions, "questions to Python server")

# Convert the question data into question body and answer (ie. "What is 1+1?$/a. 2/ b. 3/ c. 4/ d. 5" -> ("What is 1+1?", ["a. 2", "b. 3", "c. 4", "d. 5"]))
def convertToMultipleChoice(question):
    # Split the question into the question and the answer
    question, answer = question.split("$")
    options = answer.split("/") # Split the answer into the options
    
    return (question, options)

# Checks if the current question has been completed or not (ie. if the user has failed the question 3 times or has passed the question)
def isQuestionComplete(username, questionNumber):
    # Check if the question is complete
    if questionsDict[username]["attempts"][questionNumber] == 3 or questionsDict[username]["marks"][questionNumber] > 0:
        return True
    else:
        return False
    
# USED FOR MARKING STAGE: Sends the request of marking/answer to QB and receives the response from QB
def Marking_requestAndReceiveFromQB(isJavaQB, request):
    if isJavaQB:
        java_conn.sendall(bytes(request, "utf-8"))
    else:
        python_conn.sendall(bytes(request, "utf-8"))

    # If user attempt num <= 3 -> request for marking and receive either "correct" or "wrong" from QB
    # If user attempt num == 3 and user answer is wrong -> request for the correct answer from QB
    marked = []
    marked, _ , _ = select.select(inputs, outputs, inputs) # Wait for the data to be received from the QB
    received = marked[0].recv(1024).decode().strip() # Receive data

    return received

# Checks if TM and QBs are still connected by sending a PING and recieving a PONG
def PingPong():
    try:
        java_conn.sendall(bytes("PING\n","utf-8"))
        python_conn.sendall(bytes("PING\n","utf-8"))
    except:
        print("QB cannot receive")
        return 0
    print('sending PING')
    data1,data2 = java_conn.recv(1024),python_conn.recv(1024)
    if not data1 or not data2:
        print("QB cannot send")
        return 0
    return 1


############################################################################################
# Functions that generates the HTML for the pages
############################################################################################

# HTML page that notifies users when QB disconnects from the TM
def disconnectedQBHTML():
  content = ""
  content += "<h1>QB has been disconnected: TEST PAUSED</h1>"
  content += "<p>Your progress has been automatically saved."
  content += "<br>Please try reconnecting at a later time.</p>"
  return content

# Function that creates Javascript that enables the use of tab for indentations
def enableTabPresses():
    # Code was copied from https://stackoverflow.com/questions/6637341/use-tab-to-indent-in-textarea
    content = "<script>"
    content += "document.getElementById('textbox').addEventListener('keydown', function(e) {"
    content += "if (e.key == 'Tab') { e.preventDefault(); var start = this.selectionStart; var end = this.selectionEnd;"
    content += "this.value = this.value.substring(0, start) + '\t' + this.value.substring(end);"
    content += "this.selectionStart = this.selectionEnd = start + 1;}});"
    content += "</script>"

    return content
    
# Returns the total up-to-date status of the test for the user
def getTestStatus(username):
    totalNumQuestions = len(questionsDict[username]["questions"])
    userMarks = questionsDict[username]["marks"]
    userAttempts = questionsDict[username]["attempts"]

    totalNumQuestionsCompleted = 0 # Total number of questions completed by the user (ie. passed or failed)
    for index in range(len(userMarks)):
        if userMarks[index] > 0 or userAttempts[index] == 3:
            totalNumQuestionsCompleted += 1

    currentTotalMark = sum(questionsDict[username]["marks"])
    availableMarks = totalNumQuestions * 3

    content = "<p>Test Status:<br>"
    content += "You have completed {} out of {} questions. <br>".format(totalNumQuestionsCompleted, totalNumQuestions)
    content += "You have received {} marks out of {} available marks. <br>".format(currentTotalMark, availableMarks)
    content += "</p>"

    return content

# Creates the HTML for the login page
def login_page():
    content = "<html><head><title>login</title></head>"
    content += "<h1>Login</h1>"
    content += "<form method='post'>"
    content += "<label for='username'>Username:</label><br>"
    content += "<input type='text' id='username' name='username'><br><br>"
    content += "<label for='password'>Password:</label><br>"
    content += "<input type='password' id='password' name='password'><br><br>"
    content += "<input type='submit' name='login' value='Login'>"
    content += '</form>'
    content += "</body></html>"

    return content

# Starting page -> get questions
def index_page(username):
    content = "<html><head><title>localhost</title></head>"
    content += "<body>"
    content += "<h1>Welcome {}</h1>".format(username)
    content += "<form method='get'>"
    content += "<input type='submit' name='logout' value='Logout'>"
    content += "</form>"
    content += "<p>Click to get 5 random questions.</p>"
    content += "<form method='get'>"
    content += "<input type='submit' name='get-questions' value='Randomise'>"

    # Hidden username field to keep the username
    content += "<input type='hidden' id='username' name='username' value='{}'>".format(username)
    content += "</form>"
    content += "</body></html>"

    return content

# Creates the HTML that displays the current user mark (if question is completed) or the attempt number (if question is incomplete)
def generateCurrentStatus(mark, attempt):
    content = "<p>Current Question Status: "
    if attempt == 3 and mark == 0:
        content += "FAILED <br> You have failed this question 3 times. Please move on to the next question. </p>"
    elif mark > 0:
        content += "PASSED <br> You took {} attempt(s) and received {} mark(s) for this question. </p>".format(attempt, mark)
    else:
        content += "INCOMPLETE</p>"

    content += "<p>Attempt Number: "
    if attempt > 3:
        content += "3 </p>"
    else:
        content += str(attempt) + "</p>"
    
    content += "<p> Question Mark: " + str(mark) + "</p>"

    return content

# Creates the HTML for the multiple choice question
def multipleChoice(questionNumber, question, options, username, questionKey):
    # Question
    content = "<p>Q{} for <b>{}</b>)<br>{}</p>".format(questionNumber + 1, username, question)
    content += "<form method='post'>"
    # Options
    for option in options:
        content += "<input type='radio' id='{}' name='answer' value='{}'>".format(option, option)
        content += "<label for='{}'>{}</label><br>".format(option, option)

    if isQuestionComplete(username, questionNumber):
        # If question is complete, display a message
        content += "<p>Question is closed. Please move on to the next question.</p>"
    else:
        # If question is incomplete, display the submit button
        content += "<input type='submit' name='submit-answer' value='Submit'>"
    content += "<input type='hidden' id='questionKey' name='questionKey' value='{}'>".format("$MCQ$" + questionKey) # Hidden input for question ID (for marking)
    content += "<input type='hidden' id='username' name='username' value='{}'>".format(username) # Hidden username field to keep the username
    content += "</form>"

    return content

# Creates the HTML for the short answer question
def shortAnswer(questionNumber, question, username, questionKey):
    # Question
    content = "<p>Q{} for <b>{}</b>)<br>{}</p>".format(questionNumber + 1, username, question)
    content += "<form method='post'>"
    # Answer
    content += "<textarea id='textbox' name='answer' style='width: 550px; height: 250px;', placeholder='Type here'></textarea>"
    content += "<br>"
    
    if isQuestionComplete(username, questionNumber):
        # If question is complete, display a message
        content += "<p>Question is closed. Please move on to the next question.</p>"
    else:
        # If question is incomplete, display the submit button
        content += "<input type='submit' name='submit-answer' value='Submit'>"
    content += "<input type='hidden' id='questionKey' name='questionKey' value='{}'>".format("$SAQ$" + questionKey) # Hidden input for question ID (for marking)
    content += "<input type='hidden' id='username' name='username' value='{}'>".format(username) # Hidden username field to keep the username
    content += "</form>"

    return content + enableTabPresses()

# Creates the HTML that displays the current question using the packet received from the QBs
def generateQuestionsHTML(questionPacket, username, additionalContent = ""):
    index = questionsDict[username]["questions"].index(questionPacket) # Get the index of the current question for the user eg -> Qx) where x is index
    questionNum, questionLang, questionType, question = questionPacket.split("$", 3)
    content = "<form method='get'>"
    content += "<input type='submit' name='logout' value='Logout'>"
    content += "</form>"
    content += getTestStatus(username)
    if questionType == "MC":
        # If question is multiple choice
        questionBody, options = convertToMultipleChoice(question)
        content += multipleChoice(index, questionBody, options, username, questionLang + questionNum)
    elif questionType == "SA":
        # If question is short answer
        questionBody = question
        content += shortAnswer(index, questionBody, username, questionLang + questionNum)

    # Back and next buttons
    content += "<form method='get'>"
    content += "<input type='submit' name='previous-question' value='Previous Question'>"
    content += "<input type='submit' name='next-question' value='Next Question'>"
    content += "<input type='hidden' id='username' name='username' value='{}'>".format(username) # Hidden username field to keep the username
    content += "</form>"

    # Display the current question status (attempt number and mark)
    content += generateCurrentStatus(questionsDict[username]["marks"][index], questionsDict[username]["attempts"][index])

    return content + additionalContent # additional content is used for displaying the correct answer if the user has failed the question 3 times

# Creates the HTML that displays the incorrect answer given by user and correct answer provided by QB
def compareAnswersHTML(answer, correctAnswer):
    # After the third incorrect attempt, the incorrect answer given by user and correct answer provided by QB are displayed side by side
    content  = "<div><p style='display: inline-block; width: 50%; margin: 0; padding: 0;'>Your Answer: <br>{}</p>".format(answer)
    content += "<p style='display: inline-block; width: 50%; margin: 0; padding: 0;'>Correct Answer: <br>{}</p></div>".format(correctAnswer)

    return content


############################################################################################
# HTTP Request Handler Class that handles all the requests made by the client
############################################################################################

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    # In the userQuestionsDB.txt -> {'username':{
    #                                   completed: <Bool>, 
    #                                   questionNum: <Int>, 
    #                                   questions: [<List of questions>], 
    #                                   questionKeys: [<List of question keys>], 
    #                                   marks: [<List of marks>],
    #                                   attempts: [<List of attempts>]}}

    ##########################################################################
    # Set the response header and send the response to the client
    ##########################################################################
    def _set_response(self, content):
        # Everytime a request is made, the userQuestionsDB.txt file is updated
        with open("userQuestionsDB.txt", "w") as questionsDB:
            questionsDB.write(json.dumps(questionsDict))
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        self.wfile.write(bytes(content, "utf-8"))

    ##########################################################################
    # Handles the GET request made by the client
    # Get requests are made when the user first connects to the server,
    # when the user requests to get their randomised questions,
    # when the user clicks the logout button or when the user clicks the back/next button
    ##########################################################################
    def do_GET(self):
        # Checks if TM is still connected to both QBs -> If not, let user know
        res = PingPong()
        if res == 0:
            self._set_response(disconnectedQBHTML())
            return 0

        # Obtain the key-value pairs from the query string
        get_data = urlparse(self.path).query
        data = parse_qs(get_data)

        if "username" in data:
            username = data["username"][0] # Stoes the username of the current user
        HTMLContent = "" # Stores the HTML content that will be sent back to the user via _set_response()

        if self.path == "/" or "logout" in data:
            # Request the login page when the user first connects to the server or when the user clicks the logout button
            HTMLContent = login_page()
        elif 'get-questions' in data:
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
        else:
            self.send_error(404, "File not found {}".format(self.path))

        # Send the HTML content to the client
        self._set_response(HTMLContent)


    ##########################################################################
    # Handles the POST request made by the client
    # Post requests are made when the user submits their answer
    # or submits their username and password to login
    ##########################################################################
    def do_POST(self):
        # Checks if TM is still connected to QBs -> If not, notify user
        res = PingPong()
        if res == 0:
            self._set_response(disconnectedQBHTML())
            return 0

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)

        username = "" # Stoes the username of the current user
        password = "" # Stores the password of the current user (only relevant when logging in)
        HTMLContent = "" # Stores the HTML content that will be sent back to the user via _set_response()
        additionalContent = "" # Stores the additional information that will be displayed to the user

        # Extract the username and password from the form data
        params = post_data.split('&')
        for param in params:
            key, value = param.split('=')
            if key == 'username':
                username = value
            elif key == 'password':
                password = value

        if 'submit-answer' in data:
            userQuestions = questionsDict[username]["questions"]
            currQuestionNum = questionsDict[username]["questionNum"]

            if "answer" in data:
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

                answerToQB = id + "$" + userAnswer + "\n" # Format the answer to be sent to the QB
                
                receivedMark = Marking_requestAndReceiveFromQB(isJavaQB, answerToQB) # Send the answer to the correct QB and receive the mark

                questionsDict[username]["attempts"][questionsDict[username]["questionNum"]] += 1 # Increment the attempt number for the question

                if receivedMark == "correct":
                    currAttempt = questionsDict[username]["attempts"][questionsDict[username]["questionNum"]]
                    # If the answer is correct, set the mark
                    questionsDict[username]["marks"][questionsDict[username]["questionNum"]] = 4 - currAttempt
                elif receivedMark == "wrong" and questionsDict[username]["attempts"][questionsDict[username]["questionNum"]] == 3:
                    # If the answer is wrong on the 3rd attempt -> remove submit button -> request for correct answer to QB -> receive correct answer -> display to user
                    
                    idForAnswer = id.replace("$MCQ$", "").replace("$SAQ$", "") # Remove the question type from the id (e.g., $MCQ$1 -> 1)
                    requestForAns = "$ANS$" + idForAnswer + "\n" # Format the request for the correct answer to be sent to the QB

                    # Receive the correct answer from QB
                    correctAnswer =  Marking_requestAndReceiveFromQB(isJavaQB, requestForAns)

                    # Dislay the incorrect answer and correct answer side by side
                    additionalContent = compareAnswersHTML(userAnswer, correctAnswer)

                HTMLContent = (generateQuestionsHTML(userQuestions[currQuestionNum], username, additionalContent)) # After submitting their answer, the page should stay on the same question
            else:
                # If "answer" is not in data, then the user has not submitted an answer and just pressed submit
                HTMLContent = (generateQuestionsHTML(userQuestions[currQuestionNum], username)) # After submitting their answer, the page should stay on the same question

        elif username in loginDict and loginDict[username] == password:
            # Perform the login validation (e.g., check against a database)    
            if 'login' in data:
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
            HTMLContent = login_page() + "<p>Invalid username or password</p>"

        # Send the HTML content to the client
        self._set_response(HTMLContent)


############################################################################################
# main function to start the server and listen for connections 
############################################################################################ 

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

    HOST = socket.gethostbyname(socket.gethostname()) # IP for device running Java QB and running Python QB
    print(HOST) # Print the IP address of the device running the server

    # Set the ports
    JAVA_PORT = 9999
    PYTHON_PORT = 9998

    # Create the sockets
    javaQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pythonQB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Makes the servers
    javaQB.bind((HOST,JAVA_PORT))
    pythonQB.bind((HOST,PYTHON_PORT))

    # Listen for a QB to connect to each socket
    javaQB.listen(1)
    pythonQB.listen(1)

    # Wait for a client to connect to each socket
    java_conn, java_addr = javaQB.accept()
    python_conn, python_addr = pythonQB.accept()

    # Print the address of each client
    print(f"Java client connected from {java_addr[0]}")
    print(f"Python client connected from {python_addr[0]}")
    

    # TODO: Probably don't need to set the sockets to non-blocking
    # Set the sockets to non-blocking
    javaQB.setblocking(False)
    pythonQB.setblocking(False)

    # Add the sockets to the inputs list
    inputs = [java_conn, python_conn]
    outputs = []

    port = 5000
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, MyHTTPRequestHandler) # Use ThreadingHTTPServer to allow multiple users to connect to the server
    print('Starting httpd on port', port)
    httpd.serve_forever()