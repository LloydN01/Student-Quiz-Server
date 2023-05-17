import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;
import java.lang.reflect.Method;
import java.io.File;
import java.io.IOException;

public class javaTester {
    public static void main(String[] args) throws Exception {
        // Java code to be executed
        String code = "public class MyClass {public static int myMethod(int a) { return (a+2) * (a+2); } }";
        System.out.println("Max: " + max(1,2));
        System.out.println("Sum: " + sum(1,2));
        System.out.println("Even: " + evenOrOdds(4));
        System.out.print(tester(code));
    }

    public static String tester(String code) throws Exception{
        // Create an in-memory Java file
        String className = "MyClass";
        String fileName = className + ".java";
        String filePath = System.getProperty("user.dir") + "/" + fileName;
        createFile(filePath, code); // Assume FileManager is a utility class to create files
        int a = 3; 
        int b = 7;
        int Q_ID = 14;
        String correct_output = "";
        // Compile the Java file
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        compiler.run(null, null, null, filePath);
        // Load the compiled class
        Class<?> compiledClass = Class.forName(className);

        // Invoke the method using reflection
        Method method = null; 
        //compiledClass.getMethod("myMethod",int.class,int.class);
        Object returnValue = null;
        switch (Q_ID){ 
            case 11:
                correct_output = Integer.toString(sum(a,b));
                method = compiledClass.getMethod("myMethod",int.class,int.class);
                returnValue = (int) method.invoke(null,a,b);
                break;
            case 12: 
                correct_output = Integer.toString(max(a,b));
                method = compiledClass.getMethod("myMethod",int.class,int.class);
                returnValue = (int) method.invoke(null,a,b);
                break; 
            case 13: 
                correct_output = evenOrOdds(a);
                method = compiledClass.getMethod("myMethod",int.class);
                returnValue = method.invoke(null,a);
                break;
            case 14: 
                correct_output = Integer.toString(addTwoSquare(a));
                method = compiledClass.getMethod("myMethod",int.class);
                returnValue = method.invoke(null,a);
                break;
        }
        String their_answer= returnValue.toString();
        System.out.println("RETURNED: " + their_answer);
        System.out.println("CORRECT: " + correct_output);
        if (their_answer.equals(correct_output)){
            System.out.println("Success");
        } else { 
            System.out.println("Failure");
        }
        return "The return value is:" + returnValue.toString();
    }
    //Sum of 2 numbers 
    public static int sum(int a,int b){ 
        return a + b;
    }
    //Maximum of 2 numbers 
    public static int max(int a,int b){ 
        return a > b ? a : b;
    }
    //Even or odd 
    public static String evenOrOdds(int a){ 
        return a % 2 == 0 ? "Even":"Odd";
    }
    //Add two and square
    public static int addTwoSquare(int a){ 
        return (int) Math.pow(a+2,2);
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
}
    
