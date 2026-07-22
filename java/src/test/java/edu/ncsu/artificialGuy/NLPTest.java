package edu.ncsu.artificialGuy;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class NLPTest {
    @Test
    public void replacesPronounsWithRepresentativeMentions() {
        String input = "Barack Obama was born in Hawaii. "
                + "Obama was elected president in 2008. He served two terms.";
        String expected = "Barack Obama was born in Hawaii. "
                + "Obama was elected president in 2008. Barack Obama served two terms.";

        assertEquals(expected, NLP.getInstance().resolveCoRef(input));
    }
}
