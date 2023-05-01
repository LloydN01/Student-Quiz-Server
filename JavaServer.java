import java.net.*;
import java.io.*;
import java.util.*;
import java.nio.charset.StandardCharsets;

public class JavaServer {
    public static void main(String[] args) throws IOException {
        ServerSocket serverSocket = null;
        boolean listening = true;
        Scanner scanner = new Scanner(System.in);

        try {
            serverSocket = new ServerSocket(9999); // set port number
            // Print Server Port Number
            System.out.println("Server started on port 9999");
            // Print Server IP Address
            System.out.println("Server IP: " + InetAddress.getLocalHost().getHostAddress());
        } catch (IOException e) {
            System.err.println("Could not listen on port: 9999.");
            System.exit(-1);
        }
 
        while (listening) {
            // wait for client connection
            Socket clientSocket = serverSocket.accept();
            System.out.println("Client connected: " + clientSocket.getInetAddress().getHostName());

            // Send initial welcome message to client
            PrintWriter writer = new PrintWriter(new OutputStreamWriter(clientSocket.getOutputStream()), true);
            writer.println("Welcome to the server!"); // println() writes a string, followed by the '\n' character, to the output stream
            writer.flush(); // flush() flushes the output stream and forces any buffered output bytes to be written out
            
            // Read from client
            BufferedReader reader = new BufferedReader(new InputStreamReader(clientSocket.getInputStream(), StandardCharsets.UTF_8));
            String receivedLine; // read a line from the client
            receivedLine = reader.readLine(); // readLine() reads a line of text until it encounters a '\n' or '\r' character
            System.out.println("Received message from client: " + receivedLine);

            // Send customer message to client
            System.out.print("Enter message to send to client: ");
            String sendLine = scanner.nextLine();
            writer.println(sendLine);
            writer.flush();
        }
        serverSocket.close();
        scanner.close();
    }
}