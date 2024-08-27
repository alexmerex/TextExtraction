/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package edu.ncsu.artificialGuy;

import java.io.File;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

/**
 *
 * @author DOPHUC
 */
public class CoRefAppMain {

	/**
	 * @param args the command line arguments
	 */
	public static void main(String[] args) {
		// TODO code application logic here
		String StoryFile = "../content.txt";
		System.out.println("Using story file : " + StoryFile);
		File file = new File(StoryFile);
		// build a Story object
		Story story = new Story(file);

		// display the original story
		System.out.println("\n######################## ORIGINAL STORY ##########################");
		System.out.println(story.getText().replace(". ", ".\n"));
		System.out.println("##################################################################\n");

		// to perform any NLP operations required
		NLP nlp = NLP.getInstance();

		// resolve co reference
		String coRefText = nlp.resolveCoRef(story.getText());

		// story after co reference resolution
		System.out.println("\n################# AFTER COREFERENCE RESOLUTION ###################");
		System.out.println(coRefText.replace(". ", ".\n"));
		System.out.println("##################################################################\n");

		// save the result as a text file
		try {
			FileWriter writer = new FileWriter("../content_afterChange.txt");
			writer.write(coRefText);
			writer.close();
			System.out.println("Result saved as output/result.txt");
		} catch (IOException e) {
			System.out.println("An error occurred while saving the result.");
			e.printStackTrace();
		}
	}

}