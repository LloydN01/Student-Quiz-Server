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
            System.out.println(serverType + " Server is listening on port " + port);
        } catch (IOException e) {
            System.err.println("Could not listen on port: "+port);
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
                    // System.out.println("Received PING");
                    writer.println("PONG");
                    writer.flush();
                    // System.out.println("Sending PONG");
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

                                // replaces the --n with new line characters 
                                ans = ans.replace("--n", "\n");

                                String userAns = "1";
                                String actualAns = "1";

                                if (serverType == "Python"){ 
                                    // userAns = pythonTester(ans, id, params);
                                    // actualAns = pythonTester(correctAns,id, params);
                                }
                                else{
                                    // javaTester returns "" when there is an error -> when user answer is syntactically incorrect
                                    // File file = new File(System.getProperty("user.dir") + "/" + "MyClass.class");
                                    // file.delete();
                                    // file = new File(System.getProperty("user.dir") + "/" + "MyClass.java");
                                    // file.delete();
                                    userAns = javaTester(ans,params.length, params);
                                    // file = new File(System.getProperty("user.dir") + "/" + "MyClass.class");
                                    // file.delete();
                                    // file = new File(System.getProperty("user.dir") + "/" + "MyClass.java");
                                    // file.delete();
                                    actualAns = javaTester(correctAns,params.length,params);
                                }
                                System.out.println("UserAns"+userAns);
                                System.out.println("ActualAns"+actualAns);
                                if (userAns.equals(actualAns)){
                                    writer.println("correct");
                                }
                                else if(userAns.equals("") || !userAns.equals(actualAns)){
                                    writer.println("wrong");
                                }
                                writer.flush();
                                break;
                            case "$ANS$":
                                id = Integer.parseInt(receivedString);
                                question = readQuestions.get(id);
                                index = question.lastIndexOf("$");
                                correctAns = question.substring(index+1);
                                writer.println(correctAns);
                                writer.flush(); 
                                break;
                    }
                }

            }

            try {
                writer.close();
                reader.close();
                serverSocket.close();
                scanner.close();
            } catch (IOException e) {
                e.printStackTrace();
            }

            break;
        }
        serverSocket.close();
    }

    public static String pythonTester(String userCode, int question, int[] parameter){ 
        try {
            // // Create a ProcessBuilder object to run the Python interpreter
            ProcessBuilder pb = new ProcessBuilder("python", "-");
            Process p = pb.start();
            int Q_ID = question;
            String params = "";
            for(int x: parameter){
                params += Integer.toString(x) + ",";
            }
            params = params.substring(0, params.length());
            System.out.print(params);

            BufferedReader out = new BufferedReader(new InputStreamReader(p.getInputStream()));
            // code = "def func_one(a,b):\n  return a + b\n\nprint(func_one(3))";
            String code = userCode + "\nprint(func" + Q_ID + "(" + params + "))";
            p.getOutputStream().write(code.getBytes());
            p.getOutputStream().close();
            String output = out.readLine();
            System.out.println(output);
            p.waitFor();
            return output;
        } catch (IOException | InterruptedException e) {
            return ""; // Returns empty string if there is an error
        }
    }

    public static String javaTester(String userCode,int paramCount, Object... arguments) throws Exception {
            try{
                // Compile the Java file
                String fileName = "MyClass.java";
                String filePath = System.getProperty("user.dir") + "/" + fileName;
                createFile(filePath, userCode);
                JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
                compiler.run(null, null, null, filePath);
                System.out.println("here");
                // Load the compiled class
                Class<?> compiledClass = Class.forName("MyClass");
                Class<?>[] argList = new Class[paramCount];
                Arrays.fill(argList, int.class);
                // Get the myMethod() method
                Method method = compiledClass.getMethod("myMethod", argList);
                System.out.println("here2");
                // Invoke the method using reflection
                Object returnValue = method.invoke(null, arguments);
                System.out.println("ijijijiji");
                String theirAnswer = String.valueOf(returnValue);
                System.out.println("THIS SHOULDNT BE PRINTED TWICE");
                System.out.println(userCode);
                
                return theirAnswer;
            }catch(Exception e){
                
                return "INVALID BITCH0";
            }
        
    }

    public static void createFile(String filePath, String content) {
        try {
            File file = new File(filePath);

            // Create the file if it doesn't exist
            if (file.exists()) {
                file.delete();
                file.createNewFile();
                System.out.println("File deleted at: " + filePath);
            }
            else{
                file.createNewFile();
            }
            File file2 = new File(System.getProperty("user.dir") + "/" + "MyClass.class");

            if (file2.exists()){
                file2.delete();
                System.out.println("File deleted");
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


}