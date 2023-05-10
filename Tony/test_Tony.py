from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import logging

class S(BaseHTTPRequestHandler):
    clients = {}

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
            self._set_response()
            self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('utf-8') # <--- Gets the data itself

        message = post_data.split('=')[1]  # extract the message from the message body

        # Get the IP address of the client
        ip = self.client_address[0]

        # If the client is new, add them to the dictionary
        if ip not in self.clients:
            self.clients[ip] = []

        # Append the message to the client's message list
        self.clients[ip].append(message)

        self._set_response()
        self.wfile.write(bytes("Message received: {} from {}".format(message, ip), "utf-8"))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    try:
        # Create a new thread for each incoming request
        while True:
            httpd.handle_request()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
