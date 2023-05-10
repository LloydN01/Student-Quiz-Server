import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class DynamicCodeExecution2 {
    public static void main(String[] args) {
        // Python code to be executed
        String pythonCode = """
                                def hello_world():
                                    return 'Hello, World!'
                                print(hello_world())""";
        try {
            // Execute Python code using the Python interpreter
            ProcessBuilder processBuilder = new ProcessBuilder("python", "-c", pythonCode);
            Process process = processBuilder.start();

            // Read the output
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }

            // Wait for the process to finish
            int exitCode = process.waitFor();
            System.out.println("Process exited with code: " + exitCode);
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}