package edu.ncsu.artificialGuy;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public final class CliMain {
    private CliMain() {
    }

    public static void main(String[] args) {
        try {
            Arguments arguments = Arguments.parse(args);
            runCoref(arguments.workspace);
        } catch (IllegalArgumentException exception) {
            System.err.println("error: " + exception.getMessage());
            printUsage();
            System.exit(2);
        } catch (Exception exception) {
            System.err.println("error: " + exception.getMessage());
            exception.printStackTrace(System.err);
            System.exit(1);
        }
    }

    private static void printUsage() {
        System.err.println("Usage: java -jar text-extraction-java.jar coref --workspace <path>");
    }

    private static void runCoref(Path workspace) throws Exception {
        Path content = workspace.resolve("content.txt");
        Path output = workspace.resolve("content_afterChange.txt");
        if (!Files.isRegularFile(content)) {
            throw new IllegalArgumentException("Input file not found: " + content);
        }

        Story story = new Story(content.toFile());
        String coRefText = NLP.getInstance().resolveCoRef(story.getText());
        Files.createDirectories(workspace);
        Files.write(output, coRefText.getBytes(StandardCharsets.UTF_8));
        System.out.println("Coreference output written to: " + output);
    }

    private static final class Arguments {
        private final Path workspace;

        private Arguments(Path workspace) {
            this.workspace = workspace;
        }

        private static Arguments parse(String[] args) {
            if (args.length != 3 || !"coref".equals(args[0]) || !"--workspace".equals(args[1])) {
                throw new IllegalArgumentException("Invalid arguments");
            }
            return new Arguments(Paths.get(args[2]).toAbsolutePath().normalize());
        }
    }
}
