import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
public class pythonTester {

    public static void main(String[] args) {
        tester("a");
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
    public static String tester(String code){ 
        try {
            // // Create a ProcessBuilder object to run the Python interpreter
            ProcessBuilder pb = new ProcessBuilder("python", "-");
            String correct_output = "";
            Process p = pb.start();
            int Q_ID = 13;
            int a = 3; 
            int b = 7;
            String params = "";
            String call = "";
            BufferedReader out = new BufferedReader(new InputStreamReader(p.getInputStream()));
            // code = "def func_one(a,b):\n  return a + b\n\nprint(func_one(3))";
            switch (Q_ID){
                case 12: 
                    correct_output = helloWorld();
                    break; 
                case 13:
                    params="a,b";
                    call = Integer.toString(a) + "," + Integer.toString(b);
                    correct_output = Integer.toString(sum(a,b));
                    break;
                case 14: 
                    params = "a,b";
                    call = Integer.toString(a) + "," + Integer.toString(b);
                    correct_output = Integer.toString(max(a,b));
                    break; 
                case 15: 
                    call = Integer.toString(a);
                    params = "a";
                    correct_output = evenOrOdds(a);
                    break;
            }
            code = "def func_one("+params+"):\n  return a + b\n\nprint(func_one("+call+"))";
            p.getOutputStream().write(code.getBytes());
            p.getOutputStream().close();
            String output = out.readLine();
            System.out.println(output);
            p.waitFor();
            System.out.println("RETURNED: " + output);
            System.out.println("CORRECT: " + correct_output);
            if (output.equals(correct_output)){
                System.out.println("Success");
            } else { 
                System.out.println("Failure");
            }
            return "Hello"; 
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
        return "";
    }
}