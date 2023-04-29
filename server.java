import java.io.*;
import java.net.*;

public class server {

    public static void main(String[] args) throws IOException {
        // create a server socket object and listen for incoming connections
        int portNumber = 1234;
        ServerSocket serverSocket = new ServerSocket(portNumber);
        InetAddress hostAddress = InetAddress.getLocalHost();
        System.out.println("Server started and listening on port " + hostAddress.getHostAddress() + ":" + portNumber);

        while (true) {
            // accept an incoming client connection
            Socket clientSocket = serverSocket.accept();
            System.out.println("Client connected: " + clientSocket);
            System.out.println("not here");
            // create a buffered reader to read data from the client
            DataInputStream in = new DataInputStream(clientSocket.getInputStream());
            System.out.println("not here");
            // read the incoming data from the client
            System.out.println(in);
            System.out.println("not here");
            // DataOutputStream out = new DataOutputStream(server.getOutputStream());
            

            // close the client connection
            clientSocket.close();
            // close the server connection
        }
        // serverSocket.close();
    }
}
