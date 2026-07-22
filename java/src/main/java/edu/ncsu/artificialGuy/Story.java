package edu.ncsu.artificialGuy;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

public final class Story {
    private final String originalText;

    public Story(File file) throws IOException {
        if (file == null || !file.isFile()) {
            throw new IOException("Story file not found: " + file);
        }
        originalText = new String(Files.readAllBytes(file.toPath()), StandardCharsets.UTF_8);
    }

    public String getText() {
        return originalText;
    }
}
