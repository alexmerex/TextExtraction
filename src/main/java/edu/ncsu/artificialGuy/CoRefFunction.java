/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package edu.ncsu.artificialGuy;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
/**
 *
 * @author DELL
 */
public class CoRefFunction {
    public static String getCoRefText(String StoryString) {
        //String StoryFile="input/BarackObama.txt";
		//System.out.println("Using story file : " + StoryFile);
		//Path path = FileSystems.getDefault().getPath("input=", StoryFile);
		//File file = path.toFile();
        //File file = new File (StoryFile);
		// build a Story object
		//Story story = new Story(file);

		// display the original story
		//System.out.println("\n######################## ORIGINAL STORY ##########################");
		//System.out.println(story.getText().replace(". ", ".\n"));
		//System.out.println("##################################################################\n");

		// to perform any NLP operations required
		NLP nlp = NLP.getInstance();
		
		// resolve co reference
		//return nlp.resolveCoRef(story.getText());
		return nlp.resolveCoRef(StoryString);

		// story after co reference resolution
		//System.out.println("\n################# AFTER COREFERENCE RESOLUTION ###################");
		//System.out.println(coRefText.replace(". ", ".\n"));
		//System.out.println("##################################################################\n");

       
    }

}
