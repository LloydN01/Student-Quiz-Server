from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
class S(BaseHTTPRequestHandler):
    messages = []
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
            print(self.messages)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes('Button was clicked!', 'utf-8'))
        else:
            # logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            print("refreshed")
            self._set_response()
            self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('utf-8') # <--- Gets the data itself
        # print(post_data)
        # logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #         str(self.path), str(self.headers), post_data.decode('utf-8'))
        message = post_data.split('=')[1]  # extract the message from the message body
        self.messages.append(message)

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
        self.wfile.write(bytes("Message received: {}".format(message), "utf-8"))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    # logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    # logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    # logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()