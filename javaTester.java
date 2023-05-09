import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;
import java.lang.reflect.Method;
import java.io.File;
import java.io.IOException;

public class DynamicCodeExecution {
    public static void main(String[] args) throws Exception {
        // Java code to be executed
        String code = "public class MyClass { public static void myMethod() { System.out.println(\"Hello, World!\"); } }";

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
        method.invoke(null);
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
    
