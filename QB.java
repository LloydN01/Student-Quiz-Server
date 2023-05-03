import java.net.*;
import java.io.*;
import java.util.*;

public class QB {
    public static int port;
    public static String serverType;
    public static void main(String[] args) throws IOException {
        if (args[0].equals("-p")){
            port = 9998;
            serverType = "Python";
        }
        else{
            port = 9999;
            serverType = "Java";
        }
        
        ServerSocket serverSocket = null;
        boolean listening = true;

        try {
            serverSocket = new ServerSocket(port); // set port number
            // Print Server Port Number
            System.out.println(serverType + " Server is listening on port " + port);
        } catch (IOException e) {
            System.err.println("Could not listen on port: "+port);
            System.exit(-1);
        }

        while (listening) {
            // wait for client connection
            Socket clientSocket = serverSocket.accept();
            System.out.println("Client connected: " + clientSocket.getInetAddress().getHostName());

            Scanner scanner = new Scanner(System.in);
            PrintWriter writer = new PrintWriter(clientSocket.getOutputStream(), true);
            BufferedReader reader = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));

            // Send initial welcome message to client
            writer.println("Welcome to the server!"); // println() writes a string, followed by the '\n' character, to the output stream
            writer.flush(); // flush() flushes the output stream and forces any buffered output bytes to be written out

            while(clientSocket.isConnected()){
                // Read from client
                String receivedLine = reader.readLine(); // readLine() reads a line of text until it encounters a '\n' or '\r' character
                System.out.println("Received message from client: " + receivedLine);

                // Send custom message to client
                System.out.print("Enter message to send to client: ");
                String sendLine = scanner.nextLine();
                writer.println(sendLine);
                writer.flush();
            }

            try {
                writer.close();
                reader.close();
                clientSocket.close();
                scanner.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        serverSocket.close();
    }
}