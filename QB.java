import java.net.*;
import java.io.*;
import java.util.*;

public class QB {
    public static int port;
    public static String serverType;
    public static String locationOfQuestionFiles = "./Questions/";

    public static void main(String[] args) throws IOException {
        if (args[0].equals("-p")){
            port = 9998;
            serverType = "Python";
        }
        else{
            port = 9999;
            serverType = "Java";
        }

        String readQuestions = readFile(locationOfQuestionFiles + serverType + "Questions.txt");
        
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

            while(clientSocket.isConnected()){
                // Read from client
                String receivedLine = reader.readLine(); // readLine() reads a line of text until it encounters a '\n' or '\r' character
                System.out.println("Received message from client: " + receivedLine);

                // Send custom message to client
                System.out.print("Enter message to send to client: ");
                String sendLine = scanner.nextLine();
                writer.println(sendLine);
                writer.flush();
                System.out.println("Message sent");

                writer.println(readQuestions);
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

            break;
        }
        serverSocket.close();
    }

    // Function that reads a text file
    public static String readFile(String fileName) throws IOException {
        BufferedReader buffer = new BufferedReader(new FileReader(fileName));
        try {
            StringBuilder fileContent = new StringBuilder(); // Creates a mutable sequence of characters
            String line = buffer.readLine(); // readLine() reads a line of text until it encounters a '\n' or '\r' character

            while (line != null) {
                fileContent.append(line);
                fileContent.append("\n");
                line = buffer.readLine();
            }

            return fileContent.toString();
        } finally {
            buffer.close();
        }
    }
}