import java.net.*;
import java.io.*;
import java.util.*;
import java.util.ArrayList;

import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;
import java.lang.reflect.Method;

public class QB {
    public static int port;
    public static String serverType;
    public static String locationOfQuestionFiles = "./Questions/";

    public static void main(String[] args) throws IOException {
        if (args[0].equals("-p")){
            port = 9998;
            serverType = "Python";
        }
        else if (args[0].equals("-j")){
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
                // TODO redo this shit (SUNNY JOB)
                String receivedString = reader.readLine(); //reads a line of text until it encounters a '\n' or '\r' and then adds it to receievedString
                String flag = receivedString.substring(0, 5); //get the flag
                receivedString = receivedString.substring(5); //remove the flag from the string

                //Variables
                String[] splittedStrings;
                int id;
                String ans;
                String question;
                int index;
                String correctAns;

                switch (flag){
                        //Requesting Questions
                        //Format is n - where n is the number of questions requested

                        case "$REQ$":
                            int numQuestions = Integer.parseInt(receivedString);
                            System.out.println("Number of " + serverType + " questions requested: " + numQuestions);

                            // Generate random questions
                            String[] randomQuestions = generateRandomQuestions(numQuestions, readQuestions);
                            
                            // Send custom message to client
                            String questions = concatenateQuestions(randomQuestions);
                            writer.println(questions);
                            writer.flush();
                            System.out.println("Questions sent to TM");
                            break;
                        //Marking a multiple choice question
                        //Format is id$ans - where id is the id of the question and ans is the answer that is being checked.
                        case "$MCQ$":
                            splittedStrings = receivedString.split("\\$");
                            //get the id of the question
                            id = Integer.parseInt(splittedStrings[0]);
                            //get the answer of the user
                            ans = splittedStrings[1];
                            //get the actual question
                            question = readQuestions.get(id);
                            index = question.lastIndexOf("\\$");
                            correctAns = question.substring(index+1);
                            if (ans.equals(correctAns)){
                                writer.println("correct");
                            }
                            else{
                                writer.println("wrong");
                            }
                            writer.flush();
                            break;
                        case "$SAQ$":
                            splittedStrings = receivedString.split("\\$");
                            //get the id of the question
                            id = Integer.parseInt(splittedStrings[0]);
                            //get the answer of the user
                            ans = splittedStrings[1];
                            String userAns;
                            if (serverType == "Python"){ 
                                userAns = pythonTester(ans);
                            }
                            else{
                                userAns = javaTester(ans);
                            }

                            //get the actual question
                            question = readQuestions.get(id);
                            index = question.lastIndexOf("\\$");
                            correctAns = question.substring(index+1);
                            if (userAns.equals(correctAns)){
                                writer.println("correct");
                            }
                            else{
                                writer.println("wrong");
                            }
                            writer.flush();
                            break;
                        case "$ANS$":
                            break;
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
    
    //python test method
    public static String pythonTester(String codeString) {
        // Python code to be executed
        String pythonCode = codeString;
        try {
            // Execute Python code using the Python interpreter
            ProcessBuilder processBuilder = new ProcessBuilder("python", "-c", pythonCode);
            Process process = processBuilder.start();

            // Read the output
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line = reader.readLine();
            return line;
    
        } catch (IOException e) {
            e.printStackTrace();
            return "$F$";
        }
    }

    public static String javaTester(String codeString){
        // Java code to be executed
        try{
        String code = codeString;

        // Create an in-memory Java file
        String className = "MyClass";
        String fileName = className + ".java";
        String filePath = System.getProperty("user.dir") + "/" + fileName;
        createFile(filePath, code); // Assume FileManager is a utility class to create files

        // Compile the Java file
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        compiler.run(null, null, null, filePath);

        // Load the compiled class
        Class<?> compiledClass = Class.forName(className);

        // Invoke the method using reflection
        Method method = compiledClass.getMethod("myMethod");
        Object returnValue = method.invoke(null);
        return String.valueOf(returnValue);
        } catch (Exception e){
            return "$F";
        }

    }


    public static void createFile(String filePath, String content) {
        try {
            File file = new File(filePath);

            // Create the file if it doesn't exist
            if (!file.exists()) {
                file.createNewFile();
            }

            // Write the content to the file
            java.nio.file.Files.write(file.toPath(), content.getBytes());
            System.out.println("File created successfully at: " + filePath);
        } catch (IOException e) {
            e.printStackTrace();
        }
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