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
            // wait for client connection
            // Socket clientSocket = serverSocket.accept();
            // System.out.println("Client connected: " + clientSocket.getInetAddress().getHostName());

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
                                splittedStrings = receivedString.split("\\$");
                                //get the id of the question
                                id = Integer.parseInt(splittedStrings[0]);
                                //get the answer of the user
                                ans = splittedStrings[1];


                                question = readQuestions.get(id);
                                index = question.lastIndexOf("$");
                                correctAns = question.substring(index+1);
                                int secondIdex = question.lastIndexOf("$",index-1);
                                String[] params = question.substring(secondIdex+1,index).split(",");

                                int[] intparams = new int[params.length];
                                int count = 0;
                                for(String x: params){
        
                                    intparams[count] = Integer.parseInt(x);
                                    count ++;
                                }

                                String userAns;
                                String actualAns;

                                System.out.println("ASBDIBASIBDUISB");
                                
                                if (serverType == "Python"){ 
                                    userAns = pythonTester(ans, id, intparams);
                                    actualAns = pythonTester(correctAns,id, intparams);
                                }
                                else{
                                    userAns = javaTester(ans, intparams);
                                    actualAns = javaTester(correctAns, intparams);
                                    System.out.print(userAns +"SANDONSAOD" + actualAns);
                                }
    
                                if (userAns.equals(actualAns)){
                                    writer.println("correct");
                                }
                                else{
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


    // //Sum of 2 numbers 
    // public static int sum(int a,int b){ 
    //     return a + b;
    // }
    // //Maximum of 2 numbers 
    // public static int max(int a,int b){ 
    //     return a > b ? a : b;
    // }
    // //Even or odd 
    // public static String evenOrOdds(int a){ 
    //     return a % 2 == 0 ? "Even":"Odd";
    // }
    // //Add two and square
    // public static int addTwoSquare(int a){ 
    //     return (int) Math.pow(a+2,2);
    // }
    // public static String helloWorld(){ 
    //     return "Hello world!";
    // }

    // public static String pythonTester(String code, int question){ 
    //     try {
    //         // // Create a ProcessBuilder object to run the Python interpreter
    //         ProcessBuilder pb = new ProcessBuilder("python", "-");
    //         String correct_output = "";
    //         Process p = pb.start();
    //         int Q_ID = question;
    //         int a = 2; 
    //         int b = 7;
    //         String params = "";
    //         String call = "";
    //         BufferedReader out = new BufferedReader(new InputStreamReader(p.getInputStream()));
    //         // code = "def func_one(a,b):\n  return a + b\n\nprint(func_one(3))";
    //         switch (Q_ID){
    //             case 12: 
    //                 correct_output = "Hello World!";
    //                 break; 
    //             case 13:
    //                 params="a,b";
    //                 call = Integer.toString(a) + "," + Integer.toString(b);
    //                 correct_output = "9";
    //                 break;
    //             case 14: 
    //                 params = "a,b";
    //                 call = Integer.toString(a) + "," + Integer.toString(b);
    //                 correct_output = "7";
    //                 break; 
    //             case 15: 
    //                 call = Integer.toString(a);
    //                 params = "a";
    //                 correct_output = "even";
    //                 break;
    //         }
    //         code = "def func_one("+params+"):\n  return a + b\n\nprint(func_one("+call+"))";
    //         p.getOutputStream().write(code.getBytes());
    //         p.getOutputStream().close();
    //         String output = out.readLine();
    //         System.out.println(output);
    //         p.waitFor();
    //         System.out.println("RETURNED: " + output);
    //         System.out.println("CORRECT: " + correct_output);
    //         if (output.equals(correct_output)){
    //             System.out.println("Success");
    //             return "Correct";
    //         } else { 
    //             System.out.println("Failure");
    //             return "Incorrect";
    //         }
    //         // return "Hello"; 
    //     } catch (IOException | InterruptedException e) {
    //         e.printStackTrace();
    //     }
    //     return "";
    // }
    
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
            return "";
        }
    }

    // public static String javaTester(String code, int question) throws Exception{
    //     // Create an in-memory Java file
    //     String className = "MyClass";
    //     String fileName = className + ".java";
    //     String filePath = System.getProperty("user.dir") + "/" + fileName;
    //     createFile(filePath, code); // Assume FileManager is a utility class to create files
    //     int a = 2; 
    //     int b = 7;
    //     int Q_ID = question;
    //     String correct_output = "";
    //     // Compile the Java file
    //     JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
    //     compiler.run(null, null, null, filePath);
    //     // Load the compiled class
    //     Class<?> compiledClass = Class.forName(className);

    //     // Invoke the method using reflection
    //     Method method = null; 
    //     //compiledClass.getMethod("myMethod",int.class,int.class);
    //     Object returnValue = null;
    //     switch (Q_ID){ 
    //         case 11:
    //             correct_output = "9";
    //             method = compiledClass.getMethod("myMethod",int.class,int.class);
    //             returnValue = (int) method.invoke(null,a,b);
    //             break;
    //         case 12: 
    //             correct_output = "7";
    //             method = compiledClass.getMethod("myMethod",int.class,int.class);
    //             returnValue = (int) method.invoke(null,a,b);
    //             break; 
    //         case 13: 
    //             correct_output = "odd";
    //             method = compiledClass.getMethod("myMethod",int.class);
    //             returnValue = method.invoke(null,a);
    //             break;
    //         case 14: 
    //             correct_output = "16";
    //             method = compiledClass.getMethod("myMethod",int.class);
    //             returnValue = method.invoke(null,a);
    //             break;
    //     }
    //     String their_answer= returnValue.toString();
    //     System.out.println("RETURNED: " + their_answer);
    //     System.out.println("CORRECT: " + correct_output);
    //     if (their_answer.equals(correct_output)){
    //         System.out.println("Success");
    //         return "Correct";
    //     } else { 
    //         System.out.println("Failure");
    //         return "Incorrect";
    //     }
    //     // return "The return value is:" + returnValue.toString();
    // }
    // public static void createFile(String filePath, String content) {
    //     try {
    //         File file = new File(filePath);

    //         // Create the file if it doesn't exist
    //         if (!file.exists()) {
    //             file.createNewFile();
    //         }

    //         // Write the content to the file
    //         java.nio.file.Files.write(file.toPath(), content.getBytes());
    //         System.out.println("File created successfully at: " + filePath);
    //     } catch (IOException e) {
    //         e.printStackTrace();
    //     }
    // }

    public static String javaTester(String userCode, int[] parameter) throws Exception{
        // Create an in-memory Java file
        String className = "MyClass";
        String fileName = className + ".java";
        String filePath = System.getProperty("user.dir") + "/" + fileName;
        createFile(filePath, userCode); // Assume FileManager is a utility class to create files
        // Compile the Java file
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        compiler.run(null, null, null, filePath);
        // Load the compiled class
        Class<?> compiledClass = Class.forName(className);

        // Invoke the method using reflection
        Method method = null; 
        //compiledClass.getMethod("myMethod",int.class,int.class);
        Object returnValue = null;
        method = compiledClass.getMethod("myMethod",int.class,int.class);
        returnValue = (int) method.invoke(null, parameter[0], parameter[1]);
        String their_answer= returnValue.toString();
        return their_answer;
        // return "The return value is:" + returnValue.toString();
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
            //gets the number of occurance of $
            int count = question.length() - question.replace("$", "").length();

            // if the number of $ isnt 3, then its a mcq, and the ans should be remvoed 
            if (count != 3){
                int index = question.lastIndexOf("$");
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