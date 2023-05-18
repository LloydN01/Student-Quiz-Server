import java.net.*;
import java.io.*;
import java.util.*;

import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;
import java.lang.reflect.Method;

public class QB {
    public static int port;
    public static String serverType;
    public static String locationOfQuestionFiles = "./Questions/";
    public static int counter = 0; // Counter for javaTester() function

    public static void main(String[] args) throws Exception {
        if (args[0].equals("-p")){
            port = 9998;
            serverType = "Python";
        }
        else if (args[0].equals("-j")){
            port = 9999;
            serverType = "Java";
        }
        String ip_address = args[1];

        ArrayList<String> readQuestions = readFile(locationOfQuestionFiles + serverType + "Questions.txt");

        Socket serverSocket = null;
        boolean listening = true;

        try {
            serverSocket = new Socket(ip_address,port); // set port number
            // Print Server Port Number
            System.out.println(serverType + " Client is connected to port " + port);
        } catch (IOException e) {
            System.err.println("Could not connect to port: "+port);
            System.exit(-1);
        }

        while (listening) {
            Scanner scanner = new Scanner(System.in);
            PrintWriter writer = new PrintWriter(serverSocket.getOutputStream(), true);
            BufferedReader reader = new BufferedReader(new InputStreamReader(serverSocket.getInputStream()));

            while(serverSocket.isConnected()){
                // Read from client
                String receivedString = reader.readLine(); //reads a line of text until it encounters a '\n' or '\r' and then adds it to receievedString
                if (receivedString.equals("PING")){
                    writer.println("PONG");
                    writer.flush();
                }
                else{
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
                            case "$MCQ$":
                                //Marking a multiple choice question
                                //Format is id$ans - where id is the id of the question and ans is the answer that is being checked.
                                
                                splittedStrings = receivedString.split("\\$");
                                //get the id of the question
                                id = Integer.parseInt(splittedStrings[0]);
                                //get the answer of the user
                                ans = splittedStrings[1];
                                //get the actual question
                                question = readQuestions.get(id);
                                index = question.lastIndexOf("$");
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
                                //Marking a short answer question
                                //Format is id$ans - where id is the id of the question and ans is the answer that is being checked.

                                splittedStrings = receivedString.split("\\$");
                                //get the id of the question
                                id = Integer.parseInt(splittedStrings[0]);
                                //get the answer of the user
                                ans = splittedStrings[1];

                                //get the actual question
                                question = readQuestions.get(id);

                                index = question.lastIndexOf("$");
                                correctAns = question.substring(index+1);

                                int secondLastIndex = question.lastIndexOf("$", index-1);
                                String[] paramsString = question.substring(secondLastIndex+1, index).split(",");

                                Object params[] = new Object[paramsString.length];
                                for (int i = 0; i < paramsString.length; i++){
                                    params[i] = Integer.parseInt(paramsString[i]);
                                }

                                // replace --n with \n and \t with tab
                                ans = ans.replace("--n", "\n");
                                ans = ans.replace("\\n", "\n");
                                ans = ans.replace("\\t", "\t");
                                correctAns = correctAns.replace("--n", "\n");
                                correctAns = correctAns.replace("\\n", "\n");
                                correctAns = correctAns.replace("\\t", "\t");

                                String userAns = ""; // user's answer
                                String actualAns = ""; // actual answer
                                if (serverType == "Python"){ 
                                    userAns = pythonTester(ans, params.length, params);
                                    actualAns = pythonTester(correctAns, params.length, params);
                                }
                                else{
                                    userAns = javaTester(ans, params.length, params);
                                    File userFile = new File(String.format("./MyClass%d.java", counter));
                                    userFile.delete();
                                    File userFile2 = new File(String.format("./MyClass%d.class", counter));
                                    userFile2.delete();

                                    actualAns = javaTester(correctAns, params.length, params);
                                    File actualFile = new File(String.format("./MyClass%d.java", counter));
                                    actualFile.delete();
                                    File actualFile2 = new File(String.format("./MyClass%d.class", counter));
                                    actualFile2.delete();
                                }
                                File file = new File(String.format("./MyClass%d.java", counter));
                                file.delete();
                                File file2 = new File(String.format("./MyClass%d.class", counter));
                                file2.delete();

                                if (userAns.equals(actualAns)){
                                    // If the answer is correct send correct to the TM
                                    writer.println("correct");
                                }
                                else {
                                    // If the answer is wrong send wrong to the TM
                                    writer.println("wrong");
                                }
                                writer.flush();
                                break;
                            case "$ANS$":
                                // When TM requests the answer of a question
                                id = Integer.parseInt(receivedString);
                                question = readQuestions.get(id);
                                index = question.lastIndexOf("$");
                                correctAns = question.substring(index+1);
                                writer.println(correctAns); // send the correct answer to the TM
                                writer.flush(); 
                                break;
                    }
                }

            }

            try {
                // Close all the connections
                writer.close();
                reader.close();
                serverSocket.close();
                scanner.close();
            } catch (IOException e) {
                e.printStackTrace();
            }

            break;
        }
        serverSocket.close(); // close the server socket
    }

    // Execute the python code and return the output
    public static String pythonTester(String userCode, int paramCount, Object... parameter) throws Exception { 
        try {
            // Checks if the number of parameters is correct
            if (!isCorrectNumberOfParameter(userCode, paramCount)){ return ""; }

            // Create a ProcessBuilder object to run the Python interpreter
            ProcessBuilder pb = new ProcessBuilder("python", "-");
            Process p = pb.start();
            BufferedReader out = new BufferedReader(new InputStreamReader(p.getInputStream()));

            String params = "";
            for(Object x: parameter){
                params += String.valueOf(x) + ",";
            }
            String code = userCode+ "\nprint(myMethod("+params+"))";

            p.getOutputStream().write(code.getBytes());
            p.getOutputStream().close();
            String output = out.readLine();
            p.waitFor();
            return output; 
        } catch (Exception e) {
            return "";
        }
    }

    // Execute the java code and return the output
    public static String javaTester(String userCode,int paramCount, Object... arguments) throws Exception {
        try{
            // Checks if the number of parameters is correct
            if (!isCorrectNumberOfParameter(userCode, paramCount)){ return ""; }

            // Create a unique class name to prevent past executions from being reused
            String myClassDeclaration = String.format("public class MyClass%d {%s}", counter, userCode);

            // Compile the Java file
            String fileName = "MyClass" + counter + ".java";
            String filePath = "./" + fileName;
            createFile(filePath, myClassDeclaration);
            JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
            compiler.run(null, null, null, filePath);

            // Load the compiled class
            Class<?> compiledClass = Class.forName(String.format("MyClass%d", counter));
            Class<?>[] argList = new Class[paramCount];
            Arrays.fill(argList, int.class);

            // Get the myMethod() method
            Method method = compiledClass.getMethod("myMethod", argList);

            // Invoke the method using reflection
            Object returnValue = method.invoke(null, arguments);
            String theirAnswer = String.valueOf(returnValue);

            // Delete the files
            File file = new File(filePath);
            file.delete();
            File file2 = new File(String.format("./MyClass%d.class", counter));
            file2.delete();

            counter++; // increment the counter -> for unqiue class names

            return theirAnswer;
        }catch(Exception e){            
            return "";
        }
    }

    // Checks if the number of parameters is correct
    public static void createFile(String filePath, String content) {
        try {
            File file = new File(filePath);

            // Create the file if it doesn't exist
            if (!file.exists()) {
                file.createNewFile();
            }

            // Write the content to the file
            java.nio.file.Files.write(file.toPath(), content.getBytes());
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

            // Each question will have the format [Question#]$[Language]$[MC]$[Question]$[Options]$[Answer]
            // Example: 1$Java$MC$What is the capital of Canada?$Toronto,Ottawa,Vancouver,Montreal$Ottawa
            // Or, for Short Answer questions (SA), the format will be [Question#]$[Language]$[SA]$[Question]$[Answer]
            // Example: 2$Python$SA$What is the capital of Canada?$Ottawa
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
            String question = questionsList.get(randomIndex);

            int index;
            if (question.contains("$SA$")){
                index = question.lastIndexOf("$");
                question = question.substring(0,index); // Removing actual answer before sending it to QB
                index = question.lastIndexOf("$");
                question = question.substring(0,index); // Removing test cases answer before sending it to QB
            }
            else{
                index = question.lastIndexOf("$");
                question = question.substring(0,index); // Removing actual answer before sending it to QB
            }
            randomQuestions[i] = question;
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

    // Function that checks if users code has correct number of parameters
    public static boolean isCorrectNumberOfParameter(String userCode, int paramCount){
        // Gets the indexes of the left and right bracket
        int bracketIndexLeft = userCode.indexOf('(');
        int bracketIndexRight = userCode.indexOf(')');

        // Gets the parameters from the user's code
        String params = userCode.substring(bracketIndexLeft+1, bracketIndexRight);
        int userParamCount = params.split(",").length;

        // Checks if the number of parameters is correct
        return (userParamCount == paramCount);
    }
}