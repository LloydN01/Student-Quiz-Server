import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
public class pythonTester {

    public static void main(String[] args) {
        String[] paramsString = "8,3".split(",");

        Object params[] = new Object[paramsString.length];
        for (int i = 0; i < paramsString.length; i++){
            params[i] = Integer.parseInt(paramsString[i]);
        }
        String ans = "def myMethod(a, b):\n\treturn max(a, b)";
        tester(ans, params);
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
    public static String helloWorld(){ 
        return "Hello world!";
    }
    public static String tester(String userCode, Object... parameter){ 
        try {
            // // Create a ProcessBuilder object to run the Python interpreter
            ProcessBuilder pb = new ProcessBuilder("python", "-");
            Process p = pb.start();
            BufferedReader out = new BufferedReader(new InputStreamReader(p.getInputStream()));
            // code = "def func_one("+params+"):\n  return a + b\n\nprint(func_one("+call+"))";
            String params = "";
            for(Object x: parameter){
                params += String.valueOf(x) + ",";
            }
            String code = userCode+ "\nprint(myMethod("+params+"))";
            // code = "def func_one(a,b):\n  return a + b\n\nprint(func_one(3,2))";
            p.getOutputStream().write(code.getBytes());
            p.getOutputStream().close();
            String output = out.readLine();
            System.out.println(output);
            p.waitFor();
            System.out.println("RETURNED: " + output);
            return output; 
        } catch (IOException | InterruptedException e) {
            return "";
        }
    }
}