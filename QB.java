import java.net.*;
import java.io.*;
import java.util.*;
import java.util.ArrayList;

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

        ArrayList<String> readQuestions = readFile(locationOfQuestionFiles + serverType + "Questions.txt");

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
                String receivedString = reader.readLine();
                if (receivedString.contains("$REQ$")){ // readLine() reads a line of text until it encounters a '\n' or '\r' character
                    // "$REQ$" signifies the start of a request

                    String[] splited_input = receivedString.split("\\$"); // splits the string by $ (the flag)
                    int numQuestions = Integer.parseInt(splited_input[splited_input.length-1]); // parses the last element, which is the number to integer 
                    System.out.println("Number of " + serverType + " questions requested: " + numQuestions);
    
                    // Generate random questions
                    String[] randomQuestions = generateRandomQuestions(numQuestions, readQuestions);
                    
                    // // Send custom message to client
                    // String questions = concatenateQuestions(randomQuestions);
                    // writer.println(questions);
                    // writer.flush();

                    for(int i = 0; i < randomQuestions.length; i++){
                        writer.println(randomQuestions[i]);
                        writer.flush();
                        reader.readLine();  // Wait for ack
                    }

                    System.out.println("Questions sent to TM");

                } else if (receivedString.contains("$ANS$")){
                    // "$ANS$" signifies the start of an answer
                    // TODO: Implement code to deal with recieving the user answers and marking it
                }
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
    public static ArrayList<String> readFile(String fileName) throws IOException {
        BufferedReader buffer = new BufferedReader(new FileReader(fileName));
        
        String line = buffer.readLine(); // readLine() reads a line of text until it encounters a '\n' or '\r' character
        ArrayList<String> questionsList = new ArrayList<String>();

        int count = 0;
        while (line != null) {
            questionsList.add(Integer.toString(count ++) + "$" + serverType + "$" + line);
            line = buffer.readLine();

            // Each question will have the format [Question#]$[Language]$[MC]$[Question]$[Options]
            // Example: 1$Java$MC$What is the capital of Canada?$Toronto,Ottawa,Vancouver,Montreal
            // Or, for Short Answer questions (SA), the format will be [Question#]$[Language]$[SA]$[Question]
            // Example: 2$Python$SA$What is the capital of Canada?
        }

        buffer.close();
        return questionsList;
    }

    // Function that generates random questions and puts them in an array
    public static String[] generateRandomQuestions(int numQuestions, ArrayList<String> readQuestions){
        String[] randomQuestions = new String[numQuestions];
        ArrayList<String> questionsList = new ArrayList<String>(readQuestions); // Copy readQuestions to questionsList
        Random rand = new Random();

        for (int i = 0; i < numQuestions; i++){
            int randomIndex = rand.nextInt(questionsList.size());
            randomQuestions[i] = questionsList.get(randomIndex);
            questionsList.remove(randomIndex);
        }

        return randomQuestions;
    }

    // Function that concatenates all the questions into one string
    public static String concatenateQuestions(String[] randomQuestions){
        String questions = "";

        for (int i = 0; i < randomQuestions.length; i++){
            questions += randomQuestions[i] + "$$"; // $$ is the delimiter for the questions
        }

        return questions;
    }
}