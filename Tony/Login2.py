from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import logging
import ast

with open('loginDB.txt', 'r') as file:
    info = file.read()

loginDict = ast.literal_eval(info)


class S(BaseHTTPRequestHandler):

    def _set_response(self, page, username=''):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Login</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))

        if page == 'login':
            self.wfile.write(bytes("<h1>Login</h1>", "utf-8"))
            self.wfile.write(bytes("<form method='post'>", "utf-8"))
            self.wfile.write(bytes("<label for='username'>Username:</label><br>", "utf-8"))
            self.wfile.write(bytes("<input type='text' id='username' name='username'><br><br>", "utf-8"))
            self.wfile.write(bytes("<label for='password'>Password:</label><br>", "utf-8"))
            self.wfile.write(bytes("<input type='password' id='password' name='password'><br><br>", "utf-8"))
            self.wfile.write(bytes("<input type='submit' value='Login'>", "utf-8"))
            self.wfile.write(bytes('</form>', "utf-8"))
        elif page == 'questions':
            self.wfile.write(bytes("<h1>TIME TO DIE!</h1>", "utf-8"))
            self.wfile.write(bytes("<p>You have successfully logged in.</p>", "utf-8"))
            self.wfile.write(bytes(" <form method = 'post'>", "utf-8"))
            self.wfile.write(bytes("<input type='hidden' id='username' name='username' value='{}'><br><br>".format(username), "utf-8"))
            self.wfile.write(bytes("<input type='hidden' id='page' name='page' value='questions'>", "utf-8"))
            self.wfile.write(bytes("""<p>
            a = [[1,2],[3,4],[5,[6,7]]] <br>
            print(a[2][1][1]) <br>
            
            What value is printed by the print statement?</p>
            <input type="radio" id="1" name="answer" value="6">
            <label for="1">6</label><br>
            <input type="radio" id="2" name="answer" value="3">
            <label for="2">3</label><br>  
            <input type="radio" id="3" name="answer" value="5">
            <label for="3">5</label><br>
            <input type="radio" id="4" name="answer" value="7">
            <label for="4">7</label><br><br>
            <input type="submit" value="Submit">
            """, "utf-8"))
            self.wfile.write(bytes("</form>", "utf-8"))

        self.wfile.write(bytes("</body></html>", "utf-8"))


    def do_GET(self):
        if self.path == '/activate':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes('Button was clicked!', 'utf-8'))
        else:
            self._set_response('login')

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('utf-8') # <--- Gets the data itself

        username = ""
        password = ""
        answer = ""
        page = ""

        # Extract the username, password, and answer from the form data
        params = post_data.split('&')
        for param in params:
            key, value = param.split('=')
            # print(key + "and" + value)
            if key == 'username':
                username = value
            elif key == 'password':
                password = value
            elif key == 'answer':
                answer = value
            elif key == 'page':
                page = value
            
        # Perform the login validation (e.g., check against a database)
        if page == 'questions':
                # self.process_answer(answer, username)
                print("Answer:", answer)
                print("Name:", username)
                self._set_response('questions', username)
        else:
            if username in loginDict and loginDict[username] == password:
                # self.process_answer(answer, username)
                #TODO grab questions from database
                #TODO also check in stdQuestions.txt that user doesn't already have questions assigned to them
                #if they do have questions assigned, grab those and their last answers
                self._set_response('questions', username)
            else:
                self._set_response('login',"")
                self.wfile.write(bytes("<p>Invalid username or password. Please try again.</p>", "utf-8"))

    # def process_answer(self, answer, username):
    #     # Process the submitted answer and username as needed
    #     # For now, simply print the values
    #     print("Selected answer:", answer)
    #     print("Username:", username)

    #     # Send the response page
    #     self._set_response('dashboard', username)

def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    try:
        # Create a new thread for each incoming request
        while True:
            httpd.handle_request()
            #thread alternative
            #threading.Thread(target=httpd.handle_request).start()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
