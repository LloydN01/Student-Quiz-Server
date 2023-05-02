import java.net.*;
import java.io.*;
import java.util.*;

public class JavaServer {
    public static void main(String[] args) throws IOException {
        ServerSocket serverSocket = null;
        boolean listening = true;

        try {
            serverSocket = new ServerSocket(9999); // set port number
            // Print Server Port Number
            System.out.println("Server started on port 9999");
        } catch (IOException e) {
            System.err.println("Could not listen on port: 9999.");
            System.exit(-1);
        }

        while (listening) {
            // wait for client connection
            Socket clientSocket = serverSocket.accept();
            System.out.println("Client connected: " + clientSocket.getInetAddress().getHostName());

            // Create a new thread for the client
            ClientThread clientThread = new ClientThread(clientSocket);
            clientThread.start();
        }
        serverSocket.close();
    }
}

class ClientThread extends Thread {
    private Socket clientSocket = null;

    public ClientThread(Socket socket) {
        super("ClientThread");
        clientSocket = socket;
    }

    public void run() {
        try {
            Scanner scanner = new Scanner(System.in);
            PrintWriter writer = new PrintWriter(clientSocket.getOutputStream(), true);
            BufferedReader reader = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));

            // Send initial welcome message to client
            writer.println("Welcome to the server!"); // println() writes a string, followed by the '\n' character, to the output stream
            writer.flush(); // flush() flushes the output stream and forces any buffered output bytes to be written out

            while(clientSocket.isConnected()){
                // Read from client
                String receivedLine = reader.readLine(); // readLine() reads a line of text until it encounters a '\n' or '\r' character
                if(receivedLine.contains("//JAVA//")){
                    System.out.println("Received message from client: " + receivedLine);
                }
                else{
                    System.out.println("no message");
                }
                // Send customer message to client
                System.out.print("Enter message to send to client: ");
                String sendLine = scanner.nextLine();
                writer.println(sendLine);
                writer.flush();
            }

            writer.close();
            reader.close();
            clientSocket.close();
            scanner.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}