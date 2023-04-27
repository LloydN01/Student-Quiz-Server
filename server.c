#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

#define PORT 8888
#define BUFFER_SIZE 1024

int main() {
    int server_fd, client_fd, read_size;
    struct sockaddr_in server_addr, client_addr;
    char buffer[BUFFER_SIZE] = {0};
    
    // Create socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    
    // Bind socket to IP and port
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);
    
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        exit(EXIT_FAILURE);
    }
    
    // Listen for incoming connections
    if (listen(server_fd, 1) < 0) {
        perror("Listen failed");
        exit(EXIT_FAILURE);
    }
    
    printf("Server listening on port %d\n", PORT);
    
    // Accept incoming connection
    int client_addr_len = sizeof(client_addr);
    if ((client_fd = accept(server_fd, (struct sockaddr *)&client_addr, (socklen_t*)&client_addr_len)) < 0) {
        perror("Accept failed");
        exit(EXIT_FAILURE);
    }
    
    printf("Client connected\n");
    
    // Loop to continuously receive messages from client
    while (1) {
        memset(buffer, 0, BUFFER_SIZE); // Clear buffer
        
        // Read from client
        if ((read_size = recv(client_fd, buffer, BUFFER_SIZE, 0)) > 0) {
            printf("Received message: %s", buffer);
            
            // Send response back to client
            if (send(client_fd, buffer, strlen(buffer), 0) < 0) {
                perror("Send failed");
                exit(EXIT_FAILURE);
            }
        } else {
            // Client disconnected
            printf("Client disconnected\n");
            close(client_fd);
            
            // Wait for new connection
            if ((client_fd = accept(server_fd, (struct sockaddr *)&client_addr, (socklen_t*)&client_addr_len)) < 0) {
                perror("Accept failed");
                exit(EXIT_FAILURE);
            }
            
            printf("Client connected\n");
        }
    }
    
    return 0;
}