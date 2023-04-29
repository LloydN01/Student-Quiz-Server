import socket

HOST = '127.0.0.1'
PORT = 1234
BUFFER_SIZE = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connected to server")
    
    # Loop to continuously send messages to server
    while True:
        message = input("Enter message: ")
        s.sendall(message.encode())
        
        # Receive response from server
        response = s.recv(BUFFER_SIZE)
        print("Server response: ", response.decode())