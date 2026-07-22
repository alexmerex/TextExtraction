package edu.ncsu.artificialGuy;

import static org.junit.Assert.assertEquals;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.Test;

public class StoryTest {
    @Test
    public void preservesUtf8AndLineBreaks() throws Exception {
        Path file = Files.createTempFile("story", ".txt");
        String expected = "Xin chào.\nSecond line.";
        Files.write(file, expected.getBytes(StandardCharsets.UTF_8));

        assertEquals(expected, new Story(file.toFile()).getText());
    }
}
