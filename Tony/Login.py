from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import logging

class S(BaseHTTPRequestHandler):
    clients = {}

    def _set_response(self, page):
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
        elif page == 'dashboard':
            self.wfile.write(bytes("<h1>TIME TO DIE!</h1>", "utf-8"))
            self.wfile.write(bytes("<p>You have successfully logged in.</p>", "utf-8"))
            self.wfile.write(bytes("<h1>Q1 Who was in paris?</h1>", "utf-8"))

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

        # Extract the username and password from the form data
        params = post_data.split('&')
        for param in params:
            key, value = param.split('=')
            if key == 'username':
                username = value
            elif key == 'password':
                password = value

        # Perform the login validation (e.g., check against a database)
        if username == "admin" and password == "password":
            self._set_response('dashboard')
        else:
            self._set_response('login')
            self.wfile.write(bytes("<p>Invalid username or password. Please try again.</p>", "utf-8"))



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
